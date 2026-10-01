import { readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseToml } from "smol-toml";
import { isErrnoCode } from "./errno.js";
import type { ProjectRoot } from "./locator.js";
import { AiTeamError } from "./result.js";
import { frameworkVersion } from "./runtime.js";
import type { Environment } from "./runtime.js";
import { validateProject } from "./validate.js";
import type { Finding as ArtifactFinding } from "./validate.js";

/**
 * Read-only resolution and validation of the AI-team repository layout, mirroring
 * `ai_team.core.layout` (Levels 1-4). Problem text, suggested fixes, paths and ordering are
 * compared by the check-layout parity fixtures. The suggested fix is its own field.
 */

export interface LayoutFinding {
  readonly level: number;
  readonly path: string;
  readonly problem: string;
  readonly suggestedFix: string;
}

type Status = "valid" | "missing" | "invalid";

export interface LayoutContract {
  readonly repo: string;
  readonly marker: string;
  readonly projectDir: string;
  readonly tools: readonly string[];
  readonly configuredVersion: string | undefined;
  readonly currentVersion: string;
  readonly rawConfiguredVersion: unknown;
  readonly markerStatus: Status;
  readonly toolsStatus: Status;
  readonly versionStatus: Status;
}

export interface CheckLayoutOptions {
  /** The installed framework version; defaults to the runtime version (override or version file). */
  readonly currentVersion?: string;
  readonly env?: Environment;
}

const SUPPORTED_TOOLS = ["claude", "codex"];
const DEFAULT_PROJECT_DIR = "project";
const GUIDANCE_BY_TOOL: Readonly<Record<string, string>> = {
  claude: "CLAUDE.md",
  codex: "AGENTS.md",
};
const GUIDANCE_HEADINGS = ["Build and Install", "Test", "Run", "Lint and Format", "Key Conventions"];
// Python's `re` semantics, spelled out: `$` and `^` see only "\n" as a line break, never "\r".
const HEADING_PATTERN = /(?<![^\n])##[ \t]+([^\n]+?)[ \t]*#*[ \t]*(?=\n|(?![\s\S]))/g;
const VERSION_PATTERN =
  /^[0-9]+(?:\.[0-9]+)*(?:[A-Za-z][A-Za-z0-9.-]*[0-9]?|[.+-][A-Za-z0-9.-]+)*$/;
const LINE_BREAKS = /\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/;

/** Synced from the init scaffolds by `python scripts/sync_init_scaffolds.py`. */
const RESOURCES_DIR = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "resources");

function compareText(left: string, right: string): number {
  if (left === right) return 0;
  const leftPoints = Array.from(left);
  const rightPoints = Array.from(right);
  const shared = Math.min(leftPoints.length, rightPoints.length);
  for (let index = 0; index < shared; index += 1) {
    const difference = (leftPoints[index]?.codePointAt(0) ?? 0) - (rightPoints[index]?.codePointAt(0) ?? 0);
    if (difference !== 0) return difference;
  }
  return leftPoints.length - rightPoints.length;
}

function compareFindings(left: LayoutFinding, right: LayoutFinding): number {
  return (
    left.level - right.level ||
    compareText(left.path, right.path) ||
    compareText(left.problem, right.problem) ||
    compareText(left.suggestedFix, right.suggestedFix)
  );
}

function sorted(findings: LayoutFinding[]): LayoutFinding[] {
  return [...findings].sort(compareFindings);
}

function finding(level: number, path: string, problem: string, suggestedFix: string): LayoutFinding {
  return { level, path, problem, suggestedFix };
}

function quoteLikePython(text: string): string {
  const quote = text.includes("'") && !text.includes('"') ? '"' : "'";
  let body = "";
  for (const char of text) {
    const code = char.codePointAt(0) ?? 0;
    if (char === "\\" || char === quote) body += `\\${char}`;
    else if (char === "\n") body += "\\n";
    else if (char === "\r") body += "\\r";
    else if (char === "\t") body += "\\t";
    else if (code < 0x20 || code === 0x7f) body += `\\x${code.toString(16).padStart(2, "0")}`;
    else body += char;
  }
  return `${quote}${body}${quote}`;
}

