
from collections import defaultdict

def builder_hierarchy(cfg, start_name, filename):

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

    with open(filename,"w") as fp:
        fp.write('digraph "G" {\n')
        for tail,heads in edges.items():
            for head in heads:
                fp.write('\t%s -> %s\n' % (tail,head))
        fp.write('}\n')
        
