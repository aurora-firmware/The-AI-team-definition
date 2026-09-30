"""Marker parsing and claude/codex rendering for skill sources (S-005 marker contract)."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CLI_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = CLI_DIR / "scripts"
SOURCES_DIR = CLI_DIR / "src" / "ai_team" / "init" / "sources"
COMMAND_MAP_PATH = SOURCES_DIR / "command_map.json"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "skill_markers_under_test", SCRIPTS_DIR / "skill_markers.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


markers = _load_module()


@pytest.fixture
def command_map() -> dict:
    return json.loads(COMMAND_MAP_PATH.read_text(encoding="utf-8"))


def _render(text: str, target: str, command_map: dict, source: str = "body.md") -> str:
    return markers.render_markers(text, target, command_map, source)


# AC-1: claude/codex render verbatim.


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_command_marker_renders_as_ai_team_argv_verbatim(target, command_map) -> None:
    text = 'Run `{{ai-team bug new "<title>" --severity "<severity>" --json}}` now.'

    rendered = _render(text, target, command_map)

    assert (
        rendered
        == 'Run `ai-team bug new "<title>" --severity "<severity>" --json` now.'
    )


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_command_marker_keeps_optional_placeholders_verbatim(
    target, command_map
) -> None:
    text = '{{ai-team adr new "<title>" [--supersedes <ADR-ID>] --json}}'

    assert (
        _render(text, target, command_map)
        == 'ai-team adr new "<title>" [--supersedes <ADR-ID>] --json'
    )


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_command_marker_with_no_positionals_renders(target, command_map) -> None:
    assert _render("{{ai-team status}}", target, command_map) == "ai-team status"


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_flag_marker_renders_only_the_flag_text(target, command_map) -> None:
    text = "Pass `{{ai-team-flag adr new --supersedes}}` when replacing."

    assert _render(text, target, command_map) == "Pass `--supersedes` when replacing."


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_flag_marker_accepts_multiple_flags(target, command_map) -> None:
    text = "{{ai-team-flag bug new --severity --task}}"

    assert _render(text, target, command_map) == "--severity --task"


@pytest.mark.parametrize("target", ["claude", "codex"])
def test_noun_marker_renders_first_text(target, command_map) -> None:
    text = "via {{ai-team-cli|the `ai-team` CLI|the `ai_team` tool}} today"

    assert _render(text, target, command_map) == "via the `ai-team` CLI today"


def test_text_without_markers_is_returned_unchanged(command_map) -> None:
    text = "# Title\n\n```bash\nls {not a marker}\n```\n"

    assert _render(text, "claude", command_map) == text


def test_multiple_markers_on_one_line_all_render(command_map) -> None:
    text = "{{ai-team status}} then {{ai-team-cli|CLI|tool}}"

    assert _render(text, "codex", command_map) == "ai-team status then CLI"


# AC-2: unknown kind / unparseable content fails naming file and marker.


def _assert_error_names(exc: pytest.ExceptionInfo, source: str, marker: str) -> None:
    message = str(exc.value)
    assert source in message
    assert marker in message


@pytest.mark.parametrize(
    "marker",
    ["{{unknown-kind foo}}", "{{ai-team-extra status}}", "{{}}", "{{ai-teamstatus}}"],
)
def test_unknown_marker_kind_is_rejected(marker, command_map) -> None:
    with pytest.raises(markers.MarkerError) as exc:
        _render(f"text {marker} text", "claude", command_map, "skills/tdd/body.md")

    _assert_error_names(exc, "skills/tdd/body.md", marker)


def test_command_marker_with_unknown_command_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError) as exc:
        _render("{{ai-team frobnicate now}}", "claude", command_map, "a/body.md")

    _assert_error_names(exc, "a/body.md", "{{ai-team frobnicate now}}")


def test_command_marker_with_undefined_flag_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError) as exc:
        _render("{{ai-team status --bogus}}", "claude", command_map, "a/body.md")

    _assert_error_names(exc, "a/body.md", "{{ai-team status --bogus}}")
    assert "--bogus" in str(exc.value)


def test_command_marker_rejects_flag_defined_only_for_another_command(
    command_map,
) -> None:
    with pytest.raises(markers.MarkerError):
        _render("{{ai-team status --supersedes <ID>}}", "claude", command_map)


def test_command_marker_rejects_bracketed_undefined_flag(command_map) -> None:
    with pytest.raises(markers.MarkerError):
        _render('{{ai-team adr new "<t>" [--bogus <x>]}}', "claude", command_map)


def test_flag_marker_with_undefined_flag_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError) as exc:
        _render("{{ai-team-flag adr new --severity}}", "codex", command_map, "f.md")

    _assert_error_names(exc, "f.md", "{{ai-team-flag adr new --severity}}")


def test_flag_marker_with_unknown_command_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError):
        _render("{{ai-team-flag nope --json}}", "claude", command_map)


def test_flag_marker_without_flags_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError):
        _render("{{ai-team-flag adr new}}", "claude", command_map)


def test_flag_marker_with_non_flag_token_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError):
        _render("{{ai-team-flag adr new --supersedes value}}", "claude", command_map)


@pytest.mark.parametrize(
    "marker",
    ["{{ai-team-cli|only one}}", "{{ai-team-cli|a|b|c}}", "{{ai-team-cli||pi}}"],
)
def test_malformed_noun_marker_is_rejected(marker, command_map) -> None:
    with pytest.raises(markers.MarkerError) as exc:
        _render(marker, "claude", command_map, "n.md")

    _assert_error_names(exc, "n.md", marker)


def test_command_marker_without_argv_is_rejected(command_map) -> None:
    with pytest.raises(markers.MarkerError):
        _render("{{ai-team }}", "claude", command_map)


def test_unsupported_target_is_rejected(command_map) -> None:
    with pytest.raises(ValueError, match="pi"):
        _render("{{ai-team status}}", "pi", command_map)


# AC-3: header markers rendered per target (via the sync).


def _fake_repo(tmp_path: Path, body: str, metadata: str) -> Path:
    repo = tmp_path / "repo"
    init_root = repo / "cli" / "src" / "ai_team" / "init"
    sources = init_root / "sources"
    skill = sources / "skills" / "demo"
    skill.mkdir(parents=True)
    (skill / "body.md").write_text(body, encoding="utf-8")
    (skill / "metadata.toml").write_text(metadata, encoding="utf-8")
    (sources / "command_map.json").write_text(
        COMMAND_MAP_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    for tool in ("claude", "codex"):
        (sources / "agents" / tool).mkdir(parents=True)
    project = sources / "project"
    project.mkdir()
    for name in ("CLAUDE.md", "AGENTS.md", ".gitignore"):
        (project / name).write_text("x\n", encoding="utf-8")
    scripts = repo / "cli" / "scripts"
    scripts.mkdir(parents=True)
    for name in ("sync_init_scaffolds.py", "skill_markers.py"):
        shutil.copy2(SCRIPTS_DIR / name, scripts / name)
    return repo


def _run_sync(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def _skill_output(repo: Path, tool: str) -> str:
    path = repo / "cli/src/ai_team/init/scaffolds" / tool / "skills/demo/SKILL.md"
    return path.read_text(encoding="utf-8")


_METADATA = (
    '[claude]\nheader = """---\nname: demo\n'
    'description: claude via {{ai-team-cli|the ai-team CLI|the tool}}\n---"""\n\n'
    '[codex]\nheader = """---\nname: demo\n'
    'description: codex via {{ai-team-cli|AI team CLI|the tool}}\n---"""\n'
)


