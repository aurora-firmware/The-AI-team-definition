"""Tests for el_equipo_ai.logger — JSONL logger with rotation."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import LogConfig


@pytest.fixture()
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "test.log"


@pytest.fixture()
def small_logger(log_path: Path) -> Logger:
    """Logger with 1 KB size limit so rotation is easy to trigger in tests."""
    cfg = LogConfig(file=str(log_path), max_size_mb=0.001, max_rotated_files=3)
    return Logger(cfg)


@pytest.fixture()
def logger(log_path: Path) -> Logger:
    cfg = LogConfig(file=str(log_path), max_size_mb=10, max_rotated_files=3)
    return Logger(cfg)


class TestBasicLogging:
    def test_writes_valid_jsonl(self, logger: Logger, log_path: Path) -> None:
        logger.log("test_event", key="value", num=42)
        lines = log_path.read_text().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["type"] == "test_event"
        assert record["key"] == "value"
        assert record["num"] == 42

    def test_timestamp_present(self, logger: Logger, log_path: Path) -> None:
        logger.log("ts_check")
        record = json.loads(log_path.read_text())
        assert "ts" in record
        assert "T" in record["ts"]  # ISO-8601 contains 'T'

    def test_multiple_events_produce_multiple_lines(
        self, logger: Logger, log_path: Path
    ) -> None:
        for i in range(5):
            logger.log("event", index=i)
        lines = log_path.read_text().splitlines()
        assert len(lines) == 5
        for i, line in enumerate(lines):
            assert json.loads(line)["index"] == i

    def test_log_file_created_in_nonexistent_dir(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "c" / "test.log"
        cfg = LogConfig(file=str(nested), max_size_mb=10, max_rotated_files=2)
        lg = Logger(cfg)
        lg.log("hello")
        assert nested.exists()


class TestRotation:
    def test_rotation_triggers_at_size_limit(
        self, small_logger: Logger, log_path: Path
    ) -> None:
        # Write enough data to exceed 1 KB limit
        for _ in range(100):
            small_logger.log("data", payload="x" * 20)
        rotated = Path(f"{log_path}.1")
        assert rotated.exists(), "Expected a rotated file to exist"

    def test_old_files_deleted_beyond_max(
        self, log_path: Path, tmp_path: Path
    ) -> None:
        # max_rotated_files = 2: only .1 and .2 should remain
        cfg = LogConfig(file=str(log_path), max_size_mb=0.001, max_rotated_files=2)
        lg = Logger(cfg)
        # Write enough to trigger 3 rotations
        for _ in range(300):
            lg.log("data", payload="x" * 20)
        assert not Path(f"{log_path}.3").exists(), ".3 should have been deleted"

    def test_content_preserved_after_rotation(
        self, small_logger: Logger, log_path: Path
    ) -> None:
        first_event = "first_event_sentinel"
        small_logger.log(first_event)
        # Flood to trigger rotation
        for _ in range(100):
            small_logger.log("filler", payload="x" * 20)
        rotated = Path(f"{log_path}.1")
        # The first event must be in one of the rotated files
        all_content = ""
        for suffix in ("", ".1", ".2", ".3"):
            p = Path(f"{log_path}{suffix}")
            if p.exists():
                all_content += p.read_text()
        assert first_event in all_content


class TestThreadSafety:
    def test_concurrent_writes_no_corruption(
        self, logger: Logger, log_path: Path
    ) -> None:
        num_threads = 10
        writes_per_thread = 50
        errors: list[Exception] = []

        def write_events(thread_id: int) -> None:
            try:
                for i in range(writes_per_thread):
                    logger.log("concurrent", thread=thread_id, seq=i)
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [
            threading.Thread(target=write_events, args=(t,))
            for t in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        lines = log_path.read_text().splitlines()
        assert len(lines) == num_threads * writes_per_thread
        for line in lines:
            json.loads(line)  # each line must be valid JSON
