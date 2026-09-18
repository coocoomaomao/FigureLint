from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pymupdf
from PIL import Image

from figurelint.models import Severity
from figurelint.pdf_checks import check_pdf


def _save_pdf(
    path: Path,
    *,
    pages: int = 1,
    width: float = 360,
    height: float = 240,
    text: str | None = None,
) -> None:
    document = pymupdf.open()
    for _ in range(pages):
        page = document.new_page(width=width, height=height)
        if text:
            page.insert_text((36, 72), text, fontsize=12, fontname="helv")
    document.save(path)
    document.close()


def _png_bytes(
    *,
    size: tuple[int, int],
    mode: str = "RGB",
) -> bytes:
    buffer = BytesIO()
    if mode == "RGBA":
        image = Image.new(mode, size, (44, 177, 161, 128))
    else:
        image = Image.new(mode, size, "white")
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_clean_single_page_vector_pdf_has_no_warning_or_error(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    _save_pdf(path)

    findings = check_pdf(path)

    assert not [
        finding
        for finding in findings
        if finding.severity in {Severity.WARNING, Severity.ERROR}
    ]
    assert any(finding.code == "PDF_NO_EDITABLE_TEXT" for finding in findings)


def test_multi_page_pdf_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    _save_pdf(path, pages=2)

    findings = check_pdf(path)

    assert any(finding.code == "PDF_MULTI_PAGE" for finding in findings)


def test_small_page_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    _save_pdf(path, width=36, height=36)

    findings = check_pdf(path)

    assert any(finding.code == "PDF_PAGE_SMALL" for finding in findings)


def test_large_page_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    _save_pdf(path, width=1800, height=720)

    findings = check_pdf(path)

    assert any(finding.code == "PDF_PAGE_LARGE" for finding in findings)


def test_builtin_font_is_reported_as_not_embedded(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    _save_pdf(path, text="Editable axis label")

    findings = check_pdf(path)

    assert any(finding.code == "PDF_FONT_NOT_EMBEDDED" for finding in findings)
    assert not any(finding.code == "PDF_NO_EDITABLE_TEXT" for finding in findings)


def test_low_effective_image_dpi_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    document = pymupdf.open()
    page = document.new_page(width=360, height=240)
    page.insert_image(
        pymupdf.Rect(36, 36, 180, 180),
        stream=_png_bytes(size=(100, 100)),
    )
    document.save(path)
    document.close()

    findings = check_pdf(path)

    warning = next(
        finding for finding in findings if finding.code == "PDF_IMAGE_LOW_DPI"
    )
    assert warning.severity is Severity.WARNING
    assert "50.0 DPI" in warning.message


def test_300_dpi_image_does_not_warn(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    document = pymupdf.open()
    page = document.new_page(width=360, height=240)
    page.insert_image(
        pymupdf.Rect(36, 36, 180, 180),
        stream=_png_bytes(size=(600, 600)),
    )
    document.save(path)
    document.close()

    findings = check_pdf(path)

    assert not any(finding.code == "PDF_IMAGE_LOW_DPI" for finding in findings)


def test_raster_alpha_soft_mask_is_informational(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    document = pymupdf.open()
    page = document.new_page(width=360, height=240)
    page.insert_image(
        pymupdf.Rect(36, 36, 108, 108),
        stream=_png_bytes(size=(100, 100), mode="RGBA"),
    )
    document.save(path)
    document.close()

    findings = check_pdf(path)

    finding = next(
        finding for finding in findings if finding.code == "PDF_IMAGE_SOFT_MASK"
    )
    assert finding.severity is Severity.INFO


def test_malformed_pdf_is_error(tmp_path: Path) -> None:
    path = tmp_path / "figure.pdf"
    path.write_bytes(b"this is not a pdf")

    findings = check_pdf(path)

    finding = next(finding for finding in findings if finding.code == "PDF_UNREADABLE")
    assert finding.severity is Severity.ERROR
