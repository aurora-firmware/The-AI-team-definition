"""Read-only resolution and validation of the AI-team repository layout."""

from __future__ import annotations

import importlib.metadata
import importlib.resources as resources
import re
import tomllib
from dataclasses import dataclass, field
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Literal

from ai_team.core.locator import ProjectRoot
from ai_team.core.validate import Finding as ArtifactFinding
from ai_team.core.validate import validate_project

_SUPPORTED_TOOLS = ("claude", "codex")
_DEFAULT_PROJECT_DIR = "project"
_VERSION_PATTERN = re.compile(
    r"[0-9]+(?:\.[0-9]+)*(?:[A-Za-z][A-Za-z0-9.-]*[0-9]?|[.+-][A-Za-z0-9.-]+)*"
)
_Status = Literal["valid", "missing", "invalid"]


@dataclass(frozen=True)
class LayoutFinding:
    """One actionable violation of a numbered layout validation level."""

    level: int
    path: str
    problem: str
    suggested_fix: str


@dataclass(frozen=True)
class LayoutContract:
    """Locally resolved inputs used by every layout validation level."""

    repo: Path
    marker: Path
    project_dir: Path
    tools: tuple[str, ...]
    configured_version: str | None
    current_version: str | None
    raw_configured_version: object = field(default=None, repr=False)
    marker_status: _Status = field(default="valid", repr=False)
    version_status: _Status = field(default="valid", repr=False)


def _finding(
    level: int,
    path: str,
    problem: str,
    suggested_fix: str,
) -> LayoutFinding:
    return LayoutFinding(level, path, problem, suggested_fix)


def _is_project_dir_name(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value not in {".", ".."}
        and "/" not in value
        and "\\" not in value
        and not Path(value).is_absolute()
    )


def _is_version(value: object) -> bool:
    return isinstance(value, str) and _VERSION_PATTERN.fullmatch(value) is not None


def resolve_layout(
    repo: Path,
    *,
    current_version: str | None = None,
) -> tuple[LayoutContract, list[LayoutFinding]]:
    """Resolve marker configuration and installed contract data without mutation."""

    repo = repo.resolve()
    marker = repo / ".ai-team.toml"
    findings: list[LayoutFinding] = []
    marker_status: _Status = "valid"
    data: object = {}

    if not marker.is_file():
        marker_status = "missing"
        findings.append(
            _finding(
                1,
                ".ai-team.toml",
                "Repository marker .ai-team.toml is missing; project and tool settings cannot be resolved.",
                "Run 'ai-team init' or restore .ai-team.toml; repository conventions will be checked where safe.",
            )
        )
    else:
        try:
            with marker.open("rb") as stream:
                data = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            marker_status = "invalid"
            findings.append(
                _finding(
                    1,
                    ".ai-team.toml",
                    f"Repository marker .ai-team.toml is invalid: {exc}",
                    "Correct the TOML syntax or regenerate the marker with 'ai-team init'.",
                )
            )

    project_value: object = None
    tools_value: object = None
    version_value: object = None
    if marker_status == "valid" and isinstance(data, dict):
        project_table = data.get("project")
        init_table = data.get("init")
        if isinstance(project_table, dict):
            project_value = project_table.get("dir")
        if isinstance(init_table, dict):
            tools_value = init_table.get("tools")
            version_value = init_table.get("framework_version")

    project_dir_name = _DEFAULT_PROJECT_DIR
    if marker_status == "valid":
        if _is_project_dir_name(project_value):
            project_dir_name = project_value
        else:
            findings.append(
                _finding(
                    1,
                    ".ai-team.toml",
                    "Marker value [project].dir is missing or invalid; using the conventional 'project' directory.",
                    "Set [project].dir to one usable relative directory name, such as 'project'.",
                )
            )

    selected_tools: list[str] = []
    if marker_status == "valid":
        if not isinstance(tools_value, list):
            findings.append(
                _finding(
                    1,
                    ".ai-team.toml",
                    "Marker value [init].tools is missing or invalid; no tool directories can be selected safely.",
                    "Set [init].tools to an array containing supported tool names: 'claude' and/or 'codex'.",
                )
            )
        else:
            invalid_tools = [
                value
                for value in tools_value
                if not isinstance(value, str) or value not in _SUPPORTED_TOOLS
            ]
            for value in tools_value:
                if (
                    isinstance(value, str)
                    and value in _SUPPORTED_TOOLS
                    and value not in selected_tools
                ):
                    selected_tools.append(value)
            if invalid_tools:
                findings.append(
                    _finding(
                        1,
                        ".ai-team.toml",
                        f"Marker contains unsupported or invalid configured tools: {invalid_tools!r}.",
                        "Keep only supported tool names: 'claude' and/or 'codex'.",
                    )
                )

    version_status: _Status = "valid"
    configured_version: str | None = None
    if marker_status != "valid" or version_value is None:
        version_status = "missing"
    elif _is_version(version_value):
        configured_version = version_value
    else:
        version_status = "invalid"

    installed_version = (
        importlib.metadata.version("ai-team")
        if current_version is None
        else current_version
    )
    return (
        LayoutContract(
            repo=repo,
            marker=marker,
            project_dir=repo / project_dir_name,
            tools=tuple(selected_tools),
            configured_version=configured_version,
            current_version=installed_version,
            raw_configured_version=version_value,
            marker_status=marker_status,
            version_status=version_status,
        ),
        sorted(findings, key=_sort_key),
    )


