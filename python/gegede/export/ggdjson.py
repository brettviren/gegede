#!/usr/bin/env python
'''
A (trivial) JSON representation of a gegede geometry
'''

import json
import pod

def dumps(geom):
    return json.dumps(pod.convert(geom), indent=2)
