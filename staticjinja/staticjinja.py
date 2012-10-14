"""
Simple static page generator.
Uses jinja2 to compile templates.
Templates should live inside `./templates` and will be compiled in '.'.
"""
import inspect
import os
import re

import easywatch
from jinja2 import Environment, FileSystemLoader


def build_template(env, template_name, **kwargs):
    """Compile a template.
    *   env should be a Jinja environment variable indicating where to find the
        templates.
    *   template_name should be the name of the template as it appears inside
        of `./templates`.
    *   kwargs should be a series of key-value pairs. These items will be
        passed to the template to be used as needed.
    """
    template = env.get_template(template_name)
    head, tail = os.path.split(template_name)
    if head and not os.path.exists(head):
        os.makedirs(head)
    template.stream(**kwargs).dump(tail)


def should_render(filename):
    """Check if the file should be rendered.
    -   Hidden files will not be rendered.
    -   Files prefixed with an underscore are assumed to be partials and will
        not be rendered.
    """
    return not (filename.startswith('_') or filename.startswith("."))


def render_templates(env, contexts=None, filter_func=None, rules=None):
    """Render each template inside of `env`.
    -   env should be a Jinja environment object.
    -   contexts should be a list of regex-function pairs where the
        function should return a context for that template and the regex,
        if matched against a filename, will cause the context to be used.
    -   filter_func should be a function that takes a filename and returns
        a boolean indicating whether or not a template should be rendered.
    -   rules are used to override template compilation. The value of rules
        should be a list of `regex`-`function` pairs where `function` takes
        a jinja2 Environment, the filename, and the context and builds the
        template, and `regex` is a regex that if matched against a filename
        will cause `function` to be used instead of the default.
    """
    if contexts is None:
        contexts = []
    if filter_func is None:
        filter_func = should_render
    if rules is None:
        rules = []

    for template_name in env.list_templates(filter_func=filter_func):
        print "Building %s..." % template_name

        filename = env.get_template(template_name).filename

        # get the context
        for regex, context_generator in contexts:
            if re.match(regex, template_name):
                try:
                    context = context_generator(filename)
                except TypeError:
                    context = context_generator()
                break
        else:
            context = {}

        # build the template
        for regex, func in rules:
            if re.match(regex, template_name):
                func(env, filename, **context)
                break
        else:
            build_template(env, template_name, **context)


def main(searchpath="templates", filter_func=None, contexts=None,
         extensions=None, rules=None, autoreload=True):
    """
    Render each of the templates and then recompile on any changes.
    -   searchpath should be the directory that contains the template.
        Defaults to "templates"
    -   filter_func should be a function that takes a filename and returns
        a boolean indicating whether or not a template should be rendered.
        Defaults to ignore any files with '.' or '_' prefixes.
    -   contexts should be a map of template names to functions where each
        function should return a context for that template.
    -   extensions should be any extensions to add to the Environment.
    -   autoreload should be a boolean indicating whether or not to
        automatically recompile templates. Defaults to true.
    """
    if extensions is None:
        extensions = []

    # Get calling module
    mod = inspect.getmodule(inspect.stack()[1][0])
    # Absolute path to project
    project_path = os.path.realpath(os.path.dirname(mod.__file__))
    # Absolute path to templates
    template_path = os.path.join(project_path, searchpath)

    loader = FileSystemLoader(searchpath=searchpath)
    env = Environment(loader=loader,
                      extensions=extensions)

    def build_all():
        render_templates(env, contexts, filter_func=filter_func, rules=rules)
        print "Templates built."
    build_all()

    if autoreload:
        print "Watching '%s' for changes..." % searchpath
        print "Press Ctrl+C to stop."

        def handler(event_type, src_path):
            if event_type == "modified":
                if src_path.startswith(template_path):
                    build_all()
        easywatch.watch("./" + searchpath, handler)

        print "Process killed"
    return 0
