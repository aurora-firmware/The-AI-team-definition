"""Shared dataclasses used across all El-equipo-AI modules."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime


# ---------------------------------------------------------------------------
# Provider / Model configuration
# ---------------------------------------------------------------------------


@dataclass
class ProviderConfig:
    """A model provider (NVIDIA NIM, OpenAI, Anthropic, Ollama, ...)."""
    name: str
    base_url: str
    api_key_env: str | None
    api_key: str | None = None  # resolved from env at load time


@dataclass
class ModelOption:
    """A concrete (provider, model) pair inside a role's fallback list."""
    provider: str
    model: str


@dataclass
class RoleConfig:
    """A logical role (planner_creative, executor, tester, ...) with its model priority list."""
    name: str
    temperature: float
    models: list[ModelOption]
    json_mode: bool = False


# ---------------------------------------------------------------------------
# Stall detection configuration
# ---------------------------------------------------------------------------


@dataclass
class StallConfig:
    repeat_threshold: int = 3
    grace_calls_after_signal: int = 5
    hard_timeout_minutes: int = 30
    grace_timeout_minutes: int = 2


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------


@dataclass
class NotificationChannel:
    type: str            # "webhook"
    name: str
    url_env: str | None
    url: str | None = None  # resolved from env at load time


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


@dataclass
class LogConfig:
    file: str = "el-equipo-ai.log"
    max_size_mb: int = 10
    max_rotated_files: int = 3


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


@dataclass
class ProjectConfig:
    test_command: str = "pytest"
    setup_script: str | None = None


# ---------------------------------------------------------------------------
# Top-level app config
# ---------------------------------------------------------------------------


@dataclass
class AppConfig:
    providers: list[ProviderConfig] = field(default_factory=list)
    roles: dict[str, RoleConfig] = field(default_factory=dict)
    stall_detection: StallConfig = field(default_factory=StallConfig)
    notifications: list[NotificationChannel] = field(default_factory=list)
    logging: LogConfig = field(default_factory=LogConfig)
    project: ProjectConfig = field(default_factory=ProjectConfig)
    vk_url: str = "http://localhost:3000"
    state_file: str = ".el-equipo-ai-state.json"


# ---------------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------------


class ProviderStatus(enum.Enum):
    AVAILABLE = "available"
    COOLDOWN = "cooldown"
    EXHAUSTED = "exhausted"


@dataclass
class ProviderState:
    name: str
    status: ProviderStatus = ProviderStatus.AVAILABLE
    reset_at: datetime | None = None


# ---------------------------------------------------------------------------
# Events / reports
# ---------------------------------------------------------------------------


@dataclass
class LogEvent:
    ts: str
    type: str
    data: dict = field(default_factory=dict)


@dataclass
class TaskFailureReport:
    task_id: str
    attempts: int
    what_tried: str
    what_failed: str
    agent_analysis: str


@dataclass
class ArchitectVerdict:
    verdict: str                          # "simple_fix" | "scope_problem"
    revised_instructions: str | None
    analysis: str


@dataclass
class EscalationResult:
    action: str                           # "retried" | "escalated_to_human"
    new_task_id: str | None = None
    analysis: str = ""
