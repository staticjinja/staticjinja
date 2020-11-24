# -*- coding:utf-8 -*-

"""
Simple static page generator.

Uses Jinja2 to compile templates.
"""

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
    return bool(inspect.signature(func).parameters)


class Site(object):
    """The Site object.

    :param environment:
        A :class:`jinja2.Environment`.

    :param searchpath:
        A string representing the name of the directory to search for
        templates.

    :param contexts:
        A list of `regex, context` pairs. Each context is either a dictionary
        or a function that takes either no argument or or the current template
        as its sole argument and returns a dictionary. The regex, if matched
        against a filename, will cause the context to be used.

    :param rules:
        A list of *(regex, function)* pairs. The Site will delegate
        rendering to *function* if *regex* matches the name of a template
        during rendering. *function* must take a :class:`staticjinja.Site`
        object, a :class:`jinja2.Template`, and a context dictionary as
        parameters and render the template. Defaults to ``[]``.

    :param encoding:
        The encoding of templates to use.

    :param logger:
        A logging.Logger object used to log events. Defaults to
        ``logging.getLogger(__name__)``

    :param staticpaths:
        .. deprecated:: 0.3.4

        List of directory names to get static files from (relative to
        searchpath).

    :param mergecontexts:
        A boolean value. If set to ``True``, then all matching regex from the
        contexts list will be merged (in order) to get the final context.
        Otherwise, only the first matching regex is used. Defaults to
        ``False``.
    """

    def __init__(self,
                 environment,
                 searchpath,
                 outpath=".",
                 encoding="utf8",
                 logger=None,
                 contexts=None,
                 rules=None,
                 staticpaths=None,
                 mergecontexts=False,
                 ):
        self.env = environment
        self.searchpath = searchpath
        self.outpath = outpath
        self.encoding = encoding
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            logger.addHandler(logging.StreamHandler())
        self.logger = logger
        self.contexts = contexts or []
        self.rules = rules or []
        if staticpaths:
            warnings.warn("staticpaths are deprecated. Use Make instead.")
        self.staticpaths = staticpaths or []
        self.mergecontexts = mergecontexts

    @classmethod
    def make_site(cls,
                  searchpath="templates",
                  outpath=".",
                  contexts=None,
                  rules=None,
                  encoding="utf8",
                  followlinks=True,
                  extensions=None,
                  staticpaths=None,
                  filters={},
                  env_globals={},
                  env_kwargs=None,
                  mergecontexts=False):
        """Create a :class:`Site <Site>` object.

        :param searchpath:
            A string representing the absolute path to the directory that the
            Site should search to discover templates. Defaults to
            ``'templates'``.

            If a relative path is provided, it will be coerced to an absolute
            path by prepending the directory name of the calling module. For
            example, if you invoke staticjinja using ``python build.py`` in
            directory ``/foo``, then *searchpath* will be ``/foo/templates``.

        :param outpath:
            A string representing the name of the directory that the Site
            should store rendered files in. Defaults to ``'.'``.

        :param contexts:
            A list of *(regex, context)* pairs. The Site will render templates
            whose name match *regex* using *context*. *context* must be either
            a dictionary-like object or a function that takes either no
            arguments or a single :class:`jinja2.Template` as an argument and
            returns a dictionary representing the context. Defaults to ``[]``.

        :param rules:
            A list of *(regex, function)* pairs. The Site will delegate
            rendering to *function* if *regex* matches the name of a template
            during rendering. *function* must take a :class:`staticjinja.Site`
            object, a :class:`jinja2.Template`, and a context dictionary as
            parameters and render the template. Defaults to ``[]``.

        :param encoding:
            A string representing the encoding that the Site should use when
            rendering templates. Defaults to ``'utf8'``.

        :param followlinks:
            A boolean describing whether symlinks in searchpath should be
            followed or not. Defaults to ``True``.

        :param extensions:
            A list of :ref:`Jinja extensions <jinja-extensions>` that the
            :class:`jinja2.Environment` should use. Defaults to ``[]``.

        :param staticpaths:
            .. deprecated:: 0.3.4

            List of directories to get static files from (relative to
            searchpath).  Defaults to ``None``.

        :param filters:
            A dictionary of Jinja2 filters to add to the Environment.  Defaults
            to ``{}``.

        :param env_globals:
            A mapping from variable names that should be available all the time
            to their values. Defaults to ``{}``.

        :param env_kwargs:
            A dictionary that will be passed as keyword arguments to the
            jinja2 Environment. Defaults to ``{}``.

        :param mergecontexts:
            A boolean value. If set to ``True``, then all matching regex from
            the contexts list will be merged (in order) to get the final
            context.  Otherwise, only the first matching regex is used.
            Defaults to ``False``.
        """
        # Coerce search to an absolute path if it is not already
        if not os.path.isabs(searchpath):
            # TODO: Determine if there is a better way to do this
            calling_module = inspect.getmodule(inspect.stack()[-1][0])
            if calling_module is None:
                # Called from the interpreter or similar
                project_path = os.getcwd()
            else:
                # Called from a .py file
                project_path = os.path.realpath(os.path.dirname(
                    calling_module.__file__))
            searchpath = os.path.join(project_path, searchpath)

        if env_kwargs is None:
            env_kwargs = {}
        env_kwargs['loader'] = FileSystemLoader(searchpath=searchpath,
                                                encoding=encoding,
                                                followlinks=followlinks)
        env_kwargs.setdefault('extensions', extensions or [])
        environment = Environment(**env_kwargs)
        environment.filters.update(filters)
        environment.globals.update(env_globals)

        return cls(environment,
                   searchpath=searchpath,
                   outpath=outpath,
                   encoding=encoding,
                   rules=rules,
                   contexts=contexts,
                   staticpaths=staticpaths,
                   mergecontexts=mergecontexts,
                   )

    @property
    def template_names(self):
        return self.env.list_templates(filter_func=self.is_template)

    @property
    def templates(self):
        """Generator for templates."""
        for template_name in self.template_names:
            yield self.get_template(template_name)

    @property
    def static_names(self):
        return self.env.list_templates(filter_func=self.is_static)

    def get_template(self, template_name):
        """Get a :class:`jinja2.Template` from the environment.

        :param template_name: A string representing the name of the template.
        """
        try:
            return self.env.get_template(template_name)
        except UnicodeDecodeError as e:
            raise UnicodeError('Unable to decode %s: %s' % (template_name, e))

    def get_context(self, template):
        """Get the context for a template.

        If no matching value is found, an empty context is returned.
        Otherwise, this returns either the matching value if the value is
        dictionary-like or the dictionary returned by calling it with
        *template* if the value is a function.

        If several matching values are found, the resulting dictionaries will
        be merged before being returned if mergecontexts is True. Otherwise,
        only the first matching value is returned.

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
                    context.update(context_generator)

                if not self.mergecontexts:
                    break
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

    def is_static(self, template_name):
        """Check if a template is a static template. Static template are copied,
        rather than compiled using Jinja2.

        .. deprecated:: 0.3.4

        A template is considered static if it lives in any of the directories
        specified in ``staticpaths``.

        :param template_name: the name of the template to check

        """
        return any(template_name.startswith(path) for path in self.staticpaths)

    def is_partial(self, template_name):
        """Check if a template is a partial template. Partial templates are not
        rendered, but they are used in rendering templates.

        A template is considered a partial if it or any of its parent
        directories are prefixed with an ``'_'``.

        :param template_name: the name of the template to check
        """
        return any((x.startswith("_") for x in template_name.split("/")))

    def is_ignored(self, template_name):
        """Check if a template is an ignored template. Ignored templates are
        neither rendered nor used in rendering templates.

        A template is considered ignored if it or any of its parent directories
        are prefixed with an ``'.'``.

        :param template_name: the name of the template to check
        """
        return any((x.startswith(".") for x in template_name.split("/")))

    def is_template(self, filename):
        """Check if a file is a template.

        A file is a considered a template if it is not partial, ignored, or
        static.

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

        if not os.path.exists(self.outpath):
            os.makedirs(self.outpath)
        self._ensure_dir(template.name)

        try:
            rule = self.get_rule(template.name)
        except ValueError:
            if filepath is None:
                filepath = os.path.join(self.outpath, template.name)
            template.stream(**context).dump(filepath, self.encoding)
        else:
            rule(self, template, **context)

    def render_templates(self, templates):
        """Render a collection of :class:`jinja2.Template` objects.

        :param templates:
            A collection of :class:`jinja2.Template` objects to render.
        """
        for template in templates:
            self.render_template(template)

    def copy_static(self, files):
        for f in files:
            input_location = os.path.join(self.searchpath, f)
            output_location = os.path.join(self.outpath, f)
            self.logger.info("Copying %s to %s." % (f, output_location))
            self._ensure_dir(f)
            shutil.copy2(input_location, output_location)

    def get_dependencies(self, filename):
        """Get a list of files that depends on the file named *filename*.

        :param filename: the name of the file to find dependencies of
        """
        template_name = filename.replace(os.path.sep, "/")

        if self.is_partial(template_name):
            return self.templates
        elif self.is_template(template_name):
            return [self.get_template(filename)]
        elif self.is_static(template_name):
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
        return "%s('%s', '%s')" % (type(self).__name__,
                                   self.searchpath, self.outpath)


class Renderer(Site):
    def __init__(self, *args, **kwargs):
        """
        .. deprecated:: 0.3.1
           Use :meth:`Site.make_site` instead.
        """
        warnings.warn("Renderer was renamed to Site.")
        super(Renderer, Site).__init__(*args, **kwargs)

    def run(self, use_reloader=False):
        return self.render(use_reloader)


def make_site(*args, **kwargs):
    """
    .. deprecated:: 0.3.4
       Use :meth:`Site.make_site` instead.
    """
    warnings.warn("make_site was renamed to Site.make_site.")
    return Site.make_site(*args, **kwargs)


def make_renderer(*args, **kwargs):
    """
    .. deprecated:: 0.3.1
       Use :meth:`Site.make_site` instead.
    """
    warnings.warn("make_renderer was renamed to Site.make_site.")
    return make_site(*args, **kwargs)
