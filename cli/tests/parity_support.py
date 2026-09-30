"""Shared machinery for the parity fixtures (S-005 Component 5, ADR-004).

Used by the pytest runner and by ``scripts/seed_parity_fixture.py``. The format
is documented in ``fixtures/parity/README.md``.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path, PurePosixPath
from typing import Any

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures" / "parity"
LOCK_SENTINELS_FILE = "lock-sentinels.json"
CASE_FILE = "case.json"
PROJECT_DIR_PLACEHOLDER = "<project_dir>"

TreeEntry = dict[str, str]


def serialize_tree(root: Path) -> list[TreeEntry]:
    """Return a manifest of every directory and file under *root*, sorted by path."""
    entries: list[TreeEntry] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported in fixture trees: {path}")
        if path.is_dir():
            entries.append({"path": relative, "type": "dir"})
            continue
        data = path.read_bytes()
        try:
            entries.append({"path": relative, "type": "file", "text": data.decode()})
        except UnicodeDecodeError:
            encoded = base64.b64encode(data).decode("ascii")
            entries.append({"path": relative, "type": "file", "base64": encoded})
    return sorted(entries, key=lambda entry: entry["path"])


def _safe_destination(target: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise ValueError(f"Unsafe path in tree manifest: {relative}")
    return target.joinpath(*pure.parts)


def materialize_tree(manifest: list[TreeEntry], target: Path) -> None:
    """Create *target* and write every manifest entry under it, byte for byte."""
    target.mkdir(parents=True, exist_ok=True)
    for entry in manifest:
        destination = _safe_destination(target, entry["path"])
        if entry["type"] == "dir":
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if "base64" in entry:
            destination.write_bytes(base64.b64decode(entry["base64"]))
        else:
            destination.write_bytes(entry["text"].encode())


def load_lock_exclusions(fixtures_root: Path) -> list[str]:
    """Return the after-tree lock paths from the machine-readable sentinel file."""
    data = json.loads((fixtures_root / LOCK_SENTINELS_FILE).read_text("utf-8"))
    return list(data["after_tree_excluded_paths"])


def exclude_lock_paths(
    manifest: list[TreeEntry], project_dir: str, exclusions: list[str]
) -> list[TreeEntry]:
    """Drop the literal lock paths (and anything beneath them) from *manifest*."""
    literals = [
        entry.replace(PROJECT_DIR_PLACEHOLDER, project_dir) for entry in exclusions
    ]
    return [
        entry
        for entry in manifest
        if not any(
            entry["path"] == literal or entry["path"].startswith(literal + "/")
            for literal in literals
        )
    ]


def discover_cases(fixtures_root: Path) -> list[Path]:
    """Return every case directory under *fixtures_root*, sorted by name."""
    return sorted(
        path
        for path in fixtures_root.iterdir()
        if path.is_dir() and (path / CASE_FILE).is_file()
    )
