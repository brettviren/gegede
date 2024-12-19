from gegede import construct, schema
from gegede.examples.simple import airwaterboxes
from gegede import Quantity as Q
from gegede.export import gdml

import pytest

def test_cuttub_make():
    g = construct.Geometry()
    tub = g.shapes.CutTubs("tub",
                           rmin="0m", rmax="1m", dz="1m",
                           sphi="0deg", dphi="360deg",
                           normalm = (0,0,1), normalp = (0,0,1))
    print(f'{tub=}')


def test_cuttub_place():
    g = airwaterboxes()
    world = g.store.structure[g.world]

    tub = g.shapes.CutTubs("tub",
                           rmin="0m", rmax="1m", dz="1m",
                           sphi="0deg", dphi="360deg",
                           normalm = (0,0,1), normalp = (0,0,1))

    thing = g.structure.Volume('a_thing', material="Water", shape=tub)
    p = g.structure.Placement("thing", volume=thing)

    # Note, builders should not call insert()
    g.insert(p)

    o = gdml.convert(g)
    s = gdml.dumps(o)
    gdml.validate(s)
    print(s.decode())


