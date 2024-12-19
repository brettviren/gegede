#!/usr/bin/env python
'''
Test full path from schema to construction
'''

import pytest
from collections import OrderedDict
from gegede.schema.tools import make_maker
from gegede.schema.types import Array
from gegede import Quantity as Q

def test_flat():
    schema = (("qwu","1cm"), ("num",0), ("flt",0.0))
    store = OrderedDict()
    Type = make_maker(store, "Type", *schema)
    obj = Type("obj")
    assert obj.qwu == Q("1cm")
    assert obj.num == Q(0)
    assert obj.flt == Q(0.0)
    
def test_array_int():
    schema = (("arr", Array(2, int)), )
    store = OrderedDict()
    Type = make_maker(store, "Type", *schema)
    obj = Type("obj")
    
    print(obj.arr)
