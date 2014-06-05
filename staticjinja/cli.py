#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""staticjinja

Usage:
  staticjinja build [--srcpath=<srcpath> --outpath=<outpath> --static=<static>]
  staticjinja watch [--srcpath=<srcpath> --outpath=<outpath> --static=<static>]
  staticjinja (-h | --help)
  staticjinja --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from __future__ import print_function
from docopt import docopt
import os
import staticjinja
import sys


def main():
    arguments = docopt(__doc__, version='staticjinja 0.3.0')

    if arguments['--srcpath'] is not None:
        srcpath = arguments['--srcpath']
    else:
        srcpath = os.path.join(os.getcwd(), 'templates')

    if not os.path.isdir(srcpath):
        print("The templates directory '%s' is invalid."
              % srcpath)
        sys.exit(1)

    if arguments['--outpath'] is not None:
        outpath = arguments['--outpath']
    else:
        outpath = os.getcwd()

    if not os.path.isdir(outpath):
        print("The output directory '%s' is invalid."
              % outpath)
        sys.exit(1)

    staticdir = arguments['--static']
    staticpath = None

    if staticdir:
        staticpath = os.path.join(srcpath, staticdir)

    if staticpath and not os.path.isdir(staticpath):
        print("The static files directory '%s' is invalid."
              % staticpath)
        sys.exit(1)

    renderer = staticjinja.make_renderer(
        searchpath=srcpath,
        outpath=outpath,
        staticpath=staticdir
    )

    use_reloader = arguments['watch']

    renderer.run(use_reloader=use_reloader)


if __name__ == '__main__':
    main()
