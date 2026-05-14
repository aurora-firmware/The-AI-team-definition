"""`ai-team status` command for Gate 5 inline summaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import typer
from rich.markdown import Markdown

from ai_team.core.fs import read_artifact
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.models import parse_bug, parse_task
from ai_team.render import console, print_json

NAME = "status"
app = typer.Typer(help="Show a Gate 5 status summary.", invoke_without_command=True)


@dataclass(frozen=True)
class InProgressTask:
    id: str
    title: str
    assigned_role: str


@dataclass(frozen=True)
class BlockedTask:
    id: str
    title: str
    blocking_reason: str


@dataclass(frozen=True)
class CriticalBug:
    id: str
    title: str
    severity: str


def _should_skip(path: Path) -> bool:
    return path.name == ".gitkeep" or path.match("TEMPLATE-*.md")


def _iter_markdown_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        path
        for path in folder.glob("*.md")
        if path.is_file() and not _should_skip(path)
    )


def _count(folder: Path) -> int:
    return len(_iter_markdown_files(folder))


def _latest_work_log_line(task_path: Path) -> str:
    _, body = read_artifact(task_path, "task")

    lines = body.splitlines()
    start = None
    end = len(lines)
    for idx, line in enumerate(lines):
        if line.strip() == "## Work Log":
            start = idx + 1
            continue
        if start is not None and line.startswith("## "):
            end = idx
            break

    if start is None:
        return "not recorded"

    work_log = lines[start:end]
    heading_indexes = [
        idx for idx, line in enumerate(work_log) if line.startswith("### Session")
    ]
    if not heading_indexes:
        return "not recorded"

    last_heading = heading_indexes[-1]
    for line in work_log[last_heading + 1 :]:
        stripped = line.strip()
        if stripped:
            return stripped
    return "not recorded"


def _blocking_reason(task_path: Path) -> str:
    task = parse_task(task_path)
    source_map = task._source_map or {}
    for key in ("blocking-reason", "blocking_reason"):
        value = source_map.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return _latest_work_log_line(task_path)


def _latest_integration_result(root: ProjectRoot) -> str:
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(root.repo),
                "log",
                "--all",
                "--grep=merge\\|integration\\|verification\\|test",
                "-n",
                "1",
                "--pretty=format:%s",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError, subprocess.CalledProcessError:
        return "not found"

    value = completed.stdout.strip()
    if not value:
        return "not found"
    return value


def _payload(root: ProjectRoot) -> dict[str, object]:
    in_progress_tasks: list[InProgressTask] = []
    for path in _iter_markdown_files(root.tasks_in_progress):
        task = parse_task(path)
        in_progress_tasks.append(
            InProgressTask(
                id=task.id,
                title=task.title,
                assigned_role=task.assigned_role,
            )
        )

    blocked_tasks: list[BlockedTask] = []
    for path in _iter_markdown_files(root.tasks_blocked):
        task = parse_task(path)
        blocked_tasks.append(
            BlockedTask(
                id=task.id,
                title=task.title,
                blocking_reason=_blocking_reason(path),
            )
        )

    critical_high_bugs: list[CriticalBug] = []
    for path in _iter_markdown_files(root.bugs_open):
        bug = parse_bug(path)
        if bug.severity in {"critical", "high"}:
            critical_high_bugs.append(
                CriticalBug(id=bug.id, title=bug.title, severity=bug.severity)
            )

    payload: dict[str, object] = {
        "counts": {
            "specs_active": _count(root.specs),
            "tasks": {
                "pending": _count(root.tasks_pending),
                "in_progress": _count(root.tasks_in_progress),
                "completed": _count(root.tasks_completed),
                "blocked": _count(root.tasks_blocked),
            },
            "bugs": {
                "open": _count(root.bugs_open),
                "in_progress": _count(root.bugs_in_progress),
                "resolved": _count(root.bugs_resolved),
            },
            "adrs": _count(root.decisions),
        },
        "in_progress_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "assigned_role": task.assigned_role,
            }
            for task in in_progress_tasks
        ],
        "blocked_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "blocking_reason": task.blocking_reason,
            }
            for task in blocked_tasks
        ],
        "critical_high_open_bugs": [
            {"id": bug.id, "title": bug.title, "severity": bug.severity}
            for bug in critical_high_bugs
        ],
        "latest_integration_result": _latest_integration_result(root),
    }
    return payload


def _list_lines(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _to_markdown(payload: dict[str, object]) -> str:
    counts = payload["counts"]
    assert isinstance(counts, dict)
    tasks = counts["tasks"]
    assert isinstance(tasks, dict)
    bugs = counts["bugs"]
    assert isinstance(bugs, dict)

    in_progress = payload["in_progress_tasks"]
    assert isinstance(in_progress, list)
    blocked = payload["blocked_tasks"]
    assert isinstance(blocked, list)
    critical_high = payload["critical_high_open_bugs"]
    assert isinstance(critical_high, list)

    in_progress_lines = _list_lines(
        [
            f"{row['id']} — {row['title']} ({row['assigned_role']})"
            for row in in_progress
            if isinstance(row, dict)
        ]
    )
    blocked_lines = _list_lines(
        [
            f"{row['id']} — {row['title']}: {row['blocking_reason']}"
            for row in blocked
            if isinstance(row, dict)
        ]
    )
    critical_high_lines = _list_lines(
        [
            f"{row['id']} — {row['title']} ({row['severity']})"
            for row in critical_high
            if isinstance(row, dict)
        ]
    )

    return (
        "## Status Report\n\n"
        "### Summary\n"
        f"- Active specs: {counts['specs_active']}\n"
        f"- Pending tasks: {tasks['pending']}\n"
        f"- In progress: {tasks['in_progress']}\n"
        f"- Completed: {tasks['completed']}\n"
        f"- Blocked: {tasks['blocked']}\n"
        f"- Open bugs: {bugs['open']}\n"
        f"- Bugs in progress: {bugs['in_progress']}\n"
        f"- Resolved bugs: {bugs['resolved']}\n"
        f"- ADRs: {counts['adrs']}\n"
        f"- Latest integration result: {payload['latest_integration_result']}\n\n"
        "### In Progress\n"
        f"{in_progress_lines}\n\n"
        "### Blocked\n"
        f"{blocked_lines}\n\n"
        "### Critical/High Bugs\n"
        f"{critical_high_lines}\n"
    )


@app.callback()
def default(
    as_json: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    root = find_project_root(Path.cwd())
    payload = _payload(root)
    if as_json:
        print_json(payload)
        return
    console.print(Markdown(_to_markdown(payload)))
