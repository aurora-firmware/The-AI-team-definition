"""Quota state persistence — saves/loads provider cooldown state to a JSON file."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import ProviderState, ProviderStatus


class QuotaManager:
    """Persists provider quota states and swap events to a JSON file.

    File format:
        {
            "provider_states": {
                "nvidia": {"status": "cooldown", "reset_at": "2024-01-01T12:00:00+00:00"},
                ...
            },
            "swap_log": [
                {"ts": "...", "from": "nvidia", "to": "openai",
                 "reason": "quota_exhausted", "reset_at": null},
                ...
            ]
        }
    """

    def __init__(self, state_file: str, logger: Logger) -> None:
        self._path = Path(state_file)
        self._logger = logger
        self._data: dict = self._load_raw()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> dict[str, ProviderState]:
        """Return provider states from the persisted file."""
        raw_states: dict = self._data.get("provider_states", {})
        result: dict[str, ProviderState] = {}
        for name, raw in raw_states.items():
            status = ProviderStatus(raw.get("status", "available"))
            reset_at_str = raw.get("reset_at")
            reset_at: datetime | None = None
            if reset_at_str:
                reset_at = datetime.fromisoformat(reset_at_str)
            result[name] = ProviderState(name=name, status=status, reset_at=reset_at)
        return result

    def save(self, states: dict[str, ProviderState]) -> None:
        """Persist the current provider states to the JSON file."""
        serialised: dict[str, dict] = {}
        for name, state in states.items():
            serialised[name] = {
                "status": state.status.value,
                "reset_at": state.reset_at.isoformat() if state.reset_at else None,
            }
        self._data["provider_states"] = serialised
        self._write_raw()

    def log_swap_event(
        self,
        from_provider: str,
        to_provider: str,
        reason: str,
        reset_at: datetime | None,
    ) -> None:
        """Append a provider-swap event to the swap log."""
        event = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "from": from_provider,
            "to": to_provider,
            "reason": reason,
            "reset_at": reset_at.isoformat() if reset_at else None,
        }
        if "swap_log" not in self._data:
            self._data["swap_log"] = []
        self._data["swap_log"].append(event)
        self._write_raw()
        self._logger.log(
            "provider_swap",
            from_provider=from_provider,
            to_provider=to_provider,
            reason=reason,
            reset_at=reset_at.isoformat() if reset_at else None,
        )

    def get_swap_log(self) -> list[dict]:
        return list(self._data.get("swap_log", []))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_raw(self) -> dict:
        if not self._path.exists():
            return {}
        with self._path.open(encoding="utf-8") as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                return {}

    def _write_raw(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)
