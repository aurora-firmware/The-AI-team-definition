"""Task Manifest Bridge — Superpowers plan → Vibe Kanban tasks via MCP."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import requests

from el_equipo_ai.logger import Logger


# ---------------------------------------------------------------------------
# TaskSpec — internal representation before sending to VK
# ---------------------------------------------------------------------------


@dataclass
class TaskSpec:
    title: str
    description: str
    role: str = "executor"
    dependencies: list[str] = field(default_factory=list)
    verification_command: str | None = None
    files_modify: list[str] = field(default_factory=list)
    files_create: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# VK MCP Client
# ---------------------------------------------------------------------------


class VKClient:
    """Thin HTTP client for the Vibe Kanban MCP server.

    VK exposes a REST/JSON-RPC style API at its base URL.
    We use the tasks endpoint directly rather than the full MCP protocol
    because VK's task API is stable and simpler to target.

    NOTE: The VK MCP API surface is still evolving. This client targets
    the task-creation and status-query paths used by El-equipo-AI.
    If the API changes, only this file needs updating.
    """

    def __init__(self, vk_url: str, logger: Logger) -> None:
        self._base = vk_url.rstrip("/")
        self._logger = logger

    def create_task(
        self,
        title: str,
        description: str,
        dependencies: list[str] | None = None,
        role: str = "executor",
        verification_command: str | None = None,
    ) -> str:
        """Create a task in VK. Returns the new task ID."""
        payload = {
            "title": title,
            "description": description,
            "role": role,
        }
        if dependencies:
            payload["dependencies"] = dependencies
        if verification_command:
            payload["verification_command"] = verification_command

        resp = requests.post(
            f"{self._base}/api/tasks",
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        task_id: str = resp.json()["id"]
        self._logger.log(
            "vk_task_created",
            task_id=task_id,
            title=title,
            role=role,
        )
        return task_id

    def get_task_status(self, task_id: str) -> str:
        """Return task status: "todo" | "in_progress" | "done" | "failed"."""
        resp = requests.get(
            f"{self._base}/api/tasks/{task_id}",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["status"]

    def list_tasks(self, project_id: str) -> list[dict]:
        """List all tasks for a project."""
        resp = requests.get(
            f"{self._base}/api/projects/{project_id}/tasks",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Plan parser
# ---------------------------------------------------------------------------


# Expected Superpowers plan format (from writing-plans skill):
#
# ## Task N: Title
# **Description:** ...
# **Role:** executor
# **Dependencies:** Task 1, Task 2
# **Verification:** command here
# **Files to modify:** path/a, path/b
# **Files to create:** path/c
#
# We accept both "## Task N:" and "### Task N:" headers.

_TASK_HEADER_RE = re.compile(
    r"^#{1,4}\s+Task\s+(\d+)\s*[:\-–]\s*(.+)$",
    re.MULTILINE | re.IGNORECASE,
)
_FIELD_RE = re.compile(
    r"^\*{0,2}(description|role|dependencies|verification|files to modify|files to create)\*{0,2}\s*:?\s*(.+)$",
    re.IGNORECASE,
)


def parse_superpowers_plan(plan_text: str) -> list[TaskSpec]:
    """Parse Superpowers' plan markdown into a list of TaskSpec objects.

    Raises ValueError if the plan is structurally invalid.
    """
    plan_text = plan_text.strip()
    if not plan_text:
        return []

    # Split on task headers
    headers = list(_TASK_HEADER_RE.finditer(plan_text))
    if not headers:
        raise ValueError(
            "Could not find any task headers in the plan. "
            "Expected format: '## Task N: Title'"
        )

    tasks: list[TaskSpec] = []
    for i, match in enumerate(headers):
        task_num = match.group(1)
        title = match.group(2).strip()
        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(plan_text)
        body = plan_text[start:end]

        spec = TaskSpec(title=title)
        for line in body.splitlines():
            line = line.strip().lstrip("-* ")
            field_match = _FIELD_RE.match(line)
            if not field_match:
                continue
            field_name = field_match.group(1).lower()
            value = field_match.group(2).strip()

            if field_name == "description":
                spec.description = value
            elif field_name == "role":
                spec.role = value.lower()
            elif field_name == "dependencies":
                # "Task 1, Task 2" → ["1", "2"] (local task numbers)
                spec.dependencies = [
                    dep.strip().replace("Task ", "").replace("task ", "")
                    for dep in value.split(",")
                    if dep.strip()
                ]
            elif field_name == "verification":
                spec.verification_command = value
            elif field_name == "files to modify":
                spec.files_modify = [f.strip() for f in value.split(",") if f.strip()]
            elif field_name == "files to create":
                spec.files_create = [f.strip() for f in value.split(",") if f.strip()]

        tasks.append(spec)

    return tasks


def bridge_plan_to_vk(plan_text: str, vk_client: VKClient) -> list[str]:
    """Parse a Superpowers plan and create all tasks in Vibe Kanban.

    Preserves dependency relationships by mapping local task numbers to
    real VK task IDs.

    Returns the list of created VK task IDs in order.
    """
    specs = parse_superpowers_plan(plan_text)
    if not specs:
        return []

    # local_num (1-based) → vk_task_id
    id_map: dict[str, str] = {}
    vk_ids: list[str] = []

    for i, spec in enumerate(specs, start=1):
        local_num = str(i)
        resolved_deps = [id_map[d] for d in spec.dependencies if d in id_map]

        description = spec.description or spec.title
        if spec.files_modify or spec.files_create:
            extras: list[str] = []
            if spec.files_modify:
                extras.append(f"Modify: {', '.join(spec.files_modify)}")
            if spec.files_create:
                extras.append(f"Create: {', '.join(spec.files_create)}")
            description += "\n\n" + "\n".join(extras)

        vk_id = vk_client.create_task(
            title=spec.title,
            description=description,
            dependencies=resolved_deps or None,
            role=spec.role,
            verification_command=spec.verification_command,
        )
        id_map[local_num] = vk_id
        vk_ids.append(vk_id)

    return vk_ids
