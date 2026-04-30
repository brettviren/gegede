'''
USD prim path construction and identifier sanitization.
'''
import re

_BAD_CHARS = re.compile(r'[^A-Za-z0-9_]')


def sanitize(name):
    '''Return a valid USD identifier from an arbitrary string.'''
    if not name:
        return '_unnamed'
    s = _BAD_CHARS.sub('_', str(name))
    if s[0].isdigit():
        s = '_' + s
    return s


def mat_path(name):
    return f'/Library/Materials/{sanitize(name)}'


def proto_path(volname):
    return f'/Library/Volumes/{sanitize(volname)}'


def shape_path(volname):
    return f'/Library/Volumes/{sanitize(volname)}/Shape'


def placement_path(parent_proto, placename, idx=None):
    if placename and placename not in ('center', 'identity'):
        seg = sanitize(placename)
    elif idx is not None:
        seg = f'_phys{idx:06d}'
    else:
        seg = '_phys'
    return f'{parent_proto}/{seg}'


def world_placement_path(worldvolname):
    return f'/World/{sanitize(worldvolname)}'
