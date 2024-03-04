"""
Simple static page generator.

Uses Jinja2 to compile templates.
"""
from __future__ import annotations

import inspect
import logging
import os
import re
import shutil
import typing as t
import warnings
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from .reloader import Reloader

if t.TYPE_CHECKING:
    from .types import (
        Context,
        ContextLike,
        ContextMulti,
        ContextMapping,
        FilePath,
        Rule,
        RuleMapping,
    )

logger = logging.getLogger(__name__)


def _compute_contexts(context_like: ContextLike, template: Template) -> ContextMulti:
    if callable(context_like):
        params = len(inspect.signature(context_like).parameters)
        context_like = context_like(*[template][:params])

    if isinstance(context_like, dict):
        return [(None, context_like)]

    if isinstance(context_like, list):
        return context_like

    raise TypeError(f"Unexpected type for context: {type(context_like)}")


def _ensure_dir(path: FilePath) -> None:
    """Ensure the directory for a file exists."""
    Path(path).parent.mkdir(exist_ok=True, parents=True)


def resolve_path(path: FilePath) -> str:
    """Ensure a path is absolute. If relative, make it relative to ``os.getcwd()``.

    .. changed:: 5.0.0
       Previous to 5.0.0, if staticjinja was called from a python build script,
       then use the build script's directory was used as the root.
       See https://github.com/staticjinja/staticjinja/issues/149
    """
    if not Path(path).is_absolute():
        path = Path.cwd() / path
    return str(path)


# TODO replace with te.Self
# https://github.com/python/mypy/pull/11666
TSite = t.TypeVar("TSite", bound="Site")


