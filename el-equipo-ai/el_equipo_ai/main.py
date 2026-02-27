"""El-equipo-AI CLI — wires together all components."""

from __future__ import annotations

import argparse
import os
import sys

from el_equipo_ai.config import load_config
from el_equipo_ai.escalation import handle_task_failure
from el_equipo_ai.integration import integration_pipeline
from el_equipo_ai.logger import Logger
from el_equipo_ai.manifest_bridge import VKClient, bridge_plan_to_vk
from el_equipo_ai.models import AppConfig, TaskFailureReport
from el_equipo_ai.notifier import Notifier
from el_equipo_ai.provider_router import ProviderRouter
from el_equipo_ai.quota_manager import QuotaManager
from el_equipo_ai.stall_detector import StallDetector


# ---------------------------------------------------------------------------
# App context — all live components wired together
# ---------------------------------------------------------------------------


class App:
    """Top-level object holding all initialised components."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.logger = Logger(config.logging)
        self.quota_manager = QuotaManager(
            state_file=config.state_file,
            logger=self.logger,
        )
        self.provider_router = ProviderRouter(
            config=config,
            logger=self.logger,
        )
        # Restore persisted provider states (quota cooldowns from previous runs)
        saved_states = self.quota_manager.load()
        if saved_states:
            self.provider_router.set_state(saved_states)

        self.stall_detector = StallDetector(
            config=config.stall_detection,
            logger=self.logger,
        )
        self.vk_client = VKClient(
            vk_url=config.vk_url,
            logger=self.logger,
        )
        self.notifier = Notifier(
            channels=config.notifications,
            logger=self.logger,
        )

    # ------------------------------------------------------------------
    # Workflow steps
    # ------------------------------------------------------------------

    def plan(self, feature_description: str) -> str:
        """Generate a task plan from a feature description.

        Step 1: Creative brainstorm (planner_creative role).
        Step 2: Structured task breakdown (planner_structured role).

        Returns the structured plan text.
        """
        self.logger.log("plan_start", feature=feature_description[:100])
        self.notifier.info(f"Planning: {feature_description[:80]}...")

        # Brainstorm phase
        brainstorm_response = self.provider_router.call(
            role_name="planner_creative",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a software architect. Brainstorm an implementation "
                        "approach for the described feature. Ask clarifying questions "
                        "if needed. Produce a design document."
                    ),
                },
                {"role": "user", "content": feature_description},
            ],
        )
        design_doc = brainstorm_response.choices[0].message.content or ""

        # Structured plan phase
        plan_response = self.provider_router.call(
            role_name="planner_structured",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a technical project manager. Convert the design document "
                        "into an atomic task breakdown.\n\n"
                        "Format each task as:\n"
                        "## Task N: Title\n"
                        "**Description:** ...\n"
                        "**Role:** executor|tester|reviewer\n"
                        "**Dependencies:** Task X, Task Y\n"
                        "**Verification:** <test command>\n"
                        "**Files to modify:** path1, path2\n"
                        "**Files to create:** path3\n"
                    ),
                },
                {"role": "user", "content": f"Design document:\n\n{design_doc}"},
            ],
        )
        plan_text = plan_response.choices[0].message.content or ""
        self.logger.log("plan_complete", tasks_preview=plan_text[:200])
        return plan_text

    def execute(self, plan_text: str) -> list[str]:
        """Bridge a Superpowers plan into Vibe Kanban tasks.

        Returns list of created VK task IDs.
        """
        self.logger.log("execute_start")
        self.notifier.info("Bridging plan to Vibe Kanban...")

        task_ids = bridge_plan_to_vk(plan_text, self.vk_client)
        self.logger.log("execute_bridge_complete", task_count=len(task_ids))
        self.notifier.info(f"Created {len(task_ids)} tasks in Vibe Kanban.")
        return task_ids

    def integrate(self, branches: list[str]) -> None:
        """Run the integration test phase."""
        self.logger.log("integrate_start", branches=branches)
        self.notifier.info(f"Starting integration phase for {len(branches)} branches...")

        result = integration_pipeline(
            branches_in_order=branches,
            test_command=self.config.project.test_command,
            vk_client=self.vk_client,
            notifier=self.notifier,
            logger=self.logger,
        )
        self.logger.log("integrate_complete", status=result.status)

    def status(self) -> None:
        """Print current provider and task status."""
        self.provider_router.check_cooldowns()
        states = self.provider_router.get_state()
        # Build a lookup of which providers have an API key configured
        configured = {
            p.name
            for p in self.config.providers
            if p.api_key or p.api_key_env is None  # key resolved, or no key needed (e.g. Ollama)
        }
        print("=== Provider Status ===")
        for name, state in states.items():
            if name not in configured:
                print(f"  {name}: not configured (no API key)")
                continue
            reset_str = f" (resets: {state.reset_at})" if state.reset_at else ""
            print(f"  {name}: {state.status.value}{reset_str}")
        swap_log = self.quota_manager.get_swap_log()
        print(f"\n=== Swap Log ({len(swap_log)} events) ===")
        for event in swap_log[-5:]:  # last 5
            print(f"  {event['ts']} | {event['from']} → {event['to']} ({event['reason']})")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------


def cli() -> None:
    parser = argparse.ArgumentParser(
        prog="el-equipo-ai",
        description="El-equipo-AI — autonomous coding orchestrator",
    )
    parser.add_argument(
        "--config",
        default=os.environ.get("EL_EQUIPO_CONFIG", "el-equipo-ai.yaml"),
        help="Path to config YAML (default: el-equipo-ai.yaml or EL_EQUIPO_CONFIG env)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # plan
    plan_cmd = subparsers.add_parser("plan", help="Generate a task plan from a feature description")
    plan_cmd.add_argument("feature", help="Feature description")

    # execute
    exec_cmd = subparsers.add_parser("execute", help="Bridge a plan file into Vibe Kanban tasks")
    exec_cmd.add_argument("plan_file", help="Path to plan text file")

    # integrate
    int_cmd = subparsers.add_parser("integrate", help="Run integration test phase")
    int_cmd.add_argument("branches", nargs="+", help="Branch names in dependency order")

    # status
    subparsers.add_parser("status", help="Show provider and task status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = load_config(args.config)
    app = App(config)

    if args.command == "plan":
        plan_text = app.plan(args.feature)
        print(plan_text)

    elif args.command == "execute":
        with open(args.plan_file) as fh:
            plan_text = fh.read()
        task_ids = app.execute(plan_text)
        for tid in task_ids:
            print(tid)

    elif args.command == "integrate":
        app.integrate(args.branches)

    elif args.command == "status":
        app.status()


if __name__ == "__main__":
    cli()
