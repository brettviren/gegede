#!/usr/bin/env pytest
'''
End-to-end tests for optical surface properties: schema construction and
GDML export/validation.
'''

import pytest
from lxml import etree

from gegede import construct
import gegede.export.gdml as gdml_mod
from gegede.examples.simple import airwaterboxes


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_and_validate(geom):
    '''Convert geom to GDML, validate against the schema, and return the tree.'''
    obj = gdml_mod.convert(geom)
    xml_bytes = gdml_mod.dumps(obj)
    assert xml_bytes
    gdml_mod.validate(xml_bytes)
    return etree.fromstring(xml_bytes)


# ---------------------------------------------------------------------------
# schema / construct tests
# ---------------------------------------------------------------------------

def test_opticalsurface_construct():
    '''OpticalSurface, BorderSurface, SkinSurface round-trip through the store.'''
    geom = construct.Geometry()
    box = geom.shapes.Box('b')
    lv = geom.structure.Volume('lv', material='Air', shape=box)
    pl = geom.structure.Placement('pl', volume=lv)
    geom.set_world(lv)

    os_ = geom.surfaces.OpticalSurface(
        'surf1',
        model='unified', finish='polished',
        type='dielectric_dielectric', value=1.0,
        properties=[
            ('RINDEX',       [(2.0, 1.5), (3.5, 1.55)]),
            ('SCINTILLATIONYIELD', [12000.0]),
        ])
    assert os_.name == 'surf1'
    assert os_.model == 'unified'
    assert os_.value == 1.0
    # properties preserves row structure
    assert os_.properties[0] == ('RINDEX', [(2.0, 1.5), (3.5, 1.55)])
    assert os_.properties[1] == ('SCINTILLATIONYIELD', [12000.0])
    assert 'surf1' in geom.store.surfaces

    bs = geom.surfaces.BorderSurface('bs1', surface='surf1',
                                     physvol1='pl', physvol2='pl')
    assert bs.surface == 'surf1'
    assert bs.physvol1 == 'pl'
    assert 'bs1' in geom.store.surfaces

    ss = geom.surfaces.SkinSurface('ss1', surface='surf1', volume='lv')
    assert ss.surface == 'surf1'
    assert ss.volume == 'lv'
    assert 'ss1' in geom.store.surfaces


def test_opticalsurface_bad_value():
    '''Passing a non-numeric value should raise ValueError.'''
    geom = construct.Geometry()
    with pytest.raises((ValueError, TypeError)):
        geom.surfaces.OpticalSurface('bad', model='unified', finish='polished',
                                     type='dielectric_dielectric',
                                     value='not_a_number')


# ---------------------------------------------------------------------------
# GDML export tests
# ---------------------------------------------------------------------------

def test_skinsurface_gdml():
    '''SkinSurface with scalar and vector properties exports to valid GDML.'''
    geom = construct.Geometry()
    box = geom.shapes.Box('Box')
    lv = geom.structure.Volume('Box_volume', material='Air', shape=box)
    geom.set_world(lv)

    geom.surfaces.OpticalSurface(
        'mysurf',
        model='glisur', finish='polished',
        type='dielectric_dielectric', value=1.0,
        properties=[
            ('SCINTILLATIONYIELD', [12000.0]),          # scalar -> coldim=1
            ('RINDEX',       [(2.0, 1.5), (3.5, 1.55)]),  # pairs -> coldim=2
        ])
    geom.surfaces.SkinSurface('myskin', surface='mysurf', volume='Box_volume')

    root = _make_and_validate(geom)

    # exactly one <opticalsurface> in <solids>
    solids = root.find('solids')
    opt_surfs = solids.findall('opticalsurface')
    assert len(opt_surfs) == 1
    assert opt_surfs[0].get('name') == 'mysurf'

    # the opticalsurface has two <property> children
    props = opt_surfs[0].findall('property')
    assert len(props) == 2
    prop_names = {p.get('name') for p in props}
    assert prop_names == {'SCINTILLATIONYIELD', 'RINDEX'}

    # exactly one <skinsurface> in <structure>
    structure = root.find('structure')
    skin_surfs = structure.findall('skinsurface')
    assert len(skin_surfs) == 1
    assert skin_surfs[0].get('name') == 'myskin'
    assert skin_surfs[0].get('surfaceproperty') == 'mysurf'
    volrefs = skin_surfs[0].findall('volumeref')
    assert len(volrefs) == 1
    assert volrefs[0].get('ref') == 'Box_volume'

    # no <bordersurface>
    assert structure.findall('bordersurface') == []

    # <define> contains matrices with correct coldim
    define = root.find('define')
    matrices = {m.get('name'): m for m in define.findall('matrix')}
    scint_mat = matrices['mysurf_SCINTILLATIONYIELD_VALUE']
    assert scint_mat.get('coldim') == '1'
    rindex_mat = matrices['mysurf_RINDEX_VALUE']
    assert rindex_mat.get('coldim') == '2'


