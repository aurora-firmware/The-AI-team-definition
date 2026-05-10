"""
ai_team.core.models — dataclasses for AI-team artifact types parsed from YAML frontmatter.

Provides:
  - ``Task``, ``Bug``, ``Spec``, ``Adr`` dataclasses holding frontmatter fields.
  - ``parse_task``, ``parse_bug``, ``parse_spec``, ``parse_adr`` — read an artifact
    file and return the corresponding dataclass.
  - ``dump_frontmatter(model, body) -> str`` — serialise a model back to a complete
    markdown file (YAML frontmatter block + body).
  - ``FrontmatterError`` — raised when a required field is missing or invalid.

This module has no Typer dependency and performs only the I/O needed to read
the supplied path.

``ruamel.yaml`` in round-trip mode (``typ="rt"``) is used throughout so that
comments and key order are preserved when the caller rewrites a file.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------


class FrontmatterError(ValueError):
    """Raised when a frontmatter field is missing or has an invalid value.

    The message always names the problematic field and the source path so
    callers can surface a clear diagnostic.
    """


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_yaml_frontmatter(path: Path) -> dict[str, Any]:
    """Extract the YAML frontmatter block from *path* and return it as a dict.

    Raises
    ------
    FrontmatterError
        If the file does not start with a ``---`` fence or the block is
        syntactically invalid YAML.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise FrontmatterError(
            f"No YAML frontmatter block found in {path!s}"
        )

    # Find the closing --- fence (must be on its own line after the opener).
    rest = text[3:]
    close_idx = rest.find("\n---")
    if close_idx == -1:
        raise FrontmatterError(
            f"Unclosed YAML frontmatter block (missing closing ---) in {path!s}"
        )

    yaml_text = rest[:close_idx]
    yaml = YAML(typ="rt")
    try:
        data = yaml.load(yaml_text)
    except Exception as exc:
        raise FrontmatterError(
            f"YAML parse error in frontmatter of {path!s}: {exc}"
        ) from exc

    if data is None:
        return {}
    return dict(data)


def _require(data: dict[str, Any], key: str, path: Path) -> Any:
    """Return ``data[key]`` or raise :class:`FrontmatterError` naming *key* and *path*.

    The raw YAML key (e.g. ``"assigned-role"``) is used directly in the error
    so that callers see the exact field name from the template.
    """
    if key not in data or data[key] is None:
        raise FrontmatterError(
            f"Required frontmatter field '{key}' is missing or null in {path!s}"
        )
    return data[key]


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Task:
    """Frontmatter fields for a task artifact."""

    id: str
    title: str
    status: str
    priority: str
    assigned_role: str  # YAML key: assigned-role
    created: str
    spec: str | None = None  # Optional reference to a spec slug


@dataclass
class Bug:
    """Frontmatter fields for a bug artifact."""

    id: str
    title: str
    severity: str
    status: str
    created: str
    task: str | None = None  # Optional reference to a related task ID


@dataclass
class Spec:
    """Frontmatter fields for a specification artifact (ID is filename-based)."""

    title: str
    version: str
    status: str
    created: str
    author: str


@dataclass
class Adr:
    """Frontmatter fields for an Architecture Decision Record."""

    id: str
    title: str
    status: str
    created: str
    supersedes: str | None = None  # Optional reference to a superseded ADR ID


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_task(path: Path) -> Task:
    """Parse a task artifact file and return a :class:`Task`.

    Parameters
    ----------
    path:
        Path to the ``.md`` task file.

    Raises
    ------
    FrontmatterError
        If any required field is missing, null, or the frontmatter block is
        absent or malformed.
    """
    path = Path(path)
    data = _parse_yaml_frontmatter(path)
    return Task(
        id=str(_require(data, "id", path)),
        title=str(_require(data, "title", path)),
        status=str(_require(data, "status", path)),
        priority=str(_require(data, "priority", path)),
        assigned_role=str(_require(data, "assigned-role", path)),
        created=str(_require(data, "created", path)),
        spec=str(data["spec"]) if data.get("spec") is not None else None,
    )


def parse_bug(path: Path) -> Bug:
    """Parse a bug artifact file and return a :class:`Bug`.

    Raises
    ------
    FrontmatterError
        If any required field is missing or the frontmatter is malformed.
    """
    path = Path(path)
    data = _parse_yaml_frontmatter(path)
    return Bug(
        id=str(_require(data, "id", path)),
        title=str(_require(data, "title", path)),
        severity=str(_require(data, "severity", path)),
        status=str(_require(data, "status", path)),
        created=str(_require(data, "created", path)),
        task=str(data["task"]) if data.get("task") is not None else None,
    )


