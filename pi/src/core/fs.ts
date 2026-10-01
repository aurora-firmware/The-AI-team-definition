import { existsSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
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
