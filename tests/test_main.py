#!/usr/bin/env python

import os
import gegede.main

def test_main():
    fname = os.path.dirname(os.path.realpath(__file__))+'/test_configuration.cfg'
    g = gegede.main.generate(fname)

    assert g
    assert g.store.shapes
    if not g.store.matter:
        print ("You still haven't implemented this, huh?")
    assert g.store.structure
