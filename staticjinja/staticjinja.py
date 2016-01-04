# -*- coding:utf-8 -*-

"""
Simple static page generator.

Uses Jinja2 to compile templates.
"""

from __future__ import absolute_import, print_function

import inspect
import logging
import os
import re
import shutil
import warnings

from jinja2 import Environment, FileSystemLoader

from .reloader import Reloader


def _has_argument(func):
    """Test whether a function expects an argument.

    :param func:
    The function to be tested for existence of an argument.
    """
    if hasattr(inspect, 'signature'):
        # New way in python 3.3
        sig = inspect.signature(func)
        return bool(sig.parameters)
    else:
        # Old way
        return bool(inspect.getargspec(func).args)


class Site(object):
    """The Site object.

    :param environment:
        A :class:`jinja2.Environment`.

    :param searchpath:
        A string representing the name of the directory to search for
        templates.

    :param contexts:
        A list of `regex, context` pairs. Each context is either a dictionary
        or a function returning a dictionary without argument or with the
        current template as an argument. The regex, if matched against a
        filename, will cause the context to be used.

    :param rules:
        A list of `regex, function` pairs used to ovverride template
        compilation. `regex` must be a regex which if matched against a
        filename will cause `function` to be used instead of the default.
        `function` must be a function which takes a Jinja2 Environment, the
        filename, and the context and renders a template.

    :param encoding:
        The encoding of templates to use.

    :param logger:
        A logging.Logger object used to log events.

    :param staticpaths:
        List of directory names to get static files from (relative to
        searchpath).

    :param mergecontexts:
        A `bool` object. If True all matching regex from the
        contexts list will be merged (in order) to get the final context.
        Otherwise, only the first matching regex is used.
        Defaults to `False`.
    """

    def __init__(self,
                 environment,
                 searchpath,
                 outpath,
                 encoding,
                 logger,
                 contexts=[],
                 rules=None,
                 staticpaths=None,
                 mergecontexts=False
                 ):
        self._env = environment
        self.searchpath = searchpath
        self.outpath = outpath
        self.encoding = encoding
        self.logger = logger
        self.contexts = contexts
        self.rules = rules or []
        self.staticpaths = staticpaths
        self.mergecontexts = mergecontexts

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

    def get_context(self, template):
        """Get the context for a template.

        By default, this function will return an empty context.

        If a matching context_generator can be found and is a function
        it will be executed after being passed the template if it expects an
        argument. If it is not a function then it will be assumed to act like
        a dictionary object.

        If several context_generator can be found, their resulting dictionary
        will be merged if mergecontexts is True or only the first one will be
        used otherwise.

        :param template: the template to get the context for
        """

        context = {}
        for regex, context_generator in self.contexts:
            if re.match(regex, template.name):
                if inspect.isfunction(context_generator):
                    if _has_argument(context_generator):
                        context.update(context_generator(template))
                    else:
                        context.update(context_generator())
                else:
                    # Here we expect context_generator to be already a dict
                    # (or similar)
                    context.update(context_generator)

                if not self.mergecontexts:
                    return context

        return context

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
            if filename.startswith(path):
                return True
        return False

    def is_partial(self, filename):
        """Check if a file is a partial.

        Partial files are not rendered, but they are used in rendering
        templates.

        A file is considered a partial if it or any of its parent directories
        are prefixed with an ``'_'``.

        :param filename: the name of the file to check
        """
        return any((x.startswith("_") for x in filename.split(os.path.sep)))

    def is_ignored(self, filename):
        """Check if a file is an ignored file.

        Ignored files are neither rendered nor used in rendering templates.

        A file is considered ignored if it or any of its parent directories
        are prefixed with an ``'.'``.

        :param filename: the name of the file to check
        """
        return any((x.startswith(".") for x in filename.split(os.path.sep)))

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
            shutil.copy2(input_location, output_location)

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

    def render(self, use_reloader=False):
        """Generate the site.

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
        return "Site('%s', '%s')" % (self.searchpath, self.outpath)


class Renderer(Site):
    def __init__(self, *args, **kwargs):
        warnings.warn("Renderer was renamed to Site.")
        super(Renderer, Site).__init__(*args, **kwargs)

    def run(self, use_reloader=False):
        return self.render(use_reloader)


def make_site(searchpath="templates",
              outpath=".",
              contexts=[],
              rules=None,
              encoding="utf8",
              extensions=None,
              staticpaths=None,
              filters=None,
              env_kwargs=None,
              mergecontexts=False):
    """Create a :class:`Site <Site>` object.

    :param searchpath:
        A string representing the absolute path to the directory that the Site
        should search to discover templates. Defaults to ``'templates'``.

        If a relative path is provided, it will be coerced to an absolute path
        by prepending the directory name of the calling module. For example, if
        you invoke staticjinja using ``python build.py`` in directory ``/foo``,
        then *searchpath* will be ``/foo/templates``.

    :param outpath:
        A string representing the name of the directory that the Site
        should store rendered files in. Defaults to ``'.'``.

    :param contexts:
        A list of *(regex, context)* pairs. The Site will use *context* if
        *regex* matches the name of a template when rendering.  *context* must
        be either acts as a dictionary or be a function which must take either
        no arguments or a single :class:`jinja2.Template` as an argument and
        return a dictionary representing the context. Defaults to ``[]``.

    :param rules:
        A list of *(regex, function)* pairs. The Site will delegate
        rendering to *function* if *regex* matches the name of a template
        during rendering. *function* must take a :class:`jinja2.Environment`
        object, a filename, and a context as parameters and render the
        template. Defaults to ``[]``.

    :param encoding:
        A string representing the encoding that the Site should use when
        rendering templates. Defaults to ``'utf8'``.

    :param extensions:
        A list of :ref:`Jinja extensions <jinja-extensions>` that the
        :class:`jinja2.Environment` should use. Defaults to ``[]``.

    :param staticpaths:
        List of directories to get static files from (relative to searchpath).
        Defaults to ``None``.

    :param filters:
        A dictionary of Jinja2 filters to add to the Environment.
        Defaults to ``{}``.

    :param env_kwargs:
        A dictionary that will be passed as keyword arguments to the
        jinja2 Environment. Defaults to ``{}``.

    :param mergecontexts:
        A `bool` object. If True all matching regex from the
        contexts list will be merged (in order) to get the final context.
        Otherwise, only the first matching regex is used.
        Defaults to ``False``.

    """
    # Coerce search to an absolute path if it is not already
    if not os.path.isabs(searchpath):
        # TODO: Determine if there is a better way to write do this
        calling_module = inspect.getmodule(inspect.stack()[-1][0])
        # Absolute path to project
        project_path = os.path.realpath(os.path.dirname(
            calling_module.__file__))
        searchpath = os.path.join(project_path, searchpath)

    if env_kwargs is None:
        env_kwargs = {}
    env_kwargs['loader'] = FileSystemLoader(searchpath=searchpath,
                                            encoding=encoding)
    env_kwargs.setdefault('extensions', extensions or [])
    environment = Environment(**env_kwargs)
    if filters:
        for k, v in filters.items():
            environment.filters[k] = v

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return Site(environment,
                searchpath=searchpath,
                outpath=outpath,
                encoding=encoding,
                logger=logger,
                rules=rules,
                contexts=contexts,
                staticpaths=staticpaths,
                mergecontexts=mergecontexts,
                )


def make_renderer(*args, **kwargs):
    warnings.warn("make_renderer was renamed to make_site.")
    return make_site(*args, **kwargs)
