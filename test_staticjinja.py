try:
    import unittest.mock as mock
except ImportError:
    import mock
from pytest import fixture, raises

from copy import deepcopy

from staticjinja import cli, make_site, Reloader, DepGraph
import staticjinja.staticjinja


@fixture
def filename():
    return "test.txt"


@fixture
def template_path(tmpdir):
    return tmpdir.mkdir("templates")


@fixture
def build_path(tmpdir):
    return tmpdir.mkdir("build")


@fixture
def site(template_path, build_path):
    """
    Provides a site with the following dependency structure
    (all arrows pointing upward):
    t1    t2
      \  / |
       p1  |  sub.t3
      /| \ | /
    d1 |  p2    t4
       |    \  /
      d2   data.d3
    each t is a template, p is a partial and d is a data file.
    There is also an ignored file .ignored1.html and a static files
    in static_js/ static_css/ and favicon.ico
    """

    template_path.join('.ignored1.html').write('Ignored 1')
    template_path.join('_partial1.html').write(
            'Partial 1\n'
            '{% block content %}{% endblock -%}\n'
            '{% import "_partial2.html" as p2 %}'
            )
    template_path.join('_partial2.html').write('Partial 2')
    template_path.join('template1.html').write(
            '{% extends "_partial1.html" %}\n'
            '{% block content %}Template 1{% endblock -%}'
            )
    template_path.join('template2.html').write(
            '{% extends "_partial1.html" %}\n'
            '{% block content %}Test 2{% endblock -%}\n'
            '{% include "_partial2.html" %}'
            )
    template_path.mkdir('sub').join('template3.html').write(
            'Test {{b}}\n'
            '{% include "_partial2.html" %}'
            )
    template_path.join('template4.html').write('Template {{b}} and {{c}}')

    template_path.join('data1').write('Data 1')
    template_path.join('data2').write('Data 2')
    template_path.mkdir('data').join('data3').write('Data 3')

    template_path.mkdir('static_css').join('hello.css').write(
        'a { color: blue; }'
    )
    template_path.mkdir('static_js').join('hello.js').write(
        'var a = function () {return true};'
    )
    template_path.join('favicon.ico').write('Fake favicon')

    staticpaths = ["static_css", "static_js", "favicon.ico"]
    datapaths = ["data", "data/data3"]
    extra_deps = {
            '_partial1.html': ['data1', 'data2'],
            '_partial2.html': ['data/data3'],
            'template4.html': ['data/data3'],
            }
    contexts = [('template2.html', lambda t: {'a': 1}),
                ('.*template3.html', lambda: {'b': 3}),
                ('template4.html', {'b': 4, 'c': 5}),
                ('.*[4-9].html', {'c': 6})]
    rules = [('template2.html', lambda env, t, a: None), ]
    return make_site(searchpath=str(template_path),
                     outpath=str(build_path),
                     contexts=contexts,
                     rules=rules,
                     staticpaths=staticpaths,
                     datapaths=datapaths,
                     extra_deps=extra_deps,
                     )


@fixture
def expected_parents():
    return {
            'data2': set(),
            'template4.html': set(['data/data3']),
            'sub/template3.html': set(['_partial2.html']),
            'template1.html': set(['_partial1.html']),
            'data1': set(),
            '_partial2.html': set(['data/data3']),
            '_partial1.html': set(['data2', 'data1', '_partial2.html']),
            'template2.html': set(['_partial1.html', '_partial2.html']),
            'data/data3': set()
            }


@fixture
def expected_children():
    return {
            'template1.html': set(),
            'template2.html': set(),
            'sub/template3.html': set(),
            'template4.html': set(),
            '_partial1.html': set(['template1.html', 'template2.html']),
            '_partial2.html': set([
                '_partial1.html',
                'template2.html',
                'sub/template3.html',
                ]),
            'data1': set(['_partial1.html']),
            'data2': set(['_partial1.html']),
            'data/data3': set(['_partial2.html', 'template4.html'])
            }


