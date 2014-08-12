#!/usr/bin/env pytyhon
'''
Test the ROOT exporter
'''

import gegede.export.root
from gegede.examples.simple import airwaterboxes

def test_export_root():
    g = airwaterboxes()
    tg = gegede.export.root.convert(g)
