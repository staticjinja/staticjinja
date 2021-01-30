import unittest.mock as mock

import pytest

from staticjinja import cli

srcpath_cases = [(None, '/cwd/templates'),  # Default is CWD/templates/
                 ('.', '/cwd'),  # Relative paths assumed under CWD
                 ('src', '/cwd/src'),  # Relative paths assumed under CWD
                 ('./src', '/cwd/src'),  # Relative paths assumed under CWD
                 ('/foo/src', '/foo/src'),  # Absolute paths taken as-is
                 ]


@pytest.mark.parametrize("srcpath, expected", srcpath_cases)
@mock.patch('os.path.isdir')
@mock.patch('os.getcwd')
@mock.patch('staticjinja.cli.Site.make_site')
def test_srcpath(mock_make_site, mock_getcwd, mock_isdir, srcpath, expected):
    '''Test that various `--srcpath` args given to the CLI result in
    Site.make_site() being called with the correct searchpath parameter.'''
    mock_isdir.return_value = True
    mock_getcwd.return_value = '/cwd'
    argv = ['build']
    if srcpath:
        argv.append('--srcpath={}'.format(srcpath))
    cli.main(argv)
    mock_make_site.assert_called_once_with(
        searchpath=expected,
        outpath='/cwd',
        staticpaths=None
    )
