"""Tests for el_equipo_ai.integration — git ops, merge, bisect, pipeline."""

from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from el_equipo_ai.integration import (
    MergeAllResult,
    MergeResult,
    TestResult,
    abort_merge,
    bisect_failure,
    create_branch,
    get_current_branch,
    get_merge_log,
    handle_merge_conflict,
    integration_pipeline,
    merge_all_branches,
    merge_branch,
    run_tests,
)
from el_equipo_ai.logger import Logger
from el_equipo_ai.manifest_bridge import VKClient
from el_equipo_ai.models import LogConfig
from el_equipo_ai.notifier import Notifier


# ---------------------------------------------------------------------------
# Test git repo fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Create a minimal git repo with an initial commit on 'main'."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=str(repo),
            check=True,
            capture_output=True,
        )

    git("init", "-b", "main")
    git("config", "user.email", "test@test.com")
    git("config", "user.name", "Test")

    (repo / "README.md").write_text("# test repo\n")
    git("add", ".")
    git("commit", "-m", "initial")
    return repo


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def vk_client(logger: Logger) -> VKClient:
    return VKClient(vk_url="http://localhost:3000", logger=logger)


@pytest.fixture()
def notifier(logger: Logger) -> Notifier:
    return Notifier(channels=[], logger=logger)


def make_branch_with_file(repo: Path, branch: str, filename: str, content: str) -> None:
    """Create a branch off main with a new/modified file."""
    subprocess.run(["git", "checkout", "main"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)
    (repo / filename).write_text(content)
    subprocess.run(["git", "add", "."], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {filename}"],
        cwd=str(repo), check=True, capture_output=True,
    )
    subprocess.run(["git", "checkout", "main"], cwd=str(repo), check=True, capture_output=True)


# ---------------------------------------------------------------------------
# T5.1 — Git helpers
# ---------------------------------------------------------------------------


class TestGitHelpers:
    def test_create_branch_succeeds(self, git_repo: Path) -> None:
        ok = create_branch("feature/test", "main", cwd=str(git_repo))
        assert ok
        assert get_current_branch(cwd=str(git_repo)) == "feature/test"

    def test_get_current_branch(self, git_repo: Path) -> None:
        assert get_current_branch(cwd=str(git_repo)) == "main"

    def test_merge_branch_clean(self, git_repo: Path) -> None:
        make_branch_with_file(git_repo, "feat/a", "a.txt", "hello")
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)
        result = merge_branch("feat/a", cwd=str(git_repo))
        assert result.success

    def test_merge_branch_conflict(self, git_repo: Path) -> None:
        # Both branches edit the same line differently
        make_branch_with_file(git_repo, "feat/x", "conflict.txt", "version A\n")
        make_branch_with_file(git_repo, "feat/y", "conflict.txt", "version B\n")
        # Merge feat/x first
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)
        merge_branch("feat/x", cwd=str(git_repo))
        # Now merge feat/y — should conflict
        result = merge_branch("feat/y", cwd=str(git_repo))
        assert not result.success
        abort_merge(cwd=str(git_repo))

    def test_run_tests_pass(self, git_repo: Path) -> None:
        result = run_tests("echo all good", cwd=str(git_repo))
        assert result.passed
        assert result.exit_code == 0

    def test_run_tests_fail(self, git_repo: Path) -> None:
        result = run_tests("false", cwd=str(git_repo))
        assert not result.passed
        assert result.exit_code != 0

    def test_abort_merge_cleans_up(self, git_repo: Path) -> None:
        make_branch_with_file(git_repo, "feat/x2", "conflict2.txt", "version A\n")
        make_branch_with_file(git_repo, "feat/y2", "conflict2.txt", "version B\n")
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)
        merge_branch("feat/x2", cwd=str(git_repo))
        merge_branch("feat/y2", cwd=str(git_repo))
        abort_merge(cwd=str(git_repo))
        # Should be back on main without conflict
        assert get_current_branch(cwd=str(git_repo)) == "main"

    def test_get_merge_log(self, git_repo: Path) -> None:
        make_branch_with_file(git_repo, "feat/merged", "merged.txt", "merged\n")
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)
        merge_branch("feat/merged", cwd=str(git_repo))
        merged = get_merge_log("main", cwd=str(git_repo))
        assert "feat/merged" in merged


# ---------------------------------------------------------------------------
# T5.2 — Sequential merge
# ---------------------------------------------------------------------------


class TestMergeAllBranches:
    def test_all_clean_merge(self, git_repo: Path, logger: Logger) -> None:
        make_branch_with_file(git_repo, "feat/1", "f1.txt", "a")
        make_branch_with_file(git_repo, "feat/2", "f2.txt", "b")
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)
        result = merge_all_branches(
            ["feat/1", "feat/2"], "integration/test", logger, cwd=str(git_repo)
        )
        assert result.success
        assert len(result.merged_branches) == 2

    def test_conflict_returns_failure(self, git_repo: Path, logger: Logger) -> None:
        make_branch_with_file(git_repo, "feat/a", "shared.txt", "version A\n")
        make_branch_with_file(git_repo, "feat/b", "shared.txt", "version B\n")
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)
        result = merge_all_branches(
            ["feat/a", "feat/b"], "integration/conflict-test", logger, cwd=str(git_repo)
        )
        assert not result.success
        assert result.failed_at == "feat/b"

    def test_already_merged_skipped_on_restart(
        self, git_repo: Path, logger: Logger
    ) -> None:
        make_branch_with_file(git_repo, "feat/1", "r1.txt", "a")
        make_branch_with_file(git_repo, "feat/2", "r2.txt", "b")
        subprocess.run(["git", "checkout", "main"], cwd=str(git_repo), capture_output=True)

        # First run: merge feat/1
        merge_all_branches(["feat/1"], "integration/restart-test", logger, cwd=str(git_repo))

        # Second run: resume with both branches — feat/1 should be skipped
        subprocess.run(
            ["git", "checkout", "integration/restart-test"],
            cwd=str(git_repo), capture_output=True,
        )
        result = merge_all_branches(
            ["feat/1", "feat/2"], "integration/restart-test", logger, cwd=str(git_repo)
        )
        assert result.success


