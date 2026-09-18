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
    table.add_column("Name", no_wrap=True)
    table.add_column("Purpose", overflow="fold")
    table.add_column("DPI", justify="right")
    table.add_column("Raster min", justify="right")
    table.add_column("SVG font", justify="right")
    table.add_column("SVG stroke", justify="right")
    table.add_column("Provenance")

    def show(value: int | float | None, unit: str = "") -> str:
        if value is None:
            return "—"
        if isinstance(value, float):
            return f"{value:g}{unit}"
        return f"{value}{unit}"

    for name in available_preset_names():
        preset = get_preset(name)
        thresholds = preset.thresholds
        provenance = (
            preset.source_name
            if preset.is_publisher_verified
            else "FigureLint convenience preset"
        )
        font_range = (
            f"{show(thresholds.min_font_size_pt)}–{show(thresholds.max_font_size_pt)}pt"
            if thresholds.max_font_size_pt is not None
            else show(thresholds.min_font_size_pt, "pt")
        )
        stroke_range = (
            f"{show(thresholds.min_stroke_width_pt)}–{show(thresholds.max_stroke_width_pt)}pt"
            if thresholds.max_stroke_width_pt is not None
            else show(thresholds.min_stroke_width_pt, "pt")
        )
        table.add_row(
            preset.name,
            preset.description,
            show(thresholds.min_dpi),
            show(thresholds.min_short_side, "px"),
            font_range,
            stroke_range,
            provenance,
        )

    console.print(table)
    console.print(
        "[dim]Names: " + ", ".join(available_preset_names()) + "[/dim]"
    )
    console.print(
        "[dim]Convenience presets are not publisher policies. "
        "Source-verified publisher presets show official source metadata.[/dim]"
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
    max_font_size_pt: Optional[float] = typer.Option(
        None,
        "--max-font-size-pt",
        min=0.1,
        help="Override the preset maximum resolvable SVG font size in points.",
    ),
    min_stroke_width_pt: Optional[float] = typer.Option(
        None,
        "--min-stroke-width-pt",
        min=0.01,
        help="Override the preset minimum resolvable SVG stroke width in points.",
    ),
    max_stroke_width_pt: Optional[float] = typer.Option(
        None,
        "--max-stroke-width-pt",
        min=0.01,
        help="Override the preset maximum resolvable SVG stroke width in points.",
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
            max_font_size_pt=max_font_size_pt,
            min_stroke_width_pt=min_stroke_width_pt,
            max_stroke_width_pt=max_stroke_width_pt,
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
        max_font_size_pt,
        min_stroke_width_pt,
        max_stroke_width_pt,
        min_pdf_short_side_in,
        max_pdf_long_side_in,
    )
    override_suffix = (
        " + CLI overrides"
        if any(value is not None for value in override_values)
        else ""
    )
    console.print(f"[dim]Preset: {active_preset.name}{override_suffix}[/dim]")
    if active_preset.is_publisher_verified and active_preset.source_url:
        console.print(f"[dim]Official source: {active_preset.source_url}[/dim]")

    table = Table(title="FigureLint")
    table.add_column("File", overflow="fold")
    table.add_column("Severity")
    table.add_column("Code", min_width=26, no_wrap=True)
    table.add_column("Message", overflow="fold")

    error_count = 0
    warning_count = 0

    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".svg":
            svg_policy = active_preset.svg_policy
            findings = check_svg(
                path,
                min_font_size_pt=thresholds.min_font_size_pt,
                max_font_size_pt=thresholds.max_font_size_pt,
                min_stroke_width_pt=thresholds.min_stroke_width_pt,
                max_stroke_width_pt=thresholds.max_stroke_width_pt,
                panel_label_size_pt=(
                    svg_policy.panel_label_size_pt if svg_policy else None
                ),
                panel_label_require_bold=(
                    svg_policy.panel_label_require_bold if svg_policy else False
                ),
                panel_label_require_upright=(
                    svg_policy.panel_label_require_upright if svg_policy else False
                ),
                preferred_font_families=(
                    svg_policy.preferred_font_families if svg_policy else ()
                ),
                require_consistent_font_family=(
                    svg_policy.require_consistent_font_family
                    if svg_policy
                    else False
                ),
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
