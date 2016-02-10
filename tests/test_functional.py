import pytest
from pytest import fixture
import os
import re
import shutil
import yaml
import datetime
import threading
import time
import filecmp
from itertools import chain
import logging

import functools
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import jinja2
import jinja2.ext
import markdown

from staticjinja.staticjinja import Site
from staticjinja.builder import Builder
from staticjinja.sources import SourceManager

pytestmark = pytest.mark.func


def diff(dir1, dir2):
    """
    Returns the set of files differing in dir1 and dir2 (either present in only
    one of them or having a different content).
    This function is an adpatation of
    http://stackoverflow.com/a/4188870
    """
    walk1 = sorted(list(os.walk(dir1)))
    walk2 = sorted(list(os.walk(dir2)))

    if len(walk1) != len(walk2):
        return set(walk1).symmetric_difference(set(walk2))

    for (p1, d1, fl1), (p2, d2, fl2) in zip(walk1, walk2):
        d1, fl1, d2, fl2 = set(d1), set(fl1), set(d2), set(fl2)
        if d1 != d2:
            return d1.symmetric_difference(d2)
        if fl1 != fl2:
            return fl1.symmetric_difference(fl2)
        for f in fl1:
            same, diff, weird = filecmp.cmpfiles(p1, p2, fl1, shallow=False)
            if diff or weird:
                return set(chain(diff, weird))


def watch_with_signal(path, handler, stop_watching, watcher_ready):
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
    watcher_ready.set()
    stop_watching.wait()
    observer.stop()
    observer.join()


def make_mock_watch(stop_watching, watcher_ready):
    def mock_watch(self):
        watch_with_signal(
                self.searchpath, self.event_handler,
                stop_watching, watcher_ready)
    return mock_watch


@fixture
def source_dir(request):
    filename = request.module.__file__
    test_dir = os.path.dirname(filename)
    return os.path.join(test_dir, 'example')


@fixture
def expected_build_dir(request):
    filename = request.module.__file__
    test_dir = os.path.dirname(filename)
    return os.path.join(test_dir, 'build_check')


@fixture
def expected_watch_dir(request):
    filename = request.module.__file__
    test_dir = os.path.dirname(filename)
    return os.path.join(test_dir, 'watch_check')


@fixture
def tmp_source_dir(tmpdir, source_dir):
    tmp_source_dir = tmpdir.join('example')
    shutil.copytree(source_dir, str(tmp_source_dir))

    return tmp_source_dir


