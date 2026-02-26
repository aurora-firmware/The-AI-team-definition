"""Integration Test Phase — merge orchestration, test run, bisect on failure."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field

from el_equipo_ai.logger import Logger
from el_equipo_ai.manifest_bridge import VKClient
from el_equipo_ai.notifier import Notifier


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class MergeResult:
    success: bool
    conflict_files: list[str] = field(default_factory=list)
    output: str = ""


@dataclass
class TestResult:
    passed: bool
    output: str = ""
    exit_code: int = 0


@dataclass
class MergeAllResult:
    success: bool
    failed_at: str | None = None
    conflict_files: list[str] = field(default_factory=list)
    merged_branches: list[str] = field(default_factory=list)


@dataclass
class IntegrationResult:
    status: str            # "passed" | "conflict_escalated" | "test_failed"
    failing_branch: str | None = None
    conflict_fix_task_id: str | None = None
    test_output: str = ""


# ---------------------------------------------------------------------------
# T5.1 — Low-level git helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def create_branch(branch_name: str, from_ref: str = "main", cwd: str | None = None) -> bool:
    result = _run(["git", "checkout", "-b", branch_name, from_ref], cwd=cwd)
    return result.returncode == 0


def merge_branch(source_branch: str, cwd: str | None = None) -> MergeResult:
    result = _run(["git", "merge", "--no-ff", source_branch], cwd=cwd)
    if result.returncode == 0:
        return MergeResult(success=True, output=result.stdout)

    # Parse conflict file names from git output
    conflict_files: list[str] = []
    for line in (result.stdout + result.stderr).splitlines():
        # "CONFLICT (content): Merge conflict in path/to/file.py"
        if "CONFLICT" in line and " in " in line:
            parts = line.rsplit(" in ", 1)
            if len(parts) == 2:
                conflict_files.append(parts[1].strip())

    return MergeResult(
        success=False,
        conflict_files=conflict_files,
        output=result.stdout + result.stderr,
    )


def run_tests(test_command: str, cwd: str | None = None) -> TestResult:
    import shlex
    parts = shlex.split(test_command)
    result = _run(parts, cwd=cwd)
    return TestResult(
        passed=result.returncode == 0,
        output=result.stdout + result.stderr,
        exit_code=result.returncode,
    )


def abort_merge(cwd: str | None = None) -> None:
    _run(["git", "merge", "--abort"], cwd=cwd)


def get_current_branch(cwd: str | None = None) -> str:
    result = _run(["git", "branch", "--show-current"], cwd=cwd)
    return result.stdout.strip()


def get_merge_log(branch: str, cwd: str | None = None) -> list[str]:
    """Return list of branch names already merged into *branch*."""
    result = _run(
        ["git", "branch", "--merged", branch],
        cwd=cwd,
    )
    branches: list[str] = []
    for line in result.stdout.splitlines():
        name = line.strip().lstrip("* ")
        if name and name != branch:
            branches.append(name)
    return branches


# ---------------------------------------------------------------------------
# T5.2 — Sequential merge in dependency order
# ---------------------------------------------------------------------------


def merge_all_branches(
    branches_in_order: list[str],
    integration_branch: str,
    logger: Logger,
    cwd: str | None = None,
) -> MergeAllResult:
    """Merge branches sequentially into *integration_branch*.

    Crash recovery: checks which branches are already merged and skips them.
    """
    # Create integration branch (may already exist on restart)
    if get_current_branch(cwd=cwd) != integration_branch:
        already_exists = _run(
            ["git", "rev-parse", "--verify", integration_branch], cwd=cwd
        ).returncode == 0
        if already_exists:
            _run(["git", "checkout", integration_branch], cwd=cwd)
        else:
            create_branch(integration_branch, from_ref="main", cwd=cwd)

    # Crash recovery: skip already-merged branches
    already_merged = set(get_merge_log(integration_branch, cwd=cwd))
    merged: list[str] = [b for b in branches_in_order if b in already_merged]

    for branch in branches_in_order:
        if branch in already_merged:
            logger.log("integration_skip_merged", branch=branch)
            continue

        result = merge_branch(branch, cwd=cwd)
        if not result.success:
            abort_merge(cwd=cwd)
            logger.log(
                "integration_merge",
                branch=branch,
                status="conflict",
                conflict_files=result.conflict_files,
            )
            return MergeAllResult(
                success=False,
                failed_at=branch,
                conflict_files=result.conflict_files,
                merged_branches=merged,
            )
        merged.append(branch)
        logger.log("integration_merge", branch=branch, status="ok")

    return MergeAllResult(success=True, merged_branches=merged)


# ---------------------------------------------------------------------------
# T5.3 — Bisect on test failure
# ---------------------------------------------------------------------------


def bisect_failure(
    branches: list[str],
    test_command: str,
    logger: Logger,
    cwd: str | None = None,
) -> str:
    """Binary search for the branch that introduced a test failure.

    Assumes the integration branch has been checked out.
    Returns the name of the first branch that makes tests fail.
    """
    if len(branches) == 1:
        return branches[0]

    mid = len(branches) // 2
    first_half = branches[:mid]
    second_half = branches[mid:]

    logger.log("bisect_step", testing_branches=first_half, total=len(branches))

    # Test first half
    test_branch = f"bisect-test-{mid}"
    create_branch(test_branch, from_ref="main", cwd=cwd)
    for b in first_half:
        merge_branch(b, cwd=cwd)

    result = run_tests(test_command, cwd=cwd)

    # Return to integration state (checkout main and recreate)
    _run(["git", "checkout", "main"], cwd=cwd)
    _run(["git", "branch", "-D", test_branch], cwd=cwd)

    if not result.passed:
        # Failure is in the first half
        return bisect_failure(first_half, test_command, logger, cwd=cwd)
    else:
        # Failure is in the second half
        return bisect_failure(second_half, test_command, logger, cwd=cwd)


# ---------------------------------------------------------------------------
# T5.4 — Conflict escalation to VK + full pipeline
# ---------------------------------------------------------------------------


def handle_merge_conflict(
    failed_branch: str,
    conflict_files: list[str],
    conflict_diff: str,
    vk_client: VKClient,
    logger: Logger,
) -> str:
    """Create a fix task in VK for the merge conflict. Returns new task ID."""
    description = (
        f"A merge conflict occurred when integrating branch `{failed_branch}`.\n\n"
        f"Conflicting files:\n"
        + "\n".join(f"- {f}" for f in conflict_files)
        + f"\n\nConflict diff:\n```\n{conflict_diff}\n```\n\n"
        "Please resolve the conflicts and ensure all tests pass."
    )
    task_id = vk_client.create_task(
        title=f"Resolve merge conflict: {failed_branch}",
        description=description,
        role="executor",
    )
    logger.log(
        "integration_conflict",
        branch=failed_branch,
        conflict_files=conflict_files,
        fix_task=task_id,
    )
    return task_id


def integration_pipeline(
    branches_in_order: list[str],
    test_command: str,
    vk_client: VKClient,
    notifier: Notifier,
    logger: Logger,
    cwd: str | None = None,
) -> IntegrationResult:
    """Full integration pipeline: merge → test → bisect or notify.

    1. Merge all approved branches in dependency order.
    2. If conflict → create VK fix task, return "conflict_escalated".
    3. If all merged → run tests.
    4. If tests pass → notify human for final approval, return "passed".
    5. If tests fail → bisect, return "test_failed" with failing branch.
    """
    integration_branch = "integration/el-equipo-ai"

    merge_result = merge_all_branches(
        branches_in_order, integration_branch, logger, cwd=cwd
    )

    if not merge_result.success:
        # Get conflict diff for context
        diff_result = _run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=cwd,
        )
        conflict_diff = diff_result.stdout

        fix_task_id = handle_merge_conflict(
            failed_branch=merge_result.failed_at or "unknown",
            conflict_files=merge_result.conflict_files,
            conflict_diff=conflict_diff,
            vk_client=vk_client,
            logger=logger,
        )
        return IntegrationResult(
            status="conflict_escalated",
            failing_branch=merge_result.failed_at,
            conflict_fix_task_id=fix_task_id,
        )

    test_result = run_tests(test_command, cwd=cwd)

    if test_result.passed:
        notifier.action_required(
            title="Integration tests passed — approve final merge?",
            body=(
                f"All {len(branches_in_order)} branches merged successfully.\n"
                f"Test suite passed. Ready to merge to main."
            ),
            vk_link=None,
        )
        logger.log("integration_passed", branches=len(branches_in_order))
        return IntegrationResult(status="passed", test_output=test_result.output)

    # Tests failed — bisect
    logger.log("integration_test_failed", exit_code=test_result.exit_code)
    failing_branch = bisect_failure(branches_in_order, test_command, logger, cwd=cwd)
    logger.log("integration_bisect_result", failing_branch=failing_branch)
    return IntegrationResult(
        status="test_failed",
        failing_branch=failing_branch,
        test_output=test_result.output,
    )
