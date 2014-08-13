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
            if 'meter' in v.to_base_units().units:
                used['lunit'] = lunit
                ret[k] = v.to(lunit).magnitude
                continue
            if 'radian' in v.to_base_units().units:
                used['aunit'] = aunit
                ret[k] = v.to(aunit).magnitude
                continue
            pass
        ret[k] = v
    newobj = type(obj)(**ret)
    return (newobj,used)
