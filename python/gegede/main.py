#!/usr/bin/env python
'''
High level main functions.
'''
import os


def generate(filenames, world_name = None):
    '''
    Return a geometry object generated from the given configuration file(s).
    '''
    import gegede.configuration
    import gegede.interp
    import gegede.builder
    import gegede.construct

    assert filenames
    cfg = gegede.configuration.configure(filenames)
    assert cfg
    wbuilder = gegede.interp.make_builder(cfg, world_name)
    gegede.builder.configure(wbuilder, cfg)
    geom = gegede.construct.Geometry()
    gegede.builder.construct(wbuilder, geom)
    return geom

def export_gdml(geom, filename):
    import gegede.export.gdml
    s = gegede.export.gdml.dumps(geom)
    open(filename,'w').write(s)
    return

def export_json(geom, filename):
    import gegede.export.ggdjson
    s = gegede.export.ggdjson.dumps(geom)
    open(filename,'w').write(s)
    return
    
def export_pod(geom, filename):
    import gegede.export.pod
    s = gegede.export.pod.dumps(geom)
    open(filename,'w').write(s)


def export(geom, filename, ext = None):
    ext = ext or os.path.splitext(filename)[1][1:]
    try:
        meth = eval("export_%s"%ext)
    except NameError:
        raise ValueError, 'Unknown export format: "%s" for file %s' % (ext, filename)
    meth(geom, filename)

def main ():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--world", default=None,
                        help="World builder name")
    parser.add_argument("-f", "--format", default=None,
                        help = "Export format, guess by extension if not given")
    parser.add_argument("-o", "--output", default=None,
                        help="File to export to")
    parser.add_argument("config", nargs='+',
                        help="Configuration file(s)")
    args = parser.parse_args()

    if not args.format and '.' not in args.output:
        raise parser.error("Can not guess format.  Need --format or --output with file extension")
        
    if args.output == '-':
        args.output = "/dev/stdout"

    geom = generate(args.config, args.world)
    export(geom, args.output, args.format)
    return


