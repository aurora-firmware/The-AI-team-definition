import { describe, expect, it } from "vitest";
import {
  FrontmatterError,
  parseFrontmatterSource,
  renderFrontmatterYaml,
  splitFrontmatter,
} from "../src/core/frontmatter.js";
import { emitScalarEntry } from "../src/core/scalar-emitter.js";
import { parseTaskText, dumpFrontmatter } from "../src/core/models.js";

// Expected strings below were produced by the Python CLI's ruamel.yaml round-trip dump
// (typ="rt", width 80) and are pinned here; they are never regenerated from this port.
const SCALAR_GOLDENS: ReadonlyArray<readonly [string, string, string]> = [
  ["an empty string is single-quoted", "", "k: ''\n"],
  ["a boolean-looking word is quoted", "true", "k: 'true'\n"],
  ["a YAML 1.2 non-boolean such as yes stays plain", "yes", "k: yes\n"],
  ["an ISO date is quoted so it reloads as text", "2026-05-10", "k: '2026-05-10'\n"],
  ["a number-looking value is quoted", "1.5", "k: '1.5'\n"],
  ["a lone underscore stays plain because the resolver is not triggered by it", "_", "k: _\n"],
  ["a colon followed by a space forces single quotes", "x: y", "k: 'x: y'\n"],
  ["a space-hash starts a comment so it is quoted", "a #b", "k: 'a #b'\n"],
  ["a leading space forces single quotes", " lead", "k: ' lead'\n"],
  ["an apostrophe inside plain-safe text stays plain", "a'b", "k: a'b\n"],
  ["an apostrophe in text that needs quoting forces double quotes", "it's: \"x\"", "k: \"it's: \\\"x\\\"\"\n"],
  ["a newline forces double quotes with an escape", "a\nb", "k: \"a\\nb\"\n"],
  ["a tab is escaped in double quotes", "abc\tdef", "k: \"abc\\tdef\"\n"],
  ["a null character is escaped", "\u0000", "k: \"\\0\"\n"],
  ["a nonbreaking space is escaped", "a\u00a0b", "k: a\u00a0b\n"],
  ["non-ASCII text stays plain", "\u00dcn\u00efc\u00f6d\u00e9 \u2014 \u65e5\u672c\u8a9e \ud83d\ude80", "k: \u00dcn\u00efc\u00f6d\u00e9 \u2014 \u65e5\u672c\u8a9e \ud83d\ude80\n"],
  ["a unicode line separator is single-quoted with a folded continuation", "\u2028x", "k: '\u2028  x'\n"],
  ["a single long word moves to its own line", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "k: \n  aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"],
  ["plain text folds at the first space past column 80", "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum dolor", "k: lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem\n  ipsum lorem ipsum lorem ipsum lorem ipsum dolor\n"],
  ["single-quoted text folds past column 80", "Fix: word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word ", "k: 'Fix: word word word word word word word word word word word word word word word\n  word word word word word word word word word word word word word word word '\n"],
  ["double-quoted text folds with continuation backslashes", "it's: word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word \n", "k: \"it's: word word word word word word word word word word word word word word word\n  word word word word word word word word word word word word word word word \\n\"\n"],
  ["double-quoted text with a long unbroken run", "tab\txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx y z", "k: \"tab\\txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n  y z\"\n"],
  ["a value exactly at the width limit", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "k: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"],
  ["a value one past the width limit", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", "k: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \n  yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy\n"],
];

const DOCUMENT_GOLDENS: ReadonlyArray<readonly [string, string, string, string]> = [
  ["keeps unknown scalar keys, writing numbers, booleans, dates and null back as they were", "---\nid: \"T-001\"\ntitle: \"Add: thing\"\nstatus: pending\npriority: medium\nassigned-role: dev\ncreated: 2026-05-10\nx: 1.0\ny: true\nz: 2026-01-01\nw: ~\nv: 0x1F\n---\n\nbody\n", "done-now", "---\nid: T-001\ntitle: 'Add: thing'\nstatus: done-now\npriority: medium\nassigned-role: dev\ncreated: '2026-05-10'\nx: 1.0\ny: true\nz: 2026-01-01\nw:\nv: 0x1F\n---\n\nb\n"],
  ["re-renders an unknown sequence and mapping with unindented sequences", "---\nid: \"T-001\"\ntitle: \"Add: thing\"\nstatus: pending\npriority: medium\nassigned-role: dev\ncreated: 2026-05-10\ntags:\n  - a\n  - b\nnested:\n  k: v\n---\n\nbody\n", "done-now", "---\nid: T-001\ntitle: 'Add: thing'\nstatus: done-now\npriority: medium\nassigned-role: dev\ncreated: '2026-05-10'\ntags:\n- a\n- b\nnested:\n  k: v\n---\n\nb\n"],
  ["keeps comments, blank lines and the comment column across an update", "---\n# leading comment\nid: \"T-001\"   # the id\ntitle: \"Add: thing\"\n\nstatus: pending  # pending | in-progress | completed | blocked\npriority: medium  # critical | high\n\n# own line comment\nassigned-role: \"[agent role or unassigned]\"\ncreated: 2026-05-10 # c\nextra: 5\n---\n\nbody\n", "done-now", "---\n# leading comment\nid: T-001     # the id\ntitle: 'Add: thing'\n\nstatus: done-now # pending | in-progress | completed | blocked\npriority: medium  # critical | high\n\n# own line comment\nassigned-role: '[agent role or unassigned]'\ncreated: '2026-05-10' # c\nextra: 5\n---\n\nb\n"],
  ["puts a trailing comment one space after a value that outgrew its column", "---\nid: T-001\ntitle: x\nstatus: pending  # a very long trailing comment here\npriority: medium\nassigned-role: dev\ncreated: 2026-05-10\n---\nb\n", "a-much-longer-status-value-that-pushes-past-the-comment-column-for-sure-ok", "---\nid: T-001\ntitle: x\nstatus: \n  a-much-longer-status-value-that-pushes-past-the-comment-column-for-sure-ok # a very long trailing comment here\npriority: medium\nassigned-role: dev\ncreated: '2026-05-10'\n---\n\nb\n"],
  ["keeps comment lines that follow the last key", "---\nid: \"T-001\"\ntitle: \"Add: thing\"\nstatus: pending\npriority: medium\nassigned-role: dev\ncreated: 2026-05-10\n\n# trailing\n\n---\n\nbody\n", "done-now", "---\nid: T-001\ntitle: 'Add: thing'\nstatus: done-now\npriority: medium\nassigned-role: dev\ncreated: '2026-05-10'\n\n# trailing\n---\n\nb\n"],
];

describe("scalar emission matches the Python dump", () => {
  it.each(SCALAR_GOLDENS)("%s", (_name, value, expected) => {
    expect(emitScalarEntry("k", value, undefined)).toBe(expected);
  });

  it("folds a long title at the same width as Python (first space past column 80)", () => {
    const title =
      "A deliberately long title that keeps going well past the usual line width so that the YAML emitter has to decide whether to fold it across several lines: alpha beta gamma delta epsilon";
    expect(emitScalarEntry("title", title, undefined)).toBe(
      "title: 'A deliberately long title that keeps going well past the usual line width\n" +
        "  so that the YAML emitter has to decide whether to fold it across several lines:\n" +
        "  alpha beta gamma delta epsilon'\n",
    );
  });

  it("rejects a key that would need an explicit YAML key", () => {
    expect(() => emitScalarEntry("two\nlines", "v", undefined)).toThrow(RangeError);
  });
});

describe("in-place rewrite matches the Python dump", () => {
  it.each(DOCUMENT_GOLDENS)("%s", (_name, text, status, expected) => {
    const task = parseTaskText(text, "t.md");
    task.status = status;
    expect(dumpFrontmatter(task, "b\n")).toBe(expected);
  });

  it("drops an optional key that was cleared and appends a newly set one", () => {
    const text =
      "---\nid: T-001\ntitle: x\nstatus: pending\npriority: low\nassigned-role: dev\ncreated: '2026-01-01'\nspec: S-1\n---\n\nb\n";
    const task = parseTaskText(text, "t.md");
    task.spec = undefined;
    expect(dumpFrontmatter(task, "b\n")).not.toContain("spec");
    task.spec = "S-2";
    expect(dumpFrontmatter(task, "b\n")).toContain("created: '2026-01-01'\nspec: S-2\n---");
  });

  it("renders an empty mapping as {}", () => {
    expect(renderFrontmatterYaml([["a", undefined]], undefined)).toBe("{}\n");
  });
});

describe("splitFrontmatter and parse errors carry the Python messages", () => {
  it("names the path when there is no opening fence", () => {
    expect(() => splitFrontmatter("# no fence", "/x/t.md")).toThrow(
      new FrontmatterError("No YAML frontmatter block found in /x/t.md"),
    );
  });

  it("names the path when the closing fence is missing", () => {
    expect(() => splitFrontmatter("---\nid: T-1\n", "/x/t.md")).toThrow(
      new FrontmatterError("Unclosed YAML frontmatter block (missing closing ---) in /x/t.md"),
    );
  });

  it("consumes the single blank line between the closing fence and the body", () => {
    expect(splitFrontmatter("---\na: 1\n---\n\nbody\n", "p").body).toBe("body\n");
  });

  it("reports malformed YAML with the Python message prefix", () => {
    expect(() => parseFrontmatterSource("a: [unclosed", "/x/t.md")).toThrow(
      /^YAML parse error in frontmatter of \/x\/t\.md: /,
    );
  });

  it("reports duplicate keys as a YAML parse error, as ruamel does", () => {
    expect(() => parseFrontmatterSource("a: 1\na: 2", "/x/t.md")).toThrow(FrontmatterError);
  });
});
