#!/usr/bin/env python
'''
# General Geometry Description

This is the main module for gegede defining a few basic types.
'''

import pint
UndefinedUnitError = pint.UndefinedUnitError

units = pint.UnitRegistry()
'''All values must adhere to the GeGeDe system of units.'''

Quantity = units.Quantity
'''Internally, string representations like "1m" are wrapped in Quantity objects to act like numbers.'''

