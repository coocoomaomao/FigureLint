from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from .models import Finding, Severity

_LENGTH_RE = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z%]*)\s*$"
)
_CSS_BLOCK_RE = re.compile(r"([^{}]+)\{([^{}]+)\}", re.DOTALL)
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_SIMPLE_SELECTOR_RE = re.compile(
    r"^(?P<tag>[A-Za-z_][\w.-]*)?(?P<id>#[\w.-]+)?(?P<classes>(?:\.[\w.-]+)*)$"
)
_FONT_SIZE_RE = re.compile(
    r"(?<![\w.-])([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*"
    r"(px|pt|pc|in|cm|mm|q|em|rem|%)\b",
    re.IGNORECASE,
)

_INHERITED_PROPERTIES = {
    "font-size",
    "font",
    "font-family",
    "font-weight",
    "font-style",
    "stroke",
    "stroke-width",
    "visibility",
}
_GRAPHICS_TAGS = {"path", "line", "polyline", "polygon", "rect", "circle", "ellipse"}
_SKIP_SUBTREES = {"defs", "clipPath", "mask", "marker", "metadata"}


@dataclass(frozen=True)
class _TextRecord:
    text: str
    font_size_pt: float | None
    font_family: str | None
    font_weight: str | None
    font_style: str | None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_declarations(value: str | None) -> dict[str, str]:
    if not value:
        return {}

    result: dict[str, str] = {}
    for item in value.split(";"):
        if ":" not in item:
            continue
        key, raw = item.split(":", 1)
        key = key.strip().lower()
        raw = raw.strip()
        if key and raw:
            result[key] = raw
    return result


def _parse_absolute_length_to_pt(value: str | None) -> float | None:
    if value is None:
        return None

    match = _LENGTH_RE.match(value)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).lower()
    factors = {
        "": 0.75,
        "px": 0.75,
        "pt": 1.0,
        "pc": 12.0,
        "in": 72.0,
        "cm": 72.0 / 2.54,
        "mm": 72.0 / 25.4,
        "q": 72.0 / 101.6,
    }
    factor = factors.get(unit)
    if factor is None:
        return None
    return number * factor


def _root_user_unit_to_pt(root: ET.Element) -> float | None:
    """Estimate root SVG user-unit size in points."""
    view_box = root.get("viewBox") or root.get("viewbox")
    if not view_box:
        return 0.75

    try:
        parts = [float(part) for part in re.split(r"[\s,]+", view_box.strip()) if part]
    except ValueError:
        return None

    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
        return None

    width_pt = _parse_absolute_length_to_pt(root.get("width"))
    height_pt = _parse_absolute_length_to_pt(root.get("height"))
    scales: list[float] = []

    if width_pt is not None and width_pt > 0:
        scales.append(width_pt / parts[2])
    if height_pt is not None and height_pt > 0:
        scales.append(height_pt / parts[3])

    if not scales:
        return None
    if len(scales) == 1:
        return scales[0]

    small, large = sorted(scales)
    if large == 0 or (large - small) / large > 0.05:
        return None

    return sum(scales) / len(scales)


def _length_to_pt(value: str | None, user_unit_to_pt: float | None) -> float | None:
    if value is None:
        return None

    match = _LENGTH_RE.match(value)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).lower()
    if unit == "":
        return None if user_unit_to_pt is None else number * user_unit_to_pt

    return _parse_absolute_length_to_pt(f"{number}{unit}")


def _selector_specificity(selector: str) -> int | None:
    match = _SIMPLE_SELECTOR_RE.fullmatch(selector.strip())
    if not match:
        return None

    return (
        (100 if match.group("id") else 0)
        + 10 * match.group("classes").count(".")
        + (1 if match.group("tag") else 0)
    )


def _selector_matches(element: ET.Element, selector: str) -> bool:
    match = _SIMPLE_SELECTOR_RE.fullmatch(selector.strip())
    if not match:
        return False

    tag = match.group("tag")
    selector_id = match.group("id")
    classes = [item for item in match.group("classes").split(".") if item]

    if tag and _local_name(element.tag) != tag:
        return False
    if selector_id and element.get("id") != selector_id[1:]:
        return False

    element_classes = set((element.get("class") or "").split())
    return all(name in element_classes for name in classes)


