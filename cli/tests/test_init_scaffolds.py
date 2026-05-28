"""Tests for package-owned init scaffold source generation."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _script_under_test() -> Path:
    return Path(__file__).resolve().parents[1] / "scripts" / "sync_init_scaffolds.py"


def _setup_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    # Trap files at repository root that should never be read by the generator.
    _write(repo / ".claude", "trap\n")
    _write(repo / ".codex", "trap\n")
    _write(repo / "ai-process", "trap\n")

    # Package-owned skill source fixture.
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "skills"
        / "tdd"
        / "body.md",
        "# Test Skill Body\n\nRun the TDD cycle.\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "skills"
        / "tdd"
        / "metadata.toml",
        (
            "[claude]\n"
            'header = """---\n'
            "name: tdd\n"
            "description: claude skill\n"
            "allowed-tools: Read\n"
            '---"""\n\n'
            "[codex]\n"
            'header = """---\n'
            "name: tdd\n"
            "description: codex skill\n"
            "allowed-tools: Read\n"
            '---"""\n'
        ),
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "agents"
        / "claude"
        / "planner.md",
        "claude planner\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "agents"
        / "codex"
        / "planner.toml",
        "codex planner\n",
    )

    # Seed stale generated output that should be removed.
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "old"
        / "SKILL.md",
        "old\n",
    )
    _write(
        repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "project" / "old.txt",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "agents"
        / "old.md",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "agents"
        / "old.toml",
        "old\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "skills"
        / "old"
        / "SKILL.md",
        "old\n",
    )

    script = _script_under_test()
    assert script.exists(), "sync helper script is missing"
    copied_script = repo / "cli" / "scripts" / "sync_init_scaffolds.py"
    copied_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(script, copied_script)

    return repo


