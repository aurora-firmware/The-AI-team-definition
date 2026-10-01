import { existsSync, readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { parse as parseToml } from "smol-toml";
import { AiTeamError } from "./result.js";
import type { Environment } from "./runtime.js";

/**
 * Locates the consuming project's root, mirroring `ai_team.core.locator`.
 *
 * Resolution order: explicit root, `AI_TEAM_ROOT`, the `[project] dir` of the nearest
 * `.ai-team.toml` walking up, then the nearest folder holding the default project directory.
 * The start directory is always a parameter; the process working directory is never consulted.
 */

export const ROOT_ENV_VAR = "AI_TEAM_ROOT";
export const DEFAULT_PROJECT_DIR = "project";
const MARKER_FILE = ".ai-team.toml";
const INIT_HINT = "Run 'ai-team init' to bootstrap the project structure.";

/** No project root can be resolved; `message` says what was searched, `hint` what to do next. */
export class ProjectRootNotFound extends AiTeamError {
  constructor(message: string, hint: string) {
    super(message, hint);
    this.name = "ProjectRootNotFound";
  }
}

/** Absolute paths to every AI-team artifact directory in a project. */
export interface ProjectRoot {
  readonly repo: string;
  readonly projectDir: string;
  readonly specs: string;
  readonly tasksPending: string;
  readonly tasksInProgress: string;
  readonly tasksCompleted: string;
  readonly tasksBlocked: string;
  readonly bugsOpen: string;
  readonly bugsInProgress: string;
  readonly bugsResolved: string;
  readonly changeRequests: string;
  readonly decisions: string;
  readonly docs: string;
}

export interface FindProjectRootOptions {
  /** Treat this directory as the repo root and skip the environment and the walk. */
  readonly root?: string;
  /** Default artifact folder name when no `.ai-team.toml` overrides it. */
  readonly projectDir?: string;
  readonly env?: Environment;
}

function buildProjectRoot(repo: string, projectDirName: string): ProjectRoot {
  const projectDir = join(repo, projectDirName);
  return {
    repo,
    projectDir,
    specs: join(projectDir, "specs"),
    tasksPending: join(projectDir, "tasks", "pending"),
    tasksInProgress: join(projectDir, "tasks", "in-progress"),
    tasksCompleted: join(projectDir, "tasks", "completed"),
    tasksBlocked: join(projectDir, "tasks", "blocked"),
    bugsOpen: join(projectDir, "bugs", "open"),
    bugsInProgress: join(projectDir, "bugs", "in-progress"),
    bugsResolved: join(projectDir, "bugs", "resolved"),
    changeRequests: join(projectDir, "change-requests"),
    decisions: join(projectDir, "decisions"),
    docs: join(projectDir, "docs"),
  };
}

/** Absolute path with symlinks resolved when the path exists, like Python's `Path.resolve()`. */
function resolvePath(path: string): string {
  const absolute = resolve(path);
  try {
    return realpathSync(absolute);
  } catch {
    return absolute;
  }
}

function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

/** The `[project] dir` of the marker file in `directory`; undefined when absent, unreadable or unset. */
function markerProjectDir(directory: string): string | undefined {
  const markerPath = join(directory, MARKER_FILE);
  if (!existsSync(markerPath)) return undefined;
  try {
    const project = parseToml(readFileSync(markerPath, "utf-8")).project;
    if (typeof project !== "object" || project === null || Array.isArray(project)) return undefined;
    const dir = (project as Record<string, unknown>).dir;
    return typeof dir === "string" ? dir : undefined;
  } catch {
    return undefined;
  }
}

/** Finds the project root, starting the upward search at `startDirectory`. */
export function findProjectRoot(
  startDirectory: string,
  options: FindProjectRootOptions = {},
): ProjectRoot {
  const { root, projectDir = DEFAULT_PROJECT_DIR, env = process.env } = options;
  const start = resolvePath(startDirectory);

  if (root !== undefined) {
    const repo = resolvePath(root);
    const dirName = markerProjectDir(repo) || projectDir;
    if (isDirectory(join(repo, dirName))) return buildProjectRoot(repo, dirName);
    throw new ProjectRootNotFound(
      `No '${dirName}/' folder found under the provided --root ${repo}.`,
      INIT_HINT,
    );
  }

  const envRoot = env[ROOT_ENV_VAR];
  if (envRoot) {
    const repo = resolvePath(envRoot);
    const dirName = markerProjectDir(repo) || projectDir;
    if (isDirectory(join(repo, dirName))) return buildProjectRoot(repo, dirName);
    throw new ProjectRootNotFound(
      `No '${dirName}/' folder found under ${ROOT_ENV_VAR}=${repo}.`,
      INIT_HINT,
    );
  }

  const searched: string[] = [];
  let candidate = start;
  for (;;) {
    searched.push(candidate);

    const configuredName = markerProjectDir(candidate);
    if (configuredName !== undefined && isDirectory(join(candidate, configuredName))) {
      return buildProjectRoot(candidate, configuredName);
    }
    if (isDirectory(join(candidate, projectDir))) return buildProjectRoot(candidate, projectDir);

    const parent = dirname(candidate);
    if (parent === candidate) break;
    candidate = parent;
  }

  throw new ProjectRootNotFound(
    `Could not locate a '${projectDir}/' directory by walking up from ${start}. ` +
      `Searched: ${searched.join(", ")}.`,
    INIT_HINT,
  );
}
