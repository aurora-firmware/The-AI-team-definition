import { notImplemented } from "./handler.js";
import type { RootHandler } from "./handler.js";

export const createTask: RootHandler = notImplemented("task new");
export const startTask: RootHandler = notImplemented("task start");
export const completeTask: RootHandler = notImplemented("task complete");
export const unblockTask: RootHandler = notImplemented("task unblock");
export const blockTask: RootHandler = notImplemented("task block");
