import os

from pytest import fixture, raises

from staticjinja import make_renderer


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
    rules = [('test2.html', None),]
    return make_renderer(searchpath=str(tmpdir), contexts=contexts, rules=rules)


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
    assert renderer.get_rule('test2.html') is None


def test_get_dependencies(renderer, filename):
    renderer.get_template = lambda x: filename
    assert renderer.get_dependencies(".%s" % filename) == []
    assert (list(renderer.get_dependencies("_%s" % filename))
            == list(renderer.templates))
    assert (list(renderer.get_dependencies("%s" % filename)) == [filename])
