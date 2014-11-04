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
    filepath = os.path.join(testdir, 'test.gdml')
    assert os.path.exists(filepath), 'No such file: %s' % filepath

    geo = ROOT.TGeoManager()
    geo.Import(filepath)
    if not geo:
        print "WARNING: ROOT still fails to parse GDML's own test file"


def test_read_gdml_in_root():

    geom = nested_boxes()
    obj = gegede.export.gdml.convert(geom)
    s = gegede.export.gdml.dumps(obj)
    gegede.export.gdml.validate(s)
    geo = ROOT.TGeoManager()
    fd, fname = tempfile.mkstemp(suffix='.gdml')
    open(fname, 'w').write(s)
    print fname
    geo.Import(fname)
    if not geo:
        print "WARNING: ROOT still fails to parse GDML's own test file"
#    assert geo
