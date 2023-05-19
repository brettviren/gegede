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
from gegede.iter import ascending
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
        node = etree.Element('material', name=obj.name, Z=str(float(obj.z)))
        # fixme: units???
        node.append(etree.Element('D', value=D(obj)))
        node.append(etree.Element('atom', value=Atom(obj)))
        for propname, propvect in obj.properties:
            node.append(etree.Element('property',
                                      name=propname,
                                      ref=obj.name+'_'+propname+'_VALUE'))

    if typename == 'Molecule':
        node = etree.Element('material', name=obj.name, formula=Symbol(obj))
        node.append(etree.Element('D', value=D(obj)))
        for elename, elenum in obj.elements:
            node.append(etree.Element('composite', ref=elename, n=str(elenum)))
        for propname, propvect in obj.properties:
            node.append(etree.Element('property',
                                      name=propname,
                                      ref=obj.name+'_'+propname+'_VALUE'))


    if typename == 'Mixture':
        node = etree.Element('material', name=obj.name, formula=Symbol(obj))
        node.append(etree.Element('D', value=D(obj)))
        for compname, compfrac in obj.components:
            node.append(etree.Element('fraction', ref=compname, n=str(compfrac)))
        for propname, propvect in obj.properties:
            node.append(etree.Element('property',
                                      name=propname,
                                      ref=obj.name+'_'+propname+'_VALUE'))

    return node


def make_shape_node(shape):
    '''
    Return an lxml.etree.Element made from the <shape>
    '''
    lunit = 'cm'
    aunit = 'radian'
    typename = type(shape).__name__

    def unitify(unit, quant, scale=1.0):
        quant = quant * scale
        return str(quant.to(unit).magnitude)
    def dsize(quant):
        return unitify(lunit, quant, 2.0)
    def rsize(quant):
        return unitify(lunit, quant, 1.0)
    def ang(quant):
        return unitify(aunit, quant, 1.0)

    if typename == 'Box':
        dat = dict(name=shape.name, lunit=lunit,
                   x=dsize(shape.dx), y=dsize(shape.dy), z=dsize(shape.dz))
        return etree.Element('box', **dat)

    if typename == 'TwistedBox':
        dat = dict(name=shape.name, lunit=lunit,
                   x=dsize(shape.dx), y=dsize(shape.dy), z=dsize(shape.dz), PhiTwist=ang(shape.phitws))
        return etree.Element('twistedbox', **dat)

    if typename == 'Tubs':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                   rmin=rsize(shape.rmin), rmax=rsize(shape.rmax), z=dsize(shape.dz),
                   startphi=ang(shape.sphi), deltaphi=ang(shape.dphi))
        return etree.Element('tube', **dat)

    if typename == 'Sphere':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                   rmin=rsize(shape.rmin), rmax=rsize(shape.rmax),
                   startphi=ang(shape.sphi), deltaphi=ang(shape.dphi),
                   starttheta=ang(shape.stheta), deltatheta=ang(shape.dtheta))
        return etree.Element('sphere', **dat)

    if typename == 'Cone':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    rmin1=rsize(shape.rmin1), rmax1=rsize(shape.rmax1),
                    rmin2=rsize(shape.rmin2), rmax2=rsize(shape.rmax2), z=dsize(shape.dz),
                    startphi=ang(shape.sphi), deltaphi=ang(shape.dphi))
        return etree.Element('cone', **dat)

    if typename == 'Trapezoid':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    x1=dsize(shape.dx1), x2=dsize(shape.dx2),
                    y1=dsize(shape.dy1), y2=dsize(shape.dy2), z=dsize(shape.dz))
        return etree.Element('trd', **dat)

    if typename == 'TwistedTrap':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    x1=dsize(shape.dx1), x2=dsize(shape.dx2), x3=dsize(shape.dx3), x4=dsize(shape.dx4),
                    y1=dsize(shape.dy1), y2=dsize(shape.dy2), z=dsize(shape.dz),
                    Theta=ang(shape.dtheta), Phi=ang(shape.dphi), Alph=ang(shape.dalpha), PhiTwist=ang(shape.phitws))
        return etree.Element('twistedtrap', **dat)

    if typename == 'TwistedTrd':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    x1=dsize(shape.dx1), x2=dsize(shape.dx2),
                    y1=dsize(shape.dy1), y2=dsize(shape.dy2), z=dsize(shape.dz),
                    PhiTwist=ang(shape.phitws))
        return etree.Element('twistedtrd', **dat)
    
    if typename == 'Arb8':
        # print("arb8ivert",shape.ivert[0][0])
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                   v1x=dsize(shape.v1x),v1y=dsize(shape.v1y),
                   v2x=dsize(shape.v2x),v2y=dsize(shape.v2y),
                   v3x=dsize(shape.v3x),v3y=dsize(shape.v3y),
                   v4x=dsize(shape.v4x),v4y=dsize(shape.v4y),
                   v5x=dsize(shape.v5x),v5y=dsize(shape.v5y),
                   v6x=dsize(shape.v6x),v6y=dsize(shape.v6y),
                   v7x=dsize(shape.v7x),v7y=dsize(shape.v7y),
                   v8x=dsize(shape.v8x),v8y=dsize(shape.v8y),
                    dz=dsize(shape.dz))
        return etree.Element('arb8', **dat)

    if typename == 'Paraboloid':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    rlo=dsize(shape.drlo), rhi=dsize(shape.drhi),
                    dz=dsize(shape.ddz))
        return etree.Element('paraboloid', **dat)

    if typename == 'Ellipsoid':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    ax=dsize(shape.dax), by=dsize(shape.dby), cz=dsize(shape.dcz),
                    zcut1=dsize(shape.dzcut1), zcut2=dsize(shape.dzcut2))
        return etree.Element('ellipsoid', **dat)

    if typename == 'PolyhedraRegular':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    startphi=ang(shape.sphi), deltaphi=ang(shape.dphi), numsides=str(int(shape.numsides)))
        ele = etree.Element('polyhedra', **dat)
        zpos = shape.dz / 2
        zneg = - shape.dz / 2
        ele.append(etree.Element('zplane', rmin=rsize(shape.rmin), rmax=rsize(shape.rmax), z=dsize(zpos)))
        ele.append(etree.Element('zplane', rmin=rsize(shape.rmin), rmax=rsize(shape.rmax), z=dsize(zneg)))
        return ele

    if typename == 'Boolean':
        ele = etree.Element(shape.type, name=shape.name)
        # the rest are sub nodes.  why?  because, don't ask questions!
        ele.append(etree.Element('first', ref=shape.first))
        ele.append(etree.Element('second', ref=shape.second))
        ele.append(etree.Element('positionref', ref = shape.pos or 'center'))
        ele.append(etree.Element('rotationref', ref = shape.rot or 'identity'))
        return ele
    
    if typename == 'EllipticalTube':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    dx=dsize(0.5*shape.dx), dy=dsize(0.5*shape.dy), dz=dsize(0.5*shape.dz))
        return etree.Element('eltube', **dat)    

    if typename == 'Torus':
        dat = dict(name=shape.name, lunit=lunit, aunit=aunit,
                    rmin=rsize(shape.rmin), rmax=rsize(shape.rmax), rtor=rsize(shape.rtor),
                    startphi=ang(shape.startphi), deltaphi=ang(shape.deltaphi))
        return etree.Element('torus', **dat)

    # etc....  Grow this as gegede.schema.Schema.shapes grows....

    return

