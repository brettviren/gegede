'''
Tessellation of GeGeDe shapes into trimesh.Trimesh objects and USD mesh prims.

For Phase 1: Cone, Trapezoid, and Boolean operations (Union/Subtraction/Intersection).
Phase 2 will add the remaining 14 shapes.

Boolean operations use manifold3d as the trimesh boolean backend.
'''
import logging
import numpy as np

log = logging.getLogger('gegede')

try:
    import trimesh
    import trimesh.creation
    import trimesh.boolean
    import manifold3d as _manifold3d_check  # noqa – ensures the backend is importable
    HAS_TESSELLATE = True
except ImportError:
    HAS_TESSELLATE = False


def _require_tessellate():
    if not HAS_TESSELLATE:
        raise ImportError(
            'Tessellation requires trimesh and manifold3d. '
            'Install with: pip install trimesh manifold3d'
        )


def write_mesh_prim(stage, path, tmesh, opts):
    '''Write a trimesh.Trimesh as a UsdGeomMesh prim. Returns the prim.'''
    from pxr import UsdGeom, Vt, Gf

    mesh_prim = UsdGeom.Mesh.Define(stage, path)

    # Convert vertices to stage units (already in metres via to_stage_length callers;
    # but tessellation helpers below work in raw Pint → m values; we scale here).
    verts_mm = tmesh.vertices / opts.meters_per_unit
    mesh_prim.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*v) for v in verts_mm]))

    faces = tmesh.faces
    mesh_prim.GetFaceVertexCountsAttr().Set(Vt.IntArray([3] * len(faces)))
    mesh_prim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(faces.flatten().tolist()))

    mesh_prim.GetSubdivisionSchemeAttr().Set(UsdGeom.Tokens.none)

    # Extent bounding box
    bb = tmesh.bounds / opts.meters_per_unit
    mesh_prim.GetExtentAttr().Set(
        Vt.Vec3fArray([Gf.Vec3f(*bb[0]), Gf.Vec3f(*bb[1])])
    )

    return mesh_prim.GetPrim()


# ---------------------------------------------------------------------------
# Per-shape tessellation helpers
# All helpers return a trimesh.Trimesh with vertices in METRES (raw SI).
# Conversion to stage units is done in write_mesh_prim.
# ---------------------------------------------------------------------------

def _q2m(q):
    '''Pint Quantity (length) → float in metres.'''
    return float(q.to('m').magnitude)


def _q2rad(q):
    '''Pint Quantity (angle) → float in radians.'''
    return float(q.to('rad').magnitude)


def mesh_box(shape, opts):
    '''Box → trimesh box with full extents (2*dx × 2*dy × 2*dz) in metres.
    Used when a Box is a boolean operand; the Shape prim uses a Cube intrinsic.
    '''
    _require_tessellate()
    dx = _q2m(shape.dx)
    dy = _q2m(shape.dy)
    dz = _q2m(shape.dz)
    return trimesh.creation.box(extents=[2.0 * dx, 2.0 * dy, 2.0 * dz])


def mesh_sphere(shape, opts):
    '''Full Sphere → trimesh icosphere with radius=rmax in metres.
    Used when a Sphere is a boolean operand; the Shape prim uses a Sphere intrinsic.
    '''
    _require_tessellate()
    r = _q2m(shape.rmax)
    return trimesh.creation.icosphere(radius=r, subdivisions=2)


def mesh_trapezoid(shape, opts):
    '''Trapezoid (G4Trd): 8 vertex rectangular frustum.
    dx1,dy1 are half-extents at z=-dz; dx2,dy2 at z=+dz.
    '''
    _require_tessellate()
    dx1 = _q2m(shape.dx1)
    dx2 = _q2m(shape.dx2)
    dy1 = _q2m(shape.dy1)
    dy2 = _q2m(shape.dy2)
    dz  = _q2m(shape.dz)

    # 8 vertices: bottom face (z=-dz), top face (z=+dz)
    verts = np.array([
        [-dx1, -dy1, -dz], [ dx1, -dy1, -dz],
        [ dx1,  dy1, -dz], [-dx1,  dy1, -dz],   # bottom (0-3)
        [-dx2, -dy2,  dz], [ dx2, -dy2,  dz],
        [ dx2,  dy2,  dz], [-dx2,  dy2,  dz],   # top    (4-7)
    ], dtype=float)

    # 12 triangles: 2 per rectangular face × 6 faces
    faces = np.array([
        # bottom (-z)
        [0, 2, 1], [0, 3, 2],
        # top (+z)
        [4, 5, 6], [4, 6, 7],
        # front (-y)
        [0, 1, 5], [0, 5, 4],
        # back (+y)
        [2, 3, 7], [2, 7, 6],
        # left (-x)
        [3, 0, 4], [3, 4, 7],
        # right (+x)
        [1, 2, 6], [1, 6, 5],
    ], dtype=int)

    return trimesh.Trimesh(vertices=verts, faces=faces, process=False)


