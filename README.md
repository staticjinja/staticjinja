

# staticjinja

Library to easily deploy static sites using the extremely handy [jinja2](http://jinja.pocoo.org/docs/) templating language.

```bash
$ python build.py
Building index.html...
Templates built.
```


# Rationale

When deploying a static website that could benefit from factored out data or modular html pages (especially convenient when prototyping), a templating engine can be of great use. jinja2 is an extremely powerful tool in this regard.

This project takes away the pain of managing the jinja API and lets you focus on just deploying a site.


# Requirements

* jinja2
* (optional, for automatic compilation) [watchdog](http://packages.python.org/watchdog/)


# Installation

`pip install staticjinja`


# Getting Started

If you're just looking to render simple data-less templates, you get up and running with the following shortcut

```
python -m staticjinja
```

```
Building index.html...
Templates built.
Watching 'templates' for changes...
Press Ctrl+C to stop.
```

This will search `./templates` recursively for any templates and build them to `.`, ignoring any files that start with `_` or `.`. Furthermore, if you go on to change a template, it will automatically recompile it.

# Basic Configuration

To get a behavior like the default above, you can set up a simple build script in your project.

```python
# build.py
from staticjinja import Renderer


if __name__ == "__main__":
    renderer = Renderer()
    renderer.run(debug=True, use_reloader=True)
```

Then just run `python build.py` to compile the templates.

### Templates and output directories

The Renderer can be configured by adding keyword arguments to `__init__`.

*   To configure the templates directory, set `searchpath="templated_dir_name"` keyword argument (default is `./templates`).
*   To configure the output directory, set `outpath="output_dir"` (default is `.`).
*   To add Jinja extensions, set `extensions=[extension1, extension2, ...]`
*   To configure what constitutes a template, subclass Renderer and override `filter_func` with a function which, given a filename, returns a boolean indicating whether the file should be considered a template.

`renderer.run` can also be configured.

*   To enable automatic reloading, set `use_reloader` to True.
*   To enable logs, set `debug` to True.

# Advanced Configuration

### Contexts

For applications whose templates require data ("contexts"), you will need to define a mapping between filenames and functions which generate the contexts.

For instance:

```python
# build.py
from staticjinja import Renderer

def index():
    knights = [
        'sir arthur',
        'sir lancelot',
        'sir galahad',
    ]
    return {'knights': knights}

if __name__ == "__main__":
    renderer = Renderer(contexts=[
        ('index.html', index),
    ])
    renderer.run(debug=True, use_reloader=True)
```

You can then use the context in `templates/index.html` as usual.

```html
# templates/index.html
{% extends "_base.html" %}
{% block body %}
<h1>Hello world!</h1>
<p>This is an example web page.</p>
<h3>Knights</h3>
<ul>
{% for knight in knights }}
    <li>{{ knight }}</li>
{% endfor %}
</ul>
{% endblock %}
```

This example is trivial, but a more interesting context generator might read data from a JSON or CSV file or pull data from an API.

### Compilation Rules

Sometimes you'll find yourself needing to override how a template is compiled. For instance, you might want to integrate Markdown in a way that doesn't require you putting jinja syntax in the source.

To do this, just write a handler by registering a regex and a compilation function (a "rule").

```python
# build.py
import os

from staticjinja import Renderer

# Custom MarkdownExtension
from extensions import MarkdownExtension


# context generator
def get_contents(template):
    with open(template.filename) as f:
        return {'post': f.read()}


# compilation rule
def build_post(env, template, **kwargs):
    """
    Render a file using "_post.html".
    """
    template = env.get_template("_post.html")
    head, tail = os.path.split(template.name)
    title, _ = tail.split('.')
    if head:
        out = "%s/%s.html" % (head, title)
        if not os.path.exists(head):
            os.makedirs(head)
    else:
    	out = "%s.html" % (title, )
    template.stream(**kwargs).dump(out)


if __name__ == "__main__":
    renderer = Renderer(extensions=[
        MarkdownExtension,
    ], contexts=[
        ('.*.md', get_contents),
    ], rules=[
        ('.*.md', build_post),
    ])
    renderer.run(debug=True, use_reloader=True)
```

Note the rule we defined at the bottom. It tells staticjinja to check if the filename matches the `.*.md` regex, and if it does, to compile the file using `build_post`.

Now we just implement `templates/_post.html`...

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

...and now you can drop markdown files into your `templates` directory and they'll be compiled into valid html.

**Note:** You can grab the MarkdownExtension from [here](http://silas.sewell.org/blog/2010/05/10/jinja2-markdown-extension/).
