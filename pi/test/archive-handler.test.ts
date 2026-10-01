import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { archiveArtifacts } from "../src/core/commands/archive.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;
let originalToday: string | undefined;

const task = (id: string, created: string): string =>
  `---\nid: ${id}\ntitle: A task\nstatus: completed\npriority: high\nassigned-role: developer\ncreated: '${created}'\n---\n\n# A task\n`;
const bug = (id: string, created: string): string =>
  `---\nid: ${id}\ntitle: A bug\nstatus: resolved\nseverity: high\ncreated: '${created}'\n---\n\n# A bug\n`;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "archive-handler-"));
  mkdirSync(join(repo, "project/tasks/completed"), { recursive: true });
  mkdirSync(join(repo, "project/bugs/resolved"), { recursive: true });
  writeFileSync(join(repo, "project/tasks/completed/T-001-old.md"), task("T-001", "2026-01-30"));
  writeFileSync(join(repo, "project/tasks/completed/T-002-cutoff.md"), task("T-002", "2026-01-30"));
  writeFileSync(join(repo, "project/tasks/completed/T-003-recent.md"), task("T-003", "2026-02-20"));
  writeFileSync(join(repo, "project/bugs/resolved/B-001-old.md"), bug("B-001", "2025-11-30"));
  root = findProjectRoot(repo, { env: {} });
  originalToday = process.env["AI_TEAM_TODAY"];
  process.env["AI_TEAM_TODAY"] = "2026-03-01";
});

afterEach(() => {
  if (originalToday === undefined) delete process.env["AI_TEAM_TODAY"];
  else process.env["AI_TEAM_TODAY"] = originalToday;
  rmSync(repo, { recursive: true, force: true });
});

const sources = (input: Record<string, unknown>): string[] =>
  (archiveArtifacts(root, input).payload as unknown as { moves: { source: string }[] }).moves.map(
    (move) => move.source,
  );

describe("archive handler", () => {
  it("rejects a malformed olderThan value", () => {
    const result = archiveArtifacts(root, { olderThan: "soon" });
    expect(result.status).toBe(1);
    expect(result.message).toBe("Invalid --older-than 'soon'. Expected format: <number><d|w|m|y>.");
  });

  it("archives only artifacts created strictly before the cutoff", () => {
    // 30d before 2026-03-01 is 2026-01-30: artifacts created that day stay.
    expect(sources({ olderThan: "30d" })).toEqual([
      join(root.bugsResolved, "B-001-old.md"),
    ]);
    expect(sources({ olderThan: "29d" })).toContain(join(root.tasksCompleted, "T-001-old.md"));
  });

  it("defaults olderThan to 90 days", () => {
    expect(sources({})).toEqual([join(root.bugsResolved, "B-001-old.md")]);
  });

  it("moves files into month buckets when not a dry run", () => {
    const result = archiveArtifacts(root, { olderThan: "29d" });
    expect(result.payload).toMatchObject({ dry_run: false });
    expect(existsSync(join(root.projectDir, "archive/2026-01/T-001-old.md"))).toBe(true);
    expect(existsSync(join(root.tasksCompleted, "T-001-old.md"))).toBe(false);
  });

  it("changes nothing on a dry run but reports the moves", () => {
    const result = archiveArtifacts(root, { olderThan: "29d", dryRun: true });
    expect((result.payload as { dry_run: boolean }).dry_run).toBe(true);
    expect(sources({ olderThan: "29d", dryRun: true }).length).toBe(3);
    expect(existsSync(join(root.projectDir, "archive"))).toBe(false);
    expect(existsSync(join(root.tasksCompleted, "T-001-old.md"))).toBe(true);
  });
});
