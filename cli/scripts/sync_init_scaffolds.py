#!/usr/bin/env python3
"""Generate bundled init scaffolds from package-owned source assets."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_markers import render_markers  # noqa: E402

PROJECT_LEAF_DIRS = (
    "specs",
    "tasks/pending",
    "tasks/in-progress",
    "tasks/completed",
    "tasks/blocked",
    "bugs/open",
    "bugs/in-progress",
    "bugs/resolved",
    "change-requests",
    "decisions",
    "docs",
)

TOOLS = ("claude", "codex")

VERSION_OVERRIDE_ENV_VAR = "SETUPTOOLS_SCM_PRETEND_VERSION"
PI_VERSION_FILE = Path("resources") / "version.txt"
_HATCH_VERSION_COMMAND = (
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
)


class VersionError(ValueError):
    """The framework version cannot be determined from the source tree."""


def _cli_root_from_script(script_path: Path) -> Path:
    # script lives at <repo>/cli/scripts/sync_init_scaffolds.py
    return script_path.resolve().parents[1]


def compute_framework_version(cli_root: Path, env: Mapping[str, str]) -> str:
    """Return the distribution version hatch-vcs derives from the source tree.

    Asks hatchling, which applies cli/pyproject.toml's raw-options, instead of
    reading installed metadata: an editable install freezes its version at
    install time. The override variable is the one hatch-vcs itself honours.
    """
    override = env.get(VERSION_OVERRIDE_ENV_VAR, "").strip()
    if override:
        return override
    try:
        result = subprocess.run(
            _HATCH_VERSION_COMMAND,
            cwd=cli_root,
            env=dict(env),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        raise VersionError(
            f"cannot determine the framework version from {cli_root}: "
            f"{detail.strip()}. Run the sync inside the git checkout with `uv` "
            f"installed, or set {VERSION_OVERRIDE_ENV_VAR}."
        ) from error
    version = result.stdout.strip()
    if not version:
        raise VersionError(
            f"cannot determine the framework version from {cli_root}: "
            "hatchling printed nothing"
        )
    return version


def _write_pi_version(pi_root: Path, version: str) -> None:
    version_file = pi_root / PI_VERSION_FILE
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(version + "\n", encoding="utf-8")


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


def _replace_project_skeleton(destination: Path, source: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)

    for leaf in PROJECT_LEAF_DIRS:
        leaf_dir = destination / leaf
        leaf_dir.mkdir(parents=True, exist_ok=True)
        (leaf_dir / ".gitkeep").write_text("", encoding="utf-8")

    for root_file in ("CLAUDE.md", "AGENTS.md", ".gitignore"):
        src = source / root_file
        if not src.is_file():
            raise FileNotFoundError(
                f"Expected project skeleton root file does not exist: {src}"
            )
        shutil.copy2(src, destination / root_file)


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


def _load_command_map(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Expected command map does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _replace_generated_skills(
    source_root: Path, destination_root: Path, command_map: dict[str, Any]
) -> None:
    destination_root.mkdir(parents=True, exist_ok=True)
    for tool in TOOLS:
        tool_skill_root = destination_root / tool / "skills"
        if tool_skill_root.exists():
            shutil.rmtree(tool_skill_root)
        tool_skill_root.mkdir(parents=True, exist_ok=True)

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
            rendered_header = render_markers(
                headers[tool], tool, command_map, str(metadata_path)
            )
            rendered_body = render_markers(body, tool, command_map, str(body_path))
            skill_output_dir = destination_root / tool / "skills" / skill_dir.name
            skill_output_dir.mkdir(parents=True, exist_ok=True)
            skill_output = rendered_header + "\n\n" + rendered_body
            (skill_output_dir / "SKILL.md").write_text(skill_output, encoding="utf-8")


def sync_init_scaffolds(cli_root: Path, env: Mapping[str, str] | None = None) -> None:
    version = compute_framework_version(cli_root, os.environ if env is None else env)
    init_root = cli_root / "src" / "ai_team" / "init"
    scaffolds_root = init_root / "scaffolds"
    sources_root = init_root / "sources"

    scaffolds_root.mkdir(parents=True, exist_ok=True)
    _replace_project_skeleton(scaffolds_root / "project", sources_root / "project")
    _replace_generated_skills(
        sources_root / "skills",
        scaffolds_root,
        _load_command_map(sources_root / "command_map.json"),
    )
    _replace_tree(
        sources_root / "agents" / "claude",
        scaffolds_root / "claude" / "agents",
    )
    _replace_tree(
        sources_root / "agents" / "codex",
        scaffolds_root / "codex" / "agents",
    )
    _write_pi_version(cli_root.parent / "pi", version)


def main() -> None:
    cli_root = _cli_root_from_script(Path(__file__))
    try:
        sync_init_scaffolds(cli_root)
    except ValueError as error:
        sys.exit(f"sync failed: {error}")
    print(f"Synchronized init scaffolds in {cli_root / 'src/ai_team/init/scaffolds'}")
    print("Run this script before `uv build` to refresh bundled scaffold output.")


if __name__ == "__main__":
    main()
