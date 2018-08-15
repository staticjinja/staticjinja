staticjinja
===========

.. image:: https://badge.fury.io/py/staticjinja.png
    :target: http://badge.fury.io/py/staticjinja

.. image:: https://travis-ci.org/Ceasar/staticjinja.svg
    :target: https://travis-ci.org/Ceasar/staticjinja

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
http://staticjinja.readthedocs.org/en/latest/.

Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion
   around a feature idea or a bug.
#. Fork `the repository`_ on GitHub to start making your changes to
   the **master** branch (or branch off of it).
#. Send a pull request and bug the maintainer until it gets merged and
   published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: https://github.com/Ceasar/staticjinja
.. _AUTHORS: https://github.com/Ceasar/staticjinja/blob/master/AUTHORS.rst
.. _Jinja2: http://jinja.pocoo.org/
