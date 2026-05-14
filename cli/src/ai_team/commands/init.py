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


@app.callback()
def init_command(
    path: Path = typer.Argument(Path(".")),
    tools: str | None = typer.Option(None, "--tools"),
    include_ai_process: bool = typer.Option(False, "--include-ai-process"),
    force: bool = typer.Option(False, "--force"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    no_interactive: bool = typer.Option(False, "--no-interactive"),
) -> None:
    """Initialize scaffold files in *path*."""
    try:
        selected_tools = _resolve_tools(tools, no_interactive)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    if not no_interactive and tools is None and not include_ai_process:
        include_ai_process = typer.confirm(
            "Include ai-process snapshot?", default=False
        )

    target_root = path.resolve()

    scaffolds = resources.files("ai_team.init") / "scaffolds"
    with resources.as_file(scaffolds) as scaffolds_path:
        planned: list[tuple[Path, Path]] = []
        planned.extend(
            _plan_copies(scaffolds_path / "project", target_root / "project")
        )

        if "claude" in selected_tools:
            planned.extend(
                _plan_copies(scaffolds_path / "claude", target_root / ".claude")
            )

        if include_ai_process:
            planned.extend(
                _plan_copies(scaffolds_path / "ai-process", target_root / "ai-process")
            )

    marker = target_root / ".ai-team.toml"
    planned_destinations = [destination for _, destination in planned] + [marker]
    collisions = [
        destination for destination in planned_destinations if destination.exists()
    ]

    if dry_run:
        for destination in planned_destinations:
            typer.echo(f"WOULD WRITE: {destination}")

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
            "include_ai_process": include_ai_process,
            "framework_version": importlib.metadata.version("ai-team"),
        },
    }
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(tomli_w.dumps(marker_data), encoding="utf-8")

    typer.echo("Initialization complete.")
    typer.echo("Next steps:")
    for line in _next_steps():
        typer.echo(f"- {line}")
