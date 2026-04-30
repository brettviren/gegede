'''
GeGeDe USD exporter — targets UsdGeom for visualization and interchange.

This exporter produces OpenUSD output (.usda text or .usdc crate) from a
gegede.construct.Geometry object.  It uses the references+instancing model
so that repeated volume placements map to USD native scenegraph instances.

USD is a *visualization* target; GDML remains the authoritative Geant4
simulation input.  Boolean shapes (Union/Subtraction/Intersection) are
tessellated to UsdGeomMesh; USD has no native CSG.

Usage
-----
    gegede --format usd -o detector.usda config.cfg
    gegede -o detector.usda config.cfg       # extension auto-detected
    gegede -o detector.usdc config.cfg       # binary crate

Python API
----------
    import gegede.export.usd as usd
    obj = usd.convert(geom)                  # produces UsdGeometry wrapper
    text = usd.dumps(obj)                    # returns USDA text string
    usd.output(obj, 'detector.usda')         # writes to file
    usd.validate_object(obj)                 # compliance check

Optional dependencies
---------------------
    usd-core>=24   (the pxr Python bindings)
    trimesh>=4     (primitive and mesh tessellation)
    manifold3d>=2  (robust boolean CSG backend for trimesh)

Install: pip install 'gegede[usd]'
         or: uv sync --extra usd

Phase 1 shapes
--------------
  Intrinsics: Box (UsdGeomCube+scale), Sphere (full), Tubs (full, no inner radius)
  Mesh: Cone, Trapezoid, Union, Subtraction, Intersection
  Not yet (Phase 2): all other 14 shape types
'''
from __future__ import annotations

import os
import tempfile
import logging
from dataclasses import dataclass, field

from pxr import Usd, UsdGeom, Sdf

log = logging.getLogger('gegede')


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

@dataclass
class UsdGeometry:
    '''Wrapper returned by convert(); holds stage + options + source geometry.'''
    stage: 'Usd.Stage'
    opts:  object            # StageOpts dataclass
    geom:  object            # gegede.construct.Geometry


# ---------------------------------------------------------------------------
# Public exporter API
# ---------------------------------------------------------------------------

def convert(geom, *,
            meters_per_unit: float = 0.001,
            up_axis: str = 'Z',
            tess_segments: int = 32,
            tess_tolerance=None,
            default_format: str = 'usda',
            instanceable: bool = True) -> UsdGeometry:
    '''Convert a Geometry to USD.

    Parameters
    ----------
    geom            : gegede.construct.Geometry
    meters_per_unit : float, default 0.001
        Stage length unit in metres.  Default 0.001 = 1 stage unit = 1 mm,
        matching Geant4's internal length unit.
    up_axis         : 'Z' (default, matching Geant4) or 'Y'
    tess_segments   : int, default 32
        Circular subdivision count for tessellated solids.
    tess_tolerance  : float or None
        Mesh tolerance passed to manifold3d.  None = library default.
    default_format  : 'usda' or 'usdc'
        Format used when output filename has extension '.usd'.
    instanceable    : bool, default True
        Emit references+instanceable for repeated volume placements.
        Set False to get a flat (non-instanced) scene for debugging.

    Returns
    -------
    UsdGeometry wrapper containing the in-memory Usd.Stage.
    '''
    from gegede.export.usd.units import StageOpts
    from gegede.export.usd.materials import build_all_materials
    from gegede.export.usd.structure import build_structure

    opts = StageOpts(
        meters_per_unit=meters_per_unit,
        up_axis=up_axis,
        tess_segments=tess_segments,
        tess_tolerance=tess_tolerance,
        default_format=default_format,
        instanceable=instanceable,
    )

    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageMetersPerUnit(stage, opts.meters_per_unit)
    UsdGeom.SetStageUpAxis(stage, opts.up_axis)

    # Default prim /World
    world_prim = UsdGeom.Xform.Define(stage, '/World')
    stage.SetDefaultPrim(world_prim.GetPrim())

    # /Library scope — keeps prototypes and materials out of the default-prim traversal
    UsdGeom.Scope.Define(stage, '/Library')
    UsdGeom.Scope.Define(stage, '/Library/Volumes')
    UsdGeom.Scope.Define(stage, '/Library/Materials')

    # Materials
    mesh_cache = {}
    mat_map = build_all_materials(stage, geom, opts)

    # Volumes, placements, world
    build_structure(stage, geom, opts, mat_map, mesh_cache)

    return UsdGeometry(stage=stage, opts=opts, geom=geom)


def dumps(obj: UsdGeometry, fmt: str = 'usda') -> str | bytes:
    '''Serialise the stage to a string (USDA) or bytes (USDC).

    Parameters
    ----------
    obj : UsdGeometry returned by convert()
    fmt : 'usda' (default) or 'usdc'
    '''
    if fmt == 'usda':
        return obj.stage.GetRootLayer().ExportToString()

    if fmt == 'usdc':
        # Crate format is file-backed in the USD C++ API; round-trip via tempfile.
        with tempfile.NamedTemporaryFile(suffix='.usdc', delete=False) as fh:
            tmp = fh.name
        try:
            obj.stage.GetRootLayer().Export(tmp, args={'format': 'usdc'})
            with open(tmp, 'rb') as fh:
                return fh.read()
        finally:
            os.unlink(tmp)

    raise ValueError(f"Unknown USD dumps format: {fmt!r}. Use 'usda' or 'usdc'.")


def output(obj: UsdGeometry, filename: str) -> None:
    '''Write the stage to *filename*, choosing format from the extension.

    .usda  → ASCII text
    .usdc  → crate binary
    .usd   → uses obj.opts.default_format (default: usda)
    '''
    ext = os.path.splitext(filename)[1].lstrip('.').lower()
    layer = obj.stage.GetRootLayer()

    if ext == 'usda':
        layer.Export(filename, args={'format': 'usda'})
    elif ext == 'usdc':
        layer.Export(filename, args={'format': 'usdc'})
    elif ext in ('usd', ''):
        layer.Export(filename, args={'format': obj.opts.default_format})
    else:
        raise ValueError(f"Unrecognised USD extension '.{ext}'.  Use .usda, .usdc, or .usd.")


def validate_object(obj: UsdGeometry) -> bool:
    '''Run UsdUtils.ComplianceChecker on the in-memory stage.

    Returns True on success, raises ValueError on hard failures.
    '''
    from gegede.export.usd.validate import validate_object as _validate
    return _validate(obj)
