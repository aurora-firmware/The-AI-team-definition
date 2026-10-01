import { readFileSync } from "node:fs";
import {
  FrontmatterError,
  parseFrontmatterSource,
  renderFrontmatterYaml,
  splitFrontmatter,
} from "./frontmatter.js";
import type { FieldValues, FrontmatterSource } from "./frontmatter.js";

export { FrontmatterError } from "./frontmatter.js";

/**
 * Frontmatter models for the five artifact kinds, mirroring `ai_team.core.models`.
 * `sourceMap` is set by the parsers; `dumpFrontmatter` uses it to keep comments and unknown keys.
 */
export interface Task {
  readonly kind: "task";
  id: string;
  title: string;
  status: string;
  priority: string;
  assignedRole: string;
  created: string;
  spec: string | undefined;
  sourceMap: FrontmatterSource | undefined;
}

export interface Bug {
  readonly kind: "bug";
  id: string;
  title: string;
  severity: string;
  status: string;
  /** Optional because legacy resolved artifacts pre-date this field. */
  created: string | undefined;
  task: string | undefined;
  sourceMap: FrontmatterSource | undefined;
}

export interface Spec {
  readonly kind: "spec";
  title: string;
  version: string;
  status: string;
  created: string;
  author: string;
  /** Legacy specs carry no id; they are identified by their filename slug. */
  id: string | undefined;
  sourceMap: FrontmatterSource | undefined;
}

export interface Adr {
  readonly kind: "adr";
  id: string;
  title: string;
  status: string;
  created: string;
  supersedes: string | undefined;
  sourceMap: FrontmatterSource | undefined;
}

export interface ChangeRequest {
  readonly kind: "change-request";
  id: string;
  title: string;
  status: string;
  created: string;
  sourceMap: FrontmatterSource | undefined;
}

export type ArtifactModel = Task | Bug | Spec | Adr | ChangeRequest;
export type ArtifactKind = ArtifactModel["kind"];

/** Mirrors Python's `_require`: the raw YAML key appears in the message, as does the path. */
function requireField(source: FrontmatterSource, key: string, path: string): string {
  const value = source.getString(key);
  if (value === undefined) {
    throw new FrontmatterError(
      `Required frontmatter field '${key}' is missing or null in ${path}`,
    );
  }
  return value;
}

export function parseTaskText(text: string, path: string): Task {
  const source = readSource(text, path);
  return {
    kind: "task",
    id: requireField(source, "id", path),
    title: requireField(source, "title", path),
    status: requireField(source, "status", path),
    priority: requireField(source, "priority", path),
    assignedRole: requireField(source, "assigned-role", path),
    created: requireField(source, "created", path),
    spec: source.getString("spec"),
    sourceMap: source,
  };
}

export function parseBugText(text: string, path: string): Bug {
  const source = readSource(text, path);
  return {
    kind: "bug",
    id: requireField(source, "id", path),
    title: requireField(source, "title", path),
    severity: requireField(source, "severity", path),
    status: requireField(source, "status", path),
    created: source.getString("created"),
    task: source.getString("task"),
    sourceMap: source,
  };
}

export function parseSpecText(text: string, path: string): Spec {
  const source = readSource(text, path);
  return {
    kind: "spec",
    title: requireField(source, "title", path),
    version: requireField(source, "version", path),
    status: requireField(source, "status", path),
    created: requireField(source, "created", path),
    author: requireField(source, "author", path),
    id: source.getString("id"),
    sourceMap: source,
  };
}

export function parseAdrText(text: string, path: string): Adr {
  const source = readSource(text, path);
  return {
    kind: "adr",
    id: requireField(source, "id", path),
    title: requireField(source, "title", path),
    status: requireField(source, "status", path),
    created: requireField(source, "created", path),
    supersedes: source.getString("supersedes"),
    sourceMap: source,
  };
}

export function parseChangeRequestText(text: string, path: string): ChangeRequest {
  const source = readSource(text, path);
  return {
    kind: "change-request",
    id: requireField(source, "id", path),
    title: requireField(source, "title", path),
    status: requireField(source, "status", path),
    created: requireField(source, "created", path),
    sourceMap: source,
  };
}

function readSource(text: string, path: string): FrontmatterSource {
  return parseFrontmatterSource(splitFrontmatter(text, path).yamlText, path);
}

function readArtifactFile(path: string): string {
  return readFileSync(path, "utf-8");
}

export const parseTask = (path: string): Task => parseTaskText(readArtifactFile(path), path);
export const parseBug = (path: string): Bug => parseBugText(readArtifactFile(path), path);
export const parseSpec = (path: string): Spec => parseSpecText(readArtifactFile(path), path);
export const parseAdr = (path: string): Adr => parseAdrText(readArtifactFile(path), path);
export const parseChangeRequest = (path: string): ChangeRequest =>
  parseChangeRequestText(readArtifactFile(path), path);

/** The markdown body after the frontmatter, as `dumpFrontmatter` expects it back. */
export function extractBody(text: string, path: string): string {
  return splitFrontmatter(text, path).body;
}

/** Key order here is the key order of a freshly dumped file. Undefined optional fields are omitted. */
function fieldValues(model: ArtifactModel): FieldValues {
  switch (model.kind) {
    case "task":
      return [
        ["id", model.id],
        ["title", model.title],
        ["status", model.status],
        ["priority", model.priority],
        ["assigned-role", model.assignedRole],
        ["created", model.created],
        ["spec", model.spec],
      ];
    case "bug":
      return [
        ["id", model.id],
        ["title", model.title],
        ["severity", model.severity],
        ["status", model.status],
        ["created", model.created],
        ["task", model.task],
      ];
    case "spec":
      return [
        ["title", model.title],
        ["version", model.version],
        ["status", model.status],
        ["created", model.created],
        ["author", model.author],
        ["id", model.id],
      ];
    case "adr":
      return [
        ["id", model.id],
        ["title", model.title],
        ["status", model.status],
        ["created", model.created],
        ["supersedes", model.supersedes],
      ];
    case "change-request":
      return [
        ["id", model.id],
        ["title", model.title],
        ["status", model.status],
        ["created", model.created],
      ];
  }
}

/** Serialises a model to a complete markdown file: frontmatter fences, a blank line, then the body. */
export function dumpFrontmatter(model: ArtifactModel, body: string): string {
  const yaml = renderFrontmatterYaml(fieldValues(model), model.sourceMap);
  return `---\n${yaml}---\n\n${body}`;
}
