"""Tests for T-063: integrate committed-PASS gate, lifecycle guard, safe delete,
and loop committed-handoff preconditions."""

from __future__ import annotations

from pathlib import Path

from tests.skill_rendering import rendered_skill_body


def _integrate_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("integrate")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "integrate"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    codex = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "skills"
        / "integrate"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude, codex


def _dev_loop_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("dev-loop")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "dev-loop"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    codex = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "skills"
        / "dev-loop"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude, codex


def _bug_loop_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("bug-loop")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "bug-loop"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    codex = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "skills"
        / "bug-loop"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude, codex


# AC-1: integrate verifies latest committed canonical PASS verdict on dev-agent before merging


def test_integrate_verifies_committed_pass_verdict_on_dev_agent_before_merge() -> None:
    """AC-1: integrate must verify the latest committed canonical Review Verdict on
    dev-agent is PASS before proceeding to merge."""
    source, claude, codex = _integrate_skill_texts()
    required_phrases = (
        "committed",
        "PASS",
        "verdict",
    )

    for phrase in required_phrases:
        assert phrase in source, f"integrate body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_integrate_stops_when_committed_verdict_is_not_pass() -> None:
    """AC-1: integrate must stop and not proceed when the committed verdict is not PASS."""
    source, claude, codex = _integrate_skill_texts()

    # The body must describe stopping when verdict is not PASS
    required_phrases = ("not PASS",)

    for phrase in required_phrases:
        assert phrase in source, f"integrate body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-2: lifecycle-file guard is retained in integrate


def test_integrate_retains_lifecycle_file_guard_for_implementation_branches() -> None:
    """AC-2: integrate must still stop when an implementation branch modifies a canonical
    lifecycle file."""
    source, claude, codex = _integrate_skill_texts()

    required_phrases = (
        "lifecycle",
        "stop",
    )

    for phrase in required_phrases:
        assert phrase in source, f"integrate body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-3: integrate uses stop-and-report instead of git branch -D


def test_integrate_does_not_use_forced_branch_delete() -> None:
    """AC-3: integrate must not contain git branch -D (forced delete fallback removed)."""
    source, claude, codex = _integrate_skill_texts()
    forbidden_phrase = "branch -D"

    assert forbidden_phrase not in source, (
        "integrate body.md must not include forced delete 'branch -D'"
    )
    assert forbidden_phrase not in claude, (
        "Claude scaffold must not include forced delete 'branch -D'"
    )
    assert forbidden_phrase not in codex, (
        "Codex scaffold must not include forced delete 'branch -D'"
    )


def test_integrate_stops_and_reports_when_safe_delete_is_refused() -> None:
    """AC-3: when git branch -d is refused, integrate must stop and report instead of
    using git branch -D."""
    source, claude, codex = _integrate_skill_texts()

    required_phrases = (
        "stop",
        "report",
    )

    for phrase in required_phrases:
        assert phrase in source, f"integrate body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-3b: integrate task completion uses a deletion-aware move and old-path check


def test_integrate_requires_deletion_aware_task_completion_move() -> None:
    """B-012: task completion instructions must describe a git-aware move that stages
    both the old-path deletion and new-path addition."""
    source, claude, codex = _integrate_skill_texts()

    required_phrases = (
        "git mv",
        "git rm",
        "git add",
    )

    for phrase in required_phrases:
        assert phrase in source, f"integrate body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_integrate_checks_old_task_path_is_clean_before_reporting_success() -> None:
    """B-012: integrate must verify the old in-progress task path is neither tracked
    nor dirty before reporting success. Working-tree cleanliness alone is not enough,
    so the procedure must also check the tracked tree (git ls-files / git ls-tree)."""
    source, claude, codex = _integrate_skill_texts()

    required_phrases = (
        "git ls-files project/tasks/in-progress/",
        "git status --porcelain project/tasks/in-progress/",
        "empty",
    )

    for phrase in required_phrases:
        assert phrase in source, f"integrate body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-4: dev-loop records committed Developer handoffs and Review Verdicts before integration


def test_dev_loop_records_committed_work_log_on_dev_agent_before_integration() -> None:
    """AC-4: dev-loop must commit the Developer Work Log handoff on dev-agent before
    invoking integration."""
    source, claude, codex = _dev_loop_skill_texts()

    required_phrases = (
        "Commit the lifecycle update",
        "chore(tasks): record T-NNN work log",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_records_committed_review_verdict_on_dev_agent_before_integration() -> (
    None
):
    """AC-4: dev-loop must confirm the Review Verdict is committed on dev-agent before
    invoking integration."""
    source, claude, codex = _dev_loop_skill_texts()

    required_phrases = (
        "committed",
        "verdict",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_bug_loop_records_committed_diagnosis_log_on_dev_agent_before_integration() -> (
    None
):
    """AC-4: bug-loop must commit the Developer Diagnosis Log handoff on dev-agent before
    invoking integration."""
    source, claude, codex = _bug_loop_skill_texts()

    required_phrases = (
        "Commit the lifecycle update",
        "chore(bugs): record B-NNN diagnosis",
    )

    for phrase in required_phrases:
        assert phrase in source, f"bug-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_bug_loop_records_committed_work_log_on_dev_agent_before_integration() -> None:
    """AC-4: bug-loop must commit the Developer Work Log handoff on dev-agent before
    invoking integration."""
    source, claude, codex = _bug_loop_skill_texts()

    required_phrases = (
        "Commit the lifecycle update",
        "chore(bugs): record B-NNN work log",
    )

    for phrase in required_phrases:
        assert phrase in source, f"bug-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_bug_loop_records_committed_review_verdict_on_dev_agent_before_integration() -> (
    None
):
    """AC-4: bug-loop must confirm the Review Verdict is committed on dev-agent before
    invoking integration."""
    source, claude, codex = _bug_loop_skill_texts()

    required_phrases = (
        "committed",
        "verdict",
    )

    for phrase in required_phrases:
        assert phrase in source, f"bug-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"
