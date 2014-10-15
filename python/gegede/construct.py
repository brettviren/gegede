

from collections import namedtuple, OrderedDict
import schema as default_schema
from schema.tools import make_maker
from .util import list_match

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

    def get_shape(self, entry = None, index = 0):
        if hasattr(entry, 'shape'): # allow to pass entry as a Volume object
            entry = entry.shape

        return list_match(self.store.shapes.values(), entry, deref = lambda x: x.name)[index]