def _collect_css_rules(root: ET.Element) -> list[tuple[str, int, int, dict[str, str]]]:
    rules: list[tuple[str, int, int, dict[str, str]]] = []
    order = 0

    for element in root.iter():
        if _local_name(element.tag) != "style" or not element.text:
            continue

        css = _CSS_COMMENT_RE.sub("", element.text)
        for selector_group, body in _CSS_BLOCK_RE.findall(css):
            declarations = _parse_declarations(body)
            if not declarations:
                continue

            for selector in selector_group.split(","):
                selector = selector.strip()
                specificity = _selector_specificity(selector)
                if specificity is None:
                    continue

                rules.append((selector, specificity, order, declarations))
                order += 1

    return rules


def _computed_properties(
    element: ET.Element,
    inherited: dict[str, str],
    css_rules: list[tuple[str, int, int, dict[str, str]]],
) -> dict[str, str]:
    properties = {
        key: value for key, value in inherited.items() if key in _INHERITED_PROPERTIES
    }

    for key in _INHERITED_PROPERTIES:
        value = element.get(key)
        if value is not None:
            properties[key] = value.strip()

    matched: dict[str, tuple[int, int, str]] = {}
    for selector, specificity, order, declarations in css_rules:
        if not _selector_matches(element, selector):
            continue

        for key, value in declarations.items():
            previous = matched.get(key)
            if previous is None or (specificity, order) >= (previous[0], previous[1]):
                matched[key] = (specificity, order, value)

    for key, (_, _, value) in matched.items():
        properties[key] = value

    properties.update(_parse_declarations(element.get("style")))
    return properties


def _font_size_value(properties: dict[str, str]) -> str | None:
    direct = properties.get("font-size")
    if direct:
        return direct

    shorthand = properties.get("font")
    if not shorthand:
        return None

    match = _FONT_SIZE_RE.search(shorthand)
    if not match:
        return None

    return f"{match.group(1)}{match.group(2)}"


def _font_family_value(properties: dict[str, str]) -> str | None:
    direct = properties.get("font-family")
    if direct:
        return direct.strip()

    shorthand = properties.get("font")
    if not shorthand:
        return None

    match = _FONT_SIZE_RE.search(shorthand)
    if not match:
        return None

    tail = shorthand[match.end():].strip()
    if tail.startswith("/"):
        tail = tail[1:].lstrip()
        parts = tail.split(None, 1)
        if len(parts) != 2:
            return None
        tail = parts[1].strip()

    return tail or None


def _font_weight_value(properties: dict[str, str]) -> str | None:
    direct = properties.get("font-weight")
    if direct:
        return direct.strip().lower()

    shorthand = properties.get("font")
    if not shorthand:
        return None

    match = _FONT_SIZE_RE.search(shorthand)
    prefix = shorthand[: match.start()] if match else shorthand
    tokens = re.findall(r"\b(?:bold|bolder|[1-9]00)\b", prefix, re.IGNORECASE)
    return tokens[-1].lower() if tokens else None


def _font_style_value(properties: dict[str, str]) -> str | None:
    direct = properties.get("font-style")
    if direct:
        return direct.strip().lower()

    shorthand = properties.get("font")
    if not shorthand:
        return None

    match = _FONT_SIZE_RE.search(shorthand)
    prefix = shorthand[: match.start()] if match else shorthand
    style = re.search(r"\b(italic|oblique|normal)\b", prefix, re.IGNORECASE)
    return style.group(1).lower() if style else None


def _font_weight_is_bold(value: str | None) -> bool:
    if value is None:
        return False

    normalized = value.strip().lower()
    if normalized in {"bold", "bolder"}:
        return True

    try:
        return int(normalized) >= 600
    except ValueError:
        return False


def _font_style_is_upright(value: str | None) -> bool:
    return value is None or value.strip().lower() not in {"italic", "oblique"}


