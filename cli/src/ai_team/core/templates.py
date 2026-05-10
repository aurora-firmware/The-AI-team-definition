from __future__ import annotations

from importlib.resources import files
from typing import Literal

TemplateKind = Literal["task", "bug", "spec", "adr"]


def load_template(kind: TemplateKind) -> str:
    if kind != "task":
        raise ValueError("Unsupported template kind: task")

    return files("ai_team.templates").joinpath("task.md").read_text(encoding="utf-8")
