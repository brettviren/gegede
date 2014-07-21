#!/usr/bin/env python
'''
A (trivial) JSON representation of a gegede geometry
'''

import json
import pod

def dumps(geom):
    return json.dumps(pod.dumps(geom), indent=2)
