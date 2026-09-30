"""Tests for package-owned init scaffold source generation."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from tests.skill_rendering import rendered_skill_body, rendered_skill_header


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

    # Package-owned project guidance source fixtures.
    _write(
        repo / "cli" / "src" / "ai_team" / "init" / "sources" / "project" / "CLAUDE.md",
        "# Project Guidance\n\nspecs tasks bugs decisions reports project-local docs\n",
    )
    _write(
        repo / "cli" / "src" / "ai_team" / "init" / "sources" / "project" / "AGENTS.md",
        "# Project Guidance for Agents\n\nspecs tasks bugs decisions reports project-local docs\n",
    )
    _write(
        repo
        / "cli"
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "project"
        / ".gitignore",
        ".ai-team.lock\n.ai-team-ts.lock\n",
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
    shutil.copy2(
        script.with_name("skill_markers.py"),
        copied_script.with_name("skill_markers.py"),
    )
    _write(
        repo / "cli" / "src" / "ai_team" / "init" / "sources" / "command_map.json",
        '{"commands": [{"command": "status", "positionals": [], "flags": []}]}\n',
    )

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
        Path("change-requests/.gitkeep"),
        Path("decisions/.gitkeep"),
        Path("docs/.gitkeep"),
        Path("CLAUDE.md"),
        Path("AGENTS.md"),
        Path(".gitignore"),
    }
    actual_files = {
        (Path(root) / file_name).relative_to(project_root)
        for root, _, file_names in os.walk(project_root)
        for file_name in file_names
    }

    assert actual_files == expected_files
    assert not (project_root / "old.txt").exists()


def test_sync_script_copies_project_guidance_files_from_source(
    tmp_path: Path,
) -> None:
    """AC-1 & AC-2: Generator copies CLAUDE.md and AGENTS.md from sources/project/."""
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    sources_root = repo / "cli" / "src" / "ai_team" / "init" / "sources" / "project"
    project_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "project"

    for file_name in ("CLAUDE.md", "AGENTS.md"):
        source_text = (sources_root / file_name).read_text(encoding="utf-8")
        scaffold_text = (project_root / file_name).read_text(encoding="utf-8")
        assert scaffold_text == source_text, (
            f"scaffolds/project/{file_name} does not match sources/project/{file_name}"
        )


def test_sync_script_copies_project_gitignore_ignoring_the_lock_sentinel(
    tmp_path: Path,
) -> None:
    """B-017: generator copies project/.gitignore, and it ignores both lock sentinels."""
    repo = _setup_fake_repo(tmp_path)

    subprocess.run(
        [sys.executable, "cli/scripts/sync_init_scaffolds.py"],
        cwd=repo,
        check=True,
    )

    sources_root = repo / "cli" / "src" / "ai_team" / "init" / "sources" / "project"
    project_root = repo / "cli" / "src" / "ai_team" / "init" / "scaffolds" / "project"

    source_text = (sources_root / ".gitignore").read_text(encoding="utf-8")
    scaffold_text = (project_root / ".gitignore").read_text(encoding="utf-8")

    assert scaffold_text == source_text, (
        "scaffolds/project/.gitignore does not match sources/project/.gitignore"
    )
    assert scaffold_text == ".ai-team.lock\n.ai-team-ts.lock\n"


def test_package_owned_project_gitignore_source_ignores_the_lock_sentinel() -> None:
    """B-017: the real (non-fixture) sources/project/.gitignore ships the lock entry."""
    repo_root = Path(__file__).resolve().parents[1]
    source_gitignore = (
        repo_root / "src" / "ai_team" / "init" / "sources" / "project" / ".gitignore"
    )
    scaffold_gitignore = (
        repo_root / "src" / "ai_team" / "init" / "scaffolds" / "project" / ".gitignore"
    )

    assert source_gitignore.is_file(), f"Missing source template: {source_gitignore}"
    assert scaffold_gitignore.is_file(), (
        f"Missing scaffold output: {scaffold_gitignore}"
    )

    source_text = source_gitignore.read_text(encoding="utf-8")
    scaffold_text = scaffold_gitignore.read_text(encoding="utf-8")

    assert source_text == ".ai-team.lock\n.ai-team-ts.lock\n"
    assert scaffold_text == source_text


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

        metadata = tomllib.loads(metadata_files[0].read_text(encoding="utf-8"))

        assert isinstance(metadata.get("claude", {}).get("header"), str)
        assert metadata["claude"]["header"].strip()
        assert isinstance(metadata.get("codex", {}).get("header"), str)
        assert metadata["codex"]["header"].strip()

        scaffold_text = skill_scaffold_path.read_text(encoding="utf-8")
        scaffold_header, scaffold_body = scaffold_text.split("\n\n", maxsplit=1)

        assert rendered_skill_body(skill_name, "claude") == scaffold_body
        assert rendered_skill_header(skill_name, "claude") == scaffold_header.strip()


def test_init_scaffolds_export_change_request_skill_and_project_directory() -> None:
    """Fresh init scaffolds include change-request workflow surfaces."""
    repo_root = Path(__file__).resolve().parents[1]
    source_skill = (
        repo_root / "src" / "ai_team" / "init" / "sources" / "skills" / "change-request"
    )
    scaffold_project = repo_root / "src" / "ai_team" / "init" / "scaffolds" / "project"

    assert (source_skill / "body.md").is_file()
    assert (source_skill / "metadata.toml").is_file()
    assert (scaffold_project / "change-requests" / ".gitkeep").is_file()

    for tool in ("claude", "codex"):
        scaffold_skill = (
            repo_root
            / "src"
            / "ai_team"
            / "init"
            / "scaffolds"
            / tool
            / "skills"
            / "change-request"
            / "SKILL.md"
        )
        assert scaffold_skill.is_file()


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


def test_planner_agents_document_todo_ready_architecture_review_handoff() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    planner_paths = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "agents"
        / "claude"
        / "planner.md",
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "sources"
        / "agents"
        / "codex"
        / "planner.toml",
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "agents"
        / "planner.md",
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "codex"
        / "agents"
        / "planner.toml",
    )
    required_phrases = (
        "human-answerable `[TODO]` markers are resolved and before Gate 1 approval",
        "after it is TODO-free and human-approved but before its amendments are applied",
    )
    forbidden_phrases = (
        "from `new-spec`, before Gate 1",
        "from `change-request`, before its amendments are applied",
    )

    for path in planner_paths:
        text = path.read_text(encoding="utf-8")
        for phrase in required_phrases:
            assert phrase in text, f"{path} must include: {phrase!r}"
        for phrase in forbidden_phrases:
            assert phrase not in text, f"{path} must not include: {phrase!r}"


def test_package_owned_codex_agents_use_supported_role_model_defaults() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sources_root = (
        repo_root / "src" / "ai_team" / "init" / "sources" / "agents" / "codex"
    )
    scaffold_root = (
        repo_root / "src" / "ai_team" / "init" / "scaffolds" / "codex" / "agents"
    )
    expected_models = {
        "architect": "gpt-5.5",
        "planner": "gpt-5.5",
        "developer": "gpt-5.4",
        "reviewer": "gpt-5.4",
        "integrator": "gpt-5.4",
    }

    for role_name, expected_model in expected_models.items():
        source_data = tomllib.loads(
            (sources_root / f"{role_name}.toml").read_text(encoding="utf-8")
        )
        scaffold_data = tomllib.loads(
            (scaffold_root / f"{role_name}.toml").read_text(encoding="utf-8")
        )

        assert source_data["model"] == expected_model
        assert scaffold_data["model"] == expected_model
        assert source_data["model"] != "gpt-5.3-codex"
        assert scaffold_data["model"] != "gpt-5.3-codex"
        assert source_data["model_reasoning_effort"] == "high"
        assert scaffold_data["model_reasoning_effort"] == "high"
        assert scaffold_data == source_data


def _spec_breakdown_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("spec-breakdown")
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


def _spec_breakdown_review_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("spec-breakdown-review")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "spec-breakdown-review"
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
        / "spec-breakdown-review"
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


def test_spec_breakdown_skill_covers_test_planning_and_optional_omission() -> None:
    source, claude, codex = _spec_breakdown_skill_texts()
    required_phrases = (
        "consider test updates and verification changes as implementation work derived from the approved spec",
        "If documentation or test updates are not needed, omit them without placeholder tasks",
    )

    for phrase in required_phrases:
        assert phrase in source, f"spec-breakdown source must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_spec_breakdown_review_focuses_gate_2_on_technical_readiness() -> None:
    source, claude, codex = _spec_breakdown_review_skill_texts()
    required_phrases = (
        "focus findings only on technical task-plan readiness",
        "Do not fail Gate 2 for product-scope concerns that do not block technical readiness",
        "if the plan contradicts the approved spec or existing ADRs",
    )

    for phrase in required_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_spec_breakdown_review_preserves_existing_output_format_and_verdicts() -> None:
    source, claude, codex = _spec_breakdown_review_skill_texts()
    required_phrases = (
        "Result: PASS | FAIL | BLOCKED | ESCALATE",
        "Spec reviewed: project/specs/<file>",
        "Tasks reviewed: <count>",
        "Next owner:",
    )

    for phrase in required_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def _dev_loop_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("dev-loop")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "dev-loop"
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
        / "dev-loop"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude, codex


def test_dev_loop_uses_cli_task_state_filter_for_queue_discovery() -> None:
    """AC-1: Queue discovery uses ai-team list tasks --state pending, not raw filesystem."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = ("ai-team list tasks --state pending",)

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_discovers_baseline_test_command_before_claiming_task() -> None:
    """AC-2: Loop reads project guidance before claiming a task."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = (
        "baseline test command",
        "project-specific guidance",
        "CLAUDE.md",
        "AGENTS.md",
        "project/docs/coding_guidelines.md",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_allows_loop_to_continue_when_baseline_tests_pass() -> None:
    """AC-3: Loop continues to task selection when baseline test command passes."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = ("baseline test command passes",)

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_asks_user_when_baseline_test_command_missing_or_ambiguous() -> None:
    """AC-4 / F-3: Loop asks for clarification on missing or ambiguous commands."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = (
        "ask the human for one of these before claiming a task",
        "BLOCKED: no automated baseline test command is documented."
        " Provide the command to run, or confirm that this project has no automated baseline test.",
        "BLOCKED: multiple plausible baseline test commands are documented."
        " Confirm which command the loop should run before claiming tasks.",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_baseline_guard_defines_flexible_discovery_order() -> None:
    """F-1: Step 2 defines a flexible project guidance discovery order."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = (
        "Read root project guidance files that exist",
        "Read any project-local docs referenced by those files",
        "Read common project documentation or configuration files",
        "Prefer an explicitly documented test command",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_baseline_guard_handles_projects_without_automated_tests() -> None:
    """F-1: Step 2 can proceed with explicit no-automated-test confirmation."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = (
        "If the human confirms that no automated baseline test is available",
        "record that confirmation in the loop summary",
        "continue to Step 3 without running a baseline command",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_baseline_guard_does_not_restore_rigid_root_claude_policy() -> None:
    """F-2: Step 2 must not restore the rigid root-CLAUDE-only policy."""
    source, claude, codex = _dev_loop_skill_texts()
    forbidden_phrases = (
        "ONLY from the root `CLAUDE.md`",
        "exactly one fenced command block",
        "BLOCKED: root CLAUDE.md",
    )

    for phrase in forbidden_phrases:
        assert phrase not in source, f"dev-loop body.md must not include: {phrase!r}"
        assert phrase not in claude, f"Claude scaffold must not include: {phrase!r}"
        assert phrase not in codex, f"Codex scaffold must not include: {phrase!r}"


def test_dev_loop_baseline_guard_runs_once_at_startup_only() -> None:
    """F-4: Step 2 states the guard runs once at startup, not between tasks, with rationale."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = (
        "The baseline guard runs once at loop startup."
        " It is NOT re-checked between tasks.",
    )

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_dev_loop_stops_and_reports_when_baseline_tests_fail() -> None:
    """AC-5: Loop stops and reports failing command and output when baseline tests fail."""
    source, claude, codex = _dev_loop_skill_texts()
    required_phrases = ("baseline test command fails",)

    for phrase in required_phrases:
        assert phrase in source, f"dev-loop body.md must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_project_guidance_sources_exist_and_describe_project_artifact_folders() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    source_root = repo_root / "src" / "ai_team" / "init" / "sources" / "project"
    required_terms = (
        "specs",
        "tasks",
        "bugs",
        "decisions",
        "reports",
        "project-local docs",
    )

    for guidance_file_name in ("CLAUDE.md", "AGENTS.md"):
        guidance_path = source_root / guidance_file_name
        assert guidance_path.is_file(), f"Missing source template: {guidance_path}"

        guidance_text = guidance_path.read_text(encoding="utf-8")
        for term in required_terms:
            assert term in guidance_text, (
                f"{guidance_file_name} must describe {term!r} in project guidance"
            )


