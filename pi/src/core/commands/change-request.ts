import { join } from "node:path";
import { ArtifactExists } from "../fs.js";
import { splitFrontmatter } from "../frontmatter.js";
import { nextChangeRequestId } from "../ids.js";
import { createArtifactWithLock, LockTimeout } from "../lock.js";
import type { ChangeRequest } from "../models.js";
import { failure, success } from "../result.js";
import { today } from "../runtime.js";
import { slugify } from "../slug.js";
import { loadTemplate } from "../templates.js";
import type { RootHandler } from "./handler.js";

const TITLE_PLACEHOLDER = "# [Change Request Title]";

/** Creates a change request from the bundled template; the ID is allocated and the file written under the lock. */
export const createChangeRequest: RootHandler = (root, input) => {
  const { title } = input;
  if (typeof title !== "string" || title === "") {
    return failure("A non-empty 'title' is required to create a change request.");
  }

  try {
    const [id, destination] = createArtifactWithLock(root.projectDir, {
      allocateId: () => nextChangeRequestId([root.changeRequests]),
      build: (changeRequestId) => {
        const template = loadTemplate("change-request").toString("utf-8");
        const { body } = splitFrontmatter(template, "the change-request template");
        const model: ChangeRequest = {
          kind: "change-request",
          id: changeRequestId,
          title,
          status: "pending",
          created: today(),
          sourceMap: undefined,
        };
        return [
          join(root.changeRequests, `${changeRequestId}-${slugify(title)}.md`),
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
