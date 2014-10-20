#!/usr/bin/env python
'''
A (trivial) JSON representation of a gegede geometry
'''

import json
import pod

def convert(geom):
    return pod.convert(geom)

def dumps(obj):
    return json.dumps(obj, indent=2)

def output(obj, filename):
    open(filename,'w').write(dumps(obj))

def validate_object(obj):
    obj2 = json.loads(json.dumps(obj))
    assert obj == obj2

def validate_output(obj, filename):
    obj2 = json.load(filename)
    assert obj == obj2
