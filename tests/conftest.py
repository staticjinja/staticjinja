import py.test
from pytest import fixture

from staticjinja.sources import (
        DATA_FLAVOR, TEMPLATE_FLAVOR, PARTIAL_FLAVOR,
        STATIC_FLAVOR, IGNORED_FLAVOR, Source
        )


def pytest_addoption(parser):
    parser.addoption(
            '--func', action='store_true', default=False,
            help='Also run functional tests')
    parser.addoption(
            '--onlyfunc', action='store_true', default=False,
            help='Run only functional tests')


def pytest_runtest_setup(item):
    """Skip tests if they are marked as functionnal and --func is not given"""
    onlyfunc = item.config.getvalue('onlyfunc')
    func = item.config.getvalue('func') or onlyfunc
    if getattr(item.obj, 'func', None) and not func:
        py.test.skip('functionnal tests not requested')
    if not getattr(item.obj, 'func', None) and onlyfunc:
        py.test.skip('only functionnal tests requested')


def fake_source(filename, flavor, deps=None):
    deps = deps or set([])
    source = Source(filename, flavor, None)
    source.get_dep = lambda x: deps
    return source


@fixture
def data1():
    return fake_source('data1', DATA_FLAVOR)


@fixture
def data2():
    return fake_source('data2', DATA_FLAVOR)


@fixture
def data3():
    return fake_source('data/data3', DATA_FLAVOR)


@fixture
def partial1(data1, data2, partial2):
    return fake_source(
            '_partial1.html',
            PARTIAL_FLAVOR,
            deps=set([data1, data2, partial2])
            )


@fixture
def partial2(data3):
    return fake_source(
            '_partial2.html',
            PARTIAL_FLAVOR,
            deps=set([data3])
            )


@fixture
def template1(partial1):
    return fake_source(
            'template1.html',
            TEMPLATE_FLAVOR,
            deps=set([partial1])
            )


@fixture
def template2(partial1, partial2):
    return fake_source(
            'template2.html',
            TEMPLATE_FLAVOR,
            deps=set([partial1, partial2])
            )


@fixture
def template3(partial2):
    return fake_source(
            'sub/template3.html',
            TEMPLATE_FLAVOR,
            deps=set([partial2])
            )


@fixture
def template4(data3):
    return fake_source(
            'template4.html',
            TEMPLATE_FLAVOR,
            deps=set([data3])
            )


@fixture
def template5(partial1):
    return fake_source(
            'template5.html',
            TEMPLATE_FLAVOR,
            deps=set([partial1])
            )


@fixture
def static():
    return fake_source(
            'images/logo.png',
            STATIC_FLAVOR,
            deps=set()
            )


@fixture
def ignored():
    return fake_source(
            '.conf',
            IGNORED_FLAVOR,
            deps=set()
            )


@fixture
def invalid_source_file():
    return fake_source('invalid', 'invalid_flavor')
