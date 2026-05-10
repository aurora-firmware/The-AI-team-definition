"""`ai-team init` command for scaffolding a fresh repository."""

from __future__ import annotations

import importlib.metadata
import importlib.resources as resources
import shutil
from pathlib import Path

import tomli_w
import typer

NAME = "init"
app = typer.Typer(help="Scaffold an AI-team repository.", invoke_without_command=True)


def _copy_tree(source: Path, destination: Path) -> None:
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


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
    del force
    del dry_run

    selected_tools = []
    if tools:
        selected_tools = [item.strip() for item in tools.split(",") if item.strip()]

    if not selected_tools and not no_interactive:
        raw = typer.prompt("Select tools (comma-separated, all, none)", default="claude")
        selected_tools = [item.strip() for item in raw.split(",") if item.strip()]

    target_root = path.resolve()

    scaffolds = resources.files("ai_team.init") / "scaffolds"
    with resources.as_file(scaffolds) as scaffolds_path:
        _copy_tree(scaffolds_path / "project", target_root / "project")

        if "claude" in selected_tools:
            _copy_tree(scaffolds_path / "claude", target_root / ".claude")

        if include_ai_process:
            _copy_tree(scaffolds_path / "ai-process", target_root / "ai-process")

    marker_data = {
        "project": {"dir": "project"},
        "init": {
            "tools": selected_tools,
            "include_ai_process": include_ai_process,
            "framework_version": importlib.metadata.version("ai-team"),
        },
    }

    marker = target_root / ".ai-team.toml"
    marker.write_text(tomli_w.dumps(marker_data), encoding="utf-8")

    typer.echo("Initialization complete.")
