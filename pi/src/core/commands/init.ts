import { copyFileSync, existsSync, mkdirSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { stringify as stringifyToml } from "smol-toml";
import { frameworkVersion } from "../runtime.js";
import type { InitHandler } from "./handler.js";

/** Synced from the init scaffolds by `python scripts/sync_init_scaffolds.py`. */
const RESOURCES_DIR = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "resources");
const ROOT_GUIDANCE_FILES = ["CLAUDE.md", "AGENTS.md"];

interface PlannedCopy {
  readonly source: string;
  readonly destination: string;
}

interface GuidanceOutcome {
  readonly path: string;
  readonly outcome: string;
}

function compareCodePoints(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

/** Files under `directory`, ordered like Python's sorted `Path`s: path component by component. */
function listFiles(directory: string): string[] {
  const files: string[] = [];
  const visit = (current: string): void => {
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      const path = join(current, entry.name);
      if (entry.isDirectory()) visit(path);
      else files.push(path);
    }
  };
  visit(directory);
  return files.sort((left, right) => {
    const leftParts = relative(directory, left).split("/");
    const rightParts = relative(directory, right).split("/");
    for (let index = 0; index < Math.min(leftParts.length, rightParts.length); index += 1) {
      const order = compareCodePoints(leftParts[index]!, rightParts[index]!);
      if (order !== 0) return order;
    }
    return leftParts.length - rightParts.length;
  });
}

function planCopies(source: string, destination: string): PlannedCopy[] {
  return listFiles(source).map((path) => ({
    source: path,
    destination: join(destination, relative(source, path)),
  }));
}

function copyFile(source: string, destination: string): void {
  mkdirSync(dirname(destination), { recursive: true });
  copyFileSync(source, destination);
}

/** One outcome per root guidance file; only `created` writes. Never prompts. */
function handleRootGuidance(
  targetRoot: string,
  createRootGuidance: boolean,
  force: boolean,
  dryRun: boolean,
): GuidanceOutcome[] {
  return ROOT_GUIDANCE_FILES.map((filename) => {
    const destination = join(targetRoot, filename);
    let outcome: string;
    if (existsSync(destination) && !force) {
      outcome = "exists";
    } else if (dryRun) {
      outcome = "would-write";
    } else if (createRootGuidance) {
      copyFile(join(RESOURCES_DIR, "root", filename), destination);
      outcome = "created";
    } else {
      outcome = "not-requested";
    }
    return { path: destination, outcome };
  });
}

/**
 * Scaffolds the project skeleton and `.ai-team.toml` (empty `[init].tools`, runtime framework
 * version) under `input.path`, resolved against the start directory. Always non-interactive.
 */
export const initRepository: InitHandler = (startDirectory, input) => {
  const path = typeof input["path"] === "string" ? input["path"] : ".";
  const force = input["force"] === true;
  const dryRun = input["dryRun"] === true;
  const createRootGuidance = input["createRootGuidance"] === true;
  const targetRoot = resolve(startDirectory, path);

  const planned = planCopies(join(RESOURCES_DIR, "project"), join(targetRoot, "project"));
  const marker = join(targetRoot, ".ai-team.toml");
  const destinations = [...planned.map((copy) => copy.destination), marker];
  const collisions = destinations.filter((destination) => existsSync(destination));

  const payloadWith = (guidance: GuidanceOutcome[], isDryRun: boolean): Record<string, unknown> => ({
    files: destinations,
    dry_run: isDryRun,
    root_guidance: guidance,
  });

  let dryRunPayload: Record<string, unknown> | undefined;
  if (dryRun) {
    dryRunPayload = payloadWith(handleRootGuidance(targetRoot, createRootGuidance, force, true), true);
  }

  if (collisions.length > 0 && !force) {
    return {
      status: 1,
      ...(dryRunPayload === undefined ? {} : { payload: dryRunPayload }),
      message: `Refusing to overwrite existing files without --force:\n${collisions.join("\n")}`,
    };
  }
  if (dryRunPayload !== undefined) return { status: 0, payload: dryRunPayload };

  for (const copy of planned) copyFile(copy.source, copy.destination);
  const markerData = {
    project: { dir: "project" },
    init: { tools: [], framework_version: frameworkVersion() },
  };
  mkdirSync(dirname(marker), { recursive: true });
  writeFileSync(marker, stringifyToml(markerData), "utf-8");

  const guidance = handleRootGuidance(targetRoot, createRootGuidance, force, false);
  return { status: 0, payload: payloadWith(guidance, false) };
};
