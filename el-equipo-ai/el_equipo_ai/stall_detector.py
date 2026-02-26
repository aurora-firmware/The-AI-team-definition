"""Stall detector — pattern-based loop detection with graceful wrap-up injection."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import StallConfig


WRAP_UP_TEMPLATE = (
    "You have attempted the same approach multiple times without progress "
    "(pattern: {pattern}). Stop trying to fix this. "
    "Summarize: (1) what you tried, (2) what is failing and why, "
    "(3) your best guess at the root cause. "
    "Then call task_complete with status=failed and include your summary."
)


@dataclass
class _ToolCall:
    tool_name: str
    tool_input: str
    tool_output: str


@dataclass
class _TaskState:
    window: Deque[_ToolCall] = field(default_factory=deque)
    start_time: float = field(default_factory=time.monotonic)
    stall_signaled: bool = False
    calls_since_signal: int = 0
    grace_start_time: float | None = None


class StallDetector:
    """Monitors per-task tool call patterns and intervenes when agents loop.

    Two-layer protection:
    1. Pattern detector: identifies command_loop, read_loop, edit_revert_cycle.
       On detection injects a wrap-up message.
    2. Hard timeout: absolute wall-clock limit per task.
       Also triggers graceful wrap-up, then force-kill after grace period.
    """

    def __init__(self, config: StallConfig, logger: Logger) -> None:
        self._config = config
        self._logger = logger
        self._tasks: dict[str, _TaskState] = {}

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def start_task_timer(self, task_id: str) -> None:
        """Call when a task starts to initialise its timer."""
        state = self._get_or_create(task_id)
        state.start_time = time.monotonic()

    def record_tool_call(
        self,
        task_id: str,
        tool_name: str,
        tool_input: str,
        tool_output: str,
    ) -> None:
        """Record a tool call for pattern tracking."""
        state = self._get_or_create(task_id)
        max_window = self._config.repeat_threshold * 3
        state.window.append(_ToolCall(tool_name, tool_input, tool_output))
        if len(state.window) > max_window:
            state.window.popleft()

        if state.stall_signaled:
            state.calls_since_signal += 1

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def check_stall(self, task_id: str) -> str | None:
        """Analyse the tool call window. Returns stall pattern type or None."""
        state = self._tasks.get(task_id)
        if not state:
            return None

        threshold = self._config.repeat_threshold
        calls = list(state.window)

        if self._detect_command_loop(calls, threshold):
            return "command_loop"
        if self._detect_read_loop(calls, threshold):
            return "read_loop"
        if self._detect_edit_revert_cycle(calls, threshold):
            return "edit_revert_cycle"
        return None

    # ------------------------------------------------------------------
    # Intervention
    # ------------------------------------------------------------------

    def get_wrap_up_message(self, pattern: str, task_id: str) -> str:
        """Return the wrap-up prompt and mark the signal as sent."""
        state = self._get_or_create(task_id)
        state.stall_signaled = True
        state.calls_since_signal = 0
        self._logger.log(
            "stall_detected",
            task=task_id,
            pattern=pattern,
            action="wrap_up_signal",
        )
        return WRAP_UP_TEMPLATE.format(pattern=pattern)

    def is_hard_timeout(self, task_id: str) -> bool:
        """Return True if the task has exceeded hard_timeout_minutes."""
        state = self._tasks.get(task_id)
        if not state:
            return False
        elapsed_minutes = (time.monotonic() - state.start_time) / 60
        return elapsed_minutes >= self._config.hard_timeout_minutes

    def get_grace_state(self, task_id: str) -> dict:
        """Return grace state dict. Sets force_kill=True when grace limit exceeded."""
        state = self._tasks.get(task_id)
        if not state:
            return {"signaled": False, "calls_since_signal": 0, "force_kill": False}

        force_kill = (
            state.stall_signaled
            and state.calls_since_signal >= self._config.grace_calls_after_signal
        )
        if force_kill:
            self._logger.log("stall_force_kill", task=task_id)

        return {
            "signaled": state.stall_signaled,
            "calls_since_signal": state.calls_since_signal,
            "force_kill": force_kill,
        }

    def is_grace_timeout(self, task_id: str) -> bool:
        """Return True if the grace period has expired after the hard timeout signal."""
        state = self._tasks.get(task_id)
        if not state or not state.stall_signaled:
            return False
        if state.grace_start_time is None:
            # First call after signal — record grace period start
            state.grace_start_time = time.monotonic()
            return False
        elapsed_grace = (time.monotonic() - state.grace_start_time) / 60
        return elapsed_grace >= self._config.grace_timeout_minutes

    def signal_hard_timeout(self, task_id: str) -> str:
        """Signal the hard timeout and return the wrap-up message."""
        self._logger.log("hard_timeout", task=task_id)
        state = self._get_or_create(task_id)
        state.stall_signaled = True
        state.calls_since_signal = 0
        state.grace_start_time = time.monotonic()
        return WRAP_UP_TEMPLATE.format(pattern="hard_timeout")

    # ------------------------------------------------------------------
    # Pattern detectors (private)
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_command_loop(calls: list[_ToolCall], threshold: int) -> bool:
        """Same run_command with identical input AND output repeated >= threshold."""
        run_calls = [c for c in calls if c.tool_name == "run_command"]
        if len(run_calls) < threshold:
            return False
        recent = run_calls[-threshold:]
        first = recent[0]
        return all(
            c.tool_input == first.tool_input and c.tool_output == first.tool_output
            for c in recent[1:]
        )

    @staticmethod
    def _detect_read_loop(calls: list[_ToolCall], threshold: int) -> bool:
        """Same read_file path repeated >= threshold without any edit_file in between."""
        if len(calls) < threshold:
            return False
        # Find the last `threshold` read_file calls; check no edit in between
        read_calls: list[tuple[int, _ToolCall]] = [
            (i, c) for i, c in enumerate(calls) if c.tool_name == "read_file"
        ]
        if len(read_calls) < threshold:
            return False
        # Take the last `threshold` reads
        recent_reads = read_calls[-threshold:]
        first_idx, first_call = recent_reads[0]
        last_idx = recent_reads[-1][0]

        # Check they're all for the same path
        same_path = all(c.tool_input == first_call.tool_input for _, c in recent_reads)
        if not same_path:
            return False

        # Check no edit_file between first and last read
        between = calls[first_idx:last_idx + 1]
        return not any(c.tool_name == "edit_file" for c in between)

    @staticmethod
    def _detect_edit_revert_cycle(calls: list[_ToolCall], threshold: int) -> bool:
        """Alternating edit_file / run_command with same failing output >= threshold."""
        if len(calls) < threshold * 2:
            return False
        # Look for alternating edit/run pairs with identical run output
        pairs: list[str] = []
        i = 0
        while i < len(calls) - 1:
            if calls[i].tool_name == "edit_file" and calls[i + 1].tool_name == "run_command":
                pairs.append(calls[i + 1].tool_output)
                i += 2
            else:
                i += 1
        if len(pairs) < threshold:
            return False
        recent = pairs[-threshold:]
        return len(set(recent)) == 1  # all identical outputs

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_or_create(self, task_id: str) -> _TaskState:
        if task_id not in self._tasks:
            self._tasks[task_id] = _TaskState()
        return self._tasks[task_id]
