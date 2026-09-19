from pathlib import Path

from typer.testing import CliRunner

from figurelint.cli import app
from figurelint.github_annotations import format_github_annotation
from figurelint.models import Finding, Severity

runner = CliRunner()


def test_warning_annotation_escapes_message() -> None:
    finding = Finding(
        path=Path("figures/figure.svg"),
        severity=Severity.WARNING,
        code="SVG_FONT_SMALL",
        message="Too small\n50% of labels",
    )

    annotation = format_github_annotation(finding)

    assert annotation.startswith(
        "::warning file=figures/figure.svg,title=SVG_FONT_SMALL::"
    )
    assert "Too small%0A50%25 of labels" in annotation


def test_error_and_info_map_to_github_levels() -> None:
    error = Finding(
        path=Path("figure.pdf"),
        severity=Severity.ERROR,
        code="PDF_UNREADABLE",
        message="Cannot parse",
    )
    info = Finding(
        path=Path("figure.svg"),
        severity=Severity.INFO,
        code="SVG_NO_EDITABLE_TEXT",
        message="No text",
    )

    assert format_github_annotation(error).startswith("::error ")
    assert format_github_annotation(info).startswith("::notice ")


def test_cli_can_emit_github_annotations(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="4pt">Tiny label</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["check", str(path), "--github-annotations"],
    )

    assert result.exit_code == 0
    assert "::warning file=" in result.stdout
    assert "title=SVG_FONT_SMALL::" in result.stdout
