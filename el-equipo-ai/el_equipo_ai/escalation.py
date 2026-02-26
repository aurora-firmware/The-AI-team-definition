"""Escalation pipeline — architect consultation then human notification."""

from __future__ import annotations

import json

from el_equipo_ai.logger import Logger
from el_equipo_ai.manifest_bridge import VKClient
from el_equipo_ai.models import (
    ArchitectVerdict,
    EscalationResult,
    TaskFailureReport,
)
from el_equipo_ai.notifier import Notifier
from el_equipo_ai.provider_router import ProviderRouter


# ---------------------------------------------------------------------------
# Architect consultation (T4.3)
# ---------------------------------------------------------------------------


_ARCHITECT_PROMPT = """\
A coding task has failed after multiple attempts by an autonomous agent.

Task ID: {task_id}
Attempts: {attempts}

What was tried:
{what_tried}

What failed:
{what_failed}

Agent's analysis:
{agent_analysis}

Based on this context, is this:
(A) a simple fix — the agent just needs revised/clarified instructions, or
(B) a scope problem — the task design, dependencies, or requirements are wrong
    and need human re-planning?

Respond with ONLY valid JSON in this exact format:
{{
  "verdict": "simple_fix" | "scope_problem",
  "revised_instructions": "<clear new instructions for a retry agent, or null>",
  "analysis": "<brief explanation of your assessment>"
}}
"""


def consult_architect(
    failure_report: TaskFailureReport,
    provider_router: ProviderRouter,
    logger: Logger,
) -> ArchitectVerdict:
    """Query the planner_creative model for a verdict on a failed task.

    Returns ArchitectVerdict. On any failure defaults to scope_problem (safe fallback).
    """
    prompt = _ARCHITECT_PROMPT.format(
        task_id=failure_report.task_id,
        attempts=failure_report.attempts,
        what_tried=failure_report.what_tried,
        what_failed=failure_report.what_failed,
        agent_analysis=failure_report.agent_analysis,
    )

    try:
        response = provider_router.call(
            role_name="planner_creative",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or ""
        verdict = _parse_architect_response(content)
    except Exception as exc:  # noqa: BLE001
        logger.log(
            "architect_consult_error",
            task=failure_report.task_id,
            error=str(exc),
        )
        verdict = ArchitectVerdict(
            verdict="scope_problem",
            revised_instructions=None,
            analysis=f"Architect query failed: {exc}",
        )

    logger.log(
        "architect_consult",
        task=failure_report.task_id,
        verdict=verdict.verdict,
        analysis=verdict.analysis,
    )
    return verdict


def _parse_architect_response(content: str) -> ArchitectVerdict:
    """Parse the JSON response from the architect model.

    Defaults to scope_problem on any parse error (safe fallback).
    """
    try:
        # Strip markdown code fences if present
        clean = content.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:])
            clean = clean.rstrip("`").strip()

        data = json.loads(clean)
        verdict = data.get("verdict", "scope_problem")
        if verdict not in ("simple_fix", "scope_problem"):
            verdict = "scope_problem"
        return ArchitectVerdict(
            verdict=verdict,
            revised_instructions=data.get("revised_instructions"),
            analysis=data.get("analysis", ""),
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return ArchitectVerdict(
            verdict="scope_problem",
            revised_instructions=None,
            analysis="Could not parse architect response",
        )


# ---------------------------------------------------------------------------
# Full escalation pipeline (T4.4)
# ---------------------------------------------------------------------------


def handle_task_failure(
    failure_report: TaskFailureReport,
    provider_router: ProviderRouter,
    vk_client: VKClient,
    notifier: Notifier,
    logger: Logger,
) -> EscalationResult:
    """Full escalation flow for a failed task.

    Flow:
    1. First attempt (attempts == 1): consult architect.
       - simple_fix → create new VK task with revised instructions.
       - scope_problem → escalate to human.
    2. Second+ attempt (attempts >= 2): skip architect → escalate to human directly.
    """
    # Second failure (or more) → skip architect, go straight to human
    if failure_report.attempts >= 2:
        return _escalate_to_human(failure_report, notifier, logger, analysis="Second failure — skipping architect, escalating directly.")

    # First failure → consult architect
    verdict = consult_architect(failure_report, provider_router, logger)

    if verdict.verdict == "simple_fix" and verdict.revised_instructions:
        new_task_id = vk_client.create_task(
            title=f"[RETRY] {failure_report.task_id}",
            description=(
                f"Previous attempt failed. Revised instructions:\n\n"
                f"{verdict.revised_instructions}\n\n"
                f"Original failure context:\n"
                f"What tried: {failure_report.what_tried}\n"
                f"What failed: {failure_report.what_failed}"
            ),
            role="executor",
        )
        logger.log(
            "escalation_retry",
            original_task=failure_report.task_id,
            new_task=new_task_id,
            verdict=verdict.verdict,
        )
        return EscalationResult(
            action="retried",
            new_task_id=new_task_id,
            analysis=verdict.analysis,
        )

    # scope_problem (or simple_fix with no instructions) → escalate to human
    return _escalate_to_human(failure_report, notifier, logger, analysis=verdict.analysis)


def _escalate_to_human(
    failure_report: TaskFailureReport,
    notifier: Notifier,
    logger: Logger,
    analysis: str,
) -> EscalationResult:
    body = (
        f"Task: {failure_report.task_id}\n"
        f"Attempts: {failure_report.attempts}\n\n"
        f"What was tried:\n{failure_report.what_tried}\n\n"
        f"What failed:\n{failure_report.what_failed}\n\n"
        f"Agent analysis:\n{failure_report.agent_analysis}\n\n"
        f"Architect assessment:\n{analysis}"
    )
    notifier.action_required(
        title=f"Task failed: {failure_report.task_id}",
        body=body,
        vk_link=None,
    )
    logger.log(
        "escalation_human",
        task=failure_report.task_id,
        attempts=failure_report.attempts,
    )
    return EscalationResult(
        action="escalated_to_human",
        new_task_id=None,
        analysis=analysis,
    )
