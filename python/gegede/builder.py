#!/usr/bin/env python
'''
A GGD builder
'''


class Builder(object):
    '''
    A Builder base class

    This class maintains the following data members:

    .builders - a sequence holding any sub-builders

    .volumes - a sequence holding top-level logical volumes.

    For adding to these, see self.add_* methods named after these members
    '''


    def __init__(self, name):
        '''
        Create an instance of the builder with the given <name>.

        The <name> is used to later locate the builders configuration.
        '''
        self.name = name
        self.builders = list()
        self.volumes = list()
        
    def add_volume(self, *vols):
        '''Register top-level logical volumes to self.volumes.  

        <vols> is a list of names of logical volume objects.

        No return value.

        Subclass should call this in construct().
        '''

        for v in vols:
            if hasattr(v,'name'):
                v = v.name
            if v in self.volumes:
                continue
            self.volumes.append(v)

    def add_builder(self, name, klass):
        '''Add a builder of type <klass> and given name <name>.

        No return value.

        klass may be an instance of a Builder class or a string
        holding the fully-qualified name of a class.
        '''
        if (isinstance(klass, type(""))):
            mod,name = klass.rsplit('.',1) # this seems dirty
            exec ('import %s' % mod)
            klass = eval(klass)
        builder = klass(name)
        self.builders.append(builder)
        return

    def configure(self, **kwds):
        '''Process my configuration.

        The <kwds> dictionary holds any configuration parameters
        relevant to this builder.

        No return value.

        Subclass may override.

        The builder may add sub-builder objects inside this method.
        See self.add_builder().  They will have their own configure()
        method called after this method exits.
        '''
        return

    
    def construct(self, geom):
        '''Construct the builder's geometry.

        The <geom> object is an instance of gegede.construct.Geometry.

        Sub class should override.

        Implementation should produce all materials and logical or
        physical volumes needed.  Any sub-builders will have their
        construct() method called prior to this one and so will have
        their .volumes list populated.

        '''
        return


# Functions to manage builder hierarchy:

def configure(builder, cfg):
    '''Configure a builder with its item in the <cfg> dictionary and
    recurse through any sub-builders.
    '''
    builder.configure(**cfg.get(builder.name, dict()))
    for other in builder.builders:
        configure(other, cfg)
    return

def construct(builder, geom):
    '''Call the construct method on the builder after recursing any
    sub-builders'''
    for other in builder.builders:
        construct(other, geom)
    builder.construct(geom)
    return


    
