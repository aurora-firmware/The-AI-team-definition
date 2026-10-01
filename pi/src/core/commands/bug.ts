import { existsSync, mkdirSync, readdirSync, realpathSync } from "node:fs";
import { basename, join } from "node:path";
import { ArtifactExists, moveArtifact, updateStatus } from "../fs.js";
import { splitFrontmatter } from "../frontmatter.js";
import { nextBugId } from "../ids.js";
import { createArtifactWithLock, LockTimeout } from "../lock.js";
import type { ProjectRoot } from "../locator.js";
import type { Bug } from "../models.js";
import { failure, success, type Result } from "../result.js";
import { today } from "../runtime.js";
import { slugify } from "../slug.js";
import { loadTemplate } from "../templates.js";
import type { CommandInput, RootHandler } from "./handler.js";

const BUG_SEVERITIES = ["critical", "high", "medium", "low"];
const TITLE_PLACEHOLDER = "# [Bug Title]";

type BugState = "open" | "in-progress" | "resolved";

/** Creates an open bug from the bundled template; the ID is allocated and the file written under the lock. */
export const createBug: RootHandler = (root, input) => {
  const { title, severity = "medium", task } = input;
  if (typeof title !== "string" || title === "") {
    return failure("A non-empty 'title' is required to create a bug.");
  }
  if (typeof severity !== "string" || !BUG_SEVERITIES.includes(severity)) {
    return failure(
      `Invalid bug severity ${JSON.stringify(severity)}.`,
      `Use one of: ${BUG_SEVERITIES.join(", ")}.`,
    );
  }
  if (task !== undefined && task !== null && typeof task !== "string") {
    return failure("The bug 'task' value must be a string.");
  }

  try {
    const [id, destination] = createArtifactWithLock(root.projectDir, {
      allocateId: () => nextBugId(root),
      build: (bugId) => {
        const template = loadTemplate("bug").toString("utf-8");
        const { body } = splitFrontmatter(template, "the bug template");
        const model: Bug = {
          kind: "bug",
          id: bugId,
          title,
          severity,
          status: "open",
          created: today(),
          task: task ?? undefined,
          sourceMap: undefined,
        };
        return [
          join(root.bugsOpen, `${bugId}-${slugify(title)}.md`),
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

function bugStateFolders(root: ProjectRoot): Record<BugState, string> {
  return {
    open: root.bugsOpen,
    "in-progress": root.bugsInProgress,
    resolved: root.bugsResolved,
  };
}

function bugMatchesId(fileName: string, bugId: string): boolean {
  const stem = fileName.slice(0, -".md".length);
  return stem === bugId || stem.startsWith(`${bugId}-`);
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

/** First bug file for `bugId` in `folder`; names sort like Python's `sorted`. */
function findBugFile(bugId: string, folder: string): string | undefined {
  if (!existsSync(folder)) return undefined;
  const match = readdirSync(folder)
    .filter((name) => name.endsWith(".md") && !name.startsWith("TEMPLATE-"))
    .sort(compareCodePoints)
    .find((name) => bugMatchesId(name, bugId));
  return match === undefined ? undefined : join(folder, match);
}

function transitionBug(
  root: ProjectRoot,
  bugId: string,
  sourceState: BugState,
  destinationState: BugState,
): Result {
  const folders = bugStateFolders(root);

  const inDestination = findBugFile(bugId, folders[destinationState]);
  if (inDestination !== undefined) {
    return {
      status: 0,
      payload: { id: bugId, path: realpathSync(inDestination), changed: false },
      message: `Bug ${bugId} already in ${destinationState}.`,
    };
  }

  const source = findBugFile(bugId, folders[sourceState]);
  if (source === undefined) {
    const searched = [folders.open, folders["in-progress"], folders.resolved].join(", ");
    return failure(`Bug '${bugId}' not found. Searched folders: ${searched}`);
  }

  const destination = join(folders[destinationState], basename(source));
  mkdirSync(folders[destinationState], { recursive: true });
  updateStatus(source, destinationState);
  moveArtifact(source, destination);
  return success({ id: bugId, path: realpathSync(destination), changed: true });
}

function transitionHandler(
  command: string,
  sourceState: BugState,
  destinationState: BugState,
): RootHandler {
  return (root, input: CommandInput) => {
    const { id } = input;
    if (typeof id !== "string" || id === "") {
      return failure(`A non-empty 'id' is required to ${command}.`);
    }
    return transitionBug(root, id, sourceState, destinationState);
  };
}

/** Moves an open bug to in-progress. */
export const startBug: RootHandler = transitionHandler("start a bug", "open", "in-progress");

/** Moves an in-progress bug to resolved. */
export const resolveBug: RootHandler = transitionHandler("resolve a bug", "in-progress", "resolved");
