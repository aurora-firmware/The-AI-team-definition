import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { findProjectRoot } from "../src/core/locator.js";
import { validateProject } from "../src/core/validate.js";
import type { ValidateScopes } from "../src/core/validate.js";

const fixturesRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "fixtures", "parity");

interface TreeEntry {
  readonly path: string;
  readonly type: string;
  readonly text?: string;
  readonly base64?: string;
}

interface Finding {
  readonly path: string;
  readonly level: string;
  readonly code: string;
  readonly message: string;
}

interface ValidateCase {
  readonly input: Record<string, boolean>;
  readonly project_dir: string;
  readonly expected: { readonly payload: readonly Finding[] };
}

const tempRoots: string[] = [];

afterEach(() => {
  for (const root of tempRoots.splice(0)) rmSync(root, { recursive: true, force: true });
});

function materialise(entries: readonly TreeEntry[]): string {
  const root = mkdtempSync(join(tmpdir(), "validate-parity-"));
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

/** The command layer (T-118) maps no flags to every scope; the core takes explicit scopes. */
function scopesOf(input: Record<string, boolean>): ValidateScopes {
  const none = !Object.values(input).some(Boolean);
  const all = input.all === true || none;
  return {
    tasks: all || input.tasks === true,
    bugs: all || input.bugs === true,
    specs: all || input.specs === true,
    adrs: all || input.adrs === true,
    changeRequests: all || input.changeRequests === true,
  };
}

const caseNames = readdirSync(fixturesRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory() && entry.name.startsWith("validate--"))
  .map((entry) => entry.name)
  .sort();

describe("validateProject reproduces the T-092 findings", () => {
  it("discovers the validate fixture trees", () => {
    expect(caseNames.length).toBeGreaterThanOrEqual(15);
  });

  it.each(caseNames)("%s", (name) => {
    const spec: ValidateCase = JSON.parse(
      readFileSync(join(fixturesRoot, name, "case.json"), "utf-8"),
    );
    const before: TreeEntry[] = JSON.parse(
      readFileSync(join(fixturesRoot, name, "before.json"), "utf-8"),
    );
    const repo = materialise(before);
    const root = findProjectRoot(repo, { root: repo, projectDir: spec.project_dir });

    const findings = validateProject(root, scopesOf(spec.input));

    const normalised = findings.map((finding) => ({
      ...finding,
      message: finding.message.split(root.repo).join("<ROOT>"),
    }));
    expect(normalised).toEqual(spec.expected.payload);
  });
});

describe("validateProject findings", () => {
  it("reports a malformed frontmatter with the parser message", () => {
    const repo = materialise([
      { path: "project", type: "dir" },
      { path: "project/tasks", type: "dir" },
      { path: "project/tasks/pending", type: "dir" },
      { path: "project/tasks/pending/T-001-x.md", type: "file", text: "no fence\n" },
    ]);
    const root = findProjectRoot(repo, { root: repo });

    const [finding] = validateProject(root, { tasks: true });

    expect(finding?.code).toBe("frontmatter-invalid");
    expect(finding?.path).toBe("project/tasks/pending/T-001-x.md");
  });

  it("reports nothing when no scope is selected", () => {
    const repo = materialise([{ path: "project", type: "dir" }]);
    const root = findProjectRoot(repo, { root: repo });

    expect(validateProject(root, {})).toEqual([]);
  });
});
