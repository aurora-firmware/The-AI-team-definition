"""Tests for el_equipo_ai.stall_detector."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import LogConfig, StallConfig
from el_equipo_ai.stall_detector import StallDetector


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def config() -> StallConfig:
    return StallConfig(
        repeat_threshold=3,
        grace_calls_after_signal=5,
        hard_timeout_minutes=30,
        grace_timeout_minutes=2,
    )


@pytest.fixture()
def detector(config: StallConfig, logger: Logger) -> StallDetector:
    return StallDetector(config=config, logger=logger)


def record_n(detector: StallDetector, task_id: str, tool: str, inp: str, out: str, n: int) -> None:
    for _ in range(n):
        detector.record_tool_call(task_id, tool, inp, out)


class TestPatternDetection:
    def test_no_stall_on_varied_calls(self, detector: StallDetector) -> None:
        detector.record_tool_call("t1", "read_file", "a.py", "content1")
        detector.record_tool_call("t1", "edit_file", "a.py", "ok")
        detector.record_tool_call("t1", "run_command", "pytest", "passed")
        assert detector.check_stall("t1") is None

    def test_command_loop_detected(self, detector: StallDetector) -> None:
        record_n(detector, "t1", "run_command", "make build", "error: not found", 3)
        assert detector.check_stall("t1") == "command_loop"

    def test_command_loop_not_detected_below_threshold(self, detector: StallDetector) -> None:
        record_n(detector, "t1", "run_command", "make build", "error: not found", 2)
        assert detector.check_stall("t1") is None

    def test_command_loop_different_outputs_not_detected(self, detector: StallDetector) -> None:
        detector.record_tool_call("t1", "run_command", "pytest", "error A")
        detector.record_tool_call("t1", "run_command", "pytest", "error B")
        detector.record_tool_call("t1", "run_command", "pytest", "error C")
        assert detector.check_stall("t1") is None

    def test_read_loop_detected(self, detector: StallDetector) -> None:
        record_n(detector, "t1", "read_file", "config.py", "# content", 3)
        assert detector.check_stall("t1") == "read_loop"

    def test_read_loop_cleared_by_edit(self, detector: StallDetector) -> None:
        detector.record_tool_call("t1", "read_file", "config.py", "# content")
        detector.record_tool_call("t1", "read_file", "config.py", "# content")
        detector.record_tool_call("t1", "edit_file", "config.py", "updated")  # edit breaks loop
        detector.record_tool_call("t1", "read_file", "config.py", "# content")
        assert detector.check_stall("t1") is None

    def test_edit_revert_cycle_detected(self, detector: StallDetector) -> None:
        for _ in range(3):
            detector.record_tool_call("t1", "edit_file", "main.py", "changed")
            detector.record_tool_call("t1", "run_command", "pytest", "FAILED: assert error")
        assert detector.check_stall("t1") == "edit_revert_cycle"

    def test_different_tasks_tracked_independently(self, detector: StallDetector) -> None:
        record_n(detector, "task-A", "run_command", "make", "error", 3)
        # task-B should not be stalled
        assert detector.check_stall("task-B") is None
        assert detector.check_stall("task-A") == "command_loop"

    def test_unknown_task_returns_none(self, detector: StallDetector) -> None:
        assert detector.check_stall("nonexistent") is None


class TestWrapUpIntervention:
    def test_wrap_up_message_contains_required_instructions(
        self, detector: StallDetector
    ) -> None:
        msg = detector.get_wrap_up_message("command_loop", "t1")
        assert "what you tried" in msg.lower()
        assert "failing" in msg.lower()
        assert "root cause" in msg.lower()
        assert "task_complete" in msg

    def test_wrap_up_message_includes_pattern(self, detector: StallDetector) -> None:
        msg = detector.get_wrap_up_message("read_loop", "t1")
        assert "read_loop" in msg

    def test_grace_call_counter_increments(self, detector: StallDetector) -> None:
        detector.get_wrap_up_message("command_loop", "t1")
        for _ in range(3):
            detector.record_tool_call("t1", "run_command", "x", "y")
        state = detector.get_grace_state("t1")
        assert state["signaled"] is True
        assert state["calls_since_signal"] == 3

    def test_force_kill_after_grace_calls_exceeded(self, detector: StallDetector) -> None:
        detector.get_wrap_up_message("command_loop", "t1")
        for _ in range(5):
            detector.record_tool_call("t1", "run_command", "x", "y")
        state = detector.get_grace_state("t1")
        assert state["force_kill"] is True

    def test_force_kill_not_before_grace_limit(self, detector: StallDetector) -> None:
        detector.get_wrap_up_message("command_loop", "t1")
        for _ in range(4):  # one less than grace_calls_after_signal=5
            detector.record_tool_call("t1", "run_command", "x", "y")
        state = detector.get_grace_state("t1")
        assert state["force_kill"] is False


class TestHardTimeout:
    def test_hard_timeout_not_before_limit(self, detector: StallDetector) -> None:
        detector.start_task_timer("t1")
        assert not detector.is_hard_timeout("t1")

    def test_hard_timeout_after_limit(
        self, detector: StallDetector, config: StallConfig
    ) -> None:
        detector.start_task_timer("t1")
        # Simulate time passing beyond the hard timeout
        elapsed_seconds = config.hard_timeout_minutes * 60 + 1
        state = detector._tasks["t1"]
        state.start_time -= elapsed_seconds
        assert detector.is_hard_timeout("t1")

    def test_unknown_task_not_timed_out(self, detector: StallDetector) -> None:
        assert not detector.is_hard_timeout("ghost_task")

    def test_grace_timeout_after_hard_timeout(
        self, detector: StallDetector, config: StallConfig
    ) -> None:
        detector.start_task_timer("t1")
        detector.signal_hard_timeout("t1")
        # Grace period not yet expired
        assert not detector.is_grace_timeout("t1")
        # Advance grace clock beyond limit
        state = detector._tasks["t1"]
        state.grace_start_time -= config.grace_timeout_minutes * 60 + 1
        assert detector.is_grace_timeout("t1")
