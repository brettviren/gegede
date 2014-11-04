#!/usr/bin/env python
'''
Test gegede.construct module by making some structure
'''

from gegede import construct

def test_make_some_stuff():
    g = construct.Geometry()

    h = g.matter.Element("Hydrogen","H",1,"1.01g/mole")
    n = g.matter.Element("Nitrogen", "N", 7, "14.01*g/mole")
    o = g.matter.Element("Oxygen", "O", 8, "16.0g/mole")
    water = g.matter.Molecule("Water", density="1.0kg/l", elements=(("Oxygen",1),("Hydrogen",2)))
    air = g.matter.Mixture("Air", density = "1.290*mg/cc", 
                           components = (("Nitrogen", 0.7), ("Oxygen",0.3)))

    box1 = g.shapes.Box("box1",'1cm','2cm','3cm')    
    box2 = g.shapes.Box("box2",'1m','2m','3m')    

    pos = g.structure.Position(None, '1cm',z='2cm')
    assert pos.name == 'Position000000',pos.name
    print pos
    rot = g.structure.Rotation('', x='90deg')
    assert rot.name == 'Rotation000001', rot.name
    print rot

    lv1 = g.structure.Volume('a box', material=water, shape=box1)
    print lv1
    lv1inlv2 = g.structure.Placement("lv1_in_lv2", volume=lv1, pos=pos, rot=rot)
    print lv1inlv2
    lv2 = g.structure.Volume('lv2', material = air, shape=box2,
                             placements = [lv1inlv2])
    assert lv2.params is not None, 'got %s' % str(lv2.params) # want empty list
    assert not lv2.params, 'got %s' % str(lv2.params)
    lv2 = g.structure.Volume('the world', material = air, shape=box2,
                             placements = [lv1inlv2], params= (("foo",42), ("bar","baz")))
    assert lv2.params
    print lv2
    
def test_post_place():
    g = construct.Geometry()

    box0 = g.shapes.Box("box0",'1mm','2mm','3mm')    
    box1 = g.shapes.Box("box1",'1cm','2cm','3cm')    

    lv1 = g.structure.Volume('a box', material='water', shape=box1)
    lv0 = g.structure.Volume('daughter-box', material='air', shape=box0)

    lv0inlv1 = g.structure.Placement('lv0_in_lv1', volume=lv0)
    lv1.placements.append(lv0inlv1.name) # no boom!

    print 'DONE'
    print g.store.structure
    
    
