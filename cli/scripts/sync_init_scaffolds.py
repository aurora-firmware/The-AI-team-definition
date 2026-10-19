#!/usr/bin/env python3
"""Generate bundled init scaffolds from package-owned source assets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import tomllib
from pathlib import Path

PROJECT_LEAF_DIRS = (
    # Tasks, bugs, and change-requests live in the local tracker (spec S-006),
    # outside the project directory, so they are not scaffolded here.
    "specs",
    "decisions",
    "docs",
)

TOOLS = ("claude", "codex")

# Plugins are static files, so they ship rendered with the framework defaults.
# DEFAULT_PROJECT_DIR must match ai_team.core.locator.DEFAULT_PROJECT_DIR; a
# test keeps them in step.
DEFAULT_PROJECT_DIR = "ai-team"
PLUGIN_DIR = Path("plugins") / "ai-team"


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


def _replace_generated_skills(source_root: Path, destination_root: Path) -> None:
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
            skill_output_dir = destination_root / tool / "skills" / skill_dir.name
            skill_output_dir.mkdir(parents=True, exist_ok=True)
            skill_output = headers[tool] + "\n\n" + body
            (skill_output_dir / "SKILL.md").write_text(skill_output, encoding="utf-8")


def _load_config_module(cli_root: Path):
    """Load ai_team.core.config by path so the script runs without the package."""
    path = cli_root / "src" / "ai_team" / "core" / "config.py"
    spec = importlib.util.spec_from_file_location("_ai_team_config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _latest_release_version(repo_root: Path) -> str:
    """Return the newest release tag (``X.Y.Z``) of the repository, or ``0.0.0``."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "describe", "--tags", "--abbrev=0"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except OSError, subprocess.CalledProcessError:
        return "0.0.0"
    return completed.stdout.strip().removeprefix("v") or "0.0.0"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _render_tree(source: Path, destination: Path, render) -> None:
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(path.read_text(encoding="utf-8")), encoding="utf-8")


def _replace_plugin_package(
    cli_root: Path, plugin_source: Path, version: str | None
) -> None:
    """Generate the Claude Code and Codex plugin package and its marketplaces.

    Layout under the repository root:
      plugins/ai-team/.claude-plugin/plugin.json   Claude Code manifest
      plugins/ai-team/.codex-plugin/plugin.json    Codex manifest
      plugins/ai-team/skills/                      shared skills (SKILL.md)
      plugins/ai-team/agents/                      Claude Code agents
      .claude-plugin/marketplace.json              Claude Code marketplace
      .agents/plugins/marketplace.json             Codex marketplace
    """
    repo_root = cli_root.parent
    config = _load_config_module(cli_root)
    meta = tomllib.loads(plugin_source.read_text(encoding="utf-8"))
    plugin = meta["plugin"]
    name = plugin["name"]

    def render(text: str) -> str:
        return config.render_placeholders(
            text,
            project_dir=DEFAULT_PROJECT_DIR,
            integration_branch=config.DEFAULT_INTEGRATION_BRANCH,
        )

    package = repo_root / PLUGIN_DIR
    if package.exists():
        shutil.rmtree(package)

    scaffolds = cli_root / "src" / "ai_team" / "init" / "scaffolds"
    sources = cli_root / "src" / "ai_team" / "init" / "sources"
    # Claude and Codex skills are byte-identical (ADR-001), so both share one tree.
    _render_tree(scaffolds / "claude" / "skills", package / "skills", render)
    _render_tree(sources / "agents" / "claude", package / "agents", render)

    author = {"name": plugin["author"]}
    common = {
        "name": name,
        "version": version or _latest_release_version(repo_root),
        "description": plugin["description"],
        "author": author,
        "homepage": plugin["homepage"],
        "repository": plugin["repository"],
        "keywords": plugin["keywords"],
    }
    _write_json(package / ".claude-plugin" / "plugin.json", common)
    _write_json(
        package / ".codex-plugin" / "plugin.json",
        {
            **common,
            "skills": "./skills/",
            "interface": {
                **meta["codex"]["interface"],
                "category": plugin["category"],
            },
        },
    )

    source_path = "./" + PLUGIN_DIR.as_posix()
    _write_json(
        repo_root / ".claude-plugin" / "marketplace.json",
        {
            "name": name,
            "owner": author,
            "description": plugin["description"],
            "plugins": [
                {
                    "name": name,
                    "version": common["version"],
                    "source": source_path,
                    "description": plugin["description"],
                    "category": plugin["category"],
                    "keywords": plugin["keywords"],
                }
            ],
        },
    )
    _write_json(
        repo_root / ".agents" / "plugins" / "marketplace.json",
        {
            "name": name,
            "interface": {"displayName": meta["codex"]["interface"]["displayName"]},
            "plugins": [
                {
                    "name": name,
                    "source": {"source": "local", "path": source_path},
                    "policy": {
                        "installation": "AVAILABLE",
                        "authentication": "ON_INSTALL",
                    },
                    "category": plugin["category"],
                }
            ],
        },
    )


def sync_init_scaffolds(cli_root: Path, plugin_version: str | None = None) -> None:
    init_root = cli_root / "src" / "ai_team" / "init"
    scaffolds_root = init_root / "scaffolds"
    sources_root = init_root / "sources"

    scaffolds_root.mkdir(parents=True, exist_ok=True)
    _replace_project_skeleton(scaffolds_root / "project", sources_root / "project")
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
    plugin_source = sources_root / "plugin" / "plugin.toml"
    if plugin_source.is_file():
        _replace_plugin_package(cli_root, plugin_source, plugin_version)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin-version",
        help="Version written to the plugin manifests (default: newest release tag).",
    )
    args = parser.parse_args()
    cli_root = _cli_root_from_script(Path(__file__))
    sync_init_scaffolds(cli_root, args.plugin_version)
    print(f"Synchronized init scaffolds in {cli_root / 'src/ai_team/init/scaffolds'}")
    print(
        "Also refreshed the plugin package under plugins/ai-team/ and its marketplaces."
    )
    print("Run this script before `uv build` to refresh bundled scaffold output.")


if __name__ == "__main__":
    main()
