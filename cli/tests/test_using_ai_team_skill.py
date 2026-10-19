"""Issue #29: the using-ai-team meta-skill."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

INIT = Path(__file__).resolve().parents[1] / "src" / "ai_team" / "init"
SKILLS = INIT / "sources" / "skills"
BODY = (SKILLS / "using-ai-team" / "body.md").read_text(encoding="utf-8")


def test_dispatch_table_names_only_existing_skills():
    existing = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    table_rows = [line for line in BODY.splitlines() if line.startswith("| ")]
    named = {
        name for row in table_rows[2:] for name in re.findall(r"`([a-z][a-z-]+)`", row)
    }

    assert named
    assert named <= existing, named - existing


def test_every_process_skill_is_reachable_from_the_dispatch_table():
    entry_points = {
        "brainstorm",
        "change-request",
        "architecture-consistency-review",
        "spec-breakdown",
        "spec-breakdown-review",
        "tdd",
        "debug",
        "code-review",
        "integrate",
        "merge-conflicts",
        "escalation-review",
        "new-spec",
        "new-task",
        "new-bug",
        "new-adr",
        "git-conventions",
        "status-report",
    }

    for name in entry_points:
        assert f"`{name}`" in BODY, name


def test_loops_are_human_triggered_only():
    assert "`dev-loop` and `bug-loop` start only when the human invokes them" in BODY


def test_metadata_matches_skill_authoring_rules_for_both_tools():
    metadata = tomllib.loads(
        (SKILLS / "using-ai-team" / "metadata.toml").read_text(encoding="utf-8")
    )

    for tool in ("claude", "codex"):
        header = metadata[tool]["header"]
        assert "name: using-ai-team" in header
        description = re.search(r"^description: (.+)$", header, re.MULTILINE)
        assert description and len(description.group(1)) <= 1024
        assert not re.match(r"(I|You) ", description.group(1))
        assert "disable-model-invocation" not in header


def test_scaffolds_are_generated_for_both_tools():
    for tool in ("claude", "codex"):
        skill = INIT / "scaffolds" / tool / "skills" / "using-ai-team" / "SKILL.md"
        assert skill.read_text(encoding="utf-8").endswith(BODY)


def test_skill_stays_role_neutral_and_self_contained():
    for forbidden in ("ai-process/", "I am the", "the Architect can decide"):
        assert forbidden not in BODY
    assert len(BODY.splitlines()) < 500
