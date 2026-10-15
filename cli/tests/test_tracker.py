"""Tests for the local work-item tracker (spec S-006)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.core.locator import find_project_root
from ai_team.core.models import parse_change_request
from ai_team.core.tracker import resolve_tracker_dir


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _git_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    return path


def _invoke(*args: str):
    from ai_team.cli import app

    return CliRunner().invoke(app, list(args))


@pytest.fixture
def initialized_repo(monkeypatch, tmp_path) -> Path:
    """A committed `ai-team init` repository with the cwd set to its root."""
    repo = _git_repo(tmp_path / "repo")
    result = _invoke("init", str(repo), "--tools", "claude", "--no-interactive")
    assert result.exit_code == 0, result.output
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    monkeypatch.chdir(repo)
    return repo


def test_tracker_path_defaults_to_repository_root(initialized_repo):
    result = _invoke("tracker", "path")

    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == str(initialized_repo / ".ai-team" / "tracker")


def test_every_worktree_resolves_the_same_tracker(initialized_repo, monkeypatch):
    worktree = initialized_repo.parent / "linked"
    _git(initialized_repo, "worktree", "add", "-q", "-b", "task/T-001", str(worktree))
    # .ai-team.toml is committed here, so the linked worktree has the marker too.
    monkeypatch.chdir(worktree)

    result = _invoke("tracker", "path")

    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == str(initialized_repo / ".ai-team" / "tracker")
    assert resolve_tracker_dir(worktree) == resolve_tracker_dir(initialized_repo)


@pytest.mark.parametrize("configured", ["work/items", "ABSOLUTE", "~/items"])
def test_tracker_dir_honours_relative_absolute_and_home_paths(
    tmp_path, monkeypatch, configured
):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    repo = tmp_path / "repo"
    (repo / "project").mkdir(parents=True)
    value = str(tmp_path / "abs") if configured == "ABSOLUTE" else configured
    (repo / ".ai-team.toml").write_text(
        f'[project]\ndir = "project"\n\n[tracker]\ndir = "{value}"\n', encoding="utf-8"
    )

    root = find_project_root(repo)

    expected = {
        "work/items": repo / "work" / "items",
        "ABSOLUTE": tmp_path / "abs",
        "~/items": tmp_path / "home" / "items",
    }[configured]
    assert root.tracker == expected
    assert root.tasks == expected / "tasks"


def test_full_lifecycle_leaves_the_working_tree_clean(initialized_repo):
    created = json.loads(_invoke("task", "new", "Ship it", "--json").stdout)
    for args in (
        ("task", "start", created["id"]),
        ("task", "block", created["id"], "--reason", "waiting"),
        ("task", "unblock", created["id"]),
        ("task", "complete", created["id"]),
        ("bug", "new", "Crash", "--json"),
        ("bug", "start", "B-001"),
        ("bug", "resolve", "B-001"),
        ("change-request", "new", "Tweak scope", "--json"),
        ("change-request", "set-status", "CR-001", "approved"),
    ):
        result = _invoke(*args)
        assert result.exit_code == 0, (args, result.output)

    Path(created["path"]).write_text(
        Path(created["path"]).read_text(encoding="utf-8") + "\nReview Verdict\n",
        encoding="utf-8",
    )

    assert _git(initialized_repo, "status", "--porcelain") == ""


def test_planned_tasks_stay_out_of_the_pending_queue_until_activated(
    initialized_repo,
):
    _invoke("task", "new", "Planned work", "--status", "planned", "--spec", "S-001")
    _invoke("task", "new", "Other plan", "--status", "planned", "--spec", "CR-002")
    _invoke("task", "new", "Ready work")

    pending = json.loads(
        _invoke("list", "tasks", "--state", "pending", "--json").stdout
    )
    assert [row["id"] for row in pending] == ["T-003"]

    planned = json.loads(
        _invoke(
            "list", "tasks", "--state", "planned", "--spec", "S-001", "--json"
        ).stdout
    )
    assert [row["id"] for row in planned] == ["T-001"]
    assert set(planned[0]) == {"id", "title", "state", "priority", "assigned-role"}

    assert _invoke("task", "set-status", "T-001", "pending").exit_code == 0
    pending = json.loads(
        _invoke("list", "tasks", "--state", "pending", "--json").stdout
    )
    assert [row["id"] for row in pending] == ["T-001", "T-003"]


def test_change_request_set_status_and_show(initialized_repo):
    created = json.loads(_invoke("change-request", "new", "Tweak", "--json").stdout)

    result = _invoke("change-request", "set-status", created["id"], "rejected")
    assert result.exit_code == 0, result.output
    assert parse_change_request(Path(created["path"])).status == "rejected"

    shown = json.loads(_invoke("show", created["id"], "--json").stdout)
    assert shown["path"] == created["path"]
    assert shown["frontmatter"]["status"] == "rejected"

    rows = json.loads(
        _invoke("list", "change-requests", "--state", "rejected", "--json").stdout
    )
    assert [row["id"] for row in rows] == ["CR-001"]


def test_commands_warn_while_legacy_folders_hold_files(initialized_repo):
    legacy = initialized_repo / "project" / "tasks" / "pending" / "T-009-old.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("legacy", encoding="utf-8")

    result = _invoke("list", "tasks", "--json")

    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert "legacy work-item folders" in result.stderr
    assert str(initialized_repo / "project" / "tasks") in result.stderr
    assert "Migrating to the local tracker" in result.stderr

    legacy.unlink()
    result = _invoke("list", "tasks", "--json")
    assert "legacy" not in result.stderr
