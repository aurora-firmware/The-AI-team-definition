import { realpathSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { checkLayout } from "../layout.js";
import { ROOT_ENV_VAR } from "../locator.js";
import { success } from "../result.js";
import type { CheckLayoutHandler } from "./handler.js";

/** Absolute path with symlinks resolved when the path exists, like Python's `Path.resolve()`. */
function resolvePath(path: string): string {
  const absolute = resolve(path);
  try {
    return realpathSync(absolute);
  } catch {
    return absolute;
  }
}

function exists(path: string): boolean {
  try {
    statSync(path);
    return true;
  } catch {
    return false;
  }
}

function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

/**
 * AI_TEAM_ROOT when set, else the nearest directory at or above the start directory holding
 * `.ai-team.toml` or `project/`, else the start directory itself. It never fails: a missing
 * root is reported as layout findings instead.
 */
function repositoryRoot(startDirectory: string): string {
  const configuredRoot = process.env[ROOT_ENV_VAR];
  if (configuredRoot) return resolvePath(configuredRoot);

  const start = resolvePath(startDirectory);
  for (let candidate = start; ; candidate = dirname(candidate)) {
    if (exists(join(candidate, ".ai-team.toml")) || isDirectory(join(candidate, "project"))) {
      return candidate;
    }
    if (dirname(candidate) === candidate) return start;
  }
}

/** Runs every layout check read-only; status is 1 when any finding exists. */
export const checkRepositoryLayout: CheckLayoutHandler = (startDirectory) => {
  const findings = checkLayout(repositoryRoot(startDirectory), { env: process.env });
  const payload = {
    findings: findings.map((item) => ({
      level: item.level,
      path: item.path,
      message: item.problem,
      suggested_fix: item.suggestedFix,
    })),
  };
  return findings.length === 0 ? success(payload) : { status: 1, payload };
};
