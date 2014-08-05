#!/usr/bin/env python
'''
Test that correct GDML is produced
'''

import os
from gegede.examples.builders import nested_boxes
import gegede.export.gdml
etree = gegede.export.gdml.etree

testdir = os.path.dirname(__file__)

def test_gdml():
    '''
    Test the test.gdml from GDML's own Python package
    '''
    xsd_doc = etree.parse(gegede.export.gdml.schema_file)
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.parse(os.path.join(testdir, 'test.gdml'))
    valid = xsd.validate(xml)
    if not valid:
        print xsd.error_log
    assert valid, "Failed to validate GDML's own test.gdml"

def _test_gegede_gdml():
    geom = nested_boxes()

    s = gegede.export.gdml.dumps(geom)
    open('test_gdml.gdml','w').write(s)
    xsd_doc = etree.parse(gegede.export.gdml.schema_file)
    xsd = etree.XMLSchema(xsd_doc)
    xml = etree.parse('test_gdml.gdml')
    xsd.validate(xml)
    print xsd.error_log

    
