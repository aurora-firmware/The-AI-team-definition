"""Docs name the .agents/skills Codex export path and not the legacy .codex/skills."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CUSTOMIZATION_GUIDE = REPO_ROOT / "guides" / "customization-guide.md"
SETUP_GUIDE = REPO_ROOT / "guides" / "setup-guide.md"
README = REPO_ROOT / "README.md"


@pytest.mark.parametrize("doc_path", [CUSTOMIZATION_GUIDE, SETUP_GUIDE])
def test_guide_names_agents_skills_as_codex_skill_location(doc_path: Path) -> None:
    assert ".agents/skills" in doc_path.read_text(encoding="utf-8")


def test_readme_lists_agents_folder_beside_claude_and_codex() -> None:
    lines = README.read_text(encoding="utf-8").splitlines()
    tool_folder_lines = [
        line for line in lines if "`.claude/`" in line and "`.codex/`" in line
    ]
    assert tool_folder_lines, "README no longer lists the tool folders"
    missing = [line for line in tool_folder_lines if "`.agents/`" not in line]
    assert missing == []


@pytest.mark.parametrize("doc_path", [CUSTOMIZATION_GUIDE, SETUP_GUIDE, README])
def test_doc_does_not_name_legacy_codex_skills_folder(doc_path: Path) -> None:
    assert ".codex/skills" not in doc_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "relative_path",
    [
        ".gitignore",
        "CLAUDE.md",
        "AGENTS.md",
        "ai-process/architecture/system-overview.md",
    ],
)
def test_repo_guidance_names_agents_folder(relative_path: str) -> None:
    assert ".agents" in (REPO_ROOT / relative_path).read_text(encoding="utf-8")
