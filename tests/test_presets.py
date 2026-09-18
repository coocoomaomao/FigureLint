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
    assert thresholds.min_stroke_width_pt == 0.5
    assert thresholds.min_pdf_short_side_in == 1.0
    assert thresholds.max_pdf_long_side_in == 20.0


def test_explicit_thresholds_override_preset_values() -> None:
    preset, thresholds = resolve_thresholds(
        "high-resolution",
        min_dpi=450,
        min_font_size_pt=9.0,
    )

    assert preset.name == "high-resolution"
    assert thresholds.min_dpi == 450
    assert thresholds.min_font_size_pt == 9.0
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
        assert (
            thresholds.min_stroke_width_pt is not None
            and thresholds.min_stroke_width_pt > 0
        )
        assert (
            thresholds.min_pdf_short_side_in is not None
            and thresholds.min_pdf_short_side_in > 0
        )
        assert (
            thresholds.max_pdf_long_side_in is not None
            and thresholds.max_pdf_long_side_in > thresholds.min_pdf_short_side_in
        )


def test_nature_preset_has_verified_official_source() -> None:
    preset = get_preset("nature")
    thresholds = preset.thresholds

    assert preset.is_publisher_verified
    assert preset.source_name == "Nature — Final submission"
    assert preset.source_url == "https://www.nature.com/nature/for-authors/final-submission"
    assert set(preset.verified_fields) == {
        "min_dpi",
        "min_font_size_pt",
        "min_stroke_width_pt",
        "max_pdf_long_side_in",
    }
    assert thresholds.min_dpi == 300
    assert thresholds.min_short_side is None
    assert thresholds.min_font_size_pt == 5.0
    assert thresholds.min_stroke_width_pt == 0.25
    assert thresholds.min_pdf_short_side_in is None
    assert thresholds.max_pdf_long_side_in == pytest.approx(247.0 / 25.4)


def test_presets_command_lists_profiles_and_provenance() -> None:
    result = runner.invoke(app, ["presets"])

    assert result.exit_code == 0
    assert "default" in result.stdout
    assert "high-resolution" in result.stdout
    assert "presentation" in result.stdout
    assert "journal-generic" in result.stdout
    assert "nature" in result.stdout
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


def test_nature_cli_applies_sourced_font_and_stroke_minima(tmp_path: Path) -> None:
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
    assert "nature.com/nature/for-authors/final-submission" in result.stdout


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
