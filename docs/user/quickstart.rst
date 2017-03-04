Quickstart
==========

Eager to get started? This page gives a good introduction for getting
started with staticjinja.

Installation
------------

staticjinja supports Python 2.6, 2.7, 3.3 and 3.4.

Installing staticjinja is simple with `pip
<http://www.pip-installer.org/>`_::

    $ pip install staticjinja

Rendering templates
-------------------

If you're just looking to render simple data-less templates, you can
get up and running with the following shortcut:

.. code-block:: bash

   $ staticjinja build
    Rendering index.html...

This will recursively search ``./templates`` for templates (any file
whose name does not start with ``.`` or ``_``) and build them to
``.``.

To monitor your source directory for changes, and recompile files if
they change, use ``watch``:

.. code-block:: bash

   $ staticjinja watch
    Rendering index.html...
    Watching 'templates' for changes...
    Press Ctrl+C to stop.

Configuration
-------------

``build`` and ``watch`` each take 3 options:

* ``--srcpath`` - the directory to look in for templates (defaults to
  ``./templates``);
* ``--globals`` - the file to define global variables (defaults to
  ``<srcpath>/globals.yaml``);
* ``--outpath`` - the directory to place rendered files in (defaults
  to ``.``);
* ``--static`` - the directory (or directories) within ``srcpath``
  where static files   (such as CSS and JavaScript) are stored. Static
  files are copied to the output directory without any template
  compilation, maintaining any directory structure. This defaults to
  ``None``, meaning no files are considered to be static files. You
  can pass multiple directories separating them by commas:
  ``--static="foo,bar/baz,lorem"``.

More advanced configuration can be done using the staticjinja API, see
:ref:`custom-build-scripts` for details.
