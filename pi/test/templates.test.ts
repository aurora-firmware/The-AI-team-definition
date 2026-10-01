import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { AiTeamError } from "../src/core/result.js";
import { loadTemplate, type TemplateKind } from "../src/core/templates.js";

const pythonTemplates = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "cli",
  "src",
  "ai_team",
  "templates",
);

const files: ReadonlyArray<readonly [TemplateKind, string]> = [
  ["task", "task.md"],
  ["bug", "bug.md"],
  ["spec", "spec.md"],
  ["adr", "adr.md"],
  ["report", "progress-report.md"],
  ["change-request", "change-request.md"],
];

describe("loadTemplate", () => {
  it.each(files)("returns bytes identical to the Python %s template", (kind, file) => {
    const expected = readFileSync(join(pythonTemplates, file));
    expect(Buffer.compare(loadTemplate(kind), expected)).toBe(0);
  });

  it("rejects an unsupported kind naming the supported ones", () => {
    let caught: unknown;
    try {
      loadTemplate("memo" as TemplateKind);
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeInstanceOf(AiTeamError);
    expect((caught as AiTeamError).message).toContain("'memo'");
    expect((caught as AiTeamError).message).toContain("task, bug, spec, adr, report, change-request");
  });

  it("tells the user to run the sync when the templates directory is missing", () => {
    let caught: unknown;
    try {
      loadTemplate("task", join(pythonTemplates, "no-such-dir"));
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeInstanceOf(AiTeamError);
    expect((caught as AiTeamError).hint).toMatch(/sync_init_scaffolds\.py/);
  });
});
