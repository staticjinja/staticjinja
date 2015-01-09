# -*- coding:utf-8 -*-

"""
Simple static page generator.

Uses jinja2 to compile templates.
"""

from __future__ import absolute_import, print_function

import inspect
import logging
import os
import re
import shutil

from jinja2 import Environment, FileSystemLoader


class Renderer(object):
    """The renderer object.

    :param environment:
        A :class:`jinja2.Environment`.

    :param searchpath:
        A string representing the name of the directory to search for
        templates.

    :param contexts:
        A list of regex-function pairs. The function should return a context
        for that template. The regex, if matched against a filename, will cause
        the context to be used.

    :param rules:
        A list of `regex, function` pairs used to ovverride template
        compilation. `regex` must be a regex which if matched against a
        filename will cause `function` to be used instead of the default.
        `function` must be a function which takes a jinja2 Environment, the
        filename, and the context and renders a template.

    :param encoding:
        The encoding of templates to use.

    :param logger:
        A logging.Logger object used to log events.

    :param staticpaths:
        List of directory names to get static files from (relative to
        searchpath).
    """

    def __init__(self,
                 environment,
                 searchpath,
                 outpath,
                 encoding,
                 logger,
                 contexts=None,
                 rules=None,
                 staticpaths=None
                 ):
        self._env = environment
        self.searchpath = searchpath
        self.outpath = outpath
        self.encoding = encoding
        self.logger = logger
        self.contexts = contexts or []
        self.rules = rules or []
        self.staticpaths = staticpaths

    @property
    def template_names(self):
        return self._env.list_templates(filter_func=self.is_template)

    @property
    def templates(self):
        """Generator for templates."""
        for template_name in self.template_names:
            yield self.get_template(template_name)

    @property
    def static_names(self):
        return self._env.list_templates(filter_func=self.is_static)

    def get_template(self, template_name):
        """Get a :class:`jinja2.Template` from the environment.

        :param template_name: A string representing the name of the template.
        """
        return self._env.get_template(template_name)

    def _get_context_generator(self, template_name):
        """Get a context generator for a template.

        Raises a :exc:`ValueError` if no matching context generator can be
        found.

        :param template_name: the name of the template
        """
        for regex, context_generator in self.contexts:
            if re.match(regex, template_name):
                return context_generator
        raise ValueError("no matching context generator")

    def get_context(self, template):
        """Get the context for a template.

        By default, this function will return an empty context.

        If a matching context_generator can be found, it will be passed the
        template and executed. The context generator should return a dictionary
        representing the context.

        :param template: the template to get the context for
        """
        try:
            context_generator = self._get_context_generator(template.name)
        except ValueError:
            return {}
        else:
            try:
                return context_generator(template)
            except TypeError:
                return context_generator()

    def get_rule(self, template_name):
        """Find a matching compilation rule for a function.

        Raises a :exc:`ValueError` if no matching rule can be found.

        :param template_name: the name of the template
        """
        for regex, render_func in self.rules:
            if re.match(regex, template_name):
                return render_func
        raise ValueError("no matching rule")

    def is_static(self, filename):
        """Check if a file is a static file (which should be copied, rather
        than compiled using Jinja2).

        A file is considered static if it lives in any of the directories
        specified in ``staticpaths``.

        :param filename: the name of the file to check

        """
        if self.staticpaths is None:
            # We're not using static file support
            return False

        for path in self.staticpaths:
            if filename.startswith(path + os.path.sep):
                return True
        return False

    def is_partial(self, filename):
        """Check if a file is a partial.

        Partial files are not rendered, but they are used in rendering
        templates.

        A file is considered ignored if it is prefixed with an ``'_'``.

        :param filename: the name of the file to check

        """
        return os.path.basename(filename).startswith('_')

    def is_ignored(self, filename):
        """Check if a file is an ignored file.

        Ignored files are neither rendered nor used in rendering templates.

        A file is considered ignored if it is prefixed with an ``'.'``.

        :param filename: the name of the file to check
        """
        return os.path.basename(filename).startswith('.')

    def is_template(self, filename):
        """Check if a file is a template.

        A file is a considered a template if it is neither a partial nor
        ignored.

        :param filename: the name of the file to check
        """
        if self.is_partial(filename):
            return False

        if self.is_ignored(filename):
            return False

        if self.is_static(filename):
            return False

        return True

    def _ensure_dir(self, template_name):
        """Ensure the output directory for a template exists."""
        head = os.path.dirname(template_name)
        if head:
            file_dirpath = os.path.join(self.outpath, head)
            if not os.path.exists(file_dirpath):
                os.makedirs(file_dirpath)

    def render_template(self, template, context=None, filepath=None):
        """Render a single :class:`jinja2.Template` object.

        If a Rule matching the template is found, the rendering task is
        delegated to the rule.

        :param template:
            A :class:`jinja2.Template` to render.

        :param context:
            Optional. A dictionary representing the context to render
            *template* with. If no context is provided, :meth:`get_context` is
            used to provide a context.

        :param filepath:
            Optional. A file or file-like object to dump the complete template
            stream into. Defaults to to ``os.path.join(self.outpath,
            template.name)``.

        """
        self.logger.info("Rendering %s..." % template.name)

        if context is None:
            context = self.get_context(template)

        try:
            rule = self.get_rule(template.name)
        except ValueError:
            self._ensure_dir(template.name)
            if filepath is None:
                filepath = os.path.join(self.outpath, template.name)
            template.stream(**context).dump(filepath, self.encoding)
        else:
            rule(self, template, **context)

    def render_templates(self, templates, filepath=None):
        """Render a collection of :class:`jinja2.Template` objects.

        :param templates:
            A collection of Templates to render.

        :param filepath:
            Optional. A file or file-like object to dump the complete template
            stream into. Defaults to to ``os.path.join(self.outpath,
            template.name)``.

        """
        for template in templates:
            self.render_template(template, filepath)

    def copy_static(self, files):
        for f in files:
            input_location = os.path.join(self.searchpath, f)
            output_location = os.path.join(self.outpath, f)
            print("Copying %s to %s." % (f, output_location))
            self._ensure_dir(f)
            shutil.copyfile(input_location, output_location)

    def get_dependencies(self, filename):
        """Get a list of files that depends on the file named *filename*.

        :param filename: the name of the file to find dependencies of
        """
        if self.is_partial(filename):
            return self.templates
        elif self.is_template(filename):
            return [self.get_template(filename)]
        elif self.is_static(filename):
            return [filename]
        else:
            return []

    def run(self, use_reloader=False):
        """Run the renderer.

        :param use_reloader: if given, reload templates on modification
        """
        self.render_templates(self.templates)
        self.copy_static(self.static_names)

        if use_reloader:
            self.logger.info("Watching '%s' for changes..." %
                             self.searchpath)
            self.logger.info("Press Ctrl+C to stop.")
            Reloader(self).watch()

    def __repr__(self):
        return "Renderer('%s', '%s')" % (self.searchpath, self.outpath)


