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

# This needs to match what is in pyproject.toml
__version_info__ = (2, 0, 1)
__version__ = ".".join(map(str, __version_info__))

from .reloader import Reloader  # noqa: F401 (unused import)
from .staticjinja import make_site, Site  # noqa: F401 (unused import)