/** The Python `repr` of a parsed TOML value, so messages match the Python CLI. */
function pythonRepr(value: unknown): string {
  if (typeof value === "string") return quoteLikePython(value);
  if (typeof value === "boolean") return value ? "True" : "False";
  if (value === null || value === undefined) return "None";
  if (Array.isArray(value)) return `[${value.map(pythonRepr).join(", ")}]`;
  if (typeof value === "object") {
    const entries = Object.entries(value).map(([key, item]) => `${pythonRepr(key)}: ${pythonRepr(item)}`);
    return `{${entries.join(", ")}}`;
  }
  return String(value);
}

function isProjectDirName(value: unknown): value is string {
  return (
    typeof value === "string" &&
    value !== "" &&
    value !== "." &&
    value !== ".." &&
    !value.includes("/") &&
    !value.includes("\\") &&
    !isAbsolute(value)
  );
}

function isVersion(value: unknown): value is string {
  return typeof value === "string" && VERSION_PATTERN.test(value);
}

function isFile(path: string): boolean {
  try {
    return statSync(path).isFile();
  } catch {
    return false;
  }
}

function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

/** Absolute path with symlinks resolved when the path exists, like Python's `Path.resolve()`. */
function resolvePath(path: string): string {
  const absolute = resolve(path);
  try {
    return realpathSync(absolute);
  } catch {
    return absolute;
  }
}

function relativeToRepo(path: string, repo: string): string {
  return path.slice(repo.length + 1);
}

/** Strict UTF-8 text with Python's universal newlines; the BOM is kept like Python keeps it. */
function readUtf8Text(path: string): string {
  const decoder = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });
  return decoder.decode(readFileSync(path)).replace(/\r\n?/g, "\n");
}

function describeTomlError(error: unknown, source: string): string {
  if (!(error instanceof Error)) return String(error);
  const { line, column } = error as Error & { line?: number; column?: number };
  if (line === undefined || column === undefined) return error.message;
  const lines = source.split("\n");
  const failingLine = lines[line - 1] ?? "";
  // tomllib words an unterminated table header specially; smol-toml only says "illegal character".
  if (failingLine.trimStart().startsWith("[") && !failingLine.includes("]")) {
    const atEndOfDocument = line === lines.length;
    const where = atEndOfDocument ? "at end of document" : `at line ${line}, column ${failingLine.length + 1}`;
    return `Expected ']' at the end of a table declaration (${where})`;
  }
  const reason = (error.message.split("\n")[0] ?? "").replace(/^Invalid TOML document: /, "");
  return `${reason} (at line ${line}, column ${column})`;
}

function asTable(value: unknown): Record<string, unknown> | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : undefined;
}

