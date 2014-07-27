#!/usr/bin/env python
'''
High level main functions.
'''
import gegede.configuration
import gegede.interp
import gegede.builder



def generate(filenames, world_name = None):
    '''
    Return a geometry object generated from the given configuration file(s).
    '''
    assert filenames
    cfg = gegede.configuration.configure(filenames)
    assert cfg
    wbuilder = gegede.interp.make_builder(cfg, world_name)
    gegede.builder.configure(wbuilder, cfg)
    geom = gegede.construct.Geometry()
    gegede.builder.construct(wbuilder, geom)
    return geom
