"""Tests for the human-readable ``ai-team check-layout`` report."""

from pathlib import Path

from typer.testing import CliRunner

from ai_team.cli import app
from ai_team.core.layout import LayoutFinding


def test_check_layout_reports_all_findings_in_level_and_path_order(
    monkeypatch,
    tmp_path,
):
    """An issue report is complete, deterministic, and exits unsuccessfully."""
    from ai_team.commands import check_layout as command

    findings = [
        LayoutFinding(4, ".ai-team.toml", "version differs", "update version"),
        LayoutFinding(2, "project/tasks/z.md", "bad frontmatter", "fix metadata"),
        LayoutFinding(1, "project/tasks", "directory missing", "restore scaffold"),
        LayoutFinding(3, "AGENTS.md", "section missing", "add section"),
        LayoutFinding(2, "project/tasks/a.md", "bad filename", "rename file"),
    ]
    received_repositories: list[Path] = []

    def fake_check_layout(repo: Path) -> list[LayoutFinding]:
        received_repositories.append(repo)
        return findings

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(command, "run_layout_checks", fake_check_layout)

    result = CliRunner().invoke(app, ["check-layout"])

    assert result.exit_code == 1
    assert received_repositories == [tmp_path]
    assert "5 layout findings" in result.stdout
    expected_order = [
        "Level: 1",
        "Path: project/tasks",
        "Level: 2",
        "Path: project/tasks/a.md",
        "Path: project/tasks/z.md",
        "Level: 3",
        "Path: AGENTS.md",
        "Level: 4",
        "Path: .ai-team.toml",
    ]
    positions = [result.stdout.index(value) for value in expected_order]
    assert positions == sorted(positions)
    for finding in findings:
        assert f"Problem: {finding.problem}" in result.stdout
        assert f"Suggested fix: {finding.suggested_fix}" in result.stdout


def test_check_layout_reports_an_unambiguous_clean_result(monkeypatch, tmp_path):
    """A clean repository produces an explicit success result and zero exit."""
    from ai_team.commands import check_layout as command

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(command, "run_layout_checks", lambda repo: [])

    result = CliRunner().invoke(app, ["check-layout"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Layout check passed: no findings."


def test_check_layout_reports_malformed_prerequisite_without_mutating_repository(
    monkeypatch,
    tmp_path,
):
    """Malformed local inputs become findings and remain byte-for-byte unchanged."""
    marker = tmp_path / ".ai-team.toml"
    marker.write_text("[project\ndir = broken\n", encoding="utf-8")
    existing = tmp_path / "notes.txt"
    existing.write_text("keep me unchanged\n", encoding="utf-8")

    def snapshot() -> dict[str, bytes | None]:
        return {
            path.relative_to(tmp_path).as_posix(): path.read_bytes()
            if path.is_file()
            else None
            for path in tmp_path.rglob("*")
        }

    before = snapshot()
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["check-layout"])

    assert result.exit_code == 1
    assert "Path: .ai-team.toml" in result.stdout
    assert "Problem: Repository marker .ai-team.toml is invalid" in result.stdout
    assert "Suggested fix:" in result.stdout
    assert snapshot() == before


def test_check_layout_resolves_repository_root_from_nested_directory(
    monkeypatch,
    tmp_path,
):
    """Invocation below the root validates the repository rather than the cwd."""
    from ai_team.commands import check_layout as command

    (tmp_path / ".ai-team.toml").write_text("", encoding="utf-8")
    nested = tmp_path / "src" / "package"
    nested.mkdir(parents=True)
    received_repositories: list[Path] = []

    def fake_check_layout(repo: Path) -> list[LayoutFinding]:
        received_repositories.append(repo)
        return []

    monkeypatch.chdir(nested)
    monkeypatch.setattr(command, "run_layout_checks", fake_check_layout)

    result = CliRunner().invoke(app, ["check-layout"])

    assert result.exit_code == 0
    assert received_repositories == [tmp_path]
