import { existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createTask } from "../src/core/commands/task.js";
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
