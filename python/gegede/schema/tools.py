#!/usr/bin/env python
'''
Some functions to help process the schema
'''
from collections import OrderedDict, namedtuple
from .. import units, Quantity

def make_converter(obj):
    '''Return a function that will convert its argument using obj as a
    prototype.  It will raise ValueError if conversion is not
    possible.
    '''
    obj = Quantity(obj)
    def converter(other):
        other = Quantity(other)
        if obj.dimensionality == other.dimensionality:
            return other
        raise ValueError, 'Unit mismatch: %s incompatible with prototype %s' % (other, obj)
    return converter

def validate_input(proto, *args, **kwargs):
    '''Validate the input <args> and <kwargs> against the prototypes in <proto>.

    <proto> is a list of ("name",object) tuples.

    <args> is a list of positional arguments assumed to follow the
    ordering of <proto> but may be of shorter length.

    <kwargs> is a dictionary of "name"/object pairs supplying any
    remaining arguments.

    Any unspecified arguments are given the default from <proto> and
    no keys in <kwargs> may be given in addition to what are specified
    in <args>.

    A an ordered list of values are returned.
    '''
    members = OrderedDict()
    converters = dict()
    for name,pval in proto:
        members[name] = pval
        converters[name] = make_converter(pval)

    already = list()
    for k,v in zip(members.keys(), args):
        members[k] = converters[k](v)
        already.append(k)
    for k,v in kwargs.items():
        if k not in converters.keys():
            raise ValueError, 'Object "%s" not in prototype' % (k,)
        if k in already:
            raise ValueError, 'Keyword argument already supplied as positional: %s' % k
        members[k] = converters[k](v)

    return members.values()
    

def make_maker(collector, ntname, *proto):

    '''
    Make a namedtuple class that does type-checking of its args against a prototype.

    The <proto> is a list of 2-tuples ("membername",<prototype object>)
    '''
    member_names = [p[0] for p in proto]
    def instantiator(objname, *args, **kwargs):
        if objname in collector:
            raise ValueError, 'Instance "%s" of type %s already in %s' % \
                (objname, ntname, collector)

        members = validate_input(proto, *args, **kwargs)

        NTT = namedtuple(ntname, ['name'] + member_names)
        obj = NTT(objname, *members)
        collector[objname] = obj
        return obj
    instantiator.__name__ = ntname
    instantiator.__doc__ = "%s: %s" % (ntname, ', '.join(member_names))
    return instantiator

