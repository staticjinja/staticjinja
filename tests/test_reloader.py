try:
    import unittest.mock as mock
except ImportError:
    import mock

from pytest import fixture
import os.path

from staticjinja.reloader import Reloader
from staticjinja.easywatch import MODIFIED, CREATED, DELETED, MOVED
from staticjinja.sources import SourceNotFoundError, TEMPLATE_FLAVOR


@fixture
def searchpath():
    return 'templates'


@fixture
def builder():
    return mock.Mock()


@fixture
def logger():
    return mock.Mock()


@fixture
def env():
    return mock.Mock()


datapaths = ['data']
staticpaths = ['static']


class FakeSources(object):
    def __init__(self):
        self.sources = []


@fixture
def reloader(builder, searchpath, logger, env):
    return Reloader(
            searchpath, datapaths, staticpaths,
            env, FakeSources(), builder, logger)


def test_should_handle_isfile(reloader, searchpath, monkeypatch):
    template1_path = os.path.join(searchpath, "template1.html")

    monkeypatch.setattr('os.path.isfile', lambda x: True)
    assert reloader.should_handle(MODIFIED, template1_path)
    assert reloader.should_handle(CREATED, template1_path)
    assert reloader.should_handle(DELETED, template1_path)
    assert not reloader.should_handle(MOVED, template1_path)


def test_should_handle_nofile(reloader, searchpath, monkeypatch):
    monkeypatch.setattr('os.path.isfile', lambda x: False)
    dir_path = os.path.join(searchpath, "sub/")
    assert not reloader.should_handle(MODIFIED, dir_path)


def test_event_handler_should_not_handle(reloader, template1, partial1):
    reloader.sources.update_dep_graph = mock.Mock()
    reloader.should_handle = lambda x, y: False
    reloader.event_handler('modified', 'templates/template1.html')
    assert not reloader.sources.update_dep_graph.call_count
    assert not reloader.builder.handle_sources.call_count


def test_event_handler_modified(reloader, template1, partial1):
    sources = reloader.sources
    sources.source_from_name = lambda x: template1
    sources.get_dependencies = lambda x: partial1
    sources.update_dep_graph = mock.Mock()

    reloader.should_handle = lambda x, y: True
    reloader.event_handler('modified', 'templates/template1.html')
    sources.update_dep_graph.assert_called_once_with(template1)
    reloader.builder.handle_sources.assert_called_once_with(partial1)
    reloader.logger.info.assert_called_once_with('modified template1.html')


def test_event_handler_created(reloader):
    sources = reloader.sources
    sources.update_dep_graph = mock.Mock()
    mock_classify = mock.Mock()
    mock_classify.return_value = TEMPLATE_FLAVOR
    sources.classify = mock_classify
    sources.add_source = mock.Mock()

    def sfn(name):
        raise SourceNotFoundError('Source not found')
    sources.source_from_name = sfn

    mock_source = mock.Mock()
    sources.get_dependencies = lambda x: [mock_source]

    reloader.should_handle = lambda x, y: True
    reloader.event_handler('created', 'templates/template7.html')

    assert sources.add_source.call_count
    reloader.builder.handle_sources.assert_called_once_with([mock_source])
    reloader.logger.info.assert_called_once_with('created template7.html')


def test_event_handler_deleted(monkeypatch, reloader, template1):
    sources = reloader.sources
    sources.remove_source = mock.Mock()
    sources.source_from_name = lambda x: template1
    monkeypatch.setattr('os.path.isfile', lambda x: True)
    reloader.event_handler('deleted', 'templates/template1.html')
    sources.remove_source.assert_called_once_with(template1)


def test_event_handler_deleted_phantom(monkeypatch, reloader):
    sources = reloader.sources
    sources.remove_source = mock.Mock()

    def raiser(x):
        raise SourceNotFoundError
    sources.source_from_name = raiser
    monkeypatch.setattr('os.path.isfile', lambda x: True)
    reloader.event_handler('deleted', 'templates/template666.html')
    assert not sources.remove_source.call_count


def test_event_handler_4913(reloader):
    sources = reloader.sources
    sources.update_dep_graph = mock.Mock()
    reloader.event_handler('created', '4913')
    reloader.event_handler('modified', '4913')
    assert not sources.update_dep_graph.call_count
    assert not reloader.builder.handle_sources.call_count


def test_watch(reloader, monkeypatch):
    mock_watch = mock.Mock()
    monkeypatch.setattr('staticjinja.easywatch.watch', mock_watch)

    reloader.watch()
    mock_watch.assert_called_once_with(
            reloader.searchpath, reloader.event_handler)
