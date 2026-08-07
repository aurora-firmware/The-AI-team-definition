"""Validation checks for AI-team artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ai_team.core.locator import ProjectRoot
from ai_team.core.models import (
    FrontmatterError,
    parse_adr,
    parse_bug,
    parse_change_request,
    parse_spec,
    parse_task,
)


@dataclass(frozen=True)
class Finding:
    """A single validation result item."""

    path: str
    level: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "level": self.level,
            "code": self.code,
            "message": self.message,
        }


TASK_ID_RE = re.compile(r"^T-\d{3}$")
BUG_ID_RE = re.compile(r"^B-\d{3}$")
SPEC_ID_RE = re.compile(r"^S-\d{3}$")
ADR_ID_RE = re.compile(r"^ADR-\d{3}$")
CHANGE_REQUEST_ID_RE = re.compile(r"^CR-\d{3}$")
SLUGGED_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.md$")
# New-style spec filenames: S-NNN-<slug>.md
SPEC_PREFIXED_FILENAME_RE = re.compile(r"^S-\d{3}-[a-z0-9][a-z0-9-]*\.md$")


def _should_skip(path: Path) -> bool:
    return path.name == ".gitkeep" or path.match("TEMPLATE-*.md")


def _iter_markdown_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        path
        for path in folder.glob("*.md")
        if path.is_file() and not _should_skip(path)
    )


def _finding(path: Path, root: ProjectRoot, code: str, message: str) -> Finding:
    return Finding(
        path=to_relative_path(path, root.repo),
        level="error",
        code=code,
        message=message,
    )


def _check_id_pattern(
    findings: list[Finding],
    root: ProjectRoot,
    path: Path,
    *,
    artifact_label: str,
    artifact_id: str,
    pattern: re.Pattern[str],
) -> None:
    if pattern.match(artifact_id):
        return
    findings.append(
        _finding(
            path,
            root,
            "id-pattern",
            (
                f"{artifact_label} id '{artifact_id}' does not match expected "
                f"pattern '{pattern.pattern}'."
            ),
        )
    )


def _check_stateful_filename(
    findings: list[Finding],
    root: ProjectRoot,
    path: Path,
    artifact_id: str,
) -> None:
    expected = re.compile(rf"^{re.escape(artifact_id)}-[a-z0-9][a-z0-9-]*\.md$")
    if expected.match(path.name):
        return
    findings.append(
        _finding(
            path,
            root,
            "filename-pattern",
            (
                f"Filename '{path.name}' does not match expected "
                f"'{artifact_id}-<slug>.md'."
            ),
        )
    )


def _check_spec_filename(
    findings: list[Finding],
    root: ProjectRoot,
    path: Path,
    *,
    spec_id: str | None,
) -> None:
    """Check spec filename against both legacy and new-style patterns.

    Accepts:
    - Legacy: ``<slug>.md`` (all-lowercase slug, no S-NNN prefix).
    - New-style: ``S-NNN-<slug>.md`` where the prefix matches the frontmatter id.

    Reports a ``filename-pattern`` finding when neither pattern matches, or when
    the S-NNN prefix is present but does not match the frontmatter id.
    """
    if SPEC_PREFIXED_FILENAME_RE.match(path.name):
        # New-style filename: verify prefix matches frontmatter id.
        id_prefix = path.name.split("-", 2)[:2]  # e.g. ["S", "001"]
        filename_id = "-".join(id_prefix)  # e.g. "S-001"
        if spec_id is not None and filename_id != spec_id:
            findings.append(
                _finding(
                    path,
                    root,
                    "filename-pattern",
                    (
                        f"Spec filename '{path.name}' id prefix '{filename_id}' "
                        f"does not match frontmatter id '{spec_id}'."
                    ),
                )
            )
        return
    if SLUGGED_FILENAME_RE.match(path.name):
        # Legacy filename: all-lowercase slug with no id prefix — always valid.
        return
    # Neither pattern matches.
    findings.append(
        _finding(
            path,
            root,
            "filename-pattern",
            (
                f"Spec filename '{path.name}' does not match "
                f"'<slug>.md' or 'S-NNN-<slug>.md'."
            ),
        )
    )


def _spec_reference_exists(reference: str, spec_slugs: set[str]) -> bool:
    if reference in spec_slugs:
        return True
    if reference.endswith(".md"):
        return reference[:-3] in spec_slugs
    return False


def _spec_index_entries(path: Path) -> set[str]:
    """Return every reference string that should resolve to the spec at *path*.

    Accepts the full filename stem, the legacy bare slug (the stem with any
    ``S-NNN-`` prefix stripped), and the frontmatter ``id`` when present.
    """
    entries = {path.stem}
    prefix_match = SPEC_PREFIXED_FILENAME_RE.match(path.name)
    if prefix_match:
        bare_slug = path.stem.split("-", 2)[2]
        entries.add(bare_slug)
    try:
        spec = parse_spec(path)
    except FrontmatterError:
        return entries
    if spec.id is not None:
        entries.add(spec.id)
    return entries


def _build_spec_slugs(root: ProjectRoot) -> set[str]:
    """Build the set of reference strings that resolve to an existing spec.

    Scans both ``specs/`` and ``specs/archive/`` so archived specs remain
    resolvable by task ``spec:`` references.
    """
    spec_slugs: set[str] = set()
    for folder in (root.specs, root.specs / "archive"):
        for path in _iter_markdown_files(folder):
            spec_slugs.update(_spec_index_entries(path))
    return spec_slugs


def validate_project(
    root: ProjectRoot,
    *,
    tasks: bool = False,
    bugs: bool = False,
    specs: bool = False,
    adrs: bool = False,
    change_requests: bool = False,
) -> list[Finding]:
    """Validate selected artifact categories and return findings."""
    findings: list[Finding] = []

    # Cross-reference indexes are built independently from selected scopes so
    # `--tasks`, `--bugs`, and `--adrs` can still validate references.
    spec_slugs = _build_spec_slugs(root)
    task_ids = _existing_task_ids(root)
    adr_ids = _existing_adr_ids(root)

    if tasks:
        state_folders = [
            ("pending", root.tasks_pending),
            ("in-progress", root.tasks_in_progress),
            ("completed", root.tasks_completed),
            ("blocked", root.tasks_blocked),
        ]
        for expected_state, folder in state_folders:
            for path in _iter_markdown_files(folder):
                try:
                    task = parse_task(path)
                except FrontmatterError as exc:
                    findings.append(
                        _finding(path, root, "frontmatter-invalid", str(exc))
                    )
                    continue

                _check_id_pattern(
                    findings,
                    root,
                    path,
                    artifact_label="Task",
                    artifact_id=task.id,
                    pattern=TASK_ID_RE,
                )
                _check_stateful_filename(findings, root, path, task.id)
                if task.status != expected_state:
                    findings.append(
                        _finding(
                            path,
                            root,
                            "status-mismatch",
                            (
                                f"Task status '{task.status}' does not match "
                                f"folder state '{expected_state}'."
                            ),
                        )
                    )
                if task.spec and not _spec_reference_exists(task.spec, spec_slugs):
                    findings.append(
                        _finding(
                            path,
                            root,
                            "task-spec-missing",
                            (
                                f"Task spec reference '{task.spec}' does not "
                                "resolve to an existing spec file."
                            ),
                        )
                    )

    if bugs:
        state_folders = [
            ("open", root.bugs_open),
            ("in-progress", root.bugs_in_progress),
            ("resolved", root.bugs_resolved),
        ]
        for expected_state, folder in state_folders:
            for path in _iter_markdown_files(folder):
                try:
                    bug = parse_bug(path)
                except FrontmatterError as exc:
                    findings.append(
                        _finding(path, root, "frontmatter-invalid", str(exc))
                    )
                    continue

                _check_id_pattern(
                    findings,
                    root,
                    path,
                    artifact_label="Bug",
                    artifact_id=bug.id,
                    pattern=BUG_ID_RE,
                )
                _check_stateful_filename(findings, root, path, bug.id)
                if bug.status != expected_state:
                    findings.append(
                        _finding(
                            path,
                            root,
                            "status-mismatch",
                            (
                                f"Bug status '{bug.status}' does not match "
                                f"folder state '{expected_state}'."
                            ),
                        )
                    )
                if bug.task and bug.task not in task_ids:
                    findings.append(
                        _finding(
                            path,
                            root,
                            "bug-task-missing",
                            (
                                f"Bug task reference '{bug.task}' does not "
                                "resolve to an existing task."
                            ),
                        )
                    )

    if specs:
        for path in _iter_markdown_files(root.specs):
            try:
                spec = parse_spec(path)
            except FrontmatterError as exc:
                findings.append(_finding(path, root, "frontmatter-invalid", str(exc)))
                continue

            source_map = spec._source_map or {}
            spec_id = source_map.get("id")
            if spec_id is None:
                findings.append(
                    _finding(
                        path,
                        root,
                        "id-missing",
                        "Spec frontmatter is missing required 'id' field.",
                    )
                )
            else:
                _check_id_pattern(
                    findings,
                    root,
                    path,
                    artifact_label="Spec",
                    artifact_id=str(spec_id),
                    pattern=SPEC_ID_RE,
                )

            _check_spec_filename(
                findings, root, path, spec_id=str(spec_id) if spec_id else None
            )

    if adrs:
        for path in _iter_markdown_files(root.decisions):
            try:
                adr = parse_adr(path)
            except FrontmatterError as exc:
                findings.append(_finding(path, root, "frontmatter-invalid", str(exc)))
                continue

            _check_id_pattern(
                findings,
                root,
                path,
                artifact_label="ADR",
                artifact_id=adr.id,
                pattern=ADR_ID_RE,
            )
            _check_stateful_filename(findings, root, path, adr.id)
            if adr.supersedes and adr.supersedes not in adr_ids:
                findings.append(
                    _finding(
                        path,
                        root,
                        "adr-supersedes-missing",
                        (
                            f"ADR supersedes reference '{adr.supersedes}' does not "
                            "resolve to an existing ADR."
                        ),
                    )
                )

    if change_requests:
        for path in _iter_markdown_files(root.change_requests):
            try:
                cr = parse_change_request(path)
            except FrontmatterError as exc:
                findings.append(_finding(path, root, "frontmatter-invalid", str(exc)))
                continue

            _check_id_pattern(
                findings,
                root,
                path,
                artifact_label="Change request",
                artifact_id=cr.id,
                pattern=CHANGE_REQUEST_ID_RE,
            )
            _check_stateful_filename(findings, root, path, cr.id)

    return findings


def _existing_task_ids(root: ProjectRoot) -> set[str]:
    task_ids: set[str] = set()
    for folder in (
        root.tasks_pending,
        root.tasks_in_progress,
        root.tasks_completed,
        root.tasks_blocked,
    ):
        for path in _iter_markdown_files(folder):
            try:
                task_ids.add(parse_task(path).id)
            except FrontmatterError:
                continue
    return task_ids


def _existing_adr_ids(root: ProjectRoot) -> set[str]:
    adr_ids: set[str] = set()
    for path in _iter_markdown_files(root.decisions):
        try:
            adr_ids.add(parse_adr(path).id)
        except FrontmatterError:
            continue
    return adr_ids


def to_relative_path(path: Path, repo: Path) -> str:
    """Return *path* relative to *repo* when possible."""
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)
