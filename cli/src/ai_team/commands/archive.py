"""`ai-team archive` command for archiving old completed tasks and resolved bugs."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import typer

from ai_team.commands._shared import project_root
from ai_team.core.fs import move_artifact
from ai_team.core.models import parse_bug, parse_task
from ai_team.core.tracker import iter_items

NAME = "archive"
app = typer.Typer(
    help="Archive old completed tasks and resolved bugs into the tracker's archive/YYYY-MM/."
)

_DURATION_RE = re.compile(r"^(?P<amount>\d+)(?P<unit>[dwmy])$")


def _parse_older_than(value: str) -> timedelta:
    match = _DURATION_RE.fullmatch(value)
    if match is None:
        raise ValueError(
            f"Invalid --older-than '{value}'. Expected format: <number><d|w|m|y>."
        )

    amount = int(match.group("amount"))
    unit = match.group("unit")
    factors = {"d": 1, "w": 7, "m": 30, "y": 365}
    return timedelta(days=amount * factors[unit])


def _archivable(folder: Path, parser, done_status: str) -> list[tuple[Path, date]]:
    """Return ``(path, created)`` for work items in *folder* whose status is *done_status*."""
    items: list[tuple[Path, date]] = []
    for path in iter_items(folder):
        model = parser(path)
        if model.status == done_status and model.created:
            items.append((path, date.fromisoformat(model.created)))
    return items


@app.callback(invoke_without_command=True)
def archive(
    older_than: str = typer.Option("90d", "--older-than"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Archive completed tasks and resolved bugs older than --older-than."""
    try:
        delta = _parse_older_than(older_than)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    root = project_root()
    cutoff = date.today() - delta

    moves: list[tuple[Path, Path]] = []
    candidates = _archivable(root.tasks, parse_task, "completed") + _archivable(
        root.bugs, parse_bug, "resolved"
    )
    for source, created in candidates:
        if created < cutoff:
            bucket = created.strftime("%Y-%m")
            moves.append((source, root.archive / bucket / source.name))

    for source, destination in moves:
        if dry_run:
            typer.echo(f"WOULD MOVE: {source} -> {destination}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        move_artifact(source, destination)
        typer.echo(str(destination.resolve()))
