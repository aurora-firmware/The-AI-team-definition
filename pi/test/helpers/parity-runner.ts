/**
 * Runner for the shared parity fixtures (S-005 Component 5, ADR-004); the format is documented
 * in `fixtures/parity/README.md`. Mirrors `cli/tests/parity_support.py`.
 */
import {
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, posix, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { isStub, type CommandEntry, type CommandInput } from "../../src/core/commands/registry.js";
import { findProjectRoot, ProjectRootNotFound, ROOT_ENV_VAR } from "../../src/core/locator.js";
import { failure, type Result } from "../../src/core/result.js";
import { FRAMEWORK_VERSION_ENV_VAR, TODAY_ENV_VAR } from "../../src/core/runtime.js";

export const FIXTURES_ROOT = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "..",
  "fixtures",
  "parity",
);

const CASE_FILE = "case.json";
const LOCK_SENTINELS_FILE = "lock-sentinels.json";
const PROJECT_DIR_PLACEHOLDER = "<project_dir>";
const ROOT_PLACEHOLDER = "<ROOT>";
const GIT_CEILING_ENV_VAR = "GIT_CEILING_DIRECTORIES";
const REQUIRED_CASE_FIELDS = ["command", "input", "today", "version", "expected"] as const;

export type TreeEntry =
  | { path: string; type: "dir" }
  | { path: string; type: "file"; text: string }
  | { path: string; type: "file"; base64: string };

export interface ParityCase {
  readonly command: string;
  readonly input: CommandInput;
  readonly today: string;
  readonly version: string;
  readonly env?: Readonly<Record<string, string>>;
  readonly project_dir?: string;
  readonly expected: Readonly<Record<string, unknown>>;
}

export type CaseOutcome =
  | { readonly kind: "ran"; readonly diffs: string[] }
  | { readonly kind: "pending"; readonly command: string };

type Registry = Readonly<Record<string, CommandEntry>>;

// --- trees -------------------------------------------------------------------------------

const utf8 = new TextDecoder("utf-8", { fatal: true });

/** A manifest of every directory and file under `root`, sorted by path. */
export function serializeTree(root: string): TreeEntry[] {
  const entries: TreeEntry[] = [];
  for (const relative of readdirSync(root, { recursive: true, encoding: "utf-8" })) {
    const path = relative.split(sep).join(posix.sep);
    const stat = lstatSync(join(root, relative));
    if (stat.isSymbolicLink()) {
      throw new Error(`Symlinks are not supported in fixture trees: ${join(root, relative)}`);
    }
    if (stat.isDirectory()) {
      entries.push({ path, type: "dir" });
      continue;
    }
    const data = readFileSync(join(root, relative));
    try {
      entries.push({ path, type: "file", text: utf8.decode(data) });
    } catch {
      entries.push({ path, type: "file", base64: data.toString("base64") });
    }
  }
  return entries.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
}

/** Creates `target` and writes every manifest entry under it, byte for byte. */
export function materializeTree(manifest: readonly TreeEntry[], target: string): void {
  mkdirSync(target, { recursive: true });
  for (const entry of manifest) {
    const parts = entry.path.split("/");
    if (entry.path.startsWith("/") || parts.includes("..") || entry.path === "") {
      throw new Error(`Unsafe path in tree manifest: ${entry.path}`);
    }
    const destination = join(target, ...parts);
    if (entry.type === "dir") {
      mkdirSync(destination, { recursive: true });
      continue;
    }
    mkdirSync(dirname(destination), { recursive: true });
    writeFileSync(destination, "base64" in entry ? Buffer.from(entry.base64, "base64") : entry.text);
  }
}

function loadLockExclusions(fixturesRoot: string): string[] {
  const data = JSON.parse(readFileSync(join(fixturesRoot, LOCK_SENTINELS_FILE), "utf8"));
  return data.after_tree_excluded_paths as string[];
}

function excludeLockPaths(manifest: TreeEntry[], projectDir: string, exclusions: string[]): TreeEntry[] {
  const literals = exclusions.map((entry) => entry.replaceAll(PROJECT_DIR_PLACEHOLDER, projectDir));
  return manifest.filter(
    (entry) => !literals.some((literal) => entry.path === literal || entry.path.startsWith(`${literal}/`)),
  );
}

// --- cases -------------------------------------------------------------------------------

/** Every case directory under `fixturesRoot`, sorted by name. A directory with a case.json is a case. */
export function discoverCases(fixturesRoot: string): string[] {
  return readdirSync(fixturesRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && readdirSync(join(fixturesRoot, entry.name)).includes(CASE_FILE))
    .map((entry) => join(fixturesRoot, entry.name))
    .sort();
}

