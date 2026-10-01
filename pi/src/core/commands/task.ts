import { existsSync, mkdirSync, readdirSync, realpathSync } from "node:fs";
import { basename, join } from "node:path";
import {
  ArtifactExists,
  moveArtifact,
  readArtifact,
  updateStatus,
  writeArtifact,
} from "../fs.js";
import { splitFrontmatter } from "../frontmatter.js";
import { nextTaskId } from "../ids.js";
import { createArtifactWithLock, LockTimeout } from "../lock.js";
import type { ProjectRoot } from "../locator.js";
import type { Task } from "../models.js";
import { failure, success, type Result } from "../result.js";
import { today } from "../runtime.js";
import { slugify } from "../slug.js";
import { loadTemplate } from "../templates.js";
import type { CommandInput, RootHandler } from "./handler.js";

const TASK_PRIORITIES = ["critical", "high", "medium", "low"];
const TITLE_PLACEHOLDER = "# [Task Title]";

/** Creates a pending task from the bundled template; the ID is allocated and the file written under the lock. */
export const createTask: RootHandler = (root, input) => {
  const { title, priority = "medium", assignedRole = "unassigned", spec } = input;
  if (typeof title !== "string" || title === "") {
    return failure("A non-empty 'title' is required to create a task.");
  }
  if (typeof priority !== "string" || !TASK_PRIORITIES.includes(priority)) {
    return failure(
      `Invalid task priority ${JSON.stringify(priority)}.`,
      `Use one of: ${TASK_PRIORITIES.join(", ")}.`,
    );
  }
  if (typeof assignedRole !== "string") {
    return failure("The task 'assignedRole' must be a string.");
  }
  if (spec !== undefined && spec !== null && typeof spec !== "string") {
    return failure("The task 'spec' value must be a string.");
  }

  try {
    const [id, destination] = createArtifactWithLock(root.projectDir, {
      allocateId: () => nextTaskId(root),
      build: (taskId) => {
        const template = loadTemplate("task").toString("utf-8");
        const { body } = splitFrontmatter(template, "the task template");
        const model: Task = {
          kind: "task",
          id: taskId,
          title,
          status: "pending",
          priority,
          assignedRole,
          created: today(),
          spec: spec ?? undefined,
          sourceMap: undefined,
        };
        return [
          join(root.tasksPending, `${taskId}-${slugify(title)}.md`),
          model,
          body.replace(TITLE_PLACEHOLDER, () => `# ${title}`),
        ];
      },
    });
    return success({ id, path: destination });
  } catch (error) {
    if (error instanceof ArtifactExists || error instanceof LockTimeout) {
      return failure(error.message);
    }
    throw error;
  }
};

type TaskState = "pending" | "in-progress" | "completed" | "blocked";

const TASK_STATES: readonly TaskState[] = ["pending", "in-progress", "completed", "blocked"];
const WORK_LOG_HEADING = "## Work Log";

function taskStateFolders(root: ProjectRoot): Record<TaskState, string> {
  return {
    pending: root.tasksPending,
    "in-progress": root.tasksInProgress,
    completed: root.tasksCompleted,
    blocked: root.tasksBlocked,
  };
}

function taskMatchesId(fileName: string, taskId: string): boolean {
  const stem = fileName.slice(0, -".md".length);
  return stem === taskId || stem.startsWith(`${taskId}-`);
}

/** First task file for `taskId` in the folders, searched in order; names sort like Python's `sorted`. */
function findTaskFile(taskId: string, folders: readonly string[]): string | undefined {
  for (const folder of folders) {
    if (!existsSync(folder)) continue;
    const names = readdirSync(folder)
      .filter((name) => name.endsWith(".md") && !name.startsWith("TEMPLATE-"))
      .sort(compareCodePoints);
    const match = names.find((name) => taskMatchesId(name, taskId));
    if (match !== undefined) return join(folder, match);
  }
  return undefined;
}

function compareCodePoints(left: string, right: string): number {
  const leftPoints = Array.from(left, (char) => char.codePointAt(0) ?? 0);
  const rightPoints = Array.from(right, (char) => char.codePointAt(0) ?? 0);
  const shared = Math.min(leftPoints.length, rightPoints.length);
  for (let index = 0; index < shared; index += 1) {
    const difference = (leftPoints[index] ?? 0) - (rightPoints[index] ?? 0);
    if (difference !== 0) return difference;
  }
  return leftPoints.length - rightPoints.length;
}

