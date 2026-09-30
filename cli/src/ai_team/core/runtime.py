"""Runtime facts (today's date, framework version) with test-only overrides."""

from __future__ import annotations

import importlib.metadata
import os
from datetime import date

TODAY_ENV_VAR = "AI_TEAM_TODAY"
FRAMEWORK_VERSION_ENV_VAR = "AI_TEAM_FRAMEWORK_VERSION"


def today() -> date:
    """Return today's date, or the ISO date in AI_TEAM_TODAY when set."""
    override = os.environ.get(TODAY_ENV_VAR)
    if override is None:
        return date.today()
    try:
        return date.fromisoformat(override)
    except ValueError as exc:
        raise ValueError(
            f"{TODAY_ENV_VAR} must be an ISO date (YYYY-MM-DD), got {override!r}"
        ) from exc


def framework_version() -> str:
    """Return the installed framework version, or AI_TEAM_FRAMEWORK_VERSION if set."""
    override = os.environ.get(FRAMEWORK_VERSION_ENV_VAR)
    if override is not None:
        return override
    # Looked up at call time so monkeypatching importlib.metadata.version works.
    return importlib.metadata.version("ai-team")
