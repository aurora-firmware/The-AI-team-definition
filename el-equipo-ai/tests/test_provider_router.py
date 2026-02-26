"""Tests for el_equipo_ai.provider_router."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import AppConfig, LogConfig, ProviderState, ProviderStatus
from el_equipo_ai.provider_router import AllProvidersExhausted, ProviderRouter


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def router(minimal_app_config: AppConfig, logger: Logger) -> ProviderRouter:
    return ProviderRouter(config=minimal_app_config, logger=logger)


class TestProviderSelection:
    def test_returns_first_provider_when_all_available(self, router: ProviderRouter) -> None:
        result = router.get_provider_for_role("executor")
        assert result is not None
        provider, role, model = result
        assert provider.name == "primary"
        assert model == "model-a"

    def test_skips_cooldown_provider(self, router: ProviderRouter) -> None:
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        router.mark_cooldown("primary", future)
        result = router.get_provider_for_role("executor")
        assert result is not None
        provider, _, _ = result
        assert provider.name == "secondary"

    def test_returns_none_when_all_exhausted(self, router: ProviderRouter) -> None:
        router.mark_exhausted("primary")
        router.mark_exhausted("secondary")
        result = router.get_provider_for_role("executor")
        assert result is None

    def test_cooldown_expires_provider_becomes_available(
        self, router: ProviderRouter
    ) -> None:
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        router.mark_cooldown("primary", past)
        router.check_cooldowns()
        result = router.get_provider_for_role("executor")
        assert result is not None
        provider, _, _ = result
        assert provider.name == "primary"

    def test_unknown_role_raises(self, router: ProviderRouter) -> None:
        with pytest.raises(ValueError, match="Unknown role"):
            router.get_provider_for_role("nonexistent_role")


class TestApiCallWrapper:
    def _make_mock_response(self) -> MagicMock:
        resp = MagicMock()
        resp.choices = [MagicMock()]
        return resp

    def test_successful_call_returns_response(
        self, router: ProviderRouter
    ) -> None:
        mock_resp = self._make_mock_response()
        with patch("el_equipo_ai.provider_router.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.return_value = mock_resp
            result = router.call("executor", [{"role": "user", "content": "hello"}])
        assert result is mock_resp

    def test_successful_call_logs_event(
        self, router: ProviderRouter, tmp_path: Path
    ) -> None:
        import json
        log_path = tmp_path / "log.jsonl"
        lg = Logger(LogConfig(file=str(log_path), max_size_mb=10, max_rotated_files=2))
        from el_equipo_ai.provider_router import ProviderRouter as PR
        r = PR(config=router._config, logger=lg)
        with patch("el_equipo_ai.provider_router.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.return_value = self._make_mock_response()
            r.call("executor", [{"role": "user", "content": "x"}])
        lines = log_path.read_text().splitlines()
        types = [json.loads(l)["type"] for l in lines]
        assert "provider_call" in types

    def test_429_with_retry_after_waits_and_retries(
        self, router: ProviderRouter
    ) -> None:
        mock_resp = self._make_mock_response()
        rate_limit_exc = Exception("rate limit")
        rate_limit_exc.status_code = 429
        mock_response_obj = MagicMock()
        mock_response_obj.headers = {"retry-after": "1"}
        rate_limit_exc.response = mock_response_obj

        with patch("el_equipo_ai.provider_router.OpenAI") as MockOpenAI:
            mock_create = MockOpenAI.return_value.chat.completions.create
            mock_create.side_effect = [rate_limit_exc, mock_resp]
            with patch("el_equipo_ai.provider_router.time.sleep") as mock_sleep:
                result = router.call("executor", [{"role": "user", "content": "x"}])
        mock_sleep.assert_called_once_with(1)
        assert result is mock_resp

    def test_quota_error_falls_back_to_next_provider(
        self, router: ProviderRouter
    ) -> None:
        mock_resp = self._make_mock_response()
        quota_exc = Exception("insufficient_quota: credits exhausted")
        quota_exc.status_code = 429

        with patch("el_equipo_ai.provider_router.OpenAI") as MockOpenAI:
            # First call raises quota error, second call (secondary provider) succeeds
            mock_create = MockOpenAI.return_value.chat.completions.create
            mock_create.side_effect = [quota_exc, mock_resp]
            result = router.call("executor", [{"role": "user", "content": "x"}])
        assert result is mock_resp
        # Primary should now be exhausted/cooldown
        primary_state = router.get_state()["primary"]
        assert primary_state.status != ProviderStatus.AVAILABLE

    def test_all_providers_exhausted_raises(
        self, router: ProviderRouter
    ) -> None:
        quota_exc = Exception("insufficient_quota")
        quota_exc.status_code = 429

        with patch("el_equipo_ai.provider_router.OpenAI") as MockOpenAI:
            MockOpenAI.return_value.chat.completions.create.side_effect = quota_exc
            with pytest.raises(AllProvidersExhausted):
                router.call("executor", [{"role": "user", "content": "x"}])