export function readCase(caseDir: string): ParityCase {
  const source = join(caseDir, CASE_FILE);
  const parsed = JSON.parse(readFileSync(source, "utf8")) as Record<string, unknown>;
  for (const field of REQUIRED_CASE_FIELDS) {
    if (!(field in parsed)) throw new Error(`${source} is missing required field '${field}'`);
  }
  return parsed as unknown as ParityCase;
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

// --- running a case ----------------------------------------------------------------------

function withIsolatedEnvironment<T>(root: string, definition: ParityCase, run: () => T): T {
  const saved = { ...process.env };
  try {
    delete process.env[ROOT_ENV_VAR];
    process.env[TODAY_ENV_VAR] = definition.today;
    process.env[FRAMEWORK_VERSION_ENV_VAR] = definition.version;
    process.env[GIT_CEILING_ENV_VAR] = dirname(root);
    for (const [name, value] of Object.entries(definition.env ?? {})) {
      process.env[name] = value.replaceAll(ROOT_PLACEHOLDER, root);
    }
    return run();
  } finally {
    for (const name of Object.keys(process.env)) delete process.env[name];
    Object.assign(process.env, saved);
  }
}

function dispatch(entry: CommandEntry, repo: string, input: CommandInput): Result {
  if (entry.kind !== "root") return entry.handler(repo, input);
  try {
    const located = ROOT_ENV_VAR in process.env ? findProjectRoot(repo) : findProjectRoot(repo, { root: repo });
    return entry.handler(located, input);
  } catch (error) {
    if (error instanceof ProjectRootNotFound) return failure(error.message, error.hint);
    throw error;
  }
}

function normalise<T>(value: T, root: string): T {
  if (typeof value === "string") return value.replaceAll(root, ROOT_PLACEHOLDER) as T;
  if (Array.isArray(value)) return value.map((item) => normalise(item, root)) as T;
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, normalise(item, root)])) as T;
  }
  return value;
}

/** Hints are not compared (ADR-004): only status, payload and message. */
function comparableResult(result: Result, root: string): Record<string, unknown> {
  return normalise(
    {
      status: result.status,
      ...(result.payload === undefined ? {} : { payload: result.payload }),
      ...(result.message === undefined ? {} : { message: result.message }),
    },
    root,
  );
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value)
        .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
        .map(([key, item]) => [key, sortKeys(item)]),
    );
  }
  return value;
}

function dump(value: unknown): string[] {
  return JSON.stringify(sortKeys(value), null, 2).split("\n");
}

/** A line diff of the two values (longest common subsequence); empty when they are equal. */
function diffValues(label: string, expected: unknown, actual: unknown): string[] {
  const a = dump(expected);
  const b = dump(actual);
  if (a.join("\n") === b.join("\n")) return [];

  const lcs = Array.from({ length: a.length + 1 }, () => new Array<number>(b.length + 1).fill(0));
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      lcs[i]![j] = a[i] === b[j] ? lcs[i + 1]![j + 1]! + 1 : Math.max(lcs[i + 1]![j]!, lcs[i]![j + 1]!);
    }
  }
  const lines = [`--- expected ${label}`, `+++ actual ${label}`];
  let i = 0;
  let j = 0;
  while (i < a.length || j < b.length) {
    if (i < a.length && j < b.length && a[i] === b[j]) {
      lines.push(` ${a[i]}`);
      i++;
      j++;
    } else if (j >= b.length || (i < a.length && lcs[i + 1]![j]! >= lcs[i]![j + 1]!)) {
      lines.push(`-${a[i]}`);
      i++;
    } else {
      lines.push(`+${b[j]}`);
      j++;
    }
  }
  return [lines.join("\n")];
}

/**
 * Runs one case and returns one diff per mismatch. A case whose command is still a stub is
 * reported as pending without being run, so it can never pass by accident.
 */
export function runCase(caseDir: string, fixturesRoot: string, registry: Registry): CaseOutcome {
  const definition = readCase(caseDir);
  const entry = registry[definition.command];
  if (entry === undefined) throw new Error(`Unknown parity command: '${definition.command}'`);
  if (isStub(entry.handler)) return { kind: "pending", command: definition.command };

  const before = readJson<TreeEntry[]>(join(caseDir, "before.json"));
  const expectedAfter = readJson<TreeEntry[]>(join(caseDir, "after.json"));

  const parent = realpathSync(mkdtempSync(join(tmpdir(), "ai-team-parity-")));
  const root = join(parent, "repo");
  try {
    materializeTree(before, root);
    const result = withIsolatedEnvironment(root, definition, () => dispatch(entry, root, definition.input));
    const actualAfter = normalise(
      excludeLockPaths(serializeTree(root), definition.project_dir ?? "project", loadLockExclusions(fixturesRoot)),
      root,
    );
    return {
      kind: "ran",
      diffs: [
        ...diffValues("result", definition.expected, comparableResult(result, root)),
        ...diffValues("after tree", expectedAfter, actualAfter),
      ],
    };
  } finally {
    rmSync(parent, { recursive: true, force: true });
  }
}