@fixture
def expected_deps():
    return {
        '.ignored1': [],
        'static_css/hello.css': ['static_css/hello.css'],
        'static_js/hello.js': ['static_js/hello.js'],
        'favicon.ico': ['favicon.ico'],
        '_partial1.html': [
                'template1.html',
                'template2.html',
                ],
        '_partial2.html': [
                '_partial1.html',
                'sub/template3.html',
                'template1.html',
                'template2.html',
                ],
        'data1': [
                '_partial1.html',
                'template1.html',
                'template2.html',
                ],
        'data2': [
                '_partial1.html',
                'template1.html',
                'template2.html',
                ],
        'data/data3': [
                '_partial1.html',
                '_partial2.html',
                'sub/template3.html',
                'template1.html',
                'template2.html',
                'template4.html',
                ],
        'template1.html': ['template1.html'],
        'template2.html': ['template2.html'],
        'sub/template3.html': ['sub/template3.html'],
        'template4.html': ['template4.html'],
        }


@fixture
def mock_dep_graph_init(expected_parents, expected_children):
    """Returns a mock constructor for DepGraph"""
    def mock_init(self, site):
        self.parents = expected_parents
        self.children = expected_children
        self.site = site
    return mock_init


@fixture
def reloader(site):
    return Reloader(site)


def test_template_names(site):
    expected_templates = set(['template1.html',
                              'template2.html',
                              'sub/template3.html',
                              'template4.html',
                              ])
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


def test_childrens(site, expected_children):
    site.dep_graph = DepGraph(site)
    assert site.dep_graph.children == expected_children


def test_get_dependencies(
        site,
        mock_dep_graph_init,
        expected_deps,
        monkeypatch
        ):
    """Test site.get_dependencies. It actually mostly tests
    DepGraph.connected_components but mocking the construction
    of the dependency graph."""

    monkeypatch.setattr(
            staticjinja.DepGraph,
            '__init__',
            mock_dep_graph_init
            )
    site.dep_graph = DepGraph(site)
    for filename in expected_deps:
        deps = sorted(site.get_dependencies(filename))
        assert deps == expected_deps[filename]


def test_update_dependencies_remove_dep(
        site,
        mock_dep_graph_init, expected_children, expected_parents,
        monkeypatch
        ):
    monkeypatch.setattr(
            staticjinja.DepGraph,
            '__init__',
            mock_dep_graph_init
            )
    site.dep_graph = DepGraph(site)

    # We will break the dependency of template2.html on _partial2.html
    def update_file_dep(s, f):
        if f == 'template2.html':
            return set(['_partial1.html'])
        else:
            return expected_parents[f]

    monkeypatch.setattr(
            staticjinja.Site,
            'get_file_dep',
            update_file_dep
            )

    site.dep_graph.update('template2.html')

    new_expected_parents = deepcopy(expected_parents)
    new_expected_parents.update({'template2.html': set(['_partial1.html'])})
    assert site.dep_graph.parents == new_expected_parents

    new_expected_children = deepcopy(expected_children)
    new_expected_children.update(
            {'_partial2.html': set(['_partial1.html', 'sub/template3.html'])}
            )
    assert site.dep_graph.children == new_expected_children


def test_update_dependencies_create_dep(
        site,
        mock_dep_graph_init, expected_children, expected_parents,
        monkeypatch
        ):
    monkeypatch.setattr(
            staticjinja.DepGraph,
            '__init__',
            mock_dep_graph_init
            )
    site.dep_graph = DepGraph(site)

    # We create a dependency of template4.html on data1
    def update_file_dep(s, f):
        if f == 'template4.html':
            return set(['data1', 'data/data3'])
        else:
            return expected_parents[f]

    monkeypatch.setattr(
            staticjinja.Site,
            'get_file_dep',
            update_file_dep
            )

    site.dep_graph.update('template4.html')

    new_expected_parents = deepcopy(expected_parents)
    new_expected_parents.update(
            {'template4.html': set(['data1', 'data/data3'])}
            )
    assert site.dep_graph.parents == new_expected_parents

    new_expected_children = deepcopy(expected_children)
    new_expected_children.update(
            {'data1': set(['_partial1.html', 'template4.html'])}
            )
    assert site.dep_graph.children == new_expected_children


def test_update_dependencies_create_file(
        site,
        mock_dep_graph_init, expected_children, expected_parents,
        monkeypatch
        ):
    monkeypatch.setattr(
            staticjinja.DepGraph,
            '__init__',
            mock_dep_graph_init
            )
    site.dep_graph = DepGraph(site)

    # We create a file template5.html depending on data1
    def update_file_dep(s, f):
        if f == 'template5.html':
            return set(['data1'])
        else:
            return expected_parents[f]

    monkeypatch.setattr(
            staticjinja.Site,
            'get_file_dep',
            update_file_dep
            )

    site.dep_graph.update('template5.html')

    new_expected_parents = deepcopy(expected_parents)
    new_expected_parents.update(
            {'template5.html': set(['data1'])}
            )
    assert site.dep_graph.parents == new_expected_parents

    new_expected_children = deepcopy(expected_children)
    new_expected_children.update(
            {'data1': set(['_partial1.html', 'template5.html'])}
            )
    assert site.dep_graph.children == new_expected_children


