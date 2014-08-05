#!/usr/bin/env python

import gegede.construct

def test_air():
    g = gegede.construct.Geometry()
    n = g.matter.Element("Nitrogen", "N", 7, "14.01*g/mole")
    o = g.matter.Element("Oxygen", "O", 8, "16.0g/mole")
    air = g.matter.Mixture("Air", density = "1.290*mg/cc", 
                           components = (("Nitrogen", 0.7), ("Oxygen",0.3)))
    print air
    assert len(air.components) == 2
    assert type(air.components[0]) == tuple


def test_water():
    g = gegede.construct.Geometry()
    h = g.matter.Element("Hydrogen","H",1,"1.01g/mole")
    o = g.matter.Element("Oxygen", "O", 8, "16.0g/mole")
    water = g.matter.Molecule("Water", density="1.0kg/l", elements=(("Oxygen",1),("Hydrogen",2)))
    print water
    assert len(water.elements) == 2
    assert type(water.elements[0]) == tuple
    
