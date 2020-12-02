import unittest.mock as mock

from staticjinja import cli


@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.Site.make_site')
def test_cli_srcpath(mock_make_site, mock_getcwd, mock_isdir):
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
@mock.patch('staticjinja.cli.Site.make_site')
def test_cli_srcpath_default(mock_make_site, mock_getcwd, mock_isdir):
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
@mock.patch('staticjinja.cli.Site.make_site')
def test_cli_srcpath_absolute(mock_make_site, mock_getcwd, mock_isdir):
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
