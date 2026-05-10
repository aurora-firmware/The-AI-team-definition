"""
Tests for T-003: ai_team.core.models — frontmatter dataclasses, parsers, and dumper.

Covers:
  AC-1: parse_task(path) returns a Task with all fields populated from valid frontmatter.
  AC-2: dump_frontmatter(model, body) round-trips through the matching parse_* to an equal model.
  AC-3: Missing or invalid required field raises FrontmatterError naming the field and path.
  AC-4: YAML comments and key order are preserved across parse/dump cycles.
"""

from pathlib import Path

import pytest

from ai_team.core.models import (
    Adr,
    Bug,
    FrontmatterError,
    Spec,
    Task,
    dump_frontmatter,
    parse_adr,
    parse_bug,
    parse_spec,
    parse_task,
)


# ---------------------------------------------------------------------------
# Fixtures: minimal valid frontmatter files for each artifact type
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

VALID_TASK_WITH_SPEC_CONTENT = """\
---
id: "T-002"
title: "Implement models"
status: in-progress
priority: medium
assigned-role: developer
created: 2026-05-10
spec: "ai-team-python-cli"
---

Body.
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
"""

VALID_BUG_WITH_TASK_CONTENT = """\
---
id: "B-002"
title: "Regression in parser"
severity: medium
status: in-progress
created: 2026-05-10
task: "T-003"
---

Body.
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
"""

VALID_ADR_CONTENT = """\
---
id: "ADR-001"
title: "Use ruamel.yaml for round-trip parsing"
status: accepted
created: 2026-05-10
---

# ADR-001: Use ruamel.yaml
"""

VALID_ADR_WITH_SUPERSEDES_CONTENT = """\
---
id: "ADR-002"
title: "Switch to pyyaml"
status: superseded
created: 2026-05-10
supersedes: "ADR-001"
---

Body.
"""


# ---------------------------------------------------------------------------
# AC-1: parse_task returns a Task with all fields populated
# ---------------------------------------------------------------------------


def test_parse_task_returns_task_instance(tmp_path):
    """parse_task returns a Task dataclass instance."""
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    result = parse_task(path)
    assert isinstance(result, Task)


def test_parse_task_populates_common_fields(tmp_path):
    """parse_task populates id, title, status, and created from frontmatter."""
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    result = parse_task(path)
    assert result.id == "T-001"
    assert result.title == "Add CLI scaffold"
    assert result.status == "pending"
    assert result.created == "2026-05-10"


def test_parse_task_populates_type_specific_fields(tmp_path):
    """parse_task populates priority and assigned_role from frontmatter."""
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    result = parse_task(path)
    assert result.priority == "high"
    assert result.assigned_role == "developer"


def test_parse_task_spec_is_none_when_absent(tmp_path):
    """parse_task sets spec to None when the frontmatter has no spec field."""
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    result = parse_task(path)
    assert result.spec is None


def test_parse_task_populates_optional_spec_when_present(tmp_path):
    """parse_task populates spec when the frontmatter includes a spec field."""
    path = write_file(tmp_path, "T-002-task.md", VALID_TASK_WITH_SPEC_CONTENT)
    result = parse_task(path)
    assert result.spec == "ai-team-python-cli"


def test_parse_bug_returns_bug_instance(tmp_path):
    """parse_bug returns a Bug dataclass instance."""
    path = write_file(tmp_path, "B-001-bug.md", VALID_BUG_CONTENT)
    result = parse_bug(path)
    assert isinstance(result, Bug)


def test_parse_bug_populates_all_fields(tmp_path):
    """parse_bug populates id, title, severity, status, and created."""
    path = write_file(tmp_path, "B-001-bug.md", VALID_BUG_CONTENT)
    result = parse_bug(path)
    assert result.id == "B-001"
    assert result.title == "Crash on empty input"
    assert result.severity == "high"
    assert result.status == "open"
    assert result.created == "2026-05-10"


