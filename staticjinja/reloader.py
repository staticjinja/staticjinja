import os

from .dep_graph import DepGraph


class Reloader(object):
    """
    Watches ``site.searchpath`` for changes and re-renders any changed
    Templates.

    :param site:
        A :class:`Site <Site>` object.

    """
    def __init__(self, site):
        self.site = site
        # The following could be part of the Site.__init__ but it would waste
        # time if the reloader is not used
        self.site.dep_graph = DepGraph(site)

    @property
    def searchpath(self):
        return self.site.searchpath

    def should_handle(self, event_type, filename):
        """Check if an event should be handled.

        An event should be handled if a file in the searchpath was modified.

        :param event_type: a string, representing the type of event

        :param filename: the path to the file that triggered the event.
        """
        return (event_type in ("modified", "created") and
                filename.startswith(self.searchpath) and
                os.path.isfile(filename))

    def event_handler(self, event_type, src_path):
        """Re-render templates if they are modified.

        :param event_type: a string, representing the type of event

        :param src_path: the path to the file that triggered the event.

        """
        filename = os.path.relpath(src_path, self.searchpath)
        if self.should_handle(event_type, src_path):
            print("%s %s" % (event_type, filename))
            if self.site.is_static(filename):
                self.site.copy_static([filename])
            elif self.site.is_ignored(filename):
                return
            else:
                # Here the changed file is a (maybe partial) template or a data
                # file
                self.site.dep_graph.update(filename)

                if self.site.is_template(filename):
                    needs_rendering = [filename]
                else:
                    needs_rendering = filter(
                        self.site.is_template,
                        self.site.get_dependencies(filename)
                        )
                self.site.render_templates(needs_rendering)

    def watch(self):
        """Watch and reload modified templates."""
        import easywatch
        easywatch.watch(self.searchpath, self.event_handler)
