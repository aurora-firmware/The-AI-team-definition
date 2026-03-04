"""Provider Router — role-based model selection with fallback and quota handling."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from openai import OpenAI

from el_equipo_ai.logger import Logger
from el_equipo_ai.models import (
    AppConfig,
    ProviderConfig,
    ProviderState,
    ProviderStatus,
    RoleConfig,
)


class AllProvidersExhausted(Exception):
    """Raised when no provider is available for a role."""


class ProviderRouter:
    """Routes API calls to the right model based on role configuration.

    Provider selection logic:
    - Each role has an ordered list of (provider, model) pairs.
    - The router picks the first provider whose status is AVAILABLE.
    - On quota exhaustion it marks the provider COOLDOWN/EXHAUSTED,
      persists the state, and falls back to the next option.
    - On simple rate-limit (429 + Retry-After) it waits and retries once
      without changing provider.
    """

    def __init__(self, config: AppConfig, logger: Logger) -> None:
        self._config = config
        self._logger = logger
        # Build provider lookup: name → ProviderConfig
        self._providers: dict[str, ProviderConfig] = {
            p.name: p for p in config.providers
        }
        # Runtime state: name → ProviderState (all AVAILABLE at start)
        self._states: dict[str, ProviderState] = {
            p.name: ProviderState(name=p.name) for p in config.providers
        }

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def get_state(self) -> dict[str, ProviderState]:
        return dict(self._states)

    def set_state(self, states: dict[str, ProviderState]) -> None:
        """Restore persisted state (called by QuotaManager on startup)."""
        for name, state in states.items():
            if name in self._states:
                self._states[name] = state

    def mark_cooldown(self, provider_name: str, reset_at: datetime) -> None:
        if provider_name in self._states:
            self._states[provider_name] = ProviderState(
                name=provider_name,
                status=ProviderStatus.COOLDOWN,
                reset_at=reset_at,
            )
            self._logger.log(
                "provider_cooldown",
                provider=provider_name,
                reset_at=reset_at.isoformat(),
            )

    def mark_exhausted(self, provider_name: str) -> None:
        if provider_name in self._states:
            self._states[provider_name] = ProviderState(
                name=provider_name,
                status=ProviderStatus.EXHAUSTED,
                reset_at=None,
            )
            self._logger.log("provider_exhausted", provider=provider_name)

    def check_cooldowns(self) -> None:
        """Transition COOLDOWN providers back to AVAILABLE if their timer has passed."""
        now = datetime.now(timezone.utc)
        for name, state in self._states.items():
            if state.status == ProviderStatus.COOLDOWN:
                if state.reset_at and now >= state.reset_at:
                    self._states[name] = ProviderState(
                        name=name, status=ProviderStatus.AVAILABLE
                    )
                    self._logger.log("provider_available", provider=name, reason="cooldown_expired")

    # ------------------------------------------------------------------
    # Provider selection
    # ------------------------------------------------------------------

    def get_provider_for_role(
        self, role_name: str
    ) -> tuple[ProviderConfig, RoleConfig, str] | None:
        """Return (provider_config, role_config, model_id) for the first available provider.

        Returns None if no provider is available for this role.
        """
        self.check_cooldowns()
        role = self._config.roles.get(role_name)
        if not role:
            raise ValueError(f"Unknown role: {role_name!r}")

        for option in role.models:
            state = self._states.get(option.provider)
            if state and state.status == ProviderStatus.AVAILABLE:
                provider = self._providers[option.provider]
                return (provider, role, option.model)
        return None

    # ------------------------------------------------------------------
    # API call
    # ------------------------------------------------------------------

    def call(
        self,
        role_name: str,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> Any:
        """Send a chat completion request for the given role.

        Handles:
        - 429 with Retry-After: wait and retry once (same provider).
        - Quota exhaustion: mark provider exhausted/cooldown, try next provider.
        - AllProvidersExhausted if no providers remain.
        """
        role = self._config.roles.get(role_name)
        if not role:
            raise ValueError(f"Unknown role: {role_name!r}")

        # Try each model option in priority order
        for option in role.models:
            state = self._states.get(option.provider)
            if not state or state.status != ProviderStatus.AVAILABLE:
                continue

            self.check_cooldowns()
            state = self._states.get(option.provider)
            if not state or state.status != ProviderStatus.AVAILABLE:
                continue

            provider = self._providers.get(option.provider)
            if not provider:
                continue

            result = self._try_call(provider, role, option.model, messages, tools)
            if result is not None:
                return result

        raise AllProvidersExhausted(
            f"All providers exhausted for role '{role_name}'"
        )

    def _try_call(
        self,
        provider: ProviderConfig,
        role: RoleConfig,
        model: str,
        messages: list[dict],
        tools: list[dict] | None,
    ) -> Any | None:
        """Attempt one API call. Returns the response or None if we should try next provider."""
        client = OpenAI(
            base_url=provider.base_url,
            api_key=provider.api_key or "no-key",
        )

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": role.temperature,
        }
        if tools:
            kwargs["tools"] = tools
        if role.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = client.chat.completions.create(**kwargs)
            self._logger.log(
                "provider_call",
                role=role.name,
                provider=provider.name,
                model=model,
                status="ok",
            )
            return response

        except Exception as exc:
            return self._handle_exception(exc, provider, role, model, messages, tools, client, kwargs)

    def _handle_exception(
        self,
        exc: Exception,
        provider: ProviderConfig,
        role: RoleConfig,
        model: str,
        messages: list[dict],
        tools: list[dict] | None,
        client: OpenAI,
        kwargs: dict,
    ) -> Any | None:
        """Handle API exceptions. Returns response if recovered, None to try next provider."""
        exc_str = str(exc)
        status_code = getattr(exc, "status_code", None)

        # ---- Rate limit (short cooldown — wait and retry once) ----
        if status_code == 429:
            retry_after = self._extract_retry_after(exc)
            if retry_after and retry_after <= 120:  # only wait for short cooldowns
                self._logger.log(
                    "provider_rate_limit",
                    provider=provider.name,
                    model=model,
                    retry_after=retry_after,
                )
                time.sleep(retry_after)
                try:
                    response = client.chat.completions.create(**kwargs)
                    self._logger.log(
                        "provider_call",
                        role=role.name,
                        provider=provider.name,
                        model=model,
                        status="ok_after_retry",
                    )
                    return response
                except Exception as retry_exc:
                    exc = retry_exc
                    status_code = getattr(retry_exc, "status_code", None)
                    exc_str = str(retry_exc)

        # ---- Quota exhaustion ----
        if self._is_quota_error(status_code, exc_str):
            reset_at = self._extract_reset_at(exc)
            if reset_at:
                self.mark_cooldown(provider.name, reset_at)
            else:
                self.mark_exhausted(provider.name)
            self._logger.log(
                "provider_swap",
                from_provider=provider.name,
                model=model,
                reason="quota_exhausted",
            )
            return None  # signal: try next provider

        # ---- Other error — propagate ----
        self._logger.log(
            "provider_error",
            provider=provider.name,
            model=model,
            error=exc_str,
            status_code=status_code,
        )
        raise exc

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_retry_after(exc: Exception) -> int | None:
        """Try to extract a Retry-After value (seconds) from the exception."""
        # OpenAI SDK stores headers in exc.response.headers
        response = getattr(exc, "response", None)
        if response is not None:
            headers = getattr(response, "headers", {}) or {}
            retry = headers.get("retry-after") or headers.get("Retry-After")
            if retry:
                try:
                    return int(retry)
                except (ValueError, TypeError):
                    pass
        return None

    @staticmethod
    def _extract_reset_at(exc: Exception) -> datetime | None:
        """Try to extract a quota reset timestamp from the exception.

        Returns None when no reset information is available — the caller
        should treat this as a permanent exhaustion (not a timed cooldown).
        """
        response = getattr(exc, "response", None)
        if response is not None:
            headers = getattr(response, "headers", {}) or {}
            reset = (
                headers.get("x-ratelimit-reset-tokens")
                or headers.get("X-RateLimit-Reset-Tokens")
                or headers.get("x-quota-reset")
            )
            if reset:
                try:
                    return datetime.fromtimestamp(float(reset), tz=timezone.utc)
                except (ValueError, TypeError):
                    pass
        return None

    @staticmethod
    def _is_quota_error(status_code: int | None, exc_str: str) -> bool:
        """Detect quota-exhaustion errors vs plain rate-limits."""
        if status_code == 402:
            return True
        quota_phrases = (
            "quota", "billing", "insufficient_quota", "credit", "exceeded",
            "monthly limit", "usage limit",
        )
        exc_lower = exc_str.lower()
        return any(phrase in exc_lower for phrase in quota_phrases)
