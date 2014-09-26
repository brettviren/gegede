#!/usr/bin/env python
'''
test gegede.export.util
'''
from collections import namedtuple
from gegede.util import wash_units, list_match
from gegede import Quantity as Q


def test_wash_units():
    Thing = namedtuple("Thing", "name l a")
    t1 = Thing('t1', Q("1mm"), Q("1degree"))
    n1,u1 = wash_units(t1, lunit='meter', aunit='radian')
    assert n1.l == 0.001, n1
    assert abs(n1.a - 3.14159/180) < 0.01, n1
    assert 'meter' == u1['lunit'], u1
    assert 'radian' == u1['aunit'], u1


    OtherThing = namedtuple("OtherThing", "name l1 l2")
    ot2 = OtherThing('ot2', Q("1mm"), Q("2meter"))
    n2,u2 = wash_units(ot2, lunit='meter', aunit='radian')
    assert n2.l1 == 0.001, n2
    assert n2.l2 == 2.0, n2
    assert 'meter' == u2['lunit'], u2
    assert 'aunit' not in u2, u2





def test_matching():
    NO = namedtuple('NamedObj','name')
    values = [NO(o) for o in "the quick brown foxy fiend".split()]
    def deref(v): return v.name
    assert list_match(values, deref=deref) == values
    assert list_match(values,0, deref=deref) == map(NO, ['the'])
    assert list_match(values,1, deref=deref) == map(NO, ['quick'])
    assert list_match(values,"quick", deref=deref) == map(NO, ['quick'])
    assert list_match(values,'b.*', deref=deref) == map(NO, ['brown'])
    assert list_match(values,'f.*', deref=deref) == map(NO, ['foxy','fiend'])
    assert list_match(values, lambda x: 'o' in x, deref=deref) == map(NO,'brown foxy'.split())
