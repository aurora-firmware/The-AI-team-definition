"""Tests for T-082: structured results for spec/adr/change-request creation."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_team.commands.adr import create_adr
from ai_team.commands.change_request import create_change_request
from ai_team.commands.spec import create_spec
from ai_team.core.locator import ProjectRootNotFound, find_project_root
from ai_team.core.result import Result


def _root(tmp_path: Path):
    for name in ("specs", "decisions", "change-requests"):
        (tmp_path / "project" / name).mkdir(parents=True)
    return find_project_root(tmp_path, root=tmp_path)


# AC-1
def test_result_carries_status_payload_message_and_hint_separately():
    result = Result(status=1, payload=None, message="boom", hint="try again")
    assert (result.status, result.payload, result.message, result.hint) == (
        1,
        None,
        "boom",
        "try again",
    )
    with pytest.raises(FrozenInstanceError):
        result.status = 0  # type: ignore[misc]


def test_result_text_joins_message_and_hint_with_a_space():
    assert Result(1, None, "boom.", "Fix it.").text() == "boom. Fix it."
    assert Result(1, None, "boom.", None).text() == "boom."


# AC-3
@pytest.mark.parametrize(
    "handler,args,kind",
    [
        (create_spec, ("Alpha",), "S-"),
        (create_adr, ("Alpha",), "ADR"),
        (create_change_request, ("Alpha",), "CR"),
    ],
)
def test_handlers_run_with_explicit_root_without_typer_or_cwd(
    tmp_path, monkeypatch, handler, args, kind
):
    root = _root(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = handler(root, *args)

    assert result.status == 0
    assert result.message is None and result.hint is None
    assert result.payload["id"].startswith(kind)
    assert Path(result.payload["path"]).is_file()
    assert Path(result.payload["path"]).is_relative_to(tmp_path / "project")


# AC-2
@pytest.mark.parametrize(
    "argv,module,handler_name",
    [
        (["spec", "new", "Alpha"], "spec", "create_spec"),
        (["adr", "new", "Alpha"], "adr", "create_adr"),
        (["change-request", "new", "Alpha"], "change_request", "create_change_request"),
    ],
)
def test_json_output_equals_handler_payload(
    tmp_path, monkeypatch, argv, module, handler_name
):
    import importlib

    from ai_team.cli import app

    _root(tmp_path)
    monkeypatch.chdir(tmp_path)
    payload = {"id": "X-1", "path": "/somewhere", "sentinel": [1, 2]}
    command_module = importlib.import_module(f"ai_team.commands.{module}")
    monkeypatch.setattr(
        command_module, handler_name, lambda *a, **k: Result(0, payload)
    )

    cli = CliRunner().invoke(app, [*argv, "--json"])

    assert cli.exit_code == 0
    assert json.loads(cli.stdout) == payload


def _force_adr_collision(monkeypatch, root):
    """Make the next ADR id collide with an existing file; return that file."""
    first = create_adr(root, "Same")
    existing = Path(first.payload["path"])
    monkeypatch.setattr(
        "ai_team.commands.adr.next_adr_id", lambda _root: existing.name[:7]
    )
    return existing


# AC-4
def test_domain_error_message_equals_todays_stderr_without_hint(tmp_path, monkeypatch):
    root = _root(tmp_path)
    existing = _force_adr_collision(monkeypatch, root)

    result = create_adr(root, "Same")

    assert result.status == 1
    assert result.payload is None
    assert result.hint is None
    assert result.message == (
        f"Artifact already exists at {existing!s}; pass overwrite=True to replace it."
    )


def test_cli_prints_domain_error_text_on_stderr_and_exits_one(tmp_path, monkeypatch):
    from ai_team.cli import app

    root = _root(tmp_path)
    existing = _force_adr_collision(monkeypatch, root)
    monkeypatch.chdir(tmp_path)

    cli = CliRunner().invoke(app, ["adr", "new", "Same"])

    assert cli.exit_code == 1
    assert cli.stdout == ""
    assert create_adr(root, "Same").text() in cli.stderr
    assert str(existing) in cli.stderr


# AC-6
def test_project_root_not_found_exposes_message_and_hint(tmp_path):
    with pytest.raises(ProjectRootNotFound) as exc_info:
        find_project_root(tmp_path)
    exc = exc_info.value
    assert exc.hint == "Run 'ai-team init' to bootstrap the project structure."
    assert "ai-team init" not in exc.message
    assert exc.message.endswith(".")
    assert str(exc) == f"{exc.message} {exc.hint}"


def test_project_root_not_found_str_for_explicit_root_matches_prior_text(tmp_path):
    with pytest.raises(ProjectRootNotFound) as exc_info:
        find_project_root(tmp_path, root=tmp_path)
    assert str(exc_info.value) == (
        f"No 'project/' folder found under the provided --root {tmp_path.resolve()!s}. "
        "Run 'ai-team init' to bootstrap the project structure."
    )
