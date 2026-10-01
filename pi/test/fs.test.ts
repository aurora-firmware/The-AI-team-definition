import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  ArtifactExists,
  ArtifactNotFound,
  readArtifact,
  writeArtifact,
} from "../src/core/fs.js";
import { FrontmatterError, parseTaskText } from "../src/core/models.js";

const TASK_TEXT = [
  "---",
  "id: T-001",
  "title: A task",
  "status: pending",
  "priority: high",
  "assigned-role: developer",
  "created: '2026-01-15'",
  "---",
  "",
  "# A task\n",
].join("\n");

let directory: string;

beforeEach(() => {
  directory = mkdtempSync(join(tmpdir(), "ai-team-fs-"));
});

afterEach(() => {
  rmSync(directory, { recursive: true, force: true });
});

describe("readArtifact", () => {
  it("returns the model and the body after the frontmatter", () => {
    const path = join(directory, "T-001-a-task.md");
    writeFileSync(path, TASK_TEXT);

    const { model, body } = readArtifact(path, "task");

    expect(model.kind).toBe("task");
    expect(model.id).toBe("T-001");
    expect(body).toBe("# A task\n");
  });

  it("throws ArtifactNotFound with the Python message when the file is absent", () => {
    const path = join(directory, "missing.md");

    expect(() => readArtifact(path, "task")).toThrowError(
      new ArtifactNotFound(`Artifact file not found: ${path}`),
    );
    expect(() => readArtifact(path, "task")).toThrow(ArtifactNotFound);
  });

  it("propagates FrontmatterError for a file without frontmatter", () => {
    const path = join(directory, "bad.md");
    writeFileSync(path, "no frontmatter\n");

    expect(() => readArtifact(path, "task")).toThrow(FrontmatterError);
  });
});

describe("writeArtifact", () => {
  it("writes the model and body as a complete artifact file", () => {
    const path = join(directory, "T-001-a-task.md");
    const model = parseTaskText(TASK_TEXT, "inline");

    writeArtifact(path, model, "# A task\n");

    expect(readFileSync(path, "utf-8")).toBe(TASK_TEXT);
  });

  it("refuses to overwrite an existing file with the Python message", () => {
    const path = join(directory, "T-001-a-task.md");
    writeFileSync(path, "original");
    const model = parseTaskText(TASK_TEXT, "inline");

    expect(() => writeArtifact(path, model, "body")).toThrowError(
      `Artifact already exists at ${path}; pass overwrite=True to replace it.`,
    );
    expect(() => writeArtifact(path, model, "body")).toThrow(ArtifactExists);
    expect(readFileSync(path, "utf-8")).toBe("original");
  });

  it("replaces an existing file when overwrite is requested", () => {
    const path = join(directory, "T-001-a-task.md");
    writeFileSync(path, "original");
    const model = parseTaskText(TASK_TEXT, "inline");

    writeArtifact(path, model, "# A task\n", { overwrite: true });

    expect(readFileSync(path, "utf-8")).toBe(TASK_TEXT);
  });

  it("leaves no temporary file behind after a successful write", () => {
    const path = join(directory, "T-001-a-task.md");

    writeArtifact(path, parseTaskText(TASK_TEXT, "inline"), "# A task\n");

    expect(readdirSync(directory)).toEqual(["T-001-a-task.md"]);
  });

  it("keeps the destination and removes the temporary file when the final rename fails", () => {
    const path = join(directory, "occupied");
    mkdirSync(path);

    expect(() =>
      writeArtifact(path, parseTaskText(TASK_TEXT, "inline"), "body", { overwrite: true }),
    ).toThrow();

    expect(readdirSync(directory)).toEqual(["occupied"]);
  });
});
