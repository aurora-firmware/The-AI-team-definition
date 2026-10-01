import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { listBugs, listSpecs, listTasks } from "../src/core/commands/list.js";
import { showArtifact } from "../src/core/commands/show.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "read-handlers-"));
  mkdirSync(join(repo, "project"));
  root = findProjectRoot(repo, { env: {} });
  for (const directory of [root.tasksPending, root.bugsOpen, root.specs]) {
    mkdirSync(directory, { recursive: true });
  }
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
});

function seed(folder: string, name: string, text: string): void {
  writeFileSync(join(folder, name), text);
}

const task = (id: string) =>
  `---\nid: ${id}\ntitle: Task ${id}\nstatus: pending\npriority: low\nassigned-role: developer\ncreated: '2026-01-10'\n---\n\n# Task ${id}\n`;

describe("list handlers", () => {
  it("skips templates and placeholders and orders files by name", () => {
    seed(root.tasksPending, "T-002-b.md", task("T-002"));
    seed(root.tasksPending, "T-001-a.md", task("T-001"));
    seed(root.tasksPending, "TEMPLATE-task.md", "not parsed");
    seed(root.tasksPending, ".gitkeep", "");

    const ids = (listTasks(root, {}).payload as unknown as { id: string }[]).map((row) => row.id);
    expect(ids).toEqual(["T-001", "T-002"]);
  });

  it("returns no rows for a state that does not exist", () => {
    seed(root.tasksPending, "T-001-a.md", task("T-001"));
    expect(listTasks(root, { state: "archived" }).payload).toEqual([]);
  });

  it("returns no rows when a state folder is missing", () => {
    expect(listBugs(root, { state: "resolved" }).payload).toEqual([]);
  });

  it("identifies a legacy spec without an id by its file stem", () => {
    seed(
      root.specs,
      "legacy-spec.md",
      "---\ntitle: Legacy\nversion: '1.0'\nstatus: approved\ncreated: '2026-01-01'\nauthor: me\n---\n\n# Legacy\n",
    );
    expect(listSpecs(root, {}).payload).toEqual([
      { id: "legacy-spec", title: "Legacy", status: "approved", version: "1.0" },
    ]);
  });
});

describe("show handler", () => {
  it("fails with the searched roots when nothing matches", () => {
    const result = showArtifact(root, { identifier: "T-999" });
    expect(result.status).toBe(1);
    expect(result.message).toBe(
      `Artifact 'T-999' not found. Searched roots: ${root.tasksPending}, ${root.tasksInProgress}, ` +
        `${root.tasksCompleted}, ${root.tasksBlocked}, ${root.bugsOpen}, ${root.bugsInProgress}, ` +
        `${root.bugsResolved}, ${root.specs}, ${root.decisions}`,
    );
  });

  it("lists every match when the identifier is ambiguous", () => {
    seed(root.tasksPending, "T-001-a.md", task("T-001"));
    seed(root.tasksPending, "T-002-a.md", task("T-002"));
    const result = showArtifact(root, { identifier: "-a" });
    expect(result.status).toBe(1);
    expect(result.message).toBe(
      `Multiple artifacts matched '-a':\n- ${join(root.tasksPending, "T-001-a.md")}\n- ${join(root.tasksPending, "T-002-a.md")}`,
    );
  });

  it("requires a non-empty identifier", () => {
    expect(showArtifact(root, {}).status).toBe(1);
  });
});