/** Splits like Python's `str.splitlines`: every line boundary, and no trailing empty line. */
function splitLines(text: string): string[] {
  const lines = text.split(/\r\n|[\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]/);
  if (lines[lines.length - 1] === "") lines.pop();
  return lines;
}

/**
 * Appends a "Blocked" session entry at the end of the Work Log section.
 * Mirrors the Python CLI exactly, including B-018: with no Work Log heading the entry lands above the new heading.
 */
function appendWorkLogEntry(path: string, reason: string): void {
  const { model, body } = readArtifact(path, "task");
  let lines = splitLines(body);

  let start = lines.indexOf(WORK_LOG_HEADING);
  if (start === -1) {
    lines.push("", WORK_LOG_HEADING, "");
    start = lines.length - 3;
  }

  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    if (lines[index]?.startsWith("## ")) {
      end = index;
      break;
    }
  }

  const sessionNumbers = lines
    .slice(start, end)
    .map((line) => /^### Session ([0-9]+)\b/.exec(line))
    .filter((match): match is RegExpExecArray => match !== null)
    .map((match) => Number(match[1]));
  const nextSession = Math.max(0, ...sessionNumbers) + 1;

  const entry = ["", `### Session ${nextSession} \u2014 ${today()}`, `Blocked: ${reason}`];
  lines = [...lines.slice(0, end), ...entry, ...lines.slice(end)];
  writeArtifact(path, model, `${lines.join("\n").trimEnd()}\n`, { overwrite: true });
}

interface Transition {
  readonly sourceStates: readonly TaskState[];
  readonly destinationState: TaskState;
  readonly beforeTransition?: (source: string) => void;
}

function transitionTask(root: ProjectRoot, taskId: string, transition: Transition): Result {
  const folders = taskStateFolders(root);
  const { destinationState } = transition;

  const inDestination = findTaskFile(taskId, [folders[destinationState]]);
  if (inDestination !== undefined) {
    return {
      status: 0,
      payload: { id: taskId, path: realpathSync(inDestination), changed: false },
      message: `Task ${taskId} already in ${destinationState}.`,
    };
  }

  const source = findTaskFile(
    taskId,
    transition.sourceStates.map((state) => folders[state]),
  );
  if (source === undefined) {
    const searched = TASK_STATES.map((state) => folders[state]).join(", ");
    return failure(`Task '${taskId}' not found. Searched folders: ${searched}`);
  }

  transition.beforeTransition?.(source);

  const destination = join(folders[destinationState], basename(source));
  mkdirSync(folders[destinationState], { recursive: true });
  updateStatus(source, destinationState);
  moveArtifact(source, destination);
  return success({ id: taskId, path: realpathSync(destination), changed: true });
}

function requireId(input: CommandInput, command: string): string | Result {
  const { id } = input;
  if (typeof id !== "string" || id === "") {
    return failure(`A non-empty 'id' is required to ${command}.`);
  }
  return id;
}

function transitionHandler(command: string, transition: Transition): RootHandler {
  return (root, input) => {
    const id = requireId(input, command);
    return typeof id === "string" ? transitionTask(root, id, transition) : id;
  };
}

/** Moves a pending task to in-progress. */
export const startTask: RootHandler = transitionHandler("start a task", {
  sourceStates: ["pending"],
  destinationState: "in-progress",
});

/** Moves an in-progress task to completed. */
export const completeTask: RootHandler = transitionHandler("complete a task", {
  sourceStates: ["in-progress"],
  destinationState: "completed",
});

/** Moves a blocked task back to in-progress. */
export const unblockTask: RootHandler = transitionHandler("unblock a task", {
  sourceStates: ["blocked"],
  destinationState: "in-progress",
});

/** Moves a task from any state to blocked and records the reason in its Work Log. */
export const blockTask: RootHandler = (root, input) => {
  const id = requireId(input, "block a task");
  if (typeof id !== "string") return id;
  const { reason } = input;
  if (typeof reason !== "string" || reason === "") {
    return failure("A non-empty 'reason' is required to block a task.");
  }
  return transitionTask(root, id, {
    sourceStates: TASK_STATES,
    destinationState: "blocked",
    beforeTransition: (source) => appendWorkLogEntry(source, reason),
  });
};
