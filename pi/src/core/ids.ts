import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import type { ProjectRoot } from "./locator.js";

/**
 * Artifact ID allocation, mirroring `ai_team.core.ids`: the next ID is the highest number found
 * in matching filenames across the kind's folders, plus one, zero-padded to three digits.
 * Callers wanting mutual exclusion wrap the scan and the write in `createArtifactWithLock`.
 */

const TASK_PATTERN = /^T-(\d{3})-.*\.md$/;
const BUG_PATTERN = /^B-(\d{3})-.*\.md$/;
const SPEC_PATTERN = /^S-(\d{3})-.*\.md$/;
const ADR_PATTERN = /^ADR-(\d{3})-.*\.md$/;
const CHANGE_REQUEST_PATTERN = /^CR-(\d{3})-.*\.md$/;
const SPEC_FRONTMATTER_ID_PATTERN = /^id:\s*["']?S-(\d{3})["']?\s*(?:#.*)?$/m;

/** Next task ID in T-NNN format across all task state folders. */
export function nextTaskId(root: ProjectRoot): string {
  return nextId(
    "T",
    [root.tasksPending, root.tasksInProgress, root.tasksCompleted, root.tasksBlocked],
    TASK_PATTERN,
  );
}

/** Next bug ID in B-NNN format across all bug state folders. */
export function nextBugId(root: ProjectRoot): string {
  return nextId("B", [root.bugsOpen, root.bugsInProgress, root.bugsResolved], BUG_PATTERN);
}

/** Next spec ID in S-NNN format across specs/ and specs/archive/, including ids in frontmatter. */
export function nextSpecId(root: ProjectRoot): string {
  const directories = [root.specs, join(root.specs, "archive")];
  const maxNumber = Math.max(
    maxMatchingNumber(directories, SPEC_PATTERN),
    maxSpecFrontmatterIdNumber(directories),
  );
  return formatId("S", maxNumber + 1);
}

/** Next ADR ID in ADR-NNN format from the decisions folder. */
export function nextAdrId(root: ProjectRoot): string {
  return nextId("ADR", [root.decisions], ADR_PATTERN);
}

/** Next CR-NNN identifier for the provided directories. */
export function nextChangeRequestId(searchDirectories: readonly string[]): string {
  return nextId("CR", searchDirectories, CHANGE_REQUEST_PATTERN);
}

function formatId(prefix: string, number: number): string {
  return `${prefix}-${String(number).padStart(3, "0")}`;
}

function nextId(prefix: string, directories: readonly string[], pattern: RegExp): string {
  return formatId(prefix, maxMatchingNumber(directories, pattern) + 1);
}

/** Regular files in `directory`; none when the directory does not exist. */
function listFiles(directory: string): string[] {
  if (!existsSync(directory)) return [];
  return readdirSync(directory).filter((name) => statSync(join(directory, name)).isFile());
}

function maxMatchingNumber(directories: readonly string[], pattern: RegExp): number {
  let maxNumber = 0;
  for (const directory of directories) {
    for (const name of listFiles(directory)) {
      const match = pattern.exec(name);
      if (match?.[1] !== undefined) maxNumber = Math.max(maxNumber, Number(match[1]));
    }
  }
  return maxNumber;
}

function maxSpecFrontmatterIdNumber(directories: readonly string[]): number {
  let maxNumber = 0;
  for (const directory of directories) {
    for (const name of listFiles(directory)) {
      const text = readFileSync(join(directory, name), "utf-8");
      if (!text.startsWith("---")) continue;
      const rest = text.slice(3);
      const closeIndex = rest.indexOf("\n---");
      if (closeIndex === -1) continue;
      const match = SPEC_FRONTMATTER_ID_PATTERN.exec(rest.slice(0, closeIndex));
      if (match?.[1] !== undefined) maxNumber = Math.max(maxNumber, Number(match[1]));
    }
  }
  return maxNumber;
}
