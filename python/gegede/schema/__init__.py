#!/usr/bin/env python
'''The module holds the default schema definition for the geometry description elements.

The schema is a dictionary with an item for each major category in the
schema.  The item's value is in a form which is category dependent.  

In general, leaf elements are described by a 2-tuple holding a data
member name and a pro typical value.  This value must be either an
object or a string that can be interpreted into an object in a
category-dependent manner.  

Shapes ("solids") follow the conventions shows in Geant4 and ROOT:

http://geant4.web.cern.ch/geant4/G4UsersDocuments/UsersGuides/ForApplicationDeveloper/html/Detector/geomSolids.html
http://root.cern.ch/root/html534/guides/users-guide/Geometry.html#shapes

 - the naming conventions of Geant4 are taken for the shapes (although we call them "shapes" not solids")

 - where applicable, the dimensions of solids are expressed as "half lengths" an such values are indicated with a "d" in their name (eg, "dx", "dy", "dz", "dphi").

 - all dimensions must be expressed in a quantity with the appropriate unit

'''

Schema = dict(

    shapes = dict(
        Box = (("dx","1m"), ("dy","1m"), ("dz","1m")),
        Tubs = (("rmin", "0m"), ("rmax","1m"), ("dz", "1m"),
               ("sphi","0deg"), ("dphi", "360deg")),
        Sphere = (("rmin", "0m"), ("rmax","1m"),
                    ("sphi","0deg"), ("dphi", "360deg"),
                    ("stheta","0deg"), ("dtheta", "180deg")),
        # fixme: fill in the rest!
        ),

    matter = dict(
        Element = (("symbol",""), ("z",0), ("a","0.0g/mole")),
        Isotope = (("z",0), ("ia",0), ("a","0.0g/mole")),
        Composition = (("symbol",""), ("isotopes", list)),

        # a material with no specific components
        Amalgam = (("z", 0), ("a","0.0g/mole"), ("density", 0.0)),

        # three ways to mix up Elements, list of 2-tuple ("name",portion)
        Molecule = (("density", "0.0g/cc"), ("elements", list)),
        Compound = (("density", "0.0g/cc"), ("elements", list)),
        Mixture = (("density", "0.0g/cc"), ("elements", list)),
        # fixme, these need to also take state, temperature and pressure
        ),

)

