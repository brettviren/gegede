#!/usr/bin/env python
'''
'''

from gegede import Quantity

def wash_units(obj, lunit='cm', aunit='radian'):
    '''Return a tuple (newobj,used) where <newobj> is <obj> with any
    Quantities placed into explicit units given by lunit for length
    and aunit for angle.  The <used> is a dict of all units used.
    '''

    ret = dict()
    used = dict()
    for k,v in zip(obj._fields, obj):
        if type(v) == Quantity:
            base_units = v.to_base_units().units
            if 'meter' == base_units:
                used['lunit'] = lunit
                ret[k] = v.to(lunit).magnitude
                continue
            if 'radian' == base_units:
                used['aunit'] = aunit
                ret[k] = v.to(aunit).magnitude
                continue
            pass
        ret[k] = v
    newobj = type(obj)(**ret)
    return (newobj,used)

import re
def list_match(values, entry = None, deref = lambda x: x):
    '''
    If not entry, return values.  

    If entry is int, return values at entry (at most single element list)

    If entry is a callable, call it on deref(value) and return value if callable returns true.

    O.w. assume str and first try exact match otherwise interpret as regexp and return values matching deref(value).
    '''
    #print ("list_match(%s,%s)" % (', '.join(['%s:%s' % (type(v),v.name) for v in values]), entry))

    if entry is None:
        return list(values)

    if isinstance(entry, int):
        return [list(values)[entry]]

    if callable(entry):
        ret = list()
        for v in values:
            if entry(deref(v)):
                ret.append(v)
        return ret

    # assume string, first as exact match
    ret = list()
    for v in values:
        if entry == deref(v):
            ret.append(v)
    if ret:
        return ret
    

    # then as regex
    rx = re.compile(entry, re.I)
    for v in values:
        if rx.search(deref(v)) is None:
            continue
        ret.append(v)
    return list(ret)

