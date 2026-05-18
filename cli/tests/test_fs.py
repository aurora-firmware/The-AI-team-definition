"""
Tests for T-004: ai_team.core.fs — filesystem layer for artifact reads,
writes, and atomic moves.

Covers:
  AC-1: move_artifact(src, dest) atomically renames when src != dest and
        dest does not exist.
  AC-2: move_artifact raises ArtifactExists when dest already exists,
        leaving filesystem unchanged.
  AC-3: update_status rewrites only the status frontmatter field,
        preserving all other content.
  AC-4: move_artifact(src, dest) is a no-op when src == dest (after path normalisation).
"""

from pathlib import Path

import pytest

from ai_team.core.fs import (
    ArtifactExists,
    ArtifactNotFound,
    move_artifact,
    read_artifact,
    update_status,
    write_artifact,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def write_file(tmp_path: Path, name: str, content: str) -> Path:
    """Write *content* to *tmp_path/name* and return the path."""
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


VALID_TASK_CONTENT = """\
---
id: "T-001"
title: "Add CLI scaffold"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---

# Add CLI scaffold

Task body here.
"""

VALID_TASK_WITH_COMMENT = """\
---
id: "T-002"
title: "Comment Preservation"
status: pending  # workflow state
priority: medium
assigned-role: developer
created: 2026-05-10
---

Some body text.
Extra body line.
"""

VALID_BUG_CONTENT = """\
---
id: "B-001"
title: "Crash on empty input"
severity: high
status: open
created: 2026-05-10
---

# Crash on empty input

Bug body here.
"""

VALID_SPEC_CONTENT = """\
---
title: "ai-team Python CLI"
version: "0.1"
status: approved
created: 2026-05-10
author: planner
---

# ai-team Python CLI

Spec body.
"""

VALID_ADR_CONTENT = """\
---
id: "ADR-001"
title: "Use ruamel.yaml for round-trip parsing"
status: accepted
created: 2026-05-10
---

# ADR-001: Use ruamel.yaml

ADR body.
"""


# ---------------------------------------------------------------------------
# read_artifact
# ---------------------------------------------------------------------------


def test_read_artifact_task_returns_model_and_body(tmp_path):
    """read_artifact('task') returns a Task model and the body text."""
    from ai_team.core.models import Task

    path = write_file(tmp_path, "T-001.md", VALID_TASK_CONTENT)
    model, body = read_artifact(path, "task")
    assert isinstance(model, Task)
    assert model.id == "T-001"
    assert model.status == "pending"
    assert "Task body here." in body


def test_read_artifact_bug_returns_model_and_body(tmp_path):
    """read_artifact('bug') returns a Bug model and the body text."""
    from ai_team.core.models import Bug

    path = write_file(tmp_path, "B-001.md", VALID_BUG_CONTENT)
    model, body = read_artifact(path, "bug")
    assert isinstance(model, Bug)
    assert model.id == "B-001"
    assert "Bug body here." in body


def test_read_artifact_spec_returns_model_and_body(tmp_path):
    """read_artifact('spec') returns a Spec model and the body text."""
    from ai_team.core.models import Spec

    path = write_file(tmp_path, "spec.md", VALID_SPEC_CONTENT)
    model, body = read_artifact(path, "spec")
    assert isinstance(model, Spec)
    assert model.title == "ai-team Python CLI"
    assert "Spec body." in body


def test_read_artifact_adr_returns_model_and_body(tmp_path):
    """read_artifact('adr') returns an Adr model and the body text."""
    from ai_team.core.models import Adr

    path = write_file(tmp_path, "ADR-001.md", VALID_ADR_CONTENT)
    model, body = read_artifact(path, "adr")
    assert isinstance(model, Adr)
    assert model.id == "ADR-001"
    assert "ADR body." in body


def test_read_artifact_raises_artifact_not_found_for_missing_file(tmp_path):
    """read_artifact raises ArtifactNotFound when the file does not exist."""
    missing = tmp_path / "nonexistent.md"
    with pytest.raises(ArtifactNotFound) as exc_info:
        read_artifact(missing, "task")
    assert str(missing) in str(exc_info.value)


def test_read_artifact_body_is_text_after_frontmatter(tmp_path):
    """read_artifact body contains only the text after the closing --- fence."""
    path = write_file(tmp_path, "T-001.md", VALID_TASK_CONTENT)
    _, body = read_artifact(path, "task")
    # Body should not contain the frontmatter markers or keys.
    assert "id:" not in body
    assert "---" not in body
    assert "Task body here." in body


# ---------------------------------------------------------------------------
# write_artifact
# ---------------------------------------------------------------------------


def test_write_artifact_creates_file(tmp_path):
    """write_artifact writes a new file when the path does not exist."""
    from ai_team.core.models import Task

    model = Task(
        id="T-099",
        title="New Task",
        status="pending",
        priority="low",
        assigned_role="developer",
        created="2026-05-10",
    )
    dest = tmp_path / "T-099.md"
    write_artifact(dest, model, "New task body.\n")
    assert dest.exists()
    content = dest.read_text(encoding="utf-8")
    assert "T-099" in content
    assert "New task body." in content


def test_write_artifact_raises_artifact_exists_when_path_exists(tmp_path):
    """write_artifact raises ArtifactExists when the path exists and overwrite=False."""
    from ai_team.core.models import Task

    model = Task(
        id="T-099",
        title="Existing",
        status="pending",
        priority="low",
        assigned_role="developer",
        created="2026-05-10",
    )
    dest = write_file(tmp_path, "T-099.md", "already here\n")
    with pytest.raises(ArtifactExists) as exc_info:
        write_artifact(dest, model, "body\n")
    assert str(dest) in str(exc_info.value)


def test_write_artifact_overwrites_when_flag_is_true(tmp_path):
    """write_artifact replaces an existing file when overwrite=True."""
    from ai_team.core.models import Task

    model = Task(
        id="T-099",
        title="Updated",
        status="in-progress",
        priority="high",
        assigned_role="developer",
        created="2026-05-10",
    )
    dest = write_file(tmp_path, "T-099.md", "old content\n")
    write_artifact(dest, model, "updated body\n", overwrite=True)
    content = dest.read_text(encoding="utf-8")
    assert "Updated" in content
    assert "old content" not in content


# ---------------------------------------------------------------------------
# AC-1: move_artifact atomically renames file when src != dest
# ---------------------------------------------------------------------------


def test_move_artifact_renames_file_to_new_location(tmp_path):
    """move_artifact moves the file from src to dest when dest does not exist."""
    src = write_file(tmp_path, "pending", "T-001-task.md")
    dest_dir = tmp_path / "in-progress"
    dest_dir.mkdir()
    dest = dest_dir / "T-001-task.md"

    move_artifact(src, dest)

    assert dest.exists()
    assert not src.exists()


def test_move_artifact_dest_contains_original_content(tmp_path):
    """After move_artifact, dest has the same content as src did."""
    src = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    dest = tmp_path / "moved" / "T-001-task.md"
    dest.parent.mkdir()

    move_artifact(src, dest)

    assert dest.read_text(encoding="utf-8") == VALID_TASK_CONTENT


# ---------------------------------------------------------------------------
# AC-2: move_artifact raises ArtifactExists when dest already exists
# ---------------------------------------------------------------------------


def test_move_artifact_raises_artifact_exists_when_dest_exists(tmp_path):
    """move_artifact raises ArtifactExists when dest already exists."""
    src = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    dest = write_file(tmp_path, "T-001-already-there.md", "existing file\n")

    with pytest.raises(ArtifactExists) as exc_info:
        move_artifact(src, dest)
    assert str(dest) in str(exc_info.value)


def test_move_artifact_leaves_src_unchanged_when_dest_exists(tmp_path):
    """move_artifact does not modify src when dest already exists."""
    original_content = VALID_TASK_CONTENT
    src = write_file(tmp_path, "T-001-task.md", original_content)
    dest = write_file(tmp_path, "T-001-already-there.md", "existing file\n")

    with pytest.raises(ArtifactExists):
        move_artifact(src, dest)

    # src must be unchanged.
    assert src.exists()
    assert src.read_text(encoding="utf-8") == original_content


# ---------------------------------------------------------------------------
# AC-3: update_status rewrites only the status field
# ---------------------------------------------------------------------------


def test_update_status_changes_status_value(tmp_path):
    """update_status writes the new status value to the file."""
    path = write_file(tmp_path, "T-001.md", VALID_TASK_CONTENT)
    update_status(path, "in-progress")
    model, _ = read_artifact(path, "task")
    assert model.status == "in-progress"


def test_update_status_preserves_all_other_frontmatter_fields(tmp_path):
    """update_status does not modify any frontmatter field other than status."""
    path = write_file(tmp_path, "T-001.md", VALID_TASK_CONTENT)
    update_status(path, "completed")
    model, _ = read_artifact(path, "task")
    assert model.id == "T-001"
    assert model.title == "Add CLI scaffold"
    assert model.priority == "high"
    assert model.assigned_role == "developer"
    assert model.created == "2026-05-10"


def test_update_status_preserves_body_verbatim(tmp_path):
    """update_status preserves the body text exactly as it was."""
    path = write_file(tmp_path, "T-001.md", VALID_TASK_CONTENT)
    _, body_before = read_artifact(path, "task")
    update_status(path, "completed")
    _, body_after = read_artifact(path, "task")
    assert body_after == body_before


def test_update_status_preserves_inline_yaml_comments(tmp_path):
    """update_status preserves YAML inline comments in the frontmatter."""
    path = write_file(tmp_path, "T-002.md", VALID_TASK_WITH_COMMENT)
    update_status(path, "in-progress")
    content = path.read_text(encoding="utf-8")
    assert "# workflow state" in content


# ---------------------------------------------------------------------------
# AC-4: move_artifact is a no-op when src == dest
# ---------------------------------------------------------------------------


def test_move_artifact_no_op_when_src_equals_dest(tmp_path):
    """move_artifact returns without error when src == dest."""
    src = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    # Should not raise and should leave the file unchanged.
    move_artifact(src, src)
    assert src.exists()
    assert src.read_text(encoding="utf-8") == VALID_TASK_CONTENT


def test_move_artifact_no_op_when_src_equals_dest_after_resolution(tmp_path):
    """move_artifact treats paths as equal after normalisation (resolve)."""
    src = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    # Construct an equivalent path via a redundant component.
    src_alt = src.parent / "." / src.name
    move_artifact(src, src_alt)
    assert src.exists()


# ---------------------------------------------------------------------------
# Error class presence
# ---------------------------------------------------------------------------


def test_artifact_not_found_is_importable():
    """ArtifactNotFound can be imported from ai_team.core.fs."""
    assert ArtifactNotFound is not None


def test_artifact_exists_is_importable():
    """ArtifactExists can be imported from ai_team.core.fs."""
    assert ArtifactExists is not None
