from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from figurelint.cli import app
from figurelint.presets import (
    available_preset_names,
    get_preset,
    resolve_thresholds,
)

runner = CliRunner()


def test_default_preset_preserves_legacy_thresholds() -> None:
    preset = get_preset("default")
    thresholds = preset.thresholds

    assert thresholds.min_dpi == 300
    assert thresholds.min_short_side == 600
    assert thresholds.min_font_size_pt == 7.0
    assert thresholds.max_font_size_pt is None
    assert thresholds.min_stroke_width_pt == 0.5
    assert thresholds.max_stroke_width_pt is None
    assert thresholds.min_pdf_short_side_in == 1.0
    assert thresholds.max_pdf_long_side_in == 20.0


def test_explicit_thresholds_override_preset_values() -> None:
    preset, thresholds = resolve_thresholds(
        "high-resolution",
        min_dpi=450,
        min_font_size_pt=9.0,
        max_font_size_pt=11.0,
    )

    assert preset.name == "high-resolution"
    assert thresholds.min_dpi == 450
    assert thresholds.min_font_size_pt == 9.0
    assert thresholds.max_font_size_pt == 11.0
    assert thresholds.min_short_side == 1200


def test_journal_alias_resolves_to_canonical_profile() -> None:
    preset = get_preset("journal")

    assert preset.name == "journal-generic"


def test_unknown_preset_has_useful_error() -> None:
    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset("does-not-exist")


def test_convenience_presets_are_not_publisher_verified() -> None:
    for name in ("default", "high-resolution", "presentation", "journal-generic"):
        assert not get_preset(name).is_publisher_verified


def test_convenience_thresholds_are_positive_and_page_range_is_valid() -> None:
    for name in ("default", "high-resolution", "presentation", "journal-generic"):
        thresholds = get_preset(name).thresholds
        assert thresholds.min_dpi is not None and thresholds.min_dpi > 0
        assert thresholds.min_short_side is not None and thresholds.min_short_side > 0
        assert (
            thresholds.min_font_size_pt is not None
            and thresholds.min_font_size_pt > 0
        )
        assert thresholds.max_font_size_pt is None
        assert (
            thresholds.min_stroke_width_pt is not None
            and thresholds.min_stroke_width_pt > 0
        )
        assert thresholds.max_stroke_width_pt is None
        assert (
            thresholds.min_pdf_short_side_in is not None
            and thresholds.min_pdf_short_side_in > 0
        )
        assert (
            thresholds.max_pdf_long_side_in is not None
            and thresholds.max_pdf_long_side_in > thresholds.min_pdf_short_side_in
        )


def test_nature_preset_has_verified_official_source_and_ranges() -> None:
    preset = get_preset("nature")
    thresholds = preset.thresholds

    assert preset.is_publisher_verified
    assert preset.source_name == "Nature — Final submission"
    assert preset.source_url == "https://www.nature.com/nature/for-authors/final-submission"
    assert set(preset.verified_fields) == {
        "min_dpi",
        "min_font_size_pt",
        "max_font_size_pt",
        "min_stroke_width_pt",
        "max_stroke_width_pt",
        "max_pdf_long_side_in",
    }
    assert thresholds.min_dpi == 300
    assert thresholds.min_short_side is None
    assert thresholds.min_font_size_pt == 5.0
    assert thresholds.max_font_size_pt == 7.0
    assert thresholds.min_stroke_width_pt == 0.25
    assert thresholds.max_stroke_width_pt == 1.0
    assert thresholds.min_pdf_short_side_in is None
    assert thresholds.max_pdf_long_side_in == pytest.approx(247.0 / 25.4)
    assert preset.svg_policy is not None
    assert preset.svg_policy.panel_label_size_pt == 8.0
    assert preset.svg_policy.panel_label_require_bold
    assert preset.svg_policy.panel_label_require_upright
    assert preset.svg_policy.preferred_font_families == ("Arial", "Helvetica")
    assert preset.svg_policy.require_consistent_font_family
    assert {
        "panel_label_8pt_bold_upright",
        "single_sans_serif_typeface",
        "prefer_arial_or_helvetica",
        "editable_text_not_outlines",
    }.issubset(set(preset.verified_rules))


def test_presets_command_lists_profiles_and_nature_ranges() -> None:
    result = runner.invoke(app, ["presets"])

    assert result.exit_code == 0
    assert "default" in result.stdout
    assert "high-resolution" in result.stdout
    assert "presentation" in result.stdout
    assert "journal-generic" in result.stdout
    assert "nature" in result.stdout
    assert "5–7pt" in result.stdout
    assert "0.25–1pt" in result.stdout
    assert "not publisher policies" in result.stdout


