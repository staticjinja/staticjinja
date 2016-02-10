#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import

import os

import staticjinja


def main():
    searchpath = os.path.join(os.getcwd(), 'templates')
    site = staticjinja.make_site(searchpath=searchpath)
    site.render(use_reloader=True)


if __name__ == "__main__":
    main()
