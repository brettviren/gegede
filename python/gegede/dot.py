#!/usr/bin/env python
'''
GGD support for GraphViz dot.
'''

import logging
log = logging.getLogger('gegede')
warn = log.warn

from collections import defaultdict

def wash(name):
    return name.replace('-','_')


def write_edges(edges,filename):
    with open(filename,"w") as fp:
        fp.write('digraph "G" {\n')
        for tail,heads in edges.items():
            for head in heads:
                fp.write('\t%s -> %s\n' % (wash(tail),wash(head)))
        fp.write('}\n')


def builder_hierarchy(cfg, start_name, filename):
    '''
    Write a GraphViz dot file showing the hierarchy of builders.
    '''

    if start_name is None:
        start_name = cfg.items()[0][0]

    edges = defaultdict(set)

    def make_edges(name):
        sec = cfg[name]
        sbs = sec.get('subbuilders',list())
        for sb in sbs:
            edges[name].add(sb)
            make_edges(sb)
    make_edges(start_name)
    write_edges(edges, filename)


def volume_hierarchy(geom, volume_name, filename):
    '''
    Write a GraphViz dot file showing the hierarchy of volumes.
    '''
    if volume_name is None:
        volume_name = geom.world

    edges = defaultdict(set)
    seen = set()

    def make_edges(name):
        if name in seen:
            return
        seen.add(name)
        vol = geom.store.structure[name]
        for pname in vol.placements:
            place = geom.store.structure[pname]
            daughter = place.volume
            edges[vol.name].add(daughter)
            if vol.name == daughter:
                warn('mother and daughter volumes share same name: "%s"' % vol.name)
            make_edges(daughter)

    make_edges(volume_name)
    write_edges(edges, filename)


def placement_hierarchy(geom, volume_name, filename):
    '''
    Write a GraphViz dot file showing hierarchy of volume placements.

    Note: this can make a horrendous graph.
    '''

    if volume_name is None:
        volume_name = geom.world

    edges = defaultdict(set);
    volumes = set()
    placements = set()

    def walk_hier(name):
        if name in volumes:
            return
        volumes.add(name)
        vol = geom.store.structure[name]
        for pname in vol.placements:
            place = geom.store.structure[pname]
            placements.add(place.name)
            edges[vol.name].add(place.name)
            daughter = place.volume
            edges[place.name].add(daughter)
            walk_hier(daughter)

    walk_hier(volume_name)

    with open(filename,"w") as fp:
        fp.write('digraph "G" {\n')
        # nodes
        for vol in volumes:
            fp.write('\t%s;\n' % wash(vol));
        for pla in placements:
            fp.write('\t%s[shape=diamond];\n' % wash(pla));
        for tail,heads in edges.items():
            for head in heads:
                fp.write('\t%s -> %s\n' % (wash(tail),wash(head)))
        fp.write('}\n')


        
