#!/usr/bin/env python
'''
A GGD builder
'''

from collections import OrderedDict

from .util import list_match, make_class

class Builder(object):
    '''
    A Builder base class

    This class maintains the following data members:

    .builders - an ordered dictionary of sub-builder objects

    .volumes - an ordered dictionary of top-level volume objects

    For adding to these, see self.add_* methods named after these members
    '''


    def __init__(self, name):
        '''
        Create an instance of the builder with the given <name>.

        The <name> is used to later locate the builders configuration.
        '''
        self.name = name
        self.builders = OrderedDict()
        self.volumes = OrderedDict()
        
    
    def get_builders(self, entry = None):
        '''
        Return sequence of builder objects that match the entry.
        '''
        return list_match(self.builders.values(), entry, deref = lambda x: x.name)

    def get_builder(self, entry = None, index = 0):
        '''
        Return the one builder that matches the entry.
        '''
        b = list_match(self.builders.values(), entry, deref = lambda x: x.name)[index]
        #print ('get_builder("%s") -> %s:%s' % (entry, b, b.name))
        return b

    def get_volumes(self, entry = None):
        '''
        Return sequence of volume objects that match the entry.
        '''
        return list_match(self.volumes.values(), entry, deref = lambda x: x.name)

    def get_volume(self, entry = None, index = 0):
        '''
        Return the one volume that matches the entry.
        '''
        return list_match(self.volumes.values(), entry, deref = lambda x: x.name)[index]

    def add_volume(self, *vols):
        '''Register top-level logical volumes to self.volumes.  

        <vols> is a list logical volume objects.

        No return value.

        Subclass should call this in construct().
        '''

        for v in vols:
            if v.name in self.volumes:
                print ('Volume already exists: "%s" out of %d volumes' % (v.name, len(self.volumes)))
                print ('\n'.join(self.volumes))
                continue
            self.volumes[v.name] = v
        return

    def add_builder(self, name, klass):
        '''Add a builder of type <klass> and given name <name>.

        No return value.

        klass may be an instance of a Builder class or a string
        holding the fully-qualified name of a class.
        '''
        if self.get_builders(name):
            print ('Builder already registered: "%s"' % name)
            return
            
        if isinstance(klass, str):
            klass = make_class(klass)
        builder = klass(name)
        self.builders[name] = builder
        return

    def configure(self, **kwds):
        '''Process my configuration.

        The <kwds> dictionary holds any configuration parameters
        relevant to this builder.

        No return value.

        Subclass may override.

        If a self.defaults value exists it updated with kwds and the
        items are set as data members of self.  

        The builder may add sub-builder objects inside this method.
        See self.add_builder().  They will have their own configure()
        method called after this method exits.

        '''
        if hasattr(self, 'defaults'):
            if not set(kwds).issubset(self.defaults): # no unknown keywords
                msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
                raise ValueError(msg)
            self.__dict__.update(**self.defaults)    # stash them as data members
            self.__dict__.update(**kwds)             # and update any from user

        return

    
    def construct(self, geom):
        '''Construct the builder's geometry.

        The <geom> object is an instance of gegede.construct.Geometry.

        Sub class should override.

        Implementation should produce all materials and logical or
        physical volumes needed.  Any sub-builders will have their
        construct() method called prior to this one and so will have
        their .volumes ordered dictionary populated.

        '''
        return


# Functions to manage builder hierarchy:

def configure(builder, cfg):
    '''Configure a builder with its item in the <cfg> dictionary and
    recurse through any sub-builders.
    '''

    if hasattr(builder, '_configured'): 
        return                  # only configure once
    builder.configure(**cfg.get(builder.name, dict()))
    builder._configured = True;

    # recurs on child builders
    for other in builder.builders.values():
        configure(other, cfg)
    return

def construct(builder, geom):
    '''Call the construct method on the builder after recursing any
    sub-builders'''
    for other in builder.builders.values():
        construct(other, geom)

    if hasattr(builder, '_constructed'):
        return
    builder.construct(geom)
    builder._constructed = True
    return


    
