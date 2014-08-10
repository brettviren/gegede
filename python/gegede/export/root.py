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

def make_object(type, *args):
    obj = type(*args)
    ROOT.SetOwnership(0)
    return obj

def make_material(obj):
    '''
    Make and return a TGeo equivalent to the gegede obj.
    '''

    typename = type(obj).__name__
    node = None

    if typename == 'Element':
        return make_object(ROOT.TGeoElement, 
                           Symbol(obj), obj.name.upper(), obj.z, Nnuc(obj), Amass(obj))

    if typename == 'Isotope':
        return make_object(ROOT.TGeoIsotope, 
                           obj.name.upper(), obj.z, Nnuc(obj), Amass(obj))

    if typename == 'Composition': # element mix of isotopes
        obj = make_object(ROOT.TGeoMixture, obj.name, len(obj.isotopes))
        for count, (isoname, isofrac) in enumerate(obj.isotopes):
            iso = get_element(isnoame)
            obj.AddElement(iso, isofrac)
        return obj

    if typename == 'Amalgam':
        node = etree.Element('material', name=obj.name, Z=float(obj.z))
        # fixme: units???
        node.append(etree.Element('D', value=D(obj)))
        node.append(etree.Element('atom', value=Atom(obj)))

    if typename == 'Molecule':
        node = etree.Element('material', name=obj.name, formula=Symbol(obj))
        node.append(etree.Element('D', value=D(obj)))
        for elename, elenum in obj.elements:
            node.append(etree.Element('composite', ref=elename, n=str(elenum)))


    if typename == 'Mixture':
        node = etree.Element('material', name=obj.name, formula=Symbol(obj))
        node.append(etree.Element('D', value=D(obj)))
        for compname, compfrac in obj.components:
            node.append(etree.Element('fraction', ref=compname, n=str(compfrac)))

    return node


def convert(geom):
    '''
    Return a ROOT.TGeoManager filled with the geometry.
    '''
    tgeo = ROOT.TGeoManager(geom.world, 'GeGeDe %s' % geom.world)


    # Materials
    for name, obj in geom.store.matter.items():
    
    
