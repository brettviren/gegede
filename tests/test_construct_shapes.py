#!/usr/bin/env python
'''
Test the gegede.construct module by making some shapes
'''

from gegede import construct

def test_units():
    g = construct.Geometry()
    g.shapes.Box("units0",'1cm','2cm','3cm')    

    try:
        g.shapes.Box("units1",1,'2cm','3cm') # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Failed to catch unit mismatch"

def test_unique_shapes():
    g = construct.Geometry()
    try:
        g.shapes.Box("box0",1,2,3) # should fail
    except ValueError:
        g.shapes.Box("box0",'1cm','2cm','3cm')
    else:
        raise RuntimeError, "Failed to catch unit mismatch"

    try:
        g.shapes.Box("box0",'1mm','2mm','3mm')
    except ValueError:
        print 'Correctly failed to allow two boxes of same name'
        pass
    else:
        raise RuntimeError, "Allowed to make two boxes of same name"
    assert len(g.store.shapes) == 1

def test_make_some_shapes():
    g = construct.Geometry()
    try:
        b1 = g.shapes.Box("box1",1,2,3) # literal numbers should fail
    except ValueError:
        b1 = g.shapes.Box("box1",'1cm','2cm','3cm') # literal numbers should fail
        pass
    else:
        raise RuntimeError, 'Failed to catch unitless box dimensions %s' % str(b1)
        
    print 'B1',b1
    b2 = g.shapes.Box("box2",'1cm',dz='3cm',dy='2cm') # out of order kwargs should work
    b3 = g.shapes.Box("box3","1cm","2cm","3.0cm")    
    assert b1.dx==b2.dx and b2.dx==b3.dx, str([b1,b2,b3])
    assert b1.dy==b2.dy and b2.dy==b3.dy, str([b1,b2,b3])
    assert b1.dz==b2.dz and b2.dz==b3.dz, str([b1,b2,b3])
    try:
        g.shapes.Box("box4", 1, 2, dy=22, dz=33)
    except ValueError:
        print 'Correctly failed with duplicate kwargs'
        pass
    else:
        raise RuntimeError, "Didn't catch dup kwargs error"

    print 'Shape store:\n\t', '\n\t'.join([str(v) for v in g.store.shapes.values()])


if '__main__' == __name__:
    test_units()
    test_unique_shapes()
    test_make_some_shapes()
