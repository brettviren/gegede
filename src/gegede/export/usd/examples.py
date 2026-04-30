'''
Visual-comparison demo for the USD exporter.

Writes a pair of files (.usda and .gdml) with the same geometry so the
two formats can be visually compared side-by-side.

Usage
-----
    python -m gegede.export.usd.examples /tmp/gegede_demo

This produces /tmp/gegede_demo.usda and /tmp/gegede_demo.gdml.

Viewing
-------
USD:
    usdview /tmp/gegede_demo.usda
    blender --python-expr \\
        "import bpy; bpy.ops.wm.usd_import(filepath='/tmp/gegede_demo.usda')"

GDML (ROOT TGeo):
    root -e 'TGeoManager::Import("/tmp/gegede_demo.gdml"); \\
             gGeoManager->GetTopVolume()->Draw("ogl");'

GDML (HepRApp):
    java -jar HepRApp.jar --file /tmp/gegede_demo.gdml
'''

import sys
from gegede import construct


def demo_geometry():
    '''A geometry exercising Phase-1 shapes: Box, Trapezoid, and Subtraction.'''
    g = construct.Geometry()

    # Materials
    g.matter.Element('Hydrogen', 'H', 1, '1.008g/mole')
    g.matter.Element('Oxygen',   'O', 8, '15.999g/mole')
    g.matter.Element('Nitrogen', 'N', 7, '14.007g/mole')
    water = g.matter.Molecule('Water', density='1.0g/cc',
                              elements=(('Oxygen', 1), ('Hydrogen', 2)))
    air   = g.matter.Mixture('Air',   density='1.29mg/cc',
                              components=(('Nitrogen', 0.78), ('Oxygen', 0.22)))

    # World box: 4m × 4m × 4m (half-extents 2m)
    world_box = g.shapes.Box('world_box', '2m', '2m', '2m')

    # Water sphere: radius 0.5m, placed at origin
    water_sphere = g.shapes.Sphere('water_sphere', rmax='0.5m')

    # Scintillator trapezoid: placed to the +x side
    scint_trap = g.shapes.Trapezoid('scint_trap',
                                    '0.1m', '0.05m',  # dx1, dx2
                                    '0.3m', '0.2m',   # dy1, dy2
                                    '0.4m')            # dz

    # A box minus a small sphere (boolean subtraction)
    inner_box = g.shapes.Box('inner_box', '0.3m', '0.3m', '0.3m')
    cutout_sph = g.shapes.Sphere('cutout_sph', rmax='0.35m')
    box_minus_sph = g.shapes.Subtraction('box_minus_sph',
                                          first='inner_box',
                                          second='cutout_sph')

    # Volumes
    water_vol = g.structure.Volume('water_vol',   material=water, shape=water_sphere)
    trap_vol  = g.structure.Volume('trap_vol',    material=water, shape=scint_trap)
    diff_vol  = g.structure.Volume('diff_vol',    material=water, shape=box_minus_sph)
    world_vol = g.structure.Volume('world_vol',   material=air,   shape=world_box,
                                   placements=[])

    # Positions
    pos_sphere = g.structure.Position('pos_sphere',   x='0m',    y='0m',   z='0m')
    pos_trap   = g.structure.Position('pos_trap',     x='1.2m',  y='0m',   z='0m')
    pos_diff   = g.structure.Position('pos_diff',     x='-1.2m', y='0m',   z='0m')

    # Placements
    pl_sphere = g.structure.Placement('pl_sphere', volume=water_vol, pos=pos_sphere)
    pl_trap   = g.structure.Placement('pl_trap',   volume=trap_vol,  pos=pos_trap)
    pl_diff   = g.structure.Placement('pl_diff',   volume=diff_vol,  pos=pos_diff)

    # Rebuild world with placements
    world_vol2 = g.structure.Volume('world_vol_placed', material=air, shape=world_box,
                                    placements=[pl_sphere, pl_trap, pl_diff])
    g.set_world(world_vol2)
    return g


def main(stem='/tmp/gegede_demo'):
    import gegede.export.usd  as usd_exp
    import gegede.export.gdml as gdml_exp

    g = demo_geometry()

    gdml_obj = gdml_exp.convert(g)
    gdml_bytes = gdml_exp.dumps(gdml_obj)
    gdml_path = stem + '.gdml'
    with open(gdml_path, 'wb') as fh:
        fh.write(gdml_bytes)
    print(f'GDML: {gdml_path}')

    usd_obj = usd_exp.convert(g)
    usda_path = stem + '.usda'
    usd_exp.output(usd_obj, usda_path)
    print(f'USD:  {usda_path}')

    print()
    print('View USD:  usdview', usda_path)
    print('View GDML: root -e \'TGeoManager::Import("' + gdml_path + '"); '
          'gGeoManager->GetTopVolume()->Draw("ogl");\'')


if __name__ == '__main__':
    stem = sys.argv[1] if len(sys.argv) > 1 else '/tmp/gegede_demo'
    main(stem)
