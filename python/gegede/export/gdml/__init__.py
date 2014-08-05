#!/usr/bin/env python
'''
An export method producing for GDML.

http://lcgapp.cern.ch/project/simu/framework/GDML/doc/GDMLmanual.pdf
http://gdml1.web.cern.ch/gdml1/doc/g4gdml_howto.html
http://geant4.in2p3.fr/2007/prog/GiovanniSantin/GSantin_Geant4_Paris07_Materials_v08.pdf

http://lxml.de/tutorial.html
http://lxml.de/objectify.html
http://stackoverflow.com/questions/2850823/multiple-xml-namespaces-in-tag-with-lxml

'''

import os

schema_dir = os.path.join(os.path.dirname(__file__), 'schema')
schema_file = os.path.join(schema_dir, 'gdml.xsd')

from lxml import etree
from gegede import Quantity

from gegede.export import pod

def qtus(q,unit):
    'Quantity to unit string'
    return str(q.to(unit).magnitude)

def nt_qunit2xmldict(nt, unit):
    ret = dict(unit=unit)
    for k,v in zip(nt._fields,nt):
        if Quantity == type(v):
            v = str(v.to(unit).magnitude)
        else:
            v = str(v)
        ret[k] = v
    return ret

def D(obj):
    return str(obj.density.to('g/cc').magnitude)
def Atom(obj):
    return str(obj.a.to('g/mole').magnitude)
def Symbol(obj):
    return obj.symbol or ""

# def wash(geom):
#     '''Return a new geom object with its contents "washed" of any things
#     that will tickle GDML limitations.
#     '''
#     import gegede.construct
#     newg = gegede.construct.Geometry(geom.schema)
#     for store_name in geom.store._fields:
#         store = getattr(geom.store,store_name)
#         newstore = getattr(newg.store,store_name)
#         for name, obj in store.items():
#             newobj = type(obj)(obj.name.replace(' ','_'), *obj[1:])
#             newstore[name.replace(' ','_')] = newobj
#     return newg



def make_material_node(obj):
    '''
    Return an lxml.etree.Element made from the matter object.
    '''

    typename = type(obj).__name__
    node = None

    if typename == 'Element':
        node = etree.Element('element', name=obj.name, Z=str(obj.z), formula=Symbol(obj))
        node.append(etree.Element('atom', value=Atom(obj)))

    if typename == 'Isotope':
        node = etree.Element('isotope', name=obj.name, Z=str(obj.z), N=str(obj.ia))
        node.append(etree.Element('atom', type="A", value=Atom(obj)))

    if typename == 'Composition':
        node = etree.Element('element', name=obj.name)
        for isoname, isofrac in obj.isotopes:
            node.append(etree.Element('fraction', ref=isoname, n=str(isofrac)))

    if typename == 'Amalgam':
        node = etree.Element('material', name=obj.name, Z=float(obj.z))
        # fixme: units???
        node.append(etree.Element('D', value=D(obj)))
        node.append(etree.Element('atom', value=Atom(obj)))

    if typename == 'Molecule':
        node = etree.Element('material', name=obj.name, formula=Symbol(obj))
        node.append(etree.Element('D', value=D(obj)))

    if typename == 'Mixture':
        node = etree.Element('material', name=obj.name, formula=Symbol(obj))
        node.append(etree.Element('D', value=D(obj)))
        for compname, compfrac in obj.components:
            node.append(etree.Element('fraction', ref=compname, n=str(compfrac)))

    return node


