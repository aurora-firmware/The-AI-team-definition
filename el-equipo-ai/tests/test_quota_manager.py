"""Tests for el_equipo_ai.quota_manager."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import LogConfig, ProviderState, ProviderStatus
from el_equipo_ai.quota_manager import QuotaManager


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def state_file(tmp_path: Path) -> str:
    return str(tmp_path / "state.json")


@pytest.fixture()
def qm(state_file: str, logger: Logger) -> QuotaManager:
    return QuotaManager(state_file=state_file, logger=logger)


class TestSaveLoad:
    def test_missing_file_returns_empty(self, state_file: str, logger: Logger) -> None:
        qm = QuotaManager(state_file=state_file, logger=logger)
        assert qm.load() == {}

    def test_save_and_load_roundtrip(self, qm: QuotaManager) -> None:
        reset_time = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        states = {
            "nvidia": ProviderState("nvidia", ProviderStatus.COOLDOWN, reset_time),
            "openai": ProviderState("openai", ProviderStatus.AVAILABLE, None),
        }
        qm.save(states)
        loaded = qm.load()

        assert loaded["nvidia"].status == ProviderStatus.COOLDOWN
        assert loaded["nvidia"].reset_at == reset_time
        assert loaded["openai"].status == ProviderStatus.AVAILABLE
        assert loaded["openai"].reset_at is None

    def test_exhausted_status_roundtrip(self, qm: QuotaManager) -> None:
        states = {"provider_x": ProviderState("provider_x", ProviderStatus.EXHAUSTED, None)}
        qm.save(states)
        loaded = qm.load()
        assert loaded["provider_x"].status == ProviderStatus.EXHAUSTED

    def test_iso8601_datetime_roundtrip(self, qm: QuotaManager) -> None:
        # Microseconds should survive the round-trip
        now = datetime.now(timezone.utc).replace(microsecond=0)
        states = {"p": ProviderState("p", ProviderStatus.COOLDOWN, now)}
        qm.save(states)
        loaded = qm.load()
        assert loaded["p"].reset_at == now

    def test_reload_from_disk(self, state_file: str, logger: Logger) -> None:
        """A new QuotaManager instance should read from the same file."""
        qm1 = QuotaManager(state_file=state_file, logger=logger)
        states = {"p": ProviderState("p", ProviderStatus.EXHAUSTED, None)}
        qm1.save(states)

        qm2 = QuotaManager(state_file=state_file, logger=logger)
        loaded = qm2.load()
        assert loaded["p"].status == ProviderStatus.EXHAUSTED


class TestSwapLog:
    def test_swap_events_accumulate(self, qm: QuotaManager) -> None:
        reset = datetime(2025, 1, 1, tzinfo=timezone.utc)
        qm.log_swap_event("nvidia", "openai", "quota_exhausted", reset)
        qm.log_swap_event("openai", "local", "quota_exhausted", None)
        log = qm.get_swap_log()
        assert len(log) == 2
        assert log[0]["from"] == "nvidia"
        assert log[0]["to"] == "openai"
        assert log[1]["from"] == "openai"
        assert log[1]["to"] == "local"

    def test_swap_event_persisted(
        self, state_file: str, logger: Logger
    ) -> None:
        qm1 = QuotaManager(state_file=state_file, logger=logger)
        qm1.log_swap_event("a", "b", "test", None)

        qm2 = QuotaManager(state_file=state_file, logger=logger)
        assert len(qm2.get_swap_log()) == 1

    def test_swap_event_reset_at_none(self, qm: QuotaManager) -> None:
        qm.log_swap_event("a", "b", "exhausted", None)
        log = qm.get_swap_log()
        assert log[0]["reset_at"] is None
