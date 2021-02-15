from pathlib import Path

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
    template_path.join(".ignored1.html").write("Ignored 1")
    template_path.join("_partial1.html").write("Partial 1")
    template_path.join("template1.html").write("Test 1")
    template_path.join("template2.html").write("Test 2")
    template_path.mkdir("sub").join("template3.html").write("Test {{b}}")
    template_path.mkdir("sub1").join(".ignored2.html").write("Ignored 2")
    template_path.mkdir("sub2").join("_partial2.html").write("Partial 2")
    template_path.mkdir(".ignoreds").join("ignored3.html").write("Ignored 3")
    template_path.mkdir("_partials").join("partial3.html").write("Partial 3")
    template_path.join("template4.html").write("Test {{b}} and {{c}}")
    template_path.mkdir("static_css").join("hello.css").write("a { color: blue; }")
    template_path.mkdir("static_js").join("hello.js").write(
        "var a = function () {return true};"
    )
    template_path.join("favicon.ico").write("Fake favicon")
    contexts = [
        ("template2.html", lambda t: {"a": 1}),
        (".*template3.html", lambda: {"b": 3}),
        ("template4.html", {"b": 4, "c": 5}),
        (".*[4-9].html", {"c": 6}),
    ]
    rules = [
        ("template2.html", lambda env, t, a: None),
    ]
    return Site.make_site(
        searchpath=str(template_path),
        outpath=str(build_path),
        contexts=contexts,
        rules=rules,
    )


@fixture
def reloader(site):
    return Reloader(site)


def test_template_names(site):
    site.staticpaths = ["static_css", "static_js", "favicon.ico"]
    expected_templates = set(
        ["template1.html", "template2.html", "sub/template3.html", "template4.html"]
    )
    assert set(site.template_names) == expected_templates


def test_templates(site):
    expected = list(site.template_names)
    assert [t.name for t in site.templates] == expected


def test_get_context(site):
    assert site.get_context(site.get_template("template1.html")) == {}
    assert site.get_context(site.get_template("template2.html")) == {"a": 1}
    assert site.get_context(site.get_template("sub/template3.html")) == {"b": 3}
    assert site.get_context(site.get_template("template4.html")) == {"b": 4, "c": 5}
    site.mergecontexts = True
    assert site.get_context(site.get_template("template4.html")) == {"b": 4, "c": 6}


def test_get_rule(site):
    with raises(ValueError):
        assert site.get_rule("template1.html")
    assert site.get_rule("template2.html")


def test_get_dependents(monkeypatch, site):
    filename = "test.txt"
    # An ignored file has no dependendents
    assert site.get_dependents(".%s" % filename) == []
    # All the other templates might depend on a partial
    mock_template_names = ["a", "b", "c"]
    monkeypatch.setattr(Site, "template_names", mock_template_names)
    assert list(site.get_dependents("_%s" % filename)) == mock_template_names
    # A normal template only has itself as a dependent
    assert list(site.get_dependents("%s" % filename)) == [filename]
    # TODO maybe test that static files only have themselves as dependents


def test_render_template(site, build_path):
    site.render_template(site.get_template("template1.html"))
    template1 = build_path.join("template1.html")
    assert template1.check()
    assert template1.read() == "Test 1"


def test_render_nested_template(site, build_path):
    site.render_template(site.get_template("sub/template3.html"))
    template3 = build_path.join("sub").join("template3.html")
    assert template3.check()
    assert template3.read() == "Test 3"


def test_render_template_with_env_globals(template_path, build_path):
    """Ensure variables defined in env_globals can be accessed globally."""
    template_name = "template.html"
    template_path.join(template_name).write("<h1>{{greeting}}</h1>")
    site = Site.make_site(
        searchpath=str(template_path),
        outpath=str(build_path),
        env_globals={"greeting": "Hello world!"},
    )
    site.render_template(site.get_template(template_name))
    assert build_path.join(template_name).read() == "<h1>Hello world!</h1>"


def test_render_templates(site, build_path):
    site.render_templates(site.templates)
    template1 = build_path.join("template1.html")
    assert template1.check()
    assert template1.read() == "Test 1"
    template3 = build_path.join("sub").join("template3.html")
    assert template3.check()
    assert template3.read() == "Test 3"


def test_build(monkeypatch, site):
    templates = []

    def fake_render(template, context=None, filepath=None):
        templates.append(template)

    monkeypatch.setattr(site, "render_template", fake_render)

    site.render()
    assert templates == list(site.templates)


def test_with_reloader(monkeypatch, site):
    watch_called = False

    def fake_watch(self):
        nonlocal watch_called
        watch_called = True

    monkeypatch.setattr(Reloader, "watch", fake_watch)

    site.render(use_reloader=True)
    assert watch_called


def test_should_handle(reloader, root_path, template_path):
    exists = template_path / "template1.html"
    DNE = template_path / "DNE.html"
    assert reloader.should_handle("created", str(exists))
    assert reloader.should_handle("modified", str(exists))
    assert not reloader.should_handle("deleted", str(exists))
    assert not reloader.should_handle("modified", str(DNE))


def test_event_handler(monkeypatch, reloader, template_path):
    rendered = []

    def fake_renderer(template, context=None, filepath=None):
        rendered.append(template)

    monkeypatch.setattr(reloader.site, "render_template", fake_renderer)

    template1_path = str(template_path.join("template1.html"))
    reloader.event_handler("modified", template1_path)
    assert rendered == [reloader.site.get_template("template1.html")]


def test_event_handler_static(monkeypatch, reloader, template_path):
    copied_paths = []

    def fake_copy_static(files):
        copied_paths.extend(Path(f) for f in files)

    monkeypatch.setattr(reloader.site, "copy_static", fake_copy_static)

    reloader.site.staticpaths = ["static_css"]
    css_path = Path("static_css") / "hello.css"
    reloader.event_handler("modified", template_path / css_path)
    assert copied_paths == [css_path]


is_ignored_cases = [
    ("index.html", False),
    (".index.html", True),
    ("_index.html", False),
    ("normal/index.html", False),
    (".dotted/index.html", True),
    ("normal/.index.html", True),
    ("_undered/index.html", False),
    ("undered/_index.html", False),
    ("normal/normal2/index.html", False),
    (".dotted/normal/index.html", True),
    ("normal/.dotted/index.html", True),
    ("normal/normal2/.index.html", True),
    ("_undered/normal/index.html", False),
    ("normal/_undered/index.html", False),
    ("normal/normal2/_index.html", False),
]


@mark.parametrize("name, expected", is_ignored_cases)
def test_is_ignored(site, name, expected):
    assert site.is_ignored(name) == expected


is_partial_cases = [
    ("index.html", False),
    (".index.html", False),
    ("_index.html", True),
    ("normal/index.html", False),
    (".dotted/index.html", False),
    ("normal/.index.html", False),
    ("_undered/index.html", True),
    ("undered/_index.html", True),
    ("normal/normal2/index.html", False),
    (".dotted/normal/index.html", False),
    ("normal/.dotted/index.html", False),
    ("normal/normal2/.index.html", False),
    ("_undered/normal/index.html", True),
    ("normal/_undered/index.html", True),
    ("normal/normal2/_index.html", True),
]


@mark.parametrize("name, expected", is_partial_cases)
def test_is_partial(site, name, expected):
    assert site.is_partial(name) == expected
