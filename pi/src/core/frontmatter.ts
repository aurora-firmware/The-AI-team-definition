import { isCollection, isMap, isScalar, parseDocument, Scalar, stringify } from "yaml";
import type { Pair } from "yaml";
import { emitScalarEntry, resolvesToNonString } from "./scalar-emitter.js";
import type { TrailingComment } from "./scalar-emitter.js";

/** A frontmatter field is missing or invalid; the message names the field and source path. */
export class FrontmatterError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FrontmatterError";
  }
}

/** A mapping value as it was read, kept so a rewrite can reproduce what the model did not change. */
type SourceValue =
  | { readonly kind: "string"; readonly value: string }
  /** A plain scalar ruamel reads as a non-string (number, bool, date, null): written back as it was. */
  | { readonly kind: "literal"; readonly text: string; readonly pythonString: string | undefined }
  /** A collection or block scalar, re-rendered whole including its key. */
  | { readonly kind: "block"; readonly text: string };

interface SourceEntry {
  readonly key: string;
  /** Comment and blank lines that sat above the key. */
  readonly before: readonly string[];
  readonly value: SourceValue;
  readonly comment: TrailingComment | undefined;
}

/**
 * The parsed frontmatter mapping in key order, with the comments that surround it.
 * A model that carries one rewrites the file in place; without one, a fresh mapping is built.
 */
export class FrontmatterSource {
  constructor(
    readonly entries: readonly SourceEntry[],
    /** Comment and blank lines after the last entry. */
    readonly after: readonly string[],
  ) {}

  /** The value for `key` as Python's `str()` renders it, or undefined when absent or null. */
  getString(key: string): string | undefined {
    const entry = this.entries.find((candidate) => candidate.key === key);
    if (entry === undefined) return undefined;
    if (entry.value.kind === "string") return entry.value.value;
    if (entry.value.kind === "literal") return entry.value.pythonString;
    throw new FrontmatterError(`Frontmatter field '${key}' must be a scalar value`);
  }
}

export interface FrontmatterParts {
  readonly yamlText: string;
  readonly body: string;
}

/**
 * Splits a markdown file at its frontmatter fences. The single blank line `dumpFrontmatter`
 * writes between the closing fence and the body is consumed, so parse then dump is stable.
 */
export function splitFrontmatter(text: string, path: string): FrontmatterParts {
  if (!text.startsWith("---")) {
    throw new FrontmatterError(`No YAML frontmatter block found in ${path}`);
  }
  const rest = text.slice(3);
  const closeIndex = rest.indexOf("\n---");
  if (closeIndex === -1) {
    throw new FrontmatterError(
      `Unclosed YAML frontmatter block (missing closing ---) in ${path}`,
    );
  }
  const body = rest.slice(closeIndex + 5);
  return { yamlText: rest.slice(0, closeIndex), body: body.startsWith("\n") ? body.slice(1) : body };
}

function pythonNumberString(value: number, sourceText: string): string {
  const isFloatText = /[.eE]/.test(sourceText) && !/^[-+]?0[xXoObB]/.test(sourceText);
  return isFloatText && Number.isInteger(value) ? value.toFixed(1) : String(value);
}

function describeSourceValue(pair: Pair, yamlText: string): SourceValue {
  const node = pair.value;
  if (isScalar(node)) {
    const { value } = node;
    if (typeof value === "string") {
      const plain = node.type === Scalar.PLAIN || node.type === undefined;
      const quoted = node.type === Scalar.QUOTE_DOUBLE || node.type === Scalar.QUOTE_SINGLE;
      if (quoted || (plain && !resolvesToNonString(value))) return { kind: "string", value };
      if (plain) return { kind: "literal", text: value, pythonString: value };
    } else if (value === null) {
      return { kind: "literal", text: "", pythonString: undefined };
    } else if (typeof value === "boolean") {
      return { kind: "literal", text: String(value), pythonString: value ? "True" : "False" };
    } else if (typeof value === "number") {
      const text = node.range ? yamlText.slice(node.range[0], node.range[1]) : String(value);
      return { kind: "literal", text, pythonString: pythonNumberString(value, text) };
    }
  }
  const text = stringify({ [String(pair.key)]: isScalar(node) || isCollection(node) ? node.toJSON() : null }, {
    lineWidth: 80,
    indentSeq: false,
  });
  return { kind: "block", text: text.replace(/\n$/, "") };
}

function codePointColumn(line: string, utf16Index: number): number {
  return Array.from(line.slice(0, utf16Index)).length;
}

function lineStartOf(text: string, offset: number): number {
  return text.lastIndexOf("\n", offset - 1) + 1;
}

