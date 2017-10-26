#!/usr/bin/env python
'''Some functions that do the interpretation of evaluated
configuration data into builder objects.
'''

def make_builder(dat, name = None):
    '''Return the a builder object of the given name from the
    configuration data <dat> and recursively call on any subbuilders.
    If no name is given return the first found.

    This consumes the 'class' and 'subuilders' entries of the configuration dat object.
    '''
    builder_objects = dict()
    if name is None:
        name = dat.items()[0][0]

    top = walk_builder_config_graph(dat, name, builder_objects)
    return top
    
def walk_builder_config_graph(dat, bname, builder_objects):
    '''Recur through the DAG of builder configs'''

    if bname in builder_objects:
        # been here.
        return builder_objects[bname]

    try:
        bdat = dat[bname]
    except KeyError,e:
        print ('No such builder configuration section: "bname"' % bname)
        raise
    klass = bdat.pop('class')   # make exactly one instance
    bobj = klass(bname)
    builder_objects[bname] = bobj;

    subbuilders = bdat.pop('subbuilders',list())
    for sbname in subbuilders:
        sb = walk_builder_config_graph(dat, sbname, builder_objects)
        bobj.builders[sbname] = sb
    return bobj
    
