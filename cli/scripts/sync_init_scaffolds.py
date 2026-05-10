#!/usr/bin/env python3
"""Synchronize bundled init scaffolds from repository sources."""

from __future__ import annotations

import shutil
from pathlib import Path

PROJECT_LEAF_DIRS = (
    "specs",
    "tasks/pending",
    "tasks/in-progress",
    "tasks/completed",
    "tasks/blocked",
    "bugs/open",
    "bugs/in-progress",
    "bugs/resolved",
    "decisions",
    "docs",
)

COPY_SUBTREES = (("ai-process", "ai-process"),)


def _repo_root_from_script(script_path: Path) -> Path:
    # script lives at <repo>/cli/scripts/sync_init_scaffolds.py
    return script_path.resolve().parents[2]


def _replace_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Expected source directory does not exist: {source}")

    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )


def _replace_project_skeleton(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)

    for leaf in PROJECT_LEAF_DIRS:
        leaf_dir = destination / leaf
        leaf_dir.mkdir(parents=True, exist_ok=True)
        (leaf_dir / ".gitkeep").write_text("", encoding="utf-8")


def _replace_claude_snapshot(source_root: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)
    _replace_tree(source_root / "agents", destination / "agents")
    _replace_tree(source_root / "skills", destination / "skills")


def sync_init_scaffolds(repo_root: Path) -> None:
    scaffolds_root = repo_root / "cli" / "src" / "ai_team" / "init" / "scaffolds"
    scaffolds_root.mkdir(parents=True, exist_ok=True)

    _replace_project_skeleton(scaffolds_root / "project")
    _replace_claude_snapshot(repo_root / ".claude", scaffolds_root / "claude")

    for source_name, dest_name in COPY_SUBTREES:
        _replace_tree(repo_root / source_name, scaffolds_root / dest_name)


def main() -> None:
    repo_root = _repo_root_from_script(Path(__file__))
    sync_init_scaffolds(repo_root)
    print(f"Synchronized init scaffolds in {repo_root / 'cli/src/ai_team/init/scaffolds'}")
    print("Run this script before `uv build` to refresh bundled scaffold snapshots.")


if __name__ == "__main__":
    main()
