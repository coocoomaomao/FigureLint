from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .checks import check_raster, collect_figure_files
from .models import Severity
from .pdf_checks import check_pdf
from .presets import available_preset_names, get_preset, resolve_thresholds
from .svg_checks import check_svg

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Lint academic figures before submission.",
)
console = Console()


@app.command("presets")
def list_presets() -> None:
    """List built-in FigureLint presets."""
    table = Table(title="FigureLint presets")
    table.add_column("Name")
    table.add_column("Purpose", overflow="fold")
    table.add_column("DPI", justify="right")
    table.add_column("Raster min", justify="right")
    table.add_column("SVG font", justify="right")
    table.add_column("SVG stroke", justify="right")
    table.add_column("Provenance")

    for name in available_preset_names():
        preset = get_preset(name)
        thresholds = preset.thresholds
        provenance = (
            preset.source_name
            if preset.is_publisher_verified
            else "FigureLint convenience preset"
        )
        table.add_row(
            preset.name,
            preset.description,
            str(thresholds.min_dpi),
            f"{thresholds.min_short_side}px",
            f"{thresholds.min_font_size_pt:g}pt",
            f"{thresholds.min_stroke_width_pt:g}pt",
            provenance,
        )

    console.print(table)
    console.print(
        "[dim]Convenience presets are not publisher policies. "
        "Future verified journal presets will include official source metadata.[/dim]"
    )


@app.command()
def check(
    target: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Figure file or directory to inspect.",
    ),
    preset: str = typer.Option(
        "default",
        "--preset",
        help="Named threshold preset. Run 'figurelint presets' to list profiles.",
    ),
    min_dpi: Optional[int] = typer.Option(
        None,
        "--min-dpi",
        min=1,
        help="Override the preset minimum raster/effective PDF image DPI.",
    ),
    min_short_side: Optional[int] = typer.Option(
        None,
        "--min-short-side",
        min=1,
        help="Override the preset minimum raster short side in pixels.",
    ),
    min_font_size_pt: Optional[float] = typer.Option(
        None,
        "--min-font-size-pt",
        min=0.1,
        help="Override the preset minimum resolvable SVG font size in points.",
    ),
    min_stroke_width_pt: Optional[float] = typer.Option(
        None,
        "--min-stroke-width-pt",
        min=0.01,
        help="Override the preset minimum resolvable SVG stroke width in points.",
    ),
    min_pdf_short_side_in: Optional[float] = typer.Option(
        None,
        "--min-pdf-short-side-in",
        min=0.01,
        help="Override the preset minimum PDF page short side in inches.",
    ),
    max_pdf_long_side_in: Optional[float] = typer.Option(
        None,
        "--max-pdf-long-side-in",
        min=0.1,
        help="Override the preset maximum PDF page long side in inches.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit with code 1 when warnings are present.",
    ),
) -> None:
    """Check one figure or every supported figure in a directory."""
    try:
        active_preset, thresholds = resolve_thresholds(
            preset,
            min_dpi=min_dpi,
            min_short_side=min_short_side,
            min_font_size_pt=min_font_size_pt,
            min_stroke_width_pt=min_stroke_width_pt,
            min_pdf_short_side_in=min_pdf_short_side_in,
            max_pdf_long_side_in=max_pdf_long_side_in,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--preset") from exc

    files = collect_figure_files(target)

    if not files:
        console.print("[yellow]No supported PNG/JPEG/SVG/PDF figures found.[/yellow]")
        raise typer.Exit(code=0)

    override_values = (
        min_dpi,
        min_short_side,
        min_font_size_pt,
        min_stroke_width_pt,
        min_pdf_short_side_in,
        max_pdf_long_side_in,
    )
    override_suffix = (
        " + CLI overrides"
        if any(value is not None for value in override_values)
        else ""
    )
    console.print(f"[dim]Preset: {active_preset.name}{override_suffix}[/dim]")

    table = Table(title="FigureLint")
    table.add_column("File", overflow="fold")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("Message", overflow="fold")

    error_count = 0
    warning_count = 0

    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".svg":
            findings = check_svg(
                path,
                min_font_size_pt=thresholds.min_font_size_pt,
                min_stroke_width_pt=thresholds.min_stroke_width_pt,
            )
        elif suffix == ".pdf":
            findings = check_pdf(
                path,
                min_image_dpi=thresholds.min_dpi,
                min_page_short_side_in=thresholds.min_pdf_short_side_in,
                max_page_long_side_in=thresholds.max_pdf_long_side_in,
            )
        else:
            findings = check_raster(
                path,
                min_dpi=thresholds.min_dpi,
                min_short_side=thresholds.min_short_side,
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
