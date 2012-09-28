staticjinja
===========

Script to easily deploy static sites using the extremely handy [jinja2](http://jinja.pocoo.org/docs/) templating language.

    $ ls *
    README.md        build.py         requirements.txt

    templates:
    _base.html index.html
    $ python build.py
    Building index.html...
    Templates built.
    $ ls
    README.md        index.html       templates
    build.py         requirements.txt
    $ cat index.html
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <title>My Site</title>
            
            
        </head>
        <body>
            
    <h1>Hello world!</h1>
    <p>This is an example web page.</p>

            
            
        </body>
    </html>

Rationale
---------

When deploying a static website that could benefit from factored out data or modular html pages (especially convenient when prototyping) then a templating engine can be of great use. jinja2 is an extremely powerful tool in this regard.

This project takes away the pain of managing the jinja API and lets you focus on just deploying a site.

Requirements
------------

* jinja2
* (optional, for automatic compilation) [watchdog](http://packages.python.org/watchdog/)
* (optional, for haml support) [hamlish-jinja](https://github.com/Pitmairen/hamlish-jinja) for [haml](http://haml.info/) support

`pip install -r requirements.txt`

Setup
-----

Run `python build.py` to compile the templates.

Underneath the hood, this will execute the `main` function in `build.py` and discover every compilable template.

### Context Generators

For templates that require a context, you will need to define a custom "context generator".

A context generator simply generates a dictionary that represents the context for a given template.

For example, the following context generator will generate a context for the template "index.html" which contains a list of strings.

    # build.py
    @context_generator("index.html")
    def example_context_generator():
        """Compile the index with a context."""
        features = [
            'ease of use',
            'auto-discovery',
            'auto-compilation',
            'jinja2',
        ]
        return {'features': features}

You can then use the context in `templates/index.html` as expected.

    # templates/index.html
    {% extends "_base.html" %}
    {% block body %}
    <h1>Hello world!</h1>
    <p>This is an example web page.</p>
    <h3>Features</h3>
    <ul>
    {% for feature in features }}
        <li>{{ feature }}</li>
    {% endfor %}
    </ul>
    {% endblock %}

This example is trivial, but a more interesting context generator might pull data from an API or read data from a CSV.

Automatic Compilation
---------------------

If `watchdog` was installed in the previous step, you can run 'python build.py --watch' to automatically recompile templates whenever a change is made.