/** Resolves marker configuration and installed contract data without mutation. */
export function resolveLayout(
  repoPath: string,
  options: CheckLayoutOptions = {},
): { contract: LayoutContract; findings: LayoutFinding[] } {
  const repo = resolvePath(repoPath);
  const marker = join(repo, ".ai-team.toml");
  const findings: LayoutFinding[] = [];
  let markerStatus: Status = "valid";
  let data: Record<string, unknown> = {};

  if (!isFile(marker)) {
    markerStatus = "missing";
    findings.push(
      finding(
        1,
        ".ai-team.toml",
        "Repository marker .ai-team.toml is missing; project and tool settings cannot be resolved.",
        "Run 'ai-team init' or restore .ai-team.toml; repository conventions will be checked where safe.",
      ),
    );
  } else {
    let source = "";
    try {
      source = readUtf8Text(marker);
      data = parseToml(source);
    } catch (error) {
      markerStatus = "invalid";
      findings.push(
        finding(
          1,
          ".ai-team.toml",
          `Repository marker .ai-team.toml is invalid: ${describeTomlError(error, source)}`,
          "Correct the TOML syntax or regenerate the marker with 'ai-team init'.",
        ),
      );
    }
  }

  let projectValue: unknown;
  let toolsValue: unknown;
  let versionValue: unknown;
  if (markerStatus === "valid") {
    projectValue = asTable(data.project)?.dir;
    const initTable = asTable(data.init);
    toolsValue = initTable?.tools;
    versionValue = initTable?.framework_version;
  }

  let projectDirName = DEFAULT_PROJECT_DIR;
  if (markerStatus === "valid") {
    if (isProjectDirName(projectValue)) {
      projectDirName = projectValue;
    } else {
      findings.push(
        finding(
          1,
          ".ai-team.toml",
          "Marker value [project].dir is missing or invalid; using the conventional 'project' directory.",
          "Set [project].dir to one usable relative directory name, such as 'project'.",
        ),
      );
    }
  }

  const selectedTools: string[] = [];
  let toolsStatus: Status = "valid";
  if (markerStatus === "valid") {
    if (!Array.isArray(toolsValue)) {
      toolsStatus = toolsValue === undefined ? "missing" : "invalid";
      findings.push(
        finding(
          1,
          ".ai-team.toml",
          "Marker value [init].tools is missing or invalid; no tool directories can be selected safely.",
          "Set [init].tools to an array containing supported tool names: 'claude' and/or 'codex'.",
        ),
      );
    } else {
      const isSupported = (value: unknown): value is string =>
        typeof value === "string" && SUPPORTED_TOOLS.includes(value);
      const invalidTools = toolsValue.filter((value) => !isSupported(value));
      for (const value of toolsValue) {
        if (isSupported(value) && !selectedTools.includes(value)) selectedTools.push(value);
      }
      if (invalidTools.length > 0) {
        toolsStatus = "invalid";
        findings.push(
          finding(
            1,
            ".ai-team.toml",
            `Marker contains unsupported or invalid configured tools: ${pythonRepr(invalidTools)}.`,
            "Keep only supported tool names: 'claude' and/or 'codex'.",
          ),
        );
      }
    }
  } else {
    toolsStatus = markerStatus;
  }

  let versionStatus: Status = "valid";
  let configuredVersion: string | undefined;
  if (markerStatus !== "valid" || versionValue === undefined) {
    versionStatus = "missing";
  } else if (isVersion(versionValue)) {
    configuredVersion = versionValue;
  } else {
    versionStatus = "invalid";
  }

  const currentVersion = options.currentVersion ?? frameworkVersion(options.env);
  return {
    contract: {
      repo,
      marker,
      projectDir: join(repo, projectDirName),
      tools: selectedTools,
      configuredVersion,
      currentVersion,
      rawConfiguredVersion: versionValue,
      markerStatus,
      toolsStatus,
      versionStatus,
    },
    findings: sorted(findings),
  };
}

function loadScaffoldDirectories(): Record<string, readonly string[]> {
  const path = join(RESOURCES_DIR, "scaffold-dirs.json");
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch (error) {
    if (isErrnoCode(error, "ENOENT")) {
      throw new AiTeamError(
        `Scaffold directory list not found at ${path}.`,
        "Run the sync (cd cli && python scripts/sync_init_scaffolds.py) to generate pi/resources.",
      );
    }
    throw error;
  }
}

function expectedDirectories(contract: LayoutContract): string[] {
  const scaffold = loadScaffoldDirectories();
  const expected = [contract.projectDir];
  expected.push(...(scaffold.project ?? []).map((relative) => join(contract.projectDir, relative)));
  for (const tool of contract.tools) {
    const toolRoot = join(contract.repo, `.${tool}`);
    expected.push(toolRoot);
    expected.push(...(scaffold[tool] ?? []).map((relative) => join(toolRoot, relative)));
  }
  return expected;
}

export function checkLevel1(contract: LayoutContract): LayoutFinding[] {
  const findings: LayoutFinding[] = [];
  for (const path of expectedDirectories(contract)) {
    if (isDirectory(path)) continue;
    const displayPath = relativeToRepo(path, contract.repo);
    findings.push(
      finding(
        1,
        displayPath,
        `Required scaffold directory '${displayPath}' is missing.`,
        "Create the directory by restoring the current scaffold or rerunning 'ai-team init' with the configured tools.",
      ),
    );
  }
  return sorted(findings);
}

