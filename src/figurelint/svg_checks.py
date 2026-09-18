from __future__ import annotations

import re
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

_INHERITED_PROPERTIES = {"font-size", "font", "stroke", "stroke-width", "visibility"}
_GRAPHICS_TAGS = {"path", "line", "polyline", "polygon", "rect", "circle", "ellipse"}
_SKIP_SUBTREES = {"defs", "clipPath", "mask", "marker", "metadata"}


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
        "": 0.75,  # outer SVG lengths without units are CSS px
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
    """Estimate root SVG user-unit size in points.

    When width/height and viewBox provide a near-uniform mapping, use it.
    Otherwise fall back to the CSS px mapping when no viewBox mapping is
    available. Non-uniform mappings are intentionally left unresolved.
    """
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

    # SVG presentation attributes have low specificity.
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

    # Inline style wins over stylesheet/presentation attributes.
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


def check_svg(
    path: Path,
    *,
    min_font_size_pt: float | None = 7.0,
    min_stroke_width_pt: float | None = 0.5,
) -> list[Finding]:
    """Inspect an SVG using deterministic, locally-resolvable properties.

    The checker resolves presentation attributes, inline styles, and simple CSS
    selectors (tag, class, id, tag.class). Complex selectors, nested transforms,
    and relative font units are intentionally not guessed.
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

    text_count = 0
    unknown_font_sizes = 0
    small_font_sizes: list[float] = []
    thin_strokes: list[float] = []

    def visit(element: ET.Element, inherited: dict[str, str]) -> None:
        nonlocal text_count, unknown_font_sizes

        tag = _local_name(element.tag)
        if tag in _SKIP_SUBTREES:
            return

        properties = _computed_properties(element, inherited, css_rules)
        inline = _parse_declarations(element.get("style"))
        display = properties.get("display", element.get("display", "")).strip().lower()
        visibility = properties.get("visibility", "").strip().lower()

        if display == "none" or visibility in {"hidden", "collapse"}:
            return

        if tag == "text":
            text_count += 1
            raw_font_size = _font_size_value(properties)
            font_size_pt = _length_to_pt(raw_font_size, user_unit_to_pt)

            if font_size_pt is None:
                unknown_font_sizes += 1
            elif min_font_size_pt is not None and font_size_pt < min_font_size_pt:
                small_font_sizes.append(font_size_pt)

        if tag in _GRAPHICS_TAGS:
            stroke = properties.get("stroke", "").strip().lower()
            if stroke and stroke != "none":
                raw_width = properties.get("stroke-width", "1")
                stroke_width_pt = _length_to_pt(raw_width, user_unit_to_pt)

                if (
                    stroke_width_pt is not None
                    and min_stroke_width_pt is not None
                    and stroke_width_pt < min_stroke_width_pt
                ):
                    thin_strokes.append(stroke_width_pt)

        for child in element:
            visit(child, properties)

    visit(root, {})

    if text_count == 0:
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
    elif unknown_font_sizes:
        findings.append(
            Finding(
                path=path,
                severity=Severity.INFO,
                code="SVG_FONT_SIZE_UNKNOWN",
                message=(
                    f"Could not resolve the font size for {unknown_font_sizes} of "
                    f"{text_count} text element(s); relative units or complex CSS "
                    "may be in use."
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

    return findings
