"""`ai-team show` command for displaying artifact files."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from typer.core import TyperGroup
from rich.markdown import Markdown

from ai_team.core.fs import read_artifact
from ai_team.core.locator import find_project_root
from ai_team.render import console, print_json

NAME = "show"


class _ShowGroup(TyperGroup):
    """Allow options after positional args for callback-style default command."""

    allow_interspersed_args = True


app = typer.Typer(
    help="Show an artifact by identifier.",
    invoke_without_command=True,
    cls=_ShowGroup,
)


def _artifact_files(root_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in root_dir.rglob("*.md")
        if path.is_file() and path.name != ".gitkeep" and not path.match("TEMPLATE-*.md")
    )


def _resolve_matches(identifier: str, root_dir: Path) -> list[Path]:
    token = identifier.lower()
    return [path for path in _artifact_files(root_dir) if token in path.stem.lower()]


def _kind_for_path(path: Path) -> Literal["task", "bug", "spec", "adr"]:
    if "tasks" in path.parts:
        return "task"
    if "bugs" in path.parts:
        return "bug"
    if "specs" in path.parts:
        return "spec"
    return "adr"


def _frontmatter_dict(model: object) -> dict[str, object]:
    source_map = getattr(model, "_source_map", None)
    if source_map is None:
        return {}
    frontmatter: dict[str, object] = {}
    for key, value in source_map.items():
        frontmatter[str(key)] = str(value) if value is not None else None
    return frontmatter


@app.callback()
def default(
    identifier: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Show an artifact file by ID or slug fragment."""
    root = find_project_root(Path.cwd())
    matches = _resolve_matches(identifier, root.project_dir)
    if not matches:
        raise typer.Exit(code=1)

    selected = matches[0]
    if as_json:
        model, body = read_artifact(selected, _kind_for_path(selected))
        print_json(
            {
                "path": str(selected),
                "frontmatter": _frontmatter_dict(model),
                "body": body,
            }
        )
        return

    # AC-1 requires rendering markdown output through Rich.
    console.print(Markdown(selected.read_text(encoding="utf-8")))
