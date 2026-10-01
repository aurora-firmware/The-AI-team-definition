import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { checkLayout } from "../src/core/layout.js";

const fixturesRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "fixtures", "parity");
const scaffoldDirs: Record<string, string[]> = JSON.parse(
  readFileSync(join(dirname(fileURLToPath(import.meta.url)), "..", "resources", "scaffold-dirs.json"), "utf-8"),
);

interface TreeEntry {
  readonly path: string;
  readonly type: string;
  readonly text?: string;
  readonly base64?: string;
}

interface ExpectedFinding {
  readonly level: number;
  readonly path: string;
  readonly message: string;
  readonly suggested_fix: string;
}

interface CheckLayoutCase {
  readonly version: string;
  readonly expected: { readonly payload: { readonly findings: readonly ExpectedFinding[] } };
}

const tempRoots: string[] = [];

afterEach(() => {
  for (const root of tempRoots.splice(0)) rmSync(root, { recursive: true, force: true });
});

function materialise(entries: readonly TreeEntry[]): string {
  const root = mkdtempSync(join(tmpdir(), "layout-parity-"));
  tempRoots.push(root);
  for (const entry of entries) {
    const target = join(root, entry.path);
    if (entry.type === "dir") {
      mkdirSync(target, { recursive: true });
    } else if (entry.text !== undefined) {
      writeFileSync(target, entry.text, "utf-8");
    } else {
      writeFileSync(target, Buffer.from(entry.base64 ?? "", "base64"));
    }
  }
  return root;
}

function readJson<T>(name: string, file: string): T {
  return JSON.parse(readFileSync(join(fixturesRoot, name, file), "utf-8"));
}

const caseNames = readdirSync(fixturesRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory() && entry.name.startsWith("check-layout--"))
  .map((entry) => entry.name)
  .sort();

describe("checkLayout reproduces the T-093 check-layout findings", () => {
  it("discovers the check-layout fixture trees", () => {
    expect(caseNames.length).toBeGreaterThanOrEqual(23);
  });

  it.each(caseNames)("%s", (name) => {
    const spec = readJson<CheckLayoutCase>(name, "case.json");
    const repo = materialise(readJson<TreeEntry[]>(name, "before.json"));

    const findings = checkLayout(repo, { currentVersion: spec.version });

    const normalised = findings.map((finding) => ({
      level: finding.level,
      path: finding.path,
      message: finding.problem.split(repo).join("<ROOT>"),
      suggested_fix: finding.suggestedFix,
    }));
    expect(normalised).toEqual(spec.expected.payload.findings);
  });
});

const MARKER = (tools: string): string =>
  `[project]\ndir = "project"\n\n[init]\ntools = ${tools}\nframework_version = "1.0.0"\n`;

describe("checkLayout scaffold directory list", () => {
  it("expects every generated claude scaffold directory when only claude is configured", () => {
    const repo = materialise([
      { path: ".ai-team.toml", type: "file", text: MARKER('["claude"]') },
      { path: "project", type: "dir" },
    ]);

    const paths = checkLayout(repo, { currentVersion: "1.0.0" })
      .filter((finding) => finding.level === 1)
      .map((finding) => finding.path);

    expect(paths).toContain(".claude");
    for (const relative of scaffoldDirs.claude ?? []) expect(paths).toContain(`.claude/${relative}`);
    for (const relative of scaffoldDirs.project ?? []) expect(paths).toContain(`project/${relative}`);
    expect(paths.some((path) => path.startsWith(".codex"))).toBe(false);
  });

  it("expects the codex scaffold directories when codex is configured", () => {
    const repo = materialise([
      { path: ".ai-team.toml", type: "file", text: MARKER('["codex"]') },
      { path: "project", type: "dir" },
    ]);

    const paths = checkLayout(repo, { currentVersion: "1.0.0" })
      .filter((finding) => finding.level === 1)
      .map((finding) => finding.path);

    for (const relative of scaffoldDirs.codex ?? []) expect(paths).toContain(`.codex/${relative}`);
    expect(paths.some((path) => path.startsWith(".claude"))).toBe(false);
  });
});

describe("checkLayout findings", () => {
  it("keeps the suggested fix apart from the problem text", () => {
    const repo = materialise([{ path: "project", type: "dir" }]);

    const [first] = checkLayout(repo, { currentVersion: "1.0.0" });

    expect(first?.suggestedFix).toMatch(/\S/);
    expect(first?.problem).not.toContain(first?.suggestedFix ?? "");
  });

  it("reports the unsupported tools with Python-style list formatting", () => {
    const repo = materialise([
      { path: ".ai-team.toml", type: "file", text: MARKER('["claude", 7, true, "it\'s"]') },
      { path: "project", type: "dir" },
    ]);

    const problems = checkLayout(repo, { currentVersion: "1.0.0" }).map((finding) => finding.problem);

    expect(problems).toContain(
      "Marker contains unsupported or invalid configured tools: [7, True, \"it's\"].",
    );
  });

  it("reads the current version from the runtime override when none is passed", () => {
    const repo = materialise([
      { path: ".ai-team.toml", type: "file", text: MARKER("[]") },
      { path: "project", type: "dir" },
    ]);

    const levelFour = checkLayout(repo, { env: { AI_TEAM_FRAMEWORK_VERSION: "2.0.0" } }).filter(
      (finding) => finding.level === 4,
    );

    expect(levelFour.map((finding) => finding.problem)).toEqual([
      "Configured framework version '1.0.0' does not exactly match current CLI version '2.0.0'.",
    ]);
  });
});
