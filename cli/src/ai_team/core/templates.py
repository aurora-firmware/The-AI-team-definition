from __future__ import annotations

from importlib.resources import files
from typing import Literal

TemplateKind = Literal["task", "bug", "spec", "adr", "report"]
_SUPPORTED_KINDS: tuple[TemplateKind, ...] = (
    "task",
    "bug",
    "spec",
    "adr",
    "report",
)
_TEMPLATE_FILES: dict[TemplateKind, str] = {
    "task": "task.md",
    "bug": "bug.md",
    "spec": "spec.md",
    "adr": "adr.md",
    "report": "progress-report.md",
}


def load_template(kind: TemplateKind) -> str:
    template_path = _TEMPLATE_FILES.get(kind)
    if template_path is None:
        supported = ", ".join(_SUPPORTED_KINDS)
        raise ValueError(
            f"Unsupported template kind '{kind}'. Supported kinds: {supported}"
        )

    return files("ai_team.templates").joinpath(template_path).read_text(encoding="utf-8")
