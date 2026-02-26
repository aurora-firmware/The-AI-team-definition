"""Tests for el_equipo_ai.manifest_bridge."""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from el_equipo_ai.logger import Logger
from el_equipo_ai.manifest_bridge import (
    VKClient,
    TaskSpec,
    bridge_plan_to_vk,
    parse_superpowers_plan,
)
from el_equipo_ai.models import LogConfig


SAMPLE_PLAN = textwrap.dedent("""\
    ## Task 1: Set up database models
    **Description:** Create SQLAlchemy models for User and Post entities.
    **Role:** executor
    **Verification:** pytest tests/test_models.py
    **Files to create:** models/user.py, models/post.py

    ## Task 2: Write API endpoints
    **Description:** Implement REST endpoints for user CRUD operations.
    **Role:** executor
    **Dependencies:** Task 1
    **Verification:** pytest tests/test_api.py
    **Files to modify:** api/routes.py
    **Files to create:** api/users.py

    ## Task 3: Write integration tests
    **Description:** Full integration test suite covering all endpoints.
    **Role:** tester
    **Dependencies:** Task 1, Task 2
    **Verification:** pytest tests/test_integration.py
    **Files to create:** tests/test_integration.py
""")


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def vk_client(logger: Logger) -> VKClient:
    return VKClient(vk_url="http://localhost:3000", logger=logger)


class TestParseSuperPowersPlan:
    def test_extracts_three_tasks(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert len(tasks) == 3

    def test_task_titles(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert tasks[0].title == "Set up database models"
        assert tasks[1].title == "Write API endpoints"
        assert tasks[2].title == "Write integration tests"

    def test_descriptions(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert "SQLAlchemy" in tasks[0].description
        assert "REST endpoints" in tasks[1].description

    def test_roles(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert tasks[0].role == "executor"
        assert tasks[2].role == "tester"

    def test_dependencies(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert tasks[0].dependencies == []
        assert tasks[1].dependencies == ["1"]
        assert tasks[2].dependencies == ["1", "2"]

    def test_verification_commands(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert tasks[0].verification_command == "pytest tests/test_models.py"

    def test_files_create(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert "models/user.py" in tasks[0].files_create
        assert "models/post.py" in tasks[0].files_create

    def test_files_modify(self) -> None:
        tasks = parse_superpowers_plan(SAMPLE_PLAN)
        assert "api/routes.py" in tasks[1].files_modify

    def test_empty_plan_returns_empty_list(self) -> None:
        assert parse_superpowers_plan("") == []
        assert parse_superpowers_plan("   ") == []

    def test_malformed_plan_raises(self) -> None:
        with pytest.raises(ValueError, match="task headers"):
            parse_superpowers_plan("No task headers here, just random text.")

    def test_level_three_headers(self) -> None:
        plan = "### Task 1: Do something\n**Description:** test\n**Role:** executor\n"
        tasks = parse_superpowers_plan(plan)
        assert len(tasks) == 1
        assert tasks[0].title == "Do something"


class TestVKClient:
    def test_create_task_sends_correct_payload(self, vk_client: VKClient) -> None:
        with patch("el_equipo_ai.manifest_bridge.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=201, json=lambda: {"id": "vk-001"})
            task_id = vk_client.create_task(
                title="Test task",
                description="Do something",
                role="executor",
                verification_command="pytest",
            )
        assert task_id == "vk-001"
        payload = mock_post.call_args.kwargs["json"]
        assert payload["title"] == "Test task"
        assert payload["role"] == "executor"
        assert payload["verification_command"] == "pytest"

    def test_create_task_returns_task_id(self, vk_client: VKClient) -> None:
        with patch("el_equipo_ai.manifest_bridge.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=201, json=lambda: {"id": "task-xyz"})
            result = vk_client.create_task("T", "D")
        assert result == "task-xyz"

    def test_get_task_status(self, vk_client: VKClient) -> None:
        with patch("el_equipo_ai.manifest_bridge.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200, json=lambda: {"id": "t1", "status": "done"}
            )
            status = vk_client.get_task_status("t1")
        assert status == "done"

    def test_network_error_raises(self, vk_client: VKClient) -> None:
        with patch("el_equipo_ai.manifest_bridge.requests.post") as mock_post:
            mock_post.side_effect = Exception("connection refused")
            with pytest.raises(Exception, match="connection refused"):
                vk_client.create_task("T", "D")


class TestBridgePlanToVK:
    def test_creates_all_tasks(self, vk_client: VKClient) -> None:
        task_counter = [0]

        def make_task(**kwargs):
            task_counter[0] += 1
            return f"vk-{task_counter[0]:03d}"

        with patch.object(vk_client, "create_task", side_effect=make_task):
            ids = bridge_plan_to_vk(SAMPLE_PLAN, vk_client)
        assert len(ids) == 3

    def test_dependencies_mapped_to_vk_ids(self, vk_client: VKClient) -> None:
        created_tasks: list[dict] = []

        def capture_task(**kwargs):
            tid = f"vk-{len(created_tasks) + 1:03d}"
            created_tasks.append(kwargs)
            return tid

        with patch.object(vk_client, "create_task", side_effect=capture_task):
            bridge_plan_to_vk(SAMPLE_PLAN, vk_client)

        # Task 2 depends on Task 1 → should reference "vk-001"
        task2_deps = created_tasks[1].get("dependencies") or []
        assert "vk-001" in task2_deps

        # Task 3 depends on Task 1 and Task 2 → should reference "vk-001" and "vk-002"
        task3_deps = created_tasks[2].get("dependencies") or []
        assert "vk-001" in task3_deps
        assert "vk-002" in task3_deps

    def test_empty_plan_returns_empty_list(self, vk_client: VKClient) -> None:
        with patch.object(vk_client, "create_task") as mock_create:
            result = bridge_plan_to_vk("", vk_client)
        assert result == []
        mock_create.assert_not_called()
