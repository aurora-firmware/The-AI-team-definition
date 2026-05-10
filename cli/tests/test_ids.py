"""
Tests for T-008: ai_team.core.ids — artifact ID allocation helpers.

Cycle 1 scope:
  - next_task_id() behavior for empty and mixed-state task folders.
"""

from pathlib import Path

from ai_team.core.ids import next_task_id
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
    (root.tasks_completed / "T-012-finalize-parser.md").write_text(
        "", encoding="utf-8"
    )

    assert next_task_id(root) == "T-013"


def test_next_task_id_ignores_non_matching_task_files(tmp_path):
    """AC-4: only files matching T-NNN-*.md are considered."""
    root = make_project_root(tmp_path)
    (root.tasks_pending / "TEMPLATE-task.md").write_text("", encoding="utf-8")
    (root.tasks_pending / ".gitkeep").write_text("", encoding="utf-8")
    (root.tasks_pending / "T-01-not-padded.md").write_text("", encoding="utf-8")
    (root.tasks_pending / "T-999-no-extension.txt").write_text("", encoding="utf-8")

    assert next_task_id(root) == "T-001"
