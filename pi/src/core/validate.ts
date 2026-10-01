import { readdirSync, statSync } from "node:fs";
import { basename, join, sep } from "node:path";
import type { ProjectRoot } from "./locator.js";
import {
  FrontmatterError,
  parseAdr,
  parseBug,
  parseChangeRequest,
  parseSpec,
  parseTask,
} from "./models.js";

/**
 * Validation checks for AI-team artifacts, mirroring `ai_team.core.validate`.
 * Finding codes, messages, relative paths and ordering are compared by the parity fixtures.
 */

export interface Finding {
  readonly path: string;
  readonly level: string;
  readonly code: string;
  readonly message: string;
}

/** Which artifact categories to validate; the core takes explicit scopes, never a default. */
export interface ValidateScopes {
  readonly tasks?: boolean;
  readonly bugs?: boolean;
  readonly specs?: boolean;
  readonly adrs?: boolean;
  readonly changeRequests?: boolean;
}

/** An id pattern: `source` is the Python pattern text that findings print, `regex` matches like `re`. */
interface IdPattern {
  readonly source: string;
  readonly regex: RegExp;
}

// `\d` is written `\p{Nd}` in the matcher because Python's `\d` matches every Unicode digit.
function idPattern(prefix: string): IdPattern {
  return {
    source: `^${prefix}-\\d{3}$`,
    regex: new RegExp(`^${prefix}-\\p{Nd}{3}$`, "u"),
  };
}

const TASK_ID = idPattern("T");
const BUG_ID = idPattern("B");
const SPEC_ID = idPattern("S");
const ADR_ID = idPattern("ADR");
const CHANGE_REQUEST_ID = idPattern("CR");
const SLUGGED_FILENAME = /^[a-z0-9][a-z0-9-]*\.md$/;
/** New-style spec filenames: `S-NNN-<slug>.md`. */
const SPEC_PREFIXED_FILENAME = /^S-\p{Nd}{3}-[a-z0-9][a-z0-9-]*\.md$/u;

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Python compares strings by code point; the default sort compares UTF-16 units. */
function compareCodePoints(left: string, right: string): number {
  const leftPoints = Array.from(left);
  const rightPoints = Array.from(right);
  const shared = Math.min(leftPoints.length, rightPoints.length);
  for (let index = 0; index < shared; index += 1) {
    const difference = leftPoints[index]!.codePointAt(0)! - rightPoints[index]!.codePointAt(0)!;
    if (difference !== 0) return difference;
  }
  return leftPoints.length - rightPoints.length;
}

function isTemplate(name: string): boolean {
  return name.startsWith("TEMPLATE-") && name.endsWith(".md");
}

function shouldSkip(name: string): boolean {
  return name === ".gitkeep" || isTemplate(name);
}

function isFile(path: string): boolean {
  try {
    return statSync(path).isFile();
  } catch {
    return false;
  }
}

/** Markdown files directly inside `folder`, sorted by name; a missing folder has none. */
function iterMarkdownFiles(folder: string): string[] {
  let names: string[];
  try {
    names = readdirSync(folder);
  } catch {
    return [];
  }
  return names
    .filter((name) => name.endsWith(".md") && !shouldSkip(name))
    .sort(compareCodePoints)
    .map((name) => join(folder, name))
    .filter(isFile);
}

/** `path` relative to `repo` when it lies inside it, otherwise unchanged. */
export function toRelativePath(path: string, repo: string): string {
  const prefix = repo.endsWith(sep) ? repo : repo + sep;
  return path.startsWith(prefix) ? path.slice(prefix.length) : path;
}

function finding(path: string, root: ProjectRoot, code: string, message: string): Finding {
  return { path: toRelativePath(path, root.repo), level: "error", code, message };
}

function checkIdPattern(
  findings: Finding[],
  root: ProjectRoot,
  path: string,
  artifactLabel: string,
  artifactId: string,
  pattern: IdPattern,
): void {
  if (pattern.regex.test(artifactId)) return;
  findings.push(
    finding(
      path,
      root,
      "id-pattern",
      `${artifactLabel} id '${artifactId}' does not match expected pattern '${pattern.source}'.`,
    ),
  );
}