def test_sync_script_generates_tool_skill_scaffolds_from_shared_body(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    scaffolds_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"
    shared_body = "# Test Skill Body\n\nRun the TDD cycle.\n"

    claude_text = (scaffolds_root / "claude" / "skills" / "tdd" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    codex_text = (scaffolds_root / "codex" / "skills" / "tdd" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert claude_text.startswith("---\nname: tdd\ndescription: claude skill\n")
    assert codex_text.startswith("---\nname: tdd\ndescription: codex skill\n")
    assert claude_text.split("\n\n", maxsplit=1)[1] == shared_body
    assert codex_text.split("\n\n", maxsplit=1)[1] == shared_body

    assert not (scaffolds_root / "claude" / "skills" / "old").exists()
    assert not (scaffolds_root / "codex" / "skills" / "old").exists()


def test_sync_script_copies_package_owned_agents_for_each_tool(tmp_path: Path) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    scaffolds_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"

    assert (scaffolds_root / "claude" / "agents" / "planner.md").read_text(
        encoding="utf-8"
    ) == "claude planner\n"
    assert (scaffolds_root / "codex" / "agents" / "planner.toml").read_text(
        encoding="utf-8"
    ) == "codex planner\n"

    assert not (scaffolds_root / "claude" / "agents" / "old.md").exists()
    assert not (scaffolds_root / "codex" / "agents" / "old.toml").exists()


def test_sync_script_replaces_project_with_empty_lifecycle_skeleton(
    tmp_path: Path,
) -> None:
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    project_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "project"
    expected_files = {
        Path("specs/.gitkeep"),
        Path("tasks/pending/.gitkeep"),
        Path("tasks/in-progress/.gitkeep"),
        Path("tasks/completed/.gitkeep"),
        Path("tasks/blocked/.gitkeep"),
        Path("bugs/open/.gitkeep"),
        Path("bugs/in-progress/.gitkeep"),
        Path("bugs/resolved/.gitkeep"),
        Path("decisions/.gitkeep"),
        Path("docs/.gitkeep"),
    }
    actual_files = {
        (Path(root) / file_name).relative_to(project_root)
        for root, _, file_names in os.walk(project_root)
        for file_name in file_names
    }

    assert actual_files == expected_files
    assert not (project_root / "old.txt").exists()


def test_package_owned_skill_sources_include_body_and_required_metadata() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sources_root = repo_root / "src" / "ai_team" / "init" / "sources" / "skills"
    scaffold_root = (
        repo_root / "src" / "ai_team" / "init" / "scaffolds" / "claude" / "skills"
    )

    expected_skills = sorted(
        path.name for path in scaffold_root.iterdir() if path.is_dir()
    )
    source_skills = sorted(
        path.name for path in sources_root.iterdir() if path.is_dir()
    )

    assert source_skills == expected_skills

    for skill_name in source_skills:
        skill_source_dir = sources_root / skill_name
        skill_scaffold_path = scaffold_root / skill_name / "SKILL.md"

        body_files = list(skill_source_dir.glob("body.md"))
        metadata_files = list(skill_source_dir.glob("metadata.toml"))

        assert len(body_files) == 1
        assert len(metadata_files) == 1

        body = body_files[0].read_text(encoding="utf-8")
        metadata = tomllib.loads(metadata_files[0].read_text(encoding="utf-8"))

        assert isinstance(metadata.get("claude", {}).get("header"), str)
        assert metadata["claude"]["header"].strip()
        assert isinstance(metadata.get("codex", {}).get("header"), str)
        assert metadata["codex"]["header"].strip()

        scaffold_text = skill_scaffold_path.read_text(encoding="utf-8")
        scaffold_header, scaffold_body = scaffold_text.split("\n\n", maxsplit=1)

        assert body == scaffold_body
        assert metadata["claude"]["header"].strip() == scaffold_header.strip()


def test_sync_script_generates_codex_agent_scaffolds_as_real_files_not_symlinks(
    tmp_path: Path,
) -> None:
    """AC-3: Codex agent scaffold files must be real files, not symlinks."""
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    codex_agents = (
        repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "codex" / "agents"
    )
    assert codex_agents.is_dir(), "codex agents scaffold directory must exist"
    for agent_file in codex_agents.iterdir():
        assert not agent_file.is_symlink(), (
            f"Expected real file but found symlink: {agent_file}"
        )


def test_sync_script_is_idempotent_for_agent_scaffolds(tmp_path: Path) -> None:
    """AC-4: Running the generator twice leaves no additional diff."""
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    scaffolds_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds"
    claude_agents = scaffolds_root / "claude" / "agents"
    codex_agents = scaffolds_root / "codex" / "agents"

    def collect_file_contents(directory: Path) -> dict[str, str]:
        return {
            str(f.relative_to(directory)): f.read_text(encoding="utf-8")
            for f in sorted(directory.rglob("*"))
            if f.is_file()
        }

    claude_before = collect_file_contents(claude_agents)
    codex_before = collect_file_contents(codex_agents)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    claude_after = collect_file_contents(claude_agents)
    codex_after = collect_file_contents(codex_agents)

    assert claude_after == claude_before, (
        "Claude agent scaffold changed on second run — generator is not idempotent"
    )
    assert codex_after == codex_before, (
        "Codex agent scaffold changed on second run — generator is not idempotent"
    )


def test_sync_script_does_not_modify_sources_directory(tmp_path: Path) -> None:
    """AC-5: Running the generator must not modify source files."""
    repo = _setup_fake_repo(tmp_path)

    sources_dir = repo / "cli" / "src" / "ai_team" / "init" / "sources" / "agents"

    def collect_file_contents(directory: Path) -> dict[str, str]:
        return {
            str(f.relative_to(directory)): f.read_text(encoding="utf-8")
            for f in sorted(directory.rglob("*"))
            if f.is_file()
        }

    sources_before = collect_file_contents(sources_dir)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    sources_after = collect_file_contents(sources_dir)

    assert sources_after == sources_before, (
        "Generator modified source files — sources must remain unchanged"
    )


def test_package_owned_agent_sources_cover_each_exported_role_for_both_tools() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sources_root = repo_root / "src" / "ai_team" / "init" / "sources" / "agents"
    claude_source_root = sources_root / "claude"
    codex_source_root = sources_root / "codex"
    claude_scaffold_root = (
        repo_root / "src" / "ai_team" / "init" / "scaffolds" / "claude" / "agents"
    )
    codex_scaffold_root = (
        repo_root / "src" / "ai_team" / "init" / "scaffolds" / "codex" / "agents"
    )

    expected_roles = sorted(path.stem for path in claude_scaffold_root.glob("*.md"))
    claude_source_roles = sorted(path.stem for path in claude_source_root.glob("*.md"))
    codex_source_roles = sorted(path.stem for path in codex_source_root.glob("*.toml"))

    assert claude_source_roles == expected_roles
    assert codex_source_roles == expected_roles

    for role_name in expected_roles:
        claude_source = claude_source_root / f"{role_name}.md"
        codex_source = codex_source_root / f"{role_name}.toml"
        claude_scaffold = claude_scaffold_root / f"{role_name}.md"
        codex_scaffold = codex_scaffold_root / f"{role_name}.toml"

        assert claude_source.read_text(encoding="utf-8") == claude_scaffold.read_text(
            encoding="utf-8"
        )
        assert codex_source.read_text(encoding="utf-8") == codex_scaffold.read_text(
            encoding="utf-8"
        )


def _spec_breakdown_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "skills"
        / "spec-breakdown"
        / "body.md"
    ).read_text(encoding="utf-8")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "spec-breakdown"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    codex = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "skills"
        / "spec-breakdown"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude, codex


def test_spec_breakdown_skill_requires_docs_planning_during_task_creation() -> None:
    source, claude, codex = _spec_breakdown_skill_texts()
    required_phrases = (
        "consider documentation updates as implementation work derived from the approved spec",
        "not as a prerequisite before creating tasks",
    )

    for phrase in required_phrases:
        assert phrase in source, f"spec-breakdown source must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"
