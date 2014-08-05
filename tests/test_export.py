#!/usr/bin/env python
'''
Test the gegede.export modules
'''
from gegede.examples.simple import airwaterboxes

import gegede.export.ggdjson
import gegede.export.pod
import gegede.export.gdml

def test_pod():
    g = airwaterboxes()
    s = gegede.export.pod.dumps(g)
    assert s                    # lame test


def test_ggdjson():
    g = airwaterboxes()
    s = gegede.export.ggdjson.dumps(g)
    assert s                    # lame test


def test_gdml():
    g = airwaterboxes()
    s = gegede.export.gdml.dumps(g)
    assert s                    # lame test
    try:
        gegede.export.gdml.validate(s)
    except ValueError:
        print 'Validation failed!'
        for lineno,line in enumerate(s.split('\n')):
            print "[%3d] %s" %(lineno+1, line)

        raise


