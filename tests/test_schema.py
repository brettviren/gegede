#!/usr/bin/env python

import common
from gegede import schema

def test_categories():
    '''
    Test that the schema has all the needed categories
    '''
    must = ["shapes", ]
    for need in must:
        assert need in schema.Schema

def test_shapes():
    '''
    Test if the schema covers the desired shapes
    '''
    # get an idea of what gdml expects
    # grep 'xs:element name=' GDMLSchema/gdml_solids.xsd | sed -e 's/.*name="//' -e 's/".*//'
    # note, actual shape types have capitalized names
    must = ["Box","Sphere","Tubs"]
    want = ["ellipsoid","tube","cone","polycone","zplane","para","trd",
            "trap","torus","orb","polyhedra","zplane","hype","eltube"]

    shapes = schema.Schema['shapes']

    for need in must:
        assert shapes.get(need), 'No "%s" in schema' % need
    unimplemented = list()
    for like in want:
        if shapes.get(like):
            continue
        unimplemented.append(like)
    if unimplemented:
        print ('Warning: shapes still needing implementation: %s' % ', '.join(unimplemented))

    

if '__main__' == __name__:
    test_categories()
    test_shapes()
