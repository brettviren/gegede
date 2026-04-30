'''
Per-shape end-to-end tests for the USD exporter (Phase 1).

Each test builds a minimal Geometry, converts to USD, and asserts that
the correct prim type appears at the expected path with the expected attributes.
'''
import pytest

pxr = pytest.importorskip('pxr')
trimesh_mod = pytest.importorskip('trimesh')
manifold3d = pytest.importorskip('manifold3d')

from pxr import UsdGeom, Usd
from gegede import construct
import gegede.export.usd as usd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_geom(shape_factory):
    '''Build a Geometry with one shape as the world volume.'''
    g = construct.Geometry()
    shape = shape_factory(g)
    air = g.matter.Element('TestAir', 'A', 7, '14g/mole')
    vol = g.structure.Volume(shape.name + '_vol', material=air, shape=shape)
    g.set_world(vol)
    return g, shape


def _stage(geom):
    return usd.convert(geom).stage


def _proto_shape_prim(stage, volname):
    from gegede.export.usd.paths import shape_path
    return stage.GetPrimAtPath(shape_path(volname))


# ---------------------------------------------------------------------------
# Box → UsdGeomCube + scale
# ---------------------------------------------------------------------------

def test_box_cube_prim():
    g, shape = _build_geom(lambda g: g.shapes.Box('MyBox'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyBox_vol')
    assert prim.IsValid()
    assert prim.GetTypeName() == 'Cube'


def test_box_cube_size_one():
    g, shape = _build_geom(lambda g: g.shapes.Box('MyBox'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyBox_vol')
    cube = UsdGeom.Cube(prim)
    assert cube.GetSizeAttr().Get() == 1.0


def test_box_scale_default_extents():
    '''Default Box dx=dy=dz=1m; with meters_per_unit=0.001: scale = 2000mm.'''
    g, shape = _build_geom(lambda g: g.shapes.Box('MyBox'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyBox_vol')
    xf = UsdGeom.Xformable(prim)
    ops = xf.GetOrderedXformOps()
    scale_ops = [op for op in ops if op.GetOpType() == UsdGeom.XformOp.TypeScale]
    assert len(scale_ops) == 1
    sx, sy, sz = scale_ops[0].Get()
    assert abs(sx - 2000.0) < 1e-6
    assert abs(sy - 2000.0) < 1e-6
    assert abs(sz - 2000.0) < 1e-6


def test_box_scale_asymmetric():
    '''Box with different half-extents produces the correct non-uniform scale.'''
    g, shape = _build_geom(lambda g: g.shapes.Box('AB', '1cm', '2cm', '3cm'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'AB_vol')
    xf = UsdGeom.Xformable(prim)
    ops = xf.GetOrderedXformOps()
    scale_ops = [op for op in ops if op.GetOpType() == UsdGeom.XformOp.TypeScale]
    sx, sy, sz = scale_ops[0].Get()
    # 1cm = 0.01m; 0.01/0.001 = 10 stage units; full = 20mm
    assert abs(sx - 20.0) < 1e-5
    assert abs(sy - 40.0) < 1e-5
    assert abs(sz - 60.0) < 1e-5


# ---------------------------------------------------------------------------
# Sphere → UsdGeomSphere (full)
# ---------------------------------------------------------------------------

def test_sphere_prim():
    g, _ = _build_geom(lambda g: g.shapes.Sphere('MySphere'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MySphere_vol')
    assert prim.IsValid()
    assert prim.GetTypeName() == 'Sphere'


def test_sphere_radius():
    '''Default Sphere rmax=1m → radius=1000mm in stage units.'''
    g, _ = _build_geom(lambda g: g.shapes.Sphere('MySphere'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MySphere_vol')
    sph = UsdGeom.Sphere(prim)
    assert abs(sph.GetRadiusAttr().Get() - 1000.0) < 1e-6


def test_sphere_partial_raises():
    '''Sphere with rmin>0 must raise NotImplementedError in Phase 1.'''
    g, _ = _build_geom(lambda g: g.shapes.Sphere('HS', rmin='0.5m'))
    with pytest.raises(NotImplementedError):
        usd.convert(g)


# ---------------------------------------------------------------------------
# Tubs → UsdGeomCylinder (full)
# ---------------------------------------------------------------------------

def test_tubs_prim():
    g, _ = _build_geom(lambda g: g.shapes.Tubs('MyTubs'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyTubs_vol')
    assert prim.IsValid()
    assert prim.GetTypeName() == 'Cylinder'


def test_tubs_axis():
    g, _ = _build_geom(lambda g: g.shapes.Tubs('MyTubs'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyTubs_vol')
    cyl = UsdGeom.Cylinder(prim)
    assert cyl.GetAxisAttr().Get() == 'Z'


def test_tubs_height_radius():
    '''Default Tubs dz=1m, rmax=1m → height=2000mm, radius=1000mm.'''
    g, _ = _build_geom(lambda g: g.shapes.Tubs('MyTubs'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyTubs_vol')
    cyl = UsdGeom.Cylinder(prim)
    assert abs(cyl.GetHeightAttr().Get() - 2000.0) < 1e-6
    assert abs(cyl.GetRadiusAttr().Get() - 1000.0) < 1e-6


def test_tubs_rmin_raises():
    '''Tubs with rmin>0 must raise NotImplementedError in Phase 1.'''
    g, _ = _build_geom(lambda g: g.shapes.Tubs('TubsHollow', rmin='0.3m'))
    with pytest.raises(NotImplementedError):
        usd.convert(g)


# ---------------------------------------------------------------------------
# Cone → UsdGeomMesh (always mesh in Phase 1)
# ---------------------------------------------------------------------------

def test_cone_mesh_prim():
    g, _ = _build_geom(lambda g: g.shapes.Cone('MyCone'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyCone_vol')
    assert prim.IsValid()
    assert prim.GetTypeName() == 'Mesh'


def test_cone_mesh_has_points():
    g, _ = _build_geom(lambda g: g.shapes.Cone('MyCone'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyCone_vol')
    pts = UsdGeom.Mesh(prim).GetPointsAttr().Get()
    assert len(pts) > 0


# ---------------------------------------------------------------------------
# Trapezoid → UsdGeomMesh
# ---------------------------------------------------------------------------

def test_trapezoid_mesh_prim():
    g, _ = _build_geom(lambda g: g.shapes.Trapezoid('MyTrap'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyTrap_vol')
    assert prim.IsValid()
    assert prim.GetTypeName() == 'Mesh'


def test_trapezoid_mesh_eight_vertices():
    g, _ = _build_geom(lambda g: g.shapes.Trapezoid('MyTrap'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyTrap_vol')
    pts = UsdGeom.Mesh(prim).GetPointsAttr().Get()
    assert len(pts) == 8


def test_trapezoid_mesh_twelve_faces():
    g, _ = _build_geom(lambda g: g.shapes.Trapezoid('MyTrap'))
    stage = _stage(g)
    prim = _proto_shape_prim(stage, 'MyTrap_vol')
    counts = UsdGeom.Mesh(prim).GetFaceVertexCountsAttr().Get()
    assert len(counts) == 12


# ---------------------------------------------------------------------------
# Boolean operations → UsdGeomMesh
# ---------------------------------------------------------------------------

def _boolean_geom(op):
    g = construct.Geometry()
    a = g.shapes.Box('box_a')
    b = g.shapes.Sphere('sph_b', rmax='1.1m')
    if op == 'union':
        shape = g.shapes.Union('ab', first=a, second=b)
    elif op == 'subtraction':
        shape = g.shapes.Subtraction('ab', first=a, second=b)
    else:
        shape = g.shapes.Intersection('ab', first=a, second=b)
    air = g.matter.Element('Air', 'A', 7, '14g/mole')
    vol = g.structure.Volume('ab_vol', material=air, shape=shape)
    g.set_world(vol)
    return g


def test_subtraction_mesh():
    stage = _stage(_boolean_geom('subtraction'))
    prim = _proto_shape_prim(stage, 'ab_vol')
    assert prim.IsValid() and prim.GetTypeName() == 'Mesh'
    pts = UsdGeom.Mesh(prim).GetPointsAttr().Get()
    assert len(pts) > 0


def test_union_mesh():
    stage = _stage(_boolean_geom('union'))
    prim = _proto_shape_prim(stage, 'ab_vol')
    assert prim.IsValid() and prim.GetTypeName() == 'Mesh'


def test_intersection_mesh():
    stage = _stage(_boolean_geom('intersection'))
    prim = _proto_shape_prim(stage, 'ab_vol')
    assert prim.IsValid() and prim.GetTypeName() == 'Mesh'


# ---------------------------------------------------------------------------
# Placement transforms
# ---------------------------------------------------------------------------

def test_placement_translate_and_rotate():
    '''Placement with pos+rot produces both translate and rotateXYZ ops.'''
    from pxr import Gf
    g = construct.Geometry()
    inner_shape = g.shapes.Box('inner')
    outer_shape = g.shapes.Box('outer', '5m', '5m', '5m')
    air = g.matter.Element('Air', 'A', 7, '14g/mole')

    inner_vol = g.structure.Volume('inner_vol', material=air, shape=inner_shape)
    pos = g.structure.Position('p1', '10cm', '20cm', '30cm')
    rot = g.structure.Rotation('r1', x='10deg', y='20deg', z='30deg')
    pl  = g.structure.Placement('inner_pl', volume=inner_vol, pos=pos, rot=rot)
    outer_vol = g.structure.Volume('outer_vol', material=air, shape=outer_shape,
                                   placements=[pl])
    g.set_world(outer_vol)

    stage = _stage(g)

    # The placement should appear inside the outer prototype
    from gegede.export.usd.paths import proto_path, sanitize
    pl_path = proto_path('outer_vol') + '/' + sanitize('inner_pl')
    place = stage.GetPrimAtPath(pl_path)
    assert place.IsValid(), f'Placement prim not found at {pl_path}'

    xf = UsdGeom.Xformable(place)
    ops = xf.GetOrderedXformOps()
    op_types = [op.GetOpType() for op in ops]
    assert UsdGeom.XformOp.TypeTranslate in op_types
    assert UsdGeom.XformOp.TypeRotateXYZ in op_types


def test_placement_no_transform():
    '''Placement with no pos/rot produces no xformOps (just the reference).'''
    g = construct.Geometry()
    inner_shape = g.shapes.Box('inner')
    outer_shape = g.shapes.Box('outer', '5m', '5m', '5m')
    air = g.matter.Element('Air', 'A', 7, '14g/mole')
    inner_vol = g.structure.Volume('inner_vol', material=air, shape=inner_shape)
    pl = g.structure.Placement('pl_notrans', volume=inner_vol)
    outer_vol = g.structure.Volume('outer_vol', material=air, shape=outer_shape,
                                   placements=[pl])
    g.set_world(outer_vol)

    stage = _stage(g)

    from gegede.export.usd.paths import proto_path, sanitize
    pl_path = proto_path('outer_vol') + '/' + sanitize('pl_notrans')
    place = stage.GetPrimAtPath(pl_path)
    assert place.IsValid()
    xf = UsdGeom.Xformable(place)
    ops = xf.GetOrderedXformOps()
    assert len(ops) == 0


def test_instanceable_flag():
    '''By default placements are marked instanceable=True.'''
    g = construct.Geometry()
    inner_shape = g.shapes.Box('inner')
    outer_shape = g.shapes.Box('outer', '5m', '5m', '5m')
    air = g.matter.Element('Air', 'A', 7, '14g/mole')
    inner_vol = g.structure.Volume('inner_vol', material=air, shape=inner_shape)
    pl = g.structure.Placement('pl_inst', volume=inner_vol)
    outer_vol = g.structure.Volume('outer_vol', material=air, shape=outer_shape,
                                   placements=[pl])
    g.set_world(outer_vol)

    stage = _stage(g)

    from gegede.export.usd.paths import proto_path, sanitize
    pl_path = proto_path('outer_vol') + '/' + sanitize('pl_inst')
    place = stage.GetPrimAtPath(pl_path)
    assert place.IsValid()
    assert place.IsInstanceable()


# ---------------------------------------------------------------------------
# Unsupported shape in Phase 1
# ---------------------------------------------------------------------------

def test_unsupported_shape_raises():
    '''A Phase-2 shape (e.g. Torus) must raise NotImplementedError.'''
    g, _ = _build_geom(lambda g: g.shapes.Torus('MyTorus'))
    with pytest.raises(NotImplementedError):
        usd.convert(g)
