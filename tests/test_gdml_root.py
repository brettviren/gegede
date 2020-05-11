#!/usr/bin/env python

import os

import tempfile
from gegede.examples.builders import nested_boxes
import gegede.export.gdml

import unittest
skipmsg=""
try:
    import ROOT
except ImportError:
    skipmsg="PyROOT not available, skipping test"

testdir = os.path.dirname(__file__)

@unittest.skip("As for ROOT 6.20, ROOT fails to handle GDML's own test.gdml")
def test_gdml():
    '''
    Test the test.gdml from GDML's own Python package
    '''
    filepath = os.path.join(testdir, 'test.gdml')
    assert os.path.exists(filepath), 'No such file: %s' % filepath

    geo = ROOT.TGeoManager()
    geo.Import(filepath)
    if not geo:
        print ("WARNING: ROOT still fails to parse GDML's own test file")


@unittest.skipIf(skipmsg, skipmsg)
def test_read_gdml_in_root():

    geom = nested_boxes()
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    gegede.export.gdml.validate(s)
    geo = ROOT.TGeoManager()
    fd, fname = tempfile.mkstemp(suffix='.gdml')
    open(fname, 'wb').write(s)
    print (fname)
    geo.Import(fname)
    if not geo:
        print ("WARNING: ROOT still fails to parse GDML's own test file")
    #assert geo
