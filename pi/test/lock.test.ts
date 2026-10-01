import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { ArtifactExists } from "../src/core/fs.js";
import {
  LOCK_FILENAME,
  LockTimeout,
  allocationLock,
  createArtifactWithLock,
} from "../src/core/lock.js";
import { parseTaskText } from "../src/core/models.js";

let projectDir: string;

beforeEach(() => {
  projectDir = mkdtempSync(join(tmpdir(), "ai-team-lock-"));
});

afterEach(() => {
  rmSync(projectDir, { recursive: true, force: true });
});

/** A pid that is certainly not alive: a child that has already exited. */
function deadPid(): number {
  const result = spawnSync(process.execPath, ["-e", ""]);
  if (result.pid === undefined) throw new Error("could not spawn a short-lived process");
  return result.pid;
}

describe("allocationLock", () => {
  it("runs the callback and returns its value", () => {
    expect(allocationLock(projectDir, () => 42)).toBe(42);
  });

  it("removes the lock file after the callback returns", () => {
    allocationLock(projectDir, () => undefined);
    expect(existsSync(join(projectDir, LOCK_FILENAME))).toBe(false);
  });

  it("removes the lock file when the callback throws", () => {
    expect(() =>
      allocationLock(projectDir, () => {
        throw new Error("boom");
      }),
    ).toThrow("boom");
    expect(existsSync(join(projectDir, LOCK_FILENAME))).toBe(false);
  });

  it("creates the project directory when missing", () => {
    const nested = join(projectDir, "a", "b");
    allocationLock(nested, () => undefined);
    expect(existsSync(nested)).toBe(true);
  });

  it("leaves no temporary files behind", () => {
    allocationLock(projectDir, () => undefined);
    expect(readdirSync(projectDir)).toEqual([]);
  });

  it("uses the TS lock path and never touches .ai-team.lock", () => {
    const pythonLock = join(projectDir, ".ai-team.lock");
    writeFileSync(pythonLock, "python holder");
    let seen: string[] = [];
    allocationLock(projectDir, () => {
      seen = readdirSync(projectDir).sort();
    });
    expect(LOCK_FILENAME).toBe(".ai-team-ts.lock");
    expect(seen).toContain(".ai-team-ts.lock");
    expect(readFileSync(pythonLock, "utf-8")).toBe("python holder");
  });

  it("is not blocked by a Python flock sentinel file", () => {
    writeFileSync(join(projectDir, ".ai-team.lock"), "");
    expect(allocationLock(projectDir, () => "ok", { timeoutSeconds: 0.2 })).toBe("ok");
  });

  it("raises LockTimeout with the Python message template and the TS lock path", () => {
    writeFileSync(join(projectDir, LOCK_FILENAME), String(process.pid));
    const lockPath = join(projectDir, LOCK_FILENAME);
    expect(() => allocationLock(projectDir, () => 1, { timeoutSeconds: 0.2 })).toThrow(
      new LockTimeout(
        `Could not acquire the project allocation lock at ${lockPath} within 0.2 seconds; ` +
          "another ai-team process appears to be holding it.",
      ),
    );
  });

  it("formats a whole-second timeout like Python's float, with a trailing .0", () => {
    writeFileSync(join(projectDir, LOCK_FILENAME), String(process.pid));
    expect(() => allocationLock(projectDir, () => 1, { timeoutSeconds: 0 })).toThrow(
      /within 0\.0 seconds; another ai-team process appears to be holding it\.$/,
    );
  });

  it("does not remove a lock it failed to acquire", () => {
    const lockPath = join(projectDir, LOCK_FILENAME);
    writeFileSync(lockPath, String(process.pid));
    expect(() => allocationLock(projectDir, () => 1, { timeoutSeconds: 0.1 })).toThrow(
      LockTimeout,
    );
    expect(readFileSync(lockPath, "utf-8")).toBe(String(process.pid));
  });

  it("reclaims a lock whose holder process is dead", () => {
    const lockPath = join(projectDir, LOCK_FILENAME);
    writeFileSync(lockPath, String(deadPid()));
    expect(allocationLock(projectDir, () => "reclaimed", { timeoutSeconds: 2 })).toBe(
      "reclaimed",
    );
    expect(existsSync(lockPath)).toBe(false);
  });

  it("does not reclaim a lock whose content is not a pid", () => {
    writeFileSync(join(projectDir, LOCK_FILENAME), "garbage");
    expect(() => allocationLock(projectDir, () => 1, { timeoutSeconds: 0.1 })).toThrow(
      LockTimeout,
    );
  });
});

describe("createArtifactWithLock", () => {
  function taskBuild(directory: string) {
    return (id: string): [string, ReturnType<typeof parseTaskText>, string] => {
      const path = join(directory, `${id}-t.md`);
      const text = `---\nid: ${id}\ntitle: T\nstatus: pending\npriority: medium\nassigned-role: developer\ncreated: '2026-01-01'\n---\n`;
      return [path, parseTaskText(text, path), "# T\n"];
    };
  }

  it("allocates, writes and returns the id and path", () => {
    mkdirSync(join(projectDir, "tasks"));
    const [id, path] = createArtifactWithLock(projectDir, {
      allocateId: () => "T-007",
      build: taskBuild(join(projectDir, "tasks")),
    });
    expect(id).toBe("T-007");
    expect(path).toBe(join(projectDir, "tasks", "T-007-t.md"));
    expect(readFileSync(path, "utf-8")).toContain("id: T-007");
  });

  it("raises ArtifactExists when the destination exists and releases the lock", () => {
    mkdirSync(join(projectDir, "tasks"));
    const options = { allocateId: () => "T-007", build: taskBuild(join(projectDir, "tasks")) };
    createArtifactWithLock(projectDir, options);
    expect(() => createArtifactWithLock(projectDir, options)).toThrow(ArtifactExists);
    expect(existsSync(join(projectDir, LOCK_FILENAME))).toBe(false);
  });
});
