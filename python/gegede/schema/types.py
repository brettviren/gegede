#!/usr/bin/env python
'''
Special schema types
'''

try:
    python_string = basestring
except NameError:
    python_string = str

from .. import Quantity

def isquantity(thing):
    if isinstance(thing, Quantity):
        return True             # it's an instance

    if isinstance(thing, python_string):
        try:
            Quantity(thing)
        except ValueError:
            pass
        else:
            return True         # it's a string that can be parsed
    return False                # dunno what it is

def toquantity(proto):
    qobj = Quantity(proto)      # wash to assure Quantity object
    def converter(other):
        other = Quantity(other)
        if qobj.dimensionality == other.dimensionality:
            return other
        raise ValueError, 'Unit mismatch: %s incompatible with prototype %s' % (other, qobj)
    return converter

def Named(thing):
    '''
    Return thing.name if it has the attribute, otherwise return thing
    '''
    if hasattr(thing,'name'):
        return thing.name
    return thing


def NamedTypedList(typ, minentries = 1):
    '''Return a function which processes a prototype which is a list of
    2-tuples: ("name", obj) where <obj> is an instance of type <typ>.
    '''

    def named_typed_list_converter(proto):
        #print 'named_typed_list_converter(%s, "%s")' % (typ, str(proto))
        ret = list()
        if len(proto) < minentries:
            raise ValueError, "At least %d entries required" % minentries
        for n,v in proto:
            v = typ(v)
            n = Named(n)
            ret.append((n,v))
        return ret
    named_typed_list_converter.default = list
    return named_typed_list_converter


def NameList(typ, minentries = 1):
    '''Return a function which processes a prototype which is a list of
    object names.
    '''

    def name_list_converter(proto):
        #print 'name_list_converter(%s, "%s")' % (typ, str(proto))
        ret = list()
        if len(proto) < minentries:
            raise ValueError, "At least %d entries required" % minentries
        for n in proto:
            n = Named(n)
            ret.append(n)
        return ret
    name_list_converter.default = list
    return name_list_converter

