import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { COMMANDS, isStub } from "../src/core/commands/registry.js";

const PI_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

function toolContractCommands(): string[] {
  const map = JSON.parse(readFileSync(join(PI_ROOT, "resources", "command-map.json"), "utf8"));
  return map.commands.map((entry: { command: string }) => entry.command);
}

describe("command registry", () => {
  it("maps every tool-contract command to exactly one handler", () => {
    expect(Object.keys(COMMANDS).sort()).toEqual(toolContractCommands().sort());
    for (const entry of Object.values(COMMANDS)) {
      expect(typeof entry.handler).toBe("function");
    }
  });

  it("uses a distinct handler for each command", () => {
    const handlers = Object.values(COMMANDS).map((entry) => entry.handler);
    expect(new Set(handlers).size).toBe(handlers.length);
  });

  it("gives init and check-layout a start-directory handler and every other command a located-root handler", () => {
    for (const [command, entry] of Object.entries(COMMANDS)) {
      const expected =
        command === "init" ? "init" : command === "check-layout" ? "check-layout" : "root";
      expect(entry.kind, command).toBe(expected);
    }
  });

  it("reports stub handlers as not implemented when they are called", () => {
    const entry = COMMANDS["spec new"];
    expect(entry).toBeDefined();
    expect(isStub(entry!.handler)).toBe(true);
    expect(() => (entry!.handler as (a: unknown, b: unknown) => unknown)("x", {})).toThrow(
      /spec new.*not implemented/i,
    );
  });
});
