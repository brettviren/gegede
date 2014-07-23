#!/usr/bin/env python
'''
gegede configuration
'''

def parse(filenames):
    '''Parse the filename, return the parser object.'''
    try:                from ConfigParser import SafeConfigParser
    except ImportError: from configparser import SafeConfigParser
    cfg = SafeConfigParser()
    cfg.optionxform = str       # want case sensitive
    cfg.read(filenames)
    return cfg
