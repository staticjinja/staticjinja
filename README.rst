staticjinja
===========

.. image:: https://badge.fury.io/py/staticjinja.png
    :target: https://badge.fury.io/py/staticjinja
    :alt: PyPi Badge

.. image:: https://github.com/staticjinja/staticjinja/workflows/build/badge.svg?branch=main&event=schedule
    :target: https://github.com/staticjinja/staticjinja/actions?query=branch%3Amain
    :alt: Build and Testing Status

.. image:: https://readthedocs.org/projects/staticjinja/badge/?version=stable
    :target: https://staticjinja.readthedocs.io/en/stable/?badge=stable&style=plastic
    :alt: Documentation Status

.. image:: https://codecov.io/gh/staticjinja/staticjinja/branch/main/graph/badge.svg?token=En337ZXsPK
    :target: https://codecov.io/gh/staticjinja/staticjinja
    :alt: Test coverage status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: Black

.. image:: https://static.pepy.tech/personalized-badge/staticjinja?period=total&units=international_system&left_color=black&right_color=blue&left_text=downloads
    :target: https://pepy.tech/project/staticjinja
    :alt: PyPi downloads total

.. image:: https://static.pepy.tech/personalized-badge/staticjinja?period=month&units=international_system&left_color=black&right_color=blue&left_text=downloads/month
    :target: https://pepy.tech/project/staticjinja
    :alt: PyPi downloads per month

**staticjinja** is a library that makes it easy to build static sites using
Jinja2_.

Many static site generators are complex, with long manuals and unnecessary
features. But using template engines to build static websites is really useful.

staticjinja is designed to be lightweight (under 500 lines of source code),
and to be easy to use, learn, and extend, enabling you to focus on making your
site.

.. code-block:: bash

    $ mkdir templates
    $ vim templates/index.html
    $ staticjinja watch
    Building index.html...
    Templates built.
    Watching 'templates' for changes...
    Press Ctrl+C to stop.


Installation
------------

To install staticjinja, simply:

.. code-block:: bash

    $ pip install staticjinja

Documentation
-------------

Documentation is available at
https://staticjinja.readthedocs.io.

Contribute
----------

Please see CONTRIBUTING_.

.. _CONTRIBUTING: CONTRIBUTING.rst
.. _Jinja2: https://jinja.palletsprojects.com