def make_volume_node(vol, store):
    #print ('VOL',vol)
    node_type = 'volume'
    if vol.material is None and vol.shape is None:
        node = etree.Element('assembly', name=vol.name)
    else:
        assert vol.material and vol.shape
        node = etree.Element('volume', name=vol.name)
        node.append(etree.Element('materialref', ref=vol.material))
        node.append(etree.Element('solidref', ref=vol.shape))
    for placename in vol.placements or []:
        place = store[placename]
        if place.copynumber:
            pvol = etree.Element('physvol', copynumber=str(place.copynumber))
        else:
            pvol = etree.Element('physvol')
        node.append(pvol)
        pvol.append(etree.Element('volumeref', ref=place.volume))
        if place.pos:
            pvol.append(etree.Element('positionref', ref=place.pos))
        else:
            pvol.append(etree.Element('positionref', ref='center'))
        if place.rot:
            pvol.append(etree.Element('rotationref', ref=place.rot))
        else:
            pvol.append(etree.Element('rotationref', ref='identity'))
    for parname, parval in vol.params or []:
        pnode = etree.Element('auxiliary', auxtype=parname, auxvalue=parval)
        node.append(pnode)
    return node


def convert(geom):
    '''
    Return an lxml.etree formed from the geometry
    '''

    gdml_node = etree.Element("gdml")

    # I have no idea what this means but it reproduces what other GDML
    # files have and w/out it Geant4 complains.
    gdml_node.set('{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation',
                  'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd')

    # <define>
    define_node = etree.Element('define')
    gdml_node.append(define_node)
    center = identity = None
    for name, obj in geom.store.structure.items():
        typename = type(obj).__name__.lower()
        node = None
        if typename == 'position':
            node = etree.Element('position', **nt_qunit2xmldict(obj, 'cm'))
            if obj.name == 'center':
                center = obj
        if typename == 'rotation':
            node = etree.Element('rotation', **nt_qunit2xmldict(obj, 'degree'))
            if obj.name == 'identity':
                identity = obj
        if node is not None:
            define_node.append(node)
        continue
    for name, obj in geom.store.matter.items():
        typename = type(obj).__name__.lower()
        if typename=='mixture' or typename=='molecule' or typename=='amalgam':
            for prop, val in obj.properties:
                vals = str(val[0])
                for v in val[1:]: vals += ' ' + str(v)
                define_node.append(etree.Element('matrix',
                                                 name=name+'_'+prop+'_VALUE',
                                                 coldim=str(len(val)),
                                                 values=vals))
                continue
            continue
        continue
    if center is None:
        define_node.append(etree.Element('position', name='center'))
    if identity is None:
        define_node.append(etree.Element('rotation', name='identity'))

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
    for vol in ascending(geom.store.structure, geom.world):
        assert vol
        node = make_volume_node(vol, geom.store.structure)
        if node is not None:
            structure_node.append(node)

    # <setup>
    setup_node = etree.Element('setup', name="Default", version="0")
    gdml_node.append(setup_node)

    world_node = etree.Element('world', ref=geom.world)
    setup_node.append(world_node)

    return gdml_node


def validate(text):
    try:
        from StringIO import StringIO
        sio = StringIO(text)
    except ImportError:         # python3
        from io import BytesIO
        sio = BytesIO(text)

    xsd_doc = etree.parse(schema_file)
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.parse(sio)
    okay = xsd.validate(xml)
    if not okay:
        print (xsd.error_log)
        raise ValueError('Invalid GDML')
    return True

def validate_object(obj):
    return validate(dumps(obj))

#def validate_output(obj, filename):
#    return False

def dumps(obj):
    '''
    Return a string representation of the object returned by convert.
    '''
    xml = etree.tostring(obj, pretty_print = True, xml_declaration = True)
    xml = xml.replace(b"'",b'"')  # work around ROOT GDML import bug....
    # don't validate here
    return xml

def output(obj, filename):
    '''
    Save to file
    '''
    open(filename,'wb').write(dumps(obj))
