#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""staticjinja

Usage:
  staticjinja build [--srcpath=<srcpath> --outpath=<outpath> --static=<a,b,c> \
--globals=<globals.yml>]
  staticjinja watch [--srcpath=<srcpath> --outpath=<outpath> --static=<a,b,c> \
--globals=<globals.yml>]
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
import yaml


def render(args):
    """
    Render a site.

    :param args:
        A map from command-line options to their values. For example:

            {
                '--help': False,
                '--outpath': None,
                '--srcpath': None,
                '--static': None,
                '--globals': None,
                '--version': False,
                'build': True,
                'watch': False
            }
    """
    srcpath = (
        os.path.join(os.getcwd(), 'templates') if args['--srcpath'] is None
        else args['--srcpath'] if os.path.isabs(args['--srcpath'])
        else os.path.join(os.getcwd(), args['--srcpath'])
    )

    if not os.path.isdir(srcpath):
        print("The templates directory '%s' is invalid."
              % srcpath)
        sys.exit(1)

    if args['--outpath'] is not None:
        outpath = args['--outpath']
    else:
        outpath = os.getcwd()

    if not os.path.isdir(outpath):
        print("The output directory '%s' is invalid."
              % outpath)
        sys.exit(1)

    staticdirs = args['--static']
    staticpaths = None

    if staticdirs:
        staticpaths = staticdirs.split(",")
        for path in staticpaths:
            path = os.path.join(srcpath, path)
            if not os.path.isdir(path):
                print("The static files directory '%s' is invalid." % path)
                sys.exit(1)

    envglobalspath = (
        os.path.join(srcpath, 'globals.yaml') if args['--globals'] is None
        else args['--globals'] if os.path.isabs(args['--globals'])
        else os.path.join(srcpath, args['--globals'])
    )

    try:
        with open(envglobalspath, "r") as stream:
            try:
                envglobals = yaml.load(stream)
            except yaml.YAMLError as err:
                print("Failed to parse %s: %s" % (envglobalspath, err))
    except IOError as err:
        envglobals = None

    site = staticjinja.make_site(
        searchpath=srcpath,
        outpath=outpath,
        staticpaths=staticpaths,
        env_globals=envglobals
    )

    use_reloader = args['watch']

    site.render(use_reloader=use_reloader)


def main():
    render(docopt(__doc__, version='staticjinja 0.3.3'))


if __name__ == '__main__':
    main()
