"""Root Typer application and console-script entry point for ai-team."""

from __future__ import annotations

import importlib.metadata
from typing import Annotated, Optional

import typer
from typer.core import TyperGroup

from ai_team.commands import discover_and_mount

DEVELOPMENT_WARNING = (
    "Warning: ai-team is under development. Please report issues at "
    "https://github.com/aurora-firmware/the-ai-team/issues"
)


class DevelopmentWarningGroup(TyperGroup):
    """Root command group that warns once before processing an invocation."""

    def main(self, *args, **kwargs):
        typer.echo(DEVELOPMENT_WARNING, err=True)
        return super().main(*args, **kwargs)


app = typer.Typer(
    name="ai-team",
    help="Manage AI-team artifacts: specs, tasks, bugs, and ADRs.",
    add_completion=False,
    cls=DevelopmentWarningGroup,
)

# Register all command modules discovered under ai_team.commands.
discover_and_mount(app)


def _version_callback(value: bool) -> None:
    if value:
        version = importlib.metadata.version("ai-team")
        typer.echo(version)
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="Print the ai-team version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """ai-team — AI-team artifact management CLI."""
