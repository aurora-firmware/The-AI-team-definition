import { mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import {
  dumpFrontmatter,
  extractBody,
  FrontmatterError,
  parseAdrText,
  parseBugText,
  parseChangeRequestText,
  parseSpecText,
  parseTask,
  parseTaskText,
} from "../src/core/models.js";
import type { ArtifactKind, ArtifactModel } from "../src/core/models.js";

const fixturesRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "fixtures", "parity");

interface TreeEntry {
  readonly path: string;
  readonly type: string;
  readonly text?: string;
}

function readTree(caseName: string, side: "before" | "after"): TreeEntry[] {
  return JSON.parse(readFileSync(join(fixturesRoot, caseName, `${side}.json`), "utf-8"));
}

const KIND_BY_FOLDER: ReadonlyArray<readonly [string, ArtifactKind]> = [
  ["/tasks/", "task"],
  ["/bugs/", "bug"],
  ["/specs/", "spec"],
  ["/decisions/", "adr"],
  ["/change-requests/", "change-request"],
];

function kindOfPath(path: string): ArtifactKind | undefined {
  return KIND_BY_FOLDER.find(([folder]) => path.includes(folder))?.[1];
}

function parseByKind(kind: ArtifactKind, text: string, path: string): ArtifactModel {
  switch (kind) {
    case "task":
      return parseTaskText(text, path);
    case "bug":
      return parseBugText(text, path);
    case "spec":
      return parseSpecText(text, path);
    case "adr":
      return parseAdrText(text, path);
    case "change-request":
      return parseChangeRequestText(text, path);
  }
}

const caseNames = readdirSync(fixturesRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

/** Markdown artifacts an after-tree holds that no before-tree file already had: the CLI wrote them. */
function writtenArtifacts(caseName: string): Array<readonly [string, ArtifactKind, string]> {
  const existing = new Set(readTree(caseName, "before").map((entry) => entry.text));
  return readTree(caseName, "after").flatMap((entry) => {
    const kind = kindOfPath(entry.path);
    const isArtifact = entry.type === "file" && entry.path.endsWith(".md") && kind !== undefined;
    if (!isArtifact || entry.text === undefined || existing.has(entry.text)) return [];
    return [[entry.path, kind, entry.text] as const];
  });
}

describe("dump reproduces the T-089 after-tree artifacts byte for byte", () => {
  const written = caseNames.flatMap((name) =>
    writtenArtifacts(name).map(([path, kind, text]) => [`${name}: ${path}`, kind, text] as const),
  );

  it("covers artifacts of all five kinds", () => {
    expect(new Set(written.map(([, kind]) => kind))).toEqual(
      new Set(["task", "bug", "spec", "adr", "change-request"]),
    );
  });

  it.each(written)("%s", (label, kind, text) => {
    const model = parseByKind(kind, text, label);
    expect(dumpFrontmatter(model, extractBody(text, label))).toBe(text);
  });
});

describe("a missing or malformed frontmatter reports the Python messages", () => {
  interface ValidateCase {
    readonly expected: {
      readonly payload: ReadonlyArray<{ code: string; message: string; path: string }>;
    };
  }

  const invalid = caseNames.flatMap((name) => {
    const spec: ValidateCase = JSON.parse(
      readFileSync(join(fixturesRoot, name, "case.json"), "utf-8"),
    );
    if (!name.startsWith("validate--") || !Array.isArray(spec.expected.payload)) return [];
    const before = readTree(name, "before");
    return spec.expected.payload
      .filter((finding) => finding.code === "frontmatter-invalid")
      .flatMap((finding) => {
        const text = before.find((entry) => entry.path === finding.path)?.text;
        const kind = kindOfPath(`/${finding.path}`);
        return text === undefined || kind === undefined
          ? []
          : [[`${name}: ${finding.path}`, kind, text, finding.path, finding.message] as const];
      });
  });

  it("finds validate cases that exercise the frontmatter errors", () => {
    expect(invalid.length).toBeGreaterThan(0);
  });

  it.each(invalid)("%s", (_label, kind, text, relativePath, message) => {
    expect(() => parseByKind(kind, text, `<ROOT>/${relativePath}`)).toThrow(
      new FrontmatterError(message),
    );
  });
});

describe("parse", () => {
  const taskText = [
    "---",
    'id: "T-002"',
    'title: "Implement models"',
    "status: in-progress",
    "priority: medium",
    "assigned-role: developer",
    "created: 2026-05-10",
    'spec: "S-005"',
    "---",
    "",
    "Body.",
    "",
  ].join("\n");

  it("reads every task field as a string, including a date and the hyphenated key", () => {
    expect(parseTaskText(taskText, "t.md")).toMatchObject({
      kind: "task",
      id: "T-002",
      title: "Implement models",
      status: "in-progress",
      priority: "medium",
      assignedRole: "developer",
      created: "2026-05-10",
      spec: "S-005",
    });
  });

  it("names the raw YAML key when assigned-role is missing", () => {
    const text = taskText.replace("assigned-role: developer\n", "");
    expect(() => parseTaskText(text, "/p/t.md")).toThrow(
      "Required frontmatter field 'assigned-role' is missing or null in /p/t.md",
    );
  });

  it("treats an explicit null as missing", () => {
    const text = taskText.replace("priority: medium", "priority: ~");
    expect(() => parseTaskText(text, "t.md")).toThrow(/'priority' is missing or null/);
  });

  it("stringifies scalars the way Python str() does", () => {
    const text = "---\nid: 7\ntitle: true\nstatus: 1.0\npriority: 0x1F\nassigned-role: d\ncreated: 2026-01-01\n---\n";
    expect(parseTaskText(text, "t.md")).toMatchObject({
      id: "7",
      title: "True",
      status: "1.0",
      priority: "31",
    });
  });

  it("leaves optional fields undefined when absent", () => {
    const text = "---\nid: B-1\ntitle: t\nseverity: low\nstatus: open\n---\n";
    expect(parseBugText(text, "b.md")).toMatchObject({ created: undefined, task: undefined });
  });

  it("accepts a legacy spec with no id", () => {
    const text = "---\ntitle: t\nversion: '1.0'\nstatus: draft\ncreated: 2026-01-01\nauthor: human\n---\n";
    expect(parseSpecText(text, "s.md").id).toBeUndefined();
  });

  it("reads an ADR supersedes reference", () => {
    const text = "---\nid: ADR-002\ntitle: t\nstatus: accepted\ncreated: 2026-01-01\nsupersedes: ADR-001\n---\n";
    expect(parseAdrText(text, "a.md").supersedes).toBe("ADR-001");
  });

  it("reads a task from disk", () => {
    const dir = mkdtempSync(join(tmpdir(), "models-"));
    try {
      const path = join(dir, "T-002.md");
      writeFileSync(path, taskText);
      expect(parseTask(path).id).toBe("T-002");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

describe("dump of a hand-built model", () => {
  it("writes the canonical key order, omits undefined optionals and quotes dates", () => {
    const output = dumpFrontmatter(
      {
        kind: "task",
        id: "T-001",
        title: "A title",
        status: "pending",
        priority: "high",
        assignedRole: "developer",
        created: "2026-01-15",
        spec: undefined,
        sourceMap: undefined,
      },
      "# Body\n",
    );
    expect(output).toBe(
      "---\nid: T-001\ntitle: A title\nstatus: pending\npriority: high\nassigned-role: developer\ncreated: '2026-01-15'\n---\n\n# Body\n",
    );
  });
});
