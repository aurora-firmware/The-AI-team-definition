"""`ai-team list` command group for listing project artifacts."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from ai_team.core.locator import find_project_root
from ai_team.core.models import (
    parse_adr,
    parse_bug,
    parse_change_request,
    parse_spec,
    parse_task,
)
from ai_team.render import console, print_json

NAME = "list"
app = typer.Typer(help="List tasks, bugs, specs, ADRs, and change requests.")


def _should_skip(path: Path) -> bool:
    """Return True when *path* is a placeholder or template file."""
    return path.name == ".gitkeep" or path.match("TEMPLATE-*.md")


def _iter_markdown_files(folder: Path) -> list[Path]:
    """Return sorted markdown files in *folder*, excluding templates/placeholders."""
    return sorted(
        path
        for path in folder.glob("*.md")
        if path.is_file() and not _should_skip(path)
    )


def _collect_from_state_folders(
    folders: list[tuple[str, Path]],
    state: str | None,
    parser,
    row_builder,
) -> list[dict[str, str]]:
    """Collect rows by parsing markdown files in state folders."""
    by_state = dict(folders)
    if state is not None:
        folder = by_state.get(state)
        if folder is None:
            return []
        selected = [(state, folder)]
    else:
        selected = folders

    rows: list[dict[str, str]] = []
    for folder_state, folder in selected:
        for path in _iter_markdown_files(folder):
            model = parser(path)
            rows.append(row_builder(model, folder_state, path))
    return rows


def _render_table(title: str, columns: list[str], rows: list[dict[str, str]]) -> None:
    table = Table(title=title)
    for name in columns:
        table.add_column(name)
    for row in rows:
        table.add_row(*(row[column.lower()] for column in columns))
    console.print(table)


@app.command()
def tasks(
    state: str | None = typer.Option(
        None, "--state", help="Filter by task state folder."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List tasks from the project task folders."""
    root = find_project_root(Path.cwd())
    rows = _collect_from_state_folders(
        [
            ("pending", root.tasks_pending),
            ("in-progress", root.tasks_in_progress),
            ("completed", root.tasks_completed),
            ("blocked", root.tasks_blocked),
        ],
        state,
        parse_task,
        lambda task, folder_state, _: {
            "id": task.id,
            "title": task.title,
            "state": folder_state,
            "priority": task.priority,
            "assigned-role": task.assigned_role,
        },
    )
    if as_json:
        print_json(rows)
        return
    _render_table("Tasks", ["ID", "Title", "State", "Priority", "Assigned-Role"], rows)


@app.command()
def bugs(
    state: str | None = typer.Option(
        None, "--state", help="Filter by bug state folder."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List bugs from the project bug folders."""
    root = find_project_root(Path.cwd())
    rows = _collect_from_state_folders(
        [
            ("open", root.bugs_open),
            ("in-progress", root.bugs_in_progress),
            ("resolved", root.bugs_resolved),
        ],
        state,
        parse_bug,
        lambda bug, folder_state, _: {
            "id": bug.id,
            "title": bug.title,
            "state": folder_state,
            "severity": bug.severity,
        },
    )
    if as_json:
        print_json(rows)
        return
    _render_table("Bugs", ["ID", "Title", "State", "Severity"], rows)


@app.command()
def specs(
    state: str | None = typer.Option(
        None, "--state", help="Filter by state where applicable."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List specs from the project specs folder."""
    _ = state
    root = find_project_root(Path.cwd())
    rows: list[dict[str, str]] = []
    for path in _iter_markdown_files(root.specs):
        spec = parse_spec(path)
        rows.append(
            {
                "id": path.stem,
                "title": spec.title,
                "status": spec.status,
                "version": spec.version,
            }
        )
    if as_json:
        print_json(rows)
        return
    _render_table("Specs", ["ID", "Title", "Status", "Version"], rows)


@app.command()
def adrs(
    state: str | None = typer.Option(
        None, "--state", help="Filter by state where applicable."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List ADRs from the project decisions folder."""
    _ = state
    root = find_project_root(Path.cwd())
    rows: list[dict[str, str]] = []
    for path in _iter_markdown_files(root.decisions):
        adr = parse_adr(path)
        rows.append(
            {
                "id": adr.id,
                "title": adr.title,
                "status": adr.status,
            }
        )
    if as_json:
        print_json(rows)
        return
    _render_table("ADRs", ["ID", "Title", "Status"], rows)


@app.command("change-requests")
def change_requests(
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List change requests from the project change-requests folder."""
    root = find_project_root(Path.cwd())
    rows: list[dict[str, str]] = []
    for path in _iter_markdown_files(root.change_requests):
        cr = parse_change_request(path)
        rows.append(
            {
                "id": cr.id,
                "title": cr.title,
                "state": cr.status,
            }
        )
    if as_json:
        print_json(rows)
        return
    _render_table("Change Requests", ["ID", "Title", "State"], rows)
