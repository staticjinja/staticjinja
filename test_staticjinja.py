import os

from pytest import fixture, raises

from staticjinja import make_renderer, Reloader


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
def renderer(template_path, build_path):
    template_path.join('test1.html').write('Test 1')
    template_path.join('test2.html').write('Test 2')
    template_path.mkdir('sub').join('test3.html').write('Test 3')
    contexts = [('test2.html', lambda t: {'a': 1}),
                ('.*test3.html', lambda: {'b': 1}),]
    rules = [('test2.html', lambda env, t, a: None),]
    return make_renderer(searchpath=str(template_path),
                         outpath=str(build_path),
                         contexts=contexts,
                         rules=rules)


@fixture
def reloader(renderer):
    return Reloader(renderer)


def test_template_names(renderer):
    assert set(renderer.template_names) == {'test1.html',
                                            'test2.html',
                                            'sub/test3.html'}


def test_templates(renderer):
    assert [t.name for t in renderer.templates]  == list(renderer.template_names)


def test_get_context(renderer):
    assert renderer.get_context(renderer.get_template("test1.html")) == {}
    assert renderer.get_context(renderer.get_template("test2.html")) == {'a': 1}
    assert renderer.get_context(renderer.get_template("sub/test3.html")) == {'b': 1}


def test_get_rule(renderer):
    with raises(ValueError):
        assert renderer.get_rule('test1.html')
    assert renderer.get_rule('test2.html')


def test_get_dependencies(renderer, filename):
    renderer.get_template = lambda x: filename
    assert renderer.get_dependencies(".%s" % filename) == []
    assert (list(renderer.get_dependencies("_%s" % filename))
            == list(renderer.templates))
    assert (list(renderer.get_dependencies("%s" % filename)) == [filename])


def test_render_template(renderer, build_path):
    template = renderer.get_template('test1.html')
    out = build_path.join("test1.html")
    renderer.render_template(template)
    assert out.check()
    assert out.read() == "Test 1"


def test_render_nested_template(renderer, build_path):
    template = renderer.get_template('sub/test3.html')
    out = build_path.join('sub').join("test3.html")
    renderer.render_template(template)
    assert out.check()
    assert out.read() == "Test 3"


def test_render_templates(renderer):
    templates = []
    renderer.render_template = lambda t: templates.append(t)
    renderer.render_templates(renderer.templates)
    assert templates == list(renderer.templates)


def test_run(renderer):
    templates = []
    renderer.render_template = lambda t: templates.append(t)
    renderer.run()
    assert templates == list(renderer.templates)


def test_with_reloader(reloader, renderer):
    reloader.watch_called = False
    def watch(self):
        reloader.watch_called = True
    Reloader.watch = watch
    renderer.run(use_reloader=True)
    assert reloader.watch_called


def test_should_handle(reloader, template_path):
    test1_path = str(template_path.join("test1.html"))
    test4_path = str(template_path.join("test4.html"))
    assert reloader.should_handle("modified", test1_path)
    assert reloader.should_handle("modified", test4_path)
    assert not reloader.should_handle("created", test1_path)


def test_event_handler(reloader, template_path):
    templates = []
    reloader.renderer.render_template = lambda t: templates.append(t)
    test1_path = str(template_path.join("test1.html"))
    reloader.event_handler("modified", test1_path)
    assert templates == [reloader.renderer.get_template("test1.html")]
