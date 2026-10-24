"""Regression tests for B-016: Developer role has no enforced boundary against
committing lifecycle files on task branches.

Fix Verification (from the bug report):
- The Developer agent definition names tracker files (tasks, bugs,
  change-requests; spec S-006) as out of bounds for Write/Edit and for
  `git add`/commit, with the `new-bug` exception stated explicitly.
- `git-conventions` lists lifecycle-file commits from an implementation branch
  under Hard Rules.
- Both Claude and Codex Developer definitions carry the same boundary.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_AGENTS = REPO_ROOT / "src" / "ai_team" / "init" / "sources" / "agents"
SCAFFOLD_ROOT = REPO_ROOT / "src" / "ai_team" / "init" / "scaffolds"
SOURCE_SKILLS = REPO_ROOT / "src" / "ai_team" / "init" / "sources" / "skills"


def _claude_developer_texts() -> tuple[str, str]:
    source = (SOURCE_AGENTS / "claude" / "developer.md").read_text(encoding="utf-8")
    scaffold = (SCAFFOLD_ROOT / "claude" / "agents" / "developer.md").read_text(
        encoding="utf-8"
    )
    return source, scaffold


def _codex_developer_texts() -> tuple[str, str]:
    source = (SOURCE_AGENTS / "codex" / "developer.toml").read_text(encoding="utf-8")
    scaffold = (SCAFFOLD_ROOT / "codex" / "agents" / "developer.toml").read_text(
        encoding="utf-8"
    )
    return source, scaffold


def _git_conventions_texts() -> tuple[str, str, str]:
    source = (SOURCE_SKILLS / "git-conventions" / "body.md").read_text(encoding="utf-8")
    claude_scaffold = (
        SCAFFOLD_ROOT / "claude" / "skills" / "git-conventions" / "SKILL.md"
    ).read_text(encoding="utf-8")
    codex_scaffold = (
        SCAFFOLD_ROOT / "codex" / "skills" / "git-conventions" / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude_scaffold, codex_scaffold


def _hard_rules_section(body: str) -> str:
    start = body.find("## Hard Rules")
    assert start != -1, "body must contain a '## Hard Rules' heading"
    next_heading = body.find("\n## ", start + 1)
    if next_heading == -1:
        return body[start:]
    return body[start:next_heading]


def _common_pitfalls_section(body: str) -> str:
    start = body.find("## Common Pitfalls")
    if start == -1:
        return ""
    next_heading = body.find("\n## ", start + 1)
    if next_heading == -1:
        return body[start:]
    return body[start:next_heading]


def _never_touch_line(body: str) -> str:
    """Extract the 'Never touch' line/row from a Folder Scope block, whether it
    is a markdown table row (Claude) or a plain bullet line (Codex)."""
    for line in body.splitlines():
        if "Never touch" in line:
            return line
    return ""


# ---------------------------------------------------------------------------
# AC-1: Claude Developer Folder Scope names ai-team/tasks/ and ai-team/bugs/
# ---------------------------------------------------------------------------


def test_claude_developer_never_touch_lists_lifecycle_paths() -> None:
    """The Claude Developer 'Never touch' entry must name tracker work items
    (tasks, bugs, change-requests) as out of bounds."""
    for text in _claude_developer_texts():
        never_touch = _never_touch_line(text)
        assert never_touch, "Claude developer.md must contain a 'Never touch' line"
        assert "tracker files" in never_touch
        assert "tasks, bugs, change-requests" in never_touch


def test_claude_developer_never_touch_states_new_bug_exception() -> None:
    """The 'Never touch' row must state the bug-creation exception via the
    new-bug skill explicitly, not just omit it silently."""
    for text in _claude_developer_texts():
        never_touch = _never_touch_line(text)
        assert "creating a bug" in never_touch
        assert "new-bug" in never_touch


def test_claude_developer_never_touch_forbids_git_add_and_commit() -> None:
    """The 'Never touch' row must state explicitly that git add/commit under
    these lifecycle paths is forbidden from an implementation branch, not just
    Write/Edit."""
    for text in _claude_developer_texts():
        never_touch = _never_touch_line(text)
        assert "git add" in never_touch
        assert "commit" in never_touch
        assert "implementation branch" in never_touch


# ---------------------------------------------------------------------------
# AC-2: Codex Developer Folder scope carries the identical boundary
# ---------------------------------------------------------------------------


def test_codex_developer_never_touch_lists_lifecycle_paths() -> None:
    """The Codex Developer 'Never touch' entry must name tracker work items
    (tasks, bugs, change-requests) as out of bounds."""
    for text in _codex_developer_texts():
        never_touch = _never_touch_line(text)
        assert never_touch, "Codex developer.toml must contain a 'Never touch' line"
        assert "tracker files" in never_touch
        assert "tasks, bugs, change-requests" in never_touch


def test_codex_developer_never_touch_states_new_bug_exception() -> None:
    """The Codex 'Never touch' line must state the bug-creation exception via
    the new-bug skill explicitly."""
    for text in _codex_developer_texts():
        never_touch = _never_touch_line(text)
        assert "creating a bug" in never_touch
        assert "new-bug" in never_touch


def test_codex_developer_never_touch_forbids_git_add_and_commit() -> None:
    """The Codex 'Never touch' line must state explicitly that git add/commit
    under these lifecycle paths is forbidden from an implementation branch."""
    for text in _codex_developer_texts():
        never_touch = _never_touch_line(text)
        assert "git add" in never_touch
        assert "commit" in never_touch
        assert "implementation branch" in never_touch


# ---------------------------------------------------------------------------
# AC-3: git-conventions promotes the lifecycle-file-commit rule to Hard Rules
# ---------------------------------------------------------------------------


def test_git_conventions_hard_rules_covers_lifecycle_file_commits() -> None:
    """The lifecycle-file-commit-from-an-implementation-branch prohibition must
    live under '## Hard Rules', not only under '## Common Pitfalls'."""
    for body in _git_conventions_texts():
        hard_rules = _hard_rules_section(body)
        hard_rules_lower = hard_rules.lower()
        assert "lifecycle" in hard_rules_lower
        assert "implementation branch" in hard_rules_lower


def test_git_conventions_common_pitfalls_no_longer_owns_the_rule() -> None:
    """The rule must be promoted (moved) out of Common Pitfalls, not merely
    duplicated into Hard Rules while still advisory-only in Common Pitfalls."""
    for body in _git_conventions_texts():
        pitfalls = _common_pitfalls_section(body)
        assert "lifecycle-file edits from an implementation branch" not in pitfalls


# ---------------------------------------------------------------------------
# Bootstrap exception: internal docs listed by an S-000 task
# ---------------------------------------------------------------------------


def _both_developer_never_touch_lines() -> list[str]:
    return [
        _never_touch_line(text)
        for text in (*_claude_developer_texts(), *_codex_developer_texts())
    ]


def test_developer_never_touch_allows_docs_listed_by_an_s000_task() -> None:
    """The docs/ path is writable only when a task whose source spec is S-000
    lists it in Files to Touch."""
    for line in _both_developer_never_touch_lines():
        assert "{{project_dir}}/docs/" in line
        assert "source spec is S-000" in line
        assert "Files to Touch" in line


def test_developer_never_touch_keeps_specs_and_decisions_without_exception() -> None:
    """specs/ and decisions/ stay off limits, with no exception stated."""
    for line in _both_developer_never_touch_lines():
        assert "`{{project_dir}}/specs/`" in line
        assert "`{{project_dir}}/decisions/`" in line
        assert "without exception" in line