def test_sync_renders_header_and_body_markers_for_each_target(tmp_path) -> None:
    repo = _fake_repo(
        tmp_path, "Run {{ai-team status}} with {{ai-team-cli|CLI|t}}.\n", _METADATA
    )

    result = _run_sync(repo)

    assert result.returncode == 0, result.stderr
    claude = _skill_output(repo, "claude")
    codex = _skill_output(repo, "codex")
    assert "description: claude via the ai-team CLI\n" in claude
    assert "description: codex via AI team CLI\n" in codex
    assert claude.endswith("Run ai-team status with CLI.\n")
    assert codex.endswith("Run ai-team status with CLI.\n")


def test_sync_fails_naming_file_and_marker_on_unknown_body_marker(tmp_path) -> None:
    repo = _fake_repo(tmp_path, "Bad {{mystery x}} here\n", _METADATA)

    result = _run_sync(repo)

    assert result.returncode != 0
    assert "demo/body.md" in result.stderr
    assert "{{mystery x}}" in result.stderr


def test_sync_fails_naming_file_and_marker_on_bad_header_marker(tmp_path) -> None:
    metadata = _METADATA.replace("{{ai-team-cli|the ai-team CLI|the tool}}", "{{nope}}")
    repo = _fake_repo(tmp_path, "body\n", metadata)

    result = _run_sync(repo)

    assert result.returncode != 0
    assert "demo/metadata.toml" in result.stderr
    assert "{{nope}}" in result.stderr


# AC-4: unchanged sources render identically (no markers in current sources).


def test_current_skill_sources_contain_no_markers_so_output_is_unchanged(
    command_map,
) -> None:
    for path in sorted((SOURCES_DIR / "skills").glob("*/*")):
        text = path.read_text(encoding="utf-8")
        for target in ("claude", "codex"):
            assert _render(text, target, command_map, str(path)) == text
