from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .models import Finding, Severity

SUPPORTED_RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SUPPORTED_VECTOR_EXTENSIONS = {".svg", ".pdf"}
SUPPORTED_EXTENSIONS = SUPPORTED_RASTER_EXTENSIONS | SUPPORTED_VECTOR_EXTENSIONS


def collect_figure_files(target: Path) -> list[Path]:
    """Return supported figure files under target."""
    if target.is_file():
        return [target] if target.suffix.lower() in SUPPORTED_EXTENSIONS else []

    if target.is_dir():
        return sorted(
            p
            for p in target.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    return []


def _extract_dpi(image: Image.Image) -> tuple[float, float] | None:
    raw = image.info.get("dpi")
    if not raw:
        return None

    try:
        x, y = raw
        return float(x), float(y)
    except (TypeError, ValueError):
        return None


def check_raster(
    path: Path,
    *,
    min_dpi: int = 300,
    min_short_side: int = 600,
) -> list[Finding]:
    """Inspect one raster image and return technical findings."""
    findings: list[Finding] = []

    try:
        with Image.open(path) as image:
            image.verify()

        with Image.open(path) as image:
            width, height = image.size
            mode = image.mode
            dpi = _extract_dpi(image)
            bands = image.getbands()

    except (UnidentifiedImageError, OSError) as exc:
        return [
            Finding(
                path=path,
                severity=Severity.ERROR,
                code="IMAGE_UNREADABLE",
                message=f"Image could not be read: {exc}",
            )
        ]

    if min(width, height) < min_short_side:
        findings.append(
            Finding(
                path=path,
                severity=Severity.WARNING,
                code="DIM_SMALL",
                message=(
                    f"Short side is {min(width, height)} px; "
                    f"configured minimum is {min_short_side} px."
                ),
            )
        )

    if dpi is None:
        findings.append(
            Finding(
                path=path,
                severity=Severity.WARNING,
                code="DPI_MISSING",
                message=(
                    "No DPI metadata was found. Pixel dimensions may still be adequate, "
                    "but submission systems can rely on DPI metadata."
                ),
            )
        )
    # PNG stores DPI through pixels-per-metre metadata, which can round a
    # requested 300 DPI to values such as 299.9994 on read-back.
    elif min(dpi) < min_dpi - 0.5:
        findings.append(
            Finding(
                path=path,
                severity=Severity.WARNING,
                code="DPI_LOW",
                message=(
                    f"Reported DPI is {dpi[0]:.0f}×{dpi[1]:.0f}; "
                    f"configured minimum is {min_dpi} DPI."
                ),
            )
        )

    if "A" in bands or mode in {"LA", "PA"}:
        findings.append(
            Finding(
                path=path,
                severity=Severity.INFO,
                code="ALPHA_CHANNEL",
                message=(
                    "Image contains transparency. Some publication workflows require "
                    "flattened output."
                ),
            )
        )

    if path.suffix.lower() in {".jpg", ".jpeg"}:
        findings.append(
            Finding(
                path=path,
                severity=Severity.INFO,
                code="JPEG_LOSSY",
                message=(
                    "JPEG uses lossy compression. For line art or text-heavy figures, "
                    "PNG or a vector format is often preferable."
                ),
            )
        )

    return findings
