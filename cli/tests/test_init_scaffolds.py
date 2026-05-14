"""Tests for package-owned init scaffold source generation."""

from __future__ import annotations

import os
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

    # Trap files at repository root that should never be read by the generator.
    _write(repo / ".claude", "trap\n")
    _write(repo / ".codex", "trap\n")
    _write(repo / "ai-process", "trap\n")

    # Package-owned skill source fixture.
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "skills"
        / "tdd"
        / "body.md",
        "# Test Skill Body\n\nRun the TDD cycle.\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "skills"
        / "tdd"
        / "metadata.toml",
        (
            "[claude]\n"
            "header = \"\"\"---\n"
            "name: tdd\n"
            "description: claude skill\n"
            "allowed-tools: Read\n"
            "---\"\"\"\n\n"
            "[codex]\n"
            "header = \"\"\"---\n"
            "name: tdd\n"
            "description: codex skill\n"
            "allowed-tools: Read\n"
            "---\"\"\"\n"
        ),
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "agents"
        / "claude"
        / "planner.md",
        "claude planner\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "agents"
        / "codex"
        / "planner.toml",
        "codex planner\n",
    )

    # Seed stale generated output that should be removed.
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "old"
        / "SKILL.md",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "project"
        / "old.txt",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "agents"
        / "old.md",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "agents"
        / "old.toml",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "skills"
        / "old"
        / "SKILL.md",
        "old\n",
    )

    script = _script_under_test()
    assert script.exists(), "sync helper script is missing"
    copied_script = repo / "cli" / "scripts" / "sync_init_scaffolds.py"
    copied_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(script, copied_script)

    return repo


def test_sync_script_generates_tool_skill_scaffolds_from_shared_body(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    scaffolds_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"
    shared_body = "# Test Skill Body\n\nRun the TDD cycle.\n"

    claude_text = (
        scaffolds_root / "claude" / "skills" / "tdd" / "SKILL.md"
    ).read_text(encoding="utf-8")
    codex_text = (
        scaffolds_root / "codex" / "skills" / "tdd" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert claude_text.startswith("---\nname: tdd\ndescription: claude skill\n")
    assert codex_text.startswith("---\nname: tdd\ndescription: codex skill\n")
    assert claude_text.split("\n\n", maxsplit=1)[1] == shared_body
    assert codex_text.split("\n\n", maxsplit=1)[1] == shared_body

    assert not (scaffolds_root / "claude" / "skills" / "old").exists()
    assert not (scaffolds_root / "codex" / "skills" / "old").exists()


def test_sync_script_copies_package_owned_agents_for_each_tool(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    scaffolds_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"

    assert (
        scaffolds_root / "claude" / "agents" / "planner.md"
    ).read_text(encoding="utf-8") == "claude planner\n"
    assert (
        scaffolds_root / "codex" / "agents" / "planner.toml"
    ).read_text(encoding="utf-8") == "codex planner\n"

    assert not (scaffolds_root / "claude" / "agents" / "old.md").exists()
    assert not (scaffolds_root / "codex" / "agents" / "old.toml").exists()


def test_sync_script_replaces_project_with_empty_lifecycle_skeleton(
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
        (Path(root) / file_name).relative_to(project_root)
        for root, _, file_names in os.walk(project_root)
        for file_name in file_names
    }

    assert actual_files == expected_files
    assert not (project_root / "old.txt").exists()
