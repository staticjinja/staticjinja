from __future__ import annotations

import typing as t
from pathlib import Path  # noqa: F401 (unused import, but it is used)

import typing_extensions as te
from jinja2 import Template

from .staticjinja import Site

_T = t.TypeVar("_T")

FilePath: te.TypeAlias = "str | Path"
PageMapping: te.TypeAlias = "list[tuple[str, _T]]"

Context: te.TypeAlias = "dict[str, t.Any]"


class ContextCallable(te.Protocol):
    def __call__(self) -> Context:
        ...


class ContextTemplateCallable(te.Protocol):
    def __call__(self, __template: Template) -> Context:
        ...


class Rule(te.Protocol):
    def __call__(self, __site: Site, __template: Template, **metadata: t.Any) -> None:
        ...


ContextLike: te.TypeAlias = "Context | ContextCallable | ContextTemplateCallable"
