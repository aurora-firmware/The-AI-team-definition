import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const packageDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const ORCHESTRATOR_SKILLS = ["dev-loop", "bug-loop", "integrate"];

interface Manifest {
  engines?: { node?: string };
  scripts?: Record<string, string>;
  peerDependencies?: Record<string, string>;
  pi?: { extensions?: string[]; skills?: string[] };
}

const manifest = JSON.parse(
  readFileSync(join(packageDir, "package.json"), "utf8"),
) as Manifest;

function generatedSkillNames(): string[] {
  return readdirSync(join(packageDir, "resources", "skills"), {
    withFileTypes: true,
  })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function manifestSkillNames(): string[] {
  return (manifest.pi?.skills ?? [])
    .map((path) => path.replace(/^\.\/resources\/skills\//, ""))
    .sort();
}

function minimumVersion(range: string): number[] {
  return range
    .replace(/^[^\d]*/, "")
    .split(".")
    .map(Number);
}

function compareVersions(left: number[], right: number[]): number {
  for (let index = 0; index < Math.max(left.length, right.length); index++) {
    const difference = (left[index] ?? 0) - (right[index] ?? 0);
    if (difference !== 0) return difference;
  }
  return 0;
}

describe("pi package manifest", () => {
  it("lists every generated skill except the orchestrators", () => {
    const expected = generatedSkillNames().filter(
      (name) => !ORCHESTRATOR_SKILLS.includes(name),
    );
    expect(expected.length).toBeGreaterThan(0);
    expect(manifestSkillNames()).toEqual(expected);
  });

  it("lists no orchestrator skill", () => {
    for (const name of ORCHESTRATOR_SKILLS) {
      expect(manifestSkillNames()).not.toContain(name);
    }
  });

  it("points every skill entry at an existing skill file", () => {
    for (const path of manifest.pi?.skills ?? []) {
      expect(existsSync(join(packageDir, path, "SKILL.md")), path).toBe(true);
    }
  });

  it("declares the extension entry and that file exists", () => {
    expect(manifest.pi?.extensions).toEqual(["./src/index.ts"]);
    expect(existsSync(join(packageDir, "src", "index.ts"))).toBe(true);
  });

  it("declares a minimum Node version", () => {
    expect(manifest.engines?.node).toMatch(/^>=\d+/);
  });

  it("declares a pi host peer dependency of at least 0.87.1", () => {
    const range = manifest.peerDependencies?.["@earendil-works/pi-coding-agent"];
    expect(range).toBeDefined();
    const comparison = compareVersions(minimumVersion(range ?? ""), [0, 87, 1]);
    expect(comparison).toBeGreaterThanOrEqual(0);
    expect(range).toMatch(/^>=/);
  });

  it("names the scripts exactly typecheck and test", () => {
    expect(manifest.scripts?.typecheck).toBe("tsc --noEmit");
    expect(manifest.scripts?.test).toBe("vitest run");
  });
});
