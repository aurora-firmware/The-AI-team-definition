#!/usr/bin/env python3
"""Generate bundled init scaffolds from package-owned source assets."""

from __future__ import annotations

import shutil
import tomllib
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

TOOLS = ("claude", "codex")


def _cli_root_from_script(script_path: Path) -> Path:
    # script lives at <repo>/cli/scripts/sync_init_scaffolds.py
    return script_path.resolve().parents[1]


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


def _load_skill_metadata(path: Path) -> dict[str, str]:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    headers: dict[str, str] = {}
    for tool in TOOLS:
        tool_config = raw.get(tool, {})
        header = tool_config.get("header")
        if not isinstance(header, str) or not header.strip():
            raise ValueError(f"Missing [{tool}].header in {path}")
        headers[tool] = header.strip()
    return headers


def _replace_generated_skills(source_root: Path, destination_root: Path) -> None:
    if destination_root.exists():
        shutil.rmtree(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)

    if not source_root.is_dir():
        raise FileNotFoundError(
            f"Expected skill source directory does not exist: {source_root}"
        )

    for skill_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        body_path = skill_dir / "body.md"
        metadata_path = skill_dir / "metadata.toml"
        if not body_path.is_file():
            raise FileNotFoundError(
                f"Expected skill body file does not exist: {body_path}"
            )
        if not metadata_path.is_file():
            raise FileNotFoundError(
                f"Expected skill metadata file does not exist: {metadata_path}"
            )

        body = body_path.read_text(encoding="utf-8")
        headers = _load_skill_metadata(metadata_path)

        for tool in TOOLS:
            skill_output_dir = destination_root / tool / "skills" / skill_dir.name
            skill_output_dir.mkdir(parents=True, exist_ok=True)
            skill_output = headers[tool] + "\n\n" + body
            (skill_output_dir / "SKILL.md").write_text(skill_output, encoding="utf-8")


def sync_init_scaffolds(cli_root: Path) -> None:
    init_root = cli_root / "src" / "ai_team" / "init"
    scaffolds_root = init_root / "scaffolds"
    sources_root = init_root / "sources"

    scaffolds_root.mkdir(parents=True, exist_ok=True)
    _replace_project_skeleton(scaffolds_root / "project")
    _replace_generated_skills(
        sources_root / "skills",
        scaffolds_root,
    )
    _replace_tree(
        sources_root / "agents" / "claude",
        scaffolds_root / "claude" / "agents",
    )
    _replace_tree(
        sources_root / "agents" / "codex",
        scaffolds_root / "codex" / "agents",
    )


def main() -> None:
    cli_root = _cli_root_from_script(Path(__file__))
    sync_init_scaffolds(cli_root)
    print(f"Synchronized init scaffolds in {cli_root / 'src/ai_team/init/scaffolds'}")
    print("Run this script before `uv build` to refresh bundled scaffold output.")


if __name__ == "__main__":
    main()
