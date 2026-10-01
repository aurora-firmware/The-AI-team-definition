/**
 * Block-mapping entry emitter, a port of the parts of ruamel.yaml's round-trip
 * emitter that the Python CLI uses to write frontmatter (ruamel.yaml 0.19, width 80,
 * indent 2, Unicode allowed). Column arithmetic counts code points, as Python does.
 *
 * Only what frontmatter needs is ported: one `key: scalar` entry, with an optional
 * trailing comment. Porting the emitter rather than relying on a generic YAML library
 * is what keeps quoting choices and line folding byte-identical to the Python output.
 */

const BEST_WIDTH = 80;
const SCALAR_INDENT = 2;
const MAX_SIMPLE_KEY_LENGTH = 128;
const LINE_BREAKS = "\n\x85  ";
const WHITESPACE = "\0 \t\r\n\x85  ";
const LEADING_INDICATORS = "#,[]{}&*!|>'\"%@`";

const NULL_PATTERN = /^(?:~|null|Null|NULL)$/;
const BOOL_PATTERN = /^(?:true|True|TRUE|false|False|FALSE)$/;
const FLOAT_PATTERN =
  /^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+]?[0-9]+)?|[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)|[-+]?\.[0-9_]+(?:[eE][-+][0-9]+)?|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$/;
const INT_PATTERN = /^(?:[-+]?0b[0-1_]+|[-+]?0o?[0-7_]+|[-+]?[0-9_]+|[-+]?0x[0-9a-fA-F_]+)$/;
const TIMESTAMP_PATTERN =
  /^(?:[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}-[0-9][0-9]?-[0-9][0-9]?(?:[Tt]|[ \t]+)[0-9][0-9]?:[0-9]{2}:[0-9]{2}(?:\.[0-9]*)?(?:[ \t]*(?:Z|[-+][0-9][0-9]?(?::[0-9][0-9])?))?)$/;

/**
 * Whether ruamel's implicit resolver would read the plain text as something other than
 * a string. Such strings must be quoted to survive a reload. The resolver only tries a
 * pattern when the first character is one of its trigger characters, so `_` stays plain.
 */
export function resolvesToNonString(value: string): boolean {
  if (value === "") return true;
  const first = value.charAt(0);
  if ("~nN".includes(first)) return NULL_PATTERN.test(value);
  if ("fFtT".includes(first)) return BOOL_PATTERN.test(value);
  if (first === "+" || first === "-") return FLOAT_PATTERN.test(value) || INT_PATTERN.test(value);
  if (first === ".") return FLOAT_PATTERN.test(value);
  if (first >= "0" && first <= "9") {
    return FLOAT_PATTERN.test(value) || INT_PATTERN.test(value) || TIMESTAMP_PATTERN.test(value);
  }
  if (first === "<") return value === "<<";
  if (first === "=") return value === "=";
  if ("!&*".includes(first)) return value.length === 1;
  return false;
}

interface ScalarAnalysis {
  readonly empty: boolean;
  readonly multiline: boolean;
  readonly allowBlockPlain: boolean;
  readonly allowSingleQuoted: boolean;
}

function inRange(char: string, low: string, high: string): boolean {
  return char >= low && char <= high;
}

function isSpecialCharacter(char: string): boolean {
  if (char === "\n" || inRange(char, " ", "~")) return false;
  const printableUnicode =
    char === "\x85" ||
    inRange(char, "\xA0", "퟿") ||
    inRange(char, "", "�") ||
    inRange(char, "\u{10000}", "\u{10FFFF}");
  return !printableUnicode || char === "﻿";
}

