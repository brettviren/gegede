

from collections import namedtuple, OrderedDict
import schema as default_schema
from schema.tools import make_maker

class Geometry(object):
    '''A geometry constructor.

    This object provides for creation of elements in a geometry and
    maintains a store of these elements for later retrieval by name.
    '''

    # Set to the name of the world volume
    world = None

    def __init__(self, schema = None):
        '''Create a geometry constructor.

        The optional <schema> object is a raw schema and defaults to
        gegede.schema.Schema.
        '''
        if not schema:
            schema = default_schema.Schema

        parts = sorted(schema.keys())
        self.store = namedtuple('GeometryStore', parts)(*[OrderedDict() for x in parts])

        for part, store in zip(parts,self.store):
            scheme = schema[part]
            types = sorted(scheme.keys())
            makers = [make_maker(store, n, *scheme[n]) for n in types]
            setattr(self, part, namedtuple(part.capitalize(), types)(*makers))

        self.schema = schema