def test_parse_bug_task_is_none_when_absent(tmp_path):
    """parse_bug sets task to None when the frontmatter has no task field."""
    path = write_file(tmp_path, "B-001-bug.md", VALID_BUG_CONTENT)
    result = parse_bug(path)
    assert result.task is None


def test_parse_bug_populates_optional_task_when_present(tmp_path):
    """parse_bug populates task when the frontmatter includes a task field."""
    path = write_file(tmp_path, "B-002-bug.md", VALID_BUG_WITH_TASK_CONTENT)
    result = parse_bug(path)
    assert result.task == "T-003"


def test_parse_spec_returns_spec_instance(tmp_path):
    """parse_spec returns a Spec dataclass instance."""
    path = write_file(tmp_path, "ai-team-cli.md", VALID_SPEC_CONTENT)
    result = parse_spec(path)
    assert isinstance(result, Spec)


def test_parse_spec_populates_all_fields(tmp_path):
    """parse_spec populates title, version, status, created, and author."""
    path = write_file(tmp_path, "ai-team-cli.md", VALID_SPEC_CONTENT)
    result = parse_spec(path)
    assert result.title == "ai-team Python CLI"
    assert result.version == "0.1"
    assert result.status == "approved"
    assert result.created == "2026-05-10"
    assert result.author == "planner"


def test_parse_adr_returns_adr_instance(tmp_path):
    """parse_adr returns an Adr dataclass instance."""
    path = write_file(tmp_path, "ADR-001-use-ruamel.md", VALID_ADR_CONTENT)
    result = parse_adr(path)
    assert isinstance(result, Adr)


def test_parse_adr_populates_all_fields(tmp_path):
    """parse_adr populates id, title, status, and created."""
    path = write_file(tmp_path, "ADR-001.md", VALID_ADR_CONTENT)
    result = parse_adr(path)
    assert result.id == "ADR-001"
    assert result.title == "Use ruamel.yaml for round-trip parsing"
    assert result.status == "accepted"
    assert result.created == "2026-05-10"


def test_parse_adr_supersedes_is_none_when_absent(tmp_path):
    """parse_adr sets supersedes to None when the frontmatter has no supersedes field."""
    path = write_file(tmp_path, "ADR-001.md", VALID_ADR_CONTENT)
    result = parse_adr(path)
    assert result.supersedes is None


def test_parse_adr_populates_optional_supersedes_when_present(tmp_path):
    """parse_adr populates supersedes when the frontmatter includes it."""
    path = write_file(tmp_path, "ADR-002.md", VALID_ADR_WITH_SUPERSEDES_CONTENT)
    result = parse_adr(path)
    assert result.supersedes == "ADR-001"


# ---------------------------------------------------------------------------
# AC-2: dump_frontmatter round-trips through parse_* to an equal model
# ---------------------------------------------------------------------------


def test_dump_frontmatter_task_round_trips(tmp_path):
    """dump_frontmatter output parses back to an equal Task model."""
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    original = parse_task(path)
    dumped = dump_frontmatter(original, "Task body here.\n")

    # Write the dumped output and parse it again.
    roundtrip_path = write_file(tmp_path, "T-001-roundtrip.md", dumped)
    restored = parse_task(roundtrip_path)
    assert restored == original


def test_dump_frontmatter_task_with_spec_round_trips(tmp_path):
    """dump_frontmatter round-trips a Task that includes an optional spec field."""
    path = write_file(tmp_path, "T-002-task.md", VALID_TASK_WITH_SPEC_CONTENT)
    original = parse_task(path)
    dumped = dump_frontmatter(original, "Body.\n")

    roundtrip_path = write_file(tmp_path, "T-002-roundtrip.md", dumped)
    restored = parse_task(roundtrip_path)
    assert restored == original


