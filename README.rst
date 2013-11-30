
staticjinja
===========

staticjinja is a library for easily deploying static sites using the extremely handy [jinja2](http://jinja.pocoo.org/docs/) templating language.

Most static site generators are cumbersome to use. However, when deploying a static website that could benefit from factored out data or modular html pages (especially convenient when prototyping), a templating engine can be of great help. (jinja2 is an extremely powerful tool in this regard.)

staticjinja is extremely lightweight and easy-to-use and enables you to focus on just making your site.

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

Documentation is available at `docs/`.


Contribute
----------

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: https://github.com/Ceasar/staticjinja
.. _AUTHORS: https://github.com/Ceasar/staticjinja/blob/master/AUTHORS.rst
.. _`docs/`: https://github.com/Ceasar/staticjinja/tree/master/docs
