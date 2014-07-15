#!/usr/bin/env python

import common
from gegede import schema

def test_unique_shapes():
    schema.shape_store.clear()
    b0 = schema.shapes.Box("box0",1,2,3)
    try:
        b00 = schema.shapes.Box("box0",1,2,3)
    except ValueError:
        print 'Correctly failed to allow two boxes of same name'
        pass
    else:
        raise RuntimeError, "Allowed to make two boxes of same name"
    assert len(schema.shape_store) == 1

def test_make_some_shapes():
    b1 = schema.shapes.Box("box1",1,2,3)    
    b2 = schema.shapes.Box("box2",1,z=3,y=2)    
    b3 = schema.shapes.Box("box3","1","2","3.0")    
    assert b1.x==b2.x and b2.x==b3.x, str([b1,b2,b3])
    assert b1.y==b2.y and b2.y==b3.y, str([b1,b2,b3])
    assert b1.z==b2.z and b2.z==b3.z, str([b1,b2,b3])
    try:
        b4 = schema.shapes.Box("box4", 1, 2, y=22, z=33)
    except ValueError:
        print 'Correctly failed with duplicate kwargs'
        pass
    else:
        raise RuntimeError, "Didn't catch dup kwargs error"

    print 'Shape store:\n\t', '\n\t'.join([str(v) for v in schema.shape_store.values()])

if '__main__' == __name__:
    test_unique_shapes()
    test_make_some_shapes()
