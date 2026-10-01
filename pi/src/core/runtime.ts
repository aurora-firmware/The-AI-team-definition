import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { isErrnoCode } from "./errno.js";
import { AiTeamError } from "./result.js";

/** Override names shared with the Python CLI (`ai_team.core.runtime`). */
export const TODAY_ENV_VAR = "AI_TEAM_TODAY";
export const FRAMEWORK_VERSION_ENV_VAR = "AI_TEAM_FRAMEWORK_VERSION";

export type Environment = Readonly<Record<string, string | undefined>>;

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

/** Written by `python scripts/sync_init_scaffolds.py`; git-ignored. */
export const DEFAULT_VERSION_FILE = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "resources",
  "version.txt",
);

function twoDigits(value: number): string {
  return String(value).padStart(2, "0");
}

function isRealCalendarDate(year: number, month: number, day: number): boolean {
  const date = new Date(Date.UTC(year, month - 1, day));
  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day
  );
}

/** Today as `YYYY-MM-DD`, or the ISO date in AI_TEAM_TODAY when set. */
export function today(env: Environment = process.env, now: Date = new Date()): string {
  const override = env[TODAY_ENV_VAR];
  if (override === undefined) {
    return `${now.getFullYear()}-${twoDigits(now.getMonth() + 1)}-${twoDigits(now.getDate())}`;
  }
  const match = ISO_DATE.exec(override);
  if (
    match === null ||
    !isRealCalendarDate(Number(match[1]), Number(match[2]), Number(match[3]))
  ) {
    throw new AiTeamError(
      `${TODAY_ENV_VAR} must be an ISO date (YYYY-MM-DD), got '${override}'`,
    );
  }
  return override;
}

/** The framework version: AI_TEAM_FRAMEWORK_VERSION, else the generated version file. */
export function frameworkVersion(
  env: Environment = process.env,
  versionFile: string = DEFAULT_VERSION_FILE,
): string {
  const override = env[FRAMEWORK_VERSION_ENV_VAR];
  if (override !== undefined) return override;
  try {
    return readFileSync(versionFile, "utf8").trim();
  } catch (error) {
    if (isErrnoCode(error, "ENOENT")) {
      throw new AiTeamError(
        `Framework version file not found at ${versionFile}.`,
        `Run the sync (cd cli && python scripts/sync_init_scaffolds.py) to generate it, or set ${FRAMEWORK_VERSION_ENV_VAR}.`,
      );
    }
    throw error;
  }
}
