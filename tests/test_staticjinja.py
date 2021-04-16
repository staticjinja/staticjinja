from pytest import mark, raises

from staticjinja import Site, Reloader


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
    template1 = build_path.joinpath("template1.html")
    assert template1.read_text() == "Test 1"


def test_render_nested_template(site, build_path):
    site.render_template(site.get_template("sub/template3.html"))
    template3 = build_path.joinpath("sub", "template3.html")
    assert template3.read_text() == "Test 3"


def test_render_template_with_env_globals(template_path, build_path):
    """Ensure variables defined in env_globals can be accessed globally."""
    template_name = "template.html"
    template_path.joinpath(template_name).write_text("<h1>{{greeting}}</h1>")
    site = Site.make_site(
        searchpath=str(template_path),
        outpath=str(build_path),
        env_globals={"greeting": "Hello world!"},
    )
    site.render_template(site.get_template(template_name))
    assert build_path.joinpath(template_name).read_text() == "<h1>Hello world!</h1>"


def test_render_templates(site, build_path):
    site.render_templates(site.templates)
    template1 = build_path.joinpath("template1.html")
    assert template1.read_text() == "Test 1"
    template3 = build_path.joinpath("sub", "template3.html")
    assert template3.read_text() == "Test 3"


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
