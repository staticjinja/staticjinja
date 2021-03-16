"""Fixtures and code common to many tests."""

import pytest

import staticjinja


@pytest.fixture
def root_path(tmpdir):
    return tmpdir


@pytest.fixture
def template_path(root_path):
    return root_path.mkdir("templates")


@pytest.fixture
def build_path(root_path):
    return root_path.mkdir("build")


@pytest.fixture
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
    return staticjinja.Site.make_site(
        searchpath=str(template_path),
        outpath=str(build_path),
        contexts=contexts,
        rules=rules,
    )
