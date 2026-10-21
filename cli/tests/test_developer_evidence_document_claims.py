"""The Developer accepts an artifact read as proof of a document claim.

A design-review task is proved by the documents read, not by a command run,
so the Developer's evidence rule must allow that form, as
evidence-before-claims Step 3 does.
"""

from pathlib import Path

import pytest

INIT_DIR = Path(__file__).resolve().parents[1] / "src" / "ai_team" / "init"

DEVELOPER_FILES = [
    INIT_DIR / "sources" / "agents" / "claude" / "developer.md",
    INIT_DIR / "sources" / "agents" / "codex" / "developer.toml",
    INIT_DIR / "scaffolds" / "claude" / "agents" / "developer.md",
    INIT_DIR / "scaffolds" / "codex" / "agents" / "developer.toml",
]


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


@pytest.mark.parametrize(
    "path", DEVELOPER_FILES, ids=lambda p: p.parent.parent.name + "/" + p.name
)
def test_evidence_rule_accepts_artifact_read_for_document_claims(path: Path) -> None:
    text = _text(path)
    assert "a claim without a fresh command and its actual output" not in text
    assert (
        "a claim without fresh proof (command output, or for a document claim "
        "such as a design-review result, the artifact and line you read)"
    ) in text


@pytest.mark.parametrize(
    "path", DEVELOPER_FILES, ids=lambda p: p.parent.parent.name + "/" + p.name
)
def test_evidence_template_names_the_document_claim_form(path: Path) -> None:
    text = _text(path)
    assert (
        "or for a document claim the artifact path and the line that confirms it, "
        'or "not run" with reason'
    ) in text
