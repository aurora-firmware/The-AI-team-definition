"""CR-003 T-107: task and bug templates state the verification run context and design-review option."""

from __future__ import annotations

from ai_team.core.templates import load_template


def flat(text: str) -> str:
    return " ".join(text.split())


def section(template: str, heading: str) -> str:
    after_heading = template.split(heading, 1)[1]
    return flat(after_heading.split("\n## ", 1)[0])


RUN_CONTEXT = (
    "each line runs from the repository root in a fresh shell, "
    "independently of the other lines"
)
CHANGE_DIRECTORY = "changes into it on that line (`cd <dir> && <command>`)"


def test_task_template_verification_states_the_run_context():
    verification = section(load_template("task"), "## Verification")
    assert RUN_CONTEXT in verification
    assert CHANGE_DIRECTORY in verification


def test_task_template_verification_states_the_design_review_replacement():
    verification = section(load_template("task"), "## Verification")
    assert "design-review task" in verification
    assert "replaces the command block with a `Design review:` line" in verification
    assert "one bullet per reference" in verification
    assert "S-000 when it exists" in verification


def test_task_template_verifiable_rule_names_the_design_review_alternative():
    template = load_template("task")
    rules = flat(template.split("Task Quality Rules", 1)[1].split("-->", 1)[0])
    assert "Verifiable" in rules
    assert "design review" in rules.split("Verifiable", 1)[1].split("Self-contained")[0]


def test_bug_template_fix_verification_states_the_run_context():
    fix_verification = section(load_template("bug"), "## Fix Verification")
    assert RUN_CONTEXT in fix_verification
    assert CHANGE_DIRECTORY in fix_verification


def test_bug_template_fix_verification_has_no_design_review_mode():
    fix_verification = section(load_template("bug"), "## Fix Verification")
    assert "Design review" not in fix_verification


def test_task_template_verifiable_rule_keeps_the_manual_steps_alternative():
    template = load_template("task")
    rules = flat(template.split("Task Quality Rules", 1)[1].split("-->", 1)[0])
    verifiable = rules.split("Verifiable", 1)[1].split("Self-contained")[0]
    assert "explicit manual steps" in verifiable
