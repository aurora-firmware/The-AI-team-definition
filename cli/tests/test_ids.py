"""
Tests for T-008: ai_team.core.ids — artifact ID allocation helpers.

Cycle 1 scope:
  - next_task_id() behavior for empty and mixed-state task folders.
"""

from pathlib import Path

from ai_team.core.ids import next_adr_id, next_bug_id, next_spec_id, next_task_id
from ai_team.core.locator import ProjectRoot


def make_project_root(tmp_path: Path) -> ProjectRoot:
    """Create the minimal artifact tree and return a matching ProjectRoot."""
    project_dir = tmp_path / "project"
    (project_dir / "specs" / "archive").mkdir(parents=True)
    for state in ("pending", "in-progress", "completed", "blocked"):
        (project_dir / "tasks" / state).mkdir(parents=True)
    for state in ("open", "in-progress", "resolved"):
        (project_dir / "bugs" / state).mkdir(parents=True)
    (project_dir / "decisions").mkdir(parents=True)
    (project_dir / "docs").mkdir(parents=True)
    return ProjectRoot._from_repo_and_project_dir_name(tmp_path, "project")


def test_next_task_id_returns_t_001_when_no_task_files_exist(tmp_path):
    """AC-1: empty task folders return T-001."""
    root = make_project_root(tmp_path)
    assert next_task_id(root) == "T-001"


def test_next_task_id_uses_highest_number_across_all_task_states(tmp_path):
    """AC-2: allocator scans all task states and increments the max number."""
    root = make_project_root(tmp_path)
    (root.tasks_pending / "T-007-define-parser.md").write_text("", encoding="utf-8")
    (root.tasks_completed / "T-012-finalize-parser.md").write_text("", encoding="utf-8")

    assert next_task_id(root) == "T-013"


def test_next_task_id_ignores_non_matching_task_files(tmp_path):
    """AC-4: only files matching T-NNN-*.md are considered."""
    root = make_project_root(tmp_path)
    (root.tasks_pending / "TEMPLATE-task.md").write_text("", encoding="utf-8")
    (root.tasks_pending / ".gitkeep").write_text("", encoding="utf-8")
    (root.tasks_pending / "T-01-not-padded.md").write_text("", encoding="utf-8")
    (root.tasks_pending / "T-999-no-extension.txt").write_text("", encoding="utf-8")

    assert next_task_id(root) == "T-001"


def test_next_bug_id_returns_b_001_when_no_bug_files_exist(tmp_path):
    """AC-3: bug IDs are zero-padded and start from B-001."""
    root = make_project_root(tmp_path)
    assert next_bug_id(root) == "B-001"


def test_next_bug_id_scans_all_bug_states_and_ignores_non_matching(tmp_path):
    """AC-3/AC-4: bug allocator scans all state folders and ignores invalid names."""
    root = make_project_root(tmp_path)
    (root.bugs_open / "B-004-first.md").write_text("", encoding="utf-8")
    (root.bugs_resolved / "B-009-last.md").write_text("", encoding="utf-8")
    (root.bugs_in_progress / "TEMPLATE-bug.md").write_text("", encoding="utf-8")
    (root.bugs_in_progress / "B-01-not-padded.md").write_text("", encoding="utf-8")

    assert next_bug_id(root) == "B-010"


def test_next_spec_id_uses_project_and_archive_as_one_number_space(tmp_path):
    """AC-3: spec IDs scan specs/ and specs/archive/ together."""
    root = make_project_root(tmp_path)
    (root.specs / "S-002-initial-spec.md").write_text("", encoding="utf-8")
    (root.specs / "archive" / "S-014-legacy-spec.md").write_text("", encoding="utf-8")
    (root.specs / "archive" / "template-spec.md").write_text("", encoding="utf-8")

    assert next_spec_id(root) == "S-015"


def test_next_adr_id_returns_zero_padded_identifier(tmp_path):
    """AC-3: ADR IDs use ADR-NNN formatting."""
    root = make_project_root(tmp_path)
    assert next_adr_id(root) == "ADR-001"


def test_next_adr_id_ignores_non_matching_files(tmp_path):
    """AC-4: only ADR-NNN-*.md contributes to the next ADR ID."""
    root = make_project_root(tmp_path)
    (root.decisions / "ADR-003-use-skill.md").write_text("", encoding="utf-8")
    (root.decisions / "003-use-old-pattern.md").write_text("", encoding="utf-8")
    (root.decisions / "ADR-template.md").write_text("", encoding="utf-8")
    (root.decisions / ".gitkeep").write_text("", encoding="utf-8")

    assert next_adr_id(root) == "ADR-004"
