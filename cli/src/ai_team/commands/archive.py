"""`ai-team archive` command for archiving old completed tasks and resolved bugs."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import typer

from ai_team.core.fs import move_artifact
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import parse_bug, parse_task
from ai_team.core.result import Result
from ai_team.core.runtime import today

NAME = "archive"
app = typer.Typer(
    help="Archive old completed tasks and resolved bugs into project/archive/YYYY-MM/."
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


def _iter_markdown_files(folder: Path):
    if not folder.exists():
        return
    for path in sorted(folder.glob("*.md")):
        if path.name == ".gitkeep" or path.match("TEMPLATE-*.md"):
            continue
        yield path


def _created_date(path: Path) -> date:
    if path.name.startswith("T-"):
        model = parse_task(path)
    else:
        model = parse_bug(path)
    return date.fromisoformat(model.created)


def archive_artifacts(root: ProjectRoot, older_than: str, dry_run: bool) -> Result:
    """Archive (or, with ``dry_run``, list) completed tasks and resolved bugs."""
    try:
        delta = _parse_older_than(older_than)
    except ValueError as exc:
        return Result(status=1, message=str(exc))

    archive_root = root.project_dir / "archive"
    cutoff = today() - delta

    moves: list[tuple[Path, Path]] = []
    for folder in (root.tasks_completed, root.bugs_resolved):
        for source in _iter_markdown_files(folder):
            created = _created_date(source)
            if created < cutoff:
                bucket = created.strftime("%Y-%m")
                moves.append((source, archive_root / bucket / source.name))

    if not dry_run:
        for source, destination in moves:
            destination.parent.mkdir(parents=True, exist_ok=True)
            move_artifact(source, destination)

    return Result(
        status=0,
        payload={
            "dry_run": dry_run,
            "moves": [
                {"source": str(source), "destination": str(destination)}
                for source, destination in moves
            ],
        },
    )


@app.callback(invoke_without_command=True)
def archive(
    older_than: str = typer.Option("90d", "--older-than"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Archive completed tasks and resolved bugs older than --older-than."""
    result = archive_artifacts(find_project_root(Path.cwd()), older_than, dry_run)
    if result.status:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    for move in result.payload["moves"]:
        if dry_run:
            typer.echo(f"WOULD MOVE: {move['source']} -> {move['destination']}")
        else:
            typer.echo(str(Path(move["destination"]).resolve()))
