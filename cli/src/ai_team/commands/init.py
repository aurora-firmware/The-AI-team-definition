"""`ai-team init` command for scaffolding a fresh repository."""

from __future__ import annotations

import importlib.metadata
import importlib.resources as resources
import shutil
from pathlib import Path

import tomli_w
import typer

from ai_team.core.config import (
    DEFAULT_INTEGRATION_BRANCH,
    is_valid_branch_name,
    is_valid_project_dir,
    marker_integration_branch,
    marker_project_dir,
    read_marker,
    render_placeholders,
)
from ai_team.core.locator import DEFAULT_PROJECT_DIR
from ai_team.core.tool_paths import TOOL_EXPORT_PATHS
from ai_team.core.tracker import DEFAULT_TRACKER_DIR, resolve_tracker_dir

NAME = "init"
app = typer.Typer(
    help="Scaffold an AI-team repository.",
    invoke_without_command=True,
    context_settings={"allow_interspersed_args": True},
)

_SUPPORTED_TOOLS = ["claude", "codex"]

_ROOT_GUIDANCE_FILES = ["CLAUDE.md", "AGENTS.md"]

_ROOT_GUIDANCE_DECLINED_MESSAGE = (
    "To help agents run your project without guessing, add your test and run "
    "commands to a root CLAUDE.md and AGENTS.md. "
    "See `ai-team init --create-root-guidance` to generate starter templates."
)


def _iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def _tracker_ignore_rule(tracker_dir: str) -> str | None:
    """Return the root ``.gitignore`` rule for the configured tracker folder.

    The default folder keeps its historical rule (the whole ``/.ai-team/``
    folder); any other relative folder is ignored by its full path. Absolute
    and ``~`` paths live outside the repository and need no rule.
    """
    configured = Path(tracker_dir).expanduser()
    if configured.is_absolute():
        return None
    if tracker_dir == DEFAULT_TRACKER_DIR:
        return f"/{Path(DEFAULT_TRACKER_DIR).parts[0]}/"
    return f"/{configured.as_posix().strip('/')}/"


def _plan_copies(source: Path, destination: Path) -> list[tuple[Path, Path]]:
    return [
        (path, destination / path.relative_to(source)) for path in _iter_files(source)
    ]


def _parse_tools(value: str) -> list[str]:
    token = value.strip().lower()
    if token == "all":
        return _SUPPORTED_TOOLS[:]
    if token == "none":
        return []

    result: list[str] = []
    for chunk in token.split(","):
        name = chunk.strip().lower()
        if not name:
            continue
        if name not in _SUPPORTED_TOOLS:
            raise ValueError(
                f"Unsupported tool '{name}'. Supported values: "
                + ", ".join(_SUPPORTED_TOOLS + ["all", "none"])
            )
        if name not in result:
            result.append(name)
    return result


def _resolve_tools(tools: str | None, no_interactive: bool) -> list[str]:
    if tools is not None:
        return _parse_tools(tools)
    if no_interactive:
        raise ValueError("When --no-interactive is set, you must provide --tools.")

    raw = typer.prompt(
        "Select tools (comma-separated, all, none)",
        default="claude",
    )
    return _parse_tools(raw)


def _skill_invocation(skill: str, tools: list[str]) -> str:
    """Return how to invoke ``skill`` in the configured tools.

    Claude Code runs a skill as ``/name``; Codex has no per-skill slash command
    and runs it as ``$name``. With no tool configured, keep the ``/name`` form.
    """
    if tools == ["codex"]:
        return f"${skill}"
    if "claude" in tools and "codex" in tools:
        return f"/{skill} (Claude Code) or ${skill} (Codex)"
    return f"/{skill}"


def _next_steps(tools: list[str]) -> list[str]:
    return [
        f"Run {_skill_invocation('brainstorm', tools)} to explore the request and constraints.",
        f"Run {_skill_invocation('spec-breakdown', tools)} to break the approved spec into tasks.",
        f"Run {_skill_invocation('dev-loop', tools)} to execute tasks through review and integration.",
    ]


