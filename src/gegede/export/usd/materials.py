'''
Build UsdShadeMaterial prims for gegede matter objects.
Physics data is attached as customData["gegede"] for preservation across tools.

USD customData supports nested dicts with scalar leaves (str, int, float, bool).
Complex fields (element compositions, optical property tables) are serialised to
a JSON string so they round-trip through any USD tool without type conversion issues.
'''
import hashlib
import json
import logging

log = logging.getLogger('gegede')


def _color_for(name):
    '''Deterministic RGB color from material name (0..1 per channel).'''
    from pxr import Gf
    digest = hashlib.md5(name.encode()).digest()
    return Gf.Vec3f(digest[0] / 255.0, digest[1] / 255.0, digest[2] / 255.0)


def _safe_float(q, unit):
    '''Convert Pint Quantity to float in given unit; return None on failure.'''
    try:
        return float(q.to(unit).magnitude)
    except Exception:
        return None


def _plain(v):
    '''Convert a value to a JSON-serialisable Python primitive.'''
    if isinstance(v, (int, float, str, bool)):
        return v
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    # Pint Quantity — try common unit conversions
    for unit in ('eV', 'm', 'g/mole', 'g/cc', 'rad', 'deg'):
        try:
            return float(v.to(unit).magnitude)
        except Exception:
            continue
    try:
        return float(v)
    except Exception:
        return str(v)


def _matter_custom_data(matter):
    '''Build the gegede physics payload dict for a matter object.

    Scalar fields are stored as proper USD dict types (float, int, str).
    Complex fields (compositions, property tables) are JSON-encoded strings
    so they survive VtDictionary round-trips without type-mismatch errors.
    '''
    typename = type(matter).__name__
    data = {'type': typename}

    # --- scalars ---
    for attr, unit, key in [
        ('a',       'g/mole', 'a_g_per_mole'),
        ('density', 'g/cc',   'density_g_per_cm3'),
    ]:
        val = getattr(matter, attr, None)
        if val is not None:
            fval = _safe_float(val, unit)
            if fval is not None:
                data[key] = fval

    z = getattr(matter, 'z', None)
    if z is not None:
        data['z'] = z

    sym = getattr(matter, 'symbol', None)
    if sym:
        data['symbol'] = str(sym)

    # --- complex lists → JSON string (safe for all USD tools) ---
    complex_parts = {}
    for attr in ('isotopes', 'elements', 'components'):
        lst = getattr(matter, attr, None)
        if lst:
            complex_parts[attr] = [[str(n), _plain(v)] for (n, v) in lst]

    props = getattr(matter, 'properties', None)
    if props:
        serialised = []
        for (pname, rows) in props:
            serialised.append({'name': str(pname), 'rows': _plain(rows)})
        complex_parts['properties'] = serialised

    if complex_parts:
        data['gegede_json'] = json.dumps(complex_parts)

    return data


def make_material(stage, matter, opts, world_material_name=None):
    '''Define a UsdShadeMaterial for a gegede matter object.'''
    from pxr import UsdShade, Sdf
    from gegede.export.usd.paths import mat_path

    path = mat_path(matter.name)
    mat = UsdShade.Material.Define(stage, path)

    shd = UsdShade.Shader.Define(stage, path + '/PreviewShader')
    shd.CreateIdAttr('UsdPreviewSurface')

    color = _color_for(matter.name)
    shd.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(color)
    shd.CreateInput('roughness',    Sdf.ValueTypeNames.Float).Set(0.5)

    # World material semi-transparent so interior is visible in usdview
    opacity = 0.15 if matter.name == world_material_name else 1.0
    shd.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(opacity)

    mat.CreateSurfaceOutput().ConnectToSource(shd.ConnectableAPI(), 'surface')

    # Attach physics payload — guard against USD dict serialisation edge cases
    try:
        mat.GetPrim().SetCustomDataByKey('gegede', _matter_custom_data(matter))
    except Exception as exc:
        log.warning('USD: could not set customData for material %r: %s', matter.name, exc)

    return mat


def build_all_materials(stage, geom, opts):
    '''Build all materials and return a {name: UsdShade.Material} map.'''
    # Identify the world volume's material for opacity hint
    world_mat = None
    if geom.world:
        world_vol = geom.store.structure.get(geom.world)
        if world_vol is not None:
            world_mat = getattr(world_vol, 'material', None)

    mat_map = {}
    for name, matter in geom.store.matter.items():
        mat = make_material(stage, matter, opts, world_material_name=world_mat)
        mat_map[name] = mat
    return mat_map
