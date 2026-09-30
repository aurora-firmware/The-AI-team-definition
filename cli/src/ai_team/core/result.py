"""Structured command result shared by pure handlers and their Typer wrappers.

This module has no Typer dependency. Handlers return a ``Result``; wrappers
decide how to print it so CLI text stays identical to the pre-result output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Result:
    """Outcome of a command handler.

    ``status`` is the process exit status (0 on success). ``payload`` holds the
    machine-readable data (what ``--json`` prints) on success. ``message`` and
    ``hint`` are kept apart on failure so non-CLI callers can use them
    separately; ``text()`` joins them the way the CLI always has.
    """

    status: int
    payload: dict[str, Any] | None = None
    message: str | None = None
    hint: str | None = None

    def text(self) -> str:
        """Return the CLI error text: the message followed by the hint, if any."""
        parts = [part for part in (self.message, self.hint) if part]
        return " ".join(parts)
