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

If you're just looking to render simple data-less templates, you get up and running by just setting up a simple build script in your project.

```python
# build.py
import staticjinja


if __name__ == "__main__":
    staticjinja.main()
```

Then just run `python build.py` to compile the templates.

```
Building index.html...
Templates built.
Watching 'templates' for changes...
Press Ctrl+C to stop.
```

Left to the defaults, this will search `./templates` recursively for any templates and build them to `.`, ignoring any files that start with `_` or `.`. Furthermore, if you go on to change a template, it will automatically recompile it.

# Basic Configuration

### Templates and output directories

*   To set a different templates directory, use the `searchpath="templated_dir_name"` keyword argument to `staticjinja.main()` (default is `./templates`).
*   To set a different output directory, use the `outpath="output_dir"` (default is `.`).
*   To add Jinja extensions, simply pass a list of extensions to main: `staticjinja.main(extensions=[extension1, extension2])`
*   To change what constitutes a template, simply pass a function which given a filename, returns a boolean indicating whether the file should be considered a template. `staticjinja.main(filter_func=my_func)`
*   To disable autoreloading, set autoreload to False. `staticjinja.main(autoreload=False)`

# Advanced Configuration

### Contexts

For applications whose templates require data ("contexts"), you will need to define a mapping between filenames and functions which generate the contexts.

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

This example is trivial, but a more interesting context generator might read data from a JSON or CSV file or pull data from an API.

### Compilation Rules

Sometimes you'll find yourself needing to override how a template is compiled. For instance, you might want to integrate Markdown in a way that doesn't require you putting jinja syntax in the source.

To do this, just write a handler by registering a regex and a compilation function (a "rule").

```python
# build.py
import os

import staticjinja

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
