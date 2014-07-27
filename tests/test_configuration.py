#!/usr/bin/env python

import os
import gegede.configuration as ggdconf

def test_read():
    fname = os.path.splitext(__file__)[0]+'.cfg'
    cfg = ggdconf.parse(fname)
    pod = ggdconf.cfg2pod(cfg)
    dat = ggdconf.evaluate(pod)
    assert dat


def test_configure():
    fname = os.path.splitext(__file__)[0]+'.cfg'
    cfg = ggdconf.configure(fname)
    worldname, worldcfg = cfg.items()[0]
    assert 2 == len(worldcfg['subbuilders'])
