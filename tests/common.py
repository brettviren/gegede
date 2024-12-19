#!/usr/bin/env python

import os
import sys

testdir = os.path.dirname(os.path.realpath(__file__))
print ('gegede testing in %s' % testdir)
srcdir = os.path.dirname(testdir)
pydir = os.path.join(srcdir,'python')
sys.path.insert(0,pydir)


