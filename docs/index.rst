staticjinja
===========

staticjinja is a library for easily deploying static sites using the
jinja2_ templating language.

Most static site generators are cumbersome to use. Nevertheless, when
deploying a static website that could benefit from factored out data
or modular html pages (especially convenient when prototyping), a
templating engine can be invaluable. (jinja2 is an extremely powerful
tool in this regard.)

staticjinja is designed to be lightweight, easy-to-use, and highly
extensible, enabling you to focus on simply making your site.

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

This part of the documentation, which is mostly prose, focuses on
step-by-step instructions for getting the most of staticjinja.

.. toctree::
   :maxdepth: 2

   user/quickstart
   user/advanced

API Documentation
-----------------

If you are looking for information on a specific function, class, or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api

Contributor Guide
------------------

If you want to contribute to the project, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 1

   dev/todo
   dev/authors

.. _jinja2: http://jinja.pocoo.org/
