#!/usr/bin/env python
'''
Test the gegede.schema.tools module.
'''

from gegede.schema.tools import make_converter, validate_input
from gegede import Quantity as Q
import pytest

def test_converter():
    c = make_converter("1cm")
    assert isinstance(c("1m"), Q)
    with pytest.raises(ValueError):
        c(1)                    # should fail

    c = make_converter(int)
    with pytest.raises(ValueError):
        c("1m")                 # should fail

    o = c("1")
    assert isinstance(c("1"), int)

    c = make_converter('0')
    q = c(1)
    print(f'{q} {type(q)}')
    assert isinstance(q, Q)
    q *= -1
    assert q == Q(-1)

    print(f'{type(q)} {q=}')

    c = make_converter(float)
    q = c(1)
    assert q == 1


def test_validate_input():
    proto = (("intnum",int),("fpnum",float),("dist","0cm"))
    validate_input(proto, 1, 2.0, "3meter")

    validate_input(proto, 1, dist='4inch')

    try:
        validate_input(proto, 1, 2.0, 3) # should fail
    except ValueError:
        pass
    else:
        raise (RuntimeError, "Did not catch validation failure.")


if "__main__" == __name__:
    test_converter()
    test_validate_input()
