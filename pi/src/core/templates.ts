import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { isErrnoCode } from "./errno.js";
import { AiTeamError } from "./result.js";

export type TemplateKind = "task" | "bug" | "spec" | "adr" | "report" | "change-request";

const TEMPLATE_FILES: Readonly<Record<TemplateKind, string>> = {
  task: "task.md",
  bug: "bug.md",
  spec: "spec.md",
  adr: "adr.md",
  report: "progress-report.md",
  "change-request": "change-request.md",
};

/** Synced from `cli/src/ai_team/templates` by `python scripts/sync_init_scaffolds.py`. */
export const DEFAULT_TEMPLATES_DIR = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "resources",
  "templates",
);

function isTemplateKind(kind: string): kind is TemplateKind {
  return Object.hasOwn(TEMPLATE_FILES, kind);
}

/** The template's bytes, untouched, so rendered artifacts match the Python CLI. */
export function loadTemplate(
  kind: TemplateKind,
  templatesDir: string = DEFAULT_TEMPLATES_DIR,
): Buffer {
  if (!isTemplateKind(kind)) {
    const supported = Object.keys(TEMPLATE_FILES).join(", ");
    throw new AiTeamError(`Unsupported template kind '${String(kind)}'. Supported kinds: ${supported}`);
  }
  const path = join(templatesDir, TEMPLATE_FILES[kind]);
  try {
    return readFileSync(path);
  } catch (error) {
    if (isErrnoCode(error, "ENOENT")) {
      throw new AiTeamError(
        `Template file not found at ${path}.`,
        "Run the sync (cd cli && python scripts/sync_init_scaffolds.py) to generate pi/resources.",
      );
    }
    throw error;
  }
}
