import { mkdirSync, writeFileSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import type { ProjectRoot } from "../locator.js";
import { parseAdr, parseBug, parseSpec, parseTask } from "../models.js";
import { failure, success } from "../result.js";
import { today } from "../runtime.js";
import { loadTemplate } from "../templates.js";
import { listMarkdownFiles } from "./artifact-files.js";
import type { RootHandler } from "./handler.js";
import { statusPayload } from "./status.js";

interface Counts {
  specs_active: number;
  tasks: { pending: number; in_progress: number; completed: number; blocked: number };
  bugs: { open: number; in_progress: number; resolved: number };
  adrs: number;
}
interface InProgressRow { id: string; title: string; assigned_role: string }
interface BlockedRow { id: string; title: string; blocking_reason: string }
interface BugRow { id: string; title: string }
interface StatusSummary {
  counts: Counts;
  in_progress_tasks: InProgressRow[];
  blocked_tasks: BlockedRow[];
  critical_high_open_bugs: BugRow[];
  latest_integration_result: string;
}

const asRows = (rows: string[], fallback: string): string =>
  rows.length === 0 ? fallback : rows.join("\n");

function summaryLine(payload: StatusSummary): string {
  const { counts } = payload;
  return (
    `Active specs: ${counts.specs_active}. ` +
    `Pending tasks: ${counts.tasks.pending}. ` +
    `In progress tasks: ${counts.tasks.in_progress}. ` +
    `Completed tasks: ${counts.tasks.completed}. ` +
    `Blocked tasks: ${counts.tasks.blocked}. ` +
    `Open bugs: ${counts.bugs.open}. ` +
    `Bugs in progress: ${counts.bugs.in_progress}. ` +
    `Resolved bugs: ${counts.bugs.resolved}. ` +
    `ADRs: ${counts.adrs}. ` +
    `Latest integration result: ${payload.latest_integration_result}.`
  );
}

function specRows(root: ProjectRoot): string {
  const rows = listMarkdownFiles(root.specs).map((path) => {
    const spec = parseSpec(path);
    const note = spec.status === "approved" ? "Current Gate 5 target" : "Review in progress";
    return `| ${basename(path)} | ${spec.status} | ${note} |`;
  });
  return asRows(rows, "| none | n/a | No active specs |");
}

function completedRows(root: ProjectRoot): string {
  const rows = listMarkdownFiles(root.tasksCompleted).map((path) => {
    const task = parseTask(path);
    return `| ${task.id} | ${task.title} | ${task.assignedRole} |`;
  });
  return asRows(rows, "| none | n/a | n/a |");
}

function inProgressRows(payload: StatusSummary): string {
  const rows = payload.in_progress_tasks.map(
    (row) => `| ${row.id} | ${row.title} | ${row.assigned_role} | actively progressing |`,
  );
  return asRows(rows, "| none | n/a | n/a | no in-progress tasks |");
}

function blockedRows(payload: StatusSummary): string {
  const rows = payload.blocked_tasks.map(
    (row) =>
      `| ${row.id} | ${row.title} | ${row.blocking_reason} | Resolve blocker: ${row.blocking_reason} |`,
  );
  return asRows(rows, "| none | n/a | n/a | no action needed |");
}

function diagnosisStatus(state: string): string {
  if (state === "open") return "n/a";
  if (state === "in-progress") return "in progress";
  return "complete";
}

function bugRows(root: ProjectRoot): string {
  const folders: [string, string][] = [
    ["open", root.bugsOpen],
    ["in-progress", root.bugsInProgress],
    ["resolved", root.bugsResolved],
  ];
  const rows = folders.flatMap(([state, folder]) =>
    listMarkdownFiles(folder).map((path) => {
      const bug = parseBug(path);
      return `| ${bug.id} | ${bug.title} | ${bug.severity} | ${state} | ${diagnosisStatus(state)} |`;
    }),
  );
  return asRows(rows, "| none | n/a | n/a | n/a | n/a |");
}

function decisionRows(root: ProjectRoot): string {
  const rows = listMarkdownFiles(root.decisions).map((path) => {
    const adr = parseAdr(path);
    return `| ${adr.id} | ${adr.title} | ${adr.status} |`;
  });
  return asRows(rows, "| none | n/a | n/a |");
}

const MAX_NEXT_ACTIONS = 3;

function nextActions(payload: StatusSummary): string {
  const actions = [
    ...payload.blocked_tasks.map((row) => `Unblock ${row.id}: ${row.blocking_reason}`),
    ...payload.critical_high_open_bugs.map((row) => `Triage ${row.id}: ${row.title}`),
    ...payload.in_progress_tasks.map((row) => `Advance ${row.id}: ${row.title}`),
  ];
  if (actions.length === 0) actions.push("No immediate actions.");
  return actions
    .slice(0, MAX_NEXT_ACTIONS)
    .map((action, index) => `${index + 1}. ${action}`)
    .join("\n");
}

function risksAndConcerns(payload: StatusSummary): string {
  const risks: string[] = [];
  if (payload.blocked_tasks.length > 0) risks.push("Blocked tasks may delay delivery.");
  if (payload.critical_high_open_bugs.length > 0) {
    risks.push("Critical/high bugs may impact release quality.");
  }
  if (risks.length === 0) risks.push("No immediate risks identified.");
  return risks.map((risk) => `- ${risk}`).join("\n");
}

function renderReport(
  template: string,
  payload: StatusSummary,
  reportDate: string,
  root: ProjectRoot,
): string {
  const integration = payload.latest_integration_result;
  const replacements: [string, string][] = [
    ['title: "Progress Report — [Date or Sprint]"', `title: "Progress Report — ${reportDate}"`],
    ["created: YYYY-MM-DD", `created: ${reportDate}`],
    ["# Progress Report — [Date or Sprint]", `# Progress Report — ${reportDate}`],
    ["One-paragraph overview of current project state.", summaryLine(payload)],
    ["| specification-name.md | approved | Current Gate 5 target |", specRows(root)],
    ["- Latest integration-test result:", `- Latest integration-test result: ${integration}`],
    ["- Source:", "- Source: git log --all --grep=merge|integration|verification|test -n 1"],
    ["- Date:", `- Date: ${reportDate}`],
    ["| T-001 | Task title | Role |\n| T-002 | Task title | Role |", completedRows(root)],
    ["| T-003 | Task title | Role | Current state |", inProgressRows(payload)],
    [
      "| T-004 | Task title | What is blocking | What must happen to unblock |",
      blockedRows(payload),
    ],
    ["| B-001 | Bug title | high | open | not started |", bugRows(root)],
    ["| 001 | Decision title | decided |", decisionRows(root)],
    [
      "1. Next priority action\n2. Second priority action\n3. Third priority action",
      nextActions(payload),
    ],
    ["- Risk or concern 1\n- Risk or concern 2", risksAndConcerns(payload)],
  ];
  // Replacer functions keep "$" in artifact text literal.
  return replacements.reduce(
    (report, [placeholder, value]) => report.replaceAll(placeholder, () => value),
    template,
  );
}

/** Writes the Gate 5 progress report; a relative `out` is resolved against the project's repo directory. */
export const writeReport: RootHandler = (root, input) => {
  const { out } = input;
  if (out !== undefined && out !== null && (typeof out !== "string" || out === "")) {
    return failure("The report 'out' value must be a non-empty string path.");
  }

  const reportDate = today();
  const destination =
    typeof out === "string"
      ? resolve(root.repo, out)
      : join(root.docs, "reports", `progress-report-${reportDate}.md`);

  const payload = statusPayload(root) as unknown as StatusSummary;
  const content = renderReport(loadTemplate("report").toString("utf-8"), payload, reportDate, root);
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, content, "utf-8");
  return success({ path: destination, content });
};
