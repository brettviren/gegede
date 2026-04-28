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


def test_physvol_name_attribute():
    '''physvol element carries the placement name as its name= attribute.'''
    geom = construct.Geometry()
    inner = geom.shapes.Box('inner')
    outer = geom.shapes.Box('outer', '2m', '2m', '2m')
    lv_inner = geom.structure.Volume('inner_vol', material='Air', shape=inner)
    pl = geom.structure.Placement('my_placement', volume=lv_inner)
    lv_outer = geom.structure.Volume('outer_vol', material='Air', shape=outer,
                                     placements=[pl])
    geom.set_world(lv_outer)
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    root = etree.fromstring(s)
    structure = root.find('structure')
    vol_node = structure.find('volume[@name="outer_vol"]')
    pvols = vol_node.findall('physvol')
    assert len(pvols) == 1
    assert pvols[0].get('name') == 'my_placement'
    gegede.export.gdml.validate(s)


def test_physvol_empty_name_omitted():
    '''physvol must not carry name="" when the placement name is empty.

    xs:ID cannot be an empty string, so <physvol name=""> is invalid GDML.
    The exporter must omit the attribute entirely in that case (the attribute
    is optional in SinglePlacementType).

    This simulates a scenario where a placement ends up in the store under an
    empty key (e.g. due to direct store manipulation or legacy geometry data).
    '''
    geom = construct.Geometry()
    inner = geom.shapes.Box('inner')
    outer = geom.shapes.Box('outer', '2m', '2m', '2m')
    lv_inner = geom.structure.Volume('inner_vol', material='Air', shape=inner)
    pl = geom.structure.Placement('real_pl', volume=lv_inner)
    lv_outer = geom.structure.Volume('outer_vol', material='Air', shape=outer,
                                     placements=[pl])
    geom.set_world(lv_outer)

    # Inject an empty-named placement.  Bypasses the normal auto-naming in
    # make_maker so that placename == '' reaches make_volume_node.
    empty_pl = pl._replace(name='')
    geom.store.structure[''] = empty_pl
    lv_outer.placements.append('')

    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    assert b'name=""' not in s, 'physvol must not carry name="" (xs:ID cannot be empty)'
    gegede.export.gdml.validate(s)
