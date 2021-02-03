import os
import unittest.mock as mock

import pytest

from staticjinja import cli

srcpath_cases = [
    (None, "/cwd/templates"),  # Default is CWD/templates/
    (".", "/cwd"),  # Relative paths assumed under CWD
    ("src", "/cwd/src"),  # Relative paths assumed under CWD
    ("./src", "/cwd/src"),  # Relative paths assumed under CWD
    ("/foo/src", "/foo/src"),  # Absolute paths taken as-is
]


@pytest.mark.parametrize("srcpath, expected", srcpath_cases)
@mock.patch("os.path.isdir")
@mock.patch("os.getcwd")
@mock.patch("staticjinja.cli.Site.make_site")
def test_srcpath(mock_make_site, mock_getcwd, mock_isdir, srcpath, expected):
    """Test that various `--srcpath` args given to the CLI result in
    Site.make_site() being called with the correct searchpath parameter."""
    mock_isdir.return_value = True
    mock_getcwd.return_value = "/cwd"
    argv = ["build"]
    if srcpath:
        argv.append("--srcpath={}".format(srcpath))
    cli.main(argv)
    mock_make_site.assert_called_once_with(
        searchpath=os.path.normpath(expected),
        outpath=os.path.normpath("/cwd"),
        staticpaths=None,
    )


outpath_cases = [
    (None, "/cwd"),  # Default is CWD
    (".", "/cwd"),  # Relative paths assumed under CWD
    ("src", "/cwd/src"),  # Relative paths assumed under CWD
    ("./src", "/cwd/src"),  # Relative paths assumed under CWD
    ("/foo/src", "/foo/src"),  # Absolute paths taken as-is
]


@pytest.mark.parametrize("outpath, expected", outpath_cases)
@mock.patch("os.path.isdir")
@mock.patch("os.getcwd")
@mock.patch("staticjinja.cli.Site.make_site")
def test_outpath(mock_make_site, mock_getcwd, mock_isdir, outpath, expected):
    """Test that various `--outpath` args given to the CLI result in
    Site.make_site() being called with the correct outpath parameter."""
    mock_isdir.return_value = True
    mock_getcwd.return_value = "/cwd"
    argv = ["build"]
    if outpath:
        argv.append("--outpath={}".format(outpath))
    cli.main(argv)
    mock_make_site.assert_called_once_with(
        searchpath=os.path.normpath("/cwd/templates"),
        outpath=os.path.normpath(expected),
        staticpaths=None,
    )


@pytest.mark.parametrize(
    "command, expected",
    [
        ("build", False),
        ("watch", True),
    ],
)
@mock.patch("os.path.isdir")
@mock.patch("os.getcwd")
@mock.patch("staticjinja.cli.Site.make_site")
def test_watch(mock_make_site, mock_getcwd, mock_isdir, command, expected):
    """Test that build/watch commands result in Site.render() being called
    with the correct use_reloader values."""
    mock_isdir.return_value = True
    mock_getcwd.return_value = "/cwd"
    # Make our mock Site.make_site() method return a mock
    # Site instance that we can test.
    mock_site = mock.Mock()
    mock_make_site.return_value = mock_site
    cli.main([command])
    mock_site.render.assert_called_once_with(use_reloader=expected)


@mock.patch("staticjinja.cli.Site.make_site")
def test_nonexistent_srcpath(mock_make_site):
    """Test that a nonexistent `--srcpath` exits early."""
    # Technique from
    # medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(["build", "--srcpath=/I/definitely/dont/exist"])
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    mock_make_site.assert_not_called()
