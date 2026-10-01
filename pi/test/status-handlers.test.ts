import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { latestIntegrationResult, statusSummary } from "../src/core/commands/status.js";
import { findProjectRoot, type ProjectRoot } from "../src/core/locator.js";

let repo: string;
let root: ProjectRoot;

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "status-handlers-"));
  mkdirSync(join(repo, "project"));
  root = findProjectRoot(repo, { env: {} });
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
});

function git(...args: string[]): void {
  execFileSync("git", ["-C", repo, ...args], { stdio: "pipe" });
}

function commit(message: string): void {
  git(
    "-c", "user.name=Test", "-c", "user.email=test@example.com",
    "commit", "--allow-empty", "--no-gpg-sign", "-m", message,
  );
}

describe("latest integration result", () => {
  it("returns the subject of the newest commit that mentions an integration keyword", () => {
    git("init", "--quiet");
    commit("chore: unrelated work");
    commit("chore(tasks): merge T-001 into dev");
    commit("docs: unrelated again");

    expect(latestIntegrationResult(root)).toBe("chore(tasks): merge T-001 into dev");
  });

  it("returns 'not found' when no commit matches", () => {
    git("init", "--quiet");
    commit("docs: nothing relevant");

    expect(latestIntegrationResult(root)).toBe("not found");
  });

  it("returns 'not found' when the repository has no commits", () => {
    git("init", "--quiet");

    expect(latestIntegrationResult(root)).toBe("not found");
  });

  it("returns 'not found' when the project is not inside a git repository", () => {
    const previous = process.env["GIT_CEILING_DIRECTORIES"];
    process.env["GIT_CEILING_DIRECTORIES"] = tmpdir();
    try {
      expect(latestIntegrationResult(root)).toBe("not found");
    } finally {
      if (previous === undefined) delete process.env["GIT_CEILING_DIRECTORIES"];
      else process.env["GIT_CEILING_DIRECTORIES"] = previous;
    }
  });
});

describe("status handler", () => {
  it("reports the git lookup result in its payload", () => {
    git("init", "--quiet");
    commit("test: verification passed");

    const result = statusSummary(root, {});
    expect(result.status).toBe(0);
    expect(result.payload?.["latest_integration_result"]).toBe("test: verification passed");
  });
});
