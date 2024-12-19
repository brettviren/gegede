
from gegede import construct, schema
from gegede.examples.simple import airwaterboxes
from gegede import Quantity as Q
from gegede.export import gdml


import pytest

@pytest.mark.parametrize("bshape", ["Subtraction", "Intersection", "Union"])
@pytest.mark.parametrize("lower", [True, False])
def test_shape_subtraction(bshape, lower):

    # Note, this defines a "world" and we will sneak in some extra
    g = airwaterboxes()
    world = g.store.structure[g.world]

    shell = g.shapes.Box('shell')
    hole = g.shapes.Sphere('hole', rmax=Q("1.1m"))

    if lower:
        insphere = g.shapes.Boolean("insphere", bshape.lower(), "shell", "hole")
    else:
        B = getattr(g.shapes, bshape)
        insphere = B("insphere", "shell", "hole")

    thing = g.structure.Volume('a_thing', material="Water", shape=insphere)
    p = g.structure.Placement("thing", volume=thing)

    # Note, builders should not call insert()
    g.insert(p)

    o = gdml.convert(g)
    s = gdml.dumps(o)
    gdml.validate(s)

