#-*- coding:utf-8 -*-

"""
Simple static page generator.

Uses jinja2 to compile templates.
"""

from __future__ import absolute_import

import inspect
import logging
import os
import re

from jinja2 import Environment, FileSystemLoader


class Renderer(object):
    """The renderer object.

    :param environment: a jinja2 environment
    :param searchpath: the directory containing the templates
    :param contexts: list of regex-function pairs. the function should return a
                     context for that template. the regex, if matched against
                     a filename, will cause the context to be used.
    :param rules: used to override template compilation. The value of rules
                  should be a list of `regex, function` pairs where `function`
                  takes a jinja2 Environment, the filename, and the context and
                  renders the template, and `regex` is a regex that if matched
                  against a filename will cause `function` to be used instead
                  of the default.
    :param encoding: the encoding of templates to use
    :param logger: a logging.Logger object to log events
    """

    def __init__(self,
                 environment,
                 searchpath,
                 outpath,
                 encoding,
                 logger,
                 contexts=None,
                 rules=None,
                 ):
        self._env = environment
        self.searchpath = searchpath
        self.outpath = outpath
        self.encoding = encoding
        self.logger = logger
        self.contexts = contexts or []
        self.rules = rules or []

    @property
    def template_names(self):
        return self._env.list_templates(filter_func=self.is_template)

    def get_template(self, template_name):
        """Get a Template object from the environment.

        :param template_name: the name of the template
        """
        return self._env.get_template(template_name)

    def get_context_generator(self, template_name):
        """Get a context generator for a template.
        
        Raises a ValueError if no matching context generator can be found.
        
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
            context_generator = self.get_context_generator(template.name)
        except ValueError:
            return {}
        else:
            try:
                return context_generator(template)
            except TypeError:
                return context_generator()

    def get_rule(self, template_name):
        """Find a matching compilation rule for a function.
        
        Raises a ValueError if no matching rule can be found.
        
        :param template_name: the name of the template
        """
        for regex, render_func in self.rules:
            if re.match(regex, template_name):
                return render_func
        raise ValueError("no matching rule")

    def is_partial(self, filename):
        """Check if a file is a Partial.

        A Partial is not rendered but may be used by Templates.

        By default, any file prefixed with an `_` is considered a Partial.

        :param filename: the name of the file to check
        """
        _, tail = os.path.split(filename)
        return tail.startswith('_')

    def is_ignored(self, filename):
        """Check if a file is an ignored file.

        An ignored file is neither rendered nor affects rendering.

        :param filename: the name of the file to check
        """
        _, tail = os.path.split(filename)
        return tail.startswith(".")

    def is_template(self, filename):
        """Check if a file is a Template.

        :param filename: the name of the file to check
        """
        return not self.is_partial(filename) and not self.is_ignored(filename)

    def _ensure_dir(self, template_name):
        """Ensure the output directory for a template exists."""
        head, _ = os.path.split(template_name)
        if head:
            file_dirpath = os.path.join(self.outpath, head)
            if not os.path.exists(file_dirpath):
                os.makedirs(file_dirpath)

    def render_template(self, template, context):
        """Render a template.

        If a Rule matching the template is found, the rendering task is
        delegated to the rule.

        :param template: a template to render
        :param context: a context to render the template with
        """
        self.logger.info("Rendering %s..." % template.name)

        try:
            rule = self.get_rule(template.name)
        except ValueError:
            self._ensure_dir(template.name)
            fp = os.path.join(self.outpath, template.name)
            template.stream(**context).dump(fp, self.encoding)
        else:
            rule(self, template, **context)

    def render_templates(self):
        """Render each of the templates."""
        for template_name in self.template_names:
            template = self.get_template(template_name)
            context = self.get_context(template)
            self.render_template(template, context)

    def _watch(self):
        """Watch and reload templates."""
        import easywatch

        self.logger.info("Watching '%s' for changes..." %
                          self.searchpath)
        self.logger.info("Press Ctrl+C to stop.")

        def handler(event_type, src_path):
            filename = os.path.relpath(src_path, self.searchpath)
            if event_type == "modified":
                if src_path.startswith(self.searchpath):
                    if self.is_partial(filename):
                        self.render_templates()
                    elif self.is_template(filename):
                        template = self.get_template(filename)
                        context = self.get_context(template)
                        self.render_template(filename)
        easywatch.watch(self.searchpath, handler)

    def run(self, use_reloader=False):
        """Run the renderer.

        :param use_reloader: if given, reload templates on modification
        """
        self.render_templates()

        if use_reloader:
            self._watch()


def make_renderer(searchpath="templates",
                 outpath=".",
                 contexts=None,
                 rules=None,
                 encoding="utf8",
                 extensions=None,
                 ):
    """Get a Renderer object.

    :param searchpath: the name of the directory to search for templates.
    
                       Defaults to 'templates'.
    :param outpath: the name of the directory to store the rendered files in

                    Defaults to `.`.
    :param contexts: list of `(regex, function)` pairs.
    
                     If `regex` matches a template's name, `function` will
                     be invoked and expected to provide a context.

                     `function` should optionally take a Template as a
                     parameter and return a dictionary context when invoked.
    :param rules: list of `(regex, function)` pairs.

                  If `regex` matches a template's name, rendering will
                  delegate to `function`.
    
                  `function` should take a jinja2 Environment, a filename, and
                  a context and render the template.
    :param encoding: the encoding of templates to use. Defaults to 'utf8'
    :param extensions: list of extensions to add to the Environment
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
                    )