function analyzeScalar(chars: readonly string[]): ScalarAnalysis {
  if (chars.length === 0) {
    return { empty: true, multiline: false, allowBlockPlain: true, allowSingleQuoted: true };
  }
  const text = chars.join("");
  let blockIndicators = text.startsWith("---") || text.startsWith("...");
  let lineBreaks = false;
  let specialCharacters = false;
  let leadingSpace = false;
  let leadingBreak = false;
  let trailingSpace = false;
  let trailingBreak = false;
  let breakSpace = false;
  let spaceBreak = false;
  let previousSpace = false;
  let previousBreak = false;
  let precededByWhitespace = true;
  let followedByWhitespace = chars.length === 1 || WHITESPACE.includes(chars[1] ?? "");
  const last = chars.length - 1;

  chars.forEach((char, index) => {
    if (index === 0) {
      if (LEADING_INDICATORS.includes(char)) blockIndicators = true;
      if ((char === "?" || char === ":") && followedByWhitespace) blockIndicators = true;
      if (char === "-" && followedByWhitespace) blockIndicators = true;
    } else {
      if (char === ":" && followedByWhitespace) blockIndicators = true;
      if (char === "#" && precededByWhitespace) blockIndicators = true;
    }
    if (LINE_BREAKS.includes(char)) lineBreaks = true;
    if (isSpecialCharacter(char)) specialCharacters = true;

    if (char === " ") {
      if (index === 0) leadingSpace = true;
      if (index === last) trailingSpace = true;
      if (previousBreak) breakSpace = true;
      previousSpace = true;
      previousBreak = false;
    } else if (LINE_BREAKS.includes(char)) {
      if (index === 0) leadingBreak = true;
      if (index === last) trailingBreak = true;
      if (previousSpace) spaceBreak = true;
      previousSpace = false;
      previousBreak = true;
    } else {
      previousSpace = false;
      previousBreak = false;
    }
    precededByWhitespace = WHITESPACE.includes(char);
    followedByWhitespace = index + 2 >= chars.length || WHITESPACE.includes(chars[index + 2] ?? "");
  });

  let allowPlain = true;
  let allowSingleQuoted = true;
  if (leadingSpace || leadingBreak || trailingSpace || trailingBreak) allowPlain = false;
  if (breakSpace || specialCharacters || spaceBreak) {
    allowPlain = false;
    allowSingleQuoted = false;
  }
  if (lineBreaks || blockIndicators) allowPlain = false;
  return { empty: false, multiline: lineBreaks, allowBlockPlain: allowPlain, allowSingleQuoted };
}

type ScalarStyle = "plain" | "single" | "double";

function chooseStyle(value: string, analysis: ScalarAnalysis, isKey: boolean): ScalarStyle {
  const plainAllowed =
    !resolvesToNonString(value) &&
    !(isKey && (analysis.empty || analysis.multiline)) &&
    analysis.allowBlockPlain;
  if (plainAllowed) return "plain";
  if (value.includes("'") || value.includes("\n")) return "double";
  if (analysis.allowSingleQuoted && !(isKey && analysis.multiline)) return "single";
  return "double";
}

const ESCAPE_REPLACEMENTS: Readonly<Record<string, string>> = {
  "\0": "0",
  "\x07": "a",
  "\b": "b",
  "\t": "t",
  "\n": "n",
  "\v": "v",
  "\f": "f",
  "\r": "r",
  "\x1B": "e",
  '"': '"',
  "\\": "\\",
  "\x85": "N",
  "\xA0": "_",
  " ": "L",
  " ": "P",
};

function escapeForDoubleQuotes(char: string): string {
  const named = ESCAPE_REPLACEMENTS[char];
  if (named !== undefined) return `\\${named}`;
  const code = char.codePointAt(0) ?? 0;
  if (code <= 0xff) return `\\x${code.toString(16).toUpperCase().padStart(2, "0")}`;
  if (code <= 0xffff) return `\\u${code.toString(16).toUpperCase().padStart(4, "0")}`;
  return `\\U${code.toString(16).toUpperCase().padStart(8, "0")}`;
}

function needsDoubleQuoteEscape(char: string): boolean {
  if ('"\\\x85  ﻿'.includes(char)) return true;
  const printable =
    inRange(char, " ", "~") ||
    inRange(char, "\xA0", "퟿") ||
    inRange(char, "", "�") ||
    inRange(char, "\u{10000}", "\u{10FFFF}");
  return !printable;
}

