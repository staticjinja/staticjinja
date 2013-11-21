#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import absolute_import

import os

import staticjinja

if __name__ == "__main__":
    template_folder = os.path.join(os.getcwd(), 'templates')
    renderer = staticjinja.make_renderer(template_folder=template_folder)
    renderer.run(use_reloader=True)
