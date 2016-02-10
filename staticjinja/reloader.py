# -*- coding:utf-8 -*-

"""
Reloader object for staticjinja.

This object is responsible for watching the searchpath and calling the Builder
when some file needs to be handled and the SourceManager to keep it up to date.
"""

from __future__ import absolute_import

import os

from .easywatch import (
        DELETED,
        CREATED,
        MODIFIED)


from .sources import Source, SourceNotFoundError


class Reloader(object):
    """
    Watches ``site.searchpath`` for changes and uses ``builder`` to re-renders
    any affected file as determined by ``sources``. Reports what it does using
    ``logger``.

    :param searchpath:
        A string.

    :param datapaths:
        A string.

    :param staticpaths:
        A string.

    :param environment:
        A Jinja2 environment.

    :param sources:
        A :class:`SourceManager <SourceManager>` object.

    :param builder:
        A :class:`Site <Site>` object.

    :param logger:
        A :class:`Logger` object.
    """
    def __init__(
            self,
            searchpath,
            datapaths, staticpaths,
            environment, sources, builder, logger):
        self.sources = sources
        self.searchpath = searchpath
        self.datapaths = datapaths
        self.staticpaths = staticpaths
        self.env = environment
        self.builder = builder
        self.logger = logger

    def should_handle(self, event_type, filename):
        """Check if an event should be handled.

        An event should be handled if a file in the searchpath was modified,
        created or deleted.

        :param event_type: a string, representing the type of event

        :param filename: the path to the file that triggered the event.
        """
        return (event_type in (MODIFIED, CREATED, DELETED) and
                filename.startswith(self.searchpath) and
                os.path.isfile(filename))

    def event_handler(self, event_type, src_path):
        """Handle sources and update SourceManager as needed.

        :param event_type: a string, representing the type of event

        :param src_path: the path to the file that triggered the event.

        """
        filename = os.path.relpath(src_path, self.searchpath)
        # Avoid vim super temporary file
        if filename.endswith('4913'):
            return
        if self.should_handle(event_type, src_path):
            self.logger.info("%s %s" % (event_type, filename))
            if event_type in [CREATED, MODIFIED]:
                # Here we suspect some editing gets incorrectly reported as a
                # creation so we include the event type created
                try:
                    source = self.sources.source_from_name(filename)
                except SourceNotFoundError:
                    flavor = self.sources.classify(
                            filename,
                            datapaths=self.datapaths,
                            staticpaths=self.staticpaths)

                    source = Source(
                                filename,
                                flavor,
                                self.env,
                                None
                                )
                    self.sources.add_source(source)
                else:
                    self.sources.update_dep_graph(source)
                deps = self.sources.get_dependencies(source)
                self.builder.handle_sources(deps)
            else:  # event_type == DELETED:
                # Here again we must suspect strange phenomena with temporary
                # files whose deletion is detected by watchdog but not their
                # creation (vim backup files for instance...)
                try:
                    source = self.sources.source_from_name(filename)
                except SourceNotFoundError:
                    return
                else:
                    self.sources.remove_source(source)

    def watch(self):
        """Watch and reload modified templates."""
        from .easywatch import watch
        watch(self.searchpath, self.event_handler)
