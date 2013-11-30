.. staticjinja documentation master file, created by
   sphinx-quickstart on Sat Nov 30 14:33:03 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

staticjinja
===========

staticjinja is a library for easily deploying static sites using the jinja2_ templating language.

Most static site generators are cumbersome to use. Nevertheless, when deploying a static website that could benefit from factored out data or modular html pages (especially convenient when prototyping), a templating engine can be invaluable. (jinja2 is an extremely powerful tool in this regard.)

staticjinja is designed to be lightweight, easy-to-use, and highly extensible, enabling you to focus on simply making your site.

.. code-block:: bash

    $ mkdir templates
    $ vim templates/index.html
    $ python -m staticjinja
    Building index.html...
    Templates built.
    Watching 'templates' for changes...
    Press Ctrl+C to stop.



User Guide
----------

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart
   user/advanced

Contributor Guide
------------------

.. toctree::
   :maxdepth: 1

   dev/todo
   dev/authors

.. _jinja2: http://jinja.pocoo.org/
