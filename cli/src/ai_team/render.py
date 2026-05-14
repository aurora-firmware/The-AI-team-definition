"""Shared Rich console and JSON output helpers for the ai-team CLI."""

import json
import sys

from rich.console import Console

# Single console instance used across the entire CLI.
console = Console()


def print_json(obj: object) -> None:
    """Serialise *obj* to JSON and write it to stdout followed by a newline."""
    sys.stdout.write(json.dumps(obj, default=str) + "\n")
