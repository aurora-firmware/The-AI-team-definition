import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const PI_SPECIFIER = /^@(earendil-works|mariozechner)\/pi-/;
const MODULE_SPECIFIER =
  /(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\s*\(\s*)["']([^"']+)["']/g;

const coreDir = join(dirname(fileURLToPath(import.meta.url)), "..", "src", "core");

function listTypeScriptFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) return listTypeScriptFiles(path);
    return entry.name.endsWith(".ts") ? [path] : [];
  });
}

function findPiImports(source: string): string[] {
  return [...source.matchAll(MODULE_SPECIFIER)]
    .map((match) => match[1] ?? "")
    .filter((specifier) => PI_SPECIFIER.test(specifier));
}

describe("pi API import boundary", () => {
  it("detects static, dynamic and require pi imports", () => {
    const source = [
      `import { a } from "@earendil-works/pi-coding-agent";`,
      `const b = await import("@earendil-works/pi-ai");`,
      `const c = require("@mariozechner/pi-tui");`,
      `import { d } from "yaml";`,
    ].join("\n");
    expect(findPiImports(source)).toEqual([
      "@earendil-works/pi-coding-agent",
      "@earendil-works/pi-ai",
      "@mariozechner/pi-tui",
    ]);
  });

  it("finds no pi import under src/core", () => {
    let files: string[];
    try {
      files = listTypeScriptFiles(coreDir);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === "ENOENT") return;
      throw error;
    }
    const offenders = files.filter(
      (file) => findPiImports(readFileSync(file, "utf8")).length > 0,
    );
    expect(offenders).toEqual([]);
  });
});

describe("working-directory boundary", () => {
  it("finds no process.cwd call under src/core", () => {
    const offenders = listTypeScriptFiles(coreDir).filter((file) =>
      /\bprocess\s*\.\s*cwd\b/.test(readFileSync(file, "utf8")),
    );
    expect(offenders).toEqual([]);
  });

  it("detects process.cwd however it is spelled", () => {
    expect(/\bprocess\s*\.\s*cwd\b/.test("const d = process.cwd();")).toBe(true);
    expect(/\bprocess\s*\.\s*cwd\b/.test("const d = process\n  .cwd;")).toBe(true);
    expect(/\bprocess\s*\.\s*cwd\b/.test("const d = startDirectory;")).toBe(false);
  });
});
