
staticjinja
===========

.. image:: https://badge.fury.io/py/staticjinja.png
    :target: http://badge.fury.io/py/staticjinja

.. image:: https://pypip.in/d/staticjinja/badge.png
        :target: https://crate.io/packages/staticjinja/

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


Installation
------------

To install staticjinja, simply:

.. code-block:: bash

    $ pip install staticjinja

Optionally, to enable automatic reloading:

.. code-block:: bash

    $ pip install easywatch


Documentation
-------------

Documentation is available at http://staticjinja.readthedocs.org/en/latest/

Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: https://github.com/Ceasar/staticjinja
.. _AUTHORS: https://github.com/Ceasar/staticjinja/blob/master/AUTHORS.rst
.. _jinja2: http://jinja.pocoo.org/
