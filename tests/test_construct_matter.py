#!/usr/bin/env python
'''
Test the gegede.construct module by making some matter
'''

import common
from gegede import construct

def test_elements():
    g = construct.Geometry()
    o = g.matter.Element("Oxygen", "O", 8, "16g/mole")
    

if '__main__' == __name__:
    test_elements()
