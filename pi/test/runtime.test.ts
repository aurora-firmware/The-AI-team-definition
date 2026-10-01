import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { AiTeamError } from "../src/core/result.js";
import {
  FRAMEWORK_VERSION_ENV_VAR,
  TODAY_ENV_VAR,
  frameworkVersion,
  today,
} from "../src/core/runtime.js";

const scratchDirs: string[] = [];

function scratchVersionFile(content?: string): string {
  const dir = mkdtempSync(join(tmpdir(), "ai-team-runtime-"));
  scratchDirs.push(dir);
  const path = join(dir, "version.txt");
  if (content !== undefined) writeFileSync(path, content);
  return path;
}

afterEach(() => {
  for (const dir of scratchDirs.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe("override names", () => {
  it("match the Python CLI", () => {
    expect(TODAY_ENV_VAR).toBe("AI_TEAM_TODAY");
    expect(FRAMEWORK_VERSION_ENV_VAR).toBe("AI_TEAM_FRAMEWORK_VERSION");
  });
});

describe("today", () => {
  it("returns the override when AI_TEAM_TODAY is an ISO date", () => {
    expect(today({ AI_TEAM_TODAY: "2026-02-03" })).toBe("2026-02-03");
  });

  it("returns the local date as YYYY-MM-DD when no override is set", () => {
    expect(today({}, new Date(2026, 0, 5, 23, 59))).toBe("2026-01-05");
  });

  it("rejects an override that is not an ISO date", () => {
    expect(() => today({ AI_TEAM_TODAY: "tomorrow" })).toThrow(/AI_TEAM_TODAY.*YYYY-MM-DD.*tomorrow/);
  });

  it("rejects an override that is not a real calendar date", () => {
    expect(() => today({ AI_TEAM_TODAY: "2026-02-31" })).toThrow(AiTeamError);
  });
});

describe("frameworkVersion", () => {
  it("returns the override when AI_TEAM_FRAMEWORK_VERSION is set", () => {
    const missing = scratchVersionFile();
    expect(frameworkVersion({ AI_TEAM_FRAMEWORK_VERSION: "9.9.9" }, missing)).toBe("9.9.9");
  });

  it("reads the generated version file, trimming whitespace", () => {
    expect(frameworkVersion({}, scratchVersionFile("1.2.3\n"))).toBe("1.2.3");
  });

  it("tells the user to run the sync when the version file is missing", () => {
    const missing = scratchVersionFile();
    let caught: unknown;
    try {
      frameworkVersion({}, missing);
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeInstanceOf(AiTeamError);
    const error = caught as AiTeamError;
    expect(error.message).toContain(missing);
    expect(error.hint).toMatch(/sync_init_scaffolds\.py/);
  });

  it("rethrows a non-ENOENT read failure instead of hinting to run the sync", () => {
    const directoryInPlaceOfFile = dirname(scratchVersionFile());
    let caught: unknown;
    try {
      frameworkVersion({}, directoryInPlaceOfFile);
    } catch (error) {
      caught = error;
    }
    expect(caught).not.toBeInstanceOf(AiTeamError);
    expect(caught).toMatchObject({ code: "EISDIR" });
  });

  it("reads the real generated version file by default", () => {
    expect(frameworkVersion({})).not.toBe("");
  });
});