def mesh_cone(shape, opts):
    '''Cone (G4Cons): truncated cone with two radii, built by revolving a trapezoid profile.
    Uses trimesh.creation.cylinder or a manual loft for the truncated case.
    For Phase 1 this is always tessellated (no USD intrinsic used).
    '''
    _require_tessellate()
    import trimesh.creation as tc

    segs = opts.tess_segments
    rmin1 = _q2m(shape.rmin1)
    rmax1 = _q2m(shape.rmax1)
    rmin2 = _q2m(shape.rmin2)
    rmax2 = _q2m(shape.rmax2)
    dz    = _q2m(shape.dz)

    # Build via revolve: profile in (r, z) plane, swept 360°
    # Profile for rmax (outer shell)
    nsegs = segs
    theta = np.linspace(0, 2 * np.pi, nsegs, endpoint=False)

    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    # Bottom ring at z=-dz, top ring at z=+dz
    bot_outer = np.column_stack([rmax1 * cos_t, rmax1 * sin_t, np.full(nsegs, -dz)])
    top_outer = np.column_stack([rmax2 * cos_t, rmax2 * sin_t, np.full(nsegs, +dz)])

    meshes = []

    # Outer lateral surface
    verts_outer = np.vstack([bot_outer, top_outer])
    faces_outer = []
    for i in range(nsegs):
        j = (i + 1) % nsegs
        faces_outer += [[i, j, nsegs + i], [j, nsegs + j, nsegs + i]]
    meshes.append(trimesh.Trimesh(vertices=verts_outer,
                                  faces=np.array(faces_outer), process=False))

    # Bottom cap at z=-dz
    if rmax1 > 0:
        _add_annular_cap(meshes, rmin1, rmax1, -dz, nsegs, flip=True)

    # Top cap at z=+dz
    if rmax2 > 0:
        _add_annular_cap(meshes, rmin2, rmax2, +dz, nsegs, flip=False)

    # Inner lateral surface (if hollow)
    if rmin1 > 0 or rmin2 > 0:
        bot_inner = np.column_stack([rmin1 * cos_t, rmin1 * sin_t, np.full(nsegs, -dz)])
        top_inner = np.column_stack([rmin2 * cos_t, rmin2 * sin_t, np.full(nsegs, +dz)])
        verts_inner = np.vstack([bot_inner, top_inner])
        faces_inner = []
        for i in range(nsegs):
            j = (i + 1) % nsegs
            # reversed winding for inner surface (normals point inward)
            faces_inner += [[i, nsegs + i, j], [j, nsegs + i, nsegs + j]]
        meshes.append(trimesh.Trimesh(vertices=verts_inner,
                                      faces=np.array(faces_inner), process=False))

    return trimesh.util.concatenate(meshes)


