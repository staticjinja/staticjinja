staticjinja
===========

Library to easily deploy static sites using the extremely handy [jinja2](http://jinja.pocoo.org/docs/) templating language.

```bash
$ python build.py
Building index.html...
Templates built.
```

Rationale
---------

When deploying a static website that could benefit from factored out data or modular html pages (especially convenient when prototyping), a templating engine can be of great use. jinja2 is an extremely powerful tool in this regard.

This project takes away the pain of managing the jinja API and lets you focus on just deploying a site.

Requirements
------------

* jinja2
* (optional, for automatic compilation) [watchdog](http://packages.python.org/watchdog/)

Installation
------------

`pip install staticjinja`

Getting Started
---------------

If you don't need anything special, you get up and running by just setting up a simple build script.

```python
# build.py
import staticjinja

if __name__ == "__main__":
    staticjinja.main()
```

Then run `python build.py` to compile the templates.

Left to the defaults, this will search `./templates` recursively for any templates and build them to `.`, ignoring any files that start with `_` or `.`. Furthermore, if you change a template, it will automatically recompile the project.


### Contexts

For applications whose templates require contexts, you will need to define a mapping between filenames and functions which generate the contexts.

For instance:

```python
# build.py
import staticjinja

def index():
    knights = [
        'sir arthur',
        'sir lancelot',
        'sir galahad',
    ]
    return {'knights': knights}

if __name__ == "__main__":
    staticjinja.main(contexts=[
        ('index.html', index),
    ])
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

This example is trivial, but a more interesting context generator might read data from a CSV or pull data from an API.

### Compilation Rules

Sometimes you'll find yourself needing to override how a template is actualy compiled. For instance, you might want to integrate Markdown in a way that doesn't require you putting
jinja syntax in the source.

To do this, we can write a handler by registering a regex and a compilation function (a "rule").

```python
# build.py
import os

import staticjinja

# Custom MarkdownExtension
from extensions import MarkdownExtension


def get_contents(filename):
    with open(filename) as f:
        return {'post': f.read()}


def build_post(env, filename, **kwargs):
    """
    Render a file using "_post.html".
    """
    template = env.get_template("_post.html")
    _, tail = os.path.split(filename)
    title, _ = tail.split('.')
    template.stream(**kwargs).dump(title + ".html")


if __name__ == "__main__":
    staticjinja.main(extensions=[
        MarkdownExtension,
    ], contexts=[
        ('.*.md', get_contents),
    ], rules=[
        ('.*.md', build_post),
    ])
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

### Configuration

If you need further configuration, there are a few options:

*   To change where staticjinja looks for templates, simply pass the name of the directory you wish to use: `staticjinja.main(searchpath='mypath')`
*   To add Jinja extensions, simply pass a list of extensions to main: `staticjinja.main(extensions=[extension1, extension2])`
*   To change what constitutes a template, simply pass a function which given a filename, returns a boolean indicating whether the file should be considered a template. `staticjinja.main(filter_func=my_func)`
*   To disable autoreloading, set autoreload to False. `staticjinja.main(autoreload=False)`