/** Splits the text between two entries into the previous line's comment and whole lines. */
function readGap(
  yamlText: string,
  gapStart: number,
  gapEnd: number,
  position: "first" | "between" | "last",
): { comment: TrailingComment | undefined; lines: string[] } {
  const pieces = yamlText.slice(gapStart, gapEnd).split("\n");
  const restOfLine = pieces.shift() ?? "";
  let comment: TrailingComment | undefined;
  const hashIndex = restOfLine.indexOf("#");
  if (position !== "first" && hashIndex !== -1 && restOfLine.slice(0, hashIndex).trim() === "") {
    const lineStart = lineStartOf(yamlText, gapStart);
    const column = codePointColumn(
      yamlText.slice(lineStart, gapStart + hashIndex),
      gapStart + hashIndex - lineStart,
    );
    comment = { text: restOfLine.slice(hashIndex).trimEnd(), column };
  }
  if (position !== "last") pieces.pop(); // the indentation in front of the next key
  return { comment, lines: pieces.map((line) => line.trim()) };
}

/** Reads the YAML between the frontmatter fences into an ordered mapping. */
export function parseFrontmatterSource(yamlText: string, path: string): FrontmatterSource {
  const document = parseDocument(yamlText, { uniqueKeys: true });
  const [firstError] = document.errors;
  if (firstError !== undefined) {
    throw new FrontmatterError(
      `YAML parse error in frontmatter of ${path}: ${firstError.message}`,
    );
  }
  const mapping = document.contents;
  if (!isMap(mapping)) return new FrontmatterSource([], []);

  const entries: SourceEntry[] = [];
  let previousEnd = 0;
  let pendingComment: TrailingComment | undefined;
  mapping.items.forEach((pair, index) => {
    const keyStart = isScalar(pair.key) && pair.key.range ? pair.key.range[0] : previousEnd;
    const gap = readGap(yamlText, previousEnd, keyStart, index === 0 ? "first" : "between");
    if (index > 0) attachComment(entries, pendingComment ?? gap.comment);
    pendingComment = undefined;
    entries.push({
      key: String(isScalar(pair.key) ? pair.key.value : pair.key),
      before: gap.lines,
      value: describeSourceValue(pair, yamlText),
      comment: undefined,
    });
    previousEnd = pair.value?.range ? pair.value.range[1] : keyStart;
  });
  const tail = readGap(yamlText, previousEnd, yamlText.length, "last");
  attachComment(entries, tail.comment);
  const after = trimTrailingBlank(tail.lines);
  return new FrontmatterSource(entries, after);
}

function attachComment(entries: SourceEntry[], comment: TrailingComment | undefined): void {
  const last = entries.pop();
  if (last !== undefined) entries.push({ ...last, comment });
}

function trimTrailingBlank(lines: string[]): string[] {
  const kept = [...lines];
  while (kept.length > 0 && kept[kept.length - 1] === "") kept.pop();
  return kept;
}

export type FieldValues = readonly (readonly [string, string | undefined])[];

function renderEntry(entry: SourceEntry, value: SourceValue): string {
  const lines = entry.before.map((line) => `${line}\n`).join("");
  if (value.kind === "string") {
    return lines + emitScalarEntry(entry.key, value.value, entry.comment);
  }
  if (value.kind === "literal") {
    const comment = entry.comment === undefined ? "" : `  ${entry.comment.text}`;
    const separator = value.text === "" ? ":" : `: ${value.text}`;
    return `${lines}${entry.key}${separator}${comment}\n`;
  }
  return `${lines}${value.text}\n`;
}

/**
 * Renders the YAML between the fences. Known fields take their key order, in-place updates and
 * comments from `source` when there is one; a field left undefined is omitted.
 */
export function renderFrontmatterYaml(
  fields: FieldValues,
  source: FrontmatterSource | undefined,
): string {
  const known = new Map(fields);
  const entries = source?.entries ?? [];
  const parts: string[] = [];
  const written = new Set<string>();
  for (const entry of entries) {
    if (!known.has(entry.key)) {
      parts.push(renderEntry(entry, entry.value));
      continue;
    }
    const value = known.get(entry.key);
    written.add(entry.key);
    if (value !== undefined) parts.push(renderEntry(entry, { kind: "string", value }));
  }
  for (const [key, value] of fields) {
    if (value === undefined || written.has(key)) continue;
    parts.push(emitScalarEntry(key, value, undefined));
  }
  if (parts.length === 0) return "{}\n";
  const trailing = (source?.after ?? []).map((line) => `${line}\n`);
  return parts.join("") + trailing.join("");
}
