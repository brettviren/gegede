#!/usr/bin/env python
'''
Example gegede builders for a trivial LAr geometry
'''

import gegede.builders

class WorldBuilder(gegede.builders.Builder):
    '''
    Build a big box world volume.
    '''

    def configure(self, size='50m', material='Rock', **kwds):
        self.size = size
        self.material = material

    def construct(self, geom):
        shape = geom.shapes.Box(self.name + '_box_shape', dx=self.size, dy=self.size, dz=self.size)
        lv = geom.structure.Volume(self.name+'_volume', material=self.box_mat, shape=shape)
        self.add_volume(lv)

        site_lv = self.builders[0].volumes[0] # expect one sub-builder with one logical volume
        geom.structure.Placement('%s_in_%s' % (site_lv.name, self.name), volume = site_lv)
        return

class SiteBuilder(gegede.builders.Builder):
    def configure(self, site='homestake', material = 'Air', **kwds):
        self.site = site.lower()
        self.material = material

    def construct(self, geom):
        if self.site == 'homestake':
            shape = geom.structure.Box('homestake site box', dx='10m', dy='10m', dz='10m')
        elif self.site == '35t':
            shape = geom.structure.Box('35t site box', dx='5m', dy='5m', dz='5m')
        else:
            raise ValueError('Unknown site: "%s"' % self.site)
        lv = geom.structure.Volume(self.site + '_volume', material=self.material, shape = self.shape)
