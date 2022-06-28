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


ContextLike: te.TypeAlias = "Context | ContextCallable | ContextTemplateCallable"


class Rule(te.Protocol):
    # This is a little restrictive, mypy will complain (when it shouldn't) for
    # def f(site, template, other_kwarg=42, **kwargs)
    # But it's better than nothing. Users can either #  type: ignore
    # that line in their code, or submit a PR that actually fixes it.
    def __call__(self, site: Site, template: Template, **context: t.Any) -> t.Any:
        ...


ContextMapping: te.TypeAlias = "PageMapping[ContextLike]"
RuleMapping: te.TypeAlias = "PageMapping[Rule]"
