Changelog
=========

0.4.0_ (2020-11-14)
-------------------

.. _0.4.0: https://github.com/staticjinja/staticjinja/compare/0.3.5...0.4.0

* Improve Travis CI testing: Add Windows and OSX, stop testing python2,
  add newer python3 versions, update tox.ini.

* Convert all print()s to logger.logs().

* Make CLI interface use Site.make_site() instead of deprecated make_site().

* Simplify style and how kwargs are passed around.

* Single-source the version info so it's always consistent.

* Minor fixes, updates, improvements to README, AUTHORS, CONTRIBUTING,
  setup.py, __init__.py docstring,

* Rename Site._env to Site.env, making it publicly accessible, for instance
  in custom rendering functions.

* Fix docstring for the expected signature of custom rendering rules so they
  expect a staticjinja.Site as opposed to a jinja2.Environment

* Make is_{template,static,ignored,partial} functions be consistent with
  taking template names(always use `/`), not file names (use os.path.sep),
  making them consistent between OSs.
  https://github.com/staticjinja/staticjinja/issues/88

* Update and improve docs, add .readthedocs.yml so that ReadTheDocs.org can
  automatically pull from the repo and build docs on changes. Add a badge
  for if the doc build passes. Add readthedocs build task as a GitHub check,
  so new PRs and branches will automatically get this check.

* Change single example/ directory to a collection of examples in examples/,
  and add in an example for using custom rendering rules to generate HTML from
  markdown. This also fixes the totally wrong tutorial on the docs for how to
  use custom rendering rules. See https://github.com/staticjinja/staticjinja/pull/102

* Update dependencies using pip-tools to automatically generate indirect
  dependencies from direct dependencies:

  * jinja2==2.6      -> jinja2==2.11.2
  * argh==0.21.0     -> REMOVED
  * argparse==1.2.1  -> REMOVED
  * docopt==0.6.1    -> docopt==0.6.2
  * easywatch==0.0.5 -> easywatch==0.0.5
  * pathtools==0.1.2 -> pathtools==0.1.2
  * watchdog==0.6.0  -> watchdog==0.10.3
  * wsgiref==0.1.2   -> REMOVED
  * NONE             -> markupsafe==1.1.1

0.3.5_ (2018-08-16)
-------------------

.. _0.3.5: https://github.com/staticjinja/staticjinja/compare/0.3.4...0.3.5

* Make README less verbose.

* Only warn about using deprecated ``staticpaths`` if ``staticpaths`` is
  actually used.

* Updated easywatch to 0.0.5


0.3.4_ (2018-08-14)
-------------------

.. _0.3.4: https://github.com/staticjinja/staticjinja/compare/0.3.3...0.3.4

* Move ``make_site()`` to ``Site.make_site()``.

* Deprecate ``staticpaths`` argument to ``Site()`` and ``Site.make_site()``.
  See `Issue #58`_.

* Add an option (default ``True``) for Jinja's ``FileSystemLoader``
  follow to symlinks when loading templates.

* Ensure that the output directory exists, regardless of whether custom
  rendering rules were supplied. Before that was only ensured if custom
  rendering rules were not given.

* License file is included now in distributions.

* Add documentation for partial and ignored files.

* Updated easywatch to 0.0.4.

* Fix a few style errors.

.. _`Issue #58`: https://github.com/staticjinja/staticjinja/issues/58

0.3.3_ (2016-03-08)
-------------------

.. _0.3.3: https://github.com/staticjinja/staticjinja/compare/0.3.2...0.3.3

* Enable users to direct pass dictionaries instead of context generator in Site
  and make_site() for contexts that don't require any logic.

* Introduces a ``mergecontexts`` parameter to Site and make_site() to direct
  staticjinja to either use all matching context generator or only the first
  one when rendering templates.

0.3.2_ (2015-11-23)
-------------------

.. _0.3.2: https://github.com/staticjinja/staticjinja/compare/0.3.1...0.3.2

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

0.3.1_ (2015-01-21)
-------------------

.. _0.3.1: https://github.com/staticjinja/staticjinja/compare/0.3.0...0.3.1

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

0.3.0_ (2014-06-04)
-------------------

.. _0.3.0: https://github.com/staticjinja/staticjinja/compare/0.2.0...0.3.0

* Add a command, ``staticjinja``, to handle the simple case of
  building context-less templates.
* Add support for copying static files from the template directory to
  the output directory.
* Add support for testing, linting and checking the documentation
  using ``tox``.

0.2.0 (2014-01-04)
------------------

* Add a ``Reloader`` class.

* Add ``Renderer.templates``, which refers to the lists of templates available
  to the ``Renderer``.

* Make ``Renderer.get_context_generator()`` private.

* Add ``Renderer.get_dependencies(filename)``, which gets every file that
  depends on the given file.

* Make ``Renderer.render_templates()`` require a list of templates to render,
  *templates*.
