import { spawn } from "node:child_process";
import type { ChildProcess } from "node:child_process";
import { mkdirSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { LockTimeout, allocationLock } from "../src/core/lock.js";

const testDir = dirname(fileURLToPath(import.meta.url));
const viteNode = join(testDir, "..", "node_modules", ".bin", "vite-node");
const childScript = join(testDir, "helpers", "lock-child.ts");

let projectDir: string;
const children: ChildProcess[] = [];

beforeEach(() => {
  projectDir = mkdtempSync(join(tmpdir(), "ai-team-lock-"));
});

afterEach(() => {
  for (const child of children.splice(0)) child.kill("SIGKILL");
  rmSync(projectDir, { recursive: true, force: true });
});

function runChild(args: string[]): ChildProcess {
  const child = spawn(viteNode, [childScript, ...args], { stdio: ["ignore", "pipe", "pipe"] });
  children.push(child);
  return child;
}

interface ChildOutput {
  readonly lines: string[];
  readonly code: number | null;
  readonly stderr: string;
}

function collect(child: ChildProcess): Promise<ChildOutput> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    child.stdout?.on("data", (chunk: Buffer) => (stdout += chunk.toString()));
    child.stderr?.on("data", (chunk: Buffer) => (stderr += chunk.toString()));
    child.on("close", (code) =>
      resolve({ lines: stdout.split("\n").filter((line) => line !== ""), code, stderr }),
    );
  });
}

function waitForLine(child: ChildProcess, expected: string): Promise<void> {
  return new Promise((resolve, reject) => {
    let buffered = "";
    child.stdout?.on("data", (chunk: Buffer) => {
      buffered += chunk.toString();
      if (buffered.includes(expected)) resolve();
    });
    child.on("close", () => reject(new Error(`child exited before printing "${expected}"`)));
  });
}

function seedProject(): string {
  const root = join(projectDir, "repo");
  for (const dir of ["tasks/pending", "tasks/in-progress", "tasks/completed", "tasks/blocked"]) {
    mkdirSync(join(root, "project", dir), { recursive: true });
  }
  return root;
}

describe("allocationLock across processes", () => {
  it("does not block beyond the bounded wait when the holder is killed mid-allocation", async () => {
    const holder = runChild(["hold", projectDir]);
    await waitForLine(holder, "held");
    holder.kill("SIGKILL");
    await collect(holder);

    const started = Date.now();
    const value = allocationLock(projectDir, () => "acquired", { timeoutSeconds: 5 });
    expect(value).toBe("acquired");
    expect(Date.now() - started).toBeLessThan(5000);
  }, 30_000);

  it("times out while a live holder in another process keeps the lock", async () => {
    const holder = runChild(["hold", projectDir]);
    await waitForLine(holder, "held");
    expect(() => allocationLock(projectDir, () => 1, { timeoutSeconds: 0.3 })).toThrow(
      LockTimeout,
    );
  }, 30_000);

  it("allocates no duplicate ID across two concurrent processes over 50 repetitions", async () => {
    const root = seedProject();
    const first = collect(runChild(["allocate", root, "50"]));
    const second = collect(runChild(["allocate", root, "50"]));
    const [a, b] = await Promise.all([first, second]);

    expect(a.stderr).toBe("");
    expect(b.stderr).toBe("");
    const allocated = [...a.lines, ...b.lines];
    expect(allocated).toHaveLength(100);
    expect(new Set(allocated).size).toBe(100);
    expect(readdirSync(join(root, "project", "tasks", "pending"))).toHaveLength(100);
  }, 120_000);
});
