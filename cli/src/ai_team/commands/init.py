"""`ai-team init` command for scaffolding a fresh repository."""

from __future__ import annotations

import importlib.metadata
import importlib.resources as resources
import shutil
from pathlib import Path

import tomli_w
import typer

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


def _next_steps() -> list[str]:
    return [
        "Run /brainstorm to explore the request and constraints.",
        "Run /write-plan to break the spec into tasks.",
        "Run /dev-loop to execute tasks through review and integration.",
    ]


def _copy_root_guidance_file(
    source: Path,
    destination: Path,
    force: bool,
) -> None:
    """Copy a single root guidance file; overwrite only when *force* is True."""
    if destination.exists() and not force:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _handle_root_guidance(
    target_root: Path,
    sources_root: Path,
    no_interactive: bool,
    create_root_guidance: bool,
    force: bool,
    dry_run: bool,
) -> bool:
    """Prompt for or create root guidance files.  Returns True if any file was declined."""
    declined = False

    for filename in _ROOT_GUIDANCE_FILES:
        destination = target_root / filename
        source = sources_root / "root" / filename

        # AC-5: never replace an existing file unless force is active
        if destination.exists() and not force:
            continue

        if dry_run:
            typer.echo(f"WOULD WRITE: {destination}")
            continue

        if no_interactive:
            # AC-3: deterministic — only create when the flag is set
            if create_root_guidance:
                _copy_root_guidance_file(source, destination, force)
        else:
            # AC-1 / AC-2: interactive — ask the user
            create = typer.confirm(
                f"Create root {filename} from the starter template?",
                default=True,
            )
            if create:
                _copy_root_guidance_file(source, destination, force)
            else:
                declined = True

    return declined


@app.callback()
def init_command(
    path: Path = typer.Argument(Path(".")),
    tools: str | None = typer.Option(None, "--tools"),
    force: bool = typer.Option(False, "--force"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    no_interactive: bool = typer.Option(False, "--no-interactive"),
    create_root_guidance: bool = typer.Option(False, "--create-root-guidance"),
) -> None:
    """Initialize scaffold files in *path*."""
    try:
        selected_tools = _resolve_tools(tools, no_interactive)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    target_root = path.resolve()

    scaffolds = resources.files("ai_team.init") / "scaffolds"
    sources = resources.files("ai_team.init") / "sources"
    with (
        resources.as_file(scaffolds) as scaffolds_path,
        resources.as_file(sources) as sources_path,
    ):
        planned: list[tuple[Path, Path]] = []
        planned.extend(
            _plan_copies(scaffolds_path / "project", target_root / "project")
        )

        if "claude" in selected_tools:
            planned.extend(
                _plan_copies(scaffolds_path / "claude", target_root / ".claude")
            )

        if "codex" in selected_tools:
            planned.extend(
                _plan_copies(scaffolds_path / "codex", target_root / ".codex")
            )

        marker = target_root / ".ai-team.toml"
        planned_destinations = [destination for _, destination in planned] + [marker]
        collisions = [
            destination for destination in planned_destinations if destination.exists()
        ]

        if dry_run:
            for destination in planned_destinations:
                typer.echo(f"WOULD WRITE: {destination}")
            # Also show root guidance would-write entries in dry-run
            _handle_root_guidance(
                target_root,
                sources_path,
                no_interactive,
                create_root_guidance,
                force,
                dry_run=True,
            )

        if collisions and not force:
            typer.echo(
                "Refusing to overwrite existing files without --force:\n"
                + "\n".join(str(path) for path in collisions),
                err=True,
            )
            raise typer.Exit(code=1)

        if dry_run:
            return

        for source, destination in planned:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        marker_data = {
            "project": {"dir": "project"},
            "init": {
                "tools": selected_tools,
                "framework_version": importlib.metadata.version("ai-team"),
            },
        }
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(tomli_w.dumps(marker_data), encoding="utf-8")

        # Handle root guidance files (outside the collision-checked scaffold set)
        declined = _handle_root_guidance(
            target_root,
            sources_path,
            no_interactive,
            create_root_guidance,
            force,
            dry_run=False,
        )

    typer.echo("Initialization complete.")
    typer.echo("Next steps:")
    for line in _next_steps():
        typer.echo(f"- {line}")

    if declined:
        typer.echo(f"\nNote: {_ROOT_GUIDANCE_DECLINED_MESSAGE}")
