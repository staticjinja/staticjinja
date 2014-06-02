
Advanced Usage
==============

This document covers some of staticjinja's more advanced features.

Compilation rules
-----------------

Sometimes you'll find yourself needing to change how a template is
compiled. For instance, you might want to integrate Markdown in a way
that doesn't require you putting jinja syntax in the source.

To do this, just write a handler by registering a regex and a
compilation function (a "rule").

.. code-block:: python

    import os

    from staticjinja import make_renderer

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
        renderer = make_renderer(extensions=[
            MarkdownExtension,
        ], contexts=[
            ('.*.md', get_post_contents),
        ], rules=[
            ('.*.md', render_post),
        ])
        renderer.run(use_reloader=True)

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

...and now you can drop markdown files into your ``templates`` directory and they'll be compiled into HTML.

**Note:** You can grab the MarkdownExtension from
 http://silas.sewell.org/blog/2010/05/10/jinja2-markdown-extension/.
