#!/usr/bin/env python
'''
gegede configuration
'''
import os
from collections import OrderedDict

def parse(filenames):
    '''Parse configuration files.

    Return the parser object.'''

    try:                from ConfigParser import SafeConfigParser
    except ImportError: from configparser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.optionxform = str       # want case sensitive
    
    if isinstance(filenames, type("")):
        filenames = [filenames]
    for fname in filenames:
        if not os.path.exists(fname):
            raise ValueError, 'No such file: %s' % fname
        cfg.read(fname)
    return cfg


def cfg2pod(cfg):
    '''
    Convert a ConfigParser object to a plain-old-data structure
    '''
    pod = OrderedDict()
    for secname in cfg.sections():
        secdat = OrderedDict()
        for k,v in cfg.items(secname):
            secdat[k] = v
        pod[secname] = secdat
    return pod

def make_class(fqclass):
    mod, cls = fqclass.rsplit('.',1)
    exec('import %s' % mod) # better way?
    return eval(fqclass)

def make_value(v, **kwds):
    from . import Quantity
    return eval(v, globals(), dict(Q=Quantity, **kwds))


def evaluate(pod):
    '''
    Evaluate and replace each value.
    '''
    ret = OrderedDict()
    for secname, secdat in pod.items():
        newdat = OrderedDict()
        for k,v in secdat.items():
            if k == 'class':
                newdat[k] = make_class(v)
                continue
            newdat[k] = make_value(v, **newdat)
        ret[secname] = newdat
    return ret

def configure(filenames):
    '''
    Return evaluated configuration 
    '''
    cfg = parse(filenames)
    assert cfg.sections()
    pod = cfg2pod(cfg)
    assert pod
    dat = evaluate(pod)
    assert dat
    return dat