def test_dump_frontmatter_bug_round_trips(tmp_path):
    """dump_frontmatter output parses back to an equal Bug model."""
    path = write_file(tmp_path, "B-001-bug.md", VALID_BUG_CONTENT)
    original = parse_bug(path)
    dumped = dump_frontmatter(original, "# Crash on empty input\n")

    roundtrip_path = write_file(tmp_path, "B-001-roundtrip.md", dumped)
    restored = parse_bug(roundtrip_path)
    assert restored == original


def test_dump_frontmatter_spec_round_trips(tmp_path):
    """dump_frontmatter output parses back to an equal Spec model."""
    path = write_file(tmp_path, "spec.md", VALID_SPEC_CONTENT)
    original = parse_spec(path)
    dumped = dump_frontmatter(original, "# ai-team Python CLI\n")

    roundtrip_path = write_file(tmp_path, "spec-roundtrip.md", dumped)
    restored = parse_spec(roundtrip_path)
    assert restored == original


def test_dump_frontmatter_adr_round_trips(tmp_path):
    """dump_frontmatter output parses back to an equal Adr model."""
    path = write_file(tmp_path, "ADR-001.md", VALID_ADR_CONTENT)
    original = parse_adr(path)
    dumped = dump_frontmatter(original, "# ADR-001: Use ruamel.yaml\n")

    roundtrip_path = write_file(tmp_path, "ADR-001-roundtrip.md", dumped)
    restored = parse_adr(roundtrip_path)
    assert restored == original


def test_dump_frontmatter_adr_with_supersedes_round_trips(tmp_path):
    """dump_frontmatter round-trips an Adr that includes an optional supersedes field."""
    path = write_file(tmp_path, "ADR-002.md", VALID_ADR_WITH_SUPERSEDES_CONTENT)
    original = parse_adr(path)
    dumped = dump_frontmatter(original, "Body.\n")

    roundtrip_path = write_file(tmp_path, "ADR-002-roundtrip.md", dumped)
    restored = parse_adr(roundtrip_path)
    assert restored == original


def test_dump_frontmatter_produces_yaml_fenced_output(tmp_path):
    """dump_frontmatter wraps the frontmatter block in --- fences."""
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    model = parse_task(path)
    dumped = dump_frontmatter(model, "body\n")
    assert dumped.startswith("---\n")
    assert "\n---\n" in dumped


# ---------------------------------------------------------------------------
# AC-3: FrontmatterError raised on missing or invalid field
# ---------------------------------------------------------------------------


def test_frontmatter_error_raised_when_task_id_missing(tmp_path):
    """parse_task raises FrontmatterError when the id field is absent."""
    content = """\
---
title: "Missing ID"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "task-no-id.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_task(path)
    assert "id" in str(exc_info.value)
    assert str(path) in str(exc_info.value)


def test_frontmatter_error_raised_when_task_title_missing(tmp_path):
    """parse_task raises FrontmatterError when the title field is absent."""
    content = """\
---
id: "T-001"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "task-no-title.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_task(path)
    assert "title" in str(exc_info.value)
    assert str(path) in str(exc_info.value)


def test_frontmatter_error_raised_when_task_priority_missing(tmp_path):
    """parse_task raises FrontmatterError when the priority field is absent."""
    content = """\
---
id: "T-001"
title: "A Task"
status: pending
assigned-role: developer
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "task-no-priority.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_task(path)
    assert "priority" in str(exc_info.value)


def test_frontmatter_error_raised_when_task_assigned_role_missing(tmp_path):
    """parse_task raises FrontmatterError when the assigned-role field is absent."""
    content = """\
---
id: "T-001"
title: "A Task"
status: pending
priority: high
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "task-no-role.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_task(path)
    assert "assigned-role" in str(exc_info.value)


def test_frontmatter_error_raised_when_bug_severity_missing(tmp_path):
    """parse_bug raises FrontmatterError when the severity field is absent."""
    content = """\
---
id: "B-001"
title: "A Bug"
status: open
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "bug-no-severity.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_bug(path)
    assert "severity" in str(exc_info.value)
    assert str(path) in str(exc_info.value)


def test_frontmatter_error_raised_when_spec_author_missing(tmp_path):
    """parse_spec raises FrontmatterError when the author field is absent."""
    content = """\
