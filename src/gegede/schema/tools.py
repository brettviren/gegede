#!/usr/bin/env python
'''
Some functions to help process the schema
'''
from collections import OrderedDict, namedtuple
from .. import Quantity, UndefinedUnitError

import logging
log = logging.getLogger('gegede')

def isquantity(thing):
    '''
    Check if "thing" looks like a quantity.  
    '''
    # Note, we can not simply test with trying to make Quantity(thing) because
    # apparently we can successfully construct a Quantity on weird things like
    # functions which then do not go on to behave in any reasonable way.

    if isinstance(thing, (int, float, Quantity)):
        return True
    if isinstance(thing, str):
        try:
            q = Quantity(thing)
        except  UndefinedUnitError:
            return False
        return True
    return False


def toquantity(proto):
    '''
    Return a converter function that converts a value into a Quantity based on proto.

    proto is a prototypical value of type for which a Quantity can be constructed.

    '''
    qobj = Quantity(proto)      # wash to assure Quantity object
    def converter(other):
        other = Quantity(other)
        if qobj.dimensionality == other.dimensionality:
            return other
        raise ValueError(f'Unit mismatch: {other} incompatible with prototype {qobj}')
    return converter


def make_converter(proto):
    '''
    Return function to coerce a value to be consistent with proto.

    The coercion depends on `proto`

    The `proto` can be one of:
    - a Python type (`int`, `float`, `str`) giving the coercion target.
    - a value which results in coercion to `Quantity` of that type.
    - a callable that converts a value to a `Quantity` (see `gegede.schema.types`)
    '''
    log.debug(f'CONVERTER: {proto}')

    if proto in (int, float):   # simple numerical type
        def topod(other):
            # simply coerce other to be type
            return proto(other)
        return topod

    if proto == str:            # treat string special to instrument some error checking
        def tostr(other):
            other = str(other)  # coerce
            if other in ("", "None"):
                raise ValueError(f'Illegal str value: "{other}"')
            return other
        return tostr

    if hasattr(proto, "__call__"):
        return proto

    if isquantity(proto):
        return toquantity(proto)


    raise ValueError(f'unsupported converter proto of type: {type(proto)}')

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
    log.debug(f'VALIDATE INPUT {proto}')

    members = OrderedDict()
    converters = dict()
    for name, pval in proto:
        c = make_converter(pval)
        converters[name] = c

        log.debug(f'VALIDATOR: {name=} {c=} {pval=}')

        # set default
        if isquantity(pval):
            members[name] = c(pval)
            log.debug(f'SET VALUE {name=} {members[name]}')
        elif hasattr(pval, 'default'):
            log.debug(f'SET DEFAULT {name=} {pval=} {pval.default}')
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
        log.debug(f'ARGS: {k=} {v=} {members[k]}')
        already.append(k)

    for k,v in kwargs.items():
        if k not in converters.keys():
            raise ValueError('Object "%s" not in prototype' % (k,))
        if k in already:
            raise ValueError('Keyword argument already supplied as positional: %s' % k)
        members[k] = converters[k](v)
        log.debug(f'KWDS: {k=} {v=} {members[k]}')

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
        log.debug(f'INSTANTIATED {obj}')
        return obj
    instantiator.__name__ = ntname
    instantiator.__doc__ = "%s: %s" % (ntname, ', '.join(member_names))
    return instantiator

