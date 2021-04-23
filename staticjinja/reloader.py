from pathlib import Path


class Reloader:
    """
    Watches ``site.searchpath`` for changes and re-renders any changed
    Templates.

    :param site:
        A :class:`Site <Site>` object.

    """

    def __init__(self, site):
        self.site = site

    @property
    def searchpath(self):
        return self.site.searchpath

    def should_handle(self, event_type, filename):
        """Check if an event should be handled.

        An event should be handled if a file was created or modified, and
        still exists.

        :param event_type: a string, representing the type of event

        :param filename: the path to the file that triggered the event.
        """
        return event_type in ("modified", "created") and Path(filename).is_file()

    def event_handler(self, event_type, src_path):
        """Re-render templates if they are modified.

        :param event_type: a string, representing the type of event

        :param src_path: the absolute path to the file that triggered the event.
        """
        if not self.should_handle(event_type, src_path):
            return
        filename = Path(src_path).relative_to(self.searchpath)
        self.site.logger.info("%s %s", event_type, filename)
        for f in self.site.get_dependents(filename):
            if self.site.is_static(f):
                self.site.copy_static([f])
            elif self.site.is_template(f):
                t = self.site.get_template(f)
                self.site.render_template(t)

    def watch(self):
        """Watch and reload modified templates."""
        import easywatch

        self.site.logger.info("Watching '%s' for changes...", self.searchpath)
        self.site.logger.info("Press Ctrl+C to stop.")
        easywatch.watch(self.searchpath, self.event_handler)
