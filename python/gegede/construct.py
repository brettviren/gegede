

from collections import namedtuple, OrderedDict
import schema as default_schema
from schema.tools import make_maker

class GeometryStore(object):
    '''
    A "dumb" data class collecting a geometry.

    See the class "Geometry" for a suitable manager of this data.
    '''
    def __init__(self):
        self.shapes = OrderedDict()
        self.matter = OrderedDict()
        

class Geometry(object):
    '''A geometry constructor.

    This object provides for creation of elements in a geometry and
    maintains a store of these elements for later retrieval by name.
    '''
    def __init__(self, schema = None):
        '''Create a geometry constructor.

        The optional <schema> object is a raw schema and defaults to
        gegede.schema.Schema.
        '''
        self.store = GeometryStore()
        self.load_schema(schema or default_schema.Schema)

    def load_schema(self, schema):
        '''
        Instrument self with members to create elements described in the schema.
        '''
        # for now hard-code knowledge of the schema, fixme: can we make this implicit?

        scheme = schema['shapes']
        types = sorted(scheme.keys())
        makers = [make_maker(self.store.shapes, n, *scheme[n]) for n in types]
        self.shapes = namedtuple("Shapes", types)(*makers)
        
        scheme = schema['matter']
        types = sorted(scheme.keys())
        makers = [make_maker(self.store.matter, n, *scheme[n]) for n in types]
        self.matter = namedtuple("Matter", types)(*makers)
