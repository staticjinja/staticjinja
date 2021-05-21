"""Fixtures and code common to many tests."""

import pytest

import staticjinja


@pytest.fixture
def root_path(tmp_path):
    return tmp_path


@pytest.fixture
def template_path(root_path):
    p = root_path.joinpath("templates")
    p.mkdir()
    return p


@pytest.fixture
def build_path(root_path):
    p = root_path.joinpath("build")
    p.mkdir()
    return p


@pytest.fixture
def site(template_path, build_path):
    template_path.joinpath(".ignored1.html").write_text("Ignored 1")
    template_path.joinpath("_partial1.html").write_text("Partial 1")
    template_path.joinpath("template1.html").write_text("Test 1")
    template_path.joinpath("template2.html").write_text("Test 2")
    sub = template_path.joinpath("sub")
    sub.mkdir()
    sub.joinpath("template3.html").write_text("Test {{b}}")
    sub1 = template_path.joinpath("sub1")
    sub1.mkdir()
    sub1.joinpath(".ignored2.html").write_text("Ignored 2")
    sub2 = template_path.joinpath("sub2")
    sub2.mkdir()
    sub2.joinpath("_partial2.html").write_text("Partial 2")
    ignoreds = template_path.joinpath(".ignoreds")
    ignoreds.mkdir()
    ignoreds.joinpath("ignored3.html").write_text("Ignored 3")
    partials = template_path.joinpath("_partials")
    partials.mkdir()
    partials.joinpath("partial3.html").write_text("Partial 3")
    template_path.joinpath("template4.html").write_text("Test {{b}} and {{c}}")
    static_css = template_path.joinpath("static_css")
    static_css.mkdir()
    static_css.joinpath("hello.css").write_text("a { color: blue; }")
    static_js = template_path.joinpath("static_js")
    static_js.mkdir()
    static_js.joinpath("hello.js").write_text("var a = function () {return true};")
    template_path.joinpath("favicon.ico").write_text("Fake favicon")
    contexts = [
        ("template2.html", lambda t: {"a": 1}),
        (".*template3.html", lambda: {"b": 3}),
        ("template4.html", {"b": 4, "c": 5}),
        (".*[4-9].html", {"c": 6}),
    ]
    rules = [
        ("template2.html", lambda env, t, a: None),
    ]
    return staticjinja.Site.make_site(
        searchpath=str(template_path),
        outpath=str(build_path),
        contexts=contexts,
        rules=rules,
    )
