/**
 * Structured command result, mirroring the Python `ai_team.core.result.Result`.
 *
 * `status` is the process exit status (0 on success). `payload` holds the
 * machine-readable data on success. `message` and `hint` stay apart on failure
 * so non-CLI callers can use them separately; `resultText` joins them.
 */
export interface Result {
  readonly status: number;
  readonly payload?: Readonly<Record<string, unknown>>;
  readonly message?: string;
  readonly hint?: string;
}

export function success(payload: Readonly<Record<string, unknown>>): Result {
  return { status: 0, payload };
}

export function failure(message: string, hint?: string, status = 1): Result {
  return hint === undefined ? { status, message } : { status, message, hint };
}

/** The CLI error text: the message followed by the hint, if any. */
export function resultText(result: Result): string {
  return [result.message, result.hint].filter((part) => part).join(" ");
}

/** A thrown error that keeps the message and the corrective hint separate. */
export class AiTeamError extends Error {
  readonly hint: string | undefined;

  constructor(message: string, hint?: string) {
    super(message);
    this.name = "AiTeamError";
    this.hint = hint;
  }
}
