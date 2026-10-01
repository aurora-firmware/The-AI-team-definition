import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { blockTask, completeTask, createTask, startTask, unblockTask } from "../src/core/commands/task.js";
import { LOCK_FILENAME } from "../src/core/lock.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "task-handlers-"));
  mkdirSync(join(repo, "project"));
  root = findProjectRoot(repo, { env: {} });
  for (const directory of [
    root.tasksPending,
    root.tasksInProgress,
    root.tasksCompleted,
    root.tasksBlocked,
  ]) {
    mkdirSync(directory, { recursive: true });
  }
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
});

describe("task new handler", () => {
  it("fails without writing when the title is missing", () => {
    expect(createTask(root, {}).status).toBe(1);
    expect(readdirSync(root.tasksPending)).toEqual([]);
  });

  it("fails without writing when the priority is not an allowed choice", () => {
    const result = createTask(root, { title: "Bad priority", priority: "urgent" });
    expect(result.status).toBe(1);
    expect(result.message).toContain("urgent");
    expect(readdirSync(root.tasksPending)).toEqual([]);
  });

  it("releases the TS allocation lock after creating", () => {
    expect(createTask(root, { title: "Locked" }).status).toBe(0);
    expect(existsSync(join(root.projectDir, LOCK_FILENAME))).toBe(false);
  });
});

function seedTask(folder: string, id: string, status: string, extra = ""): string {
  const path = join(folder, `${id}-example.md`);
  writeFileSync(
    path,
    `---\nid: ${id}\ntitle: Example\nstatus: ${status}\npriority: medium\nassigned-role: developer\ncreated: '2026-01-10'\n---\n\n# Example\n${extra}`,
  );
  return path;
}

describe.each([
  ["start", startTask],
  ["complete", completeTask],
  ["unblock", unblockTask],
] as const)("task %s handler", (_name, handler) => {
  it("fails when the id is missing", () => {
    expect(handler(root, {}).status).toBe(1);
  });
});

describe("task start handler", () => {
  it("moves the file to in-progress and rewrites its status", () => {
    const source = seedTask(root.tasksPending, "T-001", "pending");
    const result = startTask(root, { id: "T-001" });
    expect(result.status).toBe(0);
    expect(existsSync(source)).toBe(false);
    const moved = join(root.tasksInProgress, "T-001-example.md");
    expect(readFileSync(moved, "utf8")).toContain("status: in-progress");
  });

  it("does not match a task whose id merely starts with the requested id", () => {
    seedTask(root.tasksPending, "T-0011", "pending");
    expect(startTask(root, { id: "T-001" }).status).toBe(1);
  });
});

describe("task block handler", () => {
  it("fails without moving the file when the reason is missing", () => {
    const source = seedTask(root.tasksPending, "T-001", "pending");
    expect(blockTask(root, { id: "T-001" }).status).toBe(1);
    expect(existsSync(source)).toBe(true);
  });

  it("numbers the entry after the highest existing session", () => {
    seedTask(
      root.tasksInProgress,
      "T-001",
      "in-progress",
      "\n## Work Log\n\n### Session 4 \u2014 2026-01-12\nWork.\n",
    );
    expect(blockTask(root, { id: "T-001", reason: "Stuck" }).status).toBe(0);
    const text = readFileSync(join(root.tasksBlocked, "T-001-example.md"), "utf8");
    expect(text).toContain("### Session 5 \u2014 ");
    expect(text).toContain("Blocked: Stuck");
  });
});
