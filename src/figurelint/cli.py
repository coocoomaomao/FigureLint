from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .checks import check_raster, collect_figure_files
from .models import Severity

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
        help="Image file or directory to inspect.",
    ),
    min_dpi: int = typer.Option(
        300,
        "--min-dpi",
        min=1,
        help="Warn when reported DPI is below this value.",
    ),
    min_short_side: int = typer.Option(
        600,
        "--min-short-side",
        min=1,
        help="Warn when the shorter raster dimension is below this many pixels.",
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
        console.print("[yellow]No supported PNG/JPEG figures found.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title="FigureLint")
    table.add_column("File", overflow="fold")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("Message", overflow="fold")

    error_count = 0
    warning_count = 0

    for path in files:
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
