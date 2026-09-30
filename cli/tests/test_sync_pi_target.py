"""Tests for the pi target of the scaffold sync (S-005 Component 2)."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from tests.test_init_scaffolds import _setup_fake_repo, _write

VERSION_OVERRIDE = "SETUPTOOLS_SCM_PRETEND_VERSION"
FAKE_VERSION = "7.8.9.dev3+gabc1234"


def _cli_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_sync_module() -> ModuleType:
    path = _cli_root() / "scripts" / "sync_init_scaffolds.py"
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(
            "sync_init_scaffolds_under_test", path
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def _run_sync(
    repo: Path, env_overrides: dict[str, str | None]
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    for key, value in env_overrides.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )


def _sync_with_version(repo: Path) -> subprocess.CompletedProcess[str]:
    return _run_sync(repo, {VERSION_OVERRIDE: FAKE_VERSION})


def _hatch_version(cli_root: Path) -> str:
    env = {k: v for k, v in os.environ.items() if k != VERSION_OVERRIDE}
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--with",
            "hatchling",
            "--with",
            "hatch-vcs",
            "python",
            "-m",
            "hatchling",
            "version",
        ],
        cwd=cli_root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_version_override_is_used_when_set() -> None:
    sync = _load_sync_module()

    version = sync.compute_framework_version(_cli_root(), {VERSION_OVERRIDE: "1.2.3"})

    assert version == "1.2.3"


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv is required")
def test_version_equals_what_hatch_reports_for_the_source_tree() -> None:
    sync = _load_sync_module()

    environment = {k: v for k, v in os.environ.items() if k != VERSION_OVERRIDE}

    version = sync.compute_framework_version(_cli_root(), environment)

    assert version == _hatch_version(_cli_root())


def test_sync_writes_the_version_file_from_the_override(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    result = _sync_with_version(repo)

    assert result.returncode == 0, result.stderr
    version_file = repo / "pi" / "resources" / "version.txt"
    assert version_file.read_text(encoding="utf-8") == FAKE_VERSION + "\n"


def test_sync_fails_clearly_when_the_version_cannot_be_determined(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    result = _run_sync(repo, {VERSION_OVERRIDE: None})

    assert result.returncode != 0
    assert "cannot determine the framework version" in result.stderr
    assert not (repo / "pi" / "resources" / "version.txt").exists()


def test_pi_gitignore_ignores_the_generated_version_file() -> None:
    repo_root = _cli_root().parent

    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "pi/resources/version.txt"],
        cwd=repo_root,
    )

    assert result.returncode == 0


def _resources(repo: Path) -> Path:
    return repo / "pi" / "resources"


def _set_body(repo: Path, body: str) -> None:
    sources = repo / "cli" / "src" / "ai_team" / "init" / "sources"
    (sources / "skills" / "tdd" / "body.md").write_text(body, encoding="utf-8")


def test_sync_writes_pi_skill_with_derived_header_and_tool_instructions(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)
    _set_body(repo, "Run {{ai-team status}} using {{ai-team-cli|the CLI|the tool}}.\n")

    result = _sync_with_version(repo)

    assert result.returncode == 0, result.stderr
    skill = (_resources(repo) / "skills" / "tdd" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert skill == (
        "---\nname: tdd\ndescription: claude skill\n---\n\n"
        'Run the `ai_team` tool call `{"command": "status"}` using the tool.\n'
    )


def test_sync_writes_skill_call_inputs_for_each_skill(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)
    _set_body(repo, "Run {{ai-team status}}.\n\n```bash\n{{ai-team status}}\n```\n")

    _sync_with_version(repo)

    calls = json.loads(
        (_resources(repo) / "skill-calls" / "tdd.json").read_text(encoding="utf-8")
    )
    assert calls == [{"command": "status"}, {"command": "status"}]


def test_sync_writes_empty_skill_call_list_for_skill_without_calls(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    calls = (_resources(repo) / "skill-calls" / "tdd.json").read_text(encoding="utf-8")
    assert json.loads(calls) == []


def test_sync_fails_when_a_marker_cannot_be_rendered_for_pi(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)
    _set_body(repo, "Run {{ai-team bogus}}.\n")

    result = _sync_with_version(repo)

    assert result.returncode != 0
    assert "{{ai-team bogus}}" in result.stderr


def test_sync_copies_artifact_templates_to_pi_resources(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    assert (_resources(repo) / "templates" / "task.md").read_text(
        encoding="utf-8"
    ) == "---\nid: {id}\n---\n"


def test_sync_writes_project_skeleton_with_gitignore_and_leaf_dirs(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    skeleton = _resources(repo) / "project"
    assert (skeleton / ".gitignore").read_text(
        encoding="utf-8"
    ) == ".ai-team.lock\n.ai-team-ts.lock\n"
    assert (skeleton / "tasks" / "in-progress" / ".gitkeep").is_file()
    assert (skeleton / "CLAUDE.md").is_file()
    assert (skeleton / "AGENTS.md").is_file()


def test_sync_copies_root_guidance_templates(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    assert (_resources(repo) / "root" / "CLAUDE.md").read_text(
        encoding="utf-8"
    ) == "# Root Claude\n\n## Commands\n"
    assert (_resources(repo) / "root" / "AGENTS.md").is_file()


def test_sync_writes_scaffold_directory_list_for_check_layout(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    layout = json.loads(
        (_resources(repo) / "scaffold-dirs.json").read_text(encoding="utf-8")
    )
    assert layout["claude"] == ["agents", "skills", "skills/tdd"]
    assert layout["codex"] == ["agents", "skills", "skills/tdd"]
    assert "tasks/in-progress" in layout["project"]
    assert layout["project"] == sorted(layout["project"])


def test_sync_copies_the_command_map_unchanged(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    source = repo / "cli/src/ai_team/init/sources/command_map.json"
    assert (_resources(repo) / "command-map.json").read_bytes() == source.read_bytes()


def test_sync_removes_stale_pi_resources(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)
    _write(_resources(repo) / "skills" / "old" / "SKILL.md", "old\n")

    _sync_with_version(repo)

    assert not (_resources(repo) / "skills" / "old").exists()


def _snapshot(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_two_syncs_produce_identical_output(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)
    first = _snapshot(repo / "pi"), _snapshot(repo / "cli" / "src")
    _sync_with_version(repo)
    second = _snapshot(repo / "pi"), _snapshot(repo / "cli" / "src")

    assert first == second


def test_sync_leaves_claude_and_codex_output_unchanged_by_the_pi_target(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    _sync_with_version(repo)

    scaffolds = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"
    claude = (scaffolds / "claude" / "skills" / "tdd" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert claude.startswith("---\nname: tdd\ndescription: claude skill\n")
    assert sorted(path.name for path in scaffolds.iterdir()) == [
        "claude",
        "codex",
        "project",
    ]
