#!/usr/bin/env python
'''
gegede configuration
'''
import os
import re
from collections import OrderedDict

def parse(filenames):
    '''Parse configuration files.

    Return the parser object.'''

    try:
        from ConfigParser import SafeConfigParser as ConfParse
    except ImportError:
        from configparser import ConfigParser as ConfParse

    cfg = ConfParse()
    cfg.optionxform = str       # want case sensitive
    
    if isinstance(filenames, type("")):
        filenames = [filenames]
    for fname in filenames:
        if not os.path.exists(fname):
            raise ValueError('No such file: %s' % fname)
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

interp_reobj = re.compile(r'{([\w:]+)}')
def interpolate_value(value, secname, sections):
    def getter(match):
        m = match.group(1)
        try:
            name, key = m.split(':')
        except ValueError:
            key = m
            name = secname
        return sections[name][key]
    ret = re.subn(interp_reobj, getter, value)
    return ret[0]

def interpolate(sections):
    '''Perform string interpolation values <sections>.

    The <sections> data structure is a dictionary keyed by SECTION name.

    Each section value is a dictionary keyed by KEY with string values.

    Interpolation is performed on literals matching {KEY} or {SECTION:KEY}.
    '''
    while True:
        changed = False
        for secname, secdict in sections.items():
            for key, val in secdict.items():
                newval = interpolate_value(val, secname, sections)
                if newval == val:
                    continue
                changed = True
                sections[secname][key] = newval
        if changed:
            continue
        break
        


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

    interpolate(pod)

    dat = evaluate(pod)
    assert dat
    return dat