function checkStatefulFilename(
  findings: Finding[],
  root: ProjectRoot,
  path: string,
  artifactId: string,
): void {
  const name = basename(path);
  const expected = new RegExp(`^${escapeRegExp(artifactId)}-[a-z0-9][a-z0-9-]*\\.md$`);
  if (expected.test(name)) return;
  findings.push(
    finding(
      path,
      root,
      "filename-pattern",
      `Filename '${name}' does not match expected '${artifactId}-<slug>.md'.`,
    ),
  );
}

/**
 * Accepts the legacy `<slug>.md` and the new-style `S-NNN-<slug>.md` whose prefix matches the
 * frontmatter id. Reports `filename-pattern` when neither matches or the prefix disagrees.
 */
function checkSpecFilename(
  findings: Finding[],
  root: ProjectRoot,
  path: string,
  specId: string | undefined,
): void {
  const name = basename(path);
  if (SPEC_PREFIXED_FILENAME.test(name)) {
    const filenameId = name.split("-").slice(0, 2).join("-");
    if (specId !== undefined && filenameId !== specId) {
      findings.push(
        finding(
          path,
          root,
          "filename-pattern",
          `Spec filename '${name}' id prefix '${filenameId}' does not match frontmatter id '${specId}'.`,
        ),
      );
    }
    return;
  }
  if (SLUGGED_FILENAME.test(name)) return;
  findings.push(
    finding(
      path,
      root,
      "filename-pattern",
      `Spec filename '${name}' does not match '<slug>.md' or 'S-NNN-<slug>.md'.`,
    ),
  );
}

function specReferenceExists(reference: string, specSlugs: ReadonlySet<string>): boolean {
  if (specSlugs.has(reference)) return true;
  return reference.endsWith(".md") && specSlugs.has(reference.slice(0, -3));
}

function stem(path: string): string {
  return basename(path).slice(0, -".md".length);
}

/** Every reference string that resolves to the spec at `path`: stem, legacy bare slug, and id. */
function specIndexEntries(path: string): Set<string> {
  const entries = new Set([stem(path)]);
  if (SPEC_PREFIXED_FILENAME.test(basename(path))) {
    entries.add(stem(path).split("-").slice(2).join("-"));
  }
  try {
    const spec = parseSpec(path);
    if (spec.id !== undefined) entries.add(spec.id);
  } catch (error) {
    if (!(error instanceof FrontmatterError)) throw error;
  }
  return entries;
}

/** Scans `specs/` and `specs/archive/` so archived specs stay resolvable by task references. */
function buildSpecSlugs(root: ProjectRoot): Set<string> {
  const slugs = new Set<string>();
  for (const folder of [root.specs, join(root.specs, "archive")]) {
    for (const path of iterMarkdownFiles(folder)) {
      for (const entry of specIndexEntries(path)) slugs.add(entry);
    }
  }
  return slugs;
}

function existingIds(folders: readonly string[], parse: (path: string) => { id: string }): Set<string> {
  const ids = new Set<string>();
  for (const folder of folders) {
    for (const path of iterMarkdownFiles(folder)) {
      try {
        ids.add(parse(path).id);
      } catch (error) {
        if (!(error instanceof FrontmatterError)) throw error;
      }
    }
  }
  return ids;
}

/** Runs `check` on each parsed artifact; a parse failure becomes a `frontmatter-invalid` finding. */
function forEachParsed<T>(
  findings: Finding[],
  root: ProjectRoot,
  paths: readonly string[],
  parse: (path: string) => T,
  check: (path: string, artifact: T) => void,
): void {
  for (const path of paths) {
    let artifact: T;
    try {
      artifact = parse(path);
    } catch (error) {
      if (!(error instanceof FrontmatterError)) throw error;
      findings.push(finding(path, root, "frontmatter-invalid", error.message));
      continue;
    }
    check(path, artifact);
  }
}

