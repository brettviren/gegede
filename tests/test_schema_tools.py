#!/usr/bin/env python
'''
Test the gegede.schema.tools module.
'''
import common
from gegede.schema.tools import make_converter, validate_input

def test_converter():
    c = make_converter("1cm")
    o = c("1m")                 # should be okay

    c = make_converter(1)
    try:
        o = c("1m")             # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Failed to catch mismatch with unitless prototype"

    c = make_converter('1cm')
    try:
        o = c(1)             # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Failed to catch mismatch with unitful prototype"

def test_validate_input():
    proto = (("intnum",0),("fpnum",0.0),("dist","0cm"))
    v = validate_input(proto, 1, 2.0, "3meter")

    v = validate_input(proto, 1, dist='4inch')

    try:
        v = validate_input(proto, 1, 2.0, 3) # should fail
    except ValueError:
        pass
    else:
        raise RuntimeError, "Did not catch validation failure."


if "__main__" == __name__:
    test_converter()
    test_validate_input()
