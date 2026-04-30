'''
Volume prototype and placement tree construction for the USD exporter.

Strategy: references-with-instancing.
  /Library/Volumes/<volname>       — one prototype per gegede Volume
  /Library/Volumes/<volname>/Shape — the shape prim under the prototype
  /Library/Volumes/<volname>/<pl>  — child placements inside the prototype
  /World/<worldvolname>            — the single world placement (no transform)
'''
import logging

log = logging.getLogger('gegede')

import gegede.iter as _iter
from gegede.export.usd.paths import (
    proto_path, shape_path, placement_path, world_placement_path
)
from gegede.export.usd.units import to_stage_length, to_degrees
from gegede.export.usd.shapes import make_shape_prim


def _is_placeholder(name):
    '''True when a pos/rot name is a GeGeDe "no transform" placeholder.'''
    return not name or name in ('center', 'identity')


def _apply_transform(xformable, place, geom, opts):
    '''Set translate + rotateXYZ ops on an Xformable prim from a Placement.'''
    from pxr import UsdGeom, Gf

    store = geom.store.structure

    pos_name = place.pos
    rot_name = place.rot

    if not _is_placeholder(pos_name):
        pos_obj = store.get(pos_name)
        if pos_obj is not None and type(pos_obj).__name__ == 'Position':
            op = xformable.AddTranslateOp(precision=UsdGeom.XformOp.PrecisionDouble)
            op.Set(Gf.Vec3d(
                to_stage_length(pos_obj.x, opts),
                to_stage_length(pos_obj.y, opts),
                to_stage_length(pos_obj.z, opts),
            ))
        else:
            log.warning('USD: placement pos %r not found in structure store', pos_name)

    if not _is_placeholder(rot_name):
        rot_obj = store.get(rot_name)
        if rot_obj is not None and type(rot_obj).__name__ == 'Rotation':
            op = xformable.AddRotateXYZOp(precision=UsdGeom.XformOp.PrecisionFloat)
            op.Set(Gf.Vec3f(
                to_degrees(rot_obj.x),
                to_degrees(rot_obj.y),
                to_degrees(rot_obj.z),
            ))
        else:
            log.warning('USD: placement rot %r not found in structure store', rot_name)


def _make_placement_prim(stage, pp, ref_proto_path, place, geom, opts):
    '''Create an Xform placement prim that references a volume prototype.'''
    from pxr import UsdGeom

    prim = UsdGeom.Xform.Define(stage, pp)
    prim.GetPrim().GetReferences().AddInternalReference(ref_proto_path)
    if opts.instanceable:
        prim.GetPrim().SetInstanceable(True)
    _apply_transform(prim, place, geom, opts)
    return prim


def build_structure(stage, geom, opts, mat_map, mesh_cache):
    '''Build all volume prototypes and the world placement on the stage.'''
    from pxr import UsdGeom, UsdShade

    store = geom.store.structure
    volumes = _iter.ascending(store, geom.world)

    for vol in volumes:
        pp = proto_path(vol.name)
        UsdGeom.Xform.Define(stage, pp)

        # Shape child
        if vol.shape:
            shape_obj = geom.store.shapes.get(vol.shape)
            if shape_obj is not None:
                sp = shape_path(vol.name)
                make_shape_prim(stage, sp, shape_obj, geom, mesh_cache, opts)

                # Bind material on the Shape prim
                mat_name = vol.material
                if mat_name and mat_name in mat_map:
                    shape_prim = stage.GetPrimAtPath(sp)
                    if shape_prim.IsValid():
                        UsdShade.MaterialBindingAPI(shape_prim).Bind(mat_map[mat_name])

        # Child placement prims inside this prototype
        for idx, pname in enumerate(vol.placements):
            place = store.get(pname)
            if place is None or type(place).__name__ != 'Placement':
                log.warning('USD: placement %r not found or not a Placement', pname)
                continue
            child_vol_name = place.volume
            child_proto = proto_path(child_vol_name)
            pp_child = placement_path(pp, pname, idx)
            _make_placement_prim(stage, pp_child, child_proto, place, geom, opts)

    # World placement at /World/<worldvolname>
    world_pp = world_placement_path(geom.world)
    world_prim = UsdGeom.Xform.Define(stage, world_pp)
    world_prim.GetPrim().GetReferences().AddInternalReference(proto_path(geom.world))
    if opts.instanceable:
        world_prim.GetPrim().SetInstanceable(True)
    # No transform: world is at origin
