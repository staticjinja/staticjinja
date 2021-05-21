from pathlib import Path

import pytest

import staticjinja


@pytest.fixture
def reloader(site):
    return staticjinja.Reloader(site)


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
