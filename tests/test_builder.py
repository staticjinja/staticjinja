try:
    import unittest.mock as mock
except ImportError:
    import mock

import os

from pytest import fixture, raises

from staticjinja.builder import Builder
from staticjinja.sources import SourceManager


class FakeStream(object):
    def __init__(self, env, **context):
        self.env = env
        self.context = context

    def dump(self, path, encoding):
        self.env.dump_calls.append((self.context, path, encoding))


class FakeTemplate(object):
    def __init__(self, env, name):
        self.mock_stream = mock.Mock
        self.name = name
        self.env = env

    def stream(self, **kwargs):
        return FakeStream(self.env, **kwargs)


class FakeEnvironment(object):
    def __init__(self):
        self.get_template_calls = []
        self.dump_calls = []

    def get_template(self, filename):
        self.get_template_calls.append(filename)
        return FakeTemplate(self, filename)


def test_fake_environment():
    env = FakeEnvironment()
    ft = env.get_template('template.html')
    assert env.get_template_calls == ['template.html']
    assert ft.name == 'template.html'


def test_fake_template():
    env = FakeEnvironment()
    ft = FakeTemplate(env, 'template.html')
    ft.stream(a=1, b=2).dump('/out/path/', 'utf8')
    assert env.dump_calls == [({'a': 1, 'b': 2}, '/out/path/', 'utf8')]


@fixture
def fake_env():
    return FakeEnvironment()


@fixture
def fake_logger():
    return mock.Mock()


@fixture
def sources(fake_env, template1):
    return SourceManager([template1], fake_env, None)


@fixture
def builder(fake_env, fake_logger, template1, sources):
    contexts = [('template2.html', lambda t: {'a': 1}),
                ('.*template3.html', lambda: {'b': 3}),
                ('template4.html', {'b': 4, 'c': 5}),
                ('.*[4-9].html', {'c': 6})]
    rules = [('template2.html', lambda env, t, a: None), ]
    builder = Builder(
            fake_env,
            sources,
            'templates',
            '',
            'utf8',
            fake_logger,
            contexts=contexts,
            rules=rules,
            mergecontexts=False)
    builder._ensure_dir = mock.Mock()
    return builder


def test_get_template(builder, template1, fake_env):
    builder.get_template(template1)
    assert fake_env.get_template_calls == ['template1.html']


def test_get_context(builder, template1, template2, template3, template4):
    assert builder.get_context(template1) == {}
    assert builder.get_context(template2) == {'a': 1}
    assert builder.get_context(template3) == {'b': 3}
    assert builder.get_context(template4) == {'b': 4, 'c': 5}


def test_get_context_merge(builder, template4):
    builder.mergecontexts = True
    assert builder.get_context(template4) == {'b': 4, 'c': 6}


def test_get_rule(builder, template1, template2):
    with raises(ValueError):
        assert builder.get_rule(template1)
    assert builder.get_rule(template2)


def test_ensure_dir(monkeypatch):
    mock_makedirs = mock.Mock()
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)
    builder = Builder(
            None,
            None,
            None,
            'build_dir',
            None,
            None)

    mock_exists_false = mock.Mock(return_value=False)
    monkeypatch.setattr(os.path, 'exists', mock_exists_false)
    builder._ensure_dir('sub/template.html')
    mock_makedirs.assert_called_once_with('build_dir/sub')

    mock_exists_true = mock.Mock(return_value=True)
    monkeypatch.setattr(os.path, 'exists', mock_exists_true)
    builder._ensure_dir('sub/template.html')
    assert mock_makedirs.call_count == 1

    builder._ensure_dir('template.html')
    assert mock_makedirs.call_count == 1


def test_render_template(builder, template2, template3):
    builder.render_template(template2, {'b': 2})
    builder.render_template(template2, {'a': 1}, filepath='outfile.html')
    builder.render_template(template3, {'b': 3})
    assert builder._env.dump_calls == [
            ({'b': 2}, 'template2.html', 'utf8'),
            ({'a': 1}, 'outfile.html', 'utf8'),
            ({'b': 3}, 'sub/template3.html', 'utf8'),
            ]


def test_copy_static(builder, static, monkeypatch):
    mock_copy2 = mock.Mock()
    monkeypatch.setattr('shutil.copy2', mock_copy2)
    builder.copy_static(static)

    mock_copy2.assert_called_once_with(
            'templates/images/logo.png',
            'images/logo.png')

    logger = builder.logger
    logger.info.assert_called_once_with(
            "Copying images/logo.png to images/logo.png.")


def test_handle_sources(builder, template1, template2):
    mock_handler = mock.Mock()
    builder.handle_source = mock_handler
    builder.handle_sources([template1, template2])
    assert mock_handler.mock_calls == [
            mock.call(template1, None),
            mock.call(template2, None)]


def test_handle_source_handles_templates(builder, template1, template2):
    mock_render_template = mock.Mock()
    builder.render_template = mock_render_template
    mock_rule = mock.Mock()

    builder.handle_source(template1)
    builder.rules = [
            ('template2.html', mock_rule),
            ('template1.html', mock_rule)]
    builder.handle_source(template1)
    builder.handle_source(template2)
    mock_render_template.assert_called_once_with(template1, {}, None)
    assert mock_rule.mock_calls == [
            mock.call(builder, template1),
            mock.call(builder, template2, a=1)]


def test_handle_source_handles_static(builder, static):
    mock_copy_static = mock.Mock()
    builder.copy_static = mock_copy_static

    builder.handle_source(static)
    mock_copy_static.assert_called_once_with(static)


def test_handle_source_ignores_partial(builder, partial1):
    mock_copy_static = mock.Mock()
    builder.copy_static = mock_copy_static
    mock_render_template = mock.Mock()
    builder.render_template = mock_render_template

    builder.handle_source(partial1)
    assert mock_copy_static.call_count == 0
    assert mock_render_template.call_count == 0


def test_render(builder):
    mock_handle_sources = mock.Mock()
    builder.handle_sources = mock_handle_sources

    builder.render()
    mock_handle_sources.assert_called_once_with(builder.sources)
