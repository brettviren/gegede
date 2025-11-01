#!/usr/bin/env python
'''
# GeGeDe Schema Types

The methods of this module return a function that serves as a special type in
the GeGeDe schema description.  They are used when some part of the schema is
not a simple key/value attribute.

The function that is returned by a method will coerce its value into an instance
of the represented type.  The coercion will be subject to validation.

Types that represent collections and provide a `.default` attribute providing a
default constructor.

Note, these details are not exposed to a developer of GeGeDe builders except for
understanding what type they represent when reading the `gegede.schema.Schema`
data structure.
'''

from .tools import make_converter

import logging
log = logging.getLogger('gegede')

def Named(thing):
    '''
    A type for a thing with a .name attribute.

    A Named instance is used to refer to some other object already created and
    held in a geometry store.

    Note, when used in the `gegede.schema.Schema` this type is specified simply
    `Named` with no function call.

    When called internally with some thing, it will return `thing.name`
    if the attribute exists else `thing` is returned.
    '''
    if hasattr(thing,'name'):
        return thing.name
    return thing


def NamedTypedList(typ, minentries = 1):
    '''
    A type for a list of named values of a given type.

    Return a function which processes a prototype which is a list of
    2-tuples: ("name", obj) where <obj> is an instance of type <typ>.
    '''

    def named_typed_list_converter(proto):
        ret = list()
        if len(proto) < minentries:
            raise ValueError("At least %d entries required" % minentries)
        for n,v in proto:
            v = typ(v)
            n = Named(n)
            ret.append((n,v))
        return ret
    named_typed_list_converter.default = list
    return named_typed_list_converter


def NameList(minentries = 1):
    '''A type consisting of `Named` names'''

    def name_list_converter(proto):
        ret = list()
        if len(proto) < minentries:
            raise ValueError("At least %d entries required" % minentries)
        for n in proto:
            n = Named(n)
            ret.append(n)
        return ret
    name_list_converter.default = list
    return name_list_converter

# def ListOfNtuples(n=2, typ=str):
#     '''
#     A type which is a list of N-tuples of length n and type typ.
#     '''
#     def lon_converter(proto):
#         ret = list()
#         for onent in proto:
#             if len(onent) != n:
#                 raise ValueError(f'Exactly {n} items required')
#             ret.append(tuple(map(typ, onent)))
#         return ret
#     lon_converter.default = list
#     return lon_converter

def Array(typ=float, n=0):
    '''
    A type which is an array length n and common type of elements typ.

    An n of zero implies no fixed size.

    A negative n implies finite (non-zero size) but otherwise unbound size.
    
    '''
    cvt = make_converter(typ)
    def converter(proto):
        if n > 0 and len(proto) != n:
            raise ValueError(f'Exactly {n} items required')
        if n < 0 and len(proto) == 0:
            raise ValueError(f'A finite number of items is required')
        return tuple([cvt(one) for one in proto])
    converter.default = list
    return converter

def Struct(**attrs):
    '''
    A struct-like type that maps attribute names to attribute types.

    The prototype is dict-like

    '''
    cvt = {k:make_converter(t) for k,t in attrs.items()}
    def converter(proto):
        log.debug(f'Struct converter: {proto=}')
        return {k:cvt[k](proto[k]) for k in cvt} # key error if user omits an attribute

    converter.default = dict
    return converter
