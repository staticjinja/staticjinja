from __future__ import annotations

import logging
import os
import subprocess
import sys
import unittest.mock as mock

import pytest

import staticjinja
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
@mock.patch("staticjinja.cli.staticjinja.Site.make_site")
def test_srcpath(
    mock_make_site: mock.Mock,
    mock_getcwd: mock.Mock,
    mock_isdir: mock.Mock,
    srcpath: str | None,
    expected: str,
) -> None:
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
@mock.patch("staticjinja.cli.staticjinja.Site.make_site")
def test_outpath(
    mock_make_site: mock.Mock,
    mock_getcwd: mock.Mock,
    mock_isdir: mock.Mock,
    outpath: str | None,
    expected: str,
) -> None:
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


@mock.patch("os.path.isdir")
@mock.patch("os.getcwd")
def test_log(mock_getcwd: mock.Mock, mock_isdir: mock.Mock) -> None:
    mock_isdir.return_value = True
    mock_getcwd.return_value = "/cwd"

    # Passing arg sets logger level
    argv = ["build", "--log=critical"]
    cli.main(argv)
    assert staticjinja.logger.level == logging.CRITICAL

    # Default log level is INFO if not set
    argv = ["build"]
    cli.main(argv)
    assert staticjinja.logger.level == logging.INFO

    # Bogus level is caught
    with pytest.raises(ValueError):
        argv = ["build", "--log=junk"]
        cli.main(argv)


@pytest.mark.parametrize(
    "command, expected",
    [
        ("build", False),
        ("watch", True),
    ],
)
@mock.patch("os.path.isdir")
@mock.patch("os.getcwd")
@mock.patch("staticjinja.cli.staticjinja.Site.make_site")
def test_watch(
    mock_make_site: mock.Mock,
    mock_getcwd: mock.Mock,
    mock_isdir: mock.Mock,
    command: str,
    expected: bool,
) -> None:
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


@mock.patch("staticjinja.cli.staticjinja.Site.make_site")
def test_nonexistent_srcpath(mock_make_site: mock.Mock) -> None:
    """Test that a nonexistent `--srcpath` exits early."""
    # Technique from
    # medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.main(["build", "--srcpath=/I/definitely/dont/exist"])
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    mock_make_site.assert_not_called()


@pytest.mark.parametrize(
    "command",
    [
        ["staticjinja"],
        [sys.executable, "-m", "staticjinja"],
    ],
)
def test_entrypoints_no_args(command: list[str]) -> None:
    """Ensure we can access the staticjinja CLI from the shell.

    Don't bother testing for any complex inputs or outputs, this is just to
    ensure that the entrypoints are properly installed.
    """
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5
    )
    expected_help_message = b"""Usage:
  staticjinja build [options]
  staticjinja watch [options]
  staticjinja -h | --help
  staticjinja --version
""".replace(
        b"\n", os.linesep.encode("utf8")
    )
    assert result.returncode == 1
    assert result.stdout == b""
    assert result.stderr == expected_help_message