def parse_spec(path: Path) -> Spec:
    """Parse a spec artifact file and return a :class:`Spec`.

    Note: specs have no ``id`` in their frontmatter — their identifier is the
    filename slug.

    Raises
    ------
    FrontmatterError
        If any required field is missing or the frontmatter is malformed.
    """
    path = Path(path)
    data = _parse_yaml_frontmatter(path)
    return Spec(
        title=str(_require(data, "title", path)),
        version=str(_require(data, "version", path)),
        status=str(_require(data, "status", path)),
        created=str(_require(data, "created", path)),
        author=str(_require(data, "author", path)),
    )


def parse_adr(path: Path) -> Adr:
    """Parse an ADR artifact file and return an :class:`Adr`.

    Raises
    ------
    FrontmatterError
        If any required field is missing or the frontmatter is malformed.
    """
    path = Path(path)
    data = _parse_yaml_frontmatter(path)
    return Adr(
        id=str(_require(data, "id", path)),
        title=str(_require(data, "title", path)),
        status=str(_require(data, "status", path)),
        created=str(_require(data, "created", path)),
        supersedes=str(data["supersedes"]) if data.get("supersedes") is not None else None,
    )


# ---------------------------------------------------------------------------
# Dumper
# ---------------------------------------------------------------------------

# Field definitions per model type: each entry is (yaml_key, attribute_name).
# Order here determines the key order in the dumped YAML.
_TASK_FIELDS: list[tuple[str, str]] = [
    ("id", "id"),
    ("title", "title"),
    ("status", "status"),
    ("priority", "priority"),
    ("assigned-role", "assigned_role"),
    ("created", "created"),
    ("spec", "spec"),  # optional — omitted when None
]

_BUG_FIELDS: list[tuple[str, str]] = [
    ("id", "id"),
    ("title", "title"),
    ("severity", "severity"),
    ("status", "status"),
    ("created", "created"),
    ("task", "task"),  # optional — omitted when None
]

_SPEC_FIELDS: list[tuple[str, str]] = [
    ("title", "title"),
    ("version", "version"),
    ("status", "status"),
    ("created", "created"),
    ("author", "author"),
]

_ADR_FIELDS: list[tuple[str, str]] = [
    ("id", "id"),
    ("title", "title"),
    ("status", "status"),
    ("created", "created"),
    ("supersedes", "supersedes"),  # optional — omitted when None
]

# Map each model type to its ordered field list.
_MODEL_FIELDS: dict[type, list[tuple[str, str]]] = {
    Task: _TASK_FIELDS,
    Bug: _BUG_FIELDS,
    Spec: _SPEC_FIELDS,
    Adr: _ADR_FIELDS,
}


def dump_frontmatter(model: Task | Bug | Spec | Adr, body: str) -> str:
    """Serialise *model* back to a complete markdown file string.

    The output has the form::

        ---
        key: value
        ...
        ---

        <body>

    Optional fields (those whose value is ``None``) are omitted from the
    output so that round-tripping a file with no optional fields produces
    clean output without extra null keys.

    The key order matches the canonical order defined in the module-level
    ``_*_FIELDS`` lists, which mirrors the template order.

    Parameters
    ----------
    model:
        A :class:`Task`, :class:`Bug`, :class:`Spec`, or :class:`Adr` instance.
    body:
        The markdown body text to place after the frontmatter block.

    Returns
    -------
    str
        A complete markdown file as a string: frontmatter fence + body.

    Raises
    ------
    TypeError
        If *model* is not one of the supported types.
    """
    model_type = type(model)
    if model_type not in _MODEL_FIELDS:
        raise TypeError(
            f"dump_frontmatter does not support model type {model_type.__name__!r}"
        )

    ordered_fields = _MODEL_FIELDS[model_type]

    # Build a ruamel.yaml CommentedMap to preserve insertion order.
    cm: CommentedMap = CommentedMap()
    for yaml_key, attr_name in ordered_fields:
        value = getattr(model, attr_name)
        if value is None:
            # Omit optional fields when they are None.
            continue
        cm[yaml_key] = value

    # Serialise to a YAML string.
    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    stream = io.StringIO()
    yaml.dump(cm, stream)
    yaml_text = stream.getvalue()

    return f"---\n{yaml_text}---\n\n{body}"
