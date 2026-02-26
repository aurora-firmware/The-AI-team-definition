"""Webhook notifier — info tier goes to stdout, action-required tier fires webhooks."""

from __future__ import annotations

import requests

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import NotificationChannel


class Notifier:
    """Two-tier notification delivery.

    info()           → stdout only.
    action_required() → stdout + POST to every configured webhook channel.
                        Individual channel failures are logged, never raised.
    """

    def __init__(self, channels: list[NotificationChannel], logger: Logger) -> None:
        self._channels = channels
        self._logger = logger

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def info(self, message: str) -> None:
        """Print an informational message to stdout and log it."""
        print(f"[INFO] {message}")
        self._logger.log("notification_info", message=message)

    def action_required(
        self,
        title: str,
        body: str,
        vk_link: str | None = None,
    ) -> None:
        """Notify all channels that human action is required.

        Formats a message and POSTs it to every configured webhook. A failed
        delivery is logged but does not raise so that other channels are still
        attempted.
        """
        inspect_line = f"\nInspect: {vk_link}" if vk_link else ""
        text = f"[ACTION REQUIRED] {title}\n{body}{inspect_line}"

        print(text)
        self._logger.log(
            "notification_action_required",
            title=title,
            body=body,
            vk_link=vk_link,
        )

        for channel in self._channels:
            self._send_webhook(channel, text)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _send_webhook(self, channel: NotificationChannel, text: str) -> None:
        if not channel.url:
            self._logger.log(
                "notification_skip",
                channel=channel.name,
                reason="url_not_configured",
            )
            return

        try:
            resp = requests.post(
                channel.url,
                json={"text": text},
                timeout=10,
            )
            resp.raise_for_status()
            self._logger.log(
                "notification_sent",
                channel=channel.name,
                status_code=resp.status_code,
            )
        except Exception as exc:  # noqa: BLE001
            self._logger.log(
                "notification_error",
                channel=channel.name,
                error=str(exc),
            )
