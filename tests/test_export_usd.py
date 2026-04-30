'''
Smoke tests for the USD exporter.

These tests skip cleanly when pxr, trimesh, or manifold3d are not installed.
Install dependencies with: uv sync --extra test --extra usd
'''
import pytest

pxr = pytest.importorskip('pxr')
trimesh = pytest.importorskip('trimesh')
manifold3d = pytest.importorskip('manifold3d')

from gegede.examples.simple import airwaterboxes
import gegede.export.usd as usd


def test_smoke():
    '''convert + dumps + basic string checks.'''
    g = airwaterboxes()
    o = usd.convert(g)
    s = usd.dumps(o)
    assert s
    assert '#usda' in s
    assert 'defaultPrim = "World"' in s
    assert 'Volumes' in s
    assert 'Materials' in s


def test_validate():
    g = airwaterboxes()
    o = usd.convert(g)
    assert usd.validate_object(o)


def test_dumps_usda():
    g = airwaterboxes()
    o = usd.convert(g)
    s = usd.dumps(o, fmt='usda')
    assert isinstance(s, str)
    assert '#usda' in s


def test_dumps_usdc():
    g = airwaterboxes()
    o = usd.convert(g)
    b = usd.dumps(o, fmt='usdc')
    assert isinstance(b, bytes)
    assert b[:4] == b'PXR-'


def test_output_usda(tmp_path):
    g = airwaterboxes()
    o = usd.convert(g)
    p = tmp_path / 'out.usda'
    usd.output(o, str(p))
    text = p.read_text()
    assert text.startswith('#usda')


def test_output_usdc(tmp_path):
    g = airwaterboxes()
    o = usd.convert(g)
    p = tmp_path / 'out.usdc'
    usd.output(o, str(p))
    header = p.read_bytes()[:4]
    assert header == b'PXR-'


def test_world_structure():
    '''The world volume appears as a placement under /World.'''
    from pxr import Usd, Sdf
    g = airwaterboxes()
    o = usd.convert(g)
    stage = o.stage
    world_prim = stage.GetDefaultPrim()
    assert str(world_prim.GetPath()) == '/World'
    children = list(world_prim.GetChildren())
    assert len(children) >= 1


def test_materials_in_stage():
    '''All gegede matter objects have a material prim in /Library/Materials.'''
    g = airwaterboxes()
    o = usd.convert(g)
    stage = o.stage
    for name in g.store.matter:
        from gegede.export.usd.paths import mat_path, sanitize
        p = stage.GetPrimAtPath(mat_path(name))
        assert p.IsValid(), f'No material prim for {name!r}'


def test_prototype_for_each_volume():
    '''Each gegede Volume has a prototype under /Library/Volumes.'''
    from pxr import Usd
    import gegede.iter as it
    g = airwaterboxes()
    o = usd.convert(g)
    stage = o.stage
    volumes = it.ascending(g.store.structure, g.world)
    for vol in volumes:
        from gegede.export.usd.paths import proto_path
        p = stage.GetPrimAtPath(proto_path(vol.name))
        assert p.IsValid(), f'No prototype prim for volume {vol.name!r}'


def test_nested_boxes_builder():
    '''Exercise the builder pipeline fixture.'''
    from gegede.examples.builders import nested_boxes
    g = nested_boxes()
    o = usd.convert(g)
    s = usd.dumps(o)
    assert s and '#usda' in s
