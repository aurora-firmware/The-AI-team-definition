import { join } from "node:path";
import { ArtifactExists } from "../fs.js";
import { splitFrontmatter } from "../frontmatter.js";
import { nextTaskId } from "../ids.js";
import { createArtifactWithLock, LockTimeout } from "../lock.js";
import type { Task } from "../models.js";
import { failure, success } from "../result.js";
import { today } from "../runtime.js";
import { slugify } from "../slug.js";
import { loadTemplate } from "../templates.js";
import { notImplemented } from "./handler.js";
import type { RootHandler } from "./handler.js";

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

export const startTask: RootHandler = notImplemented("task start");
export const completeTask: RootHandler = notImplemented("task complete");
export const unblockTask: RootHandler = notImplemented("task unblock");
export const blockTask: RootHandler = notImplemented("task block");