def _add_annular_cap(meshes, rmin, rmax, z, nsegs, flip):
    '''Add an annular disc (or solid disc if rmin==0) at the given z.'''
    theta = np.linspace(0, 2 * np.pi, nsegs, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    if rmin <= 0:
        # Solid disc: fan triangulation from centre
        outer = np.column_stack([rmax * cos_t, rmax * sin_t, np.full(nsegs, z)])
        centre = np.array([[0.0, 0.0, z]])
        verts = np.vstack([centre, outer])  # 0 = centre, 1..nsegs = outer
        faces = []
        for i in range(nsegs):
            j = (i + 1) % nsegs + 1
            i1 = i + 1
            if flip:
                faces.append([0, j, i1])
            else:
                faces.append([0, i1, j])
        meshes.append(trimesh.Trimesh(vertices=verts,
                                      faces=np.array(faces), process=False))
    else:
        # Annular disc
        inner = np.column_stack([rmin * cos_t, rmin * sin_t, np.full(nsegs, z)])
        outer = np.column_stack([rmax * cos_t, rmax * sin_t, np.full(nsegs, z)])
        verts = np.vstack([inner, outer])
        faces = []
        for i in range(nsegs):
            j = (i + 1) % nsegs
            if flip:
                faces += [[i, nsegs + i, j], [j, nsegs + i, nsegs + j]]
            else:
                faces += [[i, j, nsegs + i], [j, nsegs + j, nsegs + i]]
        meshes.append(trimesh.Trimesh(vertices=verts,
                                      faces=np.array(faces), process=False))


def _rot_matrix(rot_obj):
    '''Build a 4×4 rotation matrix from a Rotation namedtuple (Euler X,Y,Z in Geant4 convention).
    Geant4 applies X first, then Y, then Z: M = Rz · Ry · Rx
    '''
    rx = _q2rad(rot_obj.x)
    ry = _q2rad(rot_obj.y)
    rz = _q2rad(rot_obj.z)

    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    cz, sz = np.cos(rz), np.sin(rz)

    # Rz · Ry · Rx
    R = np.array([
        [cy*cz, cz*sx*sy - cx*sz, cx*cz*sy + sx*sz, 0],
        [cy*sz, cx*cz + sx*sy*sz, cx*sy*sz - cz*sx, 0],
        [  -sy,          cy*sx,           cx*cy, 0],
        [    0,              0,               0, 1],
    ], dtype=float)
    return R


def mesh_for_shape(shape, geom, cache, opts):
    '''Return a trimesh.Trimesh for the given shape, using cache to avoid re-tessellation.
    Vertices are in metres (SI).
    '''
    name = shape.name
    if name in cache:
        return cache[name]

    typename = type(shape).__name__
    _TESS_DISPATCH = {
        # Primitives that have USD intrinsics for Shape prims but need mesh
        # representations when used as boolean operands.
        'Box':       lambda s: mesh_box(s, opts),
        'Sphere':    lambda s: mesh_sphere(s, opts),
        # Shapes always tessellated
        'Trapezoid': lambda s: mesh_trapezoid(s, opts),
        'Cone':      lambda s: mesh_cone(s, opts),
        # Boolean compositions
        'Union':        lambda s: _mesh_boolean(s, 'union',        geom, cache, opts),
        'Subtraction':  lambda s: _mesh_boolean(s, 'difference',   geom, cache, opts),
        'Intersection': lambda s: _mesh_boolean(s, 'intersection', geom, cache, opts),
        'Boolean':      lambda s: _mesh_boolean_legacy(s,           geom, cache, opts),
    }

    if typename not in _TESS_DISPATCH:
        raise NotImplementedError(
            f"USD exporter: tessellation for '{typename}' not yet implemented (Phase 2). "
            f"See src/gegede/export/usd/tessellate.py"
        )

    tmesh = _TESS_DISPATCH[typename](shape)
    cache[name] = tmesh
    return tmesh


def _mesh_boolean(shape, op, geom, cache, opts):
    _require_tessellate()
    first_shape  = geom.store.shapes[shape.first]
    second_shape = geom.store.shapes[shape.second]

    first_mesh  = mesh_for_shape(first_shape,  geom, cache, opts).copy()
    second_mesh = mesh_for_shape(second_shape, geom, cache, opts).copy()

    # Apply the boolean's own position and rotation to the second operand
    _transform_second(second_mesh, shape.pos, shape.rot, geom)

    return trimesh.boolean.boolean_manifold([first_mesh, second_mesh], op)


def _mesh_boolean_legacy(shape, geom, cache, opts):
    '''Handle the deprecated Boolean type with explicit type string.'''
    op_map = {
        'union':        'union',
        'subtraction':  'difference',
        'intersection': 'intersection',
    }
    op = op_map.get(shape.type)
    if op is None:
        raise ValueError(f"Unknown Boolean.type: {shape.type!r}")
    return _mesh_boolean(shape, op, geom, cache, opts)


def _transform_second(mesh, pos_name, rot_name, geom):
    '''Apply a GeGeDe Position + Rotation to a trimesh in-place (metres).'''
    store = geom.store.structure
    if rot_name and rot_name not in ('identity', 'center', '', None):
        rot_obj = store.get(rot_name)
        if rot_obj is not None and type(rot_obj).__name__ == 'Rotation':
            mesh.apply_transform(_rot_matrix(rot_obj))

    if pos_name and pos_name not in ('center', '', None):
        pos_obj = store.get(pos_name)
        if pos_obj is not None and type(pos_obj).__name__ == 'Position':
            tx = _q2m(pos_obj.x)
            ty = _q2m(pos_obj.y)
            tz = _q2m(pos_obj.z)
            mesh.apply_translation([tx, ty, tz])
