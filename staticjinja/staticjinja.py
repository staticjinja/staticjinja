# -*- coding:utf-8 -*-

"""
Simple static page generator.

Uses Jinja2 to compile templates.
"""

from __future__ import absolute_import

import logging
import os
import jinja2

from .sources import SourceManager
from .builder import Builder
from .reloader import Reloader


def coerce_to_absolute_path(searchpath):
    """Coerce searchpath to an absolute path if it is not already"""
    if not os.path.isabs(searchpath):
        # I can't see how the behavior in upstream is relevant so
        # I change it
        project_path = os.getcwd()
        searchpath = os.path.join(project_path, searchpath)
    return searchpath


class Site(object):
    """The Site object.

    :param sources:
        A :class:`SourceManager` tracking all sources of the website.

    :param builder:
        A website :class:`Builder`.

    :param reloader:
        A :class:`Reloader` responsible for watching the source directory.

    :param logger:
        A logging.Logger object used to log events.

    :param searchpath:
        A string representing the absolute path to the directory that the Site
        should search to discover templates. Defaults to ``'templates'``.

    :param outpath:
        A string representing the name of the directory that the Site
        should store rendered files in. Defaults to ``'.'``.
    """

    def __init__(
            self,
            sources,
            builder,
            reloader,
            logger,
            searchpath='templates',
            outpath='',):

        self.sources = sources
        self.builder = builder
        self.reloader = reloader
        self.logger = logger
        self.searchpath = searchpath
        self.outpath = outpath

    def render(self, use_reloader=False):
        """Generate the site.

        :param use_reloader: `bool` if True, reload templates on modification.
            Defaults to False

        """

        self.builder.render()

        if use_reloader:
            self.logger.info("Watching '%s' for changes..." %
                             self.searchpath)
            self.logger.info("Press Ctrl+C to stop.")

            self.reloader.watch()

    @staticmethod
    def make_jinja2_env(
                env_kwargs,
                searchpath,
                encoding,
                extensions,
                filters):
        """Prepare the Jinja2 Environment.

        :param env_kwargs:
            A dict of extra named argument for the environment

        :param searchpath:
            A string representing the name of the directory to search for
            templates.

        :param encoding:
            A string representing the encoding that the Site should use when
            rendering templates. Defaults to ``'utf8'``.

        :param extensions:
            A list of Jinja2 extensions to use.

        :param filters:
            A dict of custom Jinja2 filters.
        """
        if env_kwargs is None:
            env_kwargs = {}
        env_kwargs['loader'] = jinja2.FileSystemLoader(
                searchpath=searchpath,
                encoding=encoding)
        env_kwargs.setdefault('extensions', extensions or [])
        env_kwargs.setdefault('keep_trailing_newline', True)
        environment = jinja2.Environment(**env_kwargs)
        if filters:
            for k, v in filters.items():
                environment.filters[k] = v
        return environment

    @staticmethod
    def make_logger():
        """Returns a logger object"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler())
        return logger

    @staticmethod
    def make_sources(*args, **kwargs):
        """Returns a SourceManager object"""
        return SourceManager.make_sources(*args, **kwargs)

    @staticmethod
    def make_builder(*args, **kwargs):
        """Returns a Builder object"""
        return Builder(*args, **kwargs)

    @staticmethod
    def make_reloader(*args, **kwargs):
        """Returns a Reloader object"""
        return Reloader(*args, **kwargs)

    @classmethod
    def make_site(cls,
                  searchpath="templates",
                  outpath=".",
                  contexts=None,
                  rules=None,
                  encoding="utf8",
                  extensions=None,
                  staticpaths=None,
                  datapaths=None,
                  extra_deps=None,
                  filters=None,
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
            during rendering. *function* must take a
            :class:`jinja2.Environment` object, a filename, and a context as
            parameters and render the template. Defaults to ``[]``.

        :param encoding:
            A string representing the encoding that the Site should use when
            rendering templates. Defaults to ``'utf8'``.

        :param extensions:
            A list of :ref:`Jinja extensions <jinja-extensions>` that the
            :class:`jinja2.Environment` should use. Defaults to ``[]``.

        :param staticpaths:
            List of directories to get static files from (relative to
            searchpath).
            Defaults to ``None``.

        :param datapaths:
            List of directories to get data files from (relative to
            searchpath).
            Defaults to ``None``.

        :param extra_deps:
            List of dependencies on data files. Each dependency is a pair (f,
            d) where f is a (maybe partial) template file path and d is a list
            of data file paths which are used to generate f.  All path are
            relative to searchpath.
            Defaults to ``None``.

        :param filters:
            A dictionary of Jinja2 filters to add to the Environment.
            Defaults to ``{}``.

        :param env_kwargs:
            A dictionary that will be passed as keyword arguments to the
            jinja2 Environment. Defaults to ``{}``.

        :param mergecontexts:
            A boolean value. If set to ``True``, then all matching regex from
            the contexts list will be merged (in order) to get the final
            context.  Otherwise, only the first matching regex is used.
            Defaults to ``False``.
        """

        searchpath = coerce_to_absolute_path(searchpath)

        environment = cls.make_jinja2_env(
                env_kwargs,
                searchpath,
                encoding,
                extensions,
                filters)

        logger = cls.make_logger()

        sources = cls.make_sources(
                environment,
                datapaths=datapaths,
                staticpaths=staticpaths,
                extra_deps=extra_deps,
                )

        builder = cls.make_builder(
                environment,
                sources,
                searchpath=searchpath,
                outpath=outpath,
                encoding=encoding,
                logger=logger,
                rules=rules,
                contexts=contexts,
                mergecontexts=mergecontexts)

        reloader = cls.make_reloader(
                searchpath, datapaths, staticpaths,
                environment, sources, builder, logger)

        return Site(
                sources,
                builder,
                reloader,
                logger,
                searchpath=searchpath,
                outpath=outpath,
                )

    def __repr__(self):
        return "Site('%s', '%s')" % (self.searchpath, self.outpath)

# Alias for backward compatibility
make_site = Site.make_site
