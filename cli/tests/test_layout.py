"""Tests for read-only project layout contract validation."""

from __future__ import annotations

import importlib.resources as resources
import shutil
from pathlib import Path

import pytest

from ai_team.core.layout import (
    LayoutContract,
    LayoutFinding,
    check_layout,
    check_level_1,
    check_level_2,
    check_level_4,
    resolve_layout,
)


def _write_marker(
    repo: Path,
    *,
    project_dir: str = "project",
    tools: tuple[str, ...] = ("claude", "codex"),
    version: str = "1.2.3",
) -> None:
    rendered_tools = ", ".join(f'"{tool}"' for tool in tools)
    (repo / ".ai-team.toml").write_text(
        f'[project]\ndir = "{project_dir}"\n\n'
        f"[init]\ntools = [{rendered_tools}]\n"
        f'framework_version = "{version}"\n',
        encoding="utf-8",
    )


def _create_current_scaffold(repo: Path, tools: tuple[str, ...]) -> None:
    scaffold_root = resources.files("ai_team.init").joinpath("scaffolds")
    for source_name, destination_name in (("project", "project"),) + tuple(
        (tool, f".{tool}") for tool in tools
    ):
        source = scaffold_root.joinpath(source_name)
        for entry in source.rglob("*"):
            if entry.is_dir():
                (repo / destination_name / entry.relative_to(source)).mkdir(
                    parents=True, exist_ok=True
                )
        (repo / destination_name).mkdir(parents=True, exist_ok=True)


def _snapshot(repo: Path) -> list[tuple[str, bool, bytes | None]]:
    return [
        (
            path.relative_to(repo).as_posix(),
            path.is_dir(),
            None if path.is_dir() else path.read_bytes(),
        )
        for path in sorted(repo.rglob("*"))
    ]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _frontmatter(**values: str) -> str:
    fields = "\n".join(f"{key}: {value}" for key, value in values.items())
    return f"---\n{fields}\n---\n\nBody.\n"


def test_resolve_layout_reads_valid_local_marker_and_distribution_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_marker(
        tmp_path,
        project_dir="team-state",
        tools=("codex", "claude"),
        version="2.4.0",
    )
    monkeypatch.setattr("importlib.metadata.version", lambda name: "2.4.0")

    contract, findings = resolve_layout(tmp_path)

    assert contract == LayoutContract(
        repo=tmp_path,
        marker=tmp_path / ".ai-team.toml",
        project_dir=tmp_path / "team-state",
        tools=("codex", "claude"),
        configured_version="2.4.0",
        current_version="2.4.0",
        raw_configured_version="2.4.0",
    )
    assert findings == []


@pytest.mark.parametrize(
    ("marker", "expected_problem"),
    [
        (None, "missing"),
        ("not valid = [toml", "invalid"),
        ('[project]\ndir = "../outside"\n[init]\ntools = "codex"\n', "invalid"),
    ],
)
def test_resolve_layout_reports_marker_faults_and_uses_safe_conventions(
    tmp_path: Path, marker: str | None, expected_problem: str
) -> None:
    if marker is not None:
        (tmp_path / ".ai-team.toml").write_text(marker, encoding="utf-8")

    contract, findings = resolve_layout(tmp_path, current_version="1.2.3")

    assert contract.project_dir == tmp_path / "project"
    assert contract.tools == ()
    assert findings
    assert all(finding.suggested_fix for finding in findings)
    assert any(expected_problem in finding.problem.lower() for finding in findings)


def test_level_1_reports_every_missing_current_scaffold_directory_and_allows_extra(
    tmp_path: Path,
) -> None:
    _write_marker(tmp_path, tools=("codex",))
    _create_current_scaffold(tmp_path, ("codex",))
    shutil.rmtree(tmp_path / "project" / "tasks" / "blocked")
    shutil.rmtree(tmp_path / ".codex" / "agents")
    (tmp_path / "project" / "extra").mkdir()
    contract, resolution_findings = resolve_layout(tmp_path, current_version="1.2.3")

    findings = check_level_1(contract)

    assert resolution_findings == []
    assert {finding.path for finding in findings} == {
        "project/tasks/blocked",
        ".codex/agents",
    }
    assert all(finding.level == 1 for finding in findings)
    assert all(finding.problem and finding.suggested_fix for finding in findings)


@pytest.mark.parametrize(
    ("relative_path", "content", "expected_problem"),
    [
        (
            "project/specs/Bad Spec.md",
            _frontmatter(
                id="S-001",
                title="Spec",
                version="'0.1'",
                status="approved",
                created="2026-06-24",
                author="planner",
            ),
            "filename",
        ),
        (
            "project/tasks/pending/T-001-task.md",
            _frontmatter(
                id="T-001",
                title="Task",
                status="pending",
                priority="medium",
                created="2026-06-24",
            ),
            "frontmatter",
        ),
        (
            "project/bugs/open/not-a-bug.md",
            _frontmatter(
                id="B-001",
                title="Bug",
                severity="medium",
                status="open",
                created="2026-06-24",
            ),
            "filename",
        ),
        (
            "project/change-requests/request.md",
            _frontmatter(
                id="CR-001",
                title="Request",
                status="pending",
                created="2026-06-24",
            ),
            "filename",
        ),
        (
            "project/decisions/decision.md",
            _frontmatter(
                id="ADR-001",
                title="Decision",
                status="accepted",
                created="2026-06-24",
            ),
            "filename",
        ),
    ],
)
def test_level_2_reuses_artifact_filename_and_frontmatter_rules(
    tmp_path: Path,
    relative_path: str,
    content: str,
    expected_problem: str,
) -> None:
    _write_marker(tmp_path, tools=())
    _write(tmp_path / relative_path, content)
    contract, resolution_findings = resolve_layout(tmp_path, current_version="1.2.3")

    findings = check_level_2(contract)

    assert resolution_findings == []
    assert findings
    assert all(finding.level == 2 for finding in findings)
    assert any(expected_problem in finding.problem.lower() for finding in findings)
    assert all(finding.suggested_fix for finding in findings)


