import type { ProjectRoot } from "../locator.js";
import type { Result } from "../result.js";

/** Tool-contract input for a command: camelCase fields, no `json` flag. */
export type CommandInput = Readonly<Record<string, unknown>>;

/** `init` takes the start directory; its `path` input is relative to it. */
export type InitHandler = (startDirectory: string, input: CommandInput) => Result;

/** `check-layout` takes the start directory and resolves its own root. */
export type CheckLayoutHandler = (startDirectory: string, input: CommandInput) => Result;

/** Every other command takes a project root that the caller has already located. */
export type RootHandler = (root: ProjectRoot, input: CommandInput) => Result;

export type Handler = InitHandler | CheckLayoutHandler | RootHandler;

/** Thrown by a stub handler so an unfinished command fails loudly rather than passing. */
export class NotImplementedError extends Error {
  constructor(command: string) {
    super(`The '${command}' command is not implemented yet.`);
    this.name = "NotImplementedError";
  }
}

const stubs = new WeakSet<Handler>();

/** A placeholder handler. The task that implements the command replaces it with a real one. */
export function notImplemented<H extends Handler>(command: string): H {
  const stub = (): never => {
    throw new NotImplementedError(command);
  };
  stubs.add(stub);
  return stub as unknown as H;
}

/** True while the handler is still a placeholder created by `notImplemented`. */
export function isStub(handler: Handler): boolean {
  return stubs.has(handler);
}
