
# staticjinja

Library to easily deploy static sites using the extremely handy [jinja2](http://jinja.pocoo.org/docs/) templating language.

```bash
$ python -m staticjinja
Building index.html...
Templates built.
```


# Rationale

When deploying a static website that could benefit from factored out data or modular html pages (especially convenient when prototyping), a templating engine can be of great use. jinja2 is an extremely powerful tool in this regard.

This project takes away the pain of managing the jinja API and lets you focus on just deploying a site.


# Requirements

* jinja2
* (optional, for automatic compilation) [easywatch](https://github.com/Ceasar/easywatch)


# Installation

`pip install staticjinja`


# Quickstart

If you're just looking to render simple data-less templates, you can get up and running with the following shortcut:

```bash
$ python -m staticjinja
Building index.html...
Templates built.
Watching 'templates' for changes...
Press Ctrl+C to stop.
```

This will recursively search `./templates` for template files and build them to `.`, ignoring any files whose names start with `_` or `.`.

If `easywatch` is installed, this will also monitor the files in `./templates` and recompile them if they change.

## Basic configuration

The command line shortcut is nice, but sometimes your project needs something different than the defaults.

To change things, you can use a build script. A minimal build script looks something like this:

```python
from staticjinja import Renderer


if __name__ == "__main__":
    renderer = Renderer()
    renderer.run(debug=True, use_reloader=True)
```

Then you can change things by passing keyword arguments to `Renderer.__init__`.

*   To change the templates directory, pass in `searchpath="templated_dir_name"` (default is `./templates`).
*   To change the output directory, pass in `outpath="output_dir"` (default is `.`).
*   To add Jinja extensions, pass in `extensions=[extension1, extension2, ...]`.
*   To change which files get rendered, subclass Renderer and override `filter_func`.

You can also change how the script runs by passing in parameters to `Renderer.run`.

*   To enable automatic reloading, pass in `use_reloader=True`.
*   To enable logs, pass in `debug=True`.
 
Finally, just save the script as _build.py_ (or something similar) and run it with your Python interpreter.

```bash
$ python build.py
Building index.html...
Templates built.
Watching 'templates' for changes...
Press Ctrl+C to stop.
```

## Loading Data

Some applications render templates based on data sources (e.g. CSVs or JSON files).

To get data to templates you can set up a mapping between filenames and functions which generate dictionaries containing the data:

```python
from staticjinja import Renderer

def get_knights():
    """Generate knights of the round table."""
    knights = [
        'sir arthur',
        'sir lancelot',
        'sir galahad',
    ]
    return {'knights': knights}

if __name__ == "__main__":
    renderer = Renderer(contexts=[
        ('index.html', get_knights),
    ])
    renderer.run(debug=True, use_reloader=True)
```

You can then use the data in `templates/index.html` as usual.

```html
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
```

## Compilation Rules

Sometimes you'll find yourself needing to change how a template is compiled. For instance, you might want to integrate Markdown in a way that doesn't require you putting jinja syntax in the source.

To do this, just write a handler by registering a regex and a compilation function (a "rule").

```python
import os

from staticjinja import Renderer

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
    renderer = Renderer(extensions=[
        MarkdownExtension,
    ], contexts=[
        ('.*.md', get_post_contents),
    ], rules=[
        ('.*.md', render_post),
    ])
    renderer.run(debug=True, use_reloader=True)
```

Note the rule we defined at the bottom. It tells staticjinja to check if the filename matches the `.*.md` regex, and if it does, to compile the file using `render_post`.

Now just implement `templates/_post.html`...

```html
<!-- templates/_post.html -->
{% extends "_base.html" %}
{% block content %}
<div class="post">
{% markdown %}
{{ post }}
{% endmarkdown %}
</div>
{% endblock %}
```

...and now you can drop markdown files into your `templates` directory and they'll be compiled into HTML.

**Note:** You can grab the MarkdownExtension from [here](http://silas.sewell.org/blog/2010/05/10/jinja2-markdown-extension/).
