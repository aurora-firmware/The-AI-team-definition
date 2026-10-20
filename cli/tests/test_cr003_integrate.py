"""CR-003 section 4: integrate run context and design-review lookup."""

from __future__ import annotations

from pathlib import Path

CLI = Path(__file__).resolve().parents[1]
SOURCES = CLI / "src" / "ai_team" / "init" / "sources"
SCAFFOLDS = CLI / "src" / "ai_team" / "init" / "scaffolds"

COPIES = {
    "source": SOURCES / "skills" / "integrate" / "body.md",
    "claude": SCAFFOLDS / "claude" / "skills" / "integrate" / "SKILL.md",
    "codex": SCAFFOLDS / "codex" / "skills" / "integrate" / "SKILL.md",
}


def section(path: Path, start_heading: str, end_heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(start_heading)
    return text[start : text.index(end_heading, start)]


def test_step_4_runs_each_line_from_repository_root_in_a_fresh_shell():
    for name, path in COPIES.items():
        step = section(path, "### Step 4:", "### Step 5:")
        assert "from the repository root in a fresh shell" in step, name
        assert "independently of the other lines" in step, name
        assert "changes into it on that line" in step, name
        assert "never run as one script" in step, name


def test_step_6_applies_the_same_run_context_to_destination_commands():
    for name, path in COPIES.items():
        step = section(path, "### Step 6:", "#### All Tests Pass")
        assert "same run context as Step 4" in step, name


def test_step_2_item_7_skips_design_review_line_and_uses_project_guidance():
    for name, path in COPIES.items():
        step = section(
            path, "7. Determine the source-branch", "8. Determine the destination"
        )
        assert "`Design review:`" in step, name
        assert "no automated command" in step, name
        assert "Gate 3" in step, name
        assert "Skip it" in step, name
        assert "from project guidance" in step, name


def test_step_5_shows_merge_command_with_second_m_argument_for_trailers():
    for name, path in COPIES.items():
        step = section(path, "### Step 5:", "### Step 6:")
        assert (
            'git merge --no-ff <source-branch> -m "chore(<kind>): merge '
            '<work-item-id> <short-description>" -m "<trailer lines>"'
        ) in step, name
        assert "commit conventions require trailers" in step, name


def test_step_5_states_git_merge_does_not_read_message_from_stdin():
    for name, path in COPIES.items():
        step = section(path, "### Step 5:", "### Step 6:")
        assert "does not read a message from stdin" in step, name
        assert "`-F -` fails" in step, name


def test_step_5_keeps_single_m_merge_command_valid_without_required_trailers():
    for name, path in COPIES.items():
        step = section(path, "### Step 5:", "### Step 6:")
        single = (
            'git merge --no-ff <source-branch> -m "chore(<kind>): merge '
            '<work-item-id> <short-description>"\n'
        )
        assert single in step, name
        assert "Without required trailers" in step, name
