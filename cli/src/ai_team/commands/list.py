"""`ai-team list` command group for listing project artifacts."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import (
    parse_adr,
    parse_bug,
    parse_change_request,
    parse_spec,
    parse_task,
)
from ai_team.core.result import Result
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


def list_tasks(root: ProjectRoot, state: str | None) -> Result:
    """Return task rows (the ``--json`` payload), optionally for one state folder."""
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
    return Result(status=0, payload=rows)


def list_bugs(root: ProjectRoot, state: str | None) -> Result:
    """Return bug rows (the ``--json`` payload), optionally for one state folder."""
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
    return Result(status=0, payload=rows)


def list_specs(root: ProjectRoot) -> Result:
    """Return spec rows (the ``--json`` payload)."""
    rows: list[dict[str, str]] = []
    for path in _iter_markdown_files(root.specs):
        spec = parse_spec(path)
        rows.append(
            {
                "id": spec.id or path.stem,
                "title": spec.title,
                "status": spec.status,
                "version": spec.version,
            }
        )
    return Result(status=0, payload=rows)


def list_adrs(root: ProjectRoot) -> Result:
    """Return ADR rows (the ``--json`` payload)."""
    rows: list[dict[str, str]] = []
    for path in _iter_markdown_files(root.decisions):
        adr = parse_adr(path)
        rows.append({"id": adr.id, "title": adr.title, "status": adr.status})
    return Result(status=0, payload=rows)


def list_change_requests(root: ProjectRoot) -> Result:
    """Return change-request rows (the ``--json`` payload)."""
    rows: list[dict[str, str]] = []
    for path in _iter_markdown_files(root.change_requests):
        cr = parse_change_request(path)
        rows.append({"id": cr.id, "title": cr.title, "state": cr.status})
    return Result(status=0, payload=rows)


def _emit_rows(result: Result, as_json: bool, title: str, columns: list[str]) -> None:
    """Print a list result as JSON or as the Rich table the CLI always printed."""
    if as_json:
        print_json(result.payload)
        return
    _render_table(title, columns, result.payload)


@app.command()
def tasks(
    state: str | None = typer.Option(
        None, "--state", help="Filter by task state folder."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List tasks from the project task folders."""
    result = list_tasks(find_project_root(Path.cwd()), state)
    _emit_rows(
        result, as_json, "Tasks", ["ID", "Title", "State", "Priority", "Assigned-Role"]
    )


@app.command()
def bugs(
    state: str | None = typer.Option(
        None, "--state", help="Filter by bug state folder."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List bugs from the project bug folders."""
    result = list_bugs(find_project_root(Path.cwd()), state)
    _emit_rows(result, as_json, "Bugs", ["ID", "Title", "State", "Severity"])


@app.command()
def specs(
    state: str | None = typer.Option(
        None, "--state", help="Filter by state where applicable."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List specs from the project specs folder."""
    _ = state
    result = list_specs(find_project_root(Path.cwd()))
    _emit_rows(result, as_json, "Specs", ["ID", "Title", "Status", "Version"])


@app.command()
def adrs(
    state: str | None = typer.Option(
        None, "--state", help="Filter by state where applicable."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List ADRs from the project decisions folder."""
    _ = state
    result = list_adrs(find_project_root(Path.cwd()))
    _emit_rows(result, as_json, "ADRs", ["ID", "Title", "Status"])


@app.command("change-requests")
def change_requests(
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """List change requests from the project change-requests folder."""
    result = list_change_requests(find_project_root(Path.cwd()))
    _emit_rows(result, as_json, "Change Requests", ["ID", "Title", "State"])
