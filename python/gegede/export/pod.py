#!/usr/bin/env python
'''
Export a gegede.construct.Geometry into a plain old data structure.
'''

# It would be nice to clean this code up to not hard-code assumptions
# about the data schema.

def value2pod(val):
    if type(val) == tuple:
        return val
    return str(val)

def obj2pod(obj):
    d = {n:value2pod(v) for n,v in zip(obj._fields,obj)}
    return dict(classname = type(obj).__name__, **d)
                

def convert(geom):
    dat = dict()
    for section in geom.schema.keys():
        secdata = getattr(geom.store, section)
        things = [obj2pod(x) for x in secdata.values()]
        dat[section] = things
    return dat

def dumps(geom):
    return str(convert(geom))
