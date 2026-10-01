import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  nextAdrId,
  nextBugId,
  nextChangeRequestId,
  nextSpecId,
  nextTaskId,
} from "../src/core/ids.js";
import { findProjectRoot } from "../src/core/locator.js";
import type { ProjectRoot } from "../src/core/locator.js";

const fixturesRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "fixtures", "parity");

interface FixtureEntry {
  readonly path: string;
  readonly type: "dir" | "file";
  readonly text?: string;
}

let repo: string;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "ai-team-ids-"));
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
});

function touch(relativePath: string, text = ""): void {
  const path = join(repo, "project", relativePath);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, text);
}

function projectRoot(): ProjectRoot {
  mkdirSync(join(repo, "project"), { recursive: true });
  return findProjectRoot(repo, { root: repo });
}

/** Materialises a parity fixture's before-tree in `repo` and returns the id the case expects. */
function loadFixture(name: string): string {
  const entries: FixtureEntry[] = JSON.parse(
    readFileSync(join(fixturesRoot, name, "before.json"), "utf-8"),
  );
  for (const entry of entries) {
    const path = join(repo, entry.path);
    if (entry.type === "dir") mkdirSync(path, { recursive: true });
    else {
      mkdirSync(dirname(path), { recursive: true });
      writeFileSync(path, entry.text ?? "");
    }
  }
  const spec = JSON.parse(readFileSync(join(fixturesRoot, name, "case.json"), "utf-8"));
  return spec.expected.payload.id;
}

describe("next IDs match the parity fixtures", () => {
  const cases: [string, (root: ProjectRoot) => string][] = [
    ["task-new--defaults", nextTaskId],
    ["task-new--id-gap", nextTaskId],
    ["task-new--blocked-only-ids", nextTaskId],
    ["task-new--completed-only-ids", nextTaskId],
    ["bug-new--defaults", nextBugId],
    ["bug-new--id-gap", nextBugId],
    ["bug-new--resolved-only-ids", nextBugId],
    ["spec-new--defaults", nextSpecId],
    ["spec-new--id-gap", nextSpecId],
    ["spec-new--archived-only-ids", nextSpecId],
    ["spec-new--frontmatter-id-beyond-filename", nextSpecId],
    ["adr-new--defaults", nextAdrId],
    ["adr-new--id-gap", nextAdrId],
    ["change-request-new--id-gap", (root) => nextChangeRequestId([root.changeRequests])],
  ];

  it.each(cases)("%s", (name, next) => {
    const expected = loadFixture(name);
    expect(next(findProjectRoot(repo, { root: repo }))).toBe(expected);
  });
});

describe("nextTaskId", () => {
  it("returns T-001 when no task folder exists", () => {
    expect(nextTaskId(projectRoot())).toBe("T-001");
  });

  it("takes the highest number across all four state folders", () => {
    touch("tasks/pending/T-002-a.md");
    touch("tasks/in-progress/T-009-b.md");
    touch("tasks/completed/T-004-c.md");
    touch("tasks/blocked/T-007-d.md");
    expect(nextTaskId(projectRoot())).toBe("T-010");
  });

  it("ignores files that do not match the T-NNN-*.md pattern", () => {
    touch("tasks/pending/T-5-short.md");
    touch("tasks/pending/T-050-notes.txt");
    touch("tasks/pending/README.md");
    expect(nextTaskId(projectRoot())).toBe("T-001");
  });

  it("ignores directories named like artifacts", () => {
    mkdirSync(join(repo, "project", "tasks", "pending", "T-050-dir.md"), { recursive: true });
    expect(nextTaskId(projectRoot())).toBe("T-001");
  });

  it("grows past three digits", () => {
    touch("tasks/pending/T-999-a.md");
    expect(nextTaskId(projectRoot())).toBe("T-1000");
  });
});

describe("nextBugId", () => {
  it("takes the highest number across the bug state folders", () => {
    touch("bugs/open/B-003-a.md");
    touch("bugs/in-progress/B-005-b.md");
    touch("bugs/resolved/B-011-c.md");
    expect(nextBugId(projectRoot())).toBe("B-012");
  });
});

describe("nextSpecId", () => {
  it("includes specs/archive/", () => {
    touch("specs/S-002-a.md");
    touch("specs/archive/S-006-b.md");
    expect(nextSpecId(projectRoot())).toBe("S-007");
  });

  it("reads the id from frontmatter in files not named S-NNN", () => {
    touch("specs/legacy.md", '---\nid: "S-020"\ntitle: x\n---\n');
    expect(nextSpecId(projectRoot())).toBe("S-021");
  });

  it("accepts single-quoted and commented frontmatter ids", () => {
    touch("specs/a.md", "---\nid: 'S-004'  # note\n---\n");
    expect(nextSpecId(projectRoot())).toBe("S-005");
  });

  it("ignores ids that appear after the closing fence", () => {
    touch("specs/a.md", "---\ntitle: x\n---\nid: S-050\n");
    expect(nextSpecId(projectRoot())).toBe("S-001");
  });

  it("ignores files without frontmatter", () => {
    touch("specs/a.md", "id: S-050\n");
    expect(nextSpecId(projectRoot())).toBe("S-001");
  });

  it("ignores frontmatter ids of other kinds", () => {
    touch("specs/a.md", "---\nid: T-050\n---\n");
    expect(nextSpecId(projectRoot())).toBe("S-001");
  });
});

describe("nextAdrId and nextChangeRequestId", () => {
  it("allocates ADR ids from decisions/", () => {
    touch("decisions/ADR-004-x.md");
    expect(nextAdrId(projectRoot())).toBe("ADR-005");
  });

  it("allocates change request ids across the given directories", () => {
    touch("change-requests/CR-002-a.md");
    touch("other/CR-008-b.md");
    expect(
      nextChangeRequestId([
        join(repo, "project", "change-requests"),
        join(repo, "project", "other"),
        join(repo, "project", "missing"),
      ]),
    ).toBe("CR-009");
  });

  it("does not create any files", () => {
    nextAdrId(projectRoot());
    expect(readdirSync(join(repo, "project"))).toEqual([]);
  });
});
