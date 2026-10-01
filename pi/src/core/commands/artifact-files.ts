import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

/** Orders strings by Unicode code point, like Python's `sorted` on file names. */
export function compareCodePoints(left: string, right: string): number {
  const leftPoints = Array.from(left, (char) => char.codePointAt(0) ?? 0);
  const rightPoints = Array.from(right, (char) => char.codePointAt(0) ?? 0);
  const shared = Math.min(leftPoints.length, rightPoints.length);
  for (let index = 0; index < shared; index += 1) {
    const difference = (leftPoints[index] ?? 0) - (rightPoints[index] ?? 0);
    if (difference !== 0) return difference;
  }
  return leftPoints.length - rightPoints.length;
}

/** Sorted markdown artifact files in `folder`, skipping templates; a missing folder has none. */
export function listMarkdownFiles(folder: string): string[] {
  if (!existsSync(folder)) return [];
  return readdirSync(folder)
    .filter((name) => name.endsWith(".md") && !name.startsWith("TEMPLATE-"))
    .filter((name) => statSync(join(folder, name)).isFile())
    .sort(compareCodePoints)
    .map((name) => join(folder, name));
}
