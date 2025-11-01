#!/usr/bin/env pytyhon
'''
Test the ROOT exporter
'''

import pytest
skipmsg=""
noroot=False
try:
    from ROOT import TGeoManager
except ImportError:
    skipmsg="PyROOT not available, skipping test"
    noroot=True

from gegede.examples.simple import airwaterboxes

@pytest.mark.skipif(noroot, reason=skipmsg)
def test_bucket():
    '''
    Test the gegede.export.root.Bucket class
    '''
    bucket = Bucket("world")
    o = bucket.make(ROOT.TGeoElement, 'ele1', 'E1', 1, 2.0)
    u235 = bucket.make(ROOT.TGeoIsotope, 'U235', 92, 235, 235.0)
    u238 = bucket.make(ROOT.TGeoIsotope, 'U238', 92, 238, 238.0)



@pytest.mark.skipif(noroot, reason=skipmsg)
def test_export_root():
    g = airwaterboxes()
    b = convert(g)
    print (b.tgeo.Print())
