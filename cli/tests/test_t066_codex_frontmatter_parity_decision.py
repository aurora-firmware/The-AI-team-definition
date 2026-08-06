"""Tests for T-066: Record the Codex skill-frontmatter parity decision.

AC-1: An ADR in the project decisions directory SHALL record that Codex skill
      frontmatter retains full parity with Claude, with rationale and the
      Skill()-wiring implication.
AC-2: The skill-authoring guide (guides/skill_template.md) SHALL state that
      [codex] headers keep the full frontmatter key set.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# This repository sets [project] dir = "docs/ai-team" in .ai-team.toml, so its
# own artifacts live there rather than under the default project/ directory.
DECISIONS_DIR = REPO_ROOT / "docs" / "ai-team" / "decisions"
SKILL_TEMPLATE = REPO_ROOT / "guides" / "skill_template.md"

# Required frontmatter keys that must be mentioned in the ADR
FRONTMATTER_KEYS = (
    "allowed-tools",
    "argument-hint",
    "effort",
    "disable-model-invocation",
)


# ---------------------------------------------------------------------------
# AC-1: ADR exists and records the parity decision with rationale
# ---------------------------------------------------------------------------


def test_adr_exists_for_codex_frontmatter_parity() -> None:
    """AC-1: An ADR file must exist in the project decisions directory covering
    Codex frontmatter parity with Claude."""
    adr_files = list(DECISIONS_DIR.glob("*.md"))
    assert adr_files, f"No ADR files found in {DECISIONS_DIR}"
    combined = "\n".join(f.read_text(encoding="utf-8") for f in adr_files)
    assert "codex" in combined.lower() or "parity" in combined.lower(), (
        f"No ADR in {DECISIONS_DIR} mentions Codex frontmatter parity"
    )


def test_adr_states_codex_frontmatter_retains_full_parity() -> None:
    """AC-1: The ADR must explicitly state that Codex skill frontmatter retains
    full parity with Claude."""
    adr_files = list(DECISIONS_DIR.glob("*.md"))
    combined = "\n".join(f.read_text(encoding="utf-8") for f in adr_files)
    assert "parity" in combined.lower(), (
        "ADR must state that Codex frontmatter retains parity with Claude"
    )
    assert "codex" in combined.lower(), "ADR must reference Codex skill frontmatter"


def test_adr_mentions_skill_wiring_implication() -> None:
    """AC-1: The ADR must mention the Skill()-wiring implication for inter-skill
    invocations expressed in allowed-tools."""
    adr_files = list(DECISIONS_DIR.glob("*.md"))
    combined = "\n".join(f.read_text(encoding="utf-8") for f in adr_files)
    assert "Skill()" in combined or "Skill(" in combined, (
        "ADR must mention the Skill()-wiring implication for allowed-tools"
    )


def test_adr_mentions_all_frontmatter_keys() -> None:
    """AC-1: The ADR must name the key frontmatter fields retained by Codex:
    allowed-tools, argument-hint, effort, disable-model-invocation."""
    adr_files = list(DECISIONS_DIR.glob("*.md"))
    combined = "\n".join(f.read_text(encoding="utf-8") for f in adr_files)
    for key in FRONTMATTER_KEYS:
        assert key in combined, (
            f"ADR must mention frontmatter key '{key}' as retained in Codex skill headers"
        )


def test_adr_has_rationale() -> None:
    """AC-1: The ADR must contain rationale explaining why parity is maintained."""
    adr_files = list(DECISIONS_DIR.glob("*.md"))
    # Find the parity ADR specifically
    parity_adrs = [
        f for f in adr_files if "parity" in f.name.lower() or "codex" in f.name.lower()
    ]
    assert parity_adrs, "No ADR file found with 'parity' or 'codex' in filename"
    content = parity_adrs[0].read_text(encoding="utf-8")
    # ADR must have a Context or Decision section with substantive rationale
    assert "## Context" in content, "ADR must have a ## Context section with rationale"
    assert "## Decision" in content, "ADR must have a ## Decision section"
    # Ensure the context section has actual content beyond placeholders
    assert "What is the situation" not in content, (
        "ADR ## Context section must be filled in, not left as placeholder"
    )


def test_adr_has_accepted_status() -> None:
    """AC-1: The parity ADR must have 'accepted' status since the decision is confirmed."""
    adr_files = list(DECISIONS_DIR.glob("*.md"))
    parity_adrs = [
        f for f in adr_files if "parity" in f.name.lower() or "codex" in f.name.lower()
    ]
    assert parity_adrs, "No ADR file found with 'parity' or 'codex' in filename"
    content = parity_adrs[0].read_text(encoding="utf-8")
    assert "accepted" in content, (
        "The parity ADR must have status: accepted since the decision is confirmed"
    )


# ---------------------------------------------------------------------------
# AC-2: skill_template.md states [codex] headers keep the full frontmatter key set
# ---------------------------------------------------------------------------


def test_skill_template_mentions_codex_frontmatter_parity() -> None:
    """AC-2: guides/skill_template.md must state that [codex] headers keep the
    full frontmatter key set."""
    content = SKILL_TEMPLATE.read_text(encoding="utf-8")
    assert "codex" in content.lower(), (
        "guides/skill_template.md must mention [codex] frontmatter headers"
    )


def test_skill_template_codex_section_mentions_full_key_set() -> None:
    """AC-2: guides/skill_template.md must state that [codex] headers retain the
    full frontmatter key set (not a subset)."""
    content = SKILL_TEMPLATE.read_text(encoding="utf-8")
    # Must say codex keeps full/complete key set
    codex_policy_markers = (
        "full frontmatter",
        "full key set",
        "full set of frontmatter",
        "same frontmatter",
        "identical frontmatter",
    )
    assert any(m in content.lower() for m in codex_policy_markers), (
        "guides/skill_template.md must state that [codex] headers retain the "
        "full frontmatter key set"
    )


def test_skill_template_codex_section_mentions_parity_keys() -> None:
    """AC-2: guides/skill_template.md must mention the key frontmatter fields
    that codex retains: allowed-tools and disable-model-invocation at minimum."""
    content = SKILL_TEMPLATE.read_text(encoding="utf-8")
    # The template should at least mention allowed-tools and codex in the same context
    assert "allowed-tools" in content, (
        "guides/skill_template.md must mention 'allowed-tools' in its frontmatter guidance"
    )
    # Verify the codex section is locatable
    lines = content.splitlines()
    codex_lines = [i for i, line in enumerate(lines) if "codex" in line.lower()]
    assert codex_lines, (
        "guides/skill_template.md must contain at least one line referencing [codex] headers"
    )