const LEVEL_2_CODES = new Set([
  "filename-pattern",
  "frontmatter-invalid",
  "id-missing",
  "id-pattern",
  "status-mismatch",
]);

function artifactSuggestedFix(artifactFinding: ArtifactFinding): string {
  switch (artifactFinding.code) {
    case "filename-pattern":
      return "Rename the artifact to the filename convention stated in the problem.";
    case "status-mismatch":
      return (
        "Update the frontmatter status to match the lifecycle directory, or move " +
        "the artifact to the directory matching its current status."
      );
    case "id-pattern":
      return "Correct the frontmatter id to the required artifact ID pattern.";
    case "id-missing":
      return "Add the required artifact id to the YAML frontmatter.";
    default:
      return "Correct the YAML frontmatter and add every required field for this artifact type.";
  }
}

/** The artifact folders under a project directory, as `ProjectRoot` lays them out. */
function projectRootFor(repo: string, projectDir: string): ProjectRoot {
  return {
    repo,
    projectDir,
    specs: join(projectDir, "specs"),
    tasksPending: join(projectDir, "tasks", "pending"),
    tasksInProgress: join(projectDir, "tasks", "in-progress"),
    tasksCompleted: join(projectDir, "tasks", "completed"),
    tasksBlocked: join(projectDir, "tasks", "blocked"),
    bugsOpen: join(projectDir, "bugs", "open"),
    bugsInProgress: join(projectDir, "bugs", "in-progress"),
    bugsResolved: join(projectDir, "bugs", "resolved"),
    changeRequests: join(projectDir, "change-requests"),
    decisions: join(projectDir, "decisions"),
    docs: join(projectDir, "docs"),
  };
}

const LEVEL_2_SCOPES = [
  { label: "specs", scopes: { specs: true } },
  { label: "tasks", scopes: { tasks: true } },
  { label: "bugs", scopes: { bugs: true } },
  { label: "change requests", scopes: { changeRequests: true } },
  { label: "adrs", scopes: { adrs: true } },
] as const;

function isSystemError(error: unknown): error is Error {
  return error instanceof Error && typeof (error as { code?: unknown }).code === "string";
}

export function checkLevel2(contract: LayoutContract): LayoutFinding[] {
  const displayPath = relativeToRepo(contract.projectDir, contract.repo);
  if (!isDirectory(contract.projectDir)) {
    return [
      finding(
        2,
        displayPath,
        `Artifact checks are blocked because project directory '${displayPath}' is missing or is not a directory.`,
        "Restore the configured project directory, then rerun the layout check.",
      ),
    ];
  }

  const root = projectRootFor(contract.repo, contract.projectDir);
  const findings: LayoutFinding[] = [];
  for (const { label, scopes } of LEVEL_2_SCOPES) {
    let artifactFindings: ArtifactFinding[];
    try {
      artifactFindings = validateProject(root, scopes);
    } catch (error) {
      if (!isSystemError(error)) throw error;
      findings.push(
        finding(
          2,
          displayPath,
          `The ${label} artifact check is blocked: ${error.message}`,
          "Restore readable managed artifact inputs, then rerun the layout check.",
        ),
      );
      continue;
    }
    for (const artifactFinding of artifactFindings) {
      if (!LEVEL_2_CODES.has(artifactFinding.code)) continue;
      findings.push(
        finding(2, artifactFinding.path, artifactFinding.message, artifactSuggestedFix(artifactFinding)),
      );
    }
  }
  return sorted(findings);
}

function markdownSections(content: string): Map<string, string> {
  const matches = [...content.matchAll(HEADING_PATTERN)];
  const sections = new Map<string, string>();
  matches.forEach((match, index) => {
    const start = match.index + match[0].length;
    const end = matches[index + 1]?.index ?? content.length;
    sections.set((match[1] ?? "").trim(), content.slice(start, end).trim());
  });
  return sections;
}

