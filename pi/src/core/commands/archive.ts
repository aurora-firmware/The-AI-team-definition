import { mkdirSync } from "node:fs";
import { basename, join } from "node:path";
import { moveArtifact } from "../fs.js";
import { parseBug, parseTask } from "../models.js";
import { AiTeamError, failure, success } from "../result.js";
import { today } from "../runtime.js";
import { listMarkdownFiles } from "./artifact-files.js";
import type { RootHandler } from "./handler.js";

const DURATION = /^(\d+)([dwmy])$/;
const DAYS_PER_UNIT: Readonly<Record<string, number>> = { d: 1, w: 7, m: 30, y: 365 };
const DEFAULT_OLDER_THAN = "90d";
const MS_PER_DAY = 86_400_000;

function parseOlderThanDays(value: string): number | undefined {
  const match = DURATION.exec(value);
  if (match === null) return undefined;
  return Number(match[1]) * DAYS_PER_UNIT[match[2]!]!;
}

/** Calendar-day arithmetic on ISO dates, done in UTC so daylight saving cannot shift a day. */
function minusDays(isoDate: string, days: number): string {
  const [year, month, day] = isoDate.split("-").map(Number) as [number, number, number];
  const shifted = new Date(Date.UTC(year, month - 1, day) - days * MS_PER_DAY);
  return shifted.toISOString().slice(0, 10);
}

interface Move { source: string; destination: string }

/** Archives (or, with `dryRun`, lists) completed tasks and resolved bugs created before the cutoff. */
export const archiveArtifacts: RootHandler = (root, input) => {
  const olderThan = input["olderThan"] ?? DEFAULT_OLDER_THAN;
  const dryRun = input["dryRun"] === true;
  const days = typeof olderThan === "string" ? parseOlderThanDays(olderThan) : undefined;
  if (days === undefined) {
    return failure(`Invalid --older-than '${String(olderThan)}'. Expected format: <number><d|w|m|y>.`);
  }

  const cutoff = minusDays(today(), days);
  const archiveRoot = join(root.projectDir, "archive");
  const moves: Move[] = [];
  const sources: [string, typeof parseTask | typeof parseBug][] = [
    [root.tasksCompleted, parseTask],
    [root.bugsResolved, parseBug],
  ];
  for (const [folder, parse] of sources) {
    for (const source of listMarkdownFiles(folder)) {
      const created = parse(source).created;
      if (created === undefined) {
        throw new AiTeamError(
          `Cannot archive ${source}: it has no 'created' date.`,
          "Add a 'created: YYYY-MM-DD' field to its frontmatter.",
        );
      }
      // ISO dates compare correctly as strings.
      if (created < cutoff) {
        moves.push({ source, destination: join(archiveRoot, created.slice(0, 7), basename(source)) });
      }
    }
  }

  if (!dryRun) {
    for (const move of moves) {
      mkdirSync(join(move.destination, ".."), { recursive: true });
      moveArtifact(move.source, move.destination);
    }
  }
  return success({ dry_run: dryRun, moves });
};
