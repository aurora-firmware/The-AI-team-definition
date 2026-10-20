"""CR-003: Codex ignores sandbox_mode in custom agent files, so none may ship it."""

import subprocess
import tomllib
from pathlib import Path

import pytest

INIT_DIR = Path(__file__).resolve().parents[1] / "src" / "ai_team" / "init"
SOURCES_DIR = INIT_DIR / "sources" / "agents" / "codex"
SCAFFOLDS_DIR = INIT_DIR / "scaffolds" / "codex" / "agents"
AGENT_NAMES = ["architect", "developer", "integrator", "planner", "reviewer"]
PRESERVED_KEYS = [
    "name",
    "description",
    "model",
    "model_reasoning_effort",
    "developer_instructions",
]


def _parse(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _committed_source(agent: str) -> dict:
    relative = (SOURCES_DIR / f"{agent}.toml").relative_to(
        Path(__file__).resolve().parents[2]
    )
    content = subprocess.run(
        ["git", "show", f"HEAD:{relative.as_posix()}"],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
    ).stdout
    return tomllib.loads(content)


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_codex_agent_source_has_no_sandbox_mode(agent: str) -> None:
    assert "sandbox_mode" not in _parse(SOURCES_DIR / f"{agent}.toml")


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_codex_agent_scaffold_has_no_sandbox_mode(agent: str) -> None:
    assert "sandbox_mode" not in _parse(SCAFFOLDS_DIR / f"{agent}.toml")


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_codex_agent_source_keeps_other_values_unchanged(agent: str) -> None:
    current = _parse(SOURCES_DIR / f"{agent}.toml")
    baseline = _committed_source(agent)
    for key in PRESERVED_KEYS:
        assert current[key] == baseline[key], key
