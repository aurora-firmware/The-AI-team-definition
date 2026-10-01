import { success } from "../result.js";
import { validateProject } from "../validate.js";
import type { RootHandler } from "./handler.js";

const SCOPE_FLAGS = ["tasks", "bugs", "specs", "adrs", "changeRequests"] as const;

/** Validates the selected artifact scopes; every scope is validated when `all` is set or no scope flag is. */
export const validateArtifacts: RootHandler = (root, input) => {
  const anySelected = SCOPE_FLAGS.some((flag) => input[flag] === true);
  const everything = input["all"] === true || !anySelected;
  const selected = (flag: (typeof SCOPE_FLAGS)[number]): boolean =>
    everything || input[flag] === true;

  const findings = validateProject(root, {
    tasks: selected("tasks"),
    bugs: selected("bugs"),
    specs: selected("specs"),
    adrs: selected("adrs"),
    changeRequests: selected("changeRequests"),
  });
  const hasError = findings.some((finding) => finding.level === "error");
  // The tool contract returns the findings list itself as the payload, as the CLI's --json does.
  const result = success(findings as unknown as Record<string, unknown>);
  return hasError ? { ...result, status: 1 } : result;
};
