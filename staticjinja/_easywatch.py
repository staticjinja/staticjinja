"""
Copied from
https://github.com/Ceasar/easywatch/blob/1dd464d2acca5932473759b187dec4eb63dab2d9/easywatch/easywatch.py
"""
from __future__ import annotations

import functools
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def watch(path: str | Path, handler) -> None:
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

    attrs = {"on_any_event": wrapper}
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
