#!/usr/bin/env python
'''
Test gegede.iter
'''

from gegede.iter import ascending, ascending_all
from gegede import construct

def test_ascending():
    'Test ascending iteration of volumes'

    g = construct.Geometry()
    box = g.shapes.Box("box",'1mm','2mm','3mm')    

    top = g.structure.Volume('top', material='air', shape=box)
    vol = top
    for dn in range(3):
        d = g.structure.Volume('daughter_%d' % dn, material='air', shape=box)
        top.placements.append(g.structure.Placement('place_%d'%dn, volume=d).name)
        top.placements.append(g.structure.Placement('again_%d'%dn, volume=d).name)
        for gdn in range(2):
            gd = g.structure.Volume('granddaughter_%d_%d' % (dn, gdn), material='air', shape=box)
            d.placements.append(g.structure.Placement('place_%d_%d' % (dn, gdn), volume=gd).name)


    seen = set()
    for vol in ascending(g.store.structure, top):
        print (vol)
        if vol.name in seen:
            raise (ValueError, "Seen again: %s" % vol.name)
            seen.add(vol.name)

    #print (g.store.structure)
    vols = list(ascending_all(g.store.structure, top))
    #print ('\n'.join([v.name for v in vols]))
    assert len(vols) == 19, len(vols)
    assert vols[-1].name == 'top'



    
