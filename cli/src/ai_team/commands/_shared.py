"""Helpers shared by tracker-aware commands (not a command module: no ``NAME``)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import typer

from ai_team.core.fs import read_artifact, write_artifact
from ai_team.core.ids import overview_exists
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.tracker import legacy_warning, legacy_work_item_dirs

OVERVIEW_HINT = (
    "Hint: this project has no system overview (S-000). "
    "Create one with `ai-team spec new --overview`, "
    "or ask your agent to use the new-system-overview skill."
)


def project_root() -> ProjectRoot:
    """Locate the project from the cwd and warn about unmigrated legacy folders."""
    root = find_project_root(Path.cwd())
    legacy = legacy_work_item_dirs(root.project_dir)
    if legacy:
        typer.echo(legacy_warning(legacy), err=True)
    return root


def hint_missing_overview(root: ProjectRoot) -> None:
    """Write the advisory missing-S-000 hint to stderr; stdout and exit codes are untouched."""
    if not overview_exists(root):
        typer.echo(OVERVIEW_HINT, err=True)


def template_body(template: str, label: str) -> str:
    """Return markdown body text after the YAML frontmatter block of *template*."""
    if not template.startswith("---"):
        raise ValueError(f"{label} template is missing opening frontmatter fence.")

    rest = template[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise ValueError(f"{label} template is missing closing frontmatter fence.")

    body = rest[close_idx + 5 :]
    if body.startswith("\n"):
        body = body[1:]
    return body


def append_work_log_entry(path: Path, kind: str, text: str) -> None:
    """Append a dated ``### Session N`` entry containing *text* under ``## Work Log``."""
    model, body = read_artifact(path, kind)  # type: ignore[arg-type]
    lines = body.splitlines()
    heading = "## Work Log"

    try:
        start = lines.index(heading)
    except ValueError:
        lines.extend(["", heading, ""])
        start = len(lines) - 3

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break

    session_numbers: list[int] = []
    for line in lines[start:end]:
        match = re.match(r"^### Session (\d+)\b", line)
        if match is not None:
            session_numbers.append(int(match.group(1)))
    next_session = max(session_numbers, default=0) + 1

    entry = ["", f"### Session {next_session} — {date.today().isoformat()}", text]
    lines = lines[:end] + entry + lines[end:]
    new_body = "\n".join(lines).rstrip() + "\n"
    write_artifact(path, model, new_body, overwrite=True)
