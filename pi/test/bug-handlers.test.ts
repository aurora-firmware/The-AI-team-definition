import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createBug, resolveBug, startBug } from "../src/core/commands/bug.js";
import { LOCK_FILENAME } from "../src/core/lock.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "bug-handlers-"));
  mkdirSync(join(repo, "project"));
  root = findProjectRoot(repo, { env: {} });
  for (const directory of [root.bugsOpen, root.bugsInProgress, root.bugsResolved]) {
    mkdirSync(directory, { recursive: true });
  }
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
});

function seedBug(folder: string, id: string, status: string): string {
  const path = join(folder, `${id}-example.md`);
  writeFileSync(
    path,
    `---\nid: ${id}\ntitle: Example\nseverity: medium\nstatus: ${status}\ncreated: '2026-01-10'\n---\n\n# Example\n`,
  );
  return path;
}

describe("bug new handler", () => {
  it("fails without writing when the title is missing", () => {
    expect(createBug(root, {}).status).toBe(1);
    expect(readdirSync(root.bugsOpen)).toEqual([]);
  });

  it("fails without writing when the severity is not an allowed choice", () => {
    const result = createBug(root, { title: "Bad", severity: "urgent" });
    expect(result.status).toBe(1);
    expect(result.message).toContain("urgent");
    expect(readdirSync(root.bugsOpen)).toEqual([]);
  });

  it("fails when the task value is not a string", () => {
    expect(createBug(root, { title: "Bad", task: 5 }).status).toBe(1);
  });

  it("creates an open bug with the title heading and releases the lock", () => {
    const result = createBug(root, { title: "Crash on save", severity: "high", task: "T-021" });
    expect(result.status).toBe(0);
    const text = readFileSync(join(root.bugsOpen, "B-001-crash-on-save.md"), "utf8");
    expect(text).toContain("severity: high");
    expect(text).toContain("task: T-021");
    expect(text).toContain("# Crash on save");
    expect(existsSync(join(root.projectDir, LOCK_FILENAME))).toBe(false);
  });
});

describe.each([
  ["start", startBug],
  ["resolve", resolveBug],
] as const)("bug %s handler", (_name, handler) => {
  it("fails when the id is missing", () => {
    expect(handler(root, {}).status).toBe(1);
  });
});

describe("bug start handler", () => {
  it("moves an open bug to in-progress and rewrites its status", () => {
    const source = seedBug(root.bugsOpen, "B-001", "open");
    const result = startBug(root, { id: "B-001" });
    expect(result.status).toBe(0);
    expect(existsSync(source)).toBe(false);
    expect(readFileSync(join(root.bugsInProgress, "B-001-example.md"), "utf8")).toContain(
      "status: in-progress",
    );
  });

  it("does not match a bug whose id merely starts with the requested id", () => {
    seedBug(root.bugsOpen, "B-0011", "open");
    expect(startBug(root, { id: "B-001" }).status).toBe(1);
  });

  it("rejects a resolved bug as not found", () => {
    seedBug(root.bugsResolved, "B-001", "resolved");
    expect(startBug(root, { id: "B-001" }).status).toBe(1);
  });
});

describe("bug resolve handler", () => {
  it("moves an in-progress bug to resolved", () => {
    seedBug(root.bugsInProgress, "B-001", "in-progress");
    expect(resolveBug(root, { id: "B-001" }).status).toBe(0);
    expect(readFileSync(join(root.bugsResolved, "B-001-example.md"), "utf8")).toContain(
      "status: resolved",
    );
  });

  it("reports an unchanged result when the bug is already resolved", () => {
    seedBug(root.bugsResolved, "B-001", "resolved");
    const result = resolveBug(root, { id: "B-001" });
    expect(result.status).toBe(0);
    expect(result.payload).toMatchObject({ id: "B-001", changed: false });
  });
});
