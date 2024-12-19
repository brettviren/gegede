#!/usr/bin/env python
'''
Export to ROOT TGeo
'''

import ROOT

from gegede.util import wash_units
import logging
log = logging.getLogger('gegede')

def Amass(obj):
    return obj.a.to('g/mole').magnitude

def Nnuc(obj):
    return int(round(obj.a.to('g/mole').magnitude))

def Symbol(obj):
    return obj.symbol.upper()

# Note, ROOT density is hard coded as g/cc
#  http://root.cern.ch/root/html534/guides/users-guide/Geometry.html#units
def Density(obj):
    return obj.density.to('g/cc').magnitude


def get_element(tgeo, name):
    et = tgeo.GetElementTable()
    ele = et.FindElement(name)

    if not ele:
        nele = et.GetNelements()
        for count in range(nele):
            known = et.GetElement(count)
        raise KeyError('No such element: "%s"' % name)
    return ele
    

# fixme, need to handle material properties with obj.params
def make_material(bucket, mat):
    '''
    Make and return a TGeo equivalent to the gegede obj.
    '''
    typename = type(mat).__name__
    new = None

    if typename == 'Element':
        new = bucket.make(ROOT.TGeoElement, mat.name, Symbol(mat), mat.z, Amass(mat))

    if typename == 'Isotope':
        new = bucket.make(ROOT.TGeoIsotope, mat.name, mat.z, Nnuc(mat), Amass(mat))

    if typename == 'Composition': # element mix of isotopes
        new = bucket.make(ROOT.TGeoElement, mat.name, Symbol(mat), len(mat.isotopes))
        for count, (isoname, isofrac) in enumerate(mat.isotopes):
            iso = bucket.get(ROOT.TGeoIsotope, isoname)
            assert iso, 'No isotope named "%s"' % isoname
            new.AddIsotope(iso, isofrac)

    if typename == 'Amalgam':
        new = bucket.make(ROOT.TGeoMaterial, mat.name, Amass(mat), float(mat.z), Density(mat))

    if typename == 'Molecule':  # mix of elements
        new = bucket.make(ROOT.TGeoMixture, mat.name, len(mat.elements), Density(mat))
        for elename, elenum in mat.elements:
            ele = bucket.get(ROOT.TGeoElement, elename)
            assert ele, 'No element named "%s"' % elename
            new.AddElement(ele, elenum)

    if typename == 'Mixture':
        new = bucket.make(ROOT.TGeoMixture, mat.name, len(mat.components), Density(mat))
        for compname, compfrac in mat.components:
            comp = bucket.get(ROOT.TGeoMaterial, compname) or bucket.get(ROOT.TGeoElement, compname)
            assert comp, 'No mat/ele named "%s"' % compname
            new.AddElement(comp, compfrac)

    if not new:
        raise ValueError('Unknown type: "%s"' % typename)

    bucket.add(new, 'MATERIAL')
    return new

def make_shape(bucket, shape):
    '''
    Make a TGeo shape out of the object
    '''
    typename = type(shape).__name__
    shape, _ = wash_units(shape)

    obj = None
    if typename == 'Box':
        obj = bucket.make(ROOT.TGeoBBox, shape.name, 
                          shape.dx, shape.dy, shape.dz)

    if typename == 'Tubs':
        obj = bucket.make(ROOT.TGeoTubeSeg, shape.name,
                          shape.rmin, shape.rmax, shape.dz,
                          shape.sphi, shape.sphi+shape.dphi)
    
    if typename == 'Sphere':
        obj = bucket.make(ROOT.TGeoSphere, shape.name,
                          shape.rmin, shape.rmax,
                          shape.stheta, shape.stheta+shape.dtheta,
                          shape.sphi, shape.sphi+shape.dphi)

    # etc....  Grow this as gegede.schema.Schema.shapes grows....

    if obj:                     # for generic look up later
        bucket.add(obj, 'SHAPE')

    return obj


def make_medium(bucket, matname):
    medname = matname+'_medium'
    med = bucket.get('MEDIUM', medname)
    if med: return med

    mat = bucket.get('MATERIAL', matname)
    if not mat: return None

    med = bucket.make(ROOT.TGeoMedium, medname, len(bucket.store('MEDIUM')), mat)
    bucket.add(med, 'MEDIUM')
    return med

def make_structure(bucket, obj):
    typename = type(obj).__name__

    if typename == 'Volume':
        shape = bucket.get('SHAPE', obj.shape)
        assert shape, 'No shape "%s"' % obj.shape
        med = make_medium(bucket, obj.material) 
        assert med, 'No medium for material "%s' % obj.material
        vol = bucket.make(ROOT.TGeoVolume, obj.name, shape, med)
    return


    

class Bucket(object):
    def __init__(self, world):
        if not isinstance(world, type("")):
            world = world.name
        from collections import defaultdict
        self._dat = defaultdict(dict)
        self.tgeo = ROOT.TGeoManager(world, 'GeGeDe %s' % world)

    def store(self, category):
        return self._dat[category]

    def get(self, category, name):
        'Get object named <name> from <category> (label or type)'
        if not isinstance(category, type("")):
            category = category.__name__
        return self._dat[category].get(name)

    def has(self, obj):
        return self.get(type(obj), obj.GetName())

    def add(self, obj, category=None):
        self._dat[category][obj.GetName()] = obj

    def make(self, TYPE, name, *args):
        obj = self.get(TYPE, name)
        if obj:
            log.warn('Object %s %s already made' % (TYPE, name))
            return obj
        obj = TYPE(name, *args)
        ROOT.SetOwnership(obj, 0)
        self.add(obj, TYPE.__name__)
        log.debug('Made: %s' % obj)
        return obj

    pass

def convert(geom):
    '''
    Return a ROOT.TGeoManager filled with the geometry.
    '''

    bucket = Bucket(geom.world)
    # Materials
    for obj in geom.store.matter.values():
        make_material(bucket, obj)

    # Shapes
    for obj in geom.store.shapes.values():
        make_shape(bucket, obj)

    # Structure
    for obj in geom.store.structure.values():
        make_structure(bucket, obj)

    return bucket

def validate(tgeo):
    return True

def dumps(tgeo):
    return None



    
