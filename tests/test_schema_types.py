#!/usr/bin/env python
'''
Test gegede.schema.types
'''

import gegede.schema.types as gst
from gegede.schema.tools import validate_input as validate
from gegede.examples.simple import airwaterboxes
from gegede.export import gdml

import pytest

def test_named_typed_list():
    '''
        Volume = (("material", Named), ("shape", Named), 
                  ("placements", NameList(str,0)),
                  ("params", NamedTypedList(str, 0))),
    '''

    s0 = gst.NamedTypedList(str, 0)
    print (f'{s0=}')
    print (f'{s0([])}')
    o = s0([("foo",42), ("bar","baz")])
    print (f'{type(o)} {o}')


def test_array():
    nt = gst.Array(int, 2)
    works = nt((1,2))
    validate([("array", nt)], (1,2))

    with pytest.raises(ValueError):
        fails = nt((1,2,3))
    with pytest.raises(ValueError):
        fails = nt(())

    arr = gst.Array(int)
    works = arr((1,2))
    works = arr((1,2,3))

    arr = gst.Array(int,-1)
    with pytest.raises(ValueError):
        fails = arr(())
    works = arr((1,2))
    works = arr((1,2,3))


def test_array_of_array():
    ao2 = gst.Array(gst.Array(int,2))
    works = ao2([(1,2)])
    assert len(works[0]) == 2
    validate([("array_of_array", ao2)], [(1,2)])
    

def test_struct():
    s = gst.Struct(string=str, array2=gst.Array(int,2))
    val = dict(string="hello", array2=(1,2))
    o = s(val)
    assert len(o) == 2
    print(f'{o=}')
    validate([("struct", s)], val)


# def test_named_typed_listofntuples():
    # Xtru = (("polygon", ), ("zsections", )),
    # lon = gst.List[gst.Ntuples(2)]

    # works = lon([ (1,2) ])

    # assert isinstance(works[0], tuple)
    # assert len(works) == 1
    # assert isinstance(works[0][0], str)
    # assert len(works[0]) == 2
    # assert works[0][0] == "1"

    # with pytest.raises(ValueError):
    #     fails = lon([ (1,2,3) ])

    # works = lon([ (1,2), ("3","4mm") ])
    # print(works)

    # works = lon([])
    # print(works)
