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


def make_object(type, *args):
    obj = type(*args)
    ROOT.SetOwnership(obj, 0)
    return obj

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
    
def make_material(tgeo, obj):
    '''
    Make and return a TGeo equivalent to the gegede obj.
    '''
    et = tgeo.GetElementTable()

    typename = type(obj).__name__

    print 'Making: <%s> "%s"' % (typename, obj.name)

    if typename == 'Element':
        # brain dead interface
        last = et.GetNelements() 
        et.AddElement(obj.name, Symbol(obj), obj.z, Amass(obj))
        ele = et.GetElement(last)
        return ele

    if typename == 'Isotope':
        # brain dead, inconsistent interface
        iso = make_object(ROOT.TGeoIsotope, 
                          obj.name, obj.z, Nnuc(obj), Amass(obj))
        et.AddIsotope(iso)
        return iso

    if typename == 'Composition': # element mix of isotopes
        new = make_object(ROOT.TGeoElement , obj.name, Symbol(obj), len(obj.isotopes))
        for count, (isoname, isofrac) in enumerate(obj.isotopes):
            iso = et.FindIsotope(isoname)
            assert iso, 'No isotope: %s' % isoname
            new.AddElement(iso, isofrac)
        return new

    if typename == 'Amalgam':
        return make_object(ROOT.TGeoMaterial, obj.name, Amass(obj), float(obj.z), Density(obj))

    if typename == 'Molecule':  # mix of elements
        new = make_object(ROOT.TGeoMixture, obj.name, len(obj.elements), Density(obj))
        for elename, elenum in obj.elements:
            ele = get_element(tgeo, elename)
            new.AddElement(ele, elenum)
        return new

    if typename == 'Mixture':
        new = make_object(ROOT.TGeoMixture, obj.name, len(obj.components), Density(obj))
        for compname, compfrac in obj.components:
            comp = get_element(tgeo, compname)
            new.AddElement(comp, compfrac)
        return obj
    return



def convert(geom):
    '''
    Return a ROOT.TGeoManager filled with the geometry.
    '''
    tgeo = make_object(ROOT.TGeoManager, geom.world, 'GeGeDe %s' % geom.world)


    # Materials
    for name, obj in geom.store.matter.items():
        make_material(tgeo, obj)

    return tgeo
def validate(tgeo):
    return True

def dumps(tgeo):
    return None



    
