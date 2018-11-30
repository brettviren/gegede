#!/usr/bin/env python
'''
Test that correct GDML is produced
'''

import os
from gegede.examples.builders import nested_boxes
from gegede import construct
import gegede.export.gdml
etree = gegede.export.gdml.etree

testdir = os.path.dirname(__file__)

def test_gdml():
    '''
    Test the test.gdml from GDML's own Python package
    '''
    xsd_doc = etree.parse(gegede.export.gdml.schema_file)
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.parse(os.path.join(testdir, 'test.gdml'))
    valid = xsd.validate(xml)
    if not valid:
        print (xsd.error_log)
    assert valid, "Failed to validate GDML's own test.gdml"

def test_gegede_gdml_boxes():
    geom = nested_boxes()
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_twistedbox():
    geom = construct.Geometry()
    shape = geom.shapes.TwistedBox('TwistedBox')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_tube():
    geom = construct.Geometry()
    shape = geom.shapes.Tubs('Tubs')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_sphere():
    geom = construct.Geometry()
    shape = geom.shapes.Sphere('Sphere')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_cone():
    geom = construct.Geometry()
    shape = geom.shapes.Cone('Cone')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_polyhedra():
    geom = construct.Geometry()
    shape = geom.shapes.PolyhedraRegular('PolyhedraRegular')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_trapezoid():
    geom = construct.Geometry()
    shape = geom.shapes.Trapezoid('Trapezoid')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_twistedtrap():
    geom = construct.Geometry()
    shape = geom.shapes.TwistedTrap('TwistedTrap')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_twistedtrd():
    geom = construct.Geometry()
    shape = geom.shapes.TwistedTrd('TwistedTrd')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_paraboloid():
    geom = construct.Geometry()
    shape = geom.shapes.Paraboloid('Paraboloid')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)

def test_gegede_gdml_ellipsoid():
    geom = construct.Geometry()
    shape = geom.shapes.Ellipsoid('Ellipsoid')
    lv = geom.structure.Volume(shape.name+'_volume', material='Air', shape=shape)
    geom.set_world(lv)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert s
    print (s.decode())
    gegede.export.gdml.validate(s)
