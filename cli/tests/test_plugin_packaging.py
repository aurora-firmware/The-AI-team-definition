"""Issue #30: Claude Code and Codex plugin packaging."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

CLI = Path(__file__).resolve().parents[1]
REPO = CLI.parent
PLUGIN = REPO / "plugins" / "ai-team"
SKILL_SOURCES = CLI / "src" / "ai_team" / "init" / "sources" / "skills"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifests_share_identity_and_version():
    claude = _json(PLUGIN / ".claude-plugin" / "plugin.json")
    codex = _json(PLUGIN / ".codex-plugin" / "plugin.json")
    claude_market = _json(REPO / ".claude-plugin" / "marketplace.json")["plugins"][0]

    assert claude["name"] == codex["name"] == claude_market["name"] == "ai-team"
    assert claude["version"] == codex["version"] == claude_market["version"]
    assert claude["version"].count(".") == 2
    assert codex["skills"] == "./skills/"
    assert codex["interface"]["displayName"]


def test_marketplaces_point_at_the_generated_plugin():
    claude_market = _json(REPO / ".claude-plugin" / "marketplace.json")
    codex_market = _json(REPO / ".agents" / "plugins" / "marketplace.json")

    claude_source = claude_market["plugins"][0]["source"]
    codex_source = codex_market["plugins"][0]["source"]

    assert (REPO / claude_source / ".claude-plugin" / "plugin.json").is_file()
    assert codex_source["source"] == "local"
    assert (REPO / codex_source["path"] / ".codex-plugin" / "plugin.json").is_file()


def test_plugin_ships_every_skill_and_agent_fully_rendered():
    skills = sorted(path.name for path in SKILL_SOURCES.iterdir() if path.is_dir())
    packaged = sorted(path.parent.name for path in PLUGIN.glob("skills/*/SKILL.md"))
    agents = sorted(path.stem for path in (PLUGIN / "agents").glob("*.md"))

    assert packaged == skills
    assert agents == ["architect", "developer", "integrator", "planner", "reviewer"]
    for path in PLUGIN.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert "{{" not in text, path
    assert "dev-agent" in (PLUGIN / "skills" / "integrate" / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_default_project_dir_in_sync_script_matches_locator():
    from ai_team.core.locator import DEFAULT_PROJECT_DIR

    script = (CLI / "scripts" / "sync_init_scaffolds.py").read_text(encoding="utf-8")

    assert f'DEFAULT_PROJECT_DIR = "{DEFAULT_PROJECT_DIR}"' in script


def test_committed_plugin_package_matches_a_fresh_sync(tmp_path):
    """The generated plugin, marketplaces, and manifests are never hand-edited."""
    repo = tmp_path / "repo"
    cli = repo / "cli"
    shutil.copytree(
        CLI / "src" / "ai_team" / "init",
        cli / "src" / "ai_team" / "init",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    config = cli / "src" / "ai_team" / "core" / "config.py"
    config.parent.mkdir(parents=True)
    shutil.copy2(CLI / "src" / "ai_team" / "core" / "config.py", config)
    (cli / "scripts").mkdir()
    shutil.copy2(
        CLI / "scripts" / "sync_init_scaffolds.py",
        cli / "scripts" / "sync_init_scaffolds.py",
    )
    version = _json(PLUGIN / ".claude-plugin" / "plugin.json")["version"]

    subprocess.run(
        [
            sys.executable,
            str(cli / "scripts" / "sync_init_scaffolds.py"),
            "--plugin-version",
            version,
        ],
        check=True,
        capture_output=True,
    )

    for relative in (
        "plugins/ai-team",
        ".claude-plugin",
        ".agents/plugins",
    ):
        fresh = sorted(
            p.relative_to(repo / relative)
            for p in (repo / relative).rglob("*")
            if p.is_file()
        )
        committed = sorted(
            p.relative_to(REPO / relative)
            for p in (REPO / relative).rglob("*")
            if p.is_file()
        )
        assert fresh == committed, relative
        for name in fresh:
            assert (repo / relative / name).read_text(encoding="utf-8") == (
                REPO / relative / name
            ).read_text(encoding="utf-8"), (
                f"{relative}/{name} is stale; run sync_init_scaffolds.py"
            )
