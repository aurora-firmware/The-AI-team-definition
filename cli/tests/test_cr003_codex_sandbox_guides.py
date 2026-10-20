"""Guides state that Codex agents take sandbox settings from the parent session."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUIDES = [
    REPO_ROOT / "guides" / "agent_template.md",
    REPO_ROOT / "guides" / "setup-guide.md",
]
WRITING_ROLES = ["Architect", "Planner", "Developer", "Reviewer", "Integrator"]


def _codex_text(guide: Path) -> str:
    return guide.read_text(encoding="utf-8")


@pytest.mark.parametrize("guide", GUIDES, ids=lambda path: path.name)
def test_guide_does_not_list_sandbox_mode_as_codex_setting(guide: Path) -> None:
    assert "sandbox_mode" not in _codex_text(guide)


@pytest.mark.parametrize("guide", GUIDES, ids=lambda path: path.name)
def test_guide_states_sandbox_and_approval_come_from_parent_session(
    guide: Path,
) -> None:
    text = " ".join(_codex_text(guide).split())
    assert "sandbox and approval settings from the parent session" in text


@pytest.mark.parametrize("guide", GUIDES, ids=lambda path: path.name)
def test_guide_names_five_roles_needing_a_writable_parent_session(
    guide: Path,
) -> None:
    text = " ".join(_codex_text(guide).split())
    role_list = ", ".join(WRITING_ROLES[:-1]) + ", and " + WRITING_ROLES[-1]
    assert role_list in text
    assert "parent Codex session that allows writes" in text
