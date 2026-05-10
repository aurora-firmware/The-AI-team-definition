"""
Auto-discovery and mounting of ai_team subcommand modules.

Convention
----------
Every module placed directly under this package must export:

    NAME : str       — the subcommand name as it appears on the CLI.
    app  : typer.Typer — the Typer application for that subcommand group.

The ``discover_and_mount`` function is called once from ``ai_team.cli`` at
startup.  Later tasks drop a new module here; ``cli.py`` requires no changes.
"""
from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable
from types import ModuleType

import typer


def discover_and_mount(
    parent: typer.Typer,
    modules: Iterable[ModuleType] | None = None,
) -> None:
    """Mount subcommand modules onto *parent*.

    Parameters
    ----------
    parent:
        The root Typer application onto which each sub-app is added.
    modules:
        An explicit iterable of already-imported modules.  When *None* (the
        default used in production) the function uses ``pkgutil.iter_modules``
        to discover every sibling module in this package and imports them
        automatically.

    A module is mounted only when it exposes both ``NAME`` (str) and ``app``
    (``typer.Typer``).  Modules that lack either attribute are silently skipped
    so that helper or utility modules can live alongside command modules without
    causing errors.
    """
    if modules is None:
        modules = _iter_command_modules()

    for mod in modules:
        name: str | None = getattr(mod, "NAME", None)
        app: typer.Typer | None = getattr(mod, "app", None)
        if name is None or app is None:
            continue
        parent.add_typer(app, name=name)


def _iter_command_modules() -> Iterable[ModuleType]:
    """Import and yield every sibling module in the commands package."""
    package_path = __path__  # type: ignore[name-defined]
    package_name = __name__

    for module_info in pkgutil.iter_modules(package_path):
        full_name = f"{package_name}.{module_info.name}"
        try:
            yield importlib.import_module(full_name)
        except Exception:
            # A broken command module must not crash the whole CLI.
            pass
