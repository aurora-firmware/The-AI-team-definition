import { existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createAdr } from "../src/core/commands/adr.js";
import { createChangeRequest } from "../src/core/commands/change-request.js";
import { createSpec } from "../src/core/commands/spec.js";
import { LOCK_FILENAME } from "../src/core/lock.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "creation-handlers-"));
  mkdirSync(join(repo, "project"));
  root = findProjectRoot(repo, { env: {} });
  for (const directory of [root.specs, root.decisions, root.changeRequests]) {
    mkdirSync(directory, { recursive: true });
  }
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
});

const handlers = [
  ["spec", createSpec, (r: ProjectRoot) => r.specs],
  ["adr", createAdr, (r: ProjectRoot) => r.decisions],
  ["change-request", createChangeRequest, (r: ProjectRoot) => r.changeRequests],
] as const;

describe.each(handlers)("%s new handler", (_name, handler, folder) => {
  it("fails without writing when the title is missing", () => {
    expect(handler(root, {}).status).toBe(1);
    expect(readdirSync(folder(root))).toEqual([]);
  });

  it("releases the TS allocation lock after creating", () => {
    expect(handler(root, { title: "Locked" }).status).toBe(0);
    expect(existsSync(join(root.projectDir, LOCK_FILENAME))).toBe(false);
    expect(readdirSync(folder(root))).toHaveLength(1);
  });

  it("does not depend on the process working directory", () => {
    const original = process.cwd();
    process.chdir(tmpdir());
    try {
      expect(handler(root, { title: "Elsewhere" }).status).toBe(0);
    } finally {
      process.chdir(original);
    }
    expect(readdirSync(folder(root))).toHaveLength(1);
  });
});

describe("status validation", () => {
  it("rejects an unknown spec status", () => {
    expect(createSpec(root, { title: "T", status: "bogus" }).status).toBe(1);
  });

  it("rejects an unknown ADR status", () => {
    expect(createAdr(root, { title: "T", status: "bogus" }).status).toBe(1);
  });

  it("allocates past a pre-existing file", () => {
    writeFileSync(join(root.decisions, "ADR-004-old.md"), "x");
    expect(createAdr(root, { title: "New" }).payload?.["id"]).toBe("ADR-005");
  });
});
