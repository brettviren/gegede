

from collections import namedtuple, OrderedDict
import gegede.schema as default_schema
from gegede.schema.tools import make_maker
from gegede.util import list_match

class Geometry(object):
    '''A geometry constructor.

    This object provides for creation of elements in a geometry and
    maintains a store of these elements for later retrieval by name.
    '''

    # Name of world volume, set via .set_world()
    _world = None

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

    @property
    def world(self):
        return self._world

    def set_world(self, world):
        if hasattr(world, 'name'):
            self._world = world.name
        else:
            self._world = world

    def get_shape(self, entry = None, index = 0):
        if hasattr(entry, 'shape'): # allow to pass entry as a Volume object
            entry = entry.shape

        return list_match(self.store.shapes.values(), entry, deref = lambda x: x.name)[index]


    def insert(self, placement, parent=None):
        '''
        Insert a child placement into a given parent volume or the world volume.
        
        Nominally, this method should be avoided.  Once created, a parent Volume
        should be considered opaque to future modifications (child placement).
        However, in rare cases it may be necessary to have an existing parent
        adopt a new child placement.  This can be accomplished by a clever
        developer that understands the store data structure but it is somewhat
        error prone.  This method makes sure this expert operation is done
        correctly.
        '''
        # store the placement
        try:
            pname = placement.name
        except AttributeError:
            raise ValueError(f'must insert placement as object, got: "{placement}"')
        self.store.structure[pname] = placement

        # adopt by parent
        if parent is None:
            parent = self.world
        if isinstance(parent, str):
            parent = self.store.structure[parent]
        parent.placements.append(placement.name)
        
