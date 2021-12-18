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
__version_info__ = (4, 1, 2)
__version__ = ".".join(map(str, __version_info__))

import logging

# Set up logging (before importing anything else that may use this logger).
# Users can configure/disable logging via staticjinja.logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

from .reloader import Reloader  # noqa: F401,E402 (unused import, not at top of file)
from .staticjinja import Site  # noqa: F401,E402