def test_cli_override_wins_over_selected_preset(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="9pt">Readable label</text>'
        '<path d="M0 0 L20 20" stroke="#000" stroke-width="1pt"/>'
        '</svg>',
        encoding="utf-8",
    )

    strict_preset = runner.invoke(
        app,
        ["check", str(path), "--preset", "presentation"],
    )
    overridden = runner.invoke(
        app,
        [
            "check",
            str(path),
            "--preset",
            "presentation",
            "--min-font-size-pt",
            "8",
        ],
    )

    assert strict_preset.exit_code == 0
    assert "SVG_FONT_SMALL" in strict_preset.stdout
    assert overridden.exit_code == 0
    assert "SVG_FONT_SMALL" not in overridden.stdout
    assert "CLI overrides" in overridden.stdout


def test_nature_cli_applies_sourced_minima(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="4.5pt">Tiny label</text>'
        '<path d="M0 0 L20 20" stroke="#000" stroke-width="0.2pt"/>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_SMALL" in result.stdout
    assert "SVG_STROKE_THIN" in result.stdout
    assert "Official source:" in result.stdout


def test_nature_cli_applies_sourced_maxima(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="8pt">Oversized label</text>'
        '<path d="M0 0 L20 20" stroke="#000" stroke-width="1.2pt"/>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_LARGE" in result.stdout
    assert "SVG_STROKE_THICK" in result.stdout


def test_nature_range_boundaries_are_allowed(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="7pt">Max allowed text</text>'
        '<path d="M0 0 L20 20" stroke="#000" stroke-width="1pt"/>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_LARGE" not in result.stdout
    assert "SVG_STROKE_THICK" not in result.stdout


def test_nature_maximum_can_be_overridden(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="8pt">Custom label</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "check",
            str(path),
            "--preset",
            "nature",
            "--max-font-size-pt",
            "8",
        ],
    )

    assert result.exit_code == 0
    assert "SVG_FONT_LARGE" not in result.stdout
    assert "CLI overrides" in result.stdout


def test_nature_does_not_apply_unsourced_raster_pixel_minimum(tmp_path: Path) -> None:
    path = tmp_path / "small.png"
    image = Image.new("RGB", (100, 100), "white")
    image.save(path, dpi=(300, 300))

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "DIM_SMALL" not in result.stdout
    assert "DPI_LOW" not in result.stdout


def test_unknown_preset_is_cli_error(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300"></svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "unknown"])

    assert result.exit_code != 0
    error_output = result.stdout + getattr(result, "stderr", "")
    assert "Unknown preset" in error_output


def test_nature_panel_labels_are_exempt_from_ordinary_7pt_max(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300" font-family="Arial">'
        '<text x="20" y="30" font-size="8pt" font-weight="bold">a</text>'
        '<text x="210" y="30" font-size="8pt" font-weight="700">b</text>'
        '<text x="60" y="280" font-size="7pt">Axis label</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_LARGE" not in result.stdout
    assert "SVG_PANEL_LABEL_SIZE" not in result.stdout
    assert "SVG_PANEL_LABEL_WEIGHT" not in result.stdout
    assert "SVG_PANEL_LABEL_STYLE" not in result.stdout


def test_nature_panel_label_style_is_checked(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300" font-family="Helvetica">'
        '<text x="20" y="30" font-size="7pt" font-style="italic">a</text>'
        '<text x="210" y="30" font-size="8pt" font-weight="bold">b</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_PANEL_LABEL_SIZE" in result.stdout
    assert "SVG_PANEL_LABEL_WEIGHT" in result.stdout
    assert "SVG_PANEL_LABEL_STYLE" in result.stdout
    assert "SVG_FONT_LARGE" not in result.stdout


def test_single_letter_is_not_assumed_to_be_panel_label(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300" font-family="Arial">'
        '<text x="20" y="30" font-size="8pt" font-weight="bold">a</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_LARGE" in result.stdout
    assert "SVG_PANEL_LABEL_SIZE" not in result.stdout


def test_nature_flags_explicit_mixed_font_families(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300">'
        '<text x="20" y="30" font-size="6pt" font-family="Arial">Axis</text>'
        '<text x="20" y="60" font-size="6pt" font-family="Times New Roman">Legend</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_INCONSISTENT" in result.stdout
    assert "SVG_FONT_NOT_PREFERRED" in result.stdout


def test_nature_accepts_consistent_helvetica_family(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300" font-family="Helvetica, Arial, sans-serif">'
        '<text x="20" y="30" font-size="6pt">Axis</text>'
        '<text x="20" y="60" font-size="6pt">Legend</text>'
        '</svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "nature"])

    assert result.exit_code == 0
    assert "SVG_FONT_INCONSISTENT" not in result.stdout
    assert "SVG_FONT_NOT_PREFERRED" not in result.stdout
    assert "SVG_FONT_FAMILY_UNKNOWN" not in result.stdout
