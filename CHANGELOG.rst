
0.3.1
-----

* Add support for filters so that users can define their own Jinja2 filters and
  use them in templates::

    filters = {
        'filter1': lambda x: "hello world!",
        'filter2': lambda x: x.lower()
    }
    site = staticjinja.make_site(filters=filters)

* Add support for multiple static directories. They can be passed as a string
  of comma-separated names to the CLI or as a list to the Renderer.

* "Renderer" was renamed to "Site" and the Reloader was moved
  staticjinja.reloader.

0.3.0
-----

* Add a command, ``staticjinja``, to handle the simple case of
  building context-less templates.
* Add support for copying static files from the template directory to
  the output directory.
* Add support for testing, linting and checking the documentation
  using ``tox``.

0.2.0
-----

* Add a ``Reloader`` class.

* Add ``Renderer.templates``, which refers to the lists of templates available
  to the ``Renderer``.

* Make ``Renderer.get_context_generator()`` private.

* Add ``Renderer.get_dependencies(filename)``, which gets every file that
  depends on the given file.

* Make ``Renderer.render_templates()`` require a list of templates to render,
  *templates*.
