#!/usr/bin/env python
'''Export GeGeDe to an Open Inventor scene graph.

A SG allows for a more flexible layout than is required to represent
the nested volume structure followed by GeGeDe.  A choice is made to
map this into an SG.

Bot logical volumes (LV) and placements (PV) are represented with
SoSeparators.  An LV SoSeparator may contain zero or more PVs followed
by an optional SoMaterial and a SoShape.  If an LV contains only PVs
it is an assembly.  A PV is a SoSeparator with a transform and an LV.

'''

from collections import defaultdict
from pivy import coin

spatial_units = 'mm'

def pos2trans(obj):
    pos = coin.SoTransform()
    pos.translation = (obj.x.to('mm').magnitude,
                       obj.y.to('mm').magnitude,
                       obj.z.to('mm').magnitude)
    return pos

def rot2trans(obj):
    tot = coin.SoGroup()
    for ang,axis in[(obj.x.to('radian').magnitude,coin.SoRotationXYZ.X),
                    (obj.y.to('radian').magnitude,coin.SoRotationXYZ.Y),
                    (obj.z.to('radian').magnitude,coin.SoRotationXYZ.Z)]:
        if ang == 0.0:
            continue
        r = coin.SoRotationXYZ()
        r.axis = axis
        r.angle = ang
        tot.addChild(r)
    assert len(tot), 'Failed to add any rotations for %s' % str(obj.name)
    return tot

# http://stackoverflow.com/questions/6283080/random-unit-vector-in-multi-dimensional-space
from random import gauss
def make_rand_vector(dims = 3):
    vec = [gauss(0, 1) for i in range(dims)]
    mag = sum(x**2 for x in vec) ** .5
    return [x/mag for x in vec]

def mat2mat(obj):
    '''
    Convert gegede material to SoMaterial.  They have nothing in common.

    ambientColor
    diffuseColor
    specularColor
    emissiveColor
    shininess
    transparency
    '''
    # fixme: add checking of hints
    out = coin.SoMaterial()
    out.diffuseColor = make_rand_vector()
    out.specularColor = make_rand_vector()
    out.ambientColor = make_rand_vector()
    out.transparency = 0.5
    return out

def shape2shape(name, geom):
    '''
    Convert from gegede shape to a SoShape
    '''
    obj = geom.get_shape(name)
    if type(obj).__name__ == 'Box':
        box = coin.SoCube()
        box.width  = 2.0*obj.dx.to(spatial_units).magnitude
        box.height = 2.0*obj.dy.to(spatial_units).magnitude
        box.depth  = 2.0*obj.dz.to(spatial_units).magnitude
        return box

    if type(obj).__name__ == 'Tubs':
        tub = coin.SoCylinder()
        tub.radius = obj.rmax.to(spatial_units).magnitude
        tub.height = 0.5*obj.dz.to(spatial_units).magnitude
        # fixme: no built-in support of rmin, nor start/stop angles - need to make boolean
        return tub

    if type(obj).__name__ == 'Sphere':
        sph = coin.SoSphere()
        sph.radius = obj.rmax.to(spatial_units).magnitude
        # fixme: no built-in support of rmin, nor start/stop angles - need to make boolean
        return sph

    if type(obj).__name__ == 'Boolean':
        print 'WARNING: Boolean shapes are not supported, simply using the first shape for %s' % obj.name
        return shape2shape(obj.first, geom)

    raise ValueError, 'Unsupported shape for scenegraph: "%s"' % type(obj).__name__

def convert(geom):
    '''
    Return the top node of an Open Inventor scenegraph made from the geom.
    '''

    materials = dict()
    for obj in geom.store.matter.values():
        materials[obj.name] = mat2mat(obj)
        continue

    positions = dict()
    rotations = dict()
    for obj in geom.store.structure.values():
        typename = type(obj).__name__.lower()
        if typename == 'position':
            positions[obj.name] = pos2trans(obj)
            continue
        if typename == 'rotation':
            rotations[obj.name] = rot2trans(obj)
            continue

    placements = defaultdict(coin.SoSeparator)
    volumes = defaultdict(coin.SoSeparator)
    for obj in geom.store.structure.values():
        typename = type(obj).__name__.lower()
        if typename != 'placement':
            continue
        pnode = placements[obj.name]
        if obj.pos:
            pos = positions[obj.pos]
            pnode.addChild(pos)
        if obj.rot:
            rot = rotations[obj.rot]
            pnode.addChild(rot)
        vol = volumes[obj.volume]
        pnode.addChild(vol)
    
    for obj in geom.store.structure.values():
        typename = type(obj).__name__.lower()
        if typename != 'volume':
            continue
        vol = volumes[obj.name]
        for place in obj.placements:
            vol.addChild(placements[place])
        if obj.shape:
            vol.addChild(shape2shape(obj.shape, geom))
            vol.addChild(materials[obj.material])
        
    return volumes[geom.world]

def output(top, filename):
    '''
    '''
    writer = coin.SoWriteAction()
    out = writer.getOutput()
    out.openFile(filename)
    out.setBinary(False)
    writer.apply(top)
    out.closeFile()