# Custom MarkdownExtension
class MarkdownExtension(jinja2.ext.Extension):
    tags = set(['markdown'])

    def __init__(self, environment):
        super(MarkdownExtension, self).__init__(environment)
        environment.extend(
            markdowner=markdown.Markdown()
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(
            ['name:endmarkdown'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_markdown_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _markdown_support(self, caller):
        return self.environment.markdowner.convert(caller()).strip()


def get_post_contents(template):
    with open(template.filename) as f:
        return {'post': f.read()}


# compilation rule
def render_post(builder, source, **context):
    """Render a template as a post."""
    template = builder.get_template(source)
    head, tail = os.path.split(template.name)
    post_title, _ = tail.split('.')
    if head:
        out = "%s/%s.html" % (head, post_title)
        if not os.path.exists(head):
            os.makedirs(head)
    else:
        out = "%s.html" % (post_title, )
    template.stream(**context).dump(out)


@fixture
def get_knights(tmp_source_dir):
    def context_gen():
        data_filename = os.path.join(str(tmp_source_dir), 'data', 'knights')
        with open(data_filename, 'r') as f:
            data = yaml.load(f)
        return data
    return context_gen


def date(template):
    template_mtime = os.path.getmtime(template.filename)
    date = datetime.datetime.fromtimestamp(template_mtime)
    return {'template_date': date.strftime('%d %B %Y')}

# Computed using Python3 :
# JANUARY_FIRST_2016 = datetime.datetime(2016, 1, 1, 0, 0).timestamp()
JANUARY_FIRST_2016 = 1451602800.0


def test_render(tmp_source_dir, tmpdir, expected_build_dir, get_knights):
    outpath = os.path.join(str(tmpdir), 'build', '')
    print('Will output to:\n', outpath)
    os.makedirs(outpath)

    index_path = str(tmp_source_dir.join('index.html'))
    with open(index_path, 'a'):
        os.utime(index_path, (JANUARY_FIRST_2016, JANUARY_FIRST_2016))

    site = Site.make_site(
                  searchpath=str(tmp_source_dir),
                  outpath=outpath,
                  contexts=[
                      ('.*.md', get_post_contents),
                      ('knights.html', get_knights),
                      ('index.html', date),
                      ('.*', {'base_url': 'http://www.python.org'})
                      ],
                  rules=[('.*.md', render_post)],
                  encoding="utf8",
                  extensions=[MarkdownExtension],
                  staticpaths=['images'],
                  datapaths=['data'],
                  extra_deps={'knights.html': set(['data/knights'])},
                  filters={
                      'hello_world': lambda x: 'Hello world!',
                      'my_lower': lambda x: x.lower(),
                      },
                  env_kwargs=None,
                  mergecontexts=True)

    site.render()
    assert not diff(expected_build_dir, outpath)


def test_watch(
        tmpdir, monkeypatch,
        tmp_source_dir, expected_watch_dir, get_knights):
    stop_watching = threading.Event()
    watcher_ready = threading.Event()
    monkeypatch.setattr(
            'staticjinja.reloader.Reloader.watch',
            make_mock_watch(stop_watching, watcher_ready))

    outpath = os.path.join(str(tmpdir), 'watched', '')
    print('Will output to:\n', outpath)
    os.makedirs(outpath)

    index_path = str(tmp_source_dir.join('index.html'))
    with open(index_path, 'a'):
        os.utime(index_path, (JANUARY_FIRST_2016, JANUARY_FIRST_2016))

    site = Site.make_site(
                  searchpath=str(tmp_source_dir),
                  outpath=outpath,
                  contexts=[
                      ('.*.md', get_post_contents),
                      ('knights.html', get_knights),
                      ('index.html', date),
                      ('.*', {'base_url': 'http://www.python.org'})
                      ],
                  rules=[('.*.md', render_post)],
                  encoding="utf8",
                  extensions=[MarkdownExtension],
                  staticpaths=['images'],
                  datapaths=['data'],
                  extra_deps={'knights.html': set(['data/knights'])},
                  filters={
                      'hello_world': lambda x: 'Hello world!',
                      'my_lower': lambda x: x.lower(),
                      },
                  env_kwargs=None,
                  mergecontexts=True)

    thread = threading.Thread(
            target=site.render,
            kwargs={'use_reloader': True})
    thread.start()
    watcher_ready.wait()

    index_file = tmp_source_dir.join('index.html')
    index_file.write(
            '{% extends "_base.html" %}\n'
            '{% block content %}\n'
            '<h1>{{\'\' | hello_world}}</h1>\n'
            'I changed something here.\n'
            '{% endblock %}')

    new_file = tmp_source_dir.join('new_file.html')
    new_file.write(
            '{% extends "_base.html" %}\n'
            '{% block content %}\n'
            'This is my new file.\n'
            '{% endblock %}')

    tmp_data_dir = tmp_source_dir.join('data')
    knights_file = tmp_data_dir.join('knights')
    knights_file.write('knights:\n - sir arthur')

    base_file = tmp_source_dir.join('_base.html')
    base_file.write(
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '  <head>\n'
            '    <meta charset="utf-8">\n'
            '    <title>StaticJinja</title>\n'
            '\n'
            '	<link href="{{ base_url }}css/style.css" rel="stylesheet">\n'
            '  </head>\n'
            '  <body>\n'
            '	  {% block content %}\n'
            '	  {% endblock %}\n'
            '  </body>\n'
            ' </html>\n')

    # Next line gives time to actually write the files modified above (I tried
    # various combination of flush and os.fsync with no success)
    time.sleep(1)
    stop_watching.set()
    thread.join()
    assert not diff(expected_watch_dir, outpath)


class MySourceManager(SourceManager):
    @staticmethod
    def is_partial(filename):
        return 'partials' in filename


class MyBuilder(Builder):
    def handle_source(self, source, outpath=None):
        outfile = Builder.handle_source(self, source, outpath=None)
        if outfile and outfile.endswith('.html'):
            linelist = []
            with open(outfile) as f:
                for line in f:
                    newline = line.replace('Perl', '')
                    linelist.append(newline)
            with open(outfile, "w") as f:
                f.truncate()
                for line in linelist:
                    f.writelines(line)
        return outfile


def test_subclass(tmpdir):
    class MySite(Site):
        @staticmethod
        def make_logger():
            """Prepare the logger"""
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(str(tmpdir.join('build.log')))
            handler.setFormatter(
                    logging.Formatter('%(asctime)s - %(message)s'))
            logger.addHandler(handler)
            logger.addHandler(logging.StreamHandler())
            return logger

        @staticmethod
        def make_sources(*args, **kwargs):
            return MySourceManager.make_sources(*args, **kwargs)

        @staticmethod
        def make_builder(*args, **kwargs):
            return MyBuilder(*args, **kwargs)
    filename = __file__
    test_dir = os.path.dirname(filename)
    check_dir = os.path.join(test_dir, 'subclass_check')
    searchpath = os.path.join(test_dir, 'subclass')

    outpath = os.path.join(str(tmpdir), 'subclass', '')
    os.makedirs(outpath)

    site = MySite.make_site(searchpath=searchpath, outpath=outpath)
    site.render()

    assert not diff(check_dir, outpath)

    logfile = tmpdir.join('build.log')
    lines = logfile.readlines()
    assert re.match(
      '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - Rendering index.html',
      lines[0])
    assert re.match(
      '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - Rendering perl.html',
      lines[1])
