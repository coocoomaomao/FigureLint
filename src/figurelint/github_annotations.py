from __future__ import annotations

from pathlib import Path

from .models import Finding, Severity


def _escape_data(value: str) -> str:
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def _escape_property(value: str) -> str:
    return (
        _escape_data(value)
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


def _annotation_level(severity: Severity) -> str:
    if severity is Severity.ERROR:
        return "error"
    if severity is Severity.WARNING:
        return "warning"
    return "notice"


def _annotation_path(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(Path.cwd().resolve())
        return relative.as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def format_github_annotation(finding: Finding) -> str:
    """Format a finding as a GitHub Actions workflow command."""
    level = _annotation_level(finding.severity)
    path = _escape_property(_annotation_path(finding.path))
    title = _escape_property(finding.code)
    message = _escape_data(finding.message)
    return f"::{level} file={path},title={title}::{message}"
