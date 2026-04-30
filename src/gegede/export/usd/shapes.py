'''
Per-shape dispatch for the USD exporter.

Phase 1 supports: Box (UsdGeomCube + scale), Sphere (full only),
Tubs (full, no inner radius), Cone (mesh), Trapezoid (mesh),
Union/Subtraction/Intersection/Boolean (mesh via tessellate).

All other shapes raise NotImplementedError; Phase 2 will add them.
'''
from gegede.export.usd.units import to_stage_length, to_degrees, is_zero, is_full_circle
from gegede.export.usd.tessellate import write_mesh_prim, mesh_for_shape


def make_shape_prim(stage, path, shape, geom, mesh_cache, opts):
    '''Create the Shape prim under a prototype.  Returns the prim.'''
    typename = type(shape).__name__
    handler = _DISPATCH.get(typename)
    if handler is None:
        raise NotImplementedError(
            f"USD exporter Phase 1: shape '{typename}' not yet supported. "
            f"Phase 2 will add tessellation for this type. "
            f"See src/gegede/export/usd/shapes.py"
        )
    return handler(stage, path, shape, geom, mesh_cache, opts)


# ---------------------------------------------------------------------------
# Individual shape handlers
# ---------------------------------------------------------------------------

def _shape_box(stage, path, shape, geom, mesh_cache, opts):
    '''Box → UsdGeomCube(size=1) + xformOp:scale to full extents.'''
    from pxr import UsdGeom, Gf

    cube = UsdGeom.Cube.Define(stage, path)
    cube.GetSizeAttr().Set(1.0)

    sx = to_stage_length(shape.dx, opts) * 2.0
    sy = to_stage_length(shape.dy, opts) * 2.0
    sz = to_stage_length(shape.dz, opts) * 2.0

    xf = UsdGeom.Xformable(cube)
    xf.AddScaleOp().Set(Gf.Vec3f(sx, sy, sz))

    half = Gf.Vec3f(sx * 0.5, sy * 0.5, sz * 0.5)
    cube.GetExtentAttr().Set([-half, half])

    return cube.GetPrim()


def _shape_sphere(stage, path, shape, geom, mesh_cache, opts):
    '''Sphere → UsdGeomSphere if full (rmin=0, full phi/theta), else Phase-2 mesh.'''
    from pxr import UsdGeom, Gf

    # Fall through to mesh for anything non-trivial
    rmin  = float(shape.rmin.to('m').magnitude)
    if (rmin > 1e-9
            or not is_full_circle(shape.dphi)
            or not is_zero(shape.sphi)
            or not is_zero(shape.stheta)
            or abs(float(shape.dtheta.to('rad').magnitude) - 3.14159265) > 1e-4):
        raise NotImplementedError(
            f"USD exporter Phase 1: Sphere with rmin>0 or partial angular range "
            f"requires Phase-2 tessellation."
        )

    sph = UsdGeom.Sphere.Define(stage, path)
    r = to_stage_length(shape.rmax, opts)
    sph.GetRadiusAttr().Set(r)
    sph.GetExtentAttr().Set([Gf.Vec3f(-r, -r, -r), Gf.Vec3f(r, r, r)])
    return sph.GetPrim()


def _shape_tubs(stage, path, shape, geom, mesh_cache, opts):
    '''Tubs → UsdGeomCylinder if full (rmin=0, dphi=360°), else Phase-2 mesh.'''
    from pxr import UsdGeom, Gf

    rmin = float(shape.rmin.to('m').magnitude)
    if (rmin > 1e-9
            or not is_full_circle(shape.dphi)
            or not is_zero(shape.sphi)):
        raise NotImplementedError(
            f"USD exporter Phase 1: Tubs with rmin>0 or partial phi "
            f"requires Phase-2 tessellation."
        )

    cyl = UsdGeom.Cylinder.Define(stage, path)
    h = to_stage_length(shape.dz, opts) * 2.0
    r = to_stage_length(shape.rmax, opts)
    cyl.GetHeightAttr().Set(h)
    cyl.GetRadiusAttr().Set(r)
    cyl.GetAxisAttr().Set('Z')
    cyl.GetExtentAttr().Set([Gf.Vec3f(-r, -r, -h * 0.5), Gf.Vec3f(r, r, h * 0.5)])
    return cyl.GetPrim()


def _shape_via_mesh(stage, path, shape, geom, mesh_cache, opts):
    '''Generic path: tessellate shape to a UsdGeomMesh.'''
    tmesh = mesh_for_shape(shape, geom, mesh_cache, opts)
    return write_mesh_prim(stage, path, tmesh, opts)


# Explicit aliases so the dispatch table is readable
_shape_cone        = _shape_via_mesh
_shape_trapezoid   = _shape_via_mesh
_shape_union       = _shape_via_mesh
_shape_subtraction = _shape_via_mesh
_shape_intersection = _shape_via_mesh
_shape_boolean     = _shape_via_mesh


_DISPATCH = {
    'Box':          _shape_box,
    'Sphere':       _shape_sphere,
    'Tubs':         _shape_tubs,
    'Cone':         _shape_cone,
    'Trapezoid':    _shape_trapezoid,
    'Union':        _shape_union,
    'Subtraction':  _shape_subtraction,
    'Intersection': _shape_intersection,
    'Boolean':      _shape_boolean,
}
