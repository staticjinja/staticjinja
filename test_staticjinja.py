import os
import shutil
import subprocess
import filecmp
import difflib
import glob

import unittest.mock as mock
from pytest import fixture, raises
import pytest_check as check

from staticjinja import cli, Site, Reloader

PROJECT_ROOT = os.path.dirname(__file__)


class ContentDirCmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """
    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(self.left, self.right, self.common_files,
                                 shallow=False)
        self.same_files, self.diff_files, self.funny_files = fcomp


def print_diff(filename1, filename2):
    with open(filename1) as f1, open(filename2) as f2:
        diff = difflib.unified_diff(f1.readlines(), f2.readlines(),
                                    fromfile=filename1, tofile=filename2)
        for line in diff:
            # line already ends with a newline
            print(line, end='')


def check_same(dir1, dir2):
    cmp = ContentDirCmp(dir1, dir2)
    cmp.report()
    for df in cmp.diff_files:
        print_diff(os.path.join(dir1, df), os.path.join(dir2, df))
    check.equal(cmp.left_only, [])
    check.equal(cmp.right_only, [])
    check.equal(cmp.funny_files, [])
    check.equal(cmp.diff_files, [])
    for subdir in cmp.common_dirs:
        check_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir))


@fixture
def filename():
    return "test.txt"


@fixture
def template_path(tmpdir):
    return tmpdir.mkdir("templates")


def example_names():
    names = os.listdir(os.path.join(PROJECT_ROOT, 'examples'))
    ignored = ['__pycache__']
    for ig in ignored:
        while ig in names:
            names.remove(ig)
    return names


@fixture(params=example_names())
def example_name(request):
    return request.param


def test_example(tmpdir, example_name):
    source_directory = os.path.join(PROJECT_ROOT, 'examples', example_name)
    working_directory = os.path.join(str(tmpdir), example_name)
    shutil.copytree(source_directory, working_directory)

    # On windows, when the repo is checked out with git, all the unix-standard
    # NL linefeed characters are converted to the dos-standard CRNL newline
    # characters. However, jinja2 always uses NL newlines. Thus all the
    # rendered files in `build/` will have NL, but all the files in
    # `build-EXPECTED/` will have CRNL. Therefore convert `build-EXPECTED/`
    # to use NL, so we can meaningfully compare them.
    # I figured it's better to just do the conversion here, as opposed to a
    # change in globl .gitconfig.
    if os.name == 'nt':
        pattern = os.path.join(working_directory,
                               'build-EXPECTED',
                               '**',
                               '*.html',
                               )
        file_list = glob.glob(pattern, recursive=True)
        args = ['dos2unix'] + file_list
        assert subprocess.call(args) == 0, "dos2unix failed"

    # os.getcwd() starts in the project's root directory.
    # But, we want to emulate running build.sh as if we were inside
    # the example directory.
    initial_directory = os.getcwd()
    try:
        os.chdir(working_directory)
        print("Running example {}".format(source_directory))
        print("Working directory for debugging: {}".format(working_directory))
        assert subprocess.call(['sh', 'build.sh']) == 0, "build.sh failed"
        check_same('build-EXPECTED', 'build')
    finally:
        os.chdir(initial_directory)


@fixture
def build_path(tmpdir):
    return tmpdir.mkdir("build")


@fixture
def site(template_path, build_path):
    template_path.join('.ignored1.html').write('Ignored 1')
    template_path.join('_partial1.html').write('Partial 1')
    template_path.join('template1.html').write('Test 1')
    template_path.join('template2.html').write('Test 2')
    template_path.mkdir('sub').join('template3.html').write('Test {{b}}')
    template_path.mkdir('sub1').join('.ignored2.html').write('Ignored 2')
    template_path.mkdir('sub2').join('_partial2.html').write('Partial 2')
    template_path.mkdir('.ignoreds').join('ignored3.html').write('Ignored 3')
    template_path.mkdir('_partials').join('partial3.html').write('Partial 3')
    template_path.join('template4.html').write('Test {{b}} and {{c}}')
    template_path.mkdir('static_css').join('hello.css').write(
        'a { color: blue; }'
    )
    template_path.mkdir('static_js').join('hello.js').write(
        'var a = function () {return true};'
    )
    template_path.join('favicon.ico').write('Fake favicon')
    contexts = [('template2.html', lambda t: {'a': 1}),
                ('.*template3.html', lambda: {'b': 3}),
                ('template4.html', {'b': 4, 'c': 5}),
                ('.*[4-9].html', {'c': 6})]
    rules = [('template2.html', lambda env, t, a: None), ]
    return Site.make_site(searchpath=str(template_path),
                          outpath=str(build_path),
                          contexts=contexts,
                          rules=rules)


@fixture
def reloader(site):
    return Reloader(site)


def test_template_names(site):
    site.staticpaths = ["static_css", "static_js", "favicon.ico"]
    expected_templates = set(['template1.html',
                              'template2.html',
                              'sub/template3.html',
                              'template4.html'])
    assert set(site.template_names) == expected_templates


def test_templates(site):
    expected = list(site.template_names)
    assert [t.name for t in site.templates] == expected


def test_get_context(site):
    assert site.get_context(site.get_template("template1.html")) == {}
    assert site.get_context(
        site.get_template("template2.html")
    ) == {'a': 1}
    assert site.get_context(
        site.get_template("sub/template3.html")
    ) == {'b': 3}
    assert site.get_context(
        site.get_template("template4.html")
    ) == {'b': 4, 'c': 5}
    site.mergecontexts = True
    assert site.get_context(
        site.get_template("template4.html")
    ) == {'b': 4, 'c': 6}


def test_get_rule(site):
    with raises(ValueError):
        assert site.get_rule('template1.html')
    assert site.get_rule('template2.html')


def test_get_dependencies(site, filename):
    site.get_template = lambda x: filename
    assert site.get_dependencies(".%s" % filename) == []
    assert (list(site.get_dependencies("_%s" % filename)) ==
            list(site.templates))
    assert (list(site.get_dependencies("%s" % filename)) == [filename])


def test_render_template(site, build_path):
    site.render_template(site.get_template('template1.html'))
    template1 = build_path.join("template1.html")
    assert template1.check()
    assert template1.read() == "Test 1"


def test_render_nested_template(site, build_path):
    site.render_template(site.get_template('sub/template3.html'))
    template3 = build_path.join('sub').join("template3.html")
    assert template3.check()
    assert template3.read() == "Test 3"


def test_render_template_with_env_globals(template_path, build_path):
    """Ensure variables defined in env_globals can be accessed globally."""
    template_name = 'template.html'
    template_path.join(template_name).write('<h1>{{greeting}}</h1>')
    site = Site.make_site(searchpath=str(template_path),
                          outpath=str(build_path),
                          env_globals={'greeting': 'Hello world!'})
    site.render_template(site.get_template(template_name))
    assert build_path.join(template_name).read() == '<h1>Hello world!</h1>'


def test_render_templates(site, build_path):
    site.render_templates(site.templates)
    template1 = build_path.join("template1.html")
    assert template1.check()
    assert template1.read() == "Test 1"
    template3 = build_path.join('sub').join("template3.html")
    assert template3.check()
    assert template3.read() == "Test 3"


def test_build(site):
    templates = []

    def fake_site(template, context=None, filepath=None):
        templates.append(template)

    site.render_template = fake_site
    site.render()
    assert templates == list(site.templates)


def test_with_reloader(reloader, site):
    reloader.watch_called = False

    def watch(self):
        reloader.watch_called = True

    Reloader.watch = watch
    site.render(use_reloader=True)
    assert reloader.watch_called


def test_should_handle(reloader, template_path):
    template1_path = template_path.join("template1.html")
    test4_path = template_path.join("test4.html")

    test4_path.write('')
    assert reloader.should_handle("modified", str(template1_path))
    assert reloader.should_handle("modified", str(test4_path))
    assert reloader.should_handle("created", str(template1_path))
    assert not reloader.should_handle("deleted", str(template1_path))


def test_event_handler(reloader, template_path):
    templates = []

    def fake_site(template, context=None, filepath=None):
        templates.append(template)

    reloader.site.render_template = fake_site
    template1_path = str(template_path.join("template1.html"))
    reloader.event_handler("modified", template1_path)
    assert templates == [reloader.site.get_template("template1.html")]


def test_event_handler_static(reloader, template_path):
    found_files = []

    def fake_copy_static(files):
        found_files.extend(f.replace(os.sep, '/') for f in files)

    reloader.site.staticpaths = ["static_css"]
    reloader.site.copy_static = fake_copy_static
    template1_path = str(template_path.join("static_css").join("hello.css"))
    reloader.event_handler("modified", template1_path)
    assert found_files == list(reloader.site.static_names)


def test_ignored_file_is_ignored(site):
    assert site.is_ignored('.index.html')


def test_regular_file_is_not_ignored(site):
    assert not site.is_ignored('index.html')


def test_ignored_file_in_directory_is_ignored(site):
    assert site.is_ignored('/'.join(['.bar', 'index.html']))


def test_ignored_file_in_nested_directory_is_ignored(site):
    assert site.is_ignored('/'.join(['foo', '.bar', 'index.html']))


def test_ignored_file_in_normal_nested_directory_is_ignored(site):
    assert site.is_ignored('/'.join(['foo', 'bar', '.index.html']))


def test_partial_file_is_partial(site):
    assert site.is_partial('_index.html')


def test_regular_file_is_not_partial(site):
    assert not site.is_partial('index.html')


def test_partial_file_in_directory_is_partial(site):
    assert site.is_partial('/'.join(['_bar', 'index.html']))


def test_partial_file_in_nested_directory_is_partial(site):
    assert site.is_partial('/'.join(['foo', '_bar', 'index.html']))


def test_partial_file_in_normal_nested_directory_is_partial(site):
    assert site.is_partial('/'.join(['foo', 'bar', '_index.html']))


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.Site.make_site')
def test_cli_srcpath(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': 'templates',
        '--outpath': None,
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/templates',
        outpath='/',
        staticpaths=None
    )


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.Site.make_site')
def test_cli_srcpath_default(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': None,
        '--outpath': None,
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/templates',
        outpath='/',
        staticpaths=None
    )


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.Site.make_site')
def test_cli_srcpath_absolute(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'
    cli.render({
        '--srcpath': '/foo/templates',
        '--outpath': None,
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/foo/templates',
        outpath='/',
        staticpaths=None
    )
