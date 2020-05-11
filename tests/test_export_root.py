#!/usr/bin/env pytyhon
'''
Test the ROOT exporter
'''

import unittest
skipmsg=""
try:
    import ROOT
    from gegede.export.root import Bucket, make_material, convert
except ImportError:
    skipmsg="PyROOT not available, skipping test"

from gegede.examples.simple import airwaterboxes

@unittest.skipIf(skipmsg, skipmsg)
def test_bucket():
    '''
    Test the gegede.export.root.Bucket class
    '''
    bucket = Bucket("world")
    o = bucket.make(ROOT.TGeoElement, 'ele1', 'E1', 1, 2.0)
    u235 = bucket.make(ROOT.TGeoIsotope, 'U235', 92, 235, 235.0)
    u238 = bucket.make(ROOT.TGeoIsotope, 'U238', 92, 238, 238.0)



@unittest.skipIf(skipmsg, skipmsg)
def test_export_root():
    g = airwaterboxes()
    b = convert(g)
    print (b.tgeo.Print())
