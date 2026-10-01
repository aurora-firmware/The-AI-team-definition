/**
 * Child-process entry point for the lock tests; run through vite-node so it can import the
 * TypeScript core. The mode and arguments come from argv:
 *
 *   allocate <projectDir> <count>  allocate `count` task IDs, printing each as it is written
 *   hold <projectDir>              take the lock, print "held", then block until killed
 */
import { join } from "node:path";
import { createArtifactWithLock, allocationLock } from "../../src/core/lock.js";
import { nextTaskId } from "../../src/core/ids.js";
import { findProjectRoot } from "../../src/core/locator.js";
import { parseTaskText } from "../../src/core/models.js";

const [mode, projectDir, countText] = process.argv.slice(2);
if (projectDir === undefined) throw new Error("projectDir argument is required");

if (mode === "allocate") {
  const root = findProjectRoot(projectDir, { root: projectDir });
  for (let index = 0; index < Number(countText); index += 1) {
    const [id] = createArtifactWithLock(root.projectDir, {
      allocateId: () => nextTaskId(root),
      build: (taskId) => {
        const text = `---\nid: ${taskId}\ntitle: Child\nstatus: pending\npriority: medium\nassigned-role: developer\ncreated: '2026-01-01'\n---\n`;
        const destination = join(root.tasksPending, `${taskId}-child.md`);
        return [destination, parseTaskText(text, destination), ""];
      },
    });
    console.log(id);
  }
} else if (mode === "hold") {
  allocationLock(projectDir, () => {
    console.log("held");
    for (;;) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1000);
  });
} else {
  throw new Error(`unknown mode: ${String(mode)}`);
}
