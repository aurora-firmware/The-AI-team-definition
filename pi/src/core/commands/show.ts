import { basename, sep } from "node:path";
import { readArtifact } from "../fs.js";
import type { ArtifactKind, ArtifactModel } from "../models.js";
import type { ProjectRoot } from "../locator.js";
import { failure, success } from "../result.js";
import { listMarkdownFiles } from "./artifact-files.js";
import type { RootHandler } from "./handler.js";

type ShownKind = Extract<ArtifactKind, "task" | "bug" | "spec" | "adr">;

function searchRoots(root: ProjectRoot): string[] {
  return [
    root.tasksPending,
    root.tasksInProgress,
    root.tasksCompleted,
    root.tasksBlocked,
    root.bugsOpen,
    root.bugsInProgress,
    root.bugsResolved,
    root.specs,
    root.decisions,
  ];
}

/** The kind is read off the path, as the Python command does. */
function kindForPath(path: string): ShownKind {
  const parts = path.split(sep);
  if (parts.includes("tasks")) return "task";
  if (parts.includes("bugs")) return "bug";
  if (parts.includes("specs")) return "spec";
  return "adr";
}

function matchesIdentifier(identifier: string, path: string): boolean {
  const token = identifier.toLowerCase();
  if (basename(path, ".md").toLowerCase().includes(token)) return true;

  const kind = kindForPath(path);
  if (kind === "spec") return false;
  const { model } = readArtifact(path, kind);
  return model.kind !== "spec" && model.id.toLowerCase() === token;
}

/** Every frontmatter key as text, with null for an empty value, as the Python command renders it. */
function frontmatterOf(model: ArtifactModel): Record<string, string | null> {
  const frontmatter: Record<string, string | null> = {};
  for (const { key } of model.sourceMap?.entries ?? []) {
    frontmatter[key] = model.sourceMap?.getString(key) ?? null;
  }
  return frontmatter;
}

/** Resolves an ID or slug fragment to one artifact and returns its path, frontmatter and body. */
export const showArtifact: RootHandler = (root, input) => {
  const { identifier } = input;
  if (typeof identifier !== "string" || identifier === "") {
    return failure("A non-empty 'identifier' is required to show an artifact.");
  }

  const roots = searchRoots(root);
  const matches = roots
    .flatMap(listMarkdownFiles)
    .filter((path) => matchesIdentifier(identifier, path));

  if (matches.length === 0) {
    return failure(`Artifact '${identifier}' not found. Searched roots: ${roots.join(", ")}`);
  }
  if (matches.length > 1) {
    return failure(
      [`Multiple artifacts matched '${identifier}':`, ...matches.map((match) => `- ${match}`)].join("\n"),
    );
  }

  const selected = matches[0] as string;
  const { model, body } = readArtifact(selected, kindForPath(selected));
  return success({ path: selected, frontmatter: frontmatterOf(model), body });
};
