from pathlib import Path

from figurelint.models import Severity
from figurelint.svg_checks import check_svg


def _write_svg(
    path: Path,
    body: str,
    *,
    width: str = "400pt",
    height: str = "300pt",
) -> None:
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 400 300">{body}</svg>',
        encoding="utf-8",
    )


def test_clean_svg_has_no_warning_or_error(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<text x="20" y="30" font-size="10pt">Axis label</text>'
        '<path d="M 0 0 L 10 10" stroke="#000" stroke-width="1pt" '
        'fill="none"/>',
    )

    findings = check_svg(path)

    assert not [
        f for f in findings if f.severity in {Severity.WARNING, Severity.ERROR}
    ]


def test_small_font_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<text x="20" y="30" style="font-size:6pt">Tiny label</text>',
    )

    findings = check_svg(path)

    assert any(f.code == "SVG_FONT_SMALL" for f in findings)


def test_simple_css_class_font_size_is_resolved(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<style>.label { font-size: 6pt; }</style>'
        '<text class="label" x="20" y="30">Tiny label</text>',
    )

    findings = check_svg(path)

    assert any(f.code == "SVG_FONT_SMALL" for f in findings)


def test_thin_stroke_is_warning(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<path d="M 0 0 L 10 10" stroke="#000" stroke-width="0.3pt" '
        'fill="none"/>',
    )

    findings = check_svg(path)

    assert any(f.code == "SVG_STROKE_THIN" for f in findings)


def test_unitless_stroke_uses_viewbox_scale(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<path d="M 0 0 L 10 10" stroke="#000" stroke-width="0.4" '
        'fill="none"/>',
    )

    findings = check_svg(path)

    assert any(f.code == "SVG_STROKE_THIN" for f in findings)


def test_no_text_is_informational(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(path, '<path d="M 0 0 L 10 10" fill="#000"/>')

    findings = check_svg(path)

    finding = next(f for f in findings if f.code == "SVG_NO_EDITABLE_TEXT")
    assert finding.severity is Severity.INFO


def test_unresolved_relative_font_size_is_informational(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<text x="20" y="30" font-size="0.8em">Label</text>',
    )

    findings = check_svg(path)

    assert any(f.code == "SVG_FONT_SIZE_UNKNOWN" for f in findings)


def test_malformed_svg_is_error(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text("<svg><text></svg>", encoding="utf-8")

    findings = check_svg(path)

    finding = next(f for f in findings if f.code == "SVG_UNREADABLE")
    assert finding.severity is Severity.ERROR


def test_percentage_viewport_does_not_guess_unitless_stroke_size(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" '
        'viewBox="0 0 400 300">'
        '<path d="M 0 0 L 10 10" stroke="#000" stroke-width="0.1" fill="none"/>'
        '</svg>',
        encoding="utf-8",
    )

    findings = check_svg(path)

    assert not any(f.code == "SVG_STROKE_THIN" for f in findings)


def test_large_font_is_warning_when_maximum_enabled(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<text x="20" y="30" font-size="8pt">Large label</text>',
    )

    findings = check_svg(path, min_font_size_pt=None, max_font_size_pt=7.0)

    assert any(f.code == "SVG_FONT_LARGE" for f in findings)


def test_thick_stroke_is_warning_when_maximum_enabled(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<path d="M 0 0 L 10 10" stroke="#000" stroke-width="1.2pt" '
        'fill="none"/>',
    )

    findings = check_svg(
        path,
        min_stroke_width_pt=None,
        max_stroke_width_pt=1.0,
    )

    assert any(f.code == "SVG_STROKE_THICK" for f in findings)


def test_exact_upper_bounds_do_not_warn(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    _write_svg(
        path,
        '<text x="20" y="30" font-size="7pt">Boundary label</text>'
        '<path d="M 0 0 L 10 10" stroke="#000" stroke-width="1pt" '
        'fill="none"/>',
    )

    findings = check_svg(
        path,
        min_font_size_pt=5.0,
        max_font_size_pt=7.0,
        min_stroke_width_pt=0.25,
        max_stroke_width_pt=1.0,
    )

    assert not any(f.code in {"SVG_FONT_LARGE", "SVG_STROKE_THICK"} for f in findings)
