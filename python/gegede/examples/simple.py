from gegede import construct

def airwaterboxes():
    g = construct.Geometry()
    h = g.matter.Element("Hydrogen","H",1,"1.01g/mole")
    n = g.matter.Element("Nitrogen", "N", 7, "14.01*g/mole")
    o = g.matter.Element("Oxygen", "O", 8, "16.0g/mole")
    water = g.matter.Molecule("Water", density="1.0kg/l", elements=(("Oxygen",1),("Hydrogen",2)))
    air = g.matter.Mixture("Air", density = "1.290*mg/cc", 
                           components = (("Nitrogen", 0.7), ("Oxygen",0.3)))

    U235 = g.matter.Isotope("U235", z=92, ia=235, a="235.0439242 g/mole")
    U238 = g.matter.Isotope("U238", z=92, ia=238, a="238.0507847 g/mole")
    enriched_uranium = g.matter.Composition("enriched_U", symbol="U", 
                                            isotopes=(("U235",0.8), ("U238",0.2)))

    box1 = g.shapes.Box("box1",'1cm','2cm','3cm')    
    box2 = g.shapes.Box("box2",'1m','2m','3m')    
    pos = g.structure.Position(None, '1cm',z='2cm')
    rot = g.structure.Rotation('', x='90deg')
    lv1 = g.structure.Volume('a_box', material=water, shape=box1)
    lv1inlv2 = g.structure.Placement("lv1_in_lv2", volume=lv1, pos=pos, rot=rot)
    lv2 = g.structure.Volume('the_world', material = air, shape=box2,
                             placements = [lv1inlv2], params= (("foo",42), ("bar","baz")))
    g.set_world(lv2)
    return g