---
title: "A Spec"
version: "0.1"
status: draft
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "spec-no-author.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_spec(path)
    assert "author" in str(exc_info.value)
    assert str(path) in str(exc_info.value)


def test_frontmatter_error_raised_when_adr_id_missing(tmp_path):
    """parse_adr raises FrontmatterError when the id field is absent."""
    content = """\
---
title: "A Decision"
status: proposed
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "adr-no-id.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_adr(path)
    assert "id" in str(exc_info.value)
    assert str(path) in str(exc_info.value)


def test_frontmatter_error_message_names_field_and_path(tmp_path):
    """FrontmatterError message names both the missing field and the file path."""
    content = """\
---
title: "Missing Status"
version: "0.1"
created: 2026-05-10
author: planner
---
Body.
"""
    path = write_file(tmp_path, "spec-no-status.md", content)
    with pytest.raises(FrontmatterError) as exc_info:
        parse_spec(path)
    error_msg = str(exc_info.value)
    assert "status" in error_msg
    assert str(path) in error_msg


def test_frontmatter_error_raised_when_no_frontmatter_block(tmp_path):
    """parse_task raises FrontmatterError when the file has no YAML frontmatter block."""
    content = "Just a plain markdown file with no frontmatter.\n"
    path = write_file(tmp_path, "no-frontmatter.md", content)
    with pytest.raises(FrontmatterError):
        parse_task(path)


# ---------------------------------------------------------------------------
# AC-4: YAML comments and key order preserved across parse/dump cycles
# ---------------------------------------------------------------------------


def test_dump_frontmatter_preserves_key_order(tmp_path):
    """
    dump_frontmatter preserves the insertion order of keys so that
    parse → dump → parse produces frontmatter with the same key sequence.
    """
    # This content has keys in a specific order; verify the dumped output
    # respects that order rather than alphabetising them.
    content = """\
---
id: "T-001"
title: "Order Test"
status: pending
priority: high
assigned-role: developer
created: 2026-05-10
---
Body.
"""
    path = write_file(tmp_path, "T-001-order.md", content)
    model = parse_task(path)
    dumped = dump_frontmatter(model, "Body.\n")

    # Extract the frontmatter section from the dumped output.
    fm_block = dumped.split("---")[1]
    keys_in_order = [
        line.split(":")[0].strip()
        for line in fm_block.splitlines()
        if ":" in line
    ]
    expected_order = ["id", "title", "status", "priority", "assigned-role", "created"]
    assert keys_in_order == expected_order


def test_dump_frontmatter_task_optional_field_omitted_when_none(tmp_path):
    """
    dump_frontmatter does not emit the optional 'spec' key when it is None,
    so the round-tripped file stays clean.
    """
    path = write_file(tmp_path, "T-001-task.md", VALID_TASK_CONTENT)
    model = parse_task(path)
    assert model.spec is None
    dumped = dump_frontmatter(model, "Task body here.\n")
    assert "spec:" not in dumped


def test_dump_frontmatter_adr_optional_field_omitted_when_none(tmp_path):
    """
    dump_frontmatter does not emit the optional 'supersedes' key when it is None.
    """
    path = write_file(tmp_path, "ADR-001.md", VALID_ADR_CONTENT)
    model = parse_adr(path)
    assert model.supersedes is None
    dumped = dump_frontmatter(model, "# ADR-001: Use ruamel.yaml\n")
    assert "supersedes:" not in dumped


def test_dump_frontmatter_task_optional_field_present_when_set(tmp_path):
    """
    dump_frontmatter includes the optional 'spec' key when it is not None,
    so the round-tripped file contains the field.
    """
    path = write_file(tmp_path, "T-002-task.md", VALID_TASK_WITH_SPEC_CONTENT)
    model = parse_task(path)
    dumped = dump_frontmatter(model, "Body.\n")
    assert "spec:" in dumped
