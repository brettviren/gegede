#!/usr/bin/env python
'''
Some low-level examples of builders.
'''

import gegede.builder
import gegede.construct

class SimpleBuilder(gegede.builder.Builder):
    '''A simple builder that makes a box and if it has a sub-builder,
    puts its volume at the center of the box.
    '''

    def configure(self, dx='1m', dy='1m', dz='1m', mat='Air', **kwds):
        self.box_mat = mat      # assume made somewhere else
        self.box_dim = (dx,dy,dz)

    def construct(self, geom):
        shape = geom.shapes.Box(self.name + '_box_shape', *self.box_dim)
        lv = geom.structure.Volume(self.name+'_volume', material=self.box_mat, shape=shape)
        self.add_volume(lv)

        # now hook up the sub-builder's LV if it exists
        if not self.builders:
            return
        subb = self.builders[0]
        if not subb.volumes:
            return

        sublv = subb.volumes[0]
        geom.structure.Placement("%s_in_%s" % (sublv, lv.name), volume=sublv)
        return


def nested_boxes():
    blist = list()
    last_b = None
    sizes = ['1m', '100cm', '10cm', '1cm', '1mm']
    cfg = dict()

    for size in sizes:          # fake up some configuration and builder building
        sb = SimpleBuilder('builder of box size %s' % size)
        cfg[sb.name] = dict(dx=size,dy=size,dz=size)
        blist.append(sb)
        if last_b:
            sb.builders.append(last_b)
        last_b = sb

    gegede.builder.configure(blist[0], cfg)
    geom = gegede.construct.Geometry()
    gegede.builder.construct(blist[0], geom)
    return geom
