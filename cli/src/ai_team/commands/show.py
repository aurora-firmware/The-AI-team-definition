"""`ai-team show` command for displaying artifact files."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.markdown import Markdown
from typer.core import TyperGroup

from ai_team.core.fs import read_artifact
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.result import Result
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


def _search_roots(root: ProjectRoot) -> list[Path]:
    return [
        root.tasks_pending,
        root.tasks_in_progress,
        root.tasks_completed,
        root.tasks_blocked,
        root.bugs_open,
        root.bugs_in_progress,
        root.bugs_resolved,
        root.specs,
        root.decisions,
    ]


def _artifact_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        files.extend(
            sorted(
                path
                for path in root.glob("*.md")
                if path.is_file()
                and path.name != ".gitkeep"
                and not path.match("TEMPLATE-*.md")
            )
        )
    return files


def _kind_for_path(path: Path) -> Literal["task", "bug", "spec", "adr"]:
    if "tasks" in path.parts:
        return "task"
    if "bugs" in path.parts:
        return "bug"
    if "specs" in path.parts:
        return "spec"
    return "adr"


def _matches_identifier(identifier: str, path: Path) -> bool:
    token = identifier.lower()
    if token in path.stem.lower():
        return True

    kind = _kind_for_path(path)
    if kind == "spec":
        return False

    model, _ = read_artifact(path, kind)
    model_id = getattr(model, "id", None)
    if model_id is None:
        return False
    return token == str(model_id).lower()


def _resolve_matches(identifier: str, roots: list[Path]) -> list[Path]:
    return [
        path for path in _artifact_files(roots) if _matches_identifier(identifier, path)
    ]


def _frontmatter_dict(model: object) -> dict[str, object]:
    source_map = getattr(model, "_source_map", None)
    if source_map is None:
        return {}
    frontmatter: dict[str, object] = {}
    for key, value in source_map.items():
        frontmatter[str(key)] = str(value) if value is not None else None
    return frontmatter


def show_artifact(root: ProjectRoot, identifier: str) -> Result:
    """Resolve *identifier* to one artifact; return its path, frontmatter and body."""
    search_roots = _search_roots(root)
    matches = _resolve_matches(identifier, search_roots)
    if not matches:
        searched = ", ".join(str(path) for path in search_roots)
        return Result(
            status=1,
            message=f"Artifact '{identifier}' not found. Searched roots: {searched}",
        )

    if len(matches) > 1:
        lines = [f"Multiple artifacts matched '{identifier}':"]
        lines.extend(f"- {match}" for match in matches)
        return Result(status=1, message="\n".join(lines))

    selected = matches[0]
    model, body = read_artifact(selected, _kind_for_path(selected))
    return Result(
        status=0,
        payload={
            "path": str(selected),
            "frontmatter": _frontmatter_dict(model),
            "body": body,
        },
    )


@app.callback()
def default(
    identifier: str,
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Show an artifact file by ID or slug fragment."""
    result = show_artifact(find_project_root(Path.cwd()), identifier)
    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if as_json:
        print_json(result.payload)
        return

    # AC-1 requires rendering markdown output through Rich.
    console.print(Markdown(Path(result.payload["path"]).read_text(encoding="utf-8")))
