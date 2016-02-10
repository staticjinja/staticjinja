try:
    import unittest.mock as mock
except ImportError:
    import mock

import sys
from staticjinja import cli


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
def test_srcpath(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': 'templates',
        '--outpath': None,
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/templates',
        outpath='/',
        staticpaths=None
    )


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
def test_outpath(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': 'templates',
        '--outpath': 'build',
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/templates',
        outpath='build',
        staticpaths=None
    )


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
def test_staticpath(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': 'templates',
        '--outpath': 'build',
        '--static': 'css, images',
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/templates',
        outpath='build',
        staticpaths=['css', 'images']
    )


@mock.patch('sys.exit')
@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
def test_invalid_paths(mock_make_site, mock_getcwd, mock_isdir, mock_exit):
    mock_isdir.return_value = False
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': 'templates',
        '--outpath': None,
        '--static': 'static',
        'watch': False,
    })

    assert mock_exit.call_count == 3


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
def test_srcpath_default(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'

    cli.render({
        '--srcpath': None,
        '--outpath': None,
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/templates',
        outpath='/',
        staticpaths=None
    )


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.staticjinja.make_site')
def test_srcpath_absolute(mock_make_site, mock_getcwd, mock_isdir):
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/'
    cli.render({
        '--srcpath': '/foo/templates',
        '--outpath': None,
        '--static': None,
        'watch': False,
    })

    mock_make_site.assert_called_once_with(
        searchpath='/foo/templates',
        outpath='/',
        staticpaths=None
    )


@mock.patch('staticjinja.cli.render')
def test_main(mock_render):
    sys.argv = [
            'staticjinja',
            'build',
            '--srcpath=templates',
            '--outpath=build',
            '--static=css, images',
    ]

    cli.main()

    mock_render.assert_called_once_with(
            {
                '--help': False,
                '--outpath': 'build',
                '--srcpath': 'templates',
                '--static': 'css, images',
                '--version': False,
                'build': True,
                'watch': False
                })
