import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { notImplemented, type RootHandler } from "../src/core/commands/handler.js";
import { COMMANDS, isStub, type CommandEntry } from "../src/core/commands/registry.js";
import { failure, success } from "../src/core/result.js";
import {
  FIXTURES_ROOT,
  discoverCases,
  materializeTree,
  readCase,
  runCase,
  serializeTree,
  type TreeEntry,
} from "./helpers/parity-runner.js";

const PI_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

function toolContractCommands(): string[] {
  const map = JSON.parse(readFileSync(join(PI_ROOT, "resources", "command-map.json"), "utf8"));
  return map.commands.map((entry: { command: string }) => entry.command);
}

describe("command registry", () => {
  it("maps every tool-contract command to exactly one handler", () => {
    expect(Object.keys(COMMANDS).sort()).toEqual(toolContractCommands().sort());
    for (const entry of Object.values(COMMANDS)) {
      expect(typeof entry.handler).toBe("function");
    }
  });

  it("uses a distinct handler for each command", () => {
    const handlers = Object.values(COMMANDS).map((entry) => entry.handler);
    expect(new Set(handlers).size).toBe(handlers.length);
  });

  it("gives init and check-layout a start-directory handler and every other command a located-root handler", () => {
    for (const [command, entry] of Object.entries(COMMANDS)) {
      const expected =
        command === "init" ? "init" : command === "check-layout" ? "check-layout" : "root";
      expect(entry.kind, command).toBe(expected);
    }
  });

  it("reports stub handlers as not implemented when they are called", () => {
    const handler = notImplemented<RootHandler>("archive");
    expect(isStub(handler)).toBe(true);
    expect(() => (handler as (a: unknown, b: unknown) => unknown)("x", {})).toThrow(
      /archive.*not implemented/i,
    );
  });
});

// --- the runner itself, exercised against throwaway fixture roots -------------------

let sandbox: string;

beforeEach(() => {
  sandbox = mkdtempSync(join(tmpdir(), "parity-runner-"));
});

afterEach(() => {
  rmSync(sandbox, { recursive: true, force: true });
});

interface CaseSpec {
  readonly name: string;
  readonly command?: string;
  readonly expected: unknown;
  readonly before?: TreeEntry[];
  readonly after?: TreeEntry[];
  readonly env?: Record<string, string>;
  readonly projectDir?: string;
}

function writeFixtures(...cases: CaseSpec[]): string {
  const fixtures = join(sandbox, "fixtures");
  mkdirSync(fixtures);
  writeFileSync(
    join(fixtures, "lock-sentinels.json"),
    JSON.stringify({
      after_tree_excluded_paths: ["<project_dir>/.ai-team.lock", "<project_dir>/.ai-team-ts.lock"],
    }),
  );
  for (const spec of cases) {
    const dir = join(fixtures, spec.name);
    mkdirSync(dir);
    const definition = {
      command: spec.command ?? "fake",
      input: {},
      today: "2026-03-01",
      version: "1.0.0",
      env: spec.env ?? {},
      ...(spec.projectDir === undefined ? {} : { project_dir: spec.projectDir }),
      expected: spec.expected,
    };
    writeFileSync(join(dir, "case.json"), JSON.stringify(definition));
    writeFileSync(join(dir, "before.json"), JSON.stringify(spec.before ?? [{ path: "project", type: "dir" }]));
    writeFileSync(join(dir, "after.json"), JSON.stringify(spec.after ?? [{ path: "project", type: "dir" }]));
  }
  return fixtures;
}

function registryOf(handler: (startDirectory: string) => ReturnType<typeof success>): Record<string, CommandEntry> {
  return { fake: { kind: "init", handler: (startDirectory) => handler(startDirectory) } };
}

