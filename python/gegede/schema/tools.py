#!/usr/bin/env python
'''
Some functions to help process the schema
'''
from collections import OrderedDict, namedtuple
from .types import isquantity, toquantity

def make_converter(proto):
    '''Return a function that will convert its argument using <proto> as a
    prototype.  The <proto> is either a type or an instance of a Quantity
    or a string that can be parsed as a Quantity.
    '''
    if proto in (int, float):   # simple numerical type
        def topod(other):
            return proto(other)
        return topod

    if proto == str:            # treat string special to instrument some error checking
        def tostr(other):
            other = str(other)
            if other == "":
                raise ValueError('Empty string is an illegal value for str')
            if other is None:
                raise ValueError('None is an illegal value for str')
            return other
        return tostr

    if isquantity(proto):
        return toquantity(proto)

    # it better be of some type of self-converting prototype
    def toobj(other):
        ret = proto(other)
        return ret
    return toobj

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
    #print ('VALIDATE INPUT', str(proto))

    members = OrderedDict()
    converters = dict()
    for name,pval in proto:
        c = make_converter(pval)
        converters[name] = c

        #print ('CONVERTER:',name,c,pval)

        # set default
        if isquantity(pval):
            members[name] = c(pval)
        elif hasattr(pval, 'default'):
            #print ('SET DEFAULT:',name,pval.default)
            members[name] = pval.default()
        else:
            members[name] = None

        # if isquantity(pval):
        #     pval = toquantity(pval)(pval)
        # members[name] = pval
        # converters[name] = make_converter(pval)

    already = list()
    for k,v in zip(members.keys(), args):
        members[k] = converters[k](v)
        #print ('ARGS:',k,v,members[k])
        already.append(k)

    for k,v in kwargs.items():
        if k not in converters.keys():
            raise ValueError('Object "%s" not in prototype' % (k,))
        if k in already:
            raise ValueError('Keyword argument already supplied as positional: %s' % k)
        members[k] = converters[k](v)
        #print ('KWDS:',k,v,members[k])

    return members.values()
    

def make_maker(collector, ntname, *proto):

    '''
    Make a namedtuple class that does type-checking of its args against a prototype.

    The <proto> is a list of 2-tuples ("membername",<prototype object>)
    '''
    member_names = [p[0] for p in proto]
    def instantiator(objname, *args, **kwargs):
        if not objname:
            objname = "%s%06d" % (ntname, len(collector))

        if objname in collector:
            raise ValueError('Instance "%s" of type %s already in %s' % \
                (objname, ntname, collector))

        members = validate_input(proto, *args, **kwargs)

        NTT = namedtuple(ntname, ['name'] + member_names)
        obj = NTT(objname, *members)
        collector[objname] = obj
        #print ('INSTANTIATED:', obj)
        return obj
    instantiator.__name__ = ntname
    instantiator.__doc__ = "%s: %s" % (ntname, ', '.join(member_names))
    return instantiator

