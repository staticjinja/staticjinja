# -*- coding:utf-8 -*-

"""
Sources for staticjinja.
"""

import os
from itertools import chain

import jinja2.meta

from .dep_graph import DepGraph

STATIC_FLAVOR = 'static'
IGNORED_FLAVOR = 'ignored'
PARTIAL_FLAVOR = 'partial'
TEMPLATE_FLAVOR = 'template'
DATA_FLAVOR = 'data'


class SourceNotFoundError(Exception):
    """Raised when a source is searched by filename but not found."""
    pass


def dep_graph_from_sources(sources):
    """
    Makes a DepGraph objects from an iterable of Source object.
    """

    parents = dict((source, source.get_dep(sources)) for source in sources)

    return DepGraph.from_parents(parents)


class Source(object):
    """
    A source file (anything inside the searchpath).

    :param filename:
        A string giving a path relative to searchpath

    :param flavor:
        A string describing the flavor of this source

    :param environment:
        A :class:`jinja2.Environment`.

    :param extra_deps:
        A list of filename names occuring as extra dependencies.

    """

    def __init__(self, filename, flavor, environment, extra_deps=None):
        self.filename = filename
        self.flavor = flavor
        self._env = environment
        self._extra_deps = extra_deps or []

    def __hash__(self):
        return hash(self.filename)

    def __eq__(self, other):
        return self.filename == other.filename

    def __repr__(self):
        return self.filename

    def get_dep(self, sources_list):
        """Return the set of sources among sources_list which this source file
        directly depends on (excluding itself).

        :param sources_list:
            An iterable of Source objects.

        """
        if self.flavor in [STATIC_FLAVOR, IGNORED_FLAVOR, DATA_FLAVOR]:
            return set(self._extra_deps)
        else:
            source = self._env.loader.get_source(self._env, self.filename)[0]
            ast = self._env.parse(source)
            jinja_deps = jinja2.meta.find_referenced_templates(ast)

            # Note that both find_referenced_templates and extra_deps will give
            # us filepaths, so we need to convert it to the relevant Source
            # object among those provided.
            return set(
                    next((s for s in sources_list if s.filename == path), None)
                    for path in chain(jinja_deps, self._extra_deps))


