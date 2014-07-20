#!/usr/bin/env python
'''
Test gegede.construct module by making some structure
'''

from gegede import construct

def test_make_some_stuff():
    g = construct.Geometry()
    pos = g.structure.Position('pos1', '1cm',z='2cm')
    print pos
    rot = g.structure.Rotation('rot1', x='90deg')
    print rot
