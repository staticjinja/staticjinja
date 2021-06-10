import os
from pathlib import Path

from pytest import mark, raises, warns

from staticjinja import Site, Reloader
import staticjinja


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


def test_path_absolute(root_path):
    expected = "/absolute/path/to/templates"
    s = Site.make_site(searchpath=expected)
    # On windows, ignore the drive (eg "C:") prefix.
    drive, searchpath = os.path.splitdrive(s.searchpath)
    assert Path(searchpath) == Path(expected)


def test_path_relative_warning(root_path):
    """If a relative path is given to staticjinja, it will try to infer the root
    of the project. If staticjinja was invoked from a python build script,
    then SJ will infer the project root is the directory of that build script.
    This is behavior is deprecated in #149, in the future pathlib.Path.cwd() will
    always be used.

    If someone *is* relying upon this deprecated behavior, (ie they are
    supplying relative paths, and build_script_dir!=pathlib.Path.cwd(), then they
    *should* get a warning.
    """
    entry_point_dir = staticjinja.staticjinja.get_build_script_directory()
    print(f"entry_point_dir={entry_point_dir}")
    print(f"CWD={Path.cwd()}")
    # Sanity check that we are set up properly to actually test this behavior
    assert Path.cwd() != Path(entry_point_dir)

    searchpath = "relative/path/to/templates"
    with warns(FutureWarning):
        s = Site.make_site(searchpath=searchpath)
    assert Path(s.searchpath) == entry_point_dir / searchpath


def test_path_relative_no_warning(root_path):
    """See sibling test for more info.

    If someone *is not* relying upon this deprecated behavior, (ie they are
    supplying relative paths, but build_script_dir==pathlib.Path.cwd(), then they
    *should not* get a warning.
    """
    entry_point_dir = staticjinja.staticjinja.get_build_script_directory()
    print(f"entry_point_dir={entry_point_dir}")
    try:
        original_cwd = Path.cwd()
        os.chdir(entry_point_dir)
        # Sanity check that we are set up properly to actually test this behavior
        assert Path.cwd() == Path(entry_point_dir)

        # This should not give a warning or anything
        searchpath = "relative/path/to/templates"
        s = Site.make_site(searchpath=searchpath)
        assert Path(s.searchpath) == Path.cwd() / searchpath
    finally:
        os.chdir(original_cwd)


def test_followlinks(root_path):
    # Set up a directory that is outside the searchpath
    # and put a file in it
    outside_dir = root_path / "outside"
    os.mkdir(outside_dir)
    outside_file = outside_dir / "outside.html"
    outside_file.write_text("I'm some text!")

    # Create our searchpath directory, and then create both a
    # symlink to a file, and a symlink to a directory
    searchpath = root_path / "src"
    os.mkdir(searchpath)
    sym_file = searchpath / "symlink_to_file"
    os.symlink(outside_file, sym_file)
    sym_dir = searchpath / "symlink_to_dir"
    os.symlink(outside_dir, sym_dir)

    # Regardless of what we set `followlinks`, the `os.walk()`
    # call that underlies jinja's FileSystemLoader will always
    # resolve symlinks that point to files. That's just how
    # `os.walk()` works.
    # Here we don't resolve directory symlinks.
    s = Site.make_site(searchpath=searchpath, followlinks=False)
    assert s.template_names == ["symlink_to_file"]
    # Here, we resolve both file and directory symlinks.
    s = Site.make_site(searchpath=searchpath, followlinks=True)
    assert sorted(s.template_names) == sorted(
        ["symlink_to_file", "symlink_to_dir/outside.html"]
    )

    # If the searchpath itself is a symlink, then we always resolve it.
    # This again emerges from the behavior of `os.walk()`, where `os.walk(abc)`
    # always resolves `abc` (the root directory of the walk), regardless of
    # `followlinks`.
    sym_searchpath = root_path / "sym_src"
    os.symlink(outside_dir, sym_searchpath)
    s = Site.make_site(searchpath=sym_searchpath, followlinks=True)
    assert s.template_names == ["outside.html"]
    s = Site.make_site(searchpath=sym_searchpath, followlinks=False)
    assert s.template_names == ["outside.html"]
