"""Tests that `init` copies non-UTF-8 scaffold files byte for byte."""

from __future__ import annotations

from pathlib import Path

from ai_team.commands.init import _write_rendered

SETTINGS = {"project_dir": "custom-dir", "integration_branch": "develop"}
PNG_LIKE_BYTES = b"\x89PNG\r\n\x1a\n\x00\xff\xfe{{project_dir}}\x80\x81"


def test_writes_non_utf8_file_byte_for_byte(tmp_path: Path) -> None:
    source = tmp_path / "image.png"
    source.write_bytes(PNG_LIKE_BYTES)
    destination = tmp_path / "out" / "image.png"

    _write_rendered(source, destination, SETTINGS)

    assert destination.read_bytes() == PNG_LIKE_BYTES


def test_does_not_raise_unicode_error_for_invalid_utf8(tmp_path: Path) -> None:
    source = tmp_path / "broken.bin"
    source.write_bytes(b"\xff\xfe\x00")
    destination = tmp_path / "broken-copy.bin"

    _write_rendered(source, destination, SETTINGS)

    assert destination.exists()


def test_replaces_both_placeholders_in_utf8_file(tmp_path: Path) -> None:
    source = tmp_path / "doc.md"
    source.write_text(
        "dir={{project_dir}} branch={{integration_branch}} café\n", encoding="utf-8"
    )
    destination = tmp_path / "doc-copy.md"

    _write_rendered(source, destination, SETTINGS)

    assert (
        destination.read_text(encoding="utf-8")
        == "dir=custom-dir branch=develop café\n"
    )
