
.. _standard Jinja2 filters: http://jinja.pocoo.org/docs/dev/templates/#builtin-filters

Advanced Usage
==============

This document covers some of staticjinja's more advanced features.

.. _custom-build-scripts:

Using Custom Build Scripts
--------------------------

The command line shortcut is convenient, but sometimes your project
needs something different than the defaults. To change them, you can
use a build script.

A minimal build script looks something like this:

.. code-block:: python

    from staticjinja import make_site


    if __name__ == "__main__":
        site = make_site()
        # enable automatic reloading
        site.render(use_reloader=True)

To change behavior, pass the appropriate keyword arguments to
``make_site``.

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

To get data to templates you can set up a mapping between filenames
and functions which generate dictionaries containing the data:

.. code-block:: python

    from staticjinja import make_site

    def get_knights():
        """Generate knights of the round table."""
        knights = [
            'sir arthur',
            'sir lancelot',
            'sir galahad',
        ]
        return {'knights': knights}

    if __name__ == "__main__":
        site = make_site(contexts=[
            ('index.html', get_knights),
        ])
        site.render(use_reloader=True)

You can then use the data in ``templates/index.html`` as you'd expect.

.. code-block:: html

    <!-- templates/index.html -->
    {% extends "_base.html" %}
    {% block body %}
    <h1>Hello world!</h1>
    <p>This is an example web page.</p>
    <h3>Knights of the Round Table</h3>
    <ul>
    {% for knight in knights %}
        <li>{{ knight }}</li>
    {% endfor %}
    </ul>
    {% endblock %}

Filters
-------

Filters modify variables. staticjinja uses Jinja2 to process templates, so all
the `standard Jinja2 filters`_ are supported. To add your own filters, simply
pass ``filters`` as an argument to ``make_site()``.

.. code-block:: python

    filters = {
        'hello_world': lambda x: 'Hello world!',
        'my_lower': lambda x: x.lower(),
    }

    if __name__ == "__main__":
        site = staticjinja.make_site(filters=filters)
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

    from staticjinja import make_site

    # Custom MarkdownExtension
    from extensions import MarkdownExtension


    def get_post_contents(template):
        with open(template.filename) as f:
            return {'post': f.read()}


    # compilation rule
    def render_post(env, template, **kwargs):
        """Render a template as a post."""
        post_template = env.get_template("_post.html")
        head, tail = os.path.split(post_template.name)
        post_title, _ = tail.split('.')
        if head:
            out = "%s/%s.html" % (head, post_title)
            if not os.path.exists(head):
                os.makedirs(head)
        else:
            out = "%s.html" % (post_title, )
        post_template.stream(**kwargs).dump(out)


    if __name__ == "__main__":
        site = make_site(extensions=[
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