def _ensure_tracker(target_root: Path, tracker_dir: str, dry_run: bool) -> None:
    """Create the configured tracker folder and make git ignore it (spec S-006).

    The folder is the one every tracker command resolves, so in a linked
    worktree it is created in the main working tree.

    The ignore rule is appended to the repository's root ``.gitignore`` only when
    no identical line exists, so re-running ``init`` never duplicates or removes
    rules.
    """
    tracker = resolve_tracker_dir(target_root)
    ignore_rule = _tracker_ignore_rule(tracker_dir)
    gitignore = target_root / ".gitignore"
    existing = (
        gitignore.read_text(encoding="utf-8").splitlines()
        if gitignore.is_file()
        else []
    )
    needs_rule = ignore_rule is not None and ignore_rule not in (
        line.strip() for line in existing
    )

    if dry_run:
        if not tracker.exists():
            typer.echo(f"WOULD CREATE: {tracker}")
        if needs_rule:
            typer.echo(f"WOULD UPDATE: {gitignore}")
        return

    tracker.mkdir(parents=True, exist_ok=True)
    if needs_rule:
        prefix = ""
        if existing:
            text = gitignore.read_text(encoding="utf-8")
            prefix = "" if text.endswith("\n") else "\n"
            prefix += "\n"
        with gitignore.open("a", encoding="utf-8") as stream:
            stream.write(
                f"{prefix}# ai-team local work-item tracker (tasks, bugs, change-requests)\n"
                f"{ignore_rule}\n"
            )


def _write_rendered(source: Path, destination: Path, settings: dict[str, str]) -> None:
    """Copy *source* to *destination*, filling the packaged-source placeholders.

    Reports ``OVERWROTE: <path>`` once the write succeeds when *destination*
    already existed.
    """
    existed = destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = render_placeholders(source.read_text(encoding="utf-8"), **settings)
    destination.write_text(text, encoding="utf-8")
    shutil.copymode(source, destination)
    if existed:
        _report_overwrite(destination)


def _report_overwrite(destination: Path) -> None:
    typer.echo(f"OVERWROTE: {destination}")


def _copy_root_guidance_file(
    source: Path,
    destination: Path,
    force: bool,
    settings: dict[str, str],
) -> None:
    """Copy a single root guidance file; overwrite only when *force* is True."""
    if destination.exists() and not force:
        return
    _write_rendered(source, destination, settings)


def _root_guidance_action(
    destination: Path,
    force: bool,
    create_root_guidance: bool,
    no_interactive: bool,
) -> str:
    """Decide what ``init`` does with one root guidance file.

    Returns ``"skip"``, ``"write"`` or ``"prompt"``. The real run and the dry
    run both use this, so the dry run cannot disagree with the real run.
    """
    if destination.exists() and not force:
        return "skip"
    if create_root_guidance:
        return "write"
    if no_interactive:
        return "skip"
    return "prompt"


def _handle_root_guidance(
    target_root: Path,
    sources_root: Path,
    no_interactive: bool,
    create_root_guidance: bool,
    force: bool,
    dry_run: bool,
    settings: dict[str, str],
) -> bool:
    """Prompt for or create root guidance files.  Returns True if any file was declined."""
    declined = False

    for filename in _ROOT_GUIDANCE_FILES:
        destination = target_root / filename
        source = sources_root / "root" / filename
        action = _root_guidance_action(
            destination, force, create_root_guidance, no_interactive
        )

        if dry_run:
            if action == "write":
                typer.echo(f"{_would_write_verb(destination, force)}: {destination}")
            elif action == "prompt":
                typer.echo(f"WOULD PROMPT: {destination}")
        elif action == "write":
            _copy_root_guidance_file(source, destination, force, settings)
        elif action == "prompt":
            create = typer.confirm(
                f"Create root {filename} from the starter template?",
                default=True,
            )
            if create:
                _copy_root_guidance_file(source, destination, force, settings)
            else:
                declined = True

    return declined


def _would_write_verb(destination: Path, force: bool) -> str:
    return "WOULD OVERWRITE" if destination.exists() and force else "WOULD WRITE"


