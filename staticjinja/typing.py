import os
import staticjinja
import sys
from typing import Any, Callable, Dict, Tuple, Union, TYPE_CHECKING

if sys.version_info >= (3, 8):  # TODO: Remove this when we only support 3.8+
    from typing import Protocol
else:
    from typing_extensions import Protocol

from jinja2 import Template

if TYPE_CHECKING:
    from .staticjinja import Site

Context = Dict[str, Any]
ContextGeneratorZeroArgs = Callable[[], Context]
ContextGeneratorOneArgs = Callable[[Template], Context]
# ContextGenerator = Union[ContextGeneratorZeroArgs, ContextGeneratorOneArgs]
ContextLike = Union[Context, ContextGeneratorZeroArgs, ContextGeneratorOneArgs]
ContextRule = Tuple[str, ContextLike]


class RenderFunction(Protocol):
    def __call__(self, site: "Site", template: Template, **kwargs: Any) -> Any:
        ...


def caller(f: RenderFunction):
    site = staticjinja.make_site()
    f(site, Template("dasdasd"), a=1, b=2)


def callback(site, template, **context):
    pass


caller(callback)


RenderRule = Tuple[str, RenderFunction]


PathLike = Union[str, "os.PathLike[str]"]
