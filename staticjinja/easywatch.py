"""
Easywatch
Dead-simple way to watch a directory.
"""
import functools
import time

from watchdog.observers import Observer
from watchdog.events import (
        FileSystemEventHandler,
        EVENT_TYPE_MOVED,
        EVENT_TYPE_DELETED,
        EVENT_TYPE_CREATED,
        EVENT_TYPE_MODIFIED)


MOVED = EVENT_TYPE_MOVED
DELETED = EVENT_TYPE_DELETED
CREATED = EVENT_TYPE_CREATED
MODIFIED = EVENT_TYPE_MODIFIED


def watch(path, handler):
    """Watch a directory for events.
    -   path should be the directory to watch
    -   handler should a function which takes an event_type and src_path
        and does something interesting. event_type will be one of 'created',
        'deleted', 'modified', or 'moved'. src_path will be the absolute
        path to the file that triggered the event.
    """
    # let the user just deal with events
    @functools.wraps(handler)
    def wrapper(self, event):
        if not event.is_directory:
            return handler(event.event_type, event.src_path)
    attrs = {'on_any_event': wrapper}
    EventHandler = type("EventHandler", (FileSystemEventHandler,), attrs)
    observer = Observer()
    observer.schedule(EventHandler(), path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
