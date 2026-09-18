from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Thresholds:
    """Numeric thresholds shared by raster, SVG, and PDF checks.

    A value of None disables that threshold. This lets source-verified publisher
    presets avoid silently inheriting FigureLint-only assumptions.
    """

    min_dpi: int | None
    min_short_side: int | None
    min_font_size_pt: float | None
    min_stroke_width_pt: float | None
    min_pdf_short_side_in: float | None
    max_pdf_long_side_in: float | None


@dataclass(frozen=True)
class Preset:
    """A named collection of FigureLint thresholds and provenance metadata."""

    name: str
    description: str
    thresholds: Thresholds
    source_name: str | None = None
    source_url: str | None = None
    source_verified: bool = False
    verified_fields: tuple[str, ...] = ()

    @property
    def is_publisher_verified(self) -> bool:
        return bool(
            self.source_verified
            and self.source_name
            and self.source_url
            and self.verified_fields
        )


_DEFAULT_THRESHOLDS = Thresholds(
    min_dpi=300,
    min_short_side=600,
    min_font_size_pt=7.0,
    min_stroke_width_pt=0.5,
    min_pdf_short_side_in=1.0,
    max_pdf_long_side_in=20.0,
)

PRESETS: dict[str, Preset] = {
    "default": Preset(
        name="default",
        description="Balanced FigureLint defaults for everyday academic figure QA.",
        thresholds=_DEFAULT_THRESHOLDS,
    ),
    "high-resolution": Preset(
        name="high-resolution",
        description=(
            "A stricter convenience profile for raster-heavy figures and export review."
        ),
        thresholds=Thresholds(
            min_dpi=600,
            min_short_side=1200,
            min_font_size_pt=7.0,
            min_stroke_width_pt=0.5,
            min_pdf_short_side_in=1.0,
            max_pdf_long_side_in=20.0,
        ),
    ),
    "presentation": Preset(
        name="presentation",
        description=(
            "A convenience profile favoring larger labels and strokes for slides/screens."
        ),
        thresholds=Thresholds(
            min_dpi=150,
            min_short_side=960,
            min_font_size_pt=12.0,
            min_stroke_width_pt=0.75,
            min_pdf_short_side_in=1.0,
            max_pdf_long_side_in=40.0,
        ),
    ),
    "journal-generic": Preset(
        name="journal-generic",
        description=(
            "A conservative paper-figure convenience profile; not publisher-specific."
        ),
        thresholds=Thresholds(
            min_dpi=300,
            min_short_side=900,
            min_font_size_pt=8.0,
            min_stroke_width_pt=0.5,
            min_pdf_short_side_in=1.0,
            max_pdf_long_side_in=20.0,
        ),
    ),
    "nature": Preset(
        name="nature",
        description=(
            "Source-verified subset of Nature final figure guidance that FigureLint "
            "can check deterministically."
        ),
        thresholds=Thresholds(
            min_dpi=300,
            min_short_side=None,
            min_font_size_pt=5.0,
            min_stroke_width_pt=0.25,
            min_pdf_short_side_in=None,
            max_pdf_long_side_in=247.0 / 25.4,
        ),
        source_name="Nature — Final submission",
        source_url="https://www.nature.com/nature/for-authors/final-submission",
        source_verified=True,
        verified_fields=(
            "min_dpi",
            "min_font_size_pt",
            "min_stroke_width_pt",
            "max_pdf_long_side_in",
        ),
    ),
}

_ALIASES = {
    "journal": "journal-generic",
}


def available_preset_names() -> tuple[str, ...]:
    """Return canonical preset names in a stable display order."""
    return tuple(PRESETS)


def get_preset(name: str) -> Preset:
    """Resolve a preset name or alias.

    Raises ValueError with a user-facing message when the preset does not exist.
    """
    normalized = name.strip().lower()
    canonical = _ALIASES.get(normalized, normalized)

    try:
        return PRESETS[canonical]
    except KeyError as exc:
        choices = ", ".join(available_preset_names())
        raise ValueError(
            f"Unknown preset '{name}'. Available presets: {choices}."
        ) from exc


def resolve_thresholds(
    preset_name: str,
    *,
    min_dpi: int | None = None,
    min_short_side: int | None = None,
    min_font_size_pt: float | None = None,
    min_stroke_width_pt: float | None = None,
    min_pdf_short_side_in: float | None = None,
    max_pdf_long_side_in: float | None = None,
) -> tuple[Preset, Thresholds]:
    """Resolve a preset and apply explicit CLI-style threshold overrides."""
    preset = get_preset(preset_name)
    thresholds = preset.thresholds

    overrides = {
        "min_dpi": min_dpi,
        "min_short_side": min_short_side,
        "min_font_size_pt": min_font_size_pt,
        "min_stroke_width_pt": min_stroke_width_pt,
        "min_pdf_short_side_in": min_pdf_short_side_in,
        "max_pdf_long_side_in": max_pdf_long_side_in,
    }
    applied = {key: value for key, value in overrides.items() if value is not None}

    if applied:
        thresholds = replace(thresholds, **applied)

    return preset, thresholds
