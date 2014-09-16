#!/usr/bin/env python
'''
Methods to iterate over a geometry.
'''

def ascending(store, top):
    '''Iterate from children to parents up to given top volume.
    '''
    if isinstance(top, type("")):
        top = store[top]
    for pname in top.placements:
        place = store[pname]
        vname = place.volume
        daughter = store[vname]
        for ret in ascending(store, daughter):
            yield ret
    yield top
 

