"""Tests for the pi target of the scaffold sync (S-005 Component 2)."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from tests.test_init_scaffolds import _setup_fake_repo

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
