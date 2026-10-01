import { mkdirSync, mkdtempSync, readdirSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { findProjectRoot, ProjectRootNotFound } from "../src/core/locator.js";
import { AiTeamError } from "../src/core/result.js";

let sandbox: string;

beforeEach(() => {
  sandbox = realpathSync(mkdtempSync(join(tmpdir(), "locator-")));
});

afterEach(() => {
  rmSync(sandbox, { recursive: true, force: true });
});

function makeDir(...parts: string[]): string {
  const path = join(sandbox, ...parts);
  mkdirSync(path, { recursive: true });
  return path;
}

function writeToml(directory: string, text: string): void {
  writeFileSync(join(directory, ".ai-team.toml"), text);
}

describe("findProjectRoot resolution order", () => {
  it("uses the explicit root over AI_TEAM_ROOT and the walk", () => {
    const explicit = makeDir("explicit");
    makeDir("explicit", "project");
    const fromEnv = makeDir("env");
    makeDir("env", "project");
    makeDir("walk", "project");

    const found = findProjectRoot(join(sandbox, "walk"), {
      root: explicit,
      env: { AI_TEAM_ROOT: fromEnv },
    });

    expect(found.repo).toBe(explicit);
  });

  it("uses AI_TEAM_ROOT over the upward walk when no explicit root is given", () => {
    const fromEnv = makeDir("env");
    makeDir("env", "project");
    makeDir("walk", "project");

    const found = findProjectRoot(join(sandbox, "walk"), { env: { AI_TEAM_ROOT: fromEnv } });

    expect(found.repo).toBe(fromEnv);
  });

  it("ignores an empty AI_TEAM_ROOT", () => {
    makeDir("walk", "project");

    const found = findProjectRoot(join(sandbox, "walk"), { env: { AI_TEAM_ROOT: "" } });

    expect(found.repo).toBe(join(sandbox, "walk"));
  });

  it("walks up from the start directory to the folder holding the project directory", () => {
    makeDir("repo", "project");
    const nested = makeDir("repo", "a", "b");

    const found = findProjectRoot(nested, { env: {} });

    expect(found.repo).toBe(join(sandbox, "repo"));
    expect(found.projectDir).toBe(join(sandbox, "repo", "project"));
  });

  it("honours the [project] dir setting of .ai-team.toml", () => {
    const repo = makeDir("repo");
    makeDir("repo", "work-items");
    writeToml(repo, '[project]\ndir = "work-items"\n');

    const found = findProjectRoot(makeDir("repo", "sub"), { env: {} });

    expect(found.projectDir).toBe(join(repo, "work-items"));
  });

  it("applies the .ai-team.toml dir setting to an explicit root", () => {
    const repo = makeDir("repo");
    makeDir("repo", "work-items");
    writeToml(repo, '[project]\ndir = "work-items"\n');

    const found = findProjectRoot(sandbox, { root: repo, env: {} });

    expect(found.projectDir).toBe(join(repo, "work-items"));
  });

  it("keeps walking when the toml names a folder that is missing", () => {
    const inner = makeDir("outer", "inner");
    writeToml(inner, '[project]\ndir = "gone"\n');
    makeDir("outer", "project");

    const found = findProjectRoot(inner, { env: {} });

    expect(found.repo).toBe(join(sandbox, "outer"));
  });

  it("ignores an unparseable .ai-team.toml and falls back to the default folder", () => {
    const repo = makeDir("repo");
    makeDir("repo", "project");
    writeToml(repo, "[project\nnot toml");

    const found = findProjectRoot(repo, { env: {} });

    expect(found.projectDir).toBe(join(repo, "project"));
  });

  it("uses the projectDir option as the default folder name", () => {
    makeDir("repo", "custom");

    const found = findProjectRoot(join(sandbox, "repo"), { projectDir: "custom", env: {} });

    expect(found.projectDir).toBe(join(sandbox, "repo", "custom"));
  });
});

describe("findProjectRoot start directory", () => {
  it("resolves from the given directory even when process.cwd differs", () => {
    makeDir("repo", "project");
    expect(process.cwd()).not.toBe(join(sandbox, "repo"));

    const found = findProjectRoot(join(sandbox, "repo"), { env: {} });

    expect(found.repo).toBe(join(sandbox, "repo"));
  });

  it("does not reference process.cwd in the locator source", () => {
    const sourcePath = join(dirname(fileURLToPath(import.meta.url)), "..", "src", "core");
    const sourceFiles = readdirSync(sourcePath, { recursive: true, encoding: "utf-8" }).filter((name) =>
      name.endsWith(".ts"),
    );
    for (const name of sourceFiles) {
      expect(readFileSync(join(sourcePath, name), "utf-8"), name).not.toContain("process.cwd");
    }
  });
});

describe("ProjectRoot paths", () => {
  it("lays out every artifact directory under the project directory", () => {
    const repo = makeDir("repo");
    makeDir("repo", "project");
    const project = join(repo, "project");

    const found = findProjectRoot(repo, { env: {} });

    expect(found).toEqual({
      repo,
      projectDir: project,
      specs: join(project, "specs"),
      tasksPending: join(project, "tasks", "pending"),
      tasksInProgress: join(project, "tasks", "in-progress"),
      tasksCompleted: join(project, "tasks", "completed"),
      tasksBlocked: join(project, "tasks", "blocked"),
      bugsOpen: join(project, "bugs", "open"),
      bugsInProgress: join(project, "bugs", "in-progress"),
      bugsResolved: join(project, "bugs", "resolved"),
      changeRequests: join(project, "change-requests"),
      decisions: join(project, "decisions"),
      docs: join(project, "docs"),
    });
  });
});

describe("findProjectRoot not found", () => {
  const hint = "Run 'ai-team init' to bootstrap the project structure.";

  it("names the folder missing under an explicit root, keeping the hint separate", () => {
    const repo = makeDir("empty");

    const error = catchError(() => findProjectRoot(sandbox, { root: repo, env: {} }));

    expect(error.message).toBe(`No 'project/' folder found under the provided --root ${repo}.`);
    expect(error.hint).toBe(hint);
  });

  it("names the folder missing under AI_TEAM_ROOT", () => {
    const repo = makeDir("empty");

    const error = catchError(() => findProjectRoot(sandbox, { env: { AI_TEAM_ROOT: repo } }));

    expect(error.message).toBe(`No 'project/' folder found under AI_TEAM_ROOT=${repo}.`);
    expect(error.hint).toBe(hint);
  });

  it("lists every searched directory when the walk reaches the filesystem root", () => {
    const start = makeDir("a", "b");

    const error = catchError(() => findProjectRoot(start, { projectDir: "no-such-folder-xyz", env: {} }));

    expect(error.message).toMatch(
      new RegExp(
        `^Could not locate a 'no-such-folder-xyz/' directory by walking up from ${escape(start)}\\. Searched: ${escape(start)}, ${escape(join(sandbox, "a"))}, `,
      ),
    );
    expect(error.message.endsWith(".")).toBe(true);
    expect(error.hint).toBe(hint);
  });

  it("is an AiTeamError", () => {
    const error = catchError(() => findProjectRoot(makeDir("x"), { root: makeDir("y"), env: {} }));

    expect(error).toBeInstanceOf(AiTeamError);
    expect(error.name).toBe("ProjectRootNotFound");
  });
});

function catchError(action: () => unknown): ProjectRootNotFound {
  try {
    action();
  } catch (error) {
    if (error instanceof ProjectRootNotFound) return error;
    throw error;
  }
  throw new Error("expected ProjectRootNotFound");
}

function escape(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
