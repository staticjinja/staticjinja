#-*- coding:utf-8 -*-

"""
Simple static page generator.
Uses jinja2 to compile templates.
"""

from __future__ import absolute_import

import inspect
import os
import re

from jinja2 import Environment, FileSystemLoader

from . import logs as logging


class Renderer(object):
    """The renderer object.

    :param template_folder: the directory containing the templates. Defaults to
                            ``'templates'``
    :param extensions: list of extensions to add to the Environment
    :param contexts: list of regex-function pairs. the function should return a
                     context for that template. the regex, if matched against
                     a filename, will cause the context to be used.
    :param rules: used to override template compilation. The value of rules
                  should be a list of `regex, function` pairs where `function`
                  takes a jinja2 Environment, the filename, and the context and
                  renders the template, and `regex` is a regex that if matched
                  against a filename will cause `function` to be used instead
                  of the default.
    :param encoding: the encoding of templates to use. Defaults to 'utf8'
    """
    debug_log_format = None

    def __init__(self,
                 template_folder="templates",
                 outpath=".",
                 extensions=None,
                 contexts=None,
                 rules=None,
                 encoding="utf8"):

        if os.path.isabs(template_folder):
            template_path = template_folder
        else:
            # TODO: Remove this
            calling_module = inspect.getmodule(inspect.stack()[-1][0])
            # Absolute path to project
            project_path = os.path.realpath(os.path.dirname(
                calling_module.__file__))
            # Absolute path to templates
            template_path = os.path.join(project_path, template_folder)

        self.template_folder = template_path
        self.outpath = outpath
        self.extensions = extensions or []
        self.contexts = contexts or []
        self.rules = rules or []
        self.encoding = encoding

        loader = FileSystemLoader(searchpath=template_folder,
                                  encoding=encoding)
        self._env = Environment(loader=loader, extensions=self.extensions)

        self.logger_name = __name__
        self.logger = logging.create_logger(self)

        self.debug = False

    @property
    def template_names(self):
        return self._env.list_templates(filter_func=self.filter_func)

    def get_template(self, template_name):
        """Get a Template object from the environment.

        :param template_name: the name of the template
        """
        return self._env.get_template(template_name)

    def get_context(self, template_name):
        """Get the context for a template.

        By default, this function will return an empty context.

        If a matching context_generator can be found, it will be passed the
        template and executed. The context generator should return a dictionary
        representing the context.

        :param template_name: the name of the template
        """
        for regex, context_generator in self.contexts:
            if re.match(regex, template_name):
                try:
                    return context_generator(self.get_template(template_name))
                except TypeError:
                    return context_generator()
        return {}

    def filter_func(self, filename):
        """Check if the file should be rendered.

        Hidden files will not be rendered.

        Files prefixed with an underscore are assumed to be partials and will
        not be rendered.

        :param filename: the name of the file to check
        """
        _, tail = os.path.split(filename)
        return not (tail.startswith('_') or tail.startswith("."))

    def _ensure_dir(self, template_name):
        """Ensure the output directory for a template exists."""
        head, tail = os.path.split(template_name)
        if head:
            file_dirpath = os.path.join(self.outpath, head)
            if not os.path.exists(file_dirpath):
                os.makedirs(file_dirpath)

    def render_template(self, template_name):
        """Render a template.

        If a matching Rule can be found, rendering will be delegated to the
        rule.

        :param template_name: the name of the template
        """
        self.logger.info("Rendering %s..." % template_name)

        template = self.get_template(template_name)
        context = self.get_context(template_name)
        for regex, render_func in self.rules:
            if re.match(regex, template.name):
                render_func(self, template, **context)
                break
        else:
            self._ensure_dir(template.name)
            fp = os.path.join(self.outpath, template.name)
            template.stream(**context).dump(fp, self.encoding)

    def render_templates(self):
        """Render each of the templates."""
        for template_name in self.template_names:
            self.render_template(template_name)

    def _watch(self):
        """Watch and reload templates."""
        import easywatch

        self.logger.info("Watching '%s' for changes..." %
                          self.template_folder)
        self.logger.info("Press Ctrl+C to stop.")

        def handler(event_type, src_path):
            template_name = os.path.relpath(src_path, self.template_folder)
            if event_type == "modified":
                if src_path.startswith(self.template_folder):
                    self.render_template(template_name)
        easywatch.watch(self.template_folder, handler)

    def run(self, debug=False, use_reloader=False):
        """Run the renderer.

        :param debug: if given, then display logs
        :param reload: if given, reload templates on modification
        """
        if debug:
            self.debug = True

        self.render_templates()

        if use_reloader:
            self._watch()


def main(*args, **kwargs):
    if 'autoreload' in kwargs:
    	autoreload = True
    	del kwargs['autoreload']
    else:
    	autoreload = False
    if 'filter_func' in kwargs:
    	filter_func = kwargs['filter_func']
    	del kwargs['filter_func']
    else:
    	filter_func = None
    renderer = Renderer(*args, **kwargs)
    if filter_func:
        renderer.filter_func = filter_func
    if autoreload:
        renderer.run(debug=True, use_reloader=True)
