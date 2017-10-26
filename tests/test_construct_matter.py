#!/usr/bin/env python
'''
Test the gegede.construct module by making some matter
'''

from gegede import construct
from gegede import Quantity

# taken from examples in this presentation:
# http://geant4.in2p3.fr/2007/prog/GiovanniSantin/GSantin_Geant4_Paris07_Materials_v08.pdf
def test_elements():
    g = construct.Geometry()

    # Elements

    o = g.matter.Element("Oxygen", "O", 8, "16.0g/mole")
    assert o.name == 'Oxygen'
    assert o.symbol == 'O'
    assert o.z == 8
    assert o.a == Quantity(16.0, 'gram / mole')
    assert len(g.store.matter) == 1
    assert len(g.store.shapes) == 0
    print (o)

    n = g.matter.Element("Nitrogen", "N", 7, "14.01*g/mole")
    assert n.a == Quantity(14.01, 'gram/mole')
    print (n)

    h = g.matter.Element("Hydrogen","H",1,"1.01g/mole")
    print (h)

    # Isotopes and Compositions

    U235 = g.matter.Isotope("U235", z=92, ia=235, a="235.0439242 g/mole")
    assert U235.z == 92
    print (U235)
    U238 = g.matter.Isotope("U238", z=92, ia=238, a="238.0507847 g/mole")
    assert U238.ia == 238
    print (U238)
    enriched_uranium = g.matter.Composition("enriched U", symbol="U", 
                                            isotopes=(("U235",0.8), ("U238",0.2)))
    assert len(enriched_uranium.isotopes) == 2
    print (enriched_uranium)

    # Materials

    lar = g.matter.Amalgam("liquidArgon", z=18, a="39.95*g/mole", density="1.390*g/cc")
    print (lar)
    assert lar.density.compare(Quantity(1.39, 'kilogram / liter'), lambda x,y: abs(x-y)<0.0001)

    water = g.matter.Molecule("Water", density="1.0kg/l", elements=(("Oxygen",1),("Hydrogen",2)))
    print (water)
    assert hasattr(water,'symbol')
    assert 2 == len(water.elements)

    air = g.matter.Mixture("Air", density = "1.290*mg/cc", 
                           components = (("Nitrogen", 0.7), ("Oxygen",0.3)))
    print (air)
    assert 2 == len(air.components)

    nuc_rod_mat = g.matter.Mixture("U for nuclear power generation", density = "19.050g/cc",
                                   # need explicit comma to tuple'ize here
                                   components = (("enriched U", 1.0),)) 
    print (nuc_rod_mat)
    assert 1 == len(nuc_rod_mat.components)


def test_pass_objects():
    g = construct.Geometry()
    
    n = g.matter.Element("Nitrogen", "N", 7, "14.01*g/mole")
    h = g.matter.Element("Hydrogen","H",1,"1.01g/mole")
    water = g.matter.Molecule("Water", density="1.0kg/l", elements=((n,1),(h,2)))
    print (water)

    assert 3 == len(g.store.matter)

if '__main__' == __name__:
    test_elements()
    test_pass_objects()

    
