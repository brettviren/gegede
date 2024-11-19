#!/usr/bin/env python
'''
For guidance on writing GeGeDe exporter modules see:

  https://github.com/brettviren/gegede/blob/master/doc/exporting.org

'''

from gegede.util import make_module

class Exporter(object):
    '''
    Wrapper around an exporter module which helps to enforce the conventions.
    '''
    def __init__(self, mod):
        if isinstance(mod, str):
            if not '.' in mod:
                mod = 'gegede.export.' + mod
            print ('Importing: "%s"' % mod)
            mod = make_module(mod)
        self.mod = mod

        self.obj = None
        self.out = None

    def convert(self, geom):
        if self.obj:
            return self.obj
        self.obj = self.mod.convert(geom)
        return self.obj

    def dumps(self):
        if not self.obj:
            return None
        return self.mod.dumps(self.obj)

    def validate_object(self):
        if not hasattr(self.mod, 'validate_object'):
            return
        return self.mod.validate_object(self.obj)

    def output(self, filename):
        if self.out:
            return
        if not hasattr(self.mod, 'output'):
            print ('Warning: Module has no output() method: %s' % self.mod)
            return
        self.out = filename
        self.mod.output(self.obj, filename)
        return

    def validate_output(self):
        if not hasattr(self.mod, 'validate_output'):
            return
        return self.mod.validate_output(self.obj, self.filename)

    pass
        
