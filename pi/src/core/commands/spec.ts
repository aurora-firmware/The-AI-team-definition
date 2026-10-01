import { join } from "node:path";
import { ArtifactExists } from "../fs.js";
import { parseFrontmatterSource, splitFrontmatter } from "../frontmatter.js";
import { nextSpecId } from "../ids.js";
import { createArtifactWithLock, LockTimeout } from "../lock.js";
import type { Spec } from "../models.js";
import { failure, success } from "../result.js";
import { today } from "../runtime.js";
import { slugify } from "../slug.js";
import { loadTemplate } from "../templates.js";
import type { RootHandler } from "./handler.js";

const SPEC_STATUSES = ["draft", "review", "approved", "superseded"];
const TITLE_PLACEHOLDER = "# [Specification Title]";

/** Creates a spec from the bundled template; the ID is allocated and the file written under the lock. */
export const createSpec: RootHandler = (root, input) => {
  const { title, author = "planner", status = "draft" } = input;
  if (typeof title !== "string" || title === "") {
    return failure("A non-empty 'title' is required to create a spec.");
  }
  if (typeof author !== "string") return failure("The spec 'author' must be a string.");
  if (typeof status !== "string" || !SPEC_STATUSES.includes(status)) {
    return failure(
      `Invalid spec status ${JSON.stringify(status)}.`,
      `Use one of: ${SPEC_STATUSES.join(", ")}.`,
    );
  }

  try {
    const [id, destination] = createArtifactWithLock(root.projectDir, {
      allocateId: () => nextSpecId(root),
      build: (specId) => {
        const template = loadTemplate("spec").toString("utf-8");
        const { yamlText, body } = splitFrontmatter(template, "the spec template");
        const model: Spec = {
          kind: "spec",
          title,
          version: "0.1",
          status,
          created: today(),
          author,
          id: specId,
          sourceMap: parseFrontmatterSource(yamlText, "the spec template"),
        };
        return [
          join(root.specs, `${specId}-${slugify(title)}.md`),
          model,
          body.replace(TITLE_PLACEHOLDER, () => `# ${title}`),
        ];
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
