"""`ai-team show` command for displaying artifact files."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.markdown import Markdown

from ai_team.core.locator import find_project_root
from ai_team.render import console

NAME = "show"
app = typer.Typer(help="Show an artifact by identifier.", invoke_without_command=True)


def _artifact_files(root_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in root_dir.rglob("*.md")
        if path.is_file() and path.name != ".gitkeep" and not path.match("TEMPLATE-*.md")
    )


def _resolve_matches(identifier: str, root_dir: Path) -> list[Path]:
    token = identifier.lower()
    return [path for path in _artifact_files(root_dir) if token in path.stem.lower()]


@app.callback()
def default(identifier: str) -> None:
    """Show an artifact file by ID or slug fragment."""
    root = find_project_root(Path.cwd())
    matches = _resolve_matches(identifier, root.project_dir)
    if not matches:
        raise typer.Exit(code=1)

    # AC-1 requires rendering markdown output through Rich.
    console.print(Markdown(matches[0].read_text(encoding="utf-8")))
