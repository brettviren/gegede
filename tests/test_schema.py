#!/usr/bin/env python

import common
from gegede import schema, units, Quantity

def test_converter():
    c = schema.make_converter("1cm")
    o = c("1m")                 # should be okay

    c = schema.make_converter(1)
    try:
        o = c("1m")             # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Failed to catch mismatch with unitless prototype"

    c = schema.make_converter('1cm')
    try:
        o = c(1)             # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Failed to catch mismatch with unitful prototype"

def test_validate_input():
    proto = (("intnum",0),("fpnum",0.0),("dist",Quantity(0,"cm")))
    v = schema.validate_input(proto, 1, 2.0, "3meter")

    v = schema.validate_input(proto, 1, dist='4inch')

    try:
        v = schema.validate_input(proto, 1, 2.0, 3) # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Did not catch validation failure."


def test_units():
    schema.shapes.Box("units0",'1cm','2cm','3cm')    

    try:
        x = schema.shapes.Box("units1",1,'2cm','3cm') # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Failed to catch unit mismatch"

def test_unique_shapes():
    schema.shape_store.clear()
    try:
        b0 = schema.shapes.Box("box0",1,2,3) # should fail
    except ValueError:
        b0 = schema.shapes.Box("box0",'1cm','2cm','3cm')
    else:
        raise RuntimeError, "Failed to catch unit mismatch"

    try:
        b00 = schema.shapes.Box("box0",'1mm','2mm','3mm')
    except ValueError:
        print 'Correctly failed to allow two boxes of same name'
        pass
    else:
        raise RuntimeError, "Allowed to make two boxes of same name"
    assert len(schema.shape_store) == 1

def test_make_some_shapes():
    try:
        b1 = schema.shapes.Box("box1",1,2,3) # literal numbers should fail
    except ValueError:
        b1 = schema.shapes.Box("box1",'1cm','2cm','3cm') # literal numbers should fail
        pass
    else:
        raise RuntimeError, 'Failed to catch unitless box dimensions %s' % str(b1)
        
    print 'B1',b1
    b2 = schema.shapes.Box("box2",'1cm',dz='3cm',dy='2cm') # out of order kwargs should work
    b3 = schema.shapes.Box("box3","1cm","2cm","3.0cm")    
    assert b1.dx==b2.dx and b2.dx==b3.dx, str([b1,b2,b3])
    assert b1.dy==b2.dy and b2.dy==b3.dy, str([b1,b2,b3])
    assert b1.dz==b2.dz and b2.dz==b3.dz, str([b1,b2,b3])
    try:
        b4 = schema.shapes.Box("box4", 1, 2, dy=22, dz=33)
    except ValueError:
        print 'Correctly failed with duplicate kwargs'
        pass
    else:
        raise RuntimeError, "Didn't catch dup kwargs error"

    print 'Shape store:\n\t', '\n\t'.join([str(v) for v in schema.shape_store.values()])

if '__main__' == __name__:
    test_converter()
    test_validate_input()
    test_units()
    test_unique_shapes()
    test_make_some_shapes()
