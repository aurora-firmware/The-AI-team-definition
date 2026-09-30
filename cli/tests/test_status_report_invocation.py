"""Regression coverage for model-invocable skill-to-skill targets."""

from __future__ import annotations

import re
from pathlib import Path

from tests.skill_rendering import rendered_skill_body, rendered_skill_header

CLI_ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCES = CLI_ROOT / "src" / "ai_team" / "init" / "sources" / "skills"
SCAFFOLDS = CLI_ROOT / "src" / "ai_team" / "init" / "scaffolds"
TOOLS = ("claude", "codex")
SKILL_INVOCATION = re.compile(r"Skill\(([^)]+)\)")
MODEL_INVOCATION_DISABLED = re.compile(
    r"^disable-model-invocation:\s*true\s*$", re.MULTILINE
)


def _headers(skill_name: str) -> dict[str, str]:
    return {tool: rendered_skill_header(skill_name, tool) for tool in TOOLS}


def test_skill_invocation_targets_allow_model_invocation() -> None:
    """A skill named in Skill(...) must be callable by the invoking model."""
    for metadata in SKILL_SOURCES.glob("*/metadata.toml"):
        for tool in TOOLS:
            caller_header = rendered_skill_header(metadata.parent.name, tool)
            for target_name in SKILL_INVOCATION.findall(caller_header):
                target_header = _headers(target_name)[tool]
                assert not MODEL_INVOCATION_DISABLED.search(target_header), (
                    f"{metadata.parent.name} invokes {target_name} for {tool}, but "
                    "the target disables model invocation"
                )


def test_status_report_is_model_invocable_in_generated_scaffolds() -> None:
    """Generated Claude and Codex status-report skills must remain callable."""
    for tool in TOOLS:
        scaffold = SCAFFOLDS / tool / "skills" / "status-report" / "SKILL.md"
        content = scaffold.read_text(encoding="utf-8")
        assert not MODEL_INVOCATION_DISABLED.search(content), (
            f"{tool} status-report scaffold disables model invocation"
        )


def test_loops_invoke_status_report_when_the_queue_drains() -> None:
    """Both autonomous loops retain the canonical Gate 5 reporting handoff."""
    for loop_name in ("dev-loop", "bug-loop"):
        body = rendered_skill_body(loop_name)
        queue_step = body.split("### Step 1: Check the Queue", 1)[1].split(
            "### Step 2:", 1
        )[0]
        for tool, header in _headers(loop_name).items():
            assert "Skill(status-report)" in header, (
                f"{loop_name} does not allow status-report invocation for {tool}"
            )
        assert "proceed directly to **Step 8: Loop Complete**" in queue_step, (
            f"{loop_name} does not route an empty full queue to Gate 5 reporting"
        )
        assert "If the queue is empty, stop" not in queue_step, (
            f"{loop_name} stops before its Gate 5 reporting step"
        )
        assert "invoke `Skill(status-report)`" in body, (
            f"{loop_name} does not invoke status-report when its queue drains"
        )
