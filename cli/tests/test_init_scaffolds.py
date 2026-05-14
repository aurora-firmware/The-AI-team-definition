"""Tests for T-024: bundled init scaffolds and sync helper."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _script_under_test() -> Path:
    return Path(__file__).resolve().parents[1] / "scripts" / "sync_init_scaffolds.py"


def _setup_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Source trees in the fake repository.
    _write(repo / ".claude" / "agents" / "planner.md", "planner\n")
    _write(repo / ".claude" / "skills" / "tdd" / "SKILL.md", "tdd\n")
    _write(repo / ".claude" / "settings.json", '{"model":"x"}\n')
    _write(repo / "ai-process" / "architecture" / "overview.md", "architecture\n")
    _write(repo / "ai-process" / "processes" / "flow.md", "flow\n")

    # Source project contains artifacts that must not be included in scaffold bundle.
    _write(repo / "project" / "tasks" / "completed" / "T-999.md", "artifact\n")
    _write(repo / "project" / "docs" / "coding_guidelines.md", "artifact\n")

    # Seed stale generated output to verify replacement behavior.
    _write(
        repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "project" / "old.txt",
        "old\n",
    )
    _write(
        repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "claude" / "old.txt",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "ai-process"
        / "old.txt",
        "old\n",
    )

    script = _script_under_test()
    assert script.exists(), "sync helper script is missing"
    copied_script = repo / "cli" / "scripts" / "sync_init_scaffolds.py"
    copied_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(script, copied_script)

    return repo


def test_sync_script_replaces_generated_subtrees_with_repo_snapshots(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    scaffolds_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"

    assert (scaffolds_root / "claude" / "agents" / "planner.md").read_text(
        encoding="utf-8"
    ) == "planner\n"
    assert (scaffolds_root / "claude" / "skills" / "tdd" / "SKILL.md").read_text(
        encoding="utf-8"
    ) == "tdd\n"
    assert (scaffolds_root / "ai-process" / "architecture" / "overview.md").read_text(
        encoding="utf-8"
    ) == "architecture\n"
    assert (scaffolds_root / "ai-process" / "processes" / "flow.md").read_text(
        encoding="utf-8"
    ) == "flow\n"
    assert not (scaffolds_root / "claude" / "settings.json").exists()

    assert not (scaffolds_root / "project" / "old.txt").exists()
    assert not (scaffolds_root / "claude" / "old.txt").exists()
    assert not (scaffolds_root / "ai-process" / "old.txt").exists()


def test_sync_script_creates_empty_project_skeleton_with_leaf_gitkeeps(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    project_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "project"

    expected_files = {
        Path("specs/.gitkeep"),
        Path("tasks/pending/.gitkeep"),
        Path("tasks/in-progress/.gitkeep"),
        Path("tasks/completed/.gitkeep"),
        Path("tasks/blocked/.gitkeep"),
        Path("bugs/open/.gitkeep"),
        Path("bugs/in-progress/.gitkeep"),
        Path("bugs/resolved/.gitkeep"),
        Path("decisions/.gitkeep"),
        Path("docs/.gitkeep"),
    }
    actual_files = {
        path.relative_to(project_root)
        for path in project_root.rglob("*")
        if path.is_file()
    }

    assert actual_files == expected_files
    assert not (project_root / "tasks" / "completed" / "T-999.md").exists()
    assert not (project_root / "docs" / "coding_guidelines.md").exists()
