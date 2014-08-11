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
    return str(obj.density.to('g/cc').magnitude)


def make_object(type, *args):
    obj = type(*args)
    ROOT.SetOwnership(0)
    return obj

def make_material(obj):
    '''
    Make and return a TGeo equivalent to the gegede obj.
    '''

    typename = type(obj).__name__

    if typename == 'Element':
        return make_object(ROOT.TGeoElement, 
                           Symbol(obj), obj.name.upper(), obj.z, Nnuc(obj), Amass(obj))

    if typename == 'Isotope':
        return make_object(ROOT.TGeoIsotope, 
                           obj.name.upper(), obj.z, Nnuc(obj), Amass(obj))

    if typename == 'Composition': # element mix of isotopes
        new = make_object(ROOT.TGeoMixture, obj.name, len(obj.isotopes))
        for count, (isoname, isofrac) in enumerate(obj.isotopes):
            iso = get_element(isnoame)
            new.AddElement(iso, isofrac)
        return new

    if typename == 'Amalgam':
        return make_object(ROOT.TGeoMaterial, obj.name, Amass(obj), float(obj.z), Density(obj))

    if typename == 'Molecule':  # mix of elements
        new = make_object(ROOT.TGeoMixture, obj.name, len(obj.elements), Density(obj))
        for elename, elenum in obj.elements:
            ele = get_element(elename):
            new.AddElement(ele, elenum)
        return new

    if typename == 'Mixture':
        new = make_object(ROOT.TGeoMixture, obj.name, len(obj.components), Density(obj))
        for compname, compfrac in obj.components:
            comp = get_element(compname):
            new.AddElement(comp, compfrac)
        return obj
    return



def convert(geom):
    '''
    Return a ROOT.TGeoManager filled with the geometry.
    '''
    tgeo = ROOT.TGeoManager(geom.world, 'GeGeDe %s' % geom.world)


    # Materials
    for name, obj in geom.store.matter.items():
        make_material(obj)

def validate(tgeo):
    return True

def dumps(tgeo):
    return None



    
