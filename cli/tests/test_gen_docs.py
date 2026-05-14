"""
Tests for T-027: Add typer-cli dependency, gen_docs script, and generate commands.md.

Covers:
  AC-1: typer-cli is declared in the dev dependency group in pyproject.toml.
  AC-2: bash cli/scripts/gen_docs.sh regenerates cli/docs/commands.md from the Typer app.
  AC-3: commands.md contains every command group, subcommand, argument, and flag.
  AC-4: commands.md has a header note stating it is generated and naming the regeneration command.
  AC-5: Running gen_docs.sh twice with no code change produces a byte-identical commands.md.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_DIR = REPO_ROOT / "cli"
PYPROJECT = CLI_DIR / "pyproject.toml"
GEN_DOCS_SCRIPT = CLI_DIR / "scripts" / "gen_docs.sh"
COMMANDS_MD = CLI_DIR / "docs" / "commands.md"


# ---------------------------------------------------------------------------
# AC-1: typer-cli in the dev dependency group
# ---------------------------------------------------------------------------


def test_typer_cli_declared_in_dev_dependency_group():
    """pyproject.toml must list typer-cli in the [dependency-groups] dev group."""
    import tomllib

    content = PYPROJECT.read_bytes()
    data = tomllib.loads(content.decode("utf-8"))

    # Confirm typer-cli is in the dev dependency group.
    dev_deps = data.get("dependency-groups", {}).get("dev", [])
    # Each entry may be a string (e.g. "typer-cli>=0.24.0") or a dict.
    found_in_dev = any(isinstance(dep, str) and "typer-cli" in dep for dep in dev_deps)
    assert found_in_dev, (
        "typer-cli must be listed in [dependency-groups] dev in cli/pyproject.toml"
    )

    # Confirm typer-cli is NOT in the runtime [project] dependencies.
    runtime_deps = data.get("project", {}).get("dependencies", [])
    found_in_runtime = any(
        isinstance(dep, str) and "typer-cli" in dep for dep in runtime_deps
    )
    assert not found_in_runtime, (
        "typer-cli must not appear in the [project] runtime dependencies"
    )


# ---------------------------------------------------------------------------
# AC-2: gen_docs.sh exists and regenerates commands.md
# ---------------------------------------------------------------------------


def test_gen_docs_script_exists():
    """cli/scripts/gen_docs.sh must exist and be a regular file."""
    assert GEN_DOCS_SCRIPT.is_file(), f"Expected script not found: {GEN_DOCS_SCRIPT}"


def test_gen_docs_script_produces_commands_md(tmp_path):
    """Running gen_docs.sh creates cli/docs/commands.md with non-empty content."""
    result = subprocess.run(
        ["bash", str(GEN_DOCS_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"gen_docs.sh exited with code {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert COMMANDS_MD.is_file(), "cli/docs/commands.md was not created by gen_docs.sh"
    content = COMMANDS_MD.read_text(encoding="utf-8")
    assert len(content) > 100, "commands.md is unexpectedly short or empty"


# ---------------------------------------------------------------------------
# AC-3: commands.md contains key commands
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("expected_term", ["task", "init", "validate"])
def test_commands_md_contains_key_command(expected_term):
    """commands.md must document the major command groups and subcommands."""
    assert COMMANDS_MD.is_file(), "commands.md must exist (run gen_docs.sh first)"
    content = COMMANDS_MD.read_text(encoding="utf-8").lower()
    assert expected_term in content, f"commands.md does not mention '{expected_term}'"


def test_commands_md_contains_global_flags():
    """commands.md must include global flags such as --version and --help."""
    assert COMMANDS_MD.is_file(), "commands.md must exist (run gen_docs.sh first)"
    content = COMMANDS_MD.read_text(encoding="utf-8")
    assert "--version" in content, "commands.md must document the global --version flag"
    assert "--help" in content, "commands.md must document the --help flag"


# ---------------------------------------------------------------------------
# AC-4: commands.md has a generated-file header note
# ---------------------------------------------------------------------------


def test_commands_md_has_generated_header_note():
    """commands.md must open with a note that it is generated and must not be hand-edited."""
    assert COMMANDS_MD.is_file(), "commands.md must exist (run gen_docs.sh first)"
    content = COMMANDS_MD.read_text(encoding="utf-8")
    # The header note should appear near the top.
    preamble = content[:500].lower()
    assert "generated" in preamble, (
        "commands.md must have a header note stating the file is generated"
    )


def test_commands_md_header_names_regeneration_command():
    """The header note in commands.md must name the regeneration command."""
    assert COMMANDS_MD.is_file(), "commands.md must exist (run gen_docs.sh first)"
    content = COMMANDS_MD.read_text(encoding="utf-8")
    preamble = content[:500]
    assert "gen_docs.sh" in preamble, (
        "commands.md header must name the regeneration command (gen_docs.sh)"
    )


# ---------------------------------------------------------------------------
# AC-5: idempotent generation
# ---------------------------------------------------------------------------


def test_gen_docs_is_idempotent():
    """Running gen_docs.sh twice produces byte-identical commands.md."""
    # First run.
    result1 = subprocess.run(
        ["bash", str(GEN_DOCS_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result1.returncode == 0, f"First gen_docs.sh run failed: {result1.stderr}"
    content_after_first = COMMANDS_MD.read_bytes()

    # Second run.
    result2 = subprocess.run(
        ["bash", str(GEN_DOCS_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result2.returncode == 0, f"Second gen_docs.sh run failed: {result2.stderr}"
    content_after_second = COMMANDS_MD.read_bytes()

    assert content_after_first == content_after_second, (
        "commands.md changed between two consecutive gen_docs.sh runs with no code change"
    )
