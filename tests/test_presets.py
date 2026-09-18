from __future__ import annotations

from pathlib import Path

import pytest
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


def test_builtin_presets_are_not_claimed_as_publisher_verified() -> None:
    for name in available_preset_names():
        assert not get_preset(name).is_publisher_verified


def test_builtin_thresholds_are_positive_and_page_range_is_valid() -> None:
    for name in available_preset_names():
        thresholds = get_preset(name).thresholds
        assert thresholds.min_dpi > 0
        assert thresholds.min_short_side > 0
        assert thresholds.min_font_size_pt > 0
        assert thresholds.min_stroke_width_pt > 0
        assert thresholds.min_pdf_short_side_in > 0
        assert thresholds.max_pdf_long_side_in > thresholds.min_pdf_short_side_in


def test_presets_command_lists_profiles_and_provenance() -> None:
    result = runner.invoke(app, ["presets"])

    assert result.exit_code == 0
    assert "default" in result.stdout
    assert "high-resolution" in result.stdout
    assert "presentation" in result.stdout
    assert "journal-generic" in result.stdout
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


def test_unknown_preset_is_cli_error(tmp_path: Path) -> None:
    path = tmp_path / "figure.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="400pt" height="300pt" '
        'viewBox="0 0 400 300"></svg>',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", str(path), "--preset", "unknown"])

    assert result.exit_code != 0
    assert "Unknown preset" in result.stdout
