import { join } from "node:path";
import { ArtifactExists } from "../fs.js";
import { splitFrontmatter } from "../frontmatter.js";
import { nextAdrId } from "../ids.js";
import { createArtifactWithLock, LockTimeout } from "../lock.js";
import type { Adr } from "../models.js";
import { failure, success } from "../result.js";
import { today } from "../runtime.js";
import { slugify } from "../slug.js";
import { loadTemplate } from "../templates.js";
import type { RootHandler } from "./handler.js";

const ADR_STATUSES = ["proposed", "accepted", "superseded"];

/** Creates an ADR from the bundled template; the ID is allocated and the file written under the lock. */
export const createAdr: RootHandler = (root, input) => {
  const { title, status = "proposed", supersedes } = input;
  if (typeof title !== "string" || title === "") {
    return failure("A non-empty 'title' is required to create an ADR.");
  }
  if (typeof status !== "string" || !ADR_STATUSES.includes(status)) {
    return failure(
      `Invalid ADR status ${JSON.stringify(status)}.`,
      `Use one of: ${ADR_STATUSES.join(", ")}.`,
    );
  }
  if (supersedes !== undefined && supersedes !== null && typeof supersedes !== "string") {
    return failure("The ADR 'supersedes' value must be a string.");
  }

  try {
    const [id, destination] = createArtifactWithLock(root.projectDir, {
      allocateId: () => nextAdrId(root),
      build: (adrId) => {
        const template = loadTemplate("adr").toString("utf-8");
        const { body } = splitFrontmatter(template, "the ADR template");
        const model: Adr = {
          kind: "adr",
          id: adrId,
          title,
          status,
          created: today(),
          supersedes: supersedes ?? undefined,
          sourceMap: undefined,
        };
        return [join(root.decisions, `${adrId}-${slugify(title)}.md`), model, body];
      },
    });
    return success({ id, path: destination });
  } catch (error) {
    if (error instanceof ArtifactExists || error instanceof LockTimeout) {
      return failure(error.message);
    }
    throw error;
  }
};