def _new_task_skill_texts() -> tuple[str, str, str]:
    repo_root = Path(__file__).resolve().parents[1]
    source = rendered_skill_body("new-task")
    claude = (
        repo_root
        / "src"
        / "ai_team"
        / "init"
        / "scaffolds"
        / "claude"
        / "skills"
        / "new-task"
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
        / "new-task"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    return source, claude, codex


# AC-1: ownership boundaries


def test_spec_breakdown_states_plan_coverage_ownership_boundary() -> None:
    """AC-1: spec-breakdown body states it owns plan coverage, dependencies, task boundaries."""
    source, claude, codex = _spec_breakdown_skill_texts()
    required_phrases = (
        "spec-breakdown owns",
        "new-task",
    )

    for phrase in required_phrases:
        assert phrase in source, f"spec-breakdown source must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_new_task_states_per_task_shape_ownership_boundary() -> None:
    """AC-1: new-task body states it owns per-task shape and references spec-breakdown for plan-level rules."""
    source, claude, codex = _new_task_skill_texts()
    required_phrases = (
        "enforces per-task shape",
        "spec-breakdown",
        "new-task owns",
    )

    for phrase in required_phrases:
        assert phrase in source, f"new-task source must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_spec_breakdown_review_states_gate_2_technical_readiness_ownership_boundary() -> (
    None
):
    """AC-1: spec-breakdown-review body states it owns Gate 2 technical readiness."""
    source, claude, codex = _spec_breakdown_review_skill_texts()
    required_phrases = (
        "spec-breakdown-review owns",
        "Gate 2 technical readiness",
    )

    for phrase in required_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-2: EARS references point to task template, not "the new-task skill"


