Quickstart
==========

Eager to get started? This page gives a good introduction for getting
started with staticjinja.

Installation
------------

Installing staticjinja is simple:

    $ pip install staticjinja

This installs two things:

* A command line interface (CLI) to staticjinja for basic needs.
* A python library, accessible via the :ref:`Developer Interface`, to be used with a custom
  python build script for advanced needs.


Rendering templates with CLI
----------------------------

If you're just looking to render simple data-less templates, you can
get up and running with the command line interface:

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

CLI Configuration
-----------------

``build`` and ``watch`` each take 3 options:

* ``--srcpath`` - the directory to look in for templates (defaults to
  ``./templates``);
* ``--outpath`` - the directory to place rendered files in (defaults
  to ``.``);
* ``--static`` - the directory (or directories) within ``srcpath``
  where static files (such as CSS and JavaScript) are stored. Static
  files are copied to the output directory without any template
  compilation, maintaining any directory structure. This defaults to
  ``None``, meaning no files are considered to be static files. You
  can pass multiple directories separating them by commas:
  ``--static="foo,bar/baz,lorem"``.

Additionally, you can specify the logging level with
``--log={debug,info,warning,error,critical}``. Default is ``info``.

Next Steps
----------

If the CLI does not satisfy your needs, more advanced configuration can be
done with custom python build scripts using the staticjinja API.
See :ref:`Advanced Usage` for details.
