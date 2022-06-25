"""Runs integration tests on the examples."""
from __future__ import annotations

import difflib
import filecmp
import os
import shutil
import subprocess
from pathlib import Path

import pytest_check as check
from _pytest.fixtures import SubRequest
from pytest import fixture

PROJECT_ROOT = Path(__file__).parent.parent


class ContentDirCmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """

    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(
            self.left, self.right, self.common_files, shallow=False
        )
        self.same_files, self.diff_files, self.funny_files = fcomp


def print_diff(filename1: str, filename2: str) -> None:
    with open(filename1) as f1, open(filename2) as f2:
        diff = difflib.unified_diff(
            f1.readlines(), f2.readlines(), fromfile=filename1, tofile=filename2
        )
        for line in diff:
            # line already ends with a newline
            print(line, end="")


def check_same(dir1: str | Path, dir2: str | Path) -> None:
    cmp = ContentDirCmp(dir1, dir2)
    cmp.report()
    for df in cmp.diff_files:
        print_diff(os.path.join(dir1, df), os.path.join(dir2, df))
    check.equal(cmp.left_only, [])
    check.equal(cmp.right_only, [])
    check.equal(cmp.funny_files, [])
    check.equal(cmp.diff_files, [])
    for subdir in cmp.common_dirs:
        check_same(os.path.join(dir1, subdir), os.path.join(dir2, subdir))


def example_names() -> list[str]:
    names = os.listdir(PROJECT_ROOT / "examples")
    ignored = ["__pycache__", "README.rst"]
    for ig in ignored:
        while ig in names:
            names.remove(ig)
    return names


@fixture(params=example_names())
def example_name(request: SubRequest) -> str:
    return request.param


def test_example(tmp_path: Path, example_name: str) -> None:
    """Builds an example, ensures the rendered output matches the expected."""
    example_directory = PROJECT_ROOT / "examples" / example_name
    source_directory = example_directory / "before"
    expected_directory = example_directory / "after"
    working_directory = tmp_path / example_name
    shutil.copytree(source_directory, working_directory)

    # os.getcwd() starts in the project's root directory.
    # But, we want to emulate running build.sh as if we were inside
    # the example directory.
    initial_directory = os.getcwd()
    try:
        os.chdir(working_directory)
        print("Running example {}".format(source_directory))
        print("Working directory for debugging: {}".format(working_directory))
        assert subprocess.call(["sh", "build.sh"]) == 0, "build.sh failed"

        # On windows, when the repo is checked out with git, all the unix-standard
        # NL linefeed characters are converted to the dos-standard CRNL newline
        # characters. However, jinja2 always uses NL newlines, so all the
        # rendered files will have NL. Just convert everything to us NL so
        # we can compare them.
        # I figured it's better to just do the conversion here, as opposed to a
        # change in globl .gitconfig.
        if os.name == "nt":
            before_files = [str(path) for path in expected_directory.glob("**/*")]
            ouput_files = [str(path) for path in working_directory.glob("**/*")]
            args = ["dos2unix"] + before_files + ouput_files
            assert subprocess.call(args) == 0, "dos2unix failed"
        check_same(expected_directory, working_directory)
    finally:
        os.chdir(initial_directory)
