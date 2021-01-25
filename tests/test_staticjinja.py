import os

from pytest import fixture, mark, raises

from staticjinja import Site, Reloader


@fixture
def root_path(tmpdir):
    return tmpdir


@fixture
def template_path(root_path):
    return root_path.mkdir("templates")


@fixture
def build_path(root_path):
    return root_path.mkdir("build")


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


def test_get_dependencies(site):
    filename = 'test.txt'
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


def test_with_reloader(site):
    watch_called = False

    def fake_watch(self):
        nonlocal watch_called
        watch_called = True

    Reloader.watch = fake_watch
    site.render(use_reloader=True)
    assert watch_called


def test_should_handle(reloader, root_path, template_path):
    exists = template_path / "template1.html"
    DNE = template_path / "DNE.html"
    outside_searchpath = root_path / "file.txt"
    assert reloader.should_handle("created", str(exists))
    assert reloader.should_handle("modified", str(exists))
    assert not reloader.should_handle("deleted", str(exists))
    assert not reloader.should_handle("modified", str(DNE))
    assert not reloader.should_handle("modified", str(outside_searchpath))


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


is_ignored_cases = [
    ('index.html', False),
    ('.index.html', True),
    ('_index.html', False),
    ('normal/index.html', False),
    ('.dotted/index.html', True),
    ('normal/.index.html', True),
    ('_undered/index.html', False),
    ('undered/_index.html', False),
    ('normal/normal2/index.html', False),
    ('.dotted/normal/index.html', True),
    ('normal/.dotted/index.html', True),
    ('normal/normal2/.index.html', True),
    ('_undered/normal/index.html', False),
    ('normal/_undered/index.html', False),
    ('normal/normal2/_index.html', False),
]


@mark.parametrize("name, expected", is_ignored_cases)
def test_is_ignored(site, name, expected):
    assert site.is_ignored(name) == expected


is_partial_cases = [
    ('index.html', False),
    ('.index.html', False),
    ('_index.html', True),
    ('normal/index.html', False),
    ('.dotted/index.html', False),
    ('normal/.index.html', False),
    ('_undered/index.html', True),
    ('undered/_index.html', True),
    ('normal/normal2/index.html', False),
    ('.dotted/normal/index.html', False),
    ('normal/.dotted/index.html', False),
    ('normal/normal2/.index.html', False),
    ('_undered/normal/index.html', True),
    ('normal/_undered/index.html', True),
    ('normal/normal2/_index.html', True),
]


@mark.parametrize("name, expected", is_partial_cases)
def test_is_partial(site, name, expected):
    assert site.is_partial(name) == expected
