"""`ai-team init` command for scaffolding a fresh repository."""

from __future__ import annotations

import importlib.resources as resources
import shutil
from collections.abc import Callable
from pathlib import Path

import tomli_w
import typer

from ai_team.core.result import Result
from ai_team.core.runtime import framework_version

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
    create_root_guidance: bool,
    force: bool,
    dry_run: bool,
    confirm_root_guidance: Callable[[str], bool] | None,
) -> list[dict[str, str]]:
    """Create root guidance files and report one outcome per file.

    Outcomes: ``exists`` (kept), ``would-write`` (dry run), ``created``,
    ``declined`` (the confirm callback said no) and ``not-requested``.
    """
    outcomes: list[dict[str, str]] = []

    for filename in _ROOT_GUIDANCE_FILES:
        destination = target_root / filename
        source = sources_root / "root" / filename

        if destination.exists() and not force:
            outcome = "exists"
        elif dry_run:
            outcome = "would-write"
        elif confirm_root_guidance is not None:
            if confirm_root_guidance(filename):
                _copy_root_guidance_file(source, destination, force)
                outcome = "created"
            else:
                outcome = "declined"
        elif create_root_guidance:
            _copy_root_guidance_file(source, destination, force)
            outcome = "created"
        else:
            outcome = "not-requested"

        outcomes.append({"path": str(destination), "outcome": outcome})

    return outcomes


def init_repository(
    path: Path,
    tools: list[str],
    force: bool,
    dry_run: bool,
    create_root_guidance: bool,
    confirm_root_guidance: Callable[[str], bool] | None = None,
) -> Result:
    """Scaffold *path* for the explicit (possibly empty) *tools* list.

    Never prompts on its own: root guidance is created when
    *create_root_guidance* is set, or decided per file by the optional
    *confirm_root_guidance* callback. The payload lists the written (or, for a
    dry run, planned) files and the root-guidance outcome per file.
    """
    unsupported = [name for name in tools if name not in _SUPPORTED_TOOLS]
    if unsupported:
        return Result(
            status=1,
            message=(
                f"Unsupported tool '{unsupported[0]}'. Supported values: "
                + ", ".join(_SUPPORTED_TOOLS)
            ),
        )

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

        if "claude" in tools:
            planned.extend(
                _plan_copies(scaffolds_path / "claude", target_root / ".claude")
            )

        if "codex" in tools:
            planned.extend(
                _plan_copies(scaffolds_path / "codex", target_root / ".codex")
            )

        marker = target_root / ".ai-team.toml"
        planned_destinations = [destination for _, destination in planned] + [marker]
        collisions = [
            destination for destination in planned_destinations if destination.exists()
        ]
        files = [str(destination) for destination in planned_destinations]

        if dry_run:
            root_guidance = _handle_root_guidance(
                target_root,
                sources_path,
                create_root_guidance,
                force,
                dry_run=True,
                confirm_root_guidance=None,
            )
            payload = {"files": files, "dry_run": True, "root_guidance": root_guidance}
        else:
            payload = None

        if collisions and not force:
            return Result(
                status=1,
                payload=payload,
                message=(
                    "Refusing to overwrite existing files without --force:\n"
                    + "\n".join(str(collision) for collision in collisions)
                ),
            )

        if payload is not None:
            return Result(status=0, payload=payload)

        for source, destination in planned:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        marker_data = {
            "project": {"dir": "project"},
            "init": {
                "tools": tools,
                "framework_version": framework_version(),
            },
        }
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(tomli_w.dumps(marker_data), encoding="utf-8")

        # Root guidance files sit outside the collision-checked scaffold set.
        root_guidance = _handle_root_guidance(
            target_root,
            sources_path,
            create_root_guidance,
            force,
            dry_run=False,
            confirm_root_guidance=confirm_root_guidance,
        )

    return Result(
        status=0,
        payload={"files": files, "dry_run": False, "root_guidance": root_guidance},
    )


def _confirm_root_guidance(filename: str) -> bool:
    return typer.confirm(
        f"Create root {filename} from the starter template?",
        default=True,
    )


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

    result = init_repository(
        path,
        selected_tools,
        force,
        dry_run,
        create_root_guidance,
        confirm_root_guidance=None if no_interactive else _confirm_root_guidance,
    )

    if dry_run and result.payload is not None:
        for destination in result.payload["files"]:
            typer.echo(f"WOULD WRITE: {destination}")
        for entry in result.payload["root_guidance"]:
            if entry["outcome"] == "would-write":
                typer.echo(f"WOULD WRITE: {entry['path']}")

    if result.status != 0:
        typer.echo(result.text(), err=True)
        raise typer.Exit(code=result.status)

    if dry_run:
        return

    typer.echo("Initialization complete.")
    typer.echo("Next steps:")
    for line in _next_steps():
        typer.echo(f"- {line}")

    declined = any(
        entry["outcome"] == "declined" for entry in result.payload["root_guidance"]
    )
    if declined:
        typer.echo(f"\nNote: {_ROOT_GUIDANCE_DECLINED_MESSAGE}")
