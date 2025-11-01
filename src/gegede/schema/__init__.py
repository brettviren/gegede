#!/usr/bin/env python
'''
# GeGeDe Schema.

This module holds the default schema definition for the geometry description elements.

The schema is a dictionary with an item for each major **category** in the
schema.  The item's value is in a form which is category dependent.

Leaf elements in the schema structure are in the form of a 2-tuple holding a
data member **name** and a **prototypical value** ("proto").  A proto must be a
string with units (if applicable), a Python type (*eg* `int` or `float`) or a
GeGeDe type object (eg `NamedTypedList`).

Shapes ("solids") follow the conventions of [Geant4](https://geant4-userdoc.web.cern.ch/UsersGuides/ForApplicationDeveloper/html/index.html).
Specifically:

- The naming conventions for attributes match Geant4 class constructor arguments.  Note, GeGeDe uses the term **shape** for Geant4's concept of "solid".

- A dimension that represents an **extent** of a shape is expressed as a "half length" following the Geant4 convention.  Likewise, they are named with a leading "d" (eg, `dx`, `dy`, `dz`, `dphi`).  Other dimensions (radial, angular) are "full length".

- All dimensions must be expressed in a quantity with the appropriate **units**, including angles.  Eg the string `"0m"` may provide a proto for a length and not a bare `0`.
'''

from .types import Named, NameList, NamedTypedList, Array, Struct

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

        # Deprecated.  The Boolean "type" must be spelled as "union", "subtraction" or
        # "intersection".
        Boolean = (("type",str), ("first", Named), ("second", Named), ("pos", Named), ("rot", Named)),
        # Instead of Boolean, it is recommended to use the explicit types Union,
        # Subtraction and Intersection.
        Union = (("first", Named), ("second", Named), ("pos", Named), ("rot", Named)),
        Subtraction = (("first", Named), ("second", Named), ("pos", Named), ("rot", Named)),
        Intersection = (("first", Named), ("second", Named), ("pos", Named), ("rot", Named)),

        Torus = (("rmin", "0m"), ("rmax", "0.5m"), ("rtor", "1m"), ("startphi", "0deg"), ("deltaphi", "360deg")),

        # Arbitrary trapezoid.
        Arb8 = (
            ("v1x","0m"),("v1y","0m"),
            ("v2x","0m"),("v2y","1m"),
            ("v3x","1m"),("v3y","1m"),
            ("v4x","1m"),("v4y","0m"),
            ("v5x","0m"),("v5y","0m"),
            ("v6x","0m"),("v6y","1m"),
            ("v7x","1m"),("v7y","1m"),
            ("v8x","1m"),("v8y","0m"),
            ("dz", "1m")),

        # Extruded polygon of many sections.
        ExtrudedMany = (("polygon", Array(Array("0m",2))), # list of 2D points around the polygon
                        ("zsections", Array(Struct(z="1m", offset=Array("0m",2), scale="1.0")))),
        ExtrudedOne = (("polygon", Array(Array("0m",2))), # list of 2D points around the polygon
                       # half-extent along local "z" dimension
                       ("dz","1m"),
                       # plus (above center) and minus (below center) transverse offsets
                       ("offsetp", Array("0m", 2)),
                       ("offsetm", Array("0m", 2)),
                       # plus (above center) and minus (below center) scales
                       ("scalep",float), ("scalem",float)),

        # Extent Tubs with two normal vectors defining planes that cut the tube ends.
        CutTubs = (("rmin", "0m"), ("rmax","1m"), ("dz", "1m"),
                   ("sphi","0deg"), ("dphi", "360deg"),
                   ("normalm", Array(float, 3)),  # the "minus" or lower plane vector
                   ("normalp", Array(float, 3))), # the "plus" or upper plane vector

        # fixme: fill in the rest!
        ),

    matter = dict(
        Element = (("symbol",str), ("z",int), ("a","0.0g/mole")),
        Isotope = (("z",int), ("ia",int), ("a","0.0g/mole")),

        # A number of isotopes composed
        Composition = (("symbol",str), ("isotopes", NamedTypedList(float))),

        # a material with no specific constituents
        Amalgam = (("z", float),
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
                  ("placements", NameList(0)),
                  ("params", NamedTypedList(str, 0))),
        Placement = (("volume", Named), ("pos", Named), ("rot", Named),("copynumber",int)),
    ),
)
