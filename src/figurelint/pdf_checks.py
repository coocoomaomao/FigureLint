from __future__ import annotations

from pathlib import Path

import pymupdf

from .models import Finding, Severity


def _font_display_name(font: tuple) -> str:
    """Return the most useful name from a PyMuPDF font tuple."""
    for index in (3, 4):
        if len(font) > index and font[index]:
            return str(font[index])
    return "unknown-font"


def _font_is_embedded(document: pymupdf.Document, xref: int) -> bool | None:
    """Return True/False when embedding can be determined, else None."""
    if xref <= 0:
        return False

    try:
        extracted = document.extract_font(xref)
    except (RuntimeError, ValueError):
        return None

    if not extracted or len(extracted) < 4:
        return None

    content = extracted[3]
    if content is None:
        return False

    try:
        return len(content) > 0
    except TypeError:
        return None


def _image_effective_dpi(
    page: pymupdf.Page,
    *,
    xref: int,
    pixel_width: int,
    pixel_height: int,
) -> list[float]:
    """Return effective DPI values for visible placements of one image."""
    try:
        rects = page.get_image_rects(xref)
    except (RuntimeError, ValueError):
        return []

    values: list[float] = []
    for rect in rects:
        width_pt = abs(float(rect.width))
        height_pt = abs(float(rect.height))
        if width_pt <= 0 or height_pt <= 0:
            continue

        dpi_x = pixel_width * 72.0 / width_pt
        dpi_y = pixel_height * 72.0 / height_pt
        values.append(min(dpi_x, dpi_y))

    return values