def test_spec_breakdown_ears_reference_points_to_task_template_not_new_task_skill() -> (
    None
):
    """AC-2: spec-breakdown EARS reference uses task template path, not 'the new-task skill'."""
    source, claude, codex = _spec_breakdown_skill_texts()

    task_template_phrases = ("task template", "templates/task")
    forbidden_phrase = "documented in the new-task skill"

    for phrase in task_template_phrases:
        assert phrase in source, f"spec-breakdown source must include: {phrase!r}"
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"

    assert forbidden_phrase not in source, (
        f"spec-breakdown source must not include: {forbidden_phrase!r}"
    )
    assert forbidden_phrase not in claude, (
        f"Claude scaffold must not include: {forbidden_phrase!r}"
    )
    assert forbidden_phrase not in codex, (
        f"Codex scaffold must not include: {forbidden_phrase!r}"
    )


def test_spec_breakdown_review_ears_reference_points_to_task_template_not_new_task_skill() -> (
    None
):
    """AC-2: spec-breakdown-review EARS reference uses task template path, not 'the new-task skill'."""
    source, claude, codex = _spec_breakdown_review_skill_texts()

    task_template_phrases = ("task template", "templates/task")

    for phrase in task_template_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-3: Gate 2 output section states architect role envelope wraps Findings block