def test_render_template(site, build_path):
    site.render_template(site.get_template('template1.html'))
    template1 = build_path.join("template1.html")
    assert template1.check()
    assert template1.read() == "Partial 1\nTemplate 1"


def test_render_nested_template(site, build_path):
    site.render_template(site.get_template('sub/template3.html'))
    template3 = build_path.join('sub').join("template3.html")
    assert template3.check()
    assert template3.read() == "Test 3\nPartial 2"


def test_render_templates(site, build_path):
    site.render_templates(site.templates)
    template1 = build_path.join("template1.html")
    assert template1.check()
    assert template1.read() == "Partial 1\nTemplate 1"
    template3 = build_path.join('sub').join("template3.html")
    assert template3.check()
    assert template3.read() == "Test 3\nPartial 2"


def test_build(site):
    templates = []

    def fake_site(template, context=None, filepath=None):
        templates.append(template)

    site.render_template = fake_site
    site.render()
    assert templates == list(site.templates)


def test_use_reloader_calls_watch(reloader, site, monkeypatch):
    mock_watch = mock.Mock()
    monkeypatch.setattr(Reloader, 'watch', mock_watch)
    site.render(use_reloader=True)
    assert mock_watch.call_count == 1


def test_should_handle(reloader, template_path):
    template1_path = template_path.join("template1.html")
    test4_path = template_path.join("test4.html")

    test4_path.write('')
    assert reloader.should_handle("modified", str(template1_path))
    assert reloader.should_handle("modified", str(test4_path))
    assert reloader.should_handle("created", str(template1_path))
    assert not reloader.should_handle("deleted", str(template1_path))


def test_event_handler_ignored_files(reloader, template_path):
    mock_render_templates = mock.Mock()

    reloader.site.render_templates = mock_render_templates

    ignored_path = str(template_path.join(".ignored.html"))
    reloader.event_handler("modified", ignored_path)
    reloader.event_handler("created", ignored_path)
    reloader.event_handler("moved", ignored_path)
    reloader.event_handler("deleted", ignored_path)
    assert mock_render_templates.call_count == 0


def test_event_handler_modify_template(reloader, template_path):
    mock_render_templates = mock.Mock()

    reloader.site.render_templates = mock_render_templates

    template1_path = str(template_path.join("template1.html"))
    reloader.event_handler("modified", template1_path)
    mock_render_templates.assert_called_once_with(["template1.html"])


def test_event_handler_modify_partial(reloader, template_path):
    mock_render_templates = mock.Mock()

    reloader.site.render_templates = mock_render_templates

    partial1_path = str(template_path.join("_partial1.html"))
    reloader.event_handler("modified", partial1_path)
    assert set(mock_render_templates.call_args[0][0]) == set(
            ["template1.html", "template2.html"]
            )


def test_event_handler_create_template(reloader, template_path):
    mock_render_templates = mock.Mock()
    reloader.site.render_templates = mock_render_templates

    template_path.join('template6.html').write('Template 6')
    template6_path = str(template_path.join("template6.html"))
    reloader.event_handler("created", template6_path)
    mock_render_templates.assert_called_once_with(["template6.html"])


def test_event_handler_static(reloader, template_path):
    found_files = []

    def fake_copy_static(files):
        found_files.extend(files)

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
    assert site.is_ignored('.bar/index.html')


def test_ignored_file_in_nested_directory_is_ignored(site):
    assert site.is_ignored('foo/.bar/index.html')


def test_partial_file_is_partial(site):
    assert site.is_partial('_index.html')


def test_regular_file_is_not_partial(site):
    assert not site.is_partial('index.html')


def test_partial_file_in_directory_is_partial(site):
    assert site.is_partial('_bar/index.html')


def test_partial_file_in_nested_directory_is_partial(site):
    assert site.is_partial('foo/_bar/index.html')


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
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
@mock.patch('staticjinja.cli.staticjinja.make_site')
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
@mock.patch('staticjinja.cli.staticjinja.make_site')
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
