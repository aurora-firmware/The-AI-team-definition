import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { validateArtifacts } from "../src/core/commands/validate.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;

const task = (id: string, status: string): string =>
  `---\nid: ${id}\ntitle: A task\nstatus: ${status}\npriority: high\nassigned-role: developer\ncreated: '2026-01-01'\n---\n\n# A task\n`;
const bug = (id: string): string =>
  `---\nid: ${id}\ntitle: A bug\nstatus: open\nseverity: high\ncreated: '2026-01-01'\ntask: T-099\n---\n\n# A bug\n`;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "validate-handler-"));
  for (const folder of ["tasks/pending", "bugs/open", "specs"]) {
    mkdirSync(join(repo, "project", folder), { recursive: true });
  }
  writeFileSync(join(repo, "project/tasks/pending/T-001-wrong.md"), task("T-001", "completed"));
  writeFileSync(join(repo, "project/bugs/open/B-001-orphan.md"), bug("B-001"));
  root = findProjectRoot(repo, { env: {} });
});

afterEach(() => rmSync(repo, { recursive: true, force: true }));

const codes = (input: Record<string, unknown>): string[] =>
  (validateArtifacts(root, input).payload as unknown as { code: string }[]).map((f) => f.code);

describe("validate handler", () => {
  it("validates every scope when no flags are given", () => {
    expect(codes({})).toEqual(["status-mismatch", "bug-task-missing"]);
  });

  it("validates every scope when all is set even alongside other flags", () => {
    expect(codes({ all: true, tasks: true })).toEqual(["status-mismatch", "bug-task-missing"]);
  });

  it("limits validation to the selected scope", () => {
    expect(codes({ bugs: true })).toEqual(["bug-task-missing"]);
  });

  it("combines several scope flags", () => {
    expect(codes({ tasks: true, bugs: true })).toEqual(["status-mismatch", "bug-task-missing"]);
  });

  it("returns status 1 when a finding is an error", () => {
    expect(validateArtifacts(root, { tasks: true }).status).toBe(1);
  });

  it("returns status 0 and an empty payload when the selected scope is clean", () => {
    const result = validateArtifacts(root, { specs: true });
    expect(result.status).toBe(0);
    expect(result.payload).toEqual([]);
  });
});