def _font_families(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()

    result: list[str] = []
    for item in value.split(","):
        normalized = item.strip().strip("'\"").lower()
        if normalized:
            result.append(normalized)
    return tuple(result)


def _panel_label_letters(records: list[_TextRecord]) -> set[str]:
    """Conservatively detect a contiguous standalone a,b,c... label sequence."""
    labels = {
        record.text
        for record in records
        if len(record.text) == 1 and "a" <= record.text <= "z"
    }

    if "a" not in labels or "b" not in labels:
        return set()

    sequence: set[str] = set()
    codepoint = ord("a")
    while chr(codepoint) in labels:
        sequence.add(chr(codepoint))
        codepoint += 1

    return sequence if len(sequence) >= 2 else set()


def check_svg(
    path: Path,
    *,
    min_font_size_pt: float | None = 7.0,
    max_font_size_pt: float | None = None,
    min_stroke_width_pt: float | None = 0.5,
    max_stroke_width_pt: float | None = None,
    panel_label_size_pt: float | None = None,
    panel_label_require_bold: bool = False,
    panel_label_require_upright: bool = False,
    preferred_font_families: tuple[str, ...] = (),
    require_consistent_font_family: bool = False,
) -> list[Finding]:
    """Inspect an SVG using deterministic, locally-resolvable properties.

    Panel-label and font-family checks are opt-in so publisher presets can use
    them without changing the default FigureLint behavior.
    """
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [
            Finding(
                path=path,
                severity=Severity.ERROR,
                code="SVG_UNREADABLE",
                message=f"SVG could not be parsed: {exc}",
            )
        ]

    if _local_name(root.tag) != "svg":
        return [
            Finding(
                path=path,
                severity=Severity.ERROR,
                code="SVG_ROOT_INVALID",
                message="Root element is not <svg>.",
            )
        ]

    findings: list[Finding] = []
    css_rules = _collect_css_rules(root)
    user_unit_to_pt = _root_user_unit_to_pt(root)

    text_records: list[_TextRecord] = []
    thin_strokes: list[float] = []
    thick_strokes: list[float] = []

    def visit(element: ET.Element, inherited: dict[str, str]) -> None:
        tag = _local_name(element.tag)
        if tag in _SKIP_SUBTREES:
            return

        properties = _computed_properties(element, inherited, css_rules)
        display = properties.get("display", element.get("display", "")).strip().lower()
        visibility = properties.get("visibility", "").strip().lower()

        if display == "none" or visibility in {"hidden", "collapse"}:
            return

        if tag == "text":
            raw_font_size = _font_size_value(properties)
            text_records.append(
                _TextRecord(
                    text="".join(element.itertext()).strip(),
                    font_size_pt=_length_to_pt(raw_font_size, user_unit_to_pt),
                    font_family=_font_family_value(properties),
                    font_weight=_font_weight_value(properties),
                    font_style=_font_style_value(properties),
                )
            )

        if tag in _GRAPHICS_TAGS:
            stroke = properties.get("stroke", "").strip().lower()
            if stroke and stroke != "none":
                raw_width = properties.get("stroke-width", "1")
                stroke_width_pt = _length_to_pt(raw_width, user_unit_to_pt)

                if stroke_width_pt is not None:
                    if (
                        min_stroke_width_pt is not None
                        and stroke_width_pt < min_stroke_width_pt
                    ):
                        thin_strokes.append(stroke_width_pt)
                    if (
                        max_stroke_width_pt is not None
                        and stroke_width_pt > max_stroke_width_pt
                    ):
                        thick_strokes.append(stroke_width_pt)

        for child in element:
            visit(child, properties)

    visit(root, {})

    if not text_records:
        findings.append(
            Finding(
                path=path,
                severity=Severity.INFO,
                code="SVG_NO_EDITABLE_TEXT",
                message=(
                    "No editable <text> elements were found. Text may have been "
                    "converted to outlines/paths, or the figure may contain no text."
                ),
            )
        )
    else:
        panel_letters = (
            _panel_label_letters(text_records)
            if panel_label_size_pt is not None
            else set()
        )
        unknown_font_sizes = 0
        small_font_sizes: list[float] = []
        large_font_sizes: list[float] = []
        panel_size_issues: list[tuple[str, float]] = []
        panel_weight_issues: list[str] = []
        panel_style_issues: list[str] = []

        preferred = {family.lower() for family in preferred_font_families}
        primary_families: set[str] = set()
        nonpreferred_families: set[str] = set()
        unknown_font_families = 0

        for record in text_records:
            is_panel_label = record.text in panel_letters

            if record.font_size_pt is None:
                unknown_font_sizes += 1
            else:
                if (
                    min_font_size_pt is not None
                    and record.font_size_pt < min_font_size_pt
                ):
                    small_font_sizes.append(record.font_size_pt)

                if (
                    max_font_size_pt is not None
                    and not is_panel_label
                    and record.font_size_pt > max_font_size_pt
                ):
                    large_font_sizes.append(record.font_size_pt)

                if (
                    is_panel_label
                    and panel_label_size_pt is not None
                    and abs(record.font_size_pt - panel_label_size_pt) > 0.05
                ):
                    panel_size_issues.append((record.text, record.font_size_pt))

            if (
                is_panel_label
                and panel_label_require_bold
                and not _font_weight_is_bold(record.font_weight)
            ):
                panel_weight_issues.append(record.text)

            if (
                is_panel_label
                and panel_label_require_upright
                and not _font_style_is_upright(record.font_style)
            ):
                panel_style_issues.append(record.text)

            if preferred or require_consistent_font_family:
                families = _font_families(record.font_family)
                if not families:
                    unknown_font_families += 1
                else:
                    primary_families.add(families[0])
                    if preferred and not any(family in preferred for family in families):
                        nonpreferred_families.add(families[0])

        if unknown_font_sizes:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.INFO,
                    code="SVG_FONT_SIZE_UNKNOWN",
                    message=(
                        f"Could not resolve the font size for {unknown_font_sizes} of "
                        f"{len(text_records)} text element(s); relative units or complex "
                        "CSS may be in use."
                    ),
                )
            )

        if small_font_sizes and min_font_size_pt is not None:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="SVG_FONT_SMALL",
                    message=(
                        f"Found {len(small_font_sizes)} text element(s) below "
                        f"{min_font_size_pt:g} pt; smallest resolved size is "
                        f"{min(small_font_sizes):.2f} pt."
                    ),
                )
            )

        if large_font_sizes and max_font_size_pt is not None:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="SVG_FONT_LARGE",
                    message=(
                        f"Found {len(large_font_sizes)} ordinary text element(s) above "
                        f"{max_font_size_pt:g} pt; largest resolved size is "
                        f"{max(large_font_sizes):.2f} pt."
                    ),
                )
            )

        if panel_size_issues and panel_label_size_pt is not None:
            labels = ", ".join(label for label, _ in panel_size_issues)
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="SVG_PANEL_LABEL_SIZE",
                    message=(
                        f"Detected panel label(s) {labels} outside the configured "
                        f"{panel_label_size_pt:g} pt panel-label size."
                    ),
                )
            )

        if panel_weight_issues:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="SVG_PANEL_LABEL_WEIGHT",
                    message=(
                        "Detected panel label(s) that are not bold: "
                        + ", ".join(panel_weight_issues)
                        + "."
                    ),
                )
            )

        if panel_style_issues:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="SVG_PANEL_LABEL_STYLE",
                    message=(
                        "Detected panel label(s) that are italic/oblique instead of "
                        "upright: "
                        + ", ".join(panel_style_issues)
                        + "."
                    ),
                )
            )

        if require_consistent_font_family and len(primary_families) > 1:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.WARNING,
                    code="SVG_FONT_INCONSISTENT",
                    message=(
                        "Multiple explicit primary font families were detected: "
                        + ", ".join(sorted(primary_families))
                        + "."
                    ),
                )
            )

        if nonpreferred_families:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.INFO,
                    code="SVG_FONT_NOT_PREFERRED",
                    message=(
                        "Explicit font families outside the preferred set were detected: "
                        + ", ".join(sorted(nonpreferred_families))
                        + "."
                    ),
                )
            )

        if (preferred or require_consistent_font_family) and unknown_font_families:
            findings.append(
                Finding(
                    path=path,
                    severity=Severity.INFO,
                    code="SVG_FONT_FAMILY_UNKNOWN",
                    message=(
                        f"Could not resolve an explicit font family for "
                        f"{unknown_font_families} of {len(text_records)} text element(s)."
                    ),
                )
            )

    if thin_strokes and min_stroke_width_pt is not None:
        findings.append(
            Finding(
                path=path,
                severity=Severity.WARNING,
                code="SVG_STROKE_THIN",
                message=(
                    f"Found {len(thin_strokes)} stroked element(s) below "
                    f"{min_stroke_width_pt:g} pt; thinnest resolved stroke is "
                    f"{min(thin_strokes):.2f} pt."
                ),
            )
        )

    if thick_strokes and max_stroke_width_pt is not None:
        findings.append(
            Finding(
                path=path,
                severity=Severity.WARNING,
                code="SVG_STROKE_THICK",
                message=(
                    f"Found {len(thick_strokes)} stroked element(s) above "
                    f"{max_stroke_width_pt:g} pt; thickest resolved stroke is "
                    f"{max(thick_strokes):.2f} pt."
                ),
            )
        )

    return findings