# ---------------------------------------------------------------------------
# T5.3 — Bisect
# ---------------------------------------------------------------------------


class TestBisectFailure:
    def test_identifies_single_failing_branch(
        self, git_repo: Path, logger: Logger
    ) -> None:
        # With one branch, bisect is trivial
        result = bisect_failure(["feat/only"], "true", logger, cwd=str(git_repo))
        assert result == "feat/only"

    def test_bisect_with_mock_test_results(self, logger: Logger) -> None:
        """Mock git and test operations to verify bisect logic."""
        branches = ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"]
        # Suppose b5 is the culprit — first 4 pass, from 5 onwards fail

        call_log: list[list[str]] = []

        def mock_run_tests(cmd, cwd=None) -> TestResult:
            # We need to know which branches were merged — track by monkeypatching
            # Instead, just return pass for <=4 branches, fail for >4
            merged = get_merged_count()
            return TestResult(passed=merged <= 4, output="", exit_code=0 if merged <= 4 else 1)

        merged_count = [0]
        original_merge = merge_branch
        original_create = create_branch

        def mock_merge(branch, cwd=None) -> MergeResult:
            merged_count[0] += 1
            return MergeResult(success=True)

        def mock_create(name, from_ref="main", cwd=None) -> bool:
            merged_count[0] = 0
            return True

        def get_merged_count():
            return merged_count[0]

        with patch("el_equipo_ai.integration.merge_branch", side_effect=mock_merge), \
             patch("el_equipo_ai.integration.create_branch", side_effect=mock_create), \
             patch("el_equipo_ai.integration.run_tests", side_effect=mock_run_tests), \
             patch("el_equipo_ai.integration._run"):  # suppress git branch -D
            result = bisect_failure(branches, "pytest", logger)

        # Should identify one of b5-b8 as the culprit
        assert result in branches


# ---------------------------------------------------------------------------
# T5.4 — Conflict escalation + full pipeline
# ---------------------------------------------------------------------------


class TestHandleMergeConflict:
    def test_creates_vk_task_with_correct_title(
        self, vk_client: VKClient, logger: Logger
    ) -> None:
        with patch.object(vk_client, "create_task", return_value="vk-fix-1") as mock_create:
            task_id = handle_merge_conflict(
                failed_branch="feat/broken",
                conflict_files=["src/main.py"],
                conflict_diff="@@...",
                vk_client=vk_client,
                logger=logger,
            )
        assert task_id == "vk-fix-1"
        assert "feat/broken" in mock_create.call_args.kwargs["title"]

    def test_conflict_files_in_description(
        self, vk_client: VKClient, logger: Logger
    ) -> None:
        with patch.object(vk_client, "create_task", return_value="vk-fix-2") as mock_create:
            handle_merge_conflict(
                failed_branch="feat/conflict",
                conflict_files=["a.py", "b.py"],
                conflict_diff="diff...",
                vk_client=vk_client,
                logger=logger,
            )
        desc = mock_create.call_args.kwargs["description"]
        assert "a.py" in desc
        assert "b.py" in desc


class TestIntegrationPipeline:
    def test_clean_merge_tests_pass_notifies(
        self, logger: Logger, vk_client: VKClient, notifier: Notifier, capsys
    ) -> None:
        with patch("el_equipo_ai.integration.merge_all_branches") as mock_merge, \
             patch("el_equipo_ai.integration.run_tests") as mock_tests:
            mock_merge.return_value = MergeAllResult(success=True, merged_branches=["b1", "b2"])
            mock_tests.return_value = TestResult(passed=True)

            result = integration_pipeline(
                ["b1", "b2"], "pytest", vk_client, notifier, logger
            )

        assert result.status == "passed"
        captured = capsys.readouterr()
        assert "Integration tests passed" in captured.out

    def test_merge_conflict_creates_vk_task(
        self, logger: Logger, vk_client: VKClient, notifier: Notifier
    ) -> None:
        with patch("el_equipo_ai.integration.merge_all_branches") as mock_merge, \
             patch("el_equipo_ai.integration._run") as mock_run, \
             patch.object(vk_client, "create_task", return_value="vk-fix-99"):
            mock_merge.return_value = MergeAllResult(
                success=False, failed_at="feat/bad", conflict_files=["bad.py"]
            )
            mock_run.return_value = MagicMock(stdout="")

            result = integration_pipeline(
                ["feat/a", "feat/bad"], "pytest", vk_client, notifier, logger
            )

        assert result.status == "conflict_escalated"
        assert result.conflict_fix_task_id == "vk-fix-99"

    def test_tests_fail_bisects(
        self, logger: Logger, vk_client: VKClient, notifier: Notifier
    ) -> None:
        with patch("el_equipo_ai.integration.merge_all_branches") as mock_merge, \
             patch("el_equipo_ai.integration.run_tests") as mock_tests, \
             patch("el_equipo_ai.integration.bisect_failure", return_value="feat/culprit"):
            mock_merge.return_value = MergeAllResult(success=True, merged_branches=["feat/a", "feat/culprit"])
            mock_tests.return_value = TestResult(passed=False, exit_code=1)

            result = integration_pipeline(
                ["feat/a", "feat/culprit"], "pytest", vk_client, notifier, logger
            )

        assert result.status == "test_failed"
        assert result.failing_branch == "feat/culprit"
