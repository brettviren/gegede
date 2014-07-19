#!/usr/bin/env python
'''
Test the gegede.construct module
'''

from gegede import construct

def test_make_an_empty_geometry():
    construct.Geometry()

if '__main__' == __name__:
    test_make_an_empty_geometry()
