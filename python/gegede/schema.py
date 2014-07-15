#!/usr/bin/env python
'''
The schema for the categories of geometry description.

'''

from collections import namedtuple, OrderedDict


Schema = dict(
    Shapes = [
        ("Box", (("x",0.0), ("y",0.0), ("z",0.0))),
        ("Sphere", (("r",0.0),)),
    ]
)


def make_ntt_typed(collector, ntname, *proto):
    '''
    Make a namedtuple class that checks type of args by attempting to convert values.

    The <args> is a list of 2-tuples ("membername",type)
    '''
    member_names = [p[0] for p in proto]
    def instantiator(objname, *args, **kwargs):
        if objname in collector:
            raise ValueError, 'Instance "%s" of type %s already in %s' % \
                (objname, ntname, collector)

        members = OrderedDict()
        converters = dict()
        for name,val in proto:
            members[name] = val
            converters[name] = type(val)

        already = list()
        for k,v in zip(member_names, args):
            members[k] = converters[k](v)
            already.append(k)
        for k,v in kwargs.items():
            if k not in converters.keys():
                raise ValueError, 'Unknown data member "%s" for "%s"' % (k,ntname)
            if k in already:
                raise ValueError, 'Keyword argument already supplied as positional: %s' % k
            members[k] = converters[k](v)

        NTT = namedtuple(ntname, ['name'] + member_names)
        obj = NTT(objname, *members.values())
        collector[objname] = obj
        return obj
    instantiator.__name__ = ntname
    instantiator.__doc__ = "%s: %s" % (ntname, ', '.join(member_names))
    return instantiator

shape_store = OrderedDict()

def make_shapes(shapes_schema):
    shape_classes = list()
    shape_names = [ss[0] for ss in shapes_schema]
    ShapeCollection = namedtuple("Shapes", shape_names)
    shapes = list()
    for ss in shapes_schema:
        shape = make_ntt_typed(shape_store, ss[0], *ss[1])
        shapes.append(shape)
    return ShapeCollection(*shapes)
shapes = make_shapes(Schema['Shapes'])


