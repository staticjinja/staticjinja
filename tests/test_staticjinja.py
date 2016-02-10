try:
    import unittest.mock as mock
except ImportError:
    import mock

from pytest import fixture
import logging
import os

from staticjinja.staticjinja import Site, coerce_to_absolute_path
import staticjinja.staticjinja as staticjinja


@fixture
def reloader():
    return mock.Mock()


@fixture
def builder():
    return mock.Mock()


@fixture
def logger():
    return mock.Mock()


@fixture
def env():
    return mock.Mock()


@fixture
def site(env, builder, reloader, logger):
    return Site(
            env, builder, reloader, logger,
            searchpath='tplts', outpath='out')


def test_make_site_still_exists():
    # for backward compatibility
    assert hasattr(staticjinja, 'make_site')


class FakeFileSystemLoader(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __eq__(self, other):
        return self.kwargs == other.kwargs


class FakeEnv(object):
    def __init__(self, **kwargs):
        self.filters = {}
        self.kwargs = kwargs


def test_make_jinja2_env_with_filters_and_kwargs(monkeypatch):
    monkeypatch.setattr('jinja2.FileSystemLoader', FakeFileSystemLoader)
    monkeypatch.setattr('jinja2.Environment', FakeEnv)

    my_filter = mock.Mock()
    env = Site.make_jinja2_env(
            {'a': 1},
            'tpltes',
            'utf16',
            'markdown',
            {'to_one': my_filter})

    fsl = FakeFileSystemLoader(searchpath='tpltes', encoding='utf16')
    assert env.kwargs == {
            'extensions': 'markdown',
            'loader': fsl,
            'a': 1,
            'keep_trailing_newline': True}
    assert env.filters == {'to_one': my_filter}


def test_make_jinja2_env_with_no_filters_or_kwargs(monkeypatch):
    monkeypatch.setattr('jinja2.FileSystemLoader', FakeFileSystemLoader)
    monkeypatch.setattr('jinja2.Environment', FakeEnv)

    env = Site.make_jinja2_env(
            None,
            'tpltes',
            'utf16',
            'markdown',
            None)

    fsl = FakeFileSystemLoader(searchpath='tpltes', encoding='utf16')
    assert env.kwargs == {
            'extensions': 'markdown',
            'loader': fsl,
            'keep_trailing_newline': True}
    assert env.filters == {}


def test_make_logger():
    # Here we only make sure logger will be able to output info to something.
    logger = Site.make_logger()
    assert logger.level == logging.INFO
    assert logger.handlers


def test_render(site, reloader, builder, logger):
    site.render()
    assert builder.render.call_count == 1

    site.render(use_reloader=True)
    assert builder.render.call_count == 2
    assert reloader.watch.call_count == 1
    assert logger.info.call_count


def test_repr(site):
    assert 'tplts' in repr(site)
    assert 'out' in repr(site)


def test_coerce_to_absolute_path_absolute():
    assert coerce_to_absolute_path('/home/me/site/') == '/home/me/site/'


def test_coerce_to_absolute_path_relative():
    assert coerce_to_absolute_path('site') == os.path.join(
            os.getcwd(),
            'site')


def test_make_site(monkeypatch):
    # In this unit test we only make sure all ingredients are called.
    # Verifying that ingredients are properly mixed is left for integration
    # tests.
    mctap = mock.Mock()
    monkeypatch.setattr(staticjinja, 'coerce_to_absolute_path', mctap)

    mje = mock.Mock()
    Site.make_jinja2_env = mje

    ml = mock.Mock()
    Site.make_logger = ml

    ms = mock.Mock()
    monkeypatch.setattr(staticjinja, 'SourceManager', ms)

    mb = mock.Mock()
    monkeypatch.setattr(staticjinja, 'Builder', mb)

    mr = mock.Mock()
    monkeypatch.setattr(staticjinja, 'Reloader', mr)

    Site.make_site()

    assert mctap.call_count
    assert mje.call_count
    assert ml.call_count
    assert ms.make_sources.call_count
    assert mb.call_count
    assert mr.call_count
