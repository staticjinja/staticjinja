from pytest import fixture
from pytest import mark
import pytest

from copy import deepcopy

from staticjinja.dep_graph import DepGraph

"""
Those tests will use the following graph
t1    t2
  \  / |
   p1  |  sub.t3
  /| \ | /
d1 |  p2    t4
   |    \  /
  d2   data.d3
each t is a template, p is a partial and d is a data file.
There is also an ignored file .ignored1.html and a static files
in static_js/ static_css/ and favicon.ico
"""


@fixture
def parents():
    return {
            '_partial2.html': set(['data/data3']),
            '_partial1.html': set(['data2', 'data1', '_partial2.html']),
            'data1': set(),
            'data2': set(),
            'data/data3': set(),
            'template1.html': set(['_partial1.html']),
            'template2.html': set(['_partial1.html', '_partial2.html']),
            'sub/template3.html': set(['_partial2.html']),
            'template4.html': set(['data/data3']),
            }


@fixture
def children():
    return {
            'template1.html': set(),
            'template2.html': set(),
            'sub/template3.html': set(),
            'template4.html': set(),
            '_partial1.html': set(['template1.html', 'template2.html']),
            '_partial2.html': set([
                '_partial1.html',
                'template2.html',
                'sub/template3.html',
                ]),
            'data1': set(['_partial1.html']),
            'data2': set(['_partial1.html']),
            'data/data3': set(['_partial2.html', 'template4.html'])
            }


descendants = {
        '_partial1.html': [
                '_partial1.html',
                'template1.html',
                'template2.html',
                ],
        '_partial2.html': [
                '_partial1.html',
                '_partial2.html',
                'sub/template3.html',
                'template1.html',
                'template2.html',
                ],
        'data1': [
                '_partial1.html',
                'data1',
                'template1.html',
                'template2.html',
                ],
        'data2': [
                '_partial1.html',
                'data2',
                'template1.html',
                'template2.html',
                ],
        'data/data3': [
                '_partial1.html',
                '_partial2.html',
                'data/data3',
                'sub/template3.html',
                'template1.html',
                'template2.html',
                'template4.html',
                ],
        'template1.html': ['template1.html'],
        'template2.html': ['template2.html'],
        'sub/template3.html': ['sub/template3.html'],
        'template4.html': ['template4.html'],
        }


ancestors = {
        '_partial1.html': [
                '_partial1.html',
                '_partial2.html',
                'data/data3',
                'data1',
                'data2',
                ],
        '_partial2.html': [
                '_partial2.html',
                'data/data3',
                ],
        'data1': [
                'data1',
                ],
        'data2': [
                'data2',
                ],
        'data/data3': [
                'data/data3',
                ],
        'template1.html': [
                '_partial1.html',
                '_partial2.html',
                'data/data3',
                'data1',
                'data2',
                'template1.html'
                ],
        'template2.html': [
                '_partial1.html',
                '_partial2.html',
                'data/data3',
                'data1',
                'data2',
                'template2.html'
                ],
        'sub/template3.html': [
                '_partial2.html',
                'data/data3',
                'sub/template3.html',
                ],
        'template4.html': [
                'data/data3',
                'template4.html'
                ],
        }


@fixture
def graph(parents, children):
    return DepGraph(parents, children)


def test_from_parents(parents, children):
    graph = DepGraph.from_parents(parents)
    assert graph.parents == parents
    assert graph.children == children


@mark.parametrize('start, dep', descendants.items())
def test_get_descendants(graph, start, dep):
    assert sorted(list(graph.get_descendants(start))) == dep


@mark.parametrize('start, dep', ancestors.items())
def test_connected_components(graph, start, dep):
    assert sorted(list(graph.connected_components('ancestors', start))) == dep


def test_connected_components_invalid_direction(graph):
    with pytest.raises(ValueError) as excinfo:
        list(graph.connected_components('sideways', 'data1'))
    assert str(excinfo.value) == (
            'direction should be either descendants or ancestors'
            )


def test_update_vertex_remove_dependency(graph, parents, children):
    graph.update_vertex('template2.html', set(['_partial1.html']))

    new_parents = deepcopy(parents)
    new_parents['template2.html'] = set(['_partial1.html'])
    assert graph.parents == new_parents

    new_children = deepcopy(children)
    new_children['_partial2.html'] = set([
        '_partial1.html', 'sub/template3.html'
        ])
    assert graph.children == new_children


def test_update_vertex_create_dependency(graph, parents, children):
    graph.update_vertex('template4.html', set(['data1', 'data/data3']))

    new_parents = deepcopy(parents)
    new_parents['template4.html'] = set(['data1', 'data/data3'])
    assert graph.parents == new_parents

    new_children = deepcopy(children)
    new_children['data1'] = set(['_partial1.html', 'template4.html'])
    assert graph.children == new_children


def test_update_vertex_create_vertex(graph, parents, children):
    graph.update_vertex('template5.html', set(['data1']))

    new_parents = deepcopy(parents)
    new_parents['template5.html'] = set(['data1'])
    assert graph.parents == new_parents

    new_children = deepcopy(children)
    new_children['data1'] = set(['_partial1.html', 'template5.html'])
    assert graph.children == new_children


def test_update_vertex_nochange(graph, parents):
    graph.update_vertex('template1.html', set(['_partial1.html']))

    assert graph.parents == parents


def test_add_vertex(graph, parents, children):
    graph.add_vertex('new_template', ['data1', 'data2'])
    assert graph.parents['new_template'] == ['data1', 'data2']
    assert graph.children['data1'] == children['data1'].union(['new_template'])
    assert graph.children['data2'] == children['data2'].union(['new_template'])


def test_remove_vertex(graph):
    graph.remove_vertex('_partial2.html')
    assert graph.children['data/data3'] == set(['template4.html'])
    assert graph.parents['_partial1.html'] == set(['data1', 'data2'])
