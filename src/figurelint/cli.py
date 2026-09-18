from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .checks import check_raster, collect_figure_files
from .models import Severity
from .svg_checks import check_svg

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Lint academic figures before submission.",
)
console = Console()


@app.command()
def check(
    target: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Figure file or directory to inspect.",
    ),
    min_dpi: int = typer.Option(
        300,
        "--min-dpi",
        min=1,
        help="Warn when reported raster DPI is below this value.",
    ),
    min_short_side: int = typer.Option(
        600,
        "--min-short-side",
        min=1,
        help="Warn when the shorter raster dimension is below this many pixels.",
    ),
    min_font_size_pt: float = typer.Option(
        7.0,
        "--min-font-size-pt",
        min=0.1,
        help="Warn when a resolvable SVG text size is below this many points.",
    ),
    min_stroke_width_pt: float = typer.Option(
        0.5,
        "--min-stroke-width-pt",
        min=0.01,
        help="Warn when a resolvable SVG stroke width is below this many points.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit with code 1 when warnings are present.",
    ),
) -> None:
    """Check one figure or every supported figure in a directory."""
    files = collect_figure_files(target)

    if not files:
        console.print("[yellow]No supported PNG/JPEG/SVG figures found.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title="FigureLint")
    table.add_column("File", overflow="fold")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("Message", overflow="fold")

    error_count = 0
    warning_count = 0

    for path in files:
        if path.suffix.lower() == ".svg":
            findings = check_svg(
                path,
                min_font_size_pt=min_font_size_pt,
                min_stroke_width_pt=min_stroke_width_pt,
            )
        else:
            findings = check_raster(
                path,
                min_dpi=min_dpi,
                min_short_side=min_short_side,
            )

        if not findings:
            table.add_row(str(path), "pass", "OK", "No findings.")
            continue

        for finding in findings:
            if finding.severity is Severity.ERROR:
                error_count += 1
            elif finding.severity is Severity.WARNING:
                warning_count += 1

            table.add_row(
                str(finding.path),
                finding.severity.value,
                finding.code,
                finding.message,
            )

    console.print(table)
    console.print(
        f"Checked {len(files)} file(s): "
        f"{error_count} error(s), {warning_count} warning(s)."
    )

    if error_count:
        raise typer.Exit(code=2)
    if strict and warning_count:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
