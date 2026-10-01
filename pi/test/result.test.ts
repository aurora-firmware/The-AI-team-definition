import { describe, expect, it } from "vitest";
import { AiTeamError, failure, resultText, success } from "../src/core/result.js";

describe("result", () => {
  it("builds a success with status 0 and the payload", () => {
    expect(success({ id: "T-001" })).toEqual({ status: 0, payload: { id: "T-001" } });
  });

  it("keeps message and hint separate on a failure", () => {
    const result = failure("No project found.", "Run init first.");
    expect(result.status).toBe(1);
    expect(result.message).toBe("No project found.");
    expect(result.hint).toBe("Run init first.");
  });

  it("joins message and hint with a space for CLI text", () => {
    expect(resultText(failure("No project found.", "Run init first."))).toBe(
      "No project found. Run init first.",
    );
  });

  it("omits a missing hint from the text", () => {
    expect(resultText(failure("No project found."))).toBe("No project found.");
  });

  it("returns empty text for a success", () => {
    expect(resultText(success({}))).toBe("");
  });

  it("carries a separate hint on AiTeamError", () => {
    const error = new AiTeamError("boom", "try again");
    expect(error).toBeInstanceOf(Error);
    expect(error.message).toBe("boom");
    expect(error.hint).toBe("try again");
  });

  it("defaults AiTeamError hint to undefined", () => {
    expect(new AiTeamError("boom").hint).toBeUndefined();
  });
});
