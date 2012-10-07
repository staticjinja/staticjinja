"""
Simple static page generator.
Uses jinja2 to compile templates.
Templates should live inside `./templates` and will be compiled in '.'.
"""
import inspect
import os
import time

from jinja2 import Environment, FileSystemLoader


def build_template(env, template_name, **kwargs):
    """Compile a template.
    *   env should be a Jinja environment variable indicating where to find the
        templates.
    *   template_name should be the name of the template as it appears inside
        of `./templates`.
    *   kwargs should be a series of key-value pairs. These items will be
        passed to the template to be used as needed.
    """
    template = env.get_template(template_name)
    head, tail = os.path.split(template_name)
    if head and not os.path.exists(head):
        os.makedirs(head)
    template.stream(**kwargs).dump(tail)


def should_render(filename):
    """Check if the file should be rendered.
    -   Hidden files will not be rendered.
    -   Files prefixed with an underscore are assumed to be partials and will
        not be rendered.
    """
    return not (filename.startswith('_') or filename.startswith("."))


def render_templates(env, contexts, filter_func=None):
    """Render each template inside of `env`.
    -   env should be a Jinja environment object.
    -   filter_func should be a function that takes a filename and returns
        a boolean indicating whether or not a template should be rendered.
    """
    if contexts is None:
        contexts = {}
    for filename in env.list_templates(filter_func=filter_func):
        try:
            context = contexts[filename]()
        except KeyError:
            context = {}
        print "Building %s..." % filename
        build_template(env, filename, **context)


def watch(path, **kwargs):
    """Watch a directory for changes.
    -   path should be the directory to watch
    -   kwargs should be a mapping of watchdog EventHandler method names to
        handlers (e.g., on_modified)
    """
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    # Start watching for any changes
    EventHandler = type("EventHandler", (FileSystemEventHandler,), kwargs)
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main(searchpath="templates", filter_func=None, contexts=None,
         extensions=None, autoreload=True):
    """
    Render each of the templates and then recompile on any changes.
    -   searchpath should be the directory that contains the template.
        Defaults to "templates"
    -   filter_func should be a function that takes a filename and returns
        a boolean indicating whether or not a template should be rendered.
        Defaults to ignore any files with '.' or '_' prefixes.
    -   contexts should be a map of template names to functions where each
        function should return a context for that template.
    -   extensions should be any extensions to add to the Environment.
    -   autoreload should be a boolean indicating whether or not to
        automatically recompile templates. Defaults to true.
    """
    if contexts is None:
        contexts = {}
    if extensions is None:
        extensions = []
    if filter_func is None:
        filter_func = should_render

    # Get calling module
    mod = inspect.getmodule(inspect.stack()[1][0])
    # Absolute path to project
    project_path = os.path.realpath(os.path.dirname(mod.__file__))
    # Absolute path to templates
    template_path = os.path.join(project_path, searchpath)

    loader = FileSystemLoader(searchpath=searchpath)
    env = Environment(loader=loader,
                      extensions=extensions)
    render_templates(env, contexts, filter_func=filter_func)
    print "Templates built."

    if autoreload:
        print "Watching '%s' for changes..." % searchpath
        print "Press Ctrl+C to stop."

        def on_modified(self, event):
            if event.src_path.startswith(template_path):
                render_templates(env, contexts, filter_func=should_render)
                print "Templates built."
        watch("./" + searchpath, on_modified=on_modified)

        print "Process killed"
    return 0
