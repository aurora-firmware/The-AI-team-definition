import {
  existsSync,
  readFileSync,
  realpathSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { isErrnoCode } from "./errno.js";
import {
  dumpFrontmatter,
  extractBody,
  parseAdrText,
  parseBugText,
  parseChangeRequestText,
  parseSpecText,
  parseTaskText,
} from "./models.js";
import type { ArtifactKind, ArtifactModel } from "./models.js";

/**
 * The single chokepoint for filesystem mutation of AI-team artifacts, mirroring
 * `ai_team.core.fs`. Error messages are the Python ones: the parity fixtures compare them.
 */

/** An artifact file that must exist is not at the given path. */
export class ArtifactNotFound extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ArtifactNotFound";
  }
}

/** The operation would silently overwrite an existing artifact file. */
export class ArtifactExists extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ArtifactExists";
  }
}

export interface ReadArtifactResult {
  readonly model: ArtifactModel;
  /** The markdown after the frontmatter, in the form `writeArtifact` takes back. */
  readonly body: string;
}

export interface WriteArtifactOptions {
  readonly overwrite?: boolean;
}

function parseModel(kind: ArtifactKind, text: string, path: string): ArtifactModel {
  switch (kind) {
    case "task":
      return parseTaskText(text, path);
    case "bug":
      return parseBugText(text, path);
    case "spec":
      return parseSpecText(text, path);
    case "adr":
      return parseAdrText(text, path);
    case "change-request":
      return parseChangeRequestText(text, path);
  }
}

function readText(path: string, notFoundMessage: string): string {
  try {
    return readFileSync(path, "utf-8");
  } catch (error) {
    if (isErrnoCode(error, "ENOENT")) throw new ArtifactNotFound(notFoundMessage);
    throw error;
  }
}

/** Writes through a sibling temporary file and a rename, so the destination is never half-written. */
function writeAtomically(path: string, content: string): void {
  const temporaryPath = `${path}.tmp~`;
  try {
    writeFileSync(temporaryPath, content, "utf-8");
    renameSync(temporaryPath, path);
  } catch (error) {
    rmSync(temporaryPath, { force: true });
    throw error;
  }
}

/**
 * Absolute path with symlinks resolved as far as the path exists, like Python's `Path.resolve()`.
 * The part that does not exist yet is appended unchanged.
 */
function resolveExistingPrefix(path: string): string {
  const absolute = resolve(path);
  try {
    return realpathSync(absolute);
  } catch (error) {
    if (!isErrnoCode(error, "ENOENT")) throw error;
    const parent = dirname(absolute);
    return parent === absolute ? absolute : join(resolveExistingPrefix(parent), basename(absolute));
  }
}

/** Mirrors the Python field-name heuristic; a change request has the same fields as an ADR. */
function inferKind(text: string): ArtifactKind {
  const parts = text.split("---");
  const frontmatter = parts.length >= 3 ? (parts[1] ?? "") : "";
  if (frontmatter.includes("severity:")) return "bug";
  if (frontmatter.includes("assigned-role:")) return "task";
  if (frontmatter.includes("author:")) return "spec";
  return "adr";
}

/**
 * Parses an artifact file.
 * @throws ArtifactNotFound when `path` does not exist.
 * @throws FrontmatterError when the frontmatter is absent or malformed.
 */
export function readArtifact(path: string, kind: ArtifactKind): ReadArtifactResult {
  const text = readText(path, `Artifact file not found: ${path}`);
  return { model: parseModel(kind, text, path), body: extractBody(text, path) };
}

/**
 * Writes an artifact file atomically.
 * @throws ArtifactExists when `path` exists and `overwrite` is not set.
 */
export function writeArtifact(
  path: string,
  model: ArtifactModel,
  body: string,
  options: WriteArtifactOptions = {},
): void {
  if (existsSync(path) && options.overwrite !== true) {
    throw new ArtifactExists(
      `Artifact already exists at ${path}; pass overwrite=True to replace it.`,
    );
  }
  writeAtomically(path, dumpFrontmatter(model, body));
}

/**
 * Renames `source` to `destination`; a no-op when both resolve to the same path.
 * @throws ArtifactNotFound when `source` does not exist.
 * @throws ArtifactExists when `destination` already exists.
 */
export function moveArtifact(source: string, destination: string): void {
  const resolvedSource = resolveExistingPrefix(source);
  const resolvedDestination = resolveExistingPrefix(destination);
  if (resolvedSource === resolvedDestination) return;
  if (!existsSync(resolvedSource)) {
    throw new ArtifactNotFound(`Source artifact not found: ${resolvedSource}`);
  }
  if (existsSync(resolvedDestination)) {
    throw new ArtifactExists(
      `Destination already exists: ${resolvedDestination}; cannot move artifact there.`,
    );
  }
  renameSync(resolvedSource, resolvedDestination);
}

/**
 * Rewrites the `status` frontmatter field, keeping comments, key order and the body.
 * The artifact kind is inferred from the frontmatter field names.
 * @throws ArtifactNotFound when `path` does not exist.
 * @throws FrontmatterError when the frontmatter is absent or malformed.
 */
export function updateStatus(path: string, newStatus: string): void {
  const text = readText(path, `Artifact file not found: ${path}`);
  const { model, body } = readArtifact(path, inferKind(text));
  model.status = newStatus;
  writeAtomically(path, dumpFrontmatter(model, body));
}
