"""
ai_team.core.lock — project-local mutual exclusion for artifact ID allocation.

Fixes B-014: concurrent ``ai-team task new`` (and ``bug new`` / ``spec new``)
processes previously scanned existing artifact files for the next ID and
wrote the new file with no mutual exclusion across the two steps, so two
processes could observe the same "next ID" and both write it.

Provides:
  - ``allocation_lock(project_dir, timeout=...)`` — a context manager that
    holds an exclusive, project-local lock for the duration of the block.
  - ``create_artifact_with_lock(project_dir, allocate_id=..., build=...)`` —
    the single shared helper that wraps "scan for the next ID, compute the
    destination, and write the artifact" in ``allocation_lock`` so that
    ``task new``, ``bug new``, and ``spec new`` all get the same
    mutual-exclusion guarantee from one implementation.
  - ``LockTimeout`` — raised when the lock cannot be acquired within the
    bounded wait.
"""

from __future__ import annotations

import fcntl
import os
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from ai_team.core.fs import write_artifact
from ai_team.core.models import Adr, Bug, ChangeRequest, Spec, Task

_LOCK_FILENAME = ".ai-team.lock"
_DEFAULT_TIMEOUT_SECONDS = 10.0
_POLL_INTERVAL_SECONDS = 0.05


class LockTimeout(RuntimeError):
    """Raised when the project allocation lock cannot be acquired in time."""


@contextmanager
def allocation_lock(
    project_dir: Path, *, timeout: float = _DEFAULT_TIMEOUT_SECONDS
) -> Iterator[None]:
    """Hold an exclusive, project-local lock for the duration of the ``with`` block.

    Concurrent ``ai-team`` processes that allocate a new artifact ID must wrap
    the "scan existing files for the next ID, then write the new file"
    sequence in this lock so that no two processes ever observe the same
    "next ID" before either has written its file.

    Staleness and bounded wait
    ---------------------------
    This uses ``fcntl.flock`` on a sentinel file
    (``<project_dir>/.ai-team.lock``) rather than a create-exclusive lockfile
    convention. ``flock`` locks belong to the *open file description*, not to
    the file's mere existence on disk, so the kernel releases the lock
    automatically the moment the holding process's file descriptor is closed
    — including on a crash or ``kill -9``. There is no stale-lock file to
    detect or clean up by hand; the sentinel file itself is harmless to leave
    on disk between runs.

    Acquisition polls with ``LOCK_EX | LOCK_NB`` on a bounded retry loop
    instead of blocking indefinitely, so a genuinely wedged or slow holder
    cannot hang callers forever: after *timeout* seconds of contention,
    :class:`LockTimeout` is raised naming the lock path.

    Parameters
    ----------
    project_dir:
        The project's top-level artifact directory. The lock's sentinel file
        is created directly under it, guarding ID allocation for every
        artifact kind in the project with a single lock.
    timeout:
        Maximum time in seconds to wait for the lock before raising
        :class:`LockTimeout`.

    Raises
    ------
    LockTimeout
        When the lock is still held by another process after *timeout*
        seconds.
    """
    project_dir.mkdir(parents=True, exist_ok=True)
    lock_path = project_dir / _LOCK_FILENAME
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise LockTimeout(
                        f"Could not acquire the project allocation lock at "
                        f"{lock_path!s} within {timeout} seconds; another "
                        "ai-team process appears to be holding it."
                    ) from None
                time.sleep(_POLL_INTERVAL_SECONDS)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def create_artifact_with_lock(
    project_dir: Path,
    *,
    allocate_id: Callable[[], str],
    build: Callable[[str], tuple[Path, Task | Bug | Spec | Adr | ChangeRequest, str]],
    timeout: float = _DEFAULT_TIMEOUT_SECONDS,
) -> tuple[str, Path]:
    """Allocate a new artifact ID and write its file in one locked critical section.

    This is the single shared implementation of "scan existing artifacts for
    the next ID, compute the destination path, and write the new file" used
    by ``task new``, ``bug new``, and ``spec new``. Wrapping all three steps
    in :func:`allocation_lock` closes the TOCTOU race diagnosed in B-014:
    concurrent processes can no longer both scan before either writes.

    Parameters
    ----------
    project_dir:
        The project's top-level artifact directory; see :func:`allocation_lock`.
    allocate_id:
        Zero-argument callable that scans existing artifacts and returns the
        next ID. Called exactly once, inside the lock.
    build:
        Callable that receives the allocated ID and returns
        ``(destination_path, model, body)`` ready for ``write_artifact``.
        Called exactly once, inside the lock, immediately after *allocate_id*.
    timeout:
        Maximum time in seconds to wait for the lock; see :func:`allocation_lock`.

    Returns
    -------
    tuple[str, Path]
        The allocated ID and the path the artifact was written to.

    Raises
    ------
    LockTimeout
        When the lock cannot be acquired within *timeout* seconds.
    ArtifactExists
        When *build*'s destination path already exists (propagated from
        ``write_artifact``).
    """
    with allocation_lock(project_dir, timeout=timeout):
        artifact_id = allocate_id()
        dest, model, body = build(artifact_id)
        write_artifact(dest, model, body, overwrite=False)
    return artifact_id, dest
