import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  realpathSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  ArtifactExists,
  ArtifactNotFound,
  moveArtifact,
  readArtifact,
  updateStatus,
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
  directory = realpathSync(mkdtempSync(join(tmpdir(), "ai-team-fs-")));
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

describe("moveArtifact", () => {
  it("renames the file", () => {
    const source = join(directory, "a.md");
    const destination = join(directory, "b.md");
    writeFileSync(source, "content");

    moveArtifact(source, destination);

    expect(existsSync(source)).toBe(false);
    expect(readFileSync(destination, "utf-8")).toBe("content");
  });

  it("does nothing when source and destination are the same path", () => {
    const source = join(directory, "a.md");
    writeFileSync(source, "content");

    moveArtifact(source, join(directory, ".", "a.md"));

    expect(readFileSync(source, "utf-8")).toBe("content");
  });

  it("does nothing when the destination reaches the source through a symlink", () => {
    const source = join(directory, "a.md");
    const alias = join(directory, "alias");
    writeFileSync(source, "content");
    symlinkSync(directory, alias);

    moveArtifact(source, join(alias, "a.md"));

    expect(readFileSync(source, "utf-8")).toBe("content");
  });

  it("throws ArtifactNotFound with the Python message when the source is absent", () => {
    const source = join(directory, "missing.md");

    expect(() => moveArtifact(source, join(directory, "b.md"))).toThrowError(
      new ArtifactNotFound(`Source artifact not found: ${source}`),
    );
    expect(() => moveArtifact(source, join(directory, "b.md"))).toThrow(ArtifactNotFound);
  });

  it("refuses to replace an existing destination with the Python message", () => {
    const source = join(directory, "a.md");
    const destination = join(directory, "b.md");
    writeFileSync(source, "source");
    writeFileSync(destination, "destination");

    expect(() => moveArtifact(source, destination)).toThrowError(
      `Destination already exists: ${destination}; cannot move artifact there.`,
    );
    expect(() => moveArtifact(source, destination)).toThrow(ArtifactExists);
    expect(readFileSync(destination, "utf-8")).toBe("destination");
    expect(readFileSync(source, "utf-8")).toBe("source");
  });
});

describe("updateStatus", () => {
  it("rewrites only the status line and keeps comments, other keys and the body", () => {
    const path = join(directory, "T-001-a-task.md");
    const text = TASK_TEXT.replace(
      "status: pending",
      "# lifecycle state\nstatus: pending  # was set by the planner",
    ).replace("---\n\n#", "---\n\nbody line\n\n#");
    writeFileSync(path, text);

    updateStatus(path, "in-progress");

    expect(readFileSync(path, "utf-8")).toBe(
      text.replace("status: pending  #", "status: in-progress #"),
    );
  });

  it("recognises a bug by its severity key", () => {
    const path = join(directory, "B-001-a-bug.md");
    const text = "---\nid: B-001\ntitle: A bug\nseverity: low\nstatus: open\n---\n\nbody\n";
    writeFileSync(path, text);

    updateStatus(path, "resolved");

    expect(readFileSync(path, "utf-8")).toBe(text.replace("status: open", "status: resolved"));
  });

  it("throws ArtifactNotFound with the Python message when the file is absent", () => {
    const path = join(directory, "missing.md");

    expect(() => updateStatus(path, "completed")).toThrowError(
      new ArtifactNotFound(`Artifact file not found: ${path}`),
    );
  });

  it("leaves no temporary file behind", () => {
    const path = join(directory, "T-001-a-task.md");
    writeFileSync(path, TASK_TEXT);

    updateStatus(path, "completed");

    expect(readdirSync(directory)).toEqual(["T-001-a-task.md"]);
  });
});
