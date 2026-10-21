"""Loops stay model-invocable so a human can delegate them to an agent."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

CLI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = CLI_ROOT.parent
SKILL_SOURCES = CLI_ROOT / "src" / "ai_team" / "init" / "sources" / "skills"
SCAFFOLDS = CLI_ROOT / "src" / "ai_team" / "init" / "scaffolds"
SKILL_GUIDE = REPO_ROOT / "guides" / "skill_template.md"
TOOLS = ("claude", "codex")
LOOP_SENTENCES = {
    "dev-loop": "Use only when the human asks to run the development loop.",
    "bug-loop": "Use only when the human asks to run the bug-fix loop.",
}
FLAG = "disable-model-invocation"


def _source_headers(skill: str) -> dict[str, str]:
    metadata = SKILL_SOURCES / skill / "metadata.toml"
    raw = tomllib.loads(metadata.read_text(encoding="utf-8"))
    return {tool: raw[tool]["header"] for tool in TOOLS}


def _scaffold_headers(skill: str) -> dict[str, str]:
    headers = {}
    for tool in TOOLS:
        path = SCAFFOLDS / tool / "skills" / skill / "SKILL.md"
        headers[tool] = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    return headers


def _description(header: str) -> str:
    match = re.search(r"^description:\s*(.*)$", header, re.MULTILINE)
    assert match, "header has no description"
    return match.group(1).strip()


def test_loop_headers_do_not_disable_model_invocation_in_sources() -> None:
    for skill in LOOP_SENTENCES:
        for tool, header in _source_headers(skill).items():
            assert FLAG not in header, f"{skill} {tool} source carries {FLAG}"


def test_loop_headers_do_not_disable_model_invocation_in_scaffolds() -> None:
    for skill in LOOP_SENTENCES:
        for tool, header in _scaffold_headers(skill).items():
            assert FLAG not in header, f"{skill} {tool} scaffold carries {FLAG}"


def test_loop_descriptions_end_with_explicit_human_request_sentence() -> None:
    for skill, sentence in LOOP_SENTENCES.items():
        for headers in (_source_headers(skill), _scaffold_headers(skill)):
            for tool, header in headers.items():
                assert _description(header).endswith(sentence), (skill, tool)


def test_bug_loop_description_no_longer_invites_auto_selection() -> None:
    for headers in (_source_headers("bug-loop"), _scaffold_headers("bug-loop")):
        for header in headers.values():
            assert "Use this whenever there are open bugs to fix" not in header


def test_skill_guide_describes_orchestrators_as_model_invocable() -> None:
    guide = SKILL_GUIDE.read_text(encoding="utf-8")
    assert "Usually carry `disable-model-invocation: true`" not in guide
    assert (
        "typically declare `Agent` in `allowed-tools` (to spawn subagents) and"
        not in guide
    )
    assert "stay model-invocable" in guide
    assert "using-ai-team" in guide
    orchestrator_yaml = guide.split("### Frontmatter", 1)[1].split("###", 1)[0]
    assert FLAG not in orchestrator_yaml.split("```yaml", 1)[1]


def test_skill_guide_checklist_does_not_expect_flag_on_orchestrators() -> None:
    guide = SKILL_GUIDE.read_text(encoding="utf-8")
    checklist = [
        ln for ln in guide.splitlines() if ln.startswith("- [ ] `disable-model")
    ]
    assert checklist and "human-only" in checklist[0]


def test_using_ai_team_rule_and_status_report_flag_unchanged() -> None:
    body = (SKILL_SOURCES / "using-ai-team" / "body.md").read_text(encoding="utf-8")
    assert (
        "`dev-loop` and `bug-loop` start only when the human invokes them. "
        "Never start either on your own."
    ) in body
    for tool, header in _source_headers("status-report").items():
        assert f"{FLAG}: true" in header, tool
