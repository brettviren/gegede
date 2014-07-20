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

def resolve_name(proto):
    ret = list()
    for n,v in proto:
        ret.append((n,Named(v)))
    return tuple(ret)


def NamedTypedList(typ, minentries = 1):
    '''
    Return a function which processes a prototype.
    '''

    def converter(proto):
        ret = list()
        if len(proto) < minentries:
            raise ValueError, "At least %d entries required" % minentries
        for n,v in resolve_name(proto):
            v = typ(v)
            ret.append((n,v))
        return tuple(ret)
    return converter

