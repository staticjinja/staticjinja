# -*- coding:utf-8 -*-

"""
Builder object for staticjinja.

This object is responsible for copying static files, compiling templates or
appyling custom rules after getting the relevant context.
"""

from __future__ import absolute_import

import inspect
import shutil
import re
import os

from staticjinja.sources import TEMPLATE_FLAVOR, STATIC_FLAVOR


def _has_argument(func):
    """Test whether a function expects an argument.

    :param func:
        The function to be tested for existence of an argument.
    """
    if hasattr(inspect, 'signature'):  # pragma: no cover
        # New way in python 3.3
        sig = inspect.signature(func)
        return bool(sig.parameters)
    else:  # pragma: no cover
        # Old way
        return bool(inspect.getargspec(func).args)


class Builder(object):
    """The Builder object.

    :param environment:
        A :class:`jinja2.Environment`.

    :param sources:
        A :class:`SourceManager` tracking all sources of the website.

    :param searchpath:
        A string representing the name of the directory to search for
        templates.

    :param outpath:
        A string representing the name of the directory that the Site
        should store rendered files in. Defaults to ``'.'``.

    :param encoding:
        A string representing the encoding that the Site should use when
        rendering templates. Defaults to ``'utf8'``.

    :param logger:
        A logging.Logger object used to log events.

    :param contexts:
        A list of `regex, context` pairs. Each context is either a dictionary
        or a function that takes either no argument or or the current template
        as its sole argument and returns a dictionary. The regex, if matched
        against a filename, will cause the context to be used.

    :param rules:
        A list of `regex, function` pairs used to override template
        compilation. `regex` must be a regex which if matched against a
        filename will cause `function` to be used instead of the default.
        `function` must be a function which takes a Jinja2 Environment, the
        filename, and the context and renders a template.

    :param mergecontexts:
        A boolean value. If set to ``True``, then all matching regex from the
        contexts list will be merged (in order) to get the final context.
        Otherwise, only the first matching regex is used. Defaults to
        ``False``.
    """

    def __init__(self,
                 environment,
                 sources,
                 searchpath,
                 outpath,
                 encoding,
                 logger,
                 contexts=None,
                 rules=None,
                 mergecontexts=False,
                 ):
        self._env = environment
        self.sources = sources
        self.searchpath = searchpath
        self.outpath = outpath
        self.encoding = encoding
        self.logger = logger
        self.contexts = contexts or []
        self.rules = rules or []
        self.mergecontexts = mergecontexts

    def get_template(self, source):
        """Get a :class:`jinja2.Template` from the environment.

        :param template_name: A string representing the name of the template.
        """
        return self._env.get_template(source.filename)

    def get_context(self, source):
        """Get the context for a source.

        If no matching value is found, an empty context is returned.
        Otherwise, this returns either the matching value if the value is
        dictionary-like or the dictionary returned by calling it with
        *template* if the value is a function.

        If several matching values are found, the resulting dictionaries will
        be merged before being returned if mergecontexts is True. Otherwise,
        only the first matching value is returned.

        :param source: the source to get the context for
        """
        context = {}
        for regex, context_generator in self.contexts:
            if re.match(regex, source.filename):
                if inspect.isfunction(context_generator):
                    if _has_argument(context_generator):
                        template = self.get_template(source)
                        context.update(context_generator(template))
                    else:
                        context.update(context_generator())
                else:
                    context.update(context_generator)

                if not self.mergecontexts:
                    break
        return context

    def get_rule(self, source):
        """Find a matching compilation rule for a source.

        Raises a :exc:`ValueError` if no matching rule can be found.

        :param source: the source needing a compilation rule
        """
        for regex, render_func in self.rules:
            if re.match(regex, source.filename):
                return render_func
        raise ValueError("no matching rule")

    def _ensure_dir(self, template_name):
        """Ensure the output directory for a template exists."""
        head = os.path.dirname(template_name)
        if head:
            file_dirpath = os.path.join(self.outpath, head)
            if not os.path.exists(file_dirpath):
                os.makedirs(file_dirpath)

    def render_template(self, source, context=None, filepath=None):
        """Render a single `Source` object using Jinja2.

        :param source:
            A :class:`Source` to render.

        :param context:
            Optional. A dictionary representing the context to render
            *template* with.

        :param filepath:
            Optional. A file or file-like object to dump the complete template
            stream into. Defaults to to ``os.path.join(self.outpath,
            source.filename)``.

        """
        self.logger.info("Rendering %s..." % source.filename)

        self._ensure_dir(source.filename)
        if filepath is None:
            filepath = os.path.join(self.outpath, source.filename)

        template = self.get_template(source)
        template.stream(**context).dump(filepath, self.encoding)
        return filepath

    def copy_static(self, source):
        """Copy a static source without Jinja2 rendering.

        :param source:
            A :class:`Source` to copy.

        """
        fname = source.filename
        input_location = os.path.join(self.searchpath, fname)
        output_location = os.path.join(self.outpath, fname)
        self.logger.info("Copying %s to %s." % (fname, output_location))
        self._ensure_dir(fname)
        shutil.copy2(input_location, output_location)
        return output_location

    def handle_sources(self, sources, outpath=None):
        """Handles a collection of sources (of any flavor).

        :param sources:
            A iterable of :class:`Source` objects to handle.

        :param outpath:
            Optional. A file or file-like object to dump the complete template
            streams into. Defaults to to ``os.path.join(self.outpath,
            template.name)``.

        """
        for source in sources:
            self.handle_source(source, outpath)

    def handle_source(self, source, outpath=None):
        """Handles a single source (of any flavor).

        :param source:
            A :class:`Source` objects to handle.

        :param outpath:
            Optional. A file or file-like object to dump the complete template
            streams into. Defaults to to ``os.path.join(self.outpath,
            template.name)``.

        If a Rule matching the template is found, the rendering task is
        delegated to the rule.

        Returns the name of the output file or None if there is no output file
        (this happens for data files, ignored files and partial templates).
        """

        context = self.get_context(source)
        try:
            rule = self.get_rule(source)
        except ValueError:
            if source.flavor == TEMPLATE_FLAVOR:
                return self.render_template(source, context, outpath)
            elif source.flavor == STATIC_FLAVOR:
                return self.copy_static(source)
            else:
                return None
        else:
            return rule(self, source, **context)

    def render(self):
        """Generate the site by handling all sources."""
        self.handle_sources(self.sources)
