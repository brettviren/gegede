#!/usr/bin/env python
'''
The schema for the categories of geometry description.

Shapes ("solids") follow the conventions shows in Geant4 and ROOT:

http://geant4.web.cern.ch/geant4/G4UsersDocuments/UsersGuides/ForApplicationDeveloper/html/Detector/geomSolids.html
http://root.cern.ch/root/html534/guides/users-guide/Geometry.html#shapes

 - the naming conventions of Geant4 are taken for the shapes (although we call them "shapes" not solids")

 - where applicable, the dimensions of solids are expressed as "half lengths" an such values are indicated with a "d" in their name (eg, "dx", "dy", "dz", "dphi").

 - all dimensions must be expressed in a quantity with the appropriate unit

'''

from collections import namedtuple, OrderedDict
from . import units, Quantity

zerolength = Quantity('0cm')
unitlength = Quantity('0cm')
zeroangle = Quantity('0deg')
piangle = Quantity('180deg')
twopiangle = Quantity('360deg')

Schema = dict(
    Shapes = [
        ("Box", (("dx",unitlength), ("dy",unitlength), ("dz",unitlength))),
        ("Tubs", (("rmin", zerolength), ("rmax",unitlength), ("dz", unitlength),
                  ("sphi",zeroangle), ("dphi", twopiangle))),
        ("Sphere", (("rmin", zerolength), ("rmax",unitlength),
                    ("sphi",zeroangle), ("dphi", twopiangle),
                    ("stheta",zeroangle), ("dtheta", piangle))),
        # fixme: fill in the rest!
    ]
)



def make_converter(obj):
    '''Return a function that will convert its argument using obj as a
    prototype.  It will raise ValueError if conversion is not
    possible.
    '''
    obj = Quantity(obj)
    def converter(other):
        other = Quantity(other)
        if obj.dimensionality == other.dimensionality:
            return other
        raise ValueError, 'Unit mismatch: %s incompatible with prototype %s' % (other, obj)
    return converter

def validate_input(proto, *args, **kwargs):
    '''Validate the input <args> and <kwargs> against the prototypes in <proto>.

    <proto> is a list of ("name",object) tuples.

    <args> is a list of positional arguments assumed to follow the
    ordering of <proto> but may be of shorter length.

    <kwargs> is a dictionary of "name"/object pairs supplying any
    remaining arguments.

    Any unspecified arguments are given the default from <proto> and
    no keys in <kwargs> may be given in addition to what are specified
    in <args>.

    A an ordered list of values are returned.
    '''
    members = OrderedDict()
    converters = dict()
    for name,pval in proto:
        members[name] = pval
        converters[name] = make_converter(pval)

    already = list()
    for k,v in zip(members.keys(), args):
        members[k] = converters[k](v)
        already.append(k)
    for k,v in kwargs.items():
        if k not in converters.keys():
            raise ValueError, 'Object "%s" not in prototype' % (k,)
        if k in already:
            raise ValueError, 'Keyword argument already supplied as positional: %s' % k
        members[k] = converters[k](v)

    return members.values()
    

def make_ntt_typed(collector, ntname, *proto):

    '''
    Make a namedtuple class that does type-checking of its args against a prototype.

    The <proto> is a list of 2-tuples ("membername",<prototype object>)
    '''
    member_names = [p[0] for p in proto]
    def instantiator(objname, *args, **kwargs):
        if objname in collector:
            raise ValueError, 'Instance "%s" of type %s already in %s' % \
                (objname, ntname, collector)

        members = validate_input(proto, *args, **kwargs)

        NTT = namedtuple(ntname, ['name'] + member_names)
        obj = NTT(objname, *members)
        collector[objname] = obj
        return obj
    instantiator.__name__ = ntname
    instantiator.__doc__ = "%s: %s" % (ntname, ', '.join(member_names))
    return instantiator

shape_store = OrderedDict()

def make_shapes(shapes_schema):
    shape_classes = list()
    shape_names = [ss[0] for ss in shapes_schema]
    ShapeCollection = namedtuple("Shapes", shape_names)
    shapes = list()
    for ss in shapes_schema:
        shape = make_ntt_typed(shape_store, ss[0], *ss[1])
        shapes.append(shape)
    return ShapeCollection(*shapes)
shapes = make_shapes(Schema['Shapes'])


