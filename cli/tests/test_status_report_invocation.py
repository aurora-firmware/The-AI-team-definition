"""Regression coverage for model-invocable skill-to-skill targets."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

CLI_ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCES = CLI_ROOT / "src" / "ai_team" / "init" / "sources" / "skills"
SCAFFOLDS = CLI_ROOT / "src" / "ai_team" / "init" / "scaffolds"
TOOLS = ("claude", "codex")
SKILL_INVOCATION = re.compile(r"Skill\(([^)]+)\)")
MODEL_INVOCATION_DISABLED = re.compile(
    r"^disable-model-invocation:\s*true\s*$", re.MULTILINE
)


def _headers(skill_name: str) -> dict[str, str]:
    metadata = SKILL_SOURCES / skill_name / "metadata.toml"
    raw = tomllib.loads(metadata.read_text(encoding="utf-8"))
    return {tool: raw[tool]["header"] for tool in TOOLS}


def test_skill_invocation_targets_allow_model_invocation() -> None:
    """A skill named in Skill(...) must be callable by the invoking model."""
    for metadata in SKILL_SOURCES.glob("*/metadata.toml"):
        raw = tomllib.loads(metadata.read_text(encoding="utf-8"))
        for tool in TOOLS:
            caller_header = raw[tool]["header"]
            for target_name in SKILL_INVOCATION.findall(caller_header):
                target_header = _headers(target_name)[tool]
                assert not MODEL_INVOCATION_DISABLED.search(target_header), (
                    f"{metadata.parent.name} invokes {target_name} for {tool}, but "
                    "the target disables model invocation"
                )


def test_status_report_is_human_invoked_only_in_generated_scaffolds() -> None:
    """Reporting is on demand: generated status-report skills disable model invocation."""
    for tool in TOOLS:
        scaffold = SCAFFOLDS / tool / "skills" / "status-report" / "SKILL.md"
        content = scaffold.read_text(encoding="utf-8")
        assert MODEL_INVOCATION_DISABLED.search(content), (
            f"{tool} status-report scaffold must disable model invocation"
        )


def test_loops_end_with_run_summary_instead_of_status_report() -> None:
    """Both loops route an empty queue to Step 8, which returns a chat summary only."""
    for loop_name in ("dev-loop", "bug-loop"):
        body = (SKILL_SOURCES / loop_name / "body.md").read_text(encoding="utf-8")
        queue_step = body.split("### Step 1: Check the Queue", 1)[1].split(
            "### Step 2:", 1
        )[0]
        loop_complete = body.split("### Step 8: Loop Complete", 1)[1].split("\n## ", 1)[
            0
        ]
        for tool, header in _headers(loop_name).items():
            assert "Skill(status-report)" not in header, (
                f"{loop_name} must not be allowed to invoke status-report for {tool}"
            )
        assert "proceed directly to **Step 8: Loop Complete**" in queue_step, (
            f"{loop_name} does not route an empty full queue to Step 8"
        )
        assert "invoke `Skill(status-report)`" not in body, (
            f"{loop_name} still invokes status-report automatically"
        )
        assert "Do not invoke the `status-report` skill" in loop_complete
        assert "run summary" in loop_complete
        assert "Workspace Hygiene" in loop_complete, (
            f"{loop_name} must check the workspace before it ends"
        )
