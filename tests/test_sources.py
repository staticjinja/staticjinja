try:
    import unittest.mock as mock
except ImportError:
    import mock

import pytest
from pytest import fixture

from staticjinja.dep_graph import DepGraph
from staticjinja.sources import (
        DATA_FLAVOR, TEMPLATE_FLAVOR, PARTIAL_FLAVOR,
        STATIC_FLAVOR, IGNORED_FLAVOR,
        SourceManager, Source, dep_graph_from_sources, SourceNotFoundError)


@fixture
def fake_env():
    env = mock.MagicMock()
    env.list_templates.return_value = [
            'images/logo.png', '.conf',
            '_partial1.html', '_partial2.html',
            'data1', 'data2', 'data/data3',
            'template1.html', 'template2.html',
            'sub/template3.html', 'template4.html']
    return env


@fixture
def parents(
        data1, data2, data3,
        partial1, partial2,
        template1, template2, template3, template4):
    return {
            partial2: set([data3]),
            partial1: set([data2, data1, partial2]),
            data1: set(),
            data2: set(),
            data3: set(),
            template1: set([partial1]),
            template2: set([partial1, partial2]),
            template3: set([partial2]),
            template4: set([data3]),
            }


@fixture
def dep_graph(parents):
    return DepGraph.from_parents(parents)


@fixture
def sources(parents, static, ignored, dep_graph):
    return SourceManager(
            list(parents.keys())+[static]+[ignored],
            fake_env,
            dep_graph)


@fixture
def data1():
    return Source(
            'data1',
            DATA_FLAVOR,
            None)


def test_source_file_hash(data1):
    assert hash(data1) == hash('data1')


def test_source_file_repr(data1):
    assert str(data1) == 'data1'


def classify(filename):
    return SourceManager.classify(
            filename,
            datapaths=['data1', 'data2', 'data'],
            staticpaths=['logo.png', 'images'])


def test_ignored_file_is_ignored():
    assert classify('.index.html') == IGNORED_FLAVOR


def test_regular_file_is_not_ignored():
    assert not classify('index.html') == IGNORED_FLAVOR


def test_ignored_file_in_directory_is_ignored():
    assert classify('.bar/index.html') == IGNORED_FLAVOR


def test_ignored_file_in_nested_directory_is_ignored():
    assert classify('foo/.bar/index.html') == IGNORED_FLAVOR


def test_partial_file_is_partial():
    assert classify('_index.html') == PARTIAL_FLAVOR


def test_regular_file_is_not_partial():
    assert not classify('index.html') == PARTIAL_FLAVOR


def test_partial_file_in_directory_is_partial():
    assert classify('_bar/index.html') == PARTIAL_FLAVOR


def test_partial_file_in_nested_directory_is_partial():
    assert classify('foo/_bar/index.html') == PARTIAL_FLAVOR


def test_static_file_is_static():
    assert classify('logo.png') == STATIC_FLAVOR


def test_static_file_in_directory_is_static():
    assert classify('images/logo.png') == STATIC_FLAVOR


def test_static_file_in_nested_directory_is_static():
    assert classify('images/large/big.png') == STATIC_FLAVOR


def test_regular_file_is_not_static():
    assert not classify('index.html') == STATIC_FLAVOR
    assert not classify('index.html') == STATIC_FLAVOR


def test_data_file_is_data():
    assert classify('data1') == DATA_FLAVOR


def test_data_file_in_directory_is_data():
    assert classify('data/data1') == DATA_FLAVOR


def test_data_file_in_nested_directory_is_data():
    assert classify('data/sub/data2') == DATA_FLAVOR


def test_regular_file_is_template():
    assert classify('index.html') == TEMPLATE_FLAVOR


def test_classify_without_staticpaths():
    flavor = SourceManager.classify('logo.png', datapaths=['data'])
    assert flavor != STATIC_FLAVOR


def test_classify_without_datapaths():
    flavor = SourceManager.classify('data1', staticpaths=['images'])
    assert flavor != DATA_FLAVOR


def test_source_file_eq(data1, data2):
    assert data1 == data1
    assert not data1 == data2


def test_source_file_iter(sources):
    assert list(iter(sources)) == sources.sources


def test_source_file_get_dep(
        fake_env, monkeypatch,
        data1, data2, data3, partial2):
    def fake_find_ref(x):
        return ['_partial2.html']
    monkeypatch.setattr('jinja2.meta.find_referenced_templates', fake_find_ref)

    # We don't use the partial1 fixture since we want to test get_dep
    partial1 = Source(
                '_partial1.html',
                PARTIAL_FLAVOR,
                fake_env,
                extra_deps=['data1', 'data2']
                )

    deps = partial1.get_dep([data1, data2, data3, partial1, partial2])
    assert deps == set([data1, data2, partial2])


def test_dep_graph_from_sources(
        parents):
    # FIXME this doesn't test everything it should test.
    graph = dep_graph_from_sources(parents.keys())
    assert graph.parents == parents


def test_make_sources(fake_env, sources):
    made_sources = SourceManager.make_sources(
            fake_env,
            staticpaths=['images'],
            datapaths=['data1', 'data2', 'data'],
            extra_deps={
                '_partial1.html': ['data1', 'data2'],
                '_partial2.html': ['data/data3'],
                'template4.html': ['data/data3'],
                }
            )

    assert made_sources == sources


def test_make_source_no_parameter(fake_env):
    # Check nothing bad happens if you don't pass any optionnal parameter
    made_sources = SourceManager.make_sources(fake_env)
    assert made_sources.sources


def test_get_dependencies(
        fake_env, sources, static, ignored,
        partial1, data1, template1, template2, invalid_source_file):
    assert set(sources.get_dependencies(template1)) == set([template1])
    assert set(sources.get_dependencies(static)) == set([static])
    assert set(sources.get_dependencies(partial1)) == set(
        [template1, template2])
    assert set(sources.get_dependencies(data1)) == set(
        [template1, template2])

    assert set(sources.get_dependencies(ignored)) == set()
    with pytest.raises(ValueError) as excinfo:
        sources.get_dependencies(invalid_source_file)
    assert str(excinfo.value) == (
            'Invalid source file'
            )


def test_update_dep_graph(sources, partial2, data3):
    mock_update = mock.Mock()
    sources.dep_graph.update_vertex = mock_update
    sources.update_dep_graph(partial2)

    mock_update.assert_called_once_with(partial2, set([data3]))


def test_source_from_name(sources, partial1, template3):
    assert (sources.source_from_name('_partial1.html') == partial1)
    assert (sources.source_from_name('sub/template3.html') == template3)
    with pytest.raises(SourceNotFoundError) as excinfo:
        sources.source_from_name('template100.html')
    assert str(excinfo.value) == (
            'Source not found'
            )


def test_remove_source(sources, template1, partial1):
    sources.remove_source(template1)
    assert template1 not in sources.sources
    assert template1 not in sources.dep_graph.parents
    assert template1 not in sources.dep_graph.children
    assert template1 not in sources.dep_graph.children[partial1]


def test_add_source(sources, template5):
    sources.add_source(template5)
    assert template5 in sources.sources
    assert template5 in sources.dep_graph.parents
