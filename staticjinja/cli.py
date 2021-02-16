#!/usr/bin/env python

"""staticjinja

Usage:
  staticjinja build [options]
  staticjinja watch [options]
  staticjinja -h | --help
  staticjinja --version

Commands:
  build      Render the site
  watch      Render the site, and re-render on changes to <srcpath>

Options:
  --srcpath=<srcpath>   Directory in which to build from [default: ./templates]
  --outpath=<outpath>   Directory in which to build to [default: ./]
  --static=<a,b,c>      Directory(s) within <srcpath> containing static files
  --log=<level>         Log level {debug,info,warn,error,critical} [default: info]
  -h --help             Show this screen.
  --version             Show version.
"""
import logging
import os
import sys

from docopt import docopt

import staticjinja


def setup_logging(log_string):
    numeric_level = getattr(logging, log_string.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_string}")
    staticjinja.logger.setLevel(numeric_level)


def render(args):
    """
    Render a site.

    :param args:
        A map from command-line options to their values. For example:

            {
                '--help': False,
                '--log': 'info',
                '--outpath': './',
                '--srcpath': './templates',
                '--static': None,
                '--version': False,
                'build': True,
                'watch': False
            }
    """
    setup_logging(args["--log"])

    def resolve(path):
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        return os.path.normpath(path)

    srcpath = resolve(args["--srcpath"])
    if not os.path.isdir(srcpath):
        print("The templates directory '{}' is invalid.".format(srcpath))
        sys.exit(1)

    outpath = resolve(args["--outpath"])

    staticdirs = args["--static"]
    staticpaths = None
    if staticdirs:
        staticpaths = staticdirs.split(",")
        for path in staticpaths:
            path = os.path.join(srcpath, path)
            if not os.path.isdir(path):
                print("The static files directory '{}' is invalid.".format(path))
                sys.exit(1)

    site = staticjinja.Site.make_site(
        searchpath=srcpath, outpath=outpath, staticpaths=staticpaths
    )
    site.render(use_reloader=args["watch"])


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    render(docopt(__doc__, argv=argv, version=staticjinja.__version__))


if __name__ == "__main__":
    main()
