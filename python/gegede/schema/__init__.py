#!/usr/bin/env python
'''The module holds the default schema definition for the geometry description elements.

The schema is a dictionary with an item for each major category in the
schema.  The item's value is in a form which is category dependent.

In general, leaf elements are described by a 2-tuple holding a data
member name and a prototypical value.  This value must be either an
object or a string that can be interpreted into an object in a
category-dependent manner.

Shapes ("solids") follow the conventions shows in Geant4 and ROOT:

http://geant4.web.cern.ch/geant4/G4UsersDocuments/UsersGuides/ForApplicationDeveloper/html/Detector/geomSolids.html
http://root.cern.ch/root/html534/guides/users-guide/Geometry.html#shapes

 - the naming conventions of Geant4 are taken for the shapes (although we call them "shapes" not solids")

 - where applicable, the dimensions of solids are expressed as "half lengths" an such values are indicated with a "d" in their name (eg, "dx", "dy", "dz", "dphi").

 - all dimensions must be expressed in a quantity with the appropriate unit

'''

from .types import Named, NameList, NamedTypedList

Schema = dict(

    shapes = dict(
        Box = (("dx","1m"), ("dy","1m"), ("dz","1m")),
        TwistedBox = (("dx","1m"), ("dy","1m"), ("dz","1m"), ("phitws", "0deg")),
        Tubs = (("rmin", "0m"), ("rmax","1m"), ("dz", "1m"),
               ("sphi","0deg"), ("dphi", "360deg")),
        Sphere = (("rmin", "0m"), ("rmax","1m"),
                    ("sphi","0deg"), ("dphi", "360deg"),
                    ("stheta","0deg"), ("dtheta", "180deg")),
        Cone = (("rmin1","0m"), ("rmax1","1m"),
                    ("rmin2","0m"), ("rmax2","2m"), ("dz","2m"),
                    ("sphi","0deg"), ("dphi","360deg")),
        Trapezoid = (("dx1","2m"),("dx2","1m"),
                        ("dy1","2.5m"),("dy2","1.5m"),("dz","3m")),
        TwistedTrap = (("dx1","2m"),("dx2","1m"),("dx3","1m"),("dx4","1m"),
                        ("dy1","2.5m"),("dy2","1.5m"),("dz","3m"),
                        ("dtheta","0deg"), ("dphi", "360deg"), ("dalpha", "0deg"), ("phitws", "0deg")),
        TwistedTrd = (("dx1","2m"),("dx2","1m"),
                        ("dy1","2.5m"),("dy2","1.5m"),("dz","3m"),
                        ("phitws", "0deg")),
        Paraboloid = (("drlo","1m"),("drhi","2m"),("ddz","2m")),
        Ellipsoid = (("dax","1m"),("dby","2m"),("dcz","2m"),
                     ("dzcut1","2m"),("dzcut2","2m")),
        PolyhedraRegular = (("numsides", "8"), ("sphi", "0deg"), ("dphi", "360deg"), ("rmin", "1m"), ("rmax", "2m"), ("dz", "1m")),
        EllipticalTube = (("dx","1m"),("dy","2m"),("dz","2m")),
        Boolean = (("type",str), ("first", Named), ("second", Named),
                   ("pos", Named), ("rot", Named))

        # fixme: fill in the rest!
        ),

    matter = dict(
        Element = (("symbol",str), ("z",int), ("a","0.0g/mole")),
        Isotope = (("z",int), ("ia",int), ("a","0.0g/mole")),

        # A number of isotopes composed
        Composition = (("symbol",str), ("isotopes", NamedTypedList(float))),

        # a material with no specific constituents
        Amalgam = (("z", int),
                   ("a","0.0g/mole"),
                   ("density", "0.0g/cc"), 
                   ("properties",NamedTypedList(list))),

        # A molecule is a Material with a number of elements
        Molecule = (("symbol",str),
                    ("density", "0.0g/cc"),
                    ("elements", NamedTypedList(int)),
                    ("properties",NamedTypedList(list))),

        # A mixture is a Material that has a number of elements or
        # other materials added by mass fraction.
        Mixture = (("symbol",str),
                   ("density", "0.0g/cc"),
                   ("components", NamedTypedList(float)),
                   ("properties", NamedTypedList(list))),

        # fixme, these need to also take state, temperature and pressure, radlen
        ),

    structure = dict(
        Position = (("x", "0m"), ("y","0m"), ("z","0m")),
        Rotation = (("x", "0deg"), ("y","0deg"), ("z","0deg")),
        Volume = (("material", Named), ("shape", Named),
                  ("placements", NameList(str,0)),
                  ("params", NamedTypedList(str, 0))),
        Placement = (("volume", Named), ("pos", Named), ("rot", Named),("copynumber",int)),
    ),
)
