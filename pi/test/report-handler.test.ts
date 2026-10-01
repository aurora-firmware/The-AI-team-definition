import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { writeReport } from "../src/core/commands/report.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;
let otherDirectory: string;
let originalCwd: string;
let originalToday: string | undefined;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "report-handler-"));
  otherDirectory = mkdtempSync(join(tmpdir(), "report-cwd-"));
  mkdirSync(join(repo, "project"));
  root = findProjectRoot(repo, { env: {} });
  originalCwd = process.cwd();
  originalToday = process.env["AI_TEAM_TODAY"];
  process.env["AI_TEAM_TODAY"] = "2026-03-04";
});

afterEach(() => {
  process.chdir(originalCwd);
  if (originalToday === undefined) delete process.env["AI_TEAM_TODAY"];
  else process.env["AI_TEAM_TODAY"] = originalToday;
  rmSync(repo, { recursive: true, force: true });
  rmSync(otherDirectory, { recursive: true, force: true });
});

describe("report handler", () => {
  it("writes the dated report under docs/reports by default and returns its content", () => {
    const result = writeReport(root, {});

    const expectedPath = join(root.docs, "reports", "progress-report-2026-03-04.md");
    const payload = result.payload as { path: string; content: string };
    expect(result.status).toBe(0);
    expect(payload.path).toBe(expectedPath);
    expect(readFileSync(expectedPath, "utf-8")).toBe(payload.content);
    expect(payload.content).toContain("# Progress Report — 2026-03-04");
    expect(payload.content).toContain("| none | n/a | No active specs |");
  });

  it("writes to the out path, resolved against the project start directory rather than process.cwd()", () => {
    process.chdir(otherDirectory);

    const result = writeReport(root, { out: "nested/custom.md" });

    const expectedPath = join(repo, "nested", "custom.md");
    expect((result.payload as { path: string }).path).toBe(expectedPath);
    expect(existsSync(expectedPath)).toBe(true);
    expect(existsSync(join(otherDirectory, "nested"))).toBe(false);
  });

  it("writes to an absolute out path unchanged", () => {
    const target = join(otherDirectory, "abs.md");

    const result = writeReport(root, { out: target });

    expect((result.payload as { path: string }).path).toBe(target);
    expect(existsSync(target)).toBe(true);
  });

  it("lists specs and counts from the seeded artifacts", () => {
    mkdirSync(root.specs, { recursive: true });
    writeFileSync(
      join(root.specs, "S-001-x.md"),
      "---\ntitle: X\nversion: '1.0'\nstatus: approved\ncreated: '2026-01-01'\nauthor: a\n---\n\n# X\n",
    );

    const content = (writeReport(root, {}).payload as { content: string }).content;

    expect(content).toContain("| S-001-x.md | approved | Current Gate 5 target |");
    expect(content).toContain("Active specs: 1.");
  });
});
