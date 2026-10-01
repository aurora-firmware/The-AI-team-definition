import { archiveArtifacts } from "./archive.js";
import { createAdr } from "./adr.js";
import { createBug, resolveBug, startBug } from "./bug.js";
import { checkRepositoryLayout } from "./check-layout.js";
import { createChangeRequest } from "./change-request.js";
import { initRepository } from "./init.js";
import { listAdrs, listBugs, listChangeRequests, listSpecs, listTasks } from "./list.js";
import { writeReport } from "./report.js";
import { showArtifact } from "./show.js";
import { createSpec } from "./spec.js";
import { statusSummary } from "./status.js";
import { blockTask, completeTask, createTask, startTask, unblockTask } from "./task.js";
import { validateArtifacts } from "./validate.js";
import type { CheckLayoutHandler, InitHandler, RootHandler } from "./handler.js";

export { isStub, NotImplementedError } from "./handler.js";
export type { CommandInput } from "./handler.js";

/** A command's handler, tagged with the first argument the handler expects. */
export type CommandEntry =
  | { readonly kind: "init"; readonly handler: InitHandler }
  | { readonly kind: "check-layout"; readonly handler: CheckLayoutHandler }
  | { readonly kind: "root"; readonly handler: RootHandler };

const root = (handler: RootHandler): CommandEntry => ({ kind: "root", handler });

/**
 * Every tool-contract command and its handler. Each handler lives in its own module so that
 * the task implementing a command edits only that module, never this table.
 */
export const COMMANDS: Readonly<Record<string, CommandEntry>> = {
  init: { kind: "init", handler: initRepository },
  "check-layout": { kind: "check-layout", handler: checkRepositoryLayout },
  "spec new": root(createSpec),
  "adr new": root(createAdr),
  "change-request new": root(createChangeRequest),
  "task new": root(createTask),
  "task start": root(startTask),
  "task complete": root(completeTask),
  "task unblock": root(unblockTask),
  "task block": root(blockTask),
  "bug new": root(createBug),
  "bug start": root(startBug),
  "bug resolve": root(resolveBug),
  "list tasks": root(listTasks),
  "list bugs": root(listBugs),
  "list specs": root(listSpecs),
  "list adrs": root(listAdrs),
  "list change-requests": root(listChangeRequests),
  show: root(showArtifact),
  status: root(statusSummary),
  report: root(writeReport),
  validate: root(validateArtifacts),
  archive: root(archiveArtifacts),
};
