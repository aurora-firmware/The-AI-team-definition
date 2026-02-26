"""JSONL logger with size-based rotation and thread safety."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from el_equipo_ai.models import LogConfig


class Logger:
    """Append-only JSONL logger with automatic rotation.

    Each call to log() writes one line:
        {"ts": "<ISO-8601>", "type": "<event_type>", ...extra_fields}

    Rotation fires before a write when the current file reaches max_size_mb.
    Rotated files are named <file>.1, <file>.2, ... up to max_rotated_files.
    Files beyond the limit are deleted.

    Thread-safe: a single lock serialises all writes including rotations.
    """

    def __init__(self, config: LogConfig) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._path = Path(config.file)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(self, event_type: str, **data: object) -> None:
        """Write one JSONL event line."""
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        record = {"ts": ts, "type": event_type, **data}
        line = json.dumps(record, default=str) + "\n"

        with self._lock:
            self._rotate_if_needed()
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line)

    # ------------------------------------------------------------------
    # Rotation helpers
    # ------------------------------------------------------------------

    def _rotate_if_needed(self) -> None:
        """Called with the lock held. Rotate if current file exceeds the size limit."""
        if not self._path.exists():
            return
        size_mb = self._path.stat().st_size / (1024 * 1024)
        if size_mb >= self._config.max_size_mb:
            self._rotate()

    def _rotate(self) -> None:
        """Shift existing rotated files up by one, delete the oldest if over limit."""
        max_n = self._config.max_rotated_files

        # Delete the oldest file if we're at the limit
        oldest = Path(f"{self._path}.{max_n}")
        if oldest.exists():
            oldest.unlink()

        # Shift .N-1 → .N, ..., .1 → .2
        for i in range(max_n - 1, 0, -1):
            src = Path(f"{self._path}.{i}")
            dst = Path(f"{self._path}.{i + 1}")
            if src.exists():
                src.rename(dst)

        # Rename current log to .1
        if self._path.exists():
            self._path.rename(Path(f"{self._path}.1"))
