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
    :param searchpath: the name of the directory to search for templates.
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

    @property
    def templates(self):
        """Generator for templates."""
        for template_name in self.template_names:
            yield self.get_template(template_name)

    def get_template(self, template_name):
        """Get a Template object from the environment.

        :param template_name: the name of the template
        """
        return self._env.get_template(template_name)

    def _get_context_generator(self, template_name):
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
        
        Raises a ValueError if no matching rule can be found.
        
        :param template_name: the name of the template
        """
        for regex, render_func in self.rules:
            if re.match(regex, template_name):
                return render_func
        raise ValueError("no matching rule")

    def is_partial(self, filename):
        """Check if a file is a partial.

        Partial files are not rendered, but they are used in rendering templates.

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
        return not self.is_partial(filename) and not self.is_ignored(filename)

    def _ensure_dir(self, template_name):
        """Ensure the output directory for a template exists."""
        head = os.path.dirname(template_name)
        if head:
            file_dirpath = os.path.join(self.outpath, head)
            if not os.path.exists(file_dirpath):
                os.makedirs(file_dirpath)

    def render_template(self, template, context=None):
        """Render a template.

        If a Rule matching the template is found, the rendering task is
        delegated to the rule.

        :param template: a template to render
        :param context: optional. A context to render the template with. If no
                        context is provided, `get_context` is used to provide a
                        context.
        """
        self.logger.info("Rendering %s..." % template.name)

        if context is None:
            context = self.get_context(template)

        try:
            rule = self.get_rule(template.name)
        except ValueError:
            self._ensure_dir(template.name)
            fp = os.path.join(self.outpath, template.name)
            template.stream(**context).dump(fp, self.encoding)
        else:
            rule(self, template, **context)

    def render_templates(self, templates):
        """Render a collection of templates.
        
        :param templates: a collection of Templates to render
        """
        for template in templates:
            self.render_template(template)

    def get_dependencies(self, filename):
        """Get every file that depends on a file.
        
        :param filename: the name of the file to find dependencies of
        """
        if self.is_partial(filename):
            return self.templates
        elif self.is_template(filename):
            return [self.get_template(filename)]
        else:
            return []

    def run(self, use_reloader=False):
        """Run the renderer.

        :param use_reloader: if given, reload templates on modification
        """
        self.render_templates(self.templates)

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

    :param renderer: a :class:`Renderer <Renderer>` to re-render templates.

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
        print event_type, filename
        return (event_type == "modified"
                and filename.startswith(self.searchpath))

    def event_handler(self, event_type, src_path):
        """Re-render templates if they are modified.
        
        :param event_type: a string, representing the type of event

        :param src_path: the path to the file that triggered the event.

        """
        filename = os.path.relpath(src_path, self.searchpath)
        if self.should_handle(event_type, src_path):
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
                 ):
    """Get a Renderer object.

    :param searchpath: the name of the directory to search for templates.
                       Defaults to ``'templates'``.

    :param outpath: the name of the directory to store the rendered files in.
                    Defaults to ``'.'``.

    :param contexts: list of *(regex, function)* pairs. When rendering, if a
                     template's name matches *regex*, *function* will be
                     invoked and expected to provide a context. *function*
                     should optionally take a Template as a parameter and
                     return a dictionary context when invoked. Defaults to
                     ``[]``.

    :param rules: list of *(regex, function)* pairs. When rendering, if a
                  template's name matches *regex*, rendering will delegate to
                  *function*. *function* should take a jinja2 Environment, a
                  filename, and a context and render the template. Defaults to
                  ``[]``.

    :param encoding: the encoding of templates to use. Defaults to ``'utf8'``.

    :param extensions: list of extensions to add to the Environment. Defaults to
                       ``[]``.

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
