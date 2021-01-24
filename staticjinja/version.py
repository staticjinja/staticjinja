"""
Store the version here, in a single place, because if it's in __init__.py, then
when we try to read the version in setup.py, we are forced to import all the
dependencies in __init__.py, which are probably not installed yet. We can
import this version info from __init__.py as needed.
"""
__version_info__ = (1, 0, 3)
__version__ = '.'.join(map(str, __version_info__))
