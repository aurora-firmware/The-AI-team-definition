"""Tests for el_equipo_ai.notifier — webhook notifier."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import LogConfig, NotificationChannel
from el_equipo_ai.notifier import Notifier


@pytest.fixture()
def logger(tmp_path: Path) -> Logger:
    return Logger(LogConfig(file=str(tmp_path / "test.log"), max_size_mb=10, max_rotated_files=2))


@pytest.fixture()
def channels() -> list[NotificationChannel]:
    return [
        NotificationChannel(type="webhook", name="ch1", url_env="CH1_URL", url="https://hooks.test/ch1"),
        NotificationChannel(type="webhook", name="ch2", url_env="CH2_URL", url="https://hooks.test/ch2"),
    ]


@pytest.fixture()
def notifier(channels: list[NotificationChannel], logger: Logger) -> Notifier:
    return Notifier(channels=channels, logger=logger)


class TestInfo:
    def test_prints_to_stdout(self, notifier: Notifier, capsys: pytest.CaptureFixture) -> None:
        notifier.info("hello world")
        captured = capsys.readouterr()
        assert "hello world" in captured.out

    def test_logs_info_event(self, channels, logger, tmp_path) -> None:
        import json
        log_path = tmp_path / "test.log"
        lg = Logger(LogConfig(file=str(log_path), max_size_mb=10, max_rotated_files=2))
        n = Notifier(channels=channels, logger=lg)
        n.info("test info message")
        lines = log_path.read_text().splitlines()
        assert any(json.loads(l)["type"] == "notification_info" for l in lines)


class TestActionRequired:
    def test_posts_to_all_channels(
        self, notifier: Notifier, channels: list[NotificationChannel]
    ) -> None:
        with patch("el_equipo_ai.notifier.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp

            notifier.action_required("Title", "Body text", "http://vk/task/1")

        assert mock_post.call_count == 2
        urls_called = {c.args[0] for c in mock_post.call_args_list}
        assert "https://hooks.test/ch1" in urls_called
        assert "https://hooks.test/ch2" in urls_called

    def test_payload_format(self, notifier: Notifier) -> None:
        with patch("el_equipo_ai.notifier.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            notifier.action_required("My Title", "Some body", "http://vk/1")

        payload = mock_post.call_args_list[0].kwargs["json"]
        assert "[ACTION REQUIRED]" in payload["text"]
        assert "My Title" in payload["text"]
        assert "Some body" in payload["text"]
        assert "http://vk/1" in payload["text"]

    def test_failed_webhook_does_not_raise(self, notifier: Notifier) -> None:
        with patch("el_equipo_ai.notifier.requests.post") as mock_post:
            mock_post.side_effect = Exception("connection refused")
            # Must not raise despite both channels failing
            notifier.action_required("T", "B")

    def test_failed_webhook_logged(
        self, channels: list[NotificationChannel], tmp_path: Path
    ) -> None:
        import json
        log_path = tmp_path / "n.log"
        lg = Logger(LogConfig(file=str(log_path), max_size_mb=10, max_rotated_files=2))
        n = Notifier(channels=channels, logger=lg)

        with patch("el_equipo_ai.notifier.requests.post") as mock_post:
            mock_post.side_effect = Exception("boom")
            n.action_required("T", "B")

        lines = log_path.read_text().splitlines()
        error_events = [json.loads(l) for l in lines if json.loads(l)["type"] == "notification_error"]
        assert len(error_events) == 2  # one per channel

    def test_missing_url_skips_gracefully(self, logger: Logger) -> None:
        channel_no_url = NotificationChannel(
            type="webhook", name="empty", url_env="MISSING_VAR", url=None
        )
        n = Notifier(channels=[channel_no_url], logger=logger)
        with patch("el_equipo_ai.notifier.requests.post") as mock_post:
            n.action_required("T", "B")
        mock_post.assert_not_called()

    def test_vk_link_optional(self, notifier: Notifier) -> None:
        with patch("el_equipo_ai.notifier.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            notifier.action_required("Title", "Body")  # no vk_link
        payload = mock_post.call_args_list[0].kwargs["json"]
        assert "None" not in payload["text"]
