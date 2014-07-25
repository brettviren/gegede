#!/usr/bin/env python

import gegede.configuration as ggdconf

def test_read():
    cfg = ggdconf.parse(__file__.replace('.py','.cfg'))
    print cfg
