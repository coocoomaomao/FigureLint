from pathlib import Path

from PIL import Image

from figurelint.checks import check_raster
from figurelint.models import Severity


def _save_image(path: Path, size=(1200, 800), dpi=None) -> None:
    image = Image.new("RGB", size, "white")
    kwargs = {}
    if dpi is not None:
        kwargs["dpi"] = dpi
    image.save(path, **kwargs)


def test_clean_png_with_300_dpi(tmp_path: Path) -> None:
    path = tmp_path / "figure.png"
    _save_image(path, dpi=(300, 300))

    findings = check_raster(path)

    assert not [f for f in findings if f.severity is Severity.ERROR]
    assert not [f for f in findings if f.severity is Severity.WARNING]


def test_missing_dpi_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.png"
    _save_image(path)

    findings = check_raster(path)

    assert any(f.code == "DPI_MISSING" for f in findings)


def test_low_dpi_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.png"
    _save_image(path, dpi=(150, 150))

    findings = check_raster(path)

    assert any(f.code == "DPI_LOW" for f in findings)


def test_small_dimension_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.png"
    _save_image(path, size=(500, 1000), dpi=(300, 300))

    findings = check_raster(path)

    assert any(f.code == "DIM_SMALL" for f in findings)
