#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""staticjinja

Usage:
  staticjinja build [--srcpath=<srcpath> --outpath=<outpath> --static=<a,b,c>]
  staticjinja watch [--srcpath=<srcpath> --outpath=<outpath> --static=<a,b,c>]
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

    staticdirs = arguments['--static']
    staticpaths = None

    if staticdirs:
        staticpaths = staticdirs.split(",")
        for path in staticpaths:
            path = os.path.join(srcpath, path)
            if not os.path.isdir(path):
                print("The static files directory '%s' is invalid." % path)
                sys.exit(1)

    site = staticjinja.make_site(
        searchpath=srcpath,
        outpath=outpath,
        staticpaths=staticpaths
    )

    use_reloader = arguments['watch']

    site.render(use_reloader=use_reloader)


if __name__ == '__main__':
    main()