/** Output buffer plus the emitter state ruamel tracks between writes. */
class EntryWriter {
  text = "";
  column = 0;
  private whitespace = true;
  private indention = true;
  private readonly indent = SCALAR_INDENT;

  private put(data: string, width = Array.from(data).length): void {
    this.text += data;
    this.column += width;
  }

  private lineBreak(): void {
    this.text += "\n";
    this.whitespace = true;
    this.indention = true;
    this.column = 0;
  }

  private writeIndent(): void {
    if (
      !this.indention ||
      this.column > this.indent ||
      (this.column === this.indent && !this.whitespace)
    ) {
      this.lineBreak();
    }
    if (this.column < this.indent) {
      this.whitespace = true;
      this.put(" ".repeat(this.indent - this.column));
    }
  }

  private indicator(indicator: string, needWhitespace: boolean): void {
    const data = this.whitespace || !needWhitespace ? indicator : ` ${indicator}`;
    this.whitespace = false;
    this.indention = false;
    this.put(data);
  }

  writeScalar(value: string, isKey: boolean): void {
    const chars = Array.from(value);
    const style = chooseStyle(value, analyzeScalar(chars), isKey);
    const split = !isKey;
    if (style === "double") this.writeDoubleQuoted(chars, split);
    else if (style === "single") this.writeSingleQuoted(chars, split);
    else this.writePlain(chars, split);
  }

  writeColon(): void {
    this.indicator(":", false);
  }

  /** The comment keeps its source column, or sits one space after the value when that is taken. */
  writeTrailingComment(text: string, sourceColumn: number): void {
    const spaces = Math.max(sourceColumn - this.column, 1);
    this.text += `${" ".repeat(spaces)}${text}`;
    this.lineBreak();
  }

  finishLine(): void {
    if (this.column !== 0) this.lineBreak();
  }

  private writePlain(chars: readonly string[], split: boolean): void {
    if (chars.length === 0) return;
    if (!this.whitespace) this.put(" ");
    this.whitespace = false;
    this.indention = false;
    let spaces = false;
    let breaks = false;
    let start = 0;
    for (let end = 0; end <= chars.length; end += 1) {
      const char = chars[end];
      if (spaces) {
        if (char !== " ") {
          if (start + 1 === end && this.column >= BEST_WIDTH && split) {
            this.writeIndent();
            this.whitespace = false;
            this.indention = false;
          } else {
            this.put(chars.slice(start, end).join(""), end - start);
          }
          start = end;
        }
      } else if (breaks) {
        if (char === undefined || !LINE_BREAKS.includes(char)) {
          this.writeBreaks(chars, start, end);
          this.whitespace = false;
          this.indention = false;
          start = end;
        }
      } else if (char === undefined || " \n\x85  ".includes(char)) {
        const width = end - start;
        if (width + this.column > BEST_WIDTH && this.column > this.indent) this.writeIndent();
        this.put(chars.slice(start, end).join(""), width);
        start = end;
      }
      if (char !== undefined) {
        spaces = char === " ";
        breaks = LINE_BREAKS.includes(char);
      }
    }
  }

  private writeBreaks(chars: readonly string[], start: number, end: number): void {
    if (chars[start] === "\n") this.lineBreak();
    for (const char of chars.slice(start, end)) {
      if (char === "\n") this.lineBreak();
      else this.lineBreakWith(char);
    }
    this.writeIndent();
  }

  private lineBreakWith(data: string): void {
    this.text += data;
    this.whitespace = true;
    this.indention = true;
    this.column = 0;
  }

