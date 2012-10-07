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
    staticjinja.main(contexts={'index.html': index})
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

### Configuration

If you need further configuration, there are a few options:

*   To change where staticjinja looks for templates, simply pass the name of the directory you wish to use: `staticjinja.main(searchpath='mypath')`
*   To add Jinja extensions, simply pass a list of extensions to main: `staticjinja.main(extensions=[extension1, extension2])`
*   To change what constitutes a template, simply pass a function which given a filename, returns a boolean indicating whether the file should be considered a template. `staticjinja.main(filter_func=my_func)`
*   To disable autoreloading, set autoreload to False. `staticjinja.main(autoreload=False)`
