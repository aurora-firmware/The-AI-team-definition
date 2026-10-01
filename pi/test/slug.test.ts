import { readdirSync, readFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { slugify } from "../src/core/slug.js";

const fixturesRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "fixtures", "parity");

interface TreeEntry {
  readonly path: string;
  readonly type: string;
}

function readTree(caseName: string, side: "before" | "after"): TreeEntry[] {
  return JSON.parse(readFileSync(join(fixturesRoot, caseName, `${side}.json`), "utf-8"));
}

interface CreationCase {
  readonly name: string;
  readonly title: string;
  readonly filename: string;
}

/** Every `* new` case that creates one file from a title: the title and the file it produced. */
function creationCases(): CreationCase[] {
  return readdirSync(fixturesRoot)
    .filter((name) => name.includes("-new--"))
    .flatMap((name) => {
      const spec = JSON.parse(readFileSync(join(fixturesRoot, name, "case.json"), "utf-8"));
      const title: unknown = spec.input?.title;
      if (typeof title !== "string") return [];
      const before = new Set(readTree(name, "before").map((entry) => entry.path));
      const created = readTree(name, "after").filter(
        (entry) => entry.type === "file" && !before.has(entry.path) && entry.path.endsWith(".md"),
      );
      const [only] = created;
      if (created.length !== 1 || only === undefined) return [];
      return [{ name, title, filename: basename(only.path) }];
    });
}

describe("slugify against the creation fixtures", () => {
  const cases = creationCases();

  it("finds creation fixtures to check", () => {
    expect(cases.length).toBeGreaterThan(30);
  });

  it.each(cases.map((c) => [c.name, c] as const))("%s: slug matches the fixture filename", (_name, c) => {
    expect(c.filename).toMatch(new RegExp(`^[A-Z]+-\\d+-${slugify(c.title)}\\.md$`));
  });
});

describe("slugify", () => {
  it("lowercases and joins words with hyphens", () => {
    expect(slugify("Plain Decision")).toBe("plain-decision");
  });

  it("transliterates accented, CJK and symbol characters", () => {
    expect(slugify("Ünïcödé — 日本語 títle: “quotes” & emoji 🚀")).toBe(
      "unicode-ri-ben-yu-title-quotes-emoji",
    );
  });

  it("treats an apostrophe as a word separator, as python-slugify does", () => {
    expect(slugify("don't stop")).toBe("don-t-stop");
  });

  it("removes thousands separators between digits", () => {
    expect(slugify("Handle 1,000 rows, ok")).toBe("handle-1000-rows-ok");
  });

  it("decodes html entities and numeric character references", () => {
    expect(slugify("Tom &amp; Jerry &#65; &#x42;")).toBe("tom-jerry-a-b");
  });

  it("keeps the accent of a decoded named entity as a separator", () => {
    expect(slugify("caf&eacute;x &eacute;")).toBe("cafe-x-e");
  });

  it("leaves an out-of-range numeric reference undecoded", () => {
    expect(slugify("a &#99999999999; b")).toBe("a-99999999999-b");
  });

  it("leaves an unknown entity name as words", () => {
    expect(slugify("&bogus; x")).toBe("bogus-x");
  });

  it("collapses repeated separators and trims them", () => {
    expect(slugify("  --a___b--  ")).toBe("a-b");
  });

  it("returns an empty string when nothing slug-worthy remains", () => {
    expect(slugify("🚀 !!!")).toBe("");
  });
});