def make_shape_node(shape):
    '''
    Return an lxml.etree.Element made from the <shape>
    '''
    lunit = 'cm'
    aunit = 'radian'
    typename = type(shape).__name__

    outdat = dict()
    udat = dict()
    for k,v in zip(shape._fields, shape): # universal defaults
        if k == 'name':
            outdat['name'] = v
            continue
        if type(v) == Quantity:
            if 'meter' in v.to_base_units().units:
                outdat.setdefault('lunit', lunit)
                udat[k] = str(v.to(lunit).magnitude)
                continue
            if 'radian' in v.to_base_units().units:
                outdat.setdefault('aunit', aunit)
                udat[k] = str(v.to(aunit).magnitude)
                continue
    
    if typename == 'Box':
        outdat.update(x=udat['dx'], y=udat['dy'], z=udat['dz'])
        return etree.Element('box', **outdat)
                             
    if typename == 'Tubs':
        outdat.update(rmin=udat['rmin'], rmax=udat['rmax'], z=udat['dz'], 
                      startphi=udat['sphi'], deltaphi=['dphi'])
        return etree.Element('tube', **outdat)

    if typename == 'Sphere':
        outdat.update(rmin=udat['rmin'], rmax=udat['rmax'],
                      startphi=udat['sphi'], deltaphi=['dphi'],
                      starttheta=udat['stheta'], deltatheta=['dtheta'])
        return etree.Element('sphere', **outdat)

    # etc....  Grow this as gegede.schema.Schema.shapes grows....

    return

def make_structure_node(obj, store):
    typename = type(obj).__name__

    if typename == 'Volume':
        node = etree.Element('volume', name=obj.name)
        node.append(etree.Element('materialref', ref=obj.material))
        node.append(etree.Element('solidref', ref=obj.shape))
        for placename in obj.placements or []:
            place = store[placename]
            pvol = etree.Element('physvol')
            node.append(pvol)
            pvol.append(etree.Element('volumeref', ref=place.volume))
            pvol.append(etree.Element('positionref', ref=place.pos))
            pvol.append(etree.Element('rotationref', ref=place.rot))
        for parname, parval in obj.params or []:
            pnode = etree.Element('auxiliary', auxtype=parname, auxvalue=parval)
            node.append(pnode)
        return node
    return

def convert(geom):
    '''
    Return an lxml.etree formed from the geometry
    '''
    # exhausting....
    gdml_node = etree.Element('gdml')

    xsi = "schema/gdml.xsd"
    # fixme: do I need this cruft: xsi:noNamespaceSchemaLocation="schema/gdml.xsd" ?

    # <define>
    define_node = etree.Element('define')
    gdml_node.append(define_node)
    for name, obj in geom.store.structure.items():
        typename = type(obj).__name__.lower()
        node = None
        if typename == 'position':
            node = etree.Element('position', **nt_qunit2xmldict(obj, 'cm'))
        if typename == 'rotation':
            node = etree.Element('rotation', **nt_qunit2xmldict(obj, 'deg'))
        if node is not None:
            define_node.append(node)
        continue

    # <materials>
    materials_node = etree.Element('materials')
    gdml_node.append(materials_node)
    for name, obj in geom.store.matter.items():
        node = make_material_node(obj)
        if node is not None:
            materials_node.append(node)

    # <solids>
    solids_node = etree.Element('solids')
    gdml_node.append(solids_node)
    for obj in geom.store.shapes.values():
        node = make_shape_node(obj)
        if node is not None:
            solids_node.append(node)        
    

    # <structure>
    structure_node = etree.Element('structure')
    gdml_node.append(structure_node)
    for obj in geom.store.structure.values():
        node = make_structure_node(obj, geom.store.structure)
        if node is not None:
            structure_node.append(node)        

    # <setup>
    setup_node = etree.Element('setup', name="Default", version="0")
    gdml_node.append(setup_node)

    world_node = etree.Element('world', ref=geom.world)
    setup_node.append(world_node)

    return gdml_node


def validate(text):
    from StringIO import StringIO
    xsd_doc = etree.parse(schema_file)
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.parse(StringIO(text))
    okay = xsd.validate(xml)
    if not okay:
        print xsd.error_log
        raise ValueError, 'Invalid GDML'
    return True

def dumps(geom):
    xml = etree.tostring(convert(geom), pretty_print = True, xml_declaration = True)
    validate(xml)
    return xml
