#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from . import staticjinja

if __name__ == "__main__":
    searchpath = os.path.join(os.getcwd(), 'templates')
    site = staticjinja.make_site(searchpath=searchpath)
    site.render(use_reloader=True)
