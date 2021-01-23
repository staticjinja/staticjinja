"""
staticjinja
===========

staticjinja is a library that makes it easy to build static sites using Jinja2.

Many static site generators are complex, with long manuals and unnecessary
features. But using template engines to build static websites is really useful.
staticjinja is designed to be lightweight (under 500 lines of source code), and
to be easy to use, learn, and extend, enabling you to focus on making your site.

Documentation is available at https://staticjinja.readthedocs.org.

Please file bugs, view source code, and contribute at
https://github.com/staticjinja/staticjinja/
"""

# flake8: noqa
from .version import __version__, __version_info__

from .reloader import Reloader
from .staticjinja import make_site, Site
