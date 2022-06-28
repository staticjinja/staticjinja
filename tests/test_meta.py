from __future__ import annotations

from pathlib import Path

import tomlkit

import staticjinja


def test_versions_match() -> None:
    """Ensure that the version info specified in the staticjinja package
    matches the version in the pyproject.toml."""
    project_root = Path(__file__).parent.parent
    toml_path = project_root / "pyproject.toml"
    toml = tomlkit.parse(toml_path.read_text())
    assert toml["tool"]["poetry"]["version"] == staticjinja.__version__