function contentLines(content: string): Set<string> {
  const lines = content
    .split(LINE_BREAKS)
    .map((line) => line.trim())
    .filter((line) => line !== "" && !line.startsWith("```"));
  return new Set(lines);
}

function starterGuidanceSections(filename: string): Map<string, string> {
  return markdownSections(readUtf8Text(join(RESOURCES_DIR, "root", filename)));
}

function isPlaceholderSection(content: string, starterContent: string): boolean {
  const lines = contentLines(content);
  const starterLines = contentLines(starterContent);
  return [...lines].every((line) => starterLines.has(line));
}

export function checkLevel3(contract: LayoutContract): LayoutFinding[] {
  const findings: LayoutFinding[] = [];
  if (contract.toolsStatus !== "valid") {
    findings.push(
      finding(
        3,
        ".ai-team.toml",
        "Root guidance selection is blocked by missing or invalid configured tools.",
        "Set [init].tools to an array containing 'claude' and/or 'codex', then rerun the layout check.",
      ),
    );
  }

  for (const tool of contract.tools) {
    const filename = GUIDANCE_BY_TOOL[tool] ?? "";
    const path = join(contract.repo, filename);
    if (!isFile(path)) {
      findings.push(
        finding(
          3,
          filename,
          `Configured tool '${tool}' requires root guidance file '${filename}', but it is missing.`,
          `Create '${filename}' and fill every required project-guidance section.`,
        ),
      );
      continue;
    }

    let content: string;
    try {
      content = readUtf8Text(path);
    } catch (error) {
      if (!isSystemError(error) && !(error instanceof TypeError)) throw error;
      findings.push(
        finding(
          3,
          filename,
          `Root guidance checks for '${filename}' are blocked: ${error.message}`,
          "Restore a readable UTF-8 guidance file, then rerun the layout check.",
        ),
      );
      continue;
    }

    const starterSections = starterGuidanceSections(filename);
    const sections = markdownSections(content);
    for (const heading of GUIDANCE_HEADINGS) {
      const section = sections.get(heading);
      if (section === undefined) {
        findings.push(
          finding(
            3,
            filename,
            `Root guidance file '${filename}' is missing required section '${heading}'.`,
            `Add a '## ${heading}' section containing project-specific guidance.`,
          ),
        );
      } else if (isPlaceholderSection(section, starterSections.get(heading) ?? "")) {
        findings.push(
          finding(
            3,
            filename,
            `Required section '${heading}' in '${filename}' contains only starter-template placeholder content.`,
            `Replace the '${heading}' placeholder with project-specific guidance.`,
          ),
        );
      }
    }
  }
  return sorted(findings);
}

export function checkLevel4(contract: LayoutContract): LayoutFinding[] {
  const current = pythonRepr(contract.currentVersion);
  if (contract.versionStatus === "missing") {
    return [
      finding(
        4,
        ".ai-team.toml",
        `Configured framework version is missing (unavailable); current CLI version is ${current}.`,
        "Set [init].framework_version to the exact current CLI distribution version.",
      ),
    ];
  }
  if (contract.versionStatus === "invalid") {
    return [
      finding(
        4,
        ".ai-team.toml",
        `Configured framework version ${pythonRepr(contract.rawConfiguredVersion)} is invalid; current CLI version is ${current}.`,
        "Set [init].framework_version to a valid version string matching the current CLI exactly.",
      ),
    ];
  }
  if (contract.configuredVersion !== contract.currentVersion) {
    return [
      finding(
        4,
        ".ai-team.toml",
        `Configured framework version ${pythonRepr(contract.configuredVersion)} does not exactly match current CLI version ${current}.`,
        "Reinitialize or update the scaffold and record the exact current CLI version.",
      ),
    ];
  }
  return [];
}

/** Runs layout Levels 1-4 and returns deterministic findings. */
export function checkLayout(repo: string, options: CheckLayoutOptions = {}): LayoutFinding[] {
  const { contract, findings } = resolveLayout(repo, options);
  return sorted([
    ...findings,
    ...checkLevel1(contract),
    ...checkLevel2(contract),
    ...checkLevel3(contract),
    ...checkLevel4(contract),
  ]);
}
