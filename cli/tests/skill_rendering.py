"""Render skill sources through the sync renderer for content assertions.

Tests assert on rendered output rather than on raw ``body.md`` or ``[claude]`` /
``[codex]`` header text, so they keep passing when sources gain markers.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

CLI_ROOT = Path(__file__).resolve().parents[1]
INIT_ROOT = CLI_ROOT / "src" / "ai_team" / "init"
SKILL_SOURCES = INIT_ROOT / "sources" / "skills"
SCAFFOLDS = INIT_ROOT / "scaffolds"
_COMMAND_MAP_PATH = INIT_ROOT / "sources" / "command_map.json"
_MARKERS_SCRIPT = CLI_ROOT / "scripts" / "skill_markers.py"


@cache
def _markers_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "skill_markers_for_tests", _MARKERS_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@cache
def _command_map() -> dict[str, Any]:
    return json.loads(_COMMAND_MAP_PATH.read_text(encoding="utf-8"))


def _render(text: str, tool: str, source: Path) -> str:
    return _markers_module().render_markers(text, tool, _command_map(), str(source))


def rendered_skill_body(skill_name: str, tool: str = "claude") -> str:
    """Return the skill body rendered for ``tool`` (``claude`` or ``codex``)."""
    body_path = SKILL_SOURCES / skill_name / "body.md"
    return _render(body_path.read_text(encoding="utf-8"), tool, body_path)


def rendered_skill_header(skill_name: str, tool: str = "claude") -> str:
    """Return the skill frontmatter header rendered for ``tool``."""
    metadata_path = SKILL_SOURCES / skill_name / "metadata.toml"
    metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
    return _render(metadata[tool]["header"].strip(), tool, metadata_path)


def rendered_skill_text(skill_name: str, tool: str = "claude") -> str:
    """Return the full SKILL.md text the sync produces for ``tool``."""
    header = rendered_skill_header(skill_name, tool)
    return header + "\n\n" + rendered_skill_body(skill_name, tool)
