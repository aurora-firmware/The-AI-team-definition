import { basename } from "node:path";
import {
  parseAdr,
  parseBug,
  parseChangeRequest,
  parseSpec,
  parseTask,
} from "../models.js";
import type { ProjectRoot } from "../locator.js";
import { success } from "../result.js";
import { listMarkdownFiles } from "./artifact-files.js";
import type { RootHandler } from "./handler.js";

type Row = Record<string, string>;

/** Rows from the state folders, or from the one folder named by `state`; an unknown state has none. */
function collectFromStateFolders<T>(
  folders: readonly (readonly [string, string])[],
  state: unknown,
  parse: (path: string) => T,
  buildRow: (model: T, folderState: string) => Row,
): Row[] {
  const selected = state === undefined || state === null ? folders : folders.filter(([name]) => name === state);
  return selected.flatMap(([folderState, folder]) =>
    listMarkdownFiles(folder).map((path) => buildRow(parse(path), folderState)),
  );
}

function taskFolders(root: ProjectRoot): [string, string][] {
  return [
    ["pending", root.tasksPending],
    ["in-progress", root.tasksInProgress],
    ["completed", root.tasksCompleted],
    ["blocked", root.tasksBlocked],
  ];
}

function bugFolders(root: ProjectRoot): [string, string][] {
  return [
    ["open", root.bugsOpen],
    ["in-progress", root.bugsInProgress],
    ["resolved", root.bugsResolved],
  ];
}

export const listTasks: RootHandler = (root, input) =>
  rows(
    collectFromStateFolders(taskFolders(root), input["state"], parseTask, (task, state) => ({
      id: task.id,
      title: task.title,
      state,
      priority: task.priority,
      "assigned-role": task.assignedRole,
    })),
  );

export const listBugs: RootHandler = (root, input) =>
  rows(
    collectFromStateFolders(bugFolders(root), input["state"], parseBug, (bug, state) => ({
      id: bug.id,
      title: bug.title,
      state,
      severity: bug.severity,
    })),
  );

export const listSpecs: RootHandler = (root) =>
  rows(
    listMarkdownFiles(root.specs).map((path) => {
      const spec = parseSpec(path);
      return {
        id: spec.id ?? basename(path, ".md"),
        title: spec.title,
        status: spec.status,
        version: spec.version,
      };
    }),
  );

export const listAdrs: RootHandler = (root) =>
  rows(
    listMarkdownFiles(root.decisions).map((path) => {
      const adr = parseAdr(path);
      return { id: adr.id, title: adr.title, status: adr.status };
    }),
  );

export const listChangeRequests: RootHandler = (root) =>
  rows(
    listMarkdownFiles(root.changeRequests).map((path) => {
      const changeRequest = parseChangeRequest(path);
      return { id: changeRequest.id, title: changeRequest.title, state: changeRequest.status };
    }),
  );

/** A list command's payload is the bare row array, as the Python `--json` output is. */
function rows(items: Row[]) {
  return success(items as unknown as Record<string, unknown>);
}