@app.callback()
def init_command(
    path: Path = typer.Argument(Path(".")),
    tools: str | None = typer.Option(None, "--tools"),
    force: bool = typer.Option(False, "--force"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    no_interactive: bool = typer.Option(False, "--no-interactive"),
    create_root_guidance: bool = typer.Option(False, "--create-root-guidance"),
    project_dir: str | None = typer.Option(
        None,
        "--project-dir",
        help="Artifact folder, at any depth (default: the configured one, else 'ai-team').",
    ),
    integration_branch: str | None = typer.Option(
        None,
        "--integration-branch",
        help="Branch work integrates into (default: the configured one, else 'dev-agent').",
    ),
) -> None:
    """Initialize scaffold files in *path*.

    On a repository that already has ``.ai-team.toml``, the configured
    ``[project] dir``, ``[tracker] dir``, and ``[git] integration_branch`` are
    kept, so ``--force`` refreshes generated agents and skills without
    rewriting user configuration.
    """
    try:
        selected_tools = _resolve_tools(tools, no_interactive)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    target_root = path.resolve()
    existing_marker = read_marker(target_root)
    project_dir = (
        project_dir or marker_project_dir(existing_marker) or DEFAULT_PROJECT_DIR
    )
    integration_branch = (
        integration_branch
        or marker_integration_branch(existing_marker)
        or DEFAULT_INTEGRATION_BRANCH
    )
    if not is_valid_project_dir(project_dir):
        typer.echo(
            f"Invalid project dir '{project_dir}': use a relative folder path "
            "inside the repository without '..'.",
            err=True,
        )
        raise typer.Exit(code=1)
    if not is_valid_branch_name(integration_branch):
        typer.echo(f"Invalid integration branch '{integration_branch}'.", err=True)
        raise typer.Exit(code=1)
    settings = {"project_dir": project_dir, "integration_branch": integration_branch}
    tracker_dir = existing_marker.get("tracker", {}).get("dir") or DEFAULT_TRACKER_DIR

    scaffolds = resources.files("ai_team.init") / "scaffolds"
    sources = resources.files("ai_team.init") / "sources"
    with (
        resources.as_file(scaffolds) as scaffolds_path,
        resources.as_file(sources) as sources_path,
    ):
        planned: list[tuple[Path, Path]] = []
        planned.extend(
            _plan_copies(scaffolds_path / "project", target_root / project_dir)
        )

        for tool in selected_tools:
            for scaffold_subfolder, destination in TOOL_EXPORT_PATHS[tool]:
                planned.extend(
                    _plan_copies(
                        scaffolds_path / tool / scaffold_subfolder,
                        target_root / destination,
                    )
                )

        marker = target_root / ".ai-team.toml"
        planned_destinations = [destination for _, destination in planned] + [marker]
        collisions = [
            destination for destination in planned_destinations if destination.exists()
        ]

        if collisions and not force:
            typer.echo(
                "Refusing to overwrite existing files without --force:\n"
                + "\n".join(str(path) for path in collisions),
                err=True,
            )
            raise typer.Exit(code=1)

        if dry_run:
            for destination in planned_destinations:
                typer.echo(f"{_would_write_verb(destination, force)}: {destination}")
            _handle_root_guidance(
                target_root,
                sources_path,
                no_interactive,
                create_root_guidance,
                force,
                dry_run=True,
                settings=settings,
            )
            _ensure_tracker(target_root, tracker_dir, dry_run=True)
            return

        for source, destination in planned:
            _write_rendered(source, destination, settings)

        # Keep every setting the user already configured; only the values this
        # command owns (project, tracker, git, init) are refreshed.
        marker_data = dict(existing_marker)
        marker_data["project"] = {
            **existing_marker.get("project", {}),
            "dir": project_dir,
        }
        marker_data["tracker"] = {
            **existing_marker.get("tracker", {}),
            "dir": tracker_dir,
        }
        marker_data["git"] = {
            **existing_marker.get("git", {}),
            "integration_branch": integration_branch,
        }
        marker_data["init"] = {
            **existing_marker.get("init", {}),
            "tools": selected_tools,
            "framework_version": importlib.metadata.version("ai-team"),
        }
        marker_existed = marker.exists()
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(tomli_w.dumps(marker_data), encoding="utf-8")
        if marker_existed:
            _report_overwrite(marker)
        _ensure_tracker(target_root, tracker_dir, dry_run=False)

        # Handle root guidance files (outside the collision-checked scaffold set)
        declined = _handle_root_guidance(
            target_root,
            sources_path,
            no_interactive,
            create_root_guidance,
            force,
            dry_run=False,
            settings=settings,
        )

    typer.echo("Initialization complete.")
    typer.echo("Next steps:")
    for line in _next_steps(selected_tools):
        typer.echo(f"- {line}")

    if declined:
        typer.echo(f"\nNote: {_ROOT_GUIDANCE_DECLINED_MESSAGE}")
