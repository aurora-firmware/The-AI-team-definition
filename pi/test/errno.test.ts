import { describe, expect, it } from "vitest";
import { isErrnoCode } from "../src/core/errno.js";

function errorWithCode(code: string): Error {
  return Object.assign(new Error("failure"), { code });
}

describe("isErrnoCode", () => {
  it("is true for an Error carrying the requested code", () => {
    expect(isErrnoCode(errorWithCode("ENOENT"), "ENOENT")).toBe(true);
  });

  it("is false for an Error carrying a different code", () => {
    expect(isErrnoCode(errorWithCode("EISDIR"), "ENOENT")).toBe(false);
  });

  it("is false for an Error without a code", () => {
    expect(isErrnoCode(new Error("failure"), "ENOENT")).toBe(false);
  });

  it("is false for values that are not Errors", () => {
    expect(isErrnoCode({ code: "ENOENT" }, "ENOENT")).toBe(false);
    expect(isErrnoCode("ENOENT", "ENOENT")).toBe(false);
    expect(isErrnoCode(undefined, "ENOENT")).toBe(false);
  });
});
