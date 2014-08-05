#!/usr/bin/env python

import os

import tempfile
from gegede.examples.builders import nested_boxes
import gegede.export.gdml

import ROOT
testdir = os.path.dirname(__file__)

def test_gdml():
    '''
    Test the test.gdml from GDML's own Python package 
    '''
    file = os.path.join(testdir, 'test.gdml')
    geo = ROOT.TGeoManager()
    geo.Import(file)
    assert geo

def test_read_gdml_in_root():

    geom = nested_boxes()
    s = gegede.export.gdml.dumps(geom)
    gegede.export.gdml.validate(s)
    geo = ROOT.TGeoManager()
    fd, fname = tempfile.mkstemp(suffix='.gdml')
    open(fname, 'w').write(s)
    print fname
    geo.Import(fname)
    assert geo