def check_pdf(
    path: Path,
    *,
    min_image_dpi: int | None = 300,
    min_page_short_side_in: float | None = 1.0,
    max_page_long_side_in: float | None = 20.0,
) -> list[Finding]:
    """Inspect one PDF figure and return deterministic technical findings."""
    try:
        document = pymupdf.open(path)
    except (pymupdf.FileDataError, RuntimeError, ValueError, OSError) as exc:
        return [
            Finding(
                path=path,
                severity=Severity.ERROR,
                code="PDF_UNREADABLE",
                message=f"PDF could not be opened: {exc}",
            )
        ]

    try:
        if document.needs_pass:
            return [
                Finding(
                    path=path,
                    severity=Severity.ERROR,
                    code="PDF_ENCRYPTED",
                    message="PDF is password-protected and cannot be inspected.",
                )
            ]

        if document.page_count == 0:
            return [
                Finding(
                    path=path,
                    severity=Severity.ERROR,
                    code="PDF_NO_PAGES",
                    message="PDF contains no pages.",
                )
            ]

        findings: list[Finding] = []

        if document.page_count > 1:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="PDF_MULTI_PAGE",
                    message=(
                        f"PDF contains {document.page_count} pages. A standalone academic "
                        "figure is commonly exported as a single page."
                    ),
                )
            )

        min_short_side_pt = (
            min_page_short_side_in * 72.0
            if min_page_short_side_in is not None
            else None
        )
        max_long_side_pt = (
            max_page_long_side_in * 72.0
            if max_page_long_side_in is not None
            else None
        )

        too_small_pages: list[float] = []
        too_large_pages: list[float] = []
        editable_word_count = 0
        unembedded_fonts: set[str] = set()
        unresolved_fonts: set[str] = set()
        low_dpi_values: list[float] = []
        soft_mask_images = 0
        seen_font_xrefs: set[int] = set()

        for page in document:
            width_pt = abs(float(page.rect.width))
            height_pt = abs(float(page.rect.height))
            short_side_pt = min(width_pt, height_pt)
            long_side_pt = max(width_pt, height_pt)

            if min_short_side_pt is not None and short_side_pt < min_short_side_pt:
                too_small_pages.append(short_side_pt / 72.0)
            if max_long_side_pt is not None and long_side_pt > max_long_side_pt:
                too_large_pages.append(long_side_pt / 72.0)

            try:
                editable_word_count += len(page.get_text("words"))
            except (RuntimeError, ValueError):
                pass

            try:
                page_fonts = page.get_fonts(full=True)
            except (RuntimeError, ValueError):
                page_fonts = []

            for font in page_fonts:
                if not font:
                    continue

                try:
                    xref = int(font[0])
                except (TypeError, ValueError, IndexError):
                    continue

                if xref in seen_font_xrefs:
                    continue
                seen_font_xrefs.add(xref)

                name = _font_display_name(font)
                embedded = _font_is_embedded(document, xref)
                if embedded is False:
                    unembedded_fonts.add(name)
                elif embedded is None:
                    unresolved_fonts.add(name)

            try:
                images = page.get_images(full=True)
            except (RuntimeError, ValueError):
                images = []

            for image in images:
                if len(image) < 4:
                    continue

                try:
                    xref = int(image[0])
                    smask = int(image[1])
                    pixel_width = int(image[2])
                    pixel_height = int(image[3])
                except (TypeError, ValueError):
                    continue

                if smask > 0:
                    soft_mask_images += 1

                if min_image_dpi is not None:
                    low_dpi_values.extend(
                        dpi
                        for dpi in _image_effective_dpi(
                            page,
                            xref=xref,
                            pixel_width=pixel_width,
                            pixel_height=pixel_height,
                        )
                        if dpi < min_image_dpi - 0.5
                    )

        if too_small_pages and min_page_short_side_in is not None:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="PDF_PAGE_SMALL",
                    message=(
                        f"Found {len(too_small_pages)} page(s) with a short side below "
                        f"{min_page_short_side_in:g} in; smallest is "
                        f"{min(too_small_pages):.2f} in."
                    ),
                )
            )

        if too_large_pages and max_page_long_side_in is not None:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="PDF_PAGE_LARGE",
                    message=(
                        f"Found {len(too_large_pages)} page(s) with a long side above "
                        f"{max_page_long_side_in:g} in; largest is "
                        f"{max(too_large_pages):.2f} in."
                    ),
                )
            )

        if editable_word_count == 0:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.INFO,
                    code="PDF_NO_EDITABLE_TEXT",
                    message=(
                        "No editable text words were detected. Text may have been "
                        "converted to outlines/paths, or the figure may contain no text."
                    ),
                )
            )

        if unembedded_fonts:
            names = ", ".join(sorted(unembedded_fonts)[:6])
            extra = ""
            if len(unembedded_fonts) > 6:
                extra = f" (+{len(unembedded_fonts) - 6} more)"
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="PDF_FONT_NOT_EMBEDDED",
                    message=(
                        f"Detected {len(unembedded_fonts)} font(s) without an embedded "
                        f"font program: {names}{extra}."
                    ),
                )
            )

        if unresolved_fonts:
            names = ", ".join(sorted(unresolved_fonts)[:6])
            extra = ""
            if len(unresolved_fonts) > 6:
                extra = f" (+{len(unresolved_fonts) - 6} more)"
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.INFO,
                    code="PDF_FONT_EMBEDDING_UNKNOWN",
                    message=(
                        "Could not determine embedding status for "
                        f"{len(unresolved_fonts)} font(s): {names}{extra}."
                    ),
                )
            )

        if low_dpi_values and min_image_dpi is not None:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="PDF_IMAGE_LOW_DPI",
                    message=(
                        f"Found {len(low_dpi_values)} embedded image placement(s) below "
                        f"{min_image_dpi} DPI; lowest effective resolution is "
                        f"{min(low_dpi_values):.1f} DPI."
                    ),
                )
            )

        if soft_mask_images:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.INFO,
                    code="PDF_IMAGE_SOFT_MASK",
                    message=(
                        f"Found {soft_mask_images} embedded raster image(s) using a soft "
                        "mask / alpha channel. Some publication workflows may flatten "
                        "transparency."
                    ),
                )
            )

        return findings
    finally:
        document.close()
