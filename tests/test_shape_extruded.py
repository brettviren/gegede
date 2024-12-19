from gegede import construct, schema
from gegede.examples.simple import airwaterboxes
from gegede import Quantity as Q
from gegede.export import gdml

import pytest

def test_make_one():
    g = construct.Geometry()
    box1 = g.shapes.Box("box1",'1cm','2cm','3cm')    
    print(f'{box1=}')
    xtru = g.shapes.ExtrudedOne("trixtrumissing",
                                (("0m","0m"), ("1m","0m"), ("0m","1m")),
                                "2m")
    print(f'{xtru.polygon=}')
    assert len(xtru.polygon) == 3;
    print(f'{xtru.dz=}')
    assert xtru.dz == Q("2m")
    print(f'{xtru.offsetp=}')
    assert not xtru.offsetp     # ggd does not yet support the schema providing defaults
    # remake with full contents
    xtru = g.shapes.ExtrudedOne("trixtrufull",
                                (("0m","0m"), ("1m","0m"), ("0m","1m")),
                                "2m",
                                 ("0m","0m"),  ("0m","0m"),
                                "1", "1")
    assert xtru.offsetp



def test_make_many():
    g = construct.Geometry()
    triangle=(("0m","0m"), ("1m","0m"), ("0m","1m"))
    zsections = [
        dict(z="-1m", offset=("-1m","-1m"), scale='2.0'),
        dict(z="0m", offset=("0m","0m"), scale='1.0'),
        dict(z="1m", offset=("1m","1m"), scale='0.5'),
    ]
    xtru = g.shapes.ExtrudedMany("trix",
                                 polygon=triangle,
                                 zsections=zsections)
    print(f'{xtru=}')
    zbroken = zsections + [
        dict(z="2m", offset=("0m","0m")) # omit scale attribute
    ]
    with pytest.raises(KeyError):
        xtrubroken = g.shapes.ExtrudedMany("trixbroken",
                                           polygon=triangle,
                                           zsections=zbroken)


def test_place_many():
    g = airwaterboxes()
    world = g.store.structure[g.world]

    triangle=(("0m","0m"), ("1m","0m"), ("0m","1m"))
    zsections = [
        dict(z="-1m", offset=("-1m","-1m"), scale='2.0'),
        dict(z="0m", offset=("0m","0m"), scale='1.0'),
        dict(z="1m", offset=("1m","1m"), scale='0.5'),
    ]
    xtru = g.shapes.ExtrudedMany("trix",
                                 polygon=triangle,
                                 zsections=zsections)

    thing = g.structure.Volume('a_thing', material="Water", shape=xtru)
    p = g.structure.Placement("thing", volume=thing)

    # Note, builders should not call insert()
    g.insert(p)

    o = gdml.convert(g)
    s = gdml.dumps(o)
    gdml.validate(s)
    print(s.decode())



def test_place_one():
    g = airwaterboxes()
    world = g.store.structure[g.world]
    xtru = g.shapes.ExtrudedOne("trixtrufull",
                                (("0m","0m"), ("1m","0m"), ("0m","1m")),
                                "2m",
                                 ("0m","0m"),  ("0m","0m"),
                                "1", "1")

    thing = g.structure.Volume('a_thing', material="Water", shape=xtru)
    p = g.structure.Placement("thing", volume=thing)

    # Note, builders should not call insert()
    g.insert(p)

    o = gdml.convert(g)
    s = gdml.dumps(o)
    gdml.validate(s)
    print(s.decode())