class Site:
    """The Site object.

    :param environment:
        A :class:`jinja2.Environment`.

    :param searchpath:
        A string representing the name of the directory to search for
        templates.

    :param contexts:
        A list of `regex, context` pairs. Each context is either a dictionary,
        a list of `(out_name, dictionary)` tuples, or a function that takes
        either no argument or or the current template as its sole argument and
        returns one of the other two. The regex, if matched against a filename,
        will cause the context to be used.

    :param rules:
        A list of *(regex, function)* pairs. The Site will delegate
        rendering to *function* if *regex* matches the name of a template
        during rendering. *function* must take a :class:`staticjinja.Site`
        object, a :class:`jinja2.Template`, and a context dictionary as
        parameters and render the template. Defaults to ``[]``.

    :param encoding:
        The encoding of templates to use.

    :param staticpaths:
        .. deprecated:: 0.3.4

        List of directory names to get static files from (relative to
        searchpath).

    :param mergecontexts:
        A boolean value. If set to ``True``, then all matching regex from the
        contexts list will be merged (in order) to get the final context(s).
        Otherwise, only the first matching regex is used. Defaults to
        ``False``.
    """

    def __init__(
        self,
        environment: Environment,
        searchpath: FilePath,
        outpath: FilePath = ".",
        encoding: str = "utf8",
        contexts: ContextMapping | None = None,
        rules: RuleMapping | None = None,
        staticpaths: list[str] | None = None,
        mergecontexts: bool = False,
    ) -> None:
        self.env = environment
        self.searchpath = searchpath
        self.outpath = outpath
        self.encoding = encoding
        self.contexts = contexts or []
        self.rules = rules or []
        if staticpaths:
            warnings.warn("staticpaths are deprecated. Use Make instead.")
        self.staticpaths = staticpaths or []
        self.mergecontexts = mergecontexts

    @classmethod
    def make_site(
        cls: type[TSite],
        searchpath: FilePath = "templates",
        outpath: FilePath = ".",
        contexts: ContextMapping | None = None,
        rules: RuleMapping | None = None,
        encoding: str = "utf8",
        followlinks: bool = True,
        extensions: list[str] | None = None,
        staticpaths: list[str] | None = None,
        filters: dict[str, t.Any] = {},
        env_globals: dict[str, t.Any] = {},
        env_kwargs: dict[str, t.Any] | None = None,
        mergecontexts: bool = False,
    ) -> TSite:
        """Create a :class:`Site <Site>` object.

        :param searchpath:
            A string or Path representing the path to the directory that the
            Site should search to discover templates. Defaults to
            ``'templates'``.

            If a relative path is provided, it will be coerced to an absolute
            path using ``os.getcwd()``.

        :param outpath:
            A string representing the name of the directory that the Site
            should store rendered files in. Defaults to ``'.'``.

        :param contexts:
            A list of *(regex, context)* pairs. The Site will render templates
            whose name match *regex* using *context*. *context* must be either
            a dictionary-like object, a list of *(out_name, dict)* pairs,
            or a function that takes either no arguments or a single
            :class:`jinja2.Template` as an argument and returns a
            dictionary-like object or a list of *(out_name, dict)* pairs.
            Defaults to ``[]``.

        :param rules:
            A list of *(regex, function)* pairs. The Site will delegate
            rendering to *function* if *regex* matches the name of a template
            during rendering. *function* must take a :class:`staticjinja.Site`
            object, a :class:`jinja2.Template`, and a context dictionary as
            parameters and render the template. Defaults to ``[]``.

        :param encoding:
            A string representing the encoding that the Site should use when
            rendering templates. Defaults to ``'utf8'``.

        :param followlinks:
            A boolean describing whether symlinks in searchpath should be
            followed or not. Defaults to ``True``.

        :param extensions:
            A list of :ref:`Jinja extensions <jinja-extensions>` that the
            :class:`jinja2.Environment` should use. Defaults to ``[]``.

        :param staticpaths:
            .. deprecated:: 0.3.4

            List of directories to get static files from (relative to
            searchpath).  Defaults to ``None``.

        :param filters:
            A dictionary of Jinja2 filters to add to the Environment.  Defaults
            to ``{}``.

        :param env_globals:
            A mapping from variable names that should be available all the time
            to their values. Defaults to ``{}``.

        :param env_kwargs:
            A dictionary that will be passed as keyword arguments to the
            jinja2 Environment. Defaults to ``{}``.

        :param mergecontexts:
            A boolean value. If set to ``True``, then all matching regex from
            the contexts list will be merged (in order) to get the final
            context.  Otherwise, only the first matching regex is used.
            Defaults to ``False``.
        """
        searchpath = resolve_path(searchpath)

        if env_kwargs is None:
            env_kwargs = {}
        env_kwargs["loader"] = FileSystemLoader(
            searchpath=searchpath, encoding=encoding, followlinks=followlinks
        )
        env_kwargs.setdefault("extensions", extensions or [])
        environment = Environment(**env_kwargs)
        environment.filters.update(filters)
        environment.globals.update(env_globals)

        return cls(
            environment,
            searchpath=searchpath,
            outpath=outpath,
            encoding=encoding,
            rules=rules,
            contexts=contexts,
            staticpaths=staticpaths,
            mergecontexts=mergecontexts,
        )

    @property
    def template_names(self) -> list[str]:
        return self.env.list_templates(filter_func=self.is_template)

    @property
    def templates(self) -> t.Iterator[Template]:
        """Generator for templates."""
        for template_name in self.template_names:
            yield self.get_template(template_name)

    @property
    def static_names(self) -> list[str]:
        return self.env.list_templates(filter_func=self.is_static)

    def get_template(self, template_name: FilePath) -> Template:
        """Get a :class:`jinja2.Template` from the environment.

        :param template_name: A string representing the name of the template.
        """
        template_name = Path(template_name).as_posix()
        try:
            return self.env.get_template(template_name)
        except UnicodeDecodeError as e:
            raise UnicodeError("Unable to decode %s: %s" % (template_name, e))

    def get_context(self, template: Template) -> Context:
        """Get the context for a single-output template.

        This works like :meth:`get_contexts`, but returns the template context
        directly and throws if multiple outputs are specified for the template.

        This method is deprecated, :meth:`get_contexts` should be used instead
        to properly handle templates with multiple outputs.

        :param template: the template to get the context for
        """
        contexts = self.get_contexts(template)

        if None not in contexts:
            raise ValueError("get_context found multiple outputs for template")

        return contexts[None]

    def get_contexts(self, template: Template) -> dict[str | None, Context]:
        """Get the contexts for a template.

        In most cases, the template produces a single output without a specific
        name and this will return a dictionary with a single key ``None`` mapped
        to a template context.

        If the matching context definition(s) specified a list of named outputs,
        a dictionary mapping each output name to a specific template context is
        returned. There is no ``None`` key in this case. If no matching context
        definition is found, a single empty context is returned.

        If mergecontexts is ``True`` and several context definitions are found,
        the contexts they specified are merged. Otherwise only the first
        matching context definition is considered.

        If definitions with single outputs and multiple outputs are mixed, the
        definitions with single outputs are applied to all outputs, whereas the
        definitions with multiple outputs are merged where the output name
        matches.

        :param template: the template to get the contexts for
        """

        # TODO unlink name from the template
        assert template.name is not None
        contexts: dict[str | None, Context] = {None: {}}

        for regex, context_like in self.contexts:
            if not re.match(regex, template.name):
                continue

            new_contexts = _compute_contexts(context_like, template)
            if not self.mergecontexts:
                return dict(new_contexts)

            for name, ctx in new_contexts:
                if name is None:
                    # apply to all existing contexts
                    for name in contexts:
                        contexts[name].update(ctx)
                else:
                    # create or update named outputs
                    context = contexts.get(name, contexts[None])
                    contexts[name] = context.copy()
                    contexts[name].update(ctx)

        # ignore the default output if we found any named outputs
        if len(contexts) > 1:
            del contexts[None]

        return contexts

    def get_rule(self, template_name: str) -> Rule:
        """Find a matching compilation rule for a function.

        Raises a :exc:`ValueError` if no matching rule can be found.

        :param template_name: the name of the template
        """
        for regex, render_func in self.rules:
            if re.match(regex, template_name):
                return render_func
        raise ValueError("no matching rule")

    def is_static(self, filename: FilePath) -> bool:
        """Check if a file is static. Static files are copied, rather than
        compiled using Jinja2.

        .. deprecated:: 0.3.4

        A template is considered static if it lives in any of the directories
        specified in ``staticpaths``.

        :param filename: A PathLike name of the file to check.

        """
        path = Path(filename).as_posix()
        return any(path.startswith(Path(sp).as_posix()) for sp in self.staticpaths)

    def is_partial(self, filename: FilePath) -> bool:
        """Check if a file is partial. Partial files are not
        rendered, but they are used in rendering templates.

        A file is considered a partial if it or any of its parent
        directories are prefixed with an ``'_'``.

        :param filename: A PathLike name of the file to check
        """
        return any(part.startswith("_") for part in Path(filename).parts)

    def is_ignored(self, filename: FilePath) -> bool:
        """Check if a file is an ignored. Ignored files are
        neither rendered nor used in rendering templates.

        A file is considered ignored if it or any of its parent directories
        are prefixed with an ``'.'``.

        :param filename: A PathLike name of the file to check
        """
        return any(part.startswith(".") for part in Path(filename).parts)

    def is_template(self, filename: FilePath) -> bool:
        """Check if a file is a template.

        A file is a considered a template if it is not partial, ignored, or
        static.

        :param filename: A PathLike name of the file to check
        """
        if self.is_partial(filename):
            return False
        if self.is_ignored(filename):
            return False
        if self.is_static(filename):
            return False
        return True

    def render_template(
        self,
        template: Template,
        context: Context | None = None,
        filepath: str | None = None,
    ) -> None:
        """Render a single :class:`jinja2.Template` object.

        If a Rule matching the template is found, the rendering task is
        delegated to the rule.

        :param template:
            A :class:`jinja2.Template` to render.

        :param context:
            Optional. A dictionary representing the context to render
            *template* with. If no context is provided, :meth:`get_contexts` is
            used to provide a context.

        :param filepath:
            Optional. A PathLike representing the output location.
            Defaults to to ``os.path.join(self.outpath, template.name)``.
            This parameter must not be specified if context is ``None`` and the
            contex definition specifies multiple outputs for the template.
        """
        if context is None:
            contexts = self.get_contexts(template)

            if filepath is not None:
                raise ValueError(
                    "can't override filepath for template with multiple outputs"
                )

            for out_name in contexts:
                filepath = out_name and os.path.join(self.outpath, out_name)
                self.render_template(template, contexts[out_name], filepath)

            return

        if filepath is not None and filepath != template.name:
            logger.info("Rendering %s to %s...", template.name, filepath)
        else:
            logger.info("Rendering %s...", template.name)

        assert template.name is not None
        try:
            rule = self.get_rule(template.name)
        except ValueError:
            if filepath is None:
                filepath = os.path.join(self.outpath, template.name)
            _ensure_dir(filepath)
            template.stream(**context).dump(filepath, self.encoding)
        else:
            rule(self, template, **context)

    def render_templates(self, templates: t.Iterable[Template]) -> None:
        """Render a collection of :class:`jinja2.Template` objects.

        :param templates:
            A collection of :class:`jinja2.Template` objects to render.
        """
        for template in templates:
            self.render_template(template)

    def copy_static(self, files: t.Iterable[FilePath]) -> None:
        for f in files:
            f = Path(f)
            input_location = Path(self.searchpath) / f
            output_location = Path(self.outpath) / f
            logger.info("Copying %s to %s.", f, output_location)
            _ensure_dir(output_location)
            shutil.copy2(input_location, output_location)

    def get_dependents(self, filename: FilePath) -> t.Sequence[FilePath]:
        """Get a list of files that depends on *filename*. Useful to decide
        what to re-render when *filename* changes.

        - Ignored files have no dependents.
        - Static and template files just have themselves as dependents.
        - Partial files have all the templates as dependents, since any template
          may rely upon a partial.

        .. versionchanged:: 2.0.0
           Now always returns list of filenames. Before the return type
           was either a list of templates or list of filenames.

        :param filename: the name of the file to find dependents of
        :return: list of filenames of dependents.
        """
        if self.is_partial(filename):
            return self.template_names
        elif self.is_template(filename):
            return [filename]
        elif self.is_static(filename):
            return [filename]
        else:
            return []

    def render(self, use_reloader: bool = False) -> None:
        """Generate the site.

        :param use_reloader: if given, reload templates on modification
        """
        self.render_templates(self.templates)
        self.copy_static(self.static_names)

        if use_reloader:
            Reloader(self).watch()

    def __repr__(self) -> str:
        return "%s('%s', '%s')" % (type(self).__name__, self.searchpath, self.outpath)
