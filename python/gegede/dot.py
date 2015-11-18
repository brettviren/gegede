
from collections import defaultdict

def write_edges(edges,filename):
    with open(filename,"w") as fp:
        fp.write('digraph "G" {\n')
        for tail,heads in edges.items():
            for head in heads:
                fp.write('\t%s -> %s\n' % (tail,head))
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
            #print '%s --> %s' % (vol.name,daughter)
            if vol.name == daughter:
                print 'WARNING: mother and daughter volumes share same name: "%s"' % vol.name
            make_edges(daughter)

    make_edges(volume_name)
    write_edges(edges, filename)
