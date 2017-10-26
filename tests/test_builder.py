#!/usr/bin/env python

from gegede.examples.builders import nested_boxes

def test_nested_boxes():
    geom = nested_boxes()
    print (geom.store)

