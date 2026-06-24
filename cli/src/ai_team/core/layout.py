"""Read-only resolution and validation of the AI-team repository layout."""

from __future__ import annotations

import importlib.metadata
import importlib.resources as resources
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_SUPPORTED_TOOLS = ("claude", "codex")
_DEFAULT_PROJECT_DIR = "project"
_VERSION_PATTERN = re.compile(
    r"[0-9]+(?:\.[0-9]+)*(?:[A-Za-z][A-Za-z0-9.-]*[0-9]?|[.+-][A-Za-z0-9.-]+)*"
)


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
    marker_status: Literal["valid", "missing", "invalid"] = field(
        default="valid", repr=False
    )
    version_status: Literal["valid", "missing", "invalid"] = field(
        default="valid", repr=False
    )


def _finding(
    level: int,
    path: str,
    problem: str,
    suggested_fix: str,
) -> LayoutFinding:
    return LayoutFinding(
        level=level,
        path=path,
        problem=problem,
        suggested_fix=suggested_fix,
    )


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
    marker_status: Literal["valid", "missing", "invalid"] = "valid"
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

    version_status: Literal["valid", "missing", "invalid"] = "valid"
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
            marker_status=marker_status,
            version_status=version_status,
        ),
        sorted(findings, key=_sort_key),
    )


def _resource_directories(root: object) -> list[Path]:
    """Return directory paths below an importlib Traversable resource root."""

    directories: list[Path] = []

    def walk(node: object, relative: Path) -> None:
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


def _display_path(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def check_level_1(contract: LayoutContract) -> list[LayoutFinding]:
    """Report missing directories from current project and selected-tool scaffolds."""

    findings = []
    for path in _expected_directories(contract):
        if not path.is_dir():
            display_path = _display_path(path, contract.repo)
            findings.append(
                _finding(
                    1,
                    display_path,
                    f"Required scaffold directory '{display_path}' is missing.",
                    "Create the directory by restoring the current scaffold or rerunning 'ai-team init' with the configured tools.",
                )
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
                f"Configured framework version is invalid; current CLI version is {current!r}.",
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
    return (
        finding.level,
        finding.path,
        finding.problem,
        finding.suggested_fix,
    )


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
