"""Tests for T-083: structured results for task and bug commands."""

import importlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.commands.bug import create_bug, resolve_bug, start_bug
from ai_team.commands.task import (
    block_task,
    complete_task,
    create_task,
    start_task,
    unblock_task,
)
from ai_team.core.locator import ProjectRoot, find_project_root
from ai_team.core.result import Result

TASK_STATES = ("pending", "in-progress", "completed", "blocked")
BUG_STATES = ("open", "in-progress", "resolved")


def _root(tmp_path: Path) -> ProjectRoot:
    for state in TASK_STATES:
        (tmp_path / "project" / "tasks" / state).mkdir(parents=True)
    for state in BUG_STATES:
        (tmp_path / "project" / "bugs" / state).mkdir(parents=True)
    return find_project_root(tmp_path, root=tmp_path)


# AC-1
@pytest.mark.parametrize(
    "handler,args",
    [
        (create_task, ("Alpha",)),
        (create_bug, ("Alpha",)),
    ],
)
def test_create_handlers_run_with_explicit_root_without_cwd(
    tmp_path, monkeypatch, handler, args
):
    root = _root(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = handler(root, *args)

    assert result.status == 0
    assert result.message is None and result.hint is None
    assert Path(result.payload["path"]).is_file()
    assert Path(result.payload["path"]).is_relative_to(tmp_path / "project")


def test_task_lifecycle_handlers_walk_a_task_through_every_state(tmp_path, monkeypatch):
    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path / "project")
    task_id = create_task(root, "Alpha").payload["id"]

    started = start_task(root, task_id)
    assert started.status == 0
    assert Path(started.payload["path"]).parent == root.tasks_in_progress

    blocked = block_task(root, task_id, "waiting")
    assert Path(blocked.payload["path"]).parent == root.tasks_blocked
    assert "Blocked: waiting" in Path(blocked.payload["path"]).read_text()

    unblocked = unblock_task(root, task_id)
    assert Path(unblocked.payload["path"]).parent == root.tasks_in_progress

    completed = complete_task(root, task_id)
    assert Path(completed.payload["path"]).parent == root.tasks_completed
    assert completed.payload["id"] == task_id


def test_bug_lifecycle_handlers_walk_a_bug_through_every_state(tmp_path, monkeypatch):
    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path / "project")
    bug_id = create_bug(root, "Alpha").payload["id"]

    started = start_bug(root, bug_id)
    assert Path(started.payload["path"]).parent == root.bugs_in_progress

    resolved = resolve_bug(root, bug_id)
    assert Path(resolved.payload["path"]).parent == root.bugs_resolved
    assert resolved.payload["id"] == bug_id


# AC-2
@pytest.mark.parametrize(
    "argv,module,handler_name",
    [
        (["task", "new", "Alpha"], "task", "create_task"),
        (["bug", "new", "Alpha"], "bug", "create_bug"),
    ],
)
def test_json_output_equals_handler_payload(
    tmp_path, monkeypatch, argv, module, handler_name
):
    from ai_team.cli import app

    _root(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = {"id": "X-1", "path": "/somewhere", "sentinel": [1, 2]}
    command_module = importlib.import_module(f"ai_team.commands.{module}")
    monkeypatch.setattr(
        command_module, handler_name, lambda *a, **k: Result(0, payload)
    )

    cli = CliRunner().invoke(app, [*argv, "--json"])

    assert cli.exit_code == 0
    assert json.loads(cli.stdout) == payload


# AC-3
def test_task_start_when_already_in_progress_succeeds_with_todays_text(
    tmp_path, monkeypatch
):
    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)
    task_id = create_task(root, "Alpha").payload["id"]
    start_task(root, task_id)

    result = start_task(root, task_id)

    assert result.status == 0
    assert result.message == f"Task {task_id} already in in-progress."


def test_bug_resolve_when_already_resolved_succeeds_with_todays_text(
    tmp_path, monkeypatch
):
    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)
    bug_id = create_bug(root, "Alpha").payload["id"]
    start_bug(root, bug_id)
    resolve_bug(root, bug_id)

    result = resolve_bug(root, bug_id)

    assert result.status == 0
    assert result.message == f"Bug {bug_id} already in resolved."


def test_cli_prints_already_in_state_text_on_stdout_and_exits_zero(
    tmp_path, monkeypatch
):
    from ai_team.cli import app

    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)
    task_id = create_task(root, "Alpha").payload["id"]
    start_task(root, task_id)

    cli = CliRunner().invoke(app, ["task", "start", task_id])

    assert cli.exit_code == 0
    assert cli.stdout == f"Task {task_id} already in in-progress.\n"


# AC-4
def test_task_not_found_result_carries_todays_message(tmp_path):
    root = _root(tmp_path)

    result = start_task(root, "T-999")

    searched = ", ".join(
        str(p)
        for p in (
            root.tasks_pending,
            root.tasks_in_progress,
            root.tasks_completed,
            root.tasks_blocked,
        )
    )
    assert result.status == 1
    assert result.payload is None
    assert result.message == f"Task 'T-999' not found. Searched folders: {searched}"


def test_bug_not_found_result_carries_todays_message(tmp_path):
    root = _root(tmp_path)

    result = resolve_bug(root, "B-999")

    searched = ", ".join(
        str(p) for p in (root.bugs_open, root.bugs_in_progress, root.bugs_resolved)
    )
    assert result.status == 1
    assert result.message == f"Bug 'B-999' not found. Searched folders: {searched}"


def test_cli_prints_not_found_on_stderr_and_exits_one(tmp_path, monkeypatch):
    from ai_team.cli import app

    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)

    cli = CliRunner().invoke(app, ["task", "complete", "T-999"])

    assert cli.exit_code == 1
    assert cli.stdout == ""
    assert start_task(root, "T-999").text() in cli.stderr


# AC-5
def test_cli_transition_prints_only_destination_path(tmp_path, monkeypatch):
    from ai_team.cli import app

    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)
    task_id = create_task(root, "Alpha").payload["id"]

    cli = CliRunner().invoke(app, ["task", "start", task_id])

    assert cli.exit_code == 0
    printed = Path(cli.stdout.strip())
    assert printed.parent == root.tasks_in_progress.resolve()
    assert cli.stdout == f"{printed}\n"


def test_cli_new_task_prints_path_and_json_shape_is_id_and_path(tmp_path, monkeypatch):
    from ai_team.cli import app

    root = _root(tmp_path)
    monkeypatch.chdir(tmp_path)

    plain = CliRunner().invoke(app, ["bug", "new", "Alpha"])
    as_json = CliRunner().invoke(app, ["task", "new", "Beta", "--json"])

    assert Path(plain.stdout.strip()).parent == root.bugs_open.resolve()
    assert set(json.loads(as_json.stdout)) == {"id", "path"}
