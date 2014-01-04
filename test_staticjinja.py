import os

from pytest import fixture, raises

from staticjinja import make_renderer, Reloader


@fixture
def filename():
    return "test.txt"


@fixture
def renderer(tmpdir):
    tmpdir.join('test1.html').write('')
    tmpdir.join('test2.html').write('')
    tmpdir.join('test3.html').write('')
    contexts = [('test2.html', lambda t: {'a': 1}),
                ('test3.html', lambda: {'b': 1}),]
    rules = [('test2.html', lambda env, t, a: None),]
    return make_renderer(searchpath=str(tmpdir), contexts=contexts, rules=rules)


@fixture
def reloader(renderer):
    return Reloader(renderer)


def test_template_names(renderer):
    assert list(renderer.template_names) == ['test1.html',
                                             'test2.html',
                                             'test3.html']


def test_templates(renderer):
    assert [t.name for t in renderer.templates]  == list(renderer.template_names)


def test_get_context(renderer):
    assert renderer.get_context(renderer.get_template("test1.html")) == {}
    assert renderer.get_context(renderer.get_template("test2.html")) == {'a': 1}
    assert renderer.get_context(renderer.get_template("test3.html")) == {'b': 1}


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


def test_render_template(renderer):
    template = renderer.get_template('test2.html')
    renderer.render_template(template)

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


def test_should_handle(reloader, tmpdir):
    test1_path = str(tmpdir.join("test1.html"))
    test4_path = str(tmpdir.join("test4.html"))
    assert reloader.should_handle("modified", test1_path)
    assert reloader.should_handle("modified", test4_path)
    assert not reloader.should_handle("created", test1_path)


def test_event_handler(reloader, tmpdir):
    templates = []
    reloader.renderer.render_template = lambda t: templates.append(t)
    test1_path = str(tmpdir.join("test1.html"))
    reloader.event_handler("modified", test1_path)
    assert templates == [reloader.renderer.get_template("test1.html")]