def test_spec_breakdown_review_output_states_architect_envelope_wraps_findings_block() -> (
    None
):
    """AC-3: spec-breakdown-review output section states architect role envelope wraps Findings block."""
    source, claude, codex = _spec_breakdown_review_skill_texts()
    required_phrases = (
        "architect",
        "envelope",
        "Findings",
    )

    for phrase in required_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_spec_breakdown_review_output_does_not_duplicate_result_summary_fields() -> (
    None
):
    """AC-3: spec-breakdown-review output section states no duplicated Result/Summary fields."""
    source, claude, codex = _spec_breakdown_review_skill_texts()
    required_phrases = (
        "no duplicated Result",
        "Result/Summary",
    )

    for phrase in required_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


# AC-4: spec-coverage check appears before dependency and file-conflict checks


def test_spec_breakdown_review_includes_spec_coverage_check() -> None:
    """AC-4: spec-breakdown-review body includes a spec-coverage check (plan covers the whole spec)."""
    source, claude, codex = _spec_breakdown_review_skill_texts()
    required_phrases = (
        "spec coverage",
        "covers the",
    )

    for phrase in required_phrases:
        assert phrase in source, (
            f"spec-breakdown-review source must include: {phrase!r}"
        )
        assert phrase in claude, f"Claude scaffold must include: {phrase!r}"
        assert phrase in codex, f"Codex scaffold must include: {phrase!r}"


def test_spec_breakdown_review_spec_coverage_check_precedes_dependency_and_conflict_checks() -> (
    None
):
    """AC-4: spec-coverage check appears before dependency check and file-conflict check."""
    source, _claude, _codex = _spec_breakdown_review_skill_texts()

    coverage_markers = ("spec coverage", "covers the")
    dependency_marker = "Check Dependency"
    conflict_marker = "Check File Conflict"

    coverage_pos = min(source.index(m) for m in coverage_markers if m in source)
    assert dependency_marker in source, (
        f"spec-breakdown-review source must include: {dependency_marker!r}"
    )
    assert conflict_marker in source, (
        f"spec-breakdown-review source must include: {conflict_marker!r}"
    )

    dep_pos = source.index(dependency_marker)
    conflict_pos = source.index(conflict_marker)

    assert coverage_pos < dep_pos, (
        "Spec-coverage check must appear before dependency check in spec-breakdown-review"
    )
    assert coverage_pos < conflict_pos, (
        "Spec-coverage check must appear before file-conflict check in spec-breakdown-review"
    )
