import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const readme = readFileSync(
  join(dirname(fileURLToPath(import.meta.url)), "..", "README.md"),
  "utf8",
);

describe("pi package README", () => {
  it("documents the scratch PI_CODING_AGENT_DIR for manual smoke tests", () => {
    expect(readme).toContain("PI_CODING_AGENT_DIR");
  });

  it("documents the one-time sync prerequisite", () => {
    expect(readme).toContain("python scripts/sync_init_scaffolds.py");
  });

  it("states that mixed concurrent allocation is unsupported", () => {
    expect(readme).toMatch(/mixed concurrent[^.]*unsupported/i);
  });

  it.each(["AI_TEAM_TODAY", "AI_TEAM_FRAMEWORK_VERSION"])(
    "documents the %s override",
    (name) => {
      expect(readme).toContain(name);
    },
  );
});