@pytest.mark.parametrize(
    ("relative_path", "status", "folder"),
    [
        ("project/tasks/pending/T-001-task.md", "completed", "pending"),
        ("project/bugs/open/B-001-bug.md", "resolved", "open"),
    ],
)
def test_level_2_reports_lifecycle_status_mismatches_with_actionable_fix(
    tmp_path: Path, relative_path: str, status: str, folder: str
) -> None:
    _write_marker(tmp_path, tools=())
    if "/tasks/" in relative_path:
        content = _frontmatter(
            id="T-001",
            title="Task",
            status=status,
            priority="medium",
            **{"assigned-role": "developer"},
            created="2026-06-24",
        )
    else:
        content = _frontmatter(
            id="B-001",
            title="Bug",
            severity="medium",
            status=status,
            created="2026-06-24",
        )
    _write(tmp_path / relative_path, content)
    contract, _ = resolve_layout(tmp_path, current_version="1.2.3")

    findings = check_level_2(contract)

    mismatch = next(
        finding for finding in findings if "does not match" in finding.problem
    )
    assert folder in mismatch.problem
    assert "status" in mismatch.suggested_fix.lower()
    assert "move" in mismatch.suggested_fix.lower()


def test_level_2_ignores_placeholders_and_non_artifact_documentation(
    tmp_path: Path,
) -> None:
    _write_marker(tmp_path, tools=())
    _write(tmp_path / "project/tasks/pending/.gitkeep", "")
    _write(tmp_path / "project/tasks/pending/TEMPLATE-task.md", "not frontmatter")
    _write(tmp_path / "project/docs/Bad Documentation.md", "not frontmatter")
    contract, _ = resolve_layout(tmp_path, current_version="1.2.3")

    assert check_level_2(contract) == []


def test_level_2_reports_malformed_artifact_and_continues_independent_checks(
    tmp_path: Path,
) -> None:
    _write_marker(tmp_path, tools=())
    _write(
        tmp_path / "project/tasks/pending/T-001-malformed.md",
        "---\ninvalid: [yaml\n---\n",
    )
    _write(
        tmp_path / "project/decisions/bad-name.md",
        _frontmatter(
            id="ADR-001",
            title="Decision",
            status="accepted",
            created="2026-06-24",
        ),
    )
    contract, _ = resolve_layout(tmp_path, current_version="1.2.3")

    findings = check_level_2(contract)

    assert {finding.path for finding in findings} == {
        "project/tasks/pending/T-001-malformed.md",
        "project/decisions/bad-name.md",
    }
    assert any("frontmatter" in finding.problem.lower() for finding in findings)
    assert any("filename" in finding.problem.lower() for finding in findings)


@pytest.mark.parametrize(
    ("configured", "problem_parts"),
    [
        (None, ("missing", "1.2.3")),
        (42, ("invalid", "42", "1.2.3")),
        ("1.2.2", ("1.2.2", "1.2.3")),
    ],
)
def test_level_4_reports_missing_invalid_and_non_exact_versions(
    tmp_path: Path, configured: str | int | None, problem_parts: tuple[str, ...]
) -> None:
    marker_version = (
        ""
        if configured is None
        else f'framework_version = "{configured}"\n'
        if isinstance(configured, str)
        else f"framework_version = {configured}\n"
    )
    (tmp_path / ".ai-team.toml").write_text(
        '[project]\ndir = "project"\n[init]\ntools = []\n' + marker_version,
        encoding="utf-8",
    )
    contract, resolution_findings = resolve_layout(tmp_path, current_version="1.2.3")

    findings = [*resolution_findings, *check_level_4(contract)]

    assert contract.raw_configured_version == configured
    if configured == 42:
        assert contract.configured_version is None
    assert any(finding.level == 4 for finding in findings)
    combined_problem = " ".join(finding.problem.lower() for finding in findings)
    assert all(part.lower() in combined_problem for part in problem_parts)


def test_level_4_accepts_only_an_exact_version_match(tmp_path: Path) -> None:
    _write_marker(tmp_path, tools=(), version="1.2.3+local.1")
    contract, resolution_findings = resolve_layout(
        tmp_path, current_version="1.2.3+local.1"
    )

    assert resolution_findings == []
    assert check_level_4(contract) == []


def test_check_layout_returns_ordered_findings_without_modifying_repository(
    tmp_path: Path,
) -> None:
    _write_marker(tmp_path, tools=("claude",), version="1.0.0")
    (tmp_path / "project" / "unexpected").mkdir(parents=True)
    before = _snapshot(tmp_path)

    findings = check_layout(tmp_path, current_version="2.0.0")

    assert findings == sorted(
        findings, key=lambda finding: (finding.level, finding.path)
    )
    assert all(isinstance(finding, LayoutFinding) for finding in findings)
    assert all(
        finding.level and finding.path and finding.problem and finding.suggested_fix
        for finding in findings
    )
    assert _snapshot(tmp_path) == before
