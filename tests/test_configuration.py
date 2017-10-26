#!/usr/bin/env python

import os
import gegede.configuration as ggdconf
from gegede import Quantity as Q

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
    assert worldcfg['width'] == Q(10,'meter')
    want_height = Q(100,'meter')
    assert worldcfg['height'] == want_height
    assert worldcfg['depth'] == Q(123,'meter')

    assert type(worldcfg['integer']) == int
    assert type(worldcfg['floating']) == float
    assert type(worldcfg['string']) == str
    assert type(worldcfg['sequence']) == list

    sb1name, sb1cfg = cfg.items()[1]
    print (sb1name,sb1cfg)
    # this fails because interpolation is global and before evaluation
    #assert sb1cfg['height'] == want_height
    

from gegede.configuration import interpolate_value, interpolate
def test_interpolate_value():
    dat = dict(aa = dict(a='{b}', b='aaa'),
               bb = dict(a='{aa:b}', b='{a}{aa:a}'))
    for give, want, sec in [('x','x','aa'),
                            ('xxx{a}yyy', 'xxx{b}yyy', 'aa'),
                            ('xxx{a}yyy', 'xxx{aa:b}yyy', 'bb'),
                            ('xxx{b}yyy', 'xxxaaayyy', 'aa'),
                            ('xxx{b}yyy', 'xxx{a}{aa:a}yyy', 'bb')]:
        got = interpolate_value(give, sec, dat)
        assert want == got, 'in section %s: "%s" gave "%s" wanted "%s"' % (sec, give, got, want)
def test_interpolate():
    dat = dict(aa = dict(a='{b}', b='aaa'),
               bb = dict(a='{aa:b}', b='{a}{aa:a}'))
    interpolate(dat)
    assert dat['aa']['a'] == 'aaa', str(dat)
    assert dat['aa']['b'] == 'aaa', str(dat)
    assert dat['bb']['a'] == 'aaa', str(dat)
    assert dat['bb']['b'] == 'aaaaaa', str(dat)
