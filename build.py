"""
Simple static page generator.
Uses jinja2 to compile templates.
Templates should live inside `./templates` and will be compiled in '.'.
"""
import csv
import sys

from jinja2 import Environment, FileSystemLoader


def build_template(env, template_name, **kwargs):
    """Compile a template."""
    print "Building %s..." % template_name
    template = env.get_template(template_name)
    with open(template_name, "w") as f:
        f.write(template.render(**kwargs))


def parse_csv(filename):
    """Read data from a CSV."""
    with open(filename, 'rb') as f:
        return list(csv.DictReader(f))


def build_index(env):
    """Build the index page."""
    build_template(env, 'index.html')


def main():
    env = Environment(loader=FileSystemLoader(searchpath="./templates"))
    build_index(env)
    print "Templates built."


if __name__ == "__main__":
    main()

    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        import time

        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class JinjaEventHandler(FileSystemEventHandler):
            """
            Naive recompiler.
            Rebuilds all templates if anything changes in /templates.
            """
            def on_modified(self, event):
                print "Recompiling templates..."
                super(JinjaEventHandler, self).on_created(event)
                if event.src_path.endswith("/templates"):
                    main()

        # Start watching for any changes
        event_handler = JinjaEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path="./templates")
        observer.start()
        print "Watching ./templates for changes..."
        print "Press Ctrl+C to stop."
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        print "Process killed"
        observer.join()
