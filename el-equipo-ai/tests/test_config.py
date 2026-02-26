"""Tests for el_equipo_ai.config — config loader."""

from __future__ import annotations

import os
import textwrap

import pytest

from el_equipo_ai.config import load_config
from el_equipo_ai.models import AppConfig


class TestLoadConfig:
    def test_loads_sample_config(self, sample_config_file: str) -> None:
        cfg = load_config(sample_config_file)
        assert isinstance(cfg, AppConfig)
        assert len(cfg.providers) == 3
        assert cfg.providers[0].name == "nvidia"
        assert len(cfg.roles) == 5
        assert "executor" in cfg.roles
        assert cfg.stall_detection.repeat_threshold == 3
        assert cfg.stall_detection.hard_timeout_minutes == 30
        assert cfg.logging.max_size_mb == 1
        assert cfg.project.test_command == "pytest"

    def test_correct_types(self, sample_config_file: str) -> None:
        cfg = load_config(sample_config_file)
        assert isinstance(cfg.roles["executor"].temperature, float)
        assert isinstance(cfg.roles["planner_structured"].json_mode, bool)
        assert cfg.roles["planner_structured"].json_mode is True
        assert cfg.roles["executor"].json_mode is False

    def test_model_options_parsed(self, sample_config_file: str) -> None:
        cfg = load_config(sample_config_file)
        executor_models = cfg.roles["executor"].models
        assert len(executor_models) == 2
        assert executor_models[0].provider == "openai"
        assert executor_models[0].model == "gpt-4o"

    def test_api_key_resolved_from_env(self, sample_config_file: str) -> None:
        cfg = load_config(sample_config_file)
        nvidia = next(p for p in cfg.providers if p.name == "nvidia")
        assert nvidia.api_key == "test-nvidia-key"  # set by conftest fixture

    def test_missing_api_key_env_var_is_none(
        self, sample_config_file: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("TEST_NVIDIA_API_KEY", raising=False)
        cfg = load_config(sample_config_file)
        nvidia = next(p for p in cfg.providers if p.name == "nvidia")
        assert nvidia.api_key is None

    def test_null_api_key_env_provider(self, sample_config_file: str) -> None:
        cfg = load_config(sample_config_file)
        local = next(p for p in cfg.providers if p.name == "local")
        assert local.api_key_env is None
        assert local.api_key is None

    def test_missing_providers_raises(self, tmp_path, monkeypatch) -> None:
        cfg_file = tmp_path / "bad.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            roles:
              executor:
                temperature: 0.3
                models: []
            stall_detection:
              repeat_threshold: 3
            logging:
              file: test.log
        """))
        with pytest.raises(ValueError, match="providers"):
            load_config(str(cfg_file))

    def test_missing_roles_raises(self, tmp_path) -> None:
        cfg_file = tmp_path / "bad.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            providers:
              - name: x
                base_url: http://x
                api_key_env: null
            stall_detection:
              repeat_threshold: 3
            logging:
              file: test.log
        """))
        with pytest.raises(ValueError, match="roles"):
            load_config(str(cfg_file))

    def test_missing_stall_detection_raises(self, tmp_path) -> None:
        cfg_file = tmp_path / "bad.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            providers:
              - name: x
                base_url: http://x
                api_key_env: null
            roles:
              executor:
                temperature: 0.3
                models: []
            logging:
              file: test.log
        """))
        with pytest.raises(ValueError, match="stall_detection"):
            load_config(str(cfg_file))

    def test_missing_logging_raises(self, tmp_path) -> None:
        cfg_file = tmp_path / "bad.yaml"
        cfg_file.write_text(textwrap.dedent("""\
            providers:
              - name: x
                base_url: http://x
                api_key_env: null
            roles:
              executor:
                temperature: 0.3
                models: []
            stall_detection:
              repeat_threshold: 3
        """))
        with pytest.raises(ValueError, match="logging"):
            load_config(str(cfg_file))

    def test_webhook_url_resolved_from_env(self, sample_config_file: str) -> None:
        cfg = load_config(sample_config_file)
        channel = cfg.notifications[0]
        assert channel.url == "https://hooks.test/webhook"

    def test_webhook_url_missing_env_is_none(
        self, sample_config_file: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("TEST_WEBHOOK_URL", raising=False)
        cfg = load_config(sample_config_file)
        assert cfg.notifications[0].url is None

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")
