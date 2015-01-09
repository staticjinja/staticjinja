import os


class Reloader(object):
    """
    Watches ``renderer.searchpath`` for changes and re-renders any changed
    Templates.

    :param renderer:
        A :class:`Renderer <Renderer>` object.

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
        print("%s %s" % (event_type, filename))
        return (event_type == "modified"
                and filename.startswith(self.searchpath))

    def event_handler(self, event_type, src_path):
        """Re-render templates if they are modified.

        :param event_type: a string, representing the type of event

        :param src_path: the path to the file that triggered the event.

        """
        filename = os.path.relpath(src_path, self.searchpath)
        if self.should_handle(event_type, src_path):
            if self.renderer.is_static(filename):
                files = self.renderer.get_dependencies(filename)
                self.renderer.copy_static(files)
            else:
                templates = self.renderer.get_dependencies(filename)
                self.renderer.render_templates(templates)

    def watch(self):
        """Watch and reload modified templates."""
        import easywatch
        easywatch.watch(self.searchpath, self.event_handler)
