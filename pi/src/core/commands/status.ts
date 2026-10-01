import { execFileSync } from "node:child_process";
import { readArtifact } from "../fs.js";
import type { ProjectRoot } from "../locator.js";
import { parseBug, parseTask } from "../models.js";
import { success } from "../result.js";
import { listMarkdownFiles } from "./artifact-files.js";
import type { RootHandler } from "./handler.js";

const NOT_RECORDED = "not recorded";
const NOT_FOUND = "not found";
const INTEGRATION_PATTERN = "merge\\|integration\\|verification\\|test";

/** The newest commit subject across all refs that mentions an integration keyword. */
export function latestIntegrationResult(root: ProjectRoot): string {
  let output: string;
  try {
    output = execFileSync(
      "git",
      ["-C", root.repo, "log", "--all", `--grep=${INTEGRATION_PATTERN}`, "-n", "1", "--pretty=format:%s"],
      { encoding: "utf-8", stdio: ["ignore", "pipe", "pipe"] },
    );
  } catch {
    return NOT_FOUND;
  }
  const value = output.trim();
  return value === "" ? NOT_FOUND : value;
}

/** The first non-blank line under the task's latest "### Session" heading in its Work Log. */
function latestWorkLogLine(taskPath: string): string {
  const lines = readArtifact(taskPath, "task").body.split(/\r\n|\r|\n/);
  const start = lines.findIndex((line) => line.trim() === "## Work Log");
  if (start === -1) return NOT_RECORDED;

  const afterHeading = lines.slice(start + 1);
  const end = afterHeading.findIndex((line) => line.startsWith("## "));
  const workLog = end === -1 ? afterHeading : afterHeading.slice(0, end);

  const lastSession = workLog.map((line) => line.startsWith("### Session")).lastIndexOf(true);
  if (lastSession === -1) return NOT_RECORDED;

  const firstLine = workLog.slice(lastSession + 1).find((line) => line.trim() !== "");
  return firstLine === undefined ? NOT_RECORDED : firstLine.trim();
}

function blockingReason(taskPath: string): string {
  const task = parseTask(taskPath);
  for (const key of ["blocking-reason", "blocking_reason"]) {
    const value = task.sourceMap?.getString(key);
    if (value !== undefined && value.trim() !== "") return value.trim();
  }
  return latestWorkLogLine(taskPath);
}

const count = (folder: string): number => listMarkdownFiles(folder).length;

/** The status summary, shared with `report`. */
export function statusPayload(root: ProjectRoot): Record<string, unknown> {
  return {
    counts: {
      specs_active: count(root.specs),
      tasks: {
        pending: count(root.tasksPending),
        in_progress: count(root.tasksInProgress),
        completed: count(root.tasksCompleted),
        blocked: count(root.tasksBlocked),
      },
      bugs: {
        open: count(root.bugsOpen),
        in_progress: count(root.bugsInProgress),
        resolved: count(root.bugsResolved),
      },
      adrs: count(root.decisions),
    },
    in_progress_tasks: listMarkdownFiles(root.tasksInProgress).map((path) => {
      const task = parseTask(path);
      return { id: task.id, title: task.title, assigned_role: task.assignedRole };
    }),
    blocked_tasks: listMarkdownFiles(root.tasksBlocked).map((path) => {
      const task = parseTask(path);
      return { id: task.id, title: task.title, blocking_reason: blockingReason(path) };
    }),
    critical_high_open_bugs: listMarkdownFiles(root.bugsOpen)
      .map(parseBug)
      .filter((bug) => bug.severity === "critical" || bug.severity === "high")
      .map((bug) => ({ id: bug.id, title: bug.title, severity: bug.severity })),
    latest_integration_result: latestIntegrationResult(root),
  };
}

export const statusSummary: RootHandler = (root) => success(statusPayload(root));
