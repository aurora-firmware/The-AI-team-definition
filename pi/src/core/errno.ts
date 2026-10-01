/** Narrows an unknown caught value to a Node system error with the given code (e.g. "ENOENT"). */
export function isErrnoCode(error: unknown, code: string): boolean {
  return error instanceof Error && "code" in error && error.code === code;
}
