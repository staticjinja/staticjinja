#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import absolute_import

from .staticjinja import Renderer
import os

if __name__ == "__main__":
    template_folder = os.path.join(os.getcwd(), 'templates')
    renderer = Renderer(template_folder=template_folder)
    renderer.run(debug=True, use_reloader=True)
