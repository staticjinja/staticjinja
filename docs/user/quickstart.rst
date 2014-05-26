
Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started
with staticjinja. This assumes you already have staticjinja installed. If you do not,
head over to the :ref:`Installation <install>` section.

Rendering templates
-------------------

If you're just looking to render simple data-less templates, you can get up and running with the following shortcut:

.. code-block:: bash

   $ python -m staticjinja
    Building index.html...
    Templates built.
    Watching 'templates' for changes...
    Press Ctrl+C to stop.

This will recursively search ``./templates`` for templates (any file whose name does not start with ``.`` or ``_``) and build them to ``.``.

If ``easywatch`` is installed, this will also monitor the files in `./templates` and recompile them if they change.


Basic configuration
-------------------

The command line shortcut is convenient, but sometimes your project needs something different than the defaults. To change them, you can use a build script.

A minimal build script looks something like this:

.. code-block:: python

    from staticjinja import make_renderer


    if __name__ == "__main__":
        renderer = make_renderer()
        # enable automatic reloading
        renderer.run(use_reloader=True)

To change behavior, pass the appropriate keyword arguments to ``make_renderer``.

*   To change which directory to search for templates, set ``searchpath="searchpath_name"`` (default is ``./templates``).
*   To change the output directory, pass in ``outpath="output_dir"`` (default is ``.``).
*   To add Jinja extensions, pass in ``extensions=[extension1, extension2, ...]``.
*   To change which files are considered templates, subclass the ``Renderer`` object and override ``is_template``.
*   To change where static files (such as CSS or JavaScript) are stored, set ``staticpath="mystaticfiles"`` (default is ``./static``).

Finally, just save the script as ``build.py`` (or something similar) and run it with your Python interpreter.

.. code-block:: bash

    $ python build.py
    Building index.html...
    Templates built.
    Watching 'templates' for changes...
    Press Ctrl+C to stop.


Loading data
------------

Some applications render templates based on data sources (e.g. CSVs or JSON files).

To get data to templates you can set up a mapping between filenames and functions which generate dictionaries containing the data:

.. code-block:: python

    from staticjinja import make_renderer

    def get_knights():
        """Generate knights of the round table."""
        knights = [
            'sir arthur',
            'sir lancelot',
            'sir galahad',
        ]
        return {'knights': knights}

    if __name__ == "__main__":
        renderer = make_renderer(contexts=[
            ('index.html', get_knights),
        ])
        renderer.run(use_reloader=True)

You can then use the data in ``templates/index.html`` as usual.

.. code-block:: html

    <!-- templates/index.html -->
    {% extends "_base.html" %}
    {% block body %}
    <h1>Hello world!</h1>
    <p>This is an example web page.</p>
    <h3>Knights of the Round Table</h3>
    <ul>
    {% for knight in knights }}
        <li>{{ knight }}</li>
    {% endfor %}
    </ul>
    {% endblock %}
