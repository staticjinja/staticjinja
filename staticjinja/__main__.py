#!/usr/bin/env python

import os

from .staticjinja import Site

if __name__ == "__main__":
    searchpath = os.path.join(os.getcwd(), "templates")
    site = Site.make_site(searchpath=searchpath)
    site.render(use_reloader=True)
