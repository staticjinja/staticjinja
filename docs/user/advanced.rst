
.. _standard Jinja2 filters: http://jinja.pocoo.org/docs/dev/templates/#builtin-filters

Advanced Usage
==============

This document covers some of staticjinja's more advanced features.

.. _partials-and-ignored-files:

Partials and ignored files
--------------------------

A **partial file** is a file whose name begins with a ``_``. Partial files are
intended to be included in other files and are not rendered. If a partial file
changes, it will trigger a rebuild if you are running ``staticjinja watch``.

An **ignored file** is a file whose name begins with a ``.``. Ignored files are
neither rendered nor used in rendering templates.

If you want to configure what is considered a partial or ignored file, subclass
``Site`` and override ``is_partial`` or ``is_ignored``.

.. _custom-build-scripts:

Using Custom Build Scripts
--------------------------

The command line shortcut is convenient, but sometimes your project
needs something different than the defaults. To change them, you can
use a build script.

A minimal build script looks something like this:

.. code-block:: python

    from staticjinja import Site


    if __name__ == "__main__":
        site = Site.make_site()
        # enable automatic reloading
        site.render(use_reloader=True)

To change behavior, pass the appropriate keyword arguments to
``Site.make_site``.

* To change which directory to search for templates, set
  ``searchpath="searchpath_name"`` (default is ``./templates``).
* To change the output directory, pass in ``outpath="output_dir"``
  (default is ``.``).
* To add Jinja extensions, pass in ``extensions=[extension1,
  extension2, ...]``.
* To change which files are considered templates, subclass the
  ``Site`` object and override ``is_template``.
* To change where static files (such as CSS or JavaScript) are stored,
  set ``staticpaths=["mystaticfiles/"]`` (the default is ``None``, which
  means no files are considered to be static files). You can pass
  multiple directories in the list: ``staticpaths=["foo/", "bar/"]``.
  You can also specify singly files to be considered as static:
  ``staticpaths=["favicon.ico"]``.

Finally, just save the script as ``build.py`` (or something similar)
and run it with your Python interpreter.

.. code-block:: bash

    $ python build.py
    Building index.html...
    Templates built.
    Watching 'templates' for changes...
    Press Ctrl+C to stop.


Loading data
------------

Some applications render templates based on data sources (e.g. CSVs or
JSON files).

The simplest way to supply data to templates is to pass ``Site.make_site()`` a
mapping from variable names to their values (a "context") as the ``env_globals``
keyword argument.

.. code-block:: python

    if __name__ == "__main__":
        site = Site.make_site(env_globals={
            'greeting':'Hello world!',
        })
        site.render()

Anything added to this dictionary will be available in all templates:

.. code-block:: html

    <!-- templates/index.html -->
    <h1>{{greeting}}</h1>

If the context needs to be different for each template, you can restrict
contexts to certain templates by supplying ``Site.make_site()`` a sequence of
regex-context pairs as the ``contexts`` keyword argument. When rendering a
template, staticjinja will search this sequence for the first regex that matches
the template's name, and use that context to interpolate variables. For example,
the following code block supplies a context to the template named "index.html":

.. code-block:: python

    from staticjinja import Site

    if __name__ == "__main__":
        context = {'knights': ['sir arthur', 'sir lancelot', 'sir galahad']}
        site = Site.make_site(contexts=[('index.html', context)])
        site.render()

.. code-block:: html

    <!-- templates/index.html -->
    <h1>Knights of the Round Table</h1>
    <ul>
    {% for knight in knights %}
        <li>{{ knight }}</li>
    {% endfor %}
    </ul>

If contexts needs to be generated dynamically, you can associate filenames with
functions that return a context ("context generators"). Context generators may
either take no arguments or the current template as its sole argument. For
example, the following code creates a context with the last modification time of
the template file for any templates with an HTML extension:

.. code-block:: python

    import datetime
    import os

    from staticjinja import Site


    def date(template):
        template_mtime = os.path.getmtime(template.filename)
        date = datetime.datetime.fromtimestamp(template_mtime)
        return {'template_date': date.strftime('%d %B %Y')}

    if __name__ == "__main__":
        site = Site.make_site(
            contexts=[('.*.html', date)],
        )
        site.render()

By default, staticjinja uses the context of the first matching regex if multiple
regexes match the name of a template. You can change this so that staticjinja
combines the contexts by passing ``mergecontexts=True`` as an argument to
``Site.make_site()``. Note the order is still important if several matching
regex define the same key, in which case the last regex wins. For example,
given a build script that looks like the following code block, the context of
the ``index.html`` template will be ``{'title': 'MySite - Index', 'date': '05
January 2016'}``.

.. code-block:: python

    import datetime
    import os

    from staticjinja import Site


    def base(template):
        template_mtime = os.path.getmtime(template.filename)
        date = datetime.datetime.fromtimestamp(template_mtime)
        return {
            'template_date': date.strftime('%d %B %Y'),
            'title': 'MySite',
        }


    def index(template):
        return {'title': 'MySite - Index'}

    if __name__ == "__main__":
        site = Site.make_site(
            contexts=[('.*.html', base), ('index.html', index)],
            mergecontexts=True,
        )
        site.render()

Filters
-------

Filters modify variables. staticjinja uses Jinja2 to process templates, so all
the `standard Jinja2 filters`_ are supported. To add your own filters, simply
pass ``filters`` as an argument to ``Site.make_site()``.

.. code-block:: python

    filters = {
        'hello_world': lambda x: 'Hello world!',
        'my_lower': lambda x: x.lower(),
    }

    if __name__ == "__main__":
        site = Site.make_site(filters=filters)
        site.render()

Then you can use them in your templates as you would expect:

.. code-block:: html

    <!-- templates/index.html -->
    {% extends "_base.html" %}
    {% block body %}
    <h1>{{'' | hello_world}}</h1>
    <p>{{'THIS IS AN EXAMPLE WEB PAGE.' | my_lower}}</p>
    {% endblock %}

Compilation rules
-----------------

Sometimes you'll find yourself needing to change how a template is
compiled. For instance, you might want to compile files with a ``.md``
extension as Markdown, without needing to put jinja syntax in your
Markdown files.

To do this, just write a handler by registering a regex for the files
you want to handle, and a compilation function (a "rule").

.. code-block:: python

    import os

    from staticjinja import Site

    # Custom MarkdownExtension
    from extensions import MarkdownExtension


    def get_post_contents(template):
        with open(template.filename) as f:
            return {'post': f.read()}


    # compilation rule
    def render_post(env, template, **kwargs):
        """Render a template as a post."""
        directory, fname = os.path.split(template.name)
        post_title, _ = fname.split(".")
        post_fname = "%s.html" % post_title

        out_dir = os.path.join(env.outpath, directory)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out = os.path.join(out_dir, post_fname)

        post_template = env.get_template("_post.html")
        post_template.stream(**kwargs).dump(out)


    if __name__ == "__main__":
        site = Site.make_site(extensions=[
            MarkdownExtension,
        ], contexts=[
            ('.*.md', get_post_contents),
        ], rules=[
            ('.*.md', render_post),
        ])
        site.render(use_reloader=True)

Note the rule we defined at the bottom. It tells staticjinja to check
if the filename matches the ``.*.md`` regex, and if it does, to
compile the file using ``render_post``.

Now just implement ``templates/_post.html``...

.. code-block:: html

    <!-- templates/_post.html -->
    {% extends "_base.html" %}
    {% block content %}
    <div class="post">
    {% markdown %}
    {{ post }}
    {% endmarkdown %}
    </div>
    {% endblock %}

This would allow you to drop Markdown files into your ``templates``
directory and have them compiled into HTML.

.. note::

     You can grab MarkdownExtension from
     http://silas.sewell.org/blog/2010/05/10/jinja2-markdown-extension/.