describe("parity runner", () => {
  it("discovers a new case directory without any registration", () => {
    const fixtures = writeFixtures({ name: "fake--first", expected: { status: 0 } });
    expect(discoverCases(fixtures).map((dir) => dir.slice(fixtures.length + 1))).toEqual(["fake--first"]);

    mkdirSync(join(fixtures, "fake--second"));
    writeFileSync(join(fixtures, "fake--second", "case.json"), "{}");
    mkdirSync(join(fixtures, "not-a-case"));

    expect(discoverCases(fixtures).map((dir) => dir.slice(fixtures.length + 1))).toEqual([
      "fake--first",
      "fake--second",
    ]);
  });

  it("discovers the shared fixtures with their commands registered", () => {
    const cases = discoverCases(FIXTURES_ROOT);
    expect(cases.length).toBeGreaterThan(0);
    for (const dir of cases) {
      expect(Object.keys(COMMANDS), dir).toContain(readCase(dir).command);
    }
  });

  it("passes a case whose result and after-tree match", () => {
    const fixtures = writeFixtures({ name: "fake--ok", expected: { status: 0, payload: { a: 1 } } });
    const outcome = runCase(join(fixtures, "fake--ok"), fixtures, registryOf(() => success({ a: 1 })));
    expect(outcome).toEqual({ kind: "ran", diffs: [] });
  });

  it("fails a payload mismatch with a diff naming expected and actual", () => {
    const fixtures = writeFixtures({ name: "fake--bad", expected: { status: 0, payload: { a: 2 } } });
    const outcome = runCase(join(fixtures, "fake--bad"), fixtures, registryOf(() => success({ a: 1 })));
    expect(outcome.kind).toBe("ran");
    const diffs = outcome.kind === "ran" ? outcome.diffs : [];
    expect(diffs).toHaveLength(1);
    expect(diffs[0]).toContain("expected result");
    expect(diffs[0]).toContain('-    "a": 2');
    expect(diffs[0]).toContain('+    "a": 1');
  });

  it("fails a status or message mismatch", () => {
    const fixtures = writeFixtures({ name: "fake--msg", expected: { status: 1, message: "boom" } });
    const outcome = runCase(
      join(fixtures, "fake--msg"),
      fixtures,
      { fake: { kind: "init", handler: () => failure("bang", "ignored hint") } },
    );
    expect(outcome.kind === "ran" && outcome.diffs[0]).toContain('+  "message": "bang"');
  });

  it("fails an after-tree mismatch", () => {
    const fixtures = writeFixtures({
      name: "fake--tree",
      expected: { status: 0, payload: {} },
      after: [{ path: "project", type: "dir" }, { path: "extra.txt", type: "file", text: "x" }],
    });
    const outcome = runCase(join(fixtures, "fake--tree"), fixtures, registryOf(() => success({})));
    expect(outcome.kind === "ran" && outcome.diffs[0]).toContain("expected after tree");
  });

  it("reports a case whose command is still a stub as pending without running it", () => {
    const fixtures = writeFixtures({ name: "archive--pending", command: "archive", expected: { status: 0 } });
    expect(runCase(join(fixtures, "archive--pending"), fixtures, {
      archive: { kind: "root", handler: notImplemented<RootHandler>("archive") },
    })).toEqual({
      kind: "pending",
      command: "archive",
    });
  });

  it("rejects a case for a command missing from the registry", () => {
    const fixtures = writeFixtures({ name: "nope--case", command: "nope", expected: { status: 0 } });
    expect(() => runCase(join(fixtures, "nope--case"), fixtures, {})).toThrow(/Unknown parity command: 'nope'/);
  });

  it("rejects a case missing a required field", () => {
    const fixtures = writeFixtures({ name: "fake--incomplete", expected: { status: 0 } });
    const caseFile = join(fixtures, "fake--incomplete", "case.json");
    const { today: _today, ...withoutToday } = JSON.parse(readFileSync(caseFile, "utf8"));
    writeFileSync(caseFile, JSON.stringify(withoutToday));
    expect(() => runCase(join(fixtures, "fake--incomplete"), fixtures, registryOf(() => success({})))).toThrow(
      /missing required field 'today'/,
    );
  });

  it("ignores the two lock paths in the after-tree and nothing else", () => {
    const fixtures = writeFixtures({
      name: "fake--locks",
      expected: { status: 0, payload: {} },
      after: [
        { path: "project", type: "dir" },
        { path: "project/sub", type: "dir" },
        { path: "project/sub/.ai-team.lock", type: "file", text: "" },
      ],
    });
    const handler = (startDirectory: string) => {
      mkdirSync(join(startDirectory, "project", "sub"));
      writeFileSync(join(startDirectory, "project", ".ai-team.lock"), "");
      mkdirSync(join(startDirectory, "project", ".ai-team-ts.lock"));
      writeFileSync(join(startDirectory, "project", ".ai-team-ts.lock", "owner"), "pid");
      writeFileSync(join(startDirectory, "project", "sub", ".ai-team.lock"), "");
      return success({});
    };
    expect(runCase(join(fixtures, "fake--locks"), fixtures, registryOf(handler))).toEqual({
      kind: "ran",
      diffs: [],
    });
  });

  it("normalises only the materialised root, in the result and in file text", () => {
    const fixtures = writeFixtures({
      name: "fake--root",
      expected: { status: 0, payload: { path: "<ROOT>/project/f.txt", other: "/tmp/elsewhere" } },
      after: [{ path: "project", type: "dir" }, { path: "project/f.txt", type: "file", text: "at <ROOT>\n" }],
    });
    const handler = (startDirectory: string) => {
      writeFileSync(join(startDirectory, "project", "f.txt"), `at ${startDirectory}\n`);
      return success({ path: join(startDirectory, "project", "f.txt"), other: "/tmp/elsewhere" });
    };
    expect(runCase(join(fixtures, "fake--root"), fixtures, registryOf(handler))).toEqual({ kind: "ran", diffs: [] });
  });

  it("applies the clock and version overrides, unsets AI_TEAM_ROOT, and restores the environment", () => {
    const seen: Record<string, string | undefined> = {};
    const fixtures = writeFixtures({ name: "fake--env", expected: { status: 0, payload: {} }, env: { EXTRA: "<ROOT>/x" } });
    process.env["AI_TEAM_ROOT"] = "/leaked";
    try {
      runCase(
        join(fixtures, "fake--env"),
        fixtures,
        registryOf((startDirectory) => {
          for (const name of ["AI_TEAM_TODAY", "AI_TEAM_FRAMEWORK_VERSION", "AI_TEAM_ROOT", "EXTRA", "GIT_CEILING_DIRECTORIES"]) {
            seen[name] = process.env[name];
          }
          seen["start"] = startDirectory;
          return success({});
        }),
      );
      expect(seen["AI_TEAM_TODAY"]).toBe("2026-03-01");
      expect(seen["AI_TEAM_FRAMEWORK_VERSION"]).toBe("1.0.0");
      expect(seen["AI_TEAM_ROOT"]).toBeUndefined();
      expect(seen["EXTRA"]).toBe(`${seen["start"]}/x`);
      expect(seen["GIT_CEILING_DIRECTORIES"]).toBe(dirname(seen["start"] as string));
      expect(process.env["AI_TEAM_ROOT"]).toBe("/leaked");
      expect(process.env["EXTRA"]).toBeUndefined();
    } finally {
      delete process.env["AI_TEAM_ROOT"];
    }
  });

  it("hands root handlers a located ProjectRoot and turns a missing root into a failure", () => {
    const fixtures = writeFixtures({
      name: "fake--root-handler",
      expected: { status: 0, payload: { repo: "<ROOT>", projectDir: "<ROOT>/project" } },
    });
    const registry: Record<string, CommandEntry> = {
      fake: { kind: "root", handler: (root) => success({ repo: root.repo, projectDir: root.projectDir }) },
    };
    expect(runCase(join(fixtures, "fake--root-handler"), fixtures, registry)).toEqual({ kind: "ran", diffs: [] });
  });

  it("turns a missing project root into a failure result for root handlers", () => {
    const fixtures = writeFixtures({
      name: "fake--no-root",
      expected: { status: 1, message: "No 'project/' folder found under the provided --root <ROOT>." },
      before: [],
      after: [],
    });
    const registry: Record<string, CommandEntry> = {
      fake: { kind: "root", handler: () => success({}) },
    };
    expect(runCase(join(fixtures, "fake--no-root"), fixtures, registry)).toEqual({ kind: "ran", diffs: [] });
  });

  it("round-trips a tree through materialise and serialise", () => {
    const tree: TreeEntry[] = [
      { path: "a", type: "dir" },
      { path: "a/crlf.txt", type: "file", text: "a\r\nb\n" },
      { path: "blob.bin", type: "file", base64: "//4A" },
    ];
    const target = join(sandbox, "tree");
    materializeTree(tree, target);
    expect(serializeTree(target)).toEqual(tree);
  });

  it("refuses unsafe paths in a tree manifest", () => {
    expect(() => materializeTree([{ path: "../escape", type: "file", text: "" }], join(sandbox, "t"))).toThrow(
      /Unsafe path/,
    );
  });
});

// --- the shared fixtures (ADR-004) ---------------------------------------------------

describe("parity fixtures", () => {
  for (const caseDir of discoverCases(FIXTURES_ROOT)) {
    const name = caseDir.slice(FIXTURES_ROOT.length + 1);
    const { command } = readCase(caseDir);
    const entry = COMMANDS[command];

    // An unimplemented command is reported as todo, never as a silent pass.
    if (entry !== undefined && isStub(entry.handler)) {
      it.todo(`${name} [pending: '${command}' is not implemented]`);
      continue;
    }

    it(name, () => {
      const outcome = runCase(caseDir, FIXTURES_ROOT, COMMANDS);
      expect(outcome.kind).toBe("ran");
      if (outcome.kind === "ran") expect(outcome.diffs.join("\n")).toBe("");
    });
  }
});