  private writeSingleQuoted(chars: readonly string[], split: boolean): void {
    this.indicator("'", true);
    let spaces = false;
    let breaks = false;
    let start = 0;
    for (let end = 0; end <= chars.length; end += 1) {
      const char = chars[end];
      if (spaces) {
        if (char !== " ") {
          if (
            start + 1 === end &&
            this.column > BEST_WIDTH &&
            split &&
            start !== 0 &&
            end !== chars.length
          ) {
            this.writeIndent();
          } else {
            this.put(chars.slice(start, end).join(""), end - start);
          }
          start = end;
        }
      } else if (breaks) {
        if (char === undefined || !LINE_BREAKS.includes(char)) {
          this.writeBreaks(chars, start, end);
          start = end;
        }
      } else if (char === undefined || " \n\x85  '".includes(char)) {
        if (start < end) {
          this.put(chars.slice(start, end).join(""), end - start);
          start = end;
        }
      }
      if (char === "'") {
        this.put("''");
        start = end + 1;
      }
      if (char !== undefined) {
        spaces = char === " ";
        breaks = LINE_BREAKS.includes(char);
      }
    }
    this.indicator("'", false);
  }

  private writeDoubleQuoted(chars: readonly string[], split: boolean): void {
    this.indicator('"', true);
    let start = 0;
    for (let end = 0; end <= chars.length; end += 1) {
      const char = chars[end];
      if (char === undefined || needsDoubleQuoteEscape(char)) {
        if (start < end) {
          this.put(chars.slice(start, end).join(""), end - start);
          start = end;
        }
        if (char !== undefined) {
          this.put(escapeForDoubleQuotes(char));
          start = end + 1;
        }
      }
      if (
        end > 0 &&
        end < chars.length - 1 &&
        (char === " " || start >= end) &&
        this.column + (end - start) > BEST_WIDTH &&
        split
      ) {
        const needBackslash = this.needsLineContinuationBackslash(chars, start, end);
        this.put(chars.slice(start, end).join("") + (needBackslash ? "\\" : ""));
        if (start < end) start = end;
        this.writeIndent();
        this.whitespace = false;
        this.indention = false;
        if (chars[start] === " ") {
          if (!needBackslash) start += 1;
          if (needBackslash) this.put("\\");
        }
      }
    }
    this.indicator('"', false);
  }

  /** ruamel omits the continuation backslash only where a plain line fold reads back the same. */
  private needsLineContinuationBackslash(
    chars: readonly string[],
    start: number,
    end: number,
  ): boolean {
    const firstSpace = chars.indexOf(" ", end);
    if (firstSpace === -1) return true;
    const newline = chars.indexOf("\n", end);
    const spacePos = newline !== -1 && newline < firstSpace ? newline : firstSpace;
    const after = chars[spacePos + 1];
    if (after === undefined) return true;
    if (chars[spacePos] === "\n" && after !== " ") return true;
    const between = chars.slice(end, spacePos);
    const hasQuote = between.includes('"') || between.includes("'");
    const doubleSpace = chars[end - 1] === " " && chars[end] === " ";
    return hasQuote || after === " " || after === "\n" || doubleSpace || start === end;
  }
}

export interface TrailingComment {
  /** The comment text, starting at its `#`. */
  readonly text: string;
  /** Zero-based column of the `#` in the source, in code points. */
  readonly column: number;
}

/** One `key: value` block-mapping entry as ruamel writes it, ending with a newline. */
export function emitScalarEntry(
  key: string,
  value: string,
  comment: TrailingComment | undefined,
): string {
  const keyChars = Array.from(key);
  const keyAnalysis = analyzeScalar(keyChars);
  if (keyAnalysis.empty || keyAnalysis.multiline || keyChars.length >= MAX_SIMPLE_KEY_LENGTH) {
    throw new RangeError(
      `Frontmatter key ${JSON.stringify(key)} needs an explicit YAML key and is not supported.`,
    );
  }
  const writer = new EntryWriter();
  writer.writeScalar(key, true);
  writer.writeColon();
  writer.writeScalar(value, false);
  if (comment === undefined) writer.finishLine();
  else writer.writeTrailingComment(comment.text, comment.column);
  return writer.text;
}
