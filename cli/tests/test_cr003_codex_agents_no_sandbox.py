"""CR-003: Codex ignores sandbox_mode in custom agent files, so none may ship it."""

import tomllib
from pathlib import Path

import pytest

INIT_DIR = Path(__file__).resolve().parents[1] / "src" / "ai_team" / "init"
SOURCES_DIR = INIT_DIR / "sources" / "agents" / "codex"
SCAFFOLDS_DIR = INIT_DIR / "scaffolds" / "codex" / "agents"
AGENT_NAMES = ["architect", "developer", "integrator", "planner", "reviewer"]
EXPECTED_VALUES = {
    "architect": (
        "gpt-5.5",
        "high",
        "Structural authority for Gate 2 preflight, escalation consul",
    ),
    "developer": (
        "gpt-5.4",
        "high",
        "Implements exactly one assigned task or diagnosed bug on the",
    ),
    "integrator": (
        "gpt-5.4",
        "high",
        "Integrates reviewed task or bug branches and resolves merge ",
    ),
    "planner": (
        "gpt-5.5",
        "high",
        "Creates approved specifications with the human, then decompo",
    ),
    "reviewer": (
        "gpt-5.4",
        "high",
        "Reviews completed task or bug-fix work after Developer hando",
    ),
}


def _parse(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_codex_agent_source_has_no_sandbox_mode(agent: str) -> None:
    assert "sandbox_mode" not in _parse(SOURCES_DIR / f"{agent}.toml")


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_codex_agent_scaffold_has_no_sandbox_mode(agent: str) -> None:
    assert "sandbox_mode" not in _parse(SCAFFOLDS_DIR / f"{agent}.toml")


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_codex_agent_source_keeps_other_values_unchanged(agent: str) -> None:
    model, effort, description_prefix = EXPECTED_VALUES[agent]
    parsed = _parse(SOURCES_DIR / f"{agent}.toml")
    assert parsed["name"] == agent
    assert parsed["model"] == model
    assert parsed["model_reasoning_effort"] == effort
    assert parsed["description"].startswith(description_prefix)
    assert parsed["developer_instructions"].startswith(
        f"You are the {agent.capitalize()} for this AI team."
    )