/** Validates the selected artifact categories and returns the findings in discovery order. */
export function validateProject(root: ProjectRoot, scopes: ValidateScopes): Finding[] {
  const findings: Finding[] = [];

  // Cross-reference indexes are built independently of the selected scopes so a single scope
  // can still validate its references.
  const taskFolders = [
    ["pending", root.tasksPending],
    ["in-progress", root.tasksInProgress],
    ["completed", root.tasksCompleted],
    ["blocked", root.tasksBlocked],
  ] as const;
  const specSlugs = buildSpecSlugs(root);
  const taskIds = existingIds(
    taskFolders.map(([, folder]) => folder),
    parseTask,
  );
  const adrIds = existingIds([root.decisions], parseAdr);

  if (scopes.tasks) {
    for (const [expectedState, folder] of taskFolders) {
      forEachParsed(findings, root, iterMarkdownFiles(folder), parseTask, (path, task) => {
        checkIdPattern(findings, root, path, "Task", task.id, TASK_ID);
        checkStatefulFilename(findings, root, path, task.id);
        if (task.status !== expectedState) {
          findings.push(
            finding(
              path,
              root,
              "status-mismatch",
              `Task status '${task.status}' does not match folder state '${expectedState}'.`,
            ),
          );
        }
        if (task.spec && !specReferenceExists(task.spec, specSlugs)) {
          findings.push(
            finding(
              path,
              root,
              "task-spec-missing",
              `Task spec reference '${task.spec}' does not resolve to an existing spec file.`,
            ),
          );
        }
      });
    }
  }

  if (scopes.bugs) {
    const bugFolders = [
      ["open", root.bugsOpen],
      ["in-progress", root.bugsInProgress],
      ["resolved", root.bugsResolved],
    ] as const;
    for (const [expectedState, folder] of bugFolders) {
      forEachParsed(findings, root, iterMarkdownFiles(folder), parseBug, (path, bug) => {
        checkIdPattern(findings, root, path, "Bug", bug.id, BUG_ID);
        checkStatefulFilename(findings, root, path, bug.id);
        if (bug.status !== expectedState) {
          findings.push(
            finding(
              path,
              root,
              "status-mismatch",
              `Bug status '${bug.status}' does not match folder state '${expectedState}'.`,
            ),
          );
        }
        if (bug.task && !taskIds.has(bug.task)) {
          findings.push(
            finding(
              path,
              root,
              "bug-task-missing",
              `Bug task reference '${bug.task}' does not resolve to an existing task.`,
            ),
          );
        }
      });
    }
  }

  if (scopes.specs) {
    forEachParsed(findings, root, iterMarkdownFiles(root.specs), parseSpec, (path, spec) => {
      // The model fills a missing id with undefined; the id check reads the raw frontmatter.
      const specId = spec.sourceMap?.getString("id");
      if (specId === undefined) {
        findings.push(
          finding(path, root, "id-missing", "Spec frontmatter is missing required 'id' field."),
        );
      } else {
        checkIdPattern(findings, root, path, "Spec", specId, SPEC_ID);
      }
      checkSpecFilename(findings, root, path, specId || undefined);
    });
  }

  if (scopes.adrs) {
    forEachParsed(findings, root, iterMarkdownFiles(root.decisions), parseAdr, (path, adr) => {
      checkIdPattern(findings, root, path, "ADR", adr.id, ADR_ID);
      checkStatefulFilename(findings, root, path, adr.id);
      if (adr.supersedes && !adrIds.has(adr.supersedes)) {
        findings.push(
          finding(
            path,
            root,
            "adr-supersedes-missing",
            `ADR supersedes reference '${adr.supersedes}' does not resolve to an existing ADR.`,
          ),
        );
      }
    });
  }

  if (scopes.changeRequests) {
    forEachParsed(
      findings,
      root,
      iterMarkdownFiles(root.changeRequests),
      parseChangeRequest,
      (path, changeRequest) => {
        checkIdPattern(
          findings,
          root,
          path,
          "Change request",
          changeRequest.id,
          CHANGE_REQUEST_ID,
        );
        checkStatefulFilename(findings, root, path, changeRequest.id);
      },
    );
  }

  return findings;
}
