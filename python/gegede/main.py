#!/usr/bin/env python
'''
High level main functions.

The main runs in these stages:

 1) Generate
    - parse configuration
    - construct GeGeDe geometry objects
 2) Optional validation on GeGeDe objects
 3) Export
    - produce transient export-specific objects
    - optionally validate these objects
    - write these objects out to persistent storage
    - optionally validate the persistent representation

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
    assert len(wbuilder.volumes) == 1, 'Top level builder "%s" must only produce one LV, produced %d' % (wbuilder.name, len(wbuilder.volumes))
    geom.world = wbuilder.get_volume(0)
    print 'Generated world "%s"' % geom.world.name
    # fixme: here would be a good time to do some internal validation
    return geom


def main ():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--world", default=None,
                        help="World builder name")
    parser.add_argument("-f", "--format", default=None,
                        help = "Export format, guess by extension if not given")
    parser.add_argument("-o", "--output", default=None,
                        help="File to export to")
    parser.add_argument("-V", "--validate", action='store_true',
                        help="Validate geometry using built-in GeGeDe")
    parser.add_argument("-O", "--validate-object", action='store_true',
                        help="Validate exported, in-memory objects")
    parser.add_argument("-F", "--validate-file", action='store_true',
                        help="Validate exported, on-file objects")
    parser.add_argument("config", nargs='+',
                        help="Configuration file(s)")
    args = parser.parse_args()

    if not args.format and '.' not in args.output:
        raise parser.error("Can not guess format.  Need --format or --output with file extension")
    if not args.format:
        args.format = os.path.splitext(args.output)[1][1:]
    if args.output == '-':
        args.output = "/dev/stdout"

    geom = generate(args.config, args.world)
    if args.validate:
        import gegede.validation
        gegede.validation.validate(geom)
    from gegede.export import Exporter
    exporter = Exporter(args.format)
    print 'Converting with module: %s' % exporter.mod

    obj = exporter.convert(geom)
    if args.validate_object:
        exporter.validate_object()

    exporter.output(args.output)

    if args.validate_file:
        exporter.validate_file()
    return


