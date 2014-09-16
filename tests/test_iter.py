#!/usr/bin/env python
'''
Test gegede.iter
'''

from gegede.iter import ascending
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
        for gdn in range(2):
            gd = g.structure.Volume('granddaughter_%d_%d' % (dn, gdn), material='air', shape=box)
            d.placements.append(g.structure.Placement('place_%d_%d' % (dn, gdn), volume=gd).name)

    #print g.store.structure
    vols = list(ascending(g.store.structure, top))
    #print '\n'.join([v.name for v in vols])
    assert len(vols) == 10, len(vols)
    assert vols[-1].name == 'top'
