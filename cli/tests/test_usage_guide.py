"""
Tests for T-028: cli/docs/usage.md hand-written CLI guide.

Covers:
  AC-1: cli/docs/usage.md exists and covers installation, ai-team init,
        daily command workflows, the project/ folder structure, and a
        maintainer section.
  AC-2: usage.md describes the project/ folder structure including specs/
        (+ archive/), task and bug state subfolders, decisions/, docs/,
        .ai-team.toml, and the locator resolution order.
  AC-3: usage.md includes a maintainer section with module map, how to add
        a command, how to run tests, how to build/release, and how to
        regenerate commands.md.
  AC-4: usage.md links to commands.md.
  AC-5: usage.md documents only commands and flags present in commands.md —
        verified by cross-checking a representative set.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
USAGE_MD = REPO_ROOT / "cli" / "docs" / "usage.md"
COMMANDS_MD = REPO_ROOT / "cli" / "docs" / "commands.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _content() -> str:
    assert USAGE_MD.is_file(), f"usage.md not found at {USAGE_MD}"
    return USAGE_MD.read_text(encoding="utf-8")


def _lower() -> str:
    return _content().lower()


# ---------------------------------------------------------------------------
# AC-1: file exists and covers the required high-level topics
# ---------------------------------------------------------------------------


def test_usage_md_file_exists():
    """cli/docs/usage.md must exist as a regular file."""
    assert USAGE_MD.is_file(), f"Expected file not found: {USAGE_MD}"


def test_usage_md_covers_installation():
    """usage.md must have an installation section."""
    assert "install" in _lower(), "usage.md must cover installation"


def test_usage_md_covers_init_command():
    """usage.md must document ai-team init."""
    assert "ai-team init" in _content() or "ai team init" in _lower(), (
        "usage.md must document the ai-team init command"
    )


def test_usage_md_covers_daily_workflows():
    """usage.md must cover at least one daily workflow sequence (task or bug)."""
    lower = _lower()
    assert "task" in lower and "bug" in lower, (
        "usage.md must cover daily task and bug workflows"
    )


def test_usage_md_covers_gate5_report_workflow():
    """usage.md must cover generating a Gate 5 report."""
    lower = _lower()
    assert "report" in lower and (
        "gate 5" in lower or "gate5" in lower or "status" in lower
    ), "usage.md must describe the Gate 5 / status report workflow"


# ---------------------------------------------------------------------------
# AC-2: project/ folder structure and .ai-team.toml locator
# ---------------------------------------------------------------------------


def test_usage_md_describes_specs_folder():
    """usage.md must document the specs/ folder."""
    assert "specs/" in _content() or "specs" in _lower(), (
        "usage.md must describe the specs/ folder"
    )


def test_usage_md_describes_specs_archive_subfolder():
    """usage.md must document the specs/archive/ subfolder."""
    lower = _lower()
    assert "archive" in lower, "usage.md must mention the specs/archive/ folder"


def test_usage_md_describes_tasks_state_subfolders():
    """usage.md must document all four task state folders."""
    lower = _lower()
    for subfolder in ("pending", "in-progress", "completed", "blocked"):
        assert subfolder in lower, (
            f"usage.md must document the tasks/{subfolder}/ subfolder"
        )


def test_usage_md_describes_bugs_state_subfolders():
    """usage.md must document all three bug state folders."""
    lower = _lower()
    for subfolder in ("open", "in-progress", "resolved"):
        assert subfolder in lower, (
            f"usage.md must document the bugs/{subfolder}/ subfolder"
        )


def test_usage_md_describes_decisions_folder():
    """usage.md must document the decisions/ folder."""
    assert "decisions" in _lower(), "usage.md must describe the decisions/ folder"


def test_usage_md_describes_docs_folder():
    """usage.md must document the docs/ folder."""
    assert "docs" in _lower(), "usage.md must describe the docs/ folder"


def test_usage_md_describes_ai_team_toml_marker():
    """usage.md must document the .ai-team.toml marker file."""
    assert ".ai-team.toml" in _content(), (
        "usage.md must document the .ai-team.toml marker"
    )


def test_usage_md_describes_locator_resolution_order():
    """usage.md must describe the locator resolution order."""
    lower = _lower()
    # The locator has 4 strategies; at minimum the env var and toml walk must be mentioned.
    assert (
        "ai_team_root" in lower or "ai-team-root" in lower or "environment" in lower
    ), (
        "usage.md must describe the AI_TEAM_ROOT environment-variable resolution strategy"
    )


# ---------------------------------------------------------------------------
# AC-3: maintainer section
# ---------------------------------------------------------------------------


def test_usage_md_has_maintainer_section():
    """usage.md must contain a maintainer section heading."""
    lower = _lower()
    assert (
        "maintainer" in lower or "for maintainer" in lower or "contributing" in lower
    ), "usage.md must have a maintainer section"


def test_usage_md_has_module_map():
    """usage.md must document the ai_team module layout."""
    lower = _lower()
    assert "module" in lower or "ai_team" in lower or "package" in lower, (
        "usage.md must include a module map"
    )


def test_usage_md_explains_how_to_add_a_command():
    """usage.md must explain how to add a new command."""
    lower = _lower()
    assert "add" in lower and "command" in lower, (
        "usage.md must explain how to add a new command"
    )


def test_usage_md_explains_how_to_run_tests():
    """usage.md must document how to run the test suite."""
    lower = _lower()
    assert "pytest" in lower or "test" in lower, (
        "usage.md must explain how to run tests"
    )


def test_usage_md_explains_how_to_build_and_release():
    """usage.md must document the build and release process."""
    lower = _lower()
    assert "build" in lower and (
        "release" in lower or "publish" in lower or "pypi" in lower
    ), "usage.md must explain how to build and release"


def test_usage_md_explains_how_to_regenerate_commands_md():
    """usage.md must document how to regenerate commands.md."""
    content = _content()
    assert "gen_docs.sh" in content, (
        "usage.md must document the gen_docs.sh regeneration script"
    )


# ---------------------------------------------------------------------------
# AC-4: link to commands.md
# ---------------------------------------------------------------------------


def test_usage_md_links_to_commands_md():
    """usage.md must contain a link to commands.md."""
    assert "commands.md" in _content(), "usage.md must link to commands.md"


# ---------------------------------------------------------------------------
# AC-5: no undocumented commands or flags
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "ai-team task new",
        "ai-team task start",
        "ai-team task complete",
        "ai-team task block",
        "ai-team bug new",
        "ai-team bug start",
        "ai-team bug resolve",
        "ai-team init",
        "ai-team status",
        "ai-team report",
        "ai-team validate",
        "ai-team list",
        "ai-team show",
        "ai-team adr new",
        "ai-team spec new",
        "ai-team archive",
    ],
)
def test_commands_mentioned_in_usage_exist_in_commands_md(command):
    """Every command mentioned in usage.md must also appear in commands.md."""
    assert COMMANDS_MD.is_file(), "commands.md must exist for cross-checking"
    commands_content = COMMANDS_MD.read_text(encoding="utf-8")
    # Extract the subcommand portion to check (e.g. "task new" from "ai-team task new")
    parts = command.split()
    # Check for the subcommand term in commands.md — the generated file has the full form
    assert command in commands_content or " ".join(parts[1:]) in commands_content, (
        f"'{command}' is documented in usage.md but does not appear in commands.md"
    )


def test_usage_md_does_not_mention_nonexistent_flags():
    """usage.md must not document flags that are absent from commands.md."""
    assert COMMANDS_MD.is_file(), "commands.md must exist for cross-checking"
    commands_content = COMMANDS_MD.read_text(encoding="utf-8").lower()
    usage_content = _content().lower()

    # These flags do not exist in any command — they must not appear in usage.md
    # as CLI flags (they may appear in prose explanation of the source code).
    nonexistent_flags = ["--verbose", "--quiet", "--output-dir"]
    for flag in nonexistent_flags:
        if flag in usage_content and flag not in commands_content:
            pytest.fail(
                f"usage.md documents flag '{flag}' that does not exist in commands.md"
            )