class SourceManager(object):
    """
    Handles all source files from a staticjinja website.

    :param sources:
        An iterable of :class:`Source`

    :param environment:
        A :class:`jinja2.Environment`.

    :param dep_graph:
        A :class:`DepGraph` tracking dependencies between the provided sources
        files
    """

    def __init__(
            self,
            sources,
            environment,
            dep_graph
            ):
        self._env = environment
        self.sources = sources
        self.dep_graph = dep_graph

    def __iter__(self):
        return iter(self.sources)

    def __eq__(self, other):
        return set(self.sources) == set(other.sources)

    @staticmethod
    def is_static(filename, staticpaths):
        """Check if a file is a static file (which should be copied, rather
        than compiled using Jinja2).

        A file is considered static if it lives in any of the directories
        specified in ``staticpaths``.

        :param filename:
            A string, the name of the file to check

        :param staticpaths:
            An iterable of strings which are beginning of static paths relative
            to searchpath or ``None``.

        """
        if staticpaths is None:
            # We're not using static file support
            return False

        for path in staticpaths:
            if filename.startswith(path):
                return True
        return False

    @staticmethod
    def is_data(filename, datapaths):
        """Check if a file is a data file (which should be used by a context
        generator rather than compiled using Jinja2).

        A file is considered data if it lives in any of the directories
        specified in ``datapaths`` or is itself listed in ``datapaths``.

        :param filename: the name of the file to check

        :param datapaths:
            An iterable of strings which are beginning of data paths relative
            to searchpath or ``None``.

        """
        if datapaths is None:
            # We're not using data file support
            return False

        for path in datapaths:
            if filename.startswith(path):
                return True
        return False

    @staticmethod
    def is_partial(filename):
        """Check if a file is a partial.

        Partial files are not rendered, but they are used in rendering
        templates.

        A file is considered a partial if it or any of its parent directories
        are prefixed with an ``'_'``.

        :param filename:
            A string, the name of the file to check
        """
        return any((x.startswith("_") for x in filename.split(os.path.sep)))

    @staticmethod
    def is_ignored(filename):
        """Check if a file is an ignored file.

        Ignored files are neither rendered nor used in rendering templates.

        A file is considered ignored if it or any of its parent directories
        are prefixed with an ``'.'``.

        :param filename:
            A string, the name of the file to check
        """
        return any((x.startswith(".") for x in filename.split(os.path.sep)))

    @classmethod
    def classify(cls, filename, datapaths=None, staticpaths=None):
        """Decides a flavor for a file.

        :param filename:
            A string, the name of the file to check

        :param datapaths:
            An iterable of strings which are beginning of data paths relative
            to searchpath or ``None``.

        :param staticpaths:
            An iterable of strings which are beginning of static paths relative
            to searchpath or ``None``.

        """

        if cls.is_data(filename, datapaths):
            flavor = DATA_FLAVOR
        elif cls.is_static(filename, staticpaths):
            flavor = STATIC_FLAVOR
        elif cls.is_ignored(filename):
            flavor = IGNORED_FLAVOR
        elif cls.is_partial(filename):
            flavor = PARTIAL_FLAVOR
        else:
            flavor = TEMPLATE_FLAVOR
        return flavor

    @classmethod
    def make_sources(
            cls,
            environment,
            staticpaths=None,
            datapaths=None,
            extra_deps=None
            ):
        """
        Constructs a SourceManager object.

        :param environment:
            A :class:`jinja2.Environment`.

        :param staticpaths:
            List of directory names to get static files from (relative to
            searchpath).
            Defaults to ``None``.

        :param datapaths:
            List of directories to get data files from (relative to
            searchpath).
            Defaults to ``None``.

        :param extra_deps:
            List of dependencies on data files. Each dependency is a pair
            (f, d) where f is a (maybe partial) template file path
            and d is a list of data file paths which are used to generate f.
            All path are relative to searchpath.
            Defaults to ``None``.

        """

        extra_deps = extra_deps or {}
        sources = []
        for filename in environment.list_templates():
            flavor = cls.classify(
                    filename,
                    datapaths=datapaths,
                    staticpaths=staticpaths)

            sources.append(
                    Source(
                        filename,
                        flavor,
                        environment,
                        extra_deps.get(filename, None)
                        )
                    )

        dep_graph = dep_graph_from_sources(sources)

        return cls(
            sources,
            environment,
            dep_graph
            )

    def get_dependencies(self, source):
        """Get the list of sources that depends on the given one.

        :param source:
            the source to find dependencies of
        """
        if source.flavor in [TEMPLATE_FLAVOR, STATIC_FLAVOR]:
            return [source]
        elif source.flavor in [PARTIAL_FLAVOR, DATA_FLAVOR]:
            return [source
                    for source in self.dep_graph.get_descendants(source)
                    if source.flavor in [TEMPLATE_FLAVOR, STATIC_FLAVOR]
                    ]
        elif source.flavor == IGNORED_FLAVOR:
            return []
        else:
            # Maybe this case shouldn't exist and we should trust our code
            raise ValueError('Invalid source file')

    def update_dep_graph(self, source):
        """Updates self.dep_graph using source.get_dep.

        :param source:
            A class:`Source` to update

        """
        self.dep_graph.update_vertex(
                source,
                source.get_dep(self.sources))

    def source_from_name(self, name):
        """Among managed source, find the one corresponding to some file name.

        :param name:
            A string, the filepath relative to searchpath.

        """
        for source in self.sources:
            if source.filename == name:
                return source
        raise SourceNotFoundError('Source not found')

    def remove_source(self, source):
        """Remove a source from managed sources.

        :param source:
            A class:`Source` to remove

        """
        self.sources.remove(source)
        self.dep_graph.remove_vertex(source)

    def add_source(self, source):
        """Add a source to managed sources.

        :param source:
            A class:`Source` to add

        """
        self.sources.append(source)
        self.dep_graph.add_vertex(source, source.get_dep(self.sources))
