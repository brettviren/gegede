#!/usr/bin/env python
'''
Methods to iterate over a geometry.
'''

def ascending_all(store, top):
    '''Iterate from children to parents up to given top volume.
    '''
    if isinstance(top, type("")):
        top = store[top]
    for pname in top.placements:
        place = store[pname]
        vname = place.volume
        daughter = store[vname]
        for ret in ascending_all(store, daughter):
            yield ret
    yield top
            
def ascending(store, top):
    '''Iterate from children to parents up to given top volume.
    '''
    seen = set()
    ret = list()
    for vol in ascending_all(store, top):
        if vol.name in seen:
            continue
        seen.add(vol.name)
        ret.append(vol)
    return ret

 

