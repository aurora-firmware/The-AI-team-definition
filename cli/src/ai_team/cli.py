"""Root Typer application and console-script entry point for ai-team."""

from __future__ import annotations

import importlib.metadata
from typing import Annotated, Optional

import typer

from ai_team.commands import discover_and_mount

app = typer.Typer(
    name="ai-team",
    help="Manage AI-team artifacts: specs, tasks, bugs, and ADRs.",
    add_completion=False,
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
