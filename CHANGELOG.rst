
0.3.3
-----

* Enable users to direct pass dictionaries instead of context generator in Site
  and make_site() for contexts that don't require any logic.

* Introduces a ``mergecontexts`` parameter to Site and make_site() to direct
  staticjinja to either use all matching context generator or only the first
  one when rendering templates.

0.3.2
-----

* Allow passing keyword arguments to jinja2 Environment.

* Use ``shutil.copy2`` instead of ``shutil.copyfile`` when copying static
  resources to preserve the modified time of files which haven't been modified.

* Make the Reloader handle "created" events to support editors like Pycharm
  which save by first deleting then creating, rather than modifying.

* Update easywatch dependency to 0.0.3 to fix an issue that occurs when
  installing easywatch 0.0.2.

* Make ``--srcpath`` accept both absolute paths and relative paths.

* Allow directories to be marked partial or ignored, so that all files inside
  them can be considered partial or ignored. Without this, developers would need
  to rename the contents of these directories manually.

* Allow users to mark a single file as static, instead of just directories.

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
