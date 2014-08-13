#!/usr/bin/env python
'''
Export to ROOT TGeo
'''

import ROOT



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
    print et
    ele = et.FindElement(name)

    if not ele:
        nele = et.GetNelements()
        print 'I know about %d elements:' % nele
        for count in range(nele):
            known = et.GetElement(count)
            print '\t%4d: "%s" "%s"' % (count, known.GetName(), known.GetTitle())
        raise KeyError, 'No such element: "%s"' % name
    return ele
    

def make_material(bucket, obj):
    '''
    Make and return a TGeo equivalent to the gegede obj.
    '''
    typename = type(obj).__name__

    if typename == 'Element':
        return bucket.make(ROOT.TGeoElement, obj.name, Symbol(obj), obj.z, Amass(obj))

    if typename == 'Isotope':
        return bucket.make(ROOT.TGeoIsotope, obj.name, obj.z, Nnuc(obj), Amass(obj))

    if typename == 'Composition': # element mix of isotopes
        new = bucket.make(ROOT.TGeoElement, obj.name, Symbol(obj), len(obj.isotopes))
        for count, (isoname, isofrac) in enumerate(obj.isotopes):
            iso = bucket.get(ROOT.TGeoIsotope, isoname)
            assert iso, 'No isotope named "%s"' % isoname
            new.AddIsotope(iso, isofrac)
        return new

    if typename == 'Amalgam':
        return bucket.make(ROOT.TGeoMaterial, obj.name, Amass(obj), float(obj.z), Density(obj))

    if typename == 'Molecule':  # mix of elements
        new = bucket.make(ROOT.TGeoMixture, obj.name, len(obj.elements), Density(obj))
        for elename, elenum in obj.elements:
            ele = bucket.get(ROOT.TGeoElement, elename)
            assert ele, 'No element named "%s"' % elename
            new.AddElement(ele, elenum)
        return new

    if typename == 'Mixture':
        new = bucket.make(ROOT.TGeoMixture, obj.name, len(obj.components), Density(obj))
        for compname, compfrac in obj.components:
            comp = bucket.get(ROOT.TGeoMaterial, compname) or bucket.get(ROOT.TGeoElement, compname)
            assert comp, 'No mat/ele named "%s"' % compname
            new.AddElement(comp, compfrac)
        return new

    raise ValueError, 'Unknown type: "%s"' % typename



class Bucket(object):
    def __init__(self):
        from collections import defaultdict
        self._dat = defaultdict(dict)
    def get(self, TYPE, name):
        tname = TYPE.__name__
        return self._dat[tname].get(name)
    def has(self, obj):
        return self.get(type(obj), obj.GetName())
    def add(self, obj):
        self._dat[type(obj).__name__][obj.GetName()] = obj
    def make(self, TYPE, name, *args):
        obj = self.get(TYPE, name)
        if obj:
            print 'Object %s %s already made' % (TYPE, name)
            return obj
        obj = TYPE(name, *args)
        ROOT.SetOwnership(obj, 0)
        self.add(obj)
        print 'Made: %s' % obj
        return obj

    pass


def convert(geom):
    '''
    Return a ROOT.TGeoManager filled with the geometry.
    '''
    tgeo = ROOT.TGeoManager(geom.world, 'GeGeDe %s' % geom.world)
    ROOT.SetOwnership(tgeo, 0)



    bucket = Bucket()
    # Materials
    for name, obj in geom.store.matter.items():
        make_material(bucket, obj)

    return tgeo
def validate(tgeo):
    return True

def dumps(tgeo):
    return None



    
