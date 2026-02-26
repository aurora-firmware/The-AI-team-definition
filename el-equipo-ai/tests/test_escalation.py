"""Tests for el_equipo_ai.escalation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from el_equipo_ai.escalation import consult_architect, handle_task_failure
from el_equipo_ai.logger import Logger
from el_equipo_ai.manifest_bridge import VKClient
from el_equipo_ai.models import (
    ArchitectVerdict,
    AppConfig,
    LogConfig,
    TaskFailureReport,
)
from el_equipo_ai.notifier import Notifier
from el_equipo_ai.provider_router import ProviderRouter


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def failure_report() -> TaskFailureReport:
    return TaskFailureReport(
        task_id="task-42",
        attempts=1,
        what_tried="Ran pytest three times with same fix",
        what_failed="AssertionError on line 17",
        agent_analysis="Suspect circular import in models.py",
    )


@pytest.fixture()
def mock_router(minimal_app_config: AppConfig, logger: Logger) -> ProviderRouter:
    return ProviderRouter(config=minimal_app_config, logger=logger)


@pytest.fixture()
def mock_vk_client(logger: Logger) -> VKClient:
    return VKClient(vk_url="http://localhost:3000", logger=logger)


@pytest.fixture()
def notifier(logger: Logger) -> Notifier:
    return Notifier(channels=[], logger=logger)


def _make_api_response(verdict: str, instructions: str | None, analysis: str) -> MagicMock:
    content = json.dumps({
        "verdict": verdict,
        "revised_instructions": instructions,
        "analysis": analysis,
    })
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


class TestConsultArchitect:
    def test_simple_fix_verdict_parsed(
        self, mock_router, failure_report, logger
    ) -> None:
        response = _make_api_response(
            "simple_fix", "Try removing the circular import", "Import cycle detected"
        )
        with patch.object(mock_router, "call", return_value=response):
            verdict = consult_architect(failure_report, mock_router, logger)
        assert verdict.verdict == "simple_fix"
        assert verdict.revised_instructions == "Try removing the circular import"
        assert "Import cycle" in verdict.analysis

    def test_scope_problem_verdict_parsed(
        self, mock_router, failure_report, logger
    ) -> None:
        response = _make_api_response("scope_problem", None, "Task too broad")
        with patch.object(mock_router, "call", return_value=response):
            verdict = consult_architect(failure_report, mock_router, logger)
        assert verdict.verdict == "scope_problem"
        assert verdict.revised_instructions is None

    def test_api_failure_defaults_to_scope_problem(
        self, mock_router, failure_report, logger
    ) -> None:
        with patch.object(mock_router, "call", side_effect=Exception("timeout")):
            verdict = consult_architect(failure_report, mock_router, logger)
        assert verdict.verdict == "scope_problem"
        assert "timeout" in verdict.analysis

    def test_malformed_json_defaults_to_scope_problem(
        self, mock_router, failure_report, logger
    ) -> None:
        bad_response = MagicMock()
        bad_response.choices[0].message.content = "not valid json at all"
        with patch.object(mock_router, "call", return_value=bad_response):
            verdict = consult_architect(failure_report, mock_router, logger)
        assert verdict.verdict == "scope_problem"

    def test_unknown_verdict_defaults_to_scope_problem(
        self, mock_router, failure_report, logger
    ) -> None:
        response = _make_api_response("maybe_fix", None, "Unsure")
        with patch.object(mock_router, "call", return_value=response):
            verdict = consult_architect(failure_report, mock_router, logger)
        assert verdict.verdict == "scope_problem"

    def test_logs_architect_consult_event(
        self, mock_router, failure_report, tmp_path
    ) -> None:
        log_path = tmp_path / "arch.log"
        lg = Logger(LogConfig(file=str(log_path), max_size_mb=10, max_rotated_files=2))
        response = _make_api_response("simple_fix", "instructions", "ok")
        with patch.object(mock_router, "call", return_value=response):
            consult_architect(failure_report, mock_router, lg)
        lines = log_path.read_text().splitlines()
        types = [json.loads(l)["type"] for l in lines]
        assert "architect_consult" in types


class TestHandleTaskFailure:
    def test_first_failure_simple_fix_creates_vk_task(
        self,
        mock_router,
        mock_vk_client,
        notifier,
        failure_report,
        logger,
    ) -> None:
        arch_response = _make_api_response(
            "simple_fix", "Remove the circular import in models.py", "Import issue"
        )
        with patch.object(mock_router, "call", return_value=arch_response):
            with patch.object(mock_vk_client, "create_task", return_value="vk-retry-1"):
                result = handle_task_failure(
                    failure_report, mock_router, mock_vk_client, notifier, logger
                )
        assert result.action == "retried"
        assert result.new_task_id == "vk-retry-1"

    def test_first_failure_scope_problem_notifies_human(
        self,
        mock_router,
        mock_vk_client,
        notifier,
        failure_report,
        logger,
        capsys,
    ) -> None:
        arch_response = _make_api_response("scope_problem", None, "Too complex")
        with patch.object(mock_router, "call", return_value=arch_response):
            result = handle_task_failure(
                failure_report, mock_router, mock_vk_client, notifier, logger
            )
        assert result.action == "escalated_to_human"
        captured = capsys.readouterr()
        assert "ACTION REQUIRED" in captured.out
        assert "task-42" in captured.out

    def test_second_failure_skips_architect(
        self,
        mock_router,
        mock_vk_client,
        notifier,
        logger,
        capsys,
    ) -> None:
        second_attempt = TaskFailureReport(
            task_id="task-42",
            attempts=2,
            what_tried="Tried again",
            what_failed="Still failing",
            agent_analysis="No idea",
        )
        with patch.object(mock_router, "call") as mock_call:
            result = handle_task_failure(
                second_attempt, mock_router, mock_vk_client, notifier, logger
            )
        # Architect should NOT be called
        mock_call.assert_not_called()
        assert result.action == "escalated_to_human"

    def test_notifier_called_with_task_context(
        self,
        mock_router,
        mock_vk_client,
        notifier,
        failure_report,
        logger,
        capsys,
    ) -> None:
        arch_response = _make_api_response("scope_problem", None, "Design flaw")
        with patch.object(mock_router, "call", return_value=arch_response):
            handle_task_failure(
                failure_report, mock_router, mock_vk_client, notifier, logger
            )
        captured = capsys.readouterr()
        assert "Ran pytest three times" in captured.out
        assert "AssertionError" in captured.out