def test_bordersurface_gdml():
    '''BorderSurface exports to valid GDML with two physvolref children.'''
    geom = construct.Geometry()
    inner = geom.shapes.Box('inner', '0.5m', '0.5m', '0.5m')
    outer = geom.shapes.Box('outer', '1m', '1m', '1m')
    pos = geom.structure.Position('center_pos')
    lv_inner = geom.structure.Volume('inner_vol', material='Air', shape=inner)
    pl = geom.structure.Placement('inner_in_outer', volume=lv_inner, pos=pos)
    lv_outer = geom.structure.Volume('outer_vol', material='Air', shape=outer,
                                     placements=[pl])
    geom.set_world(lv_outer)

    geom.surfaces.OpticalSurface('bsurf', model='unified', finish='ground',
                                 type='dielectric_metal', value=0.9)
    geom.surfaces.BorderSurface('border1', surface='bsurf',
                                physvol1='inner_in_outer',
                                physvol2='inner_in_outer')

    root = _make_and_validate(geom)

    structure = root.find('structure')
    borders = structure.findall('bordersurface')
    assert len(borders) == 1
    assert borders[0].get('surfaceproperty') == 'bsurf'
    physvolrefs = borders[0].findall('physvolref')
    assert len(physvolrefs) == 2
    assert all(pv.get('ref') == 'inner_in_outer' for pv in physvolrefs)

    # border must appear after all <volume> elements in <structure>
    children = list(structure)
    vol_indices = [i for i, c in enumerate(children) if c.tag == 'volume']
    border_indices = [i for i, c in enumerate(children) if c.tag == 'bordersurface']
    assert border_indices[0] > vol_indices[-1]

    # no <skinsurface>
    assert structure.findall('skinsurface') == []


def test_opticalsurface_no_properties():
    '''An OpticalSurface with no spectral properties is valid GDML.'''
    geom = construct.Geometry()
    box = geom.shapes.Box('Box')
    lv = geom.structure.Volume('Box_vol', material='Air', shape=box)
    geom.set_world(lv)

    geom.surfaces.OpticalSurface('bare_surf', model='glisur', finish='polished',
                                 type='dielectric_dielectric', value=1.0)
    geom.surfaces.SkinSurface('bare_skin', surface='bare_surf', volume='Box_vol')

    root = _make_and_validate(geom)
    opt_surfs = root.find('solids').findall('opticalsurface')
    assert len(opt_surfs) == 1
    assert opt_surfs[0].findall('property') == []


def test_airwaterboxes_gdml():
    '''The extended airwaterboxes example produces valid GDML with optical surfaces.'''
    geom = airwaterboxes()
    root = _make_and_validate(geom)

    solids = root.find('solids')
    opt_surfs = solids.findall('opticalsurface')
    assert len(opt_surfs) == 1
    assert opt_surfs[0].get('name') == 'air_water_surface'

    define = root.find('define')
    matrices = {m.get('name') for m in define.findall('matrix')}
    assert 'air_water_surface_RINDEX_VALUE' in matrices
    assert 'air_water_surface_REFLECTIVITY_VALUE' in matrices

    structure = root.find('structure')
    borders = structure.findall('bordersurface')
    assert len(borders) == 1
    assert borders[0].get('name') == 'air_water_border'


def test_geometry_without_surfaces_still_valid():
    '''A geometry that uses no surfaces still produces valid GDML.'''
    geom = construct.Geometry()
    box = geom.shapes.Box('Box')
    lv = geom.structure.Volume('Box_vol', material='Air', shape=box)
    geom.set_world(lv)
    # surfaces store exists but is empty — no change to output
    root = _make_and_validate(geom)
    assert root.find('solids').findall('opticalsurface') == []
    assert root.find('structure').findall('bordersurface') == []
    assert root.find('structure').findall('skinsurface') == []