class Reloader(object):
    """
    Watches ``renderer.searchpath`` for changes and re-renders any changed
    Templates.

    :param renderer:
        A :class:`Renderer <Renderer>` object.

    """
    def __init__(self, renderer):
        self.renderer = renderer

    @property
    def searchpath(self):
        return self.renderer.searchpath

    def should_handle(self, event_type, filename):
        """Check if an event should be handled.

        An event should be handled if a file in the searchpath was modified.

        :param event_type: a string, representing the type of event

        :param filename: the path to the file that triggered the event.
        """
        print("%s %s" % (event_type, filename))
        return (event_type == "modified"
                and filename.startswith(self.searchpath))

    def event_handler(self, event_type, src_path):
        """Re-render templates if they are modified.

        :param event_type: a string, representing the type of event

        :param src_path: the path to the file that triggered the event.

        """
        filename = os.path.relpath(src_path, self.searchpath)
        if self.should_handle(event_type, src_path):
            if self.renderer.is_static(filename):
                files = self.renderer.get_dependencies(filename)
                self.renderer.copy_static(files)
            else:
                templates = self.renderer.get_dependencies(filename)
                self.renderer.render_templates(templates)

    def watch(self):
        """Watch and reload modified templates."""
        import easywatch
        easywatch.watch(self.searchpath, self.event_handler)


def make_renderer(searchpath="templates",
                  outpath=".",
                  contexts=None,
                  rules=None,
                  encoding="utf8",
                  extensions=None,
                  staticpaths=None):
    """Create a :class:`Renderer <Renderer>` object.

    :param searchpath:
        A string representing the name of the directory that the Renderer
        should search to discover templates. Defaults to ``'templates'``.

    :param outpath:
        A string representing the name of the directory that the Renderer
        should store rendered files in. Defaults to ``'.'``.

    :param contexts:
        A list of *(regex, function)* pairs. The Renderer will invoke
        *function* if *regex* matches the name of a template when rendering.
        *function* must take either no arguments or a single
        :class:`jinja2.Template` as an argument and return a dictionary
        representing the context. Defaults to ``[]``.

    :param rules:
        A list of *(regex, function)* pairs. The Renderer will delegate
        rendering to *function* if *regex* matches the name of a template
        during rendering. *function* must take a :class:`jinja2.Environment`
        object, a filename, and a context as parameters and render the
        template. Defaults to ``[]``.

    :param encoding:
        A string representing the encoding that the Renderer should use when
        rendering templates. Defaults to ``'utf8'``.

    :param extensions:
        A list of :ref:`Jinja extensions <jinja-extensions>` that the
        :class:`jinja2.Environment` should use. Defaults to ``[]``.

    :param staticpaths:
        List of directories to get static files from (relative to searchpath).
        Defaults to ``None``.

    """
    # Coerce search to an absolute path if it is not already
    if not os.path.isabs(searchpath):
        # TODO: Determine if there is a better way to write do this
        calling_module = inspect.getmodule(inspect.stack()[-1][0])
        # Absolute path to project
        project_path = os.path.realpath(os.path.dirname(
            calling_module.__file__))
        searchpath = os.path.join(project_path, searchpath)

    loader = FileSystemLoader(searchpath=searchpath,
                              encoding=encoding)
    environment = Environment(loader=loader, extensions=extensions or [])
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return Renderer(environment,
                    searchpath=searchpath,
                    outpath=outpath,
                    encoding=encoding,
                    logger=logger,
                    rules=rules,
                    contexts=contexts,
                    staticpaths=staticpaths,
                    )
