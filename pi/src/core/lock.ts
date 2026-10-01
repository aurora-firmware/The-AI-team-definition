import {
  linkSync,
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { join } from "node:path";
import { isErrnoCode } from "./errno.js";
import { writeArtifact } from "./fs.js";
import type { ArtifactModel } from "./models.js";

/**
 * Project-local mutual exclusion for artifact ID allocation, the TS counterpart of
 * `ai_team.core.lock` (ADR-003).
 *
 * Node has no `flock`, so the lock is a file whose creation is atomic: the holder's pid is written
 * to a private temporary file, which is then hard-linked to the lock path. `link` fails when the
 * path exists, so exactly one process wins, and the lock never appears half-written. The lock
 * records its holder's pid, which lets a waiter detect a holder that died without releasing
 * (a crash or `kill -9`) and reclaim the lock.
 *
 * The lock path is `.ai-team-ts.lock`, separate from the Python CLI's `.ai-team.lock`, which this
 * module never reads or writes. A Python process and a pi session allocating at the same time in
 * one working tree remain unsupported.
 */

export const LOCK_FILENAME = ".ai-team-ts.lock";
export const DEFAULT_TIMEOUT_SECONDS = 10;
const POLL_INTERVAL_MILLISECONDS = 50;

/** The project allocation lock could not be acquired within the bounded wait. */
export class LockTimeout extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LockTimeout";
  }
}

export interface AllocationLockOptions {
  /** Maximum time to wait for the lock before raising `LockTimeout`. */
  readonly timeoutSeconds?: number;
}

function sleep(milliseconds: number): void {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, milliseconds);
}

/** Formats seconds like Python's `str(float)`, so the timeout message matches the core's. */
function formatSeconds(seconds: number): string {
  return Number.isInteger(seconds) ? seconds.toFixed(1) : String(seconds);
}

function isProcessAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    // EPERM means the process exists but belongs to someone else.
    return !isErrnoCode(error, "ESRCH");
  }
}

/** The pid recorded in the lock file; undefined when the file is gone or holds anything else. */
function readHolderPid(lockPath: string): number | undefined {
  let content: string;
  try {
    content = readFileSync(lockPath, "utf-8").trim();
  } catch (error) {
    if (isErrnoCode(error, "ENOENT")) return undefined;
    throw error;
  }
  return /^\d+$/.test(content) ? Number(content) : undefined;
}

/** Creates the lock file atomically with the holder pid inside; false when it already exists. */
function tryCreateLock(lockPath: string): boolean {
  const privatePath = `${lockPath}.${process.pid}.${Math.random().toString(36).slice(2)}.tmp`;
  writeFileSync(privatePath, String(process.pid), { flag: "wx" });
  try {
    linkSync(privatePath, lockPath);
    return true;
  } catch (error) {
    if (isErrnoCode(error, "EEXIST")) return false;
    throw error;
  } finally {
    rmSync(privatePath, { force: true });
  }
}

/**
 * Removes the lock when its holder is a dead process. The lock is first renamed to a private name,
 * so only one reclaimer acts on it. If the renamed file turns out to belong to a different holder
 * than the one observed dead (the lock was freed and retaken in between), it is linked back.
 */
function reclaimIfHolderDead(lockPath: string): void {
  const holderPid = readHolderPid(lockPath);
  if (holderPid === undefined || isProcessAlive(holderPid)) return;

  const stalePath = `${lockPath}.${process.pid}.${Math.random().toString(36).slice(2)}.stale`;
  try {
    renameSync(lockPath, stalePath);
  } catch (error) {
    if (isErrnoCode(error, "ENOENT")) return;
    throw error;
  }
  if (readHolderPid(stalePath) !== holderPid) {
    try {
      linkSync(stalePath, lockPath);
    } catch (error) {
      if (!isErrnoCode(error, "EEXIST")) throw error;
    }
  }
  rmSync(stalePath, { force: true });
}

/**
 * Runs `callback` while holding an exclusive, project-local lock at `<projectDir>/.ai-team-ts.lock`.
 *
 * Acquisition polls on a bounded retry loop. A lock whose holder process is dead is reclaimed; a
 * lock held by a live process, or holding unrecognised content, is waited on until the timeout.
 * @throws LockTimeout when the lock is still held after `timeoutSeconds`.
 */
export function allocationLock<T>(
  projectDir: string,
  callback: () => T,
  options: AllocationLockOptions = {},
): T {
  const { timeoutSeconds = DEFAULT_TIMEOUT_SECONDS } = options;
  mkdirSync(projectDir, { recursive: true });
  const lockPath = join(projectDir, LOCK_FILENAME);
  const deadline = Date.now() + timeoutSeconds * 1000;

  while (!tryCreateLock(lockPath)) {
    reclaimIfHolderDead(lockPath);
    if (tryCreateLock(lockPath)) break;
    if (Date.now() >= deadline) {
      throw new LockTimeout(
        `Could not acquire the project allocation lock at ${lockPath} within ` +
          `${formatSeconds(timeoutSeconds)} seconds; another ai-team process appears to be holding it.`,
      );
    }
    sleep(POLL_INTERVAL_MILLISECONDS);
  }

  try {
    return callback();
  } finally {
    rmSync(lockPath, { force: true });
  }
}

export interface CreateArtifactOptions {
  /** Scans existing artifacts and returns the next ID; called once, inside the lock. */
  readonly allocateId: () => string;
  /** Receives the allocated ID and returns the destination, model and body to write. */
  readonly build: (id: string) => readonly [string, ArtifactModel, string];
  readonly timeoutSeconds?: number;
}

/**
 * Allocates a new artifact ID and writes its file in one locked critical section.
 * @throws LockTimeout when the lock cannot be acquired in time.
 * @throws ArtifactExists when the built destination already exists.
 */
export function createArtifactWithLock(
  projectDir: string,
  options: CreateArtifactOptions,
): [string, string] {
  const lockOptions =
    options.timeoutSeconds === undefined ? {} : { timeoutSeconds: options.timeoutSeconds };
  return allocationLock(
    projectDir,
    () => {
      const id = options.allocateId();
      const [destination, model, body] = options.build(id);
      writeArtifact(destination, model, body);
      return [id, destination];
    },
    lockOptions,
  );
}
