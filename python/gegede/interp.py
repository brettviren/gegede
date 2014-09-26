#!/usr/bin/env python
'''Some functions that to the interpretation of evaluated
configuration data into builder objects.
'''

def get_builder_config(dat, name):
    '''
    Return the builder's configuration section of the given <name>.

    If <name> is None, return first builder in <dat>.
    '''
    if name is None:
        return dat.items()[0]
    return name, dat[name]

def make_builder(dat, name = None):
    '''Return the a builder object of the given name from the
    configuration data <dat> and recursively call on any subbuilders.
    If no name is given return the first found.
    '''
    bname, bdat = get_builder_config(dat, name)
    klass = bdat.pop('class')
    bobj = klass(bname)
    subbuilders = bdat.pop('subbuilders',list())
    for sbname in subbuilders:
        sb = make_builder(dat, sbname)
        bobj.builders[sbname] = sb
    return bobj
    
