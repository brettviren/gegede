#!/usr/bin/env python
'''
Test quantity handling
'''

from gegede import Quantity as Q
from gegede.schema.tools import toquantity, isquantity
import pytest

def test_isquantity():
    assert isquantity(1)
    assert isquantity(1.0)
    assert isquantity("1")
    assert isquantity("1.0")
    assert isquantity("1cm")
    assert isquantity("1.0cm")
    assert isquantity(Q(0))
    assert not isquantity(test_isquantity)

def test_toquantity():
    toquantity("1")(1)
    toquantity("1cm")("0cm")
    with pytest.raises(ValueError):
        toquantity("1cm")(1)
    with pytest.raises(ValueError):
        toquantity(1)("1cm")

        