def _resource_directories(root: Traversable) -> list[Path]:
    """Return directory paths below an importlib Traversable resource root."""

    directories: list[Path] = []

    def walk(node: Traversable, relative: Path) -> None:
        for child in node.iterdir():
            if child.is_dir():
                child_relative = relative / child.name
                directories.append(child_relative)
                walk(child, child_relative)

    walk(root, Path())
    return directories


def _expected_directories(contract: LayoutContract) -> list[Path]:
    scaffold_root = resources.files("ai_team.init").joinpath("scaffolds")
    expected = [contract.project_dir]
    expected.extend(
        contract.project_dir / relative
        for relative in _resource_directories(scaffold_root.joinpath("project"))
    )
    for tool in contract.tools:
        tool_root = contract.repo / f".{tool}"
        expected.append(tool_root)
        expected.extend(
            tool_root / relative
            for relative in _resource_directories(scaffold_root.joinpath(tool))
        )
    return expected


def check_level_1(contract: LayoutContract) -> list[LayoutFinding]:
    """Report missing directories from current project and selected-tool scaffolds."""

    findings = []
    for path in _expected_directories(contract):
        if not path.is_dir():
            display_path = path.relative_to(contract.repo).as_posix()
            findings.append(
                _finding(
                    1,
                    display_path,
                    f"Required scaffold directory '{display_path}' is missing.",
                    "Create the directory by restoring the current scaffold or rerunning 'ai-team init' with the configured tools.",
                )
            )
    return sorted(findings, key=_sort_key)


_LEVEL_2_CODES = {
    "filename-pattern",
    "frontmatter-invalid",
    "id-missing",
    "id-pattern",
    "status-mismatch",
}


def _artifact_suggested_fix(finding: ArtifactFinding) -> str:
    if finding.code == "filename-pattern":
        return "Rename the artifact to the filename convention stated in the problem."
    if finding.code == "status-mismatch":
        return (
            "Update the frontmatter status to match the lifecycle directory, or move "
            "the artifact to the directory matching its current status."
        )
    if finding.code == "id-pattern":
        return "Correct the frontmatter id to the required artifact ID pattern."
    if finding.code == "id-missing":
        return "Add the required artifact id to the YAML frontmatter."
    return (
        "Correct the YAML frontmatter and add every required field for this "
        "artifact type."
    )


def check_level_2(contract: LayoutContract) -> list[LayoutFinding]:
    """Report managed artifact naming, frontmatter, and lifecycle violations."""

    if not contract.project_dir.is_dir():
        display_path = contract.project_dir.relative_to(contract.repo).as_posix()
        return [
            _finding(
                2,
                display_path,
                f"Artifact checks are blocked because project directory '{display_path}' is missing or is not a directory.",
                "Restore the configured project directory, then rerun the layout check.",
            )
        ]

    root = ProjectRoot._from_repo_and_project_dir_name(
        contract.repo, contract.project_dir.name
    )
    findings: list[LayoutFinding] = []
    scopes = (
        {"specs": True},
        {"tasks": True},
        {"bugs": True},
        {"change_requests": True},
        {"adrs": True},
    )
    for scope in scopes:
        try:
            artifact_findings = validate_project(root, **scope)
        except OSError as exc:
            scope_name = next(iter(scope)).replace("_", " ")
            findings.append(
                _finding(
                    2,
                    contract.project_dir.relative_to(contract.repo).as_posix(),
                    f"The {scope_name} artifact check is blocked: {exc}",
                    "Restore readable managed artifact inputs, then rerun the layout check.",
                )
            )
            continue

        findings.extend(
            _finding(
                2,
                finding.path,
                finding.message,
                _artifact_suggested_fix(finding),
            )
            for finding in artifact_findings
            if finding.code in _LEVEL_2_CODES
        )
    return sorted(findings, key=_sort_key)


def check_level_4(contract: LayoutContract) -> list[LayoutFinding]:
    """Report missing, invalid, or non-exact framework version alignment."""

    current = contract.current_version
    if contract.version_status == "missing":
        configured = "unavailable"
        return [
            _finding(
                4,
                ".ai-team.toml",
                f"Configured framework version is missing ({configured}); current CLI version is {current!r}.",
                "Set [init].framework_version to the exact current CLI distribution version.",
            )
        ]
    if contract.version_status == "invalid":
        return [
            _finding(
                4,
                ".ai-team.toml",
                f"Configured framework version {contract.raw_configured_version!r} is invalid; current CLI version is {current!r}.",
                "Set [init].framework_version to a valid version string matching the current CLI exactly.",
            )
        ]
    if contract.configured_version != current:
        return [
            _finding(
                4,
                ".ai-team.toml",
                f"Configured framework version {contract.configured_version!r} does not exactly match current CLI version {current!r}.",
                "Reinitialize or update the scaffold and record the exact current CLI version.",
            )
        ]
    return []


def _sort_key(finding: LayoutFinding) -> tuple[int, str, str, str]:
    return finding.level, finding.path, finding.problem, finding.suggested_fix


def check_layout(
    repo: Path,
    *,
    current_version: str | None = None,
) -> list[LayoutFinding]:
    """Run implemented layout levels and return deterministic findings."""

    contract, findings = resolve_layout(repo, current_version=current_version)
    findings.extend(check_level_1(contract))
    findings.extend(check_level_4(contract))
    return sorted(findings, key=_sort_key)
