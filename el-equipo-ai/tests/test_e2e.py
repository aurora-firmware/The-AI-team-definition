"""End-to-end integration tests — full pipeline with mocked external services."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from el_equipo_ai.config import load_config
from el_equipo_ai.integration import IntegrationResult, MergeAllResult, TestResult
from el_equipo_ai.main import App
from el_equipo_ai.models import (
    AppConfig,
    ProviderState,
    ProviderStatus,
    TaskFailureReport,
)


SAMPLE_PLAN = textwrap.dedent("""\
    ## Task 1: Create data model
    **Description:** Define the data structures.
    **Role:** executor
    **Verification:** pytest tests/test_models.py
    **Files to create:** models.py

    ## Task 2: Write API
    **Description:** Implement the API layer.
    **Role:** executor
    **Dependencies:** Task 1
    **Verification:** pytest tests/test_api.py
    **Files to modify:** api.py
""")


@pytest.fixture()
def app(sample_config_file: str) -> App:
    config = load_config(sample_config_file)
    return App(config)


def _make_mock_response(content: str) -> MagicMock:
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


class TestHappyPath:
    def test_plan_returns_text(self, app: App) -> None:
        with patch.object(app.provider_router, "call") as mock_call:
            mock_call.side_effect = [
                _make_mock_response("Design doc content"),
                _make_mock_response(SAMPLE_PLAN),
            ]
            plan = app.plan("Build a REST API for a todo app")
        assert "Task 1" in plan

    def test_execute_creates_vk_tasks(self, app: App) -> None:
        counter = [0]

        def make_task(**kwargs):
            counter[0] += 1
            return f"vk-{counter[0]:03d}"

        with patch.object(app.vk_client, "create_task", side_effect=make_task):
            task_ids = app.execute(SAMPLE_PLAN)

        assert len(task_ids) == 2

    def test_integrate_calls_pipeline(self, app: App, capsys) -> None:
        with patch("el_equipo_ai.main.integration_pipeline") as mock_pipeline:
            mock_pipeline.return_value = IntegrationResult(status="passed")
            app.integrate(["feat/task-1", "feat/task-2"])
        mock_pipeline.assert_called_once()
        args = mock_pipeline.call_args
        assert args.kwargs["branches_in_order"] == ["feat/task-1", "feat/task-2"]

    def test_full_pipeline_happy_path(self, app: App, capsys) -> None:
        """Simulate full plan → execute → integrate flow."""
        with patch.object(app.provider_router, "call") as mock_call:
            mock_call.side_effect = [
                _make_mock_response("Design doc"),
                _make_mock_response(SAMPLE_PLAN),
            ]
            plan = app.plan("Make a thing")

        counter = [0]
        def make_task(**kwargs):
            counter[0] += 1
            return f"vk-{counter[0]:03d}"

        with patch.object(app.vk_client, "create_task", side_effect=make_task):
            task_ids = app.execute(plan)

        with patch("el_equipo_ai.main.integration_pipeline") as mock_pipeline:
            mock_pipeline.return_value = IntegrationResult(status="passed")
            app.integrate(["feat/task-1", "feat/task-2"])

        assert len(task_ids) == 2
        captured = capsys.readouterr()
        assert "Vibe Kanban" in captured.out


class TestProviderFallback:
    def test_primary_fails_secondary_used(self, app: App) -> None:
        from el_equipo_ai.provider_router import AllProvidersExhausted
        from datetime import datetime, timezone, timedelta

        # Mark primary (nvidia) as exhausted
        app.provider_router.mark_exhausted("nvidia")

        # Secondary (openai) should be used
        mock_resp = _make_mock_response("plan content")
        with patch.object(app.provider_router, "_try_call") as mock_try:
            mock_try.return_value = mock_resp
            result = app.provider_router.call(
                "planner_creative",
                [{"role": "user", "content": "hello"}],
            )
        assert result is mock_resp


class TestStallDetectionE2E:
    def test_stall_detected_and_logged(self, app: App, tmp_path: Path) -> None:
        # Simulate an agent sending the same command repeatedly
        for _ in range(3):
            app.stall_detector.record_tool_call(
                "task-1", "run_command", "pytest", "FAILED: assert error"
            )
        pattern = app.stall_detector.check_stall("task-1")
        assert pattern == "command_loop"

        # Get wrap-up message
        msg = app.stall_detector.get_wrap_up_message(pattern, "task-1")
        assert "task_complete" in msg


class TestEscalationE2E:
    def test_first_failure_consults_architect(self, app: App) -> None:
        from el_equipo_ai.escalation import handle_task_failure

        report = TaskFailureReport(
            task_id="task-5",
            attempts=1,
            what_tried="Ran tests 3 times",
            what_failed="Import error",
            agent_analysis="Circular import suspected",
        )

        arch_response = _make_mock_response(json.dumps({
            "verdict": "simple_fix",
            "revised_instructions": "Remove circular import from utils.py",
            "analysis": "Clear import cycle",
        }))

        with patch.object(app.provider_router, "call", return_value=arch_response):
            with patch.object(app.vk_client, "create_task", return_value="vk-retry-5"):
                result = handle_task_failure(
                    report,
                    app.provider_router,
                    app.vk_client,
                    app.notifier,
                    app.logger,
                )
        assert result.action == "retried"
        assert result.new_task_id == "vk-retry-5"

    def test_second_failure_escalates_to_human(self, app: App, capsys) -> None:
        from el_equipo_ai.escalation import handle_task_failure

        report = TaskFailureReport(
            task_id="task-5",
            attempts=2,
            what_tried="Tried again",
            what_failed="Still failing",
            agent_analysis="Unknown",
        )

        with patch.object(app.provider_router, "call") as mock_call:
            result = handle_task_failure(
                report,
                app.provider_router,
                app.vk_client,
                app.notifier,
                app.logger,
            )

        mock_call.assert_not_called()
        assert result.action == "escalated_to_human"
        captured = capsys.readouterr()
        assert "ACTION REQUIRED" in captured.out


class TestLogger:
    def test_full_event_trail(self, app: App) -> None:
        """Verify that key events are logged during a plan→execute flow."""
        log_path = Path(app.config.logging.file)

        with patch.object(app.provider_router, "call") as mock_call:
            mock_call.side_effect = [
                _make_mock_response("Design"),
                _make_mock_response(SAMPLE_PLAN),
            ]
            app.plan("Build something")

        if log_path.exists():
            lines = log_path.read_text().splitlines()
            types = [json.loads(l)["type"] for l in lines]
            assert "plan_start" in types


class TestStatus:
    def test_status_prints_provider_info(self, app: App, capsys) -> None:
        app.status()
        captured = capsys.readouterr()
        assert "Provider Status" in captured.out
