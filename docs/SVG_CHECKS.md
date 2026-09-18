# SVG inspection

FigureLint's SVG checker focuses on technical properties that can be inspected reproducibly without rendering the file in a browser.

## Default checks

| Code | Severity | Meaning |
| --- | --- | --- |
| `SVG_UNREADABLE` | error | The SVG is malformed or cannot be parsed. |
| `SVG_ROOT_INVALID` | error | The document root is not an `<svg>` element. |
| `SVG_NO_EDITABLE_TEXT` | info | No editable `<text>` elements were found. Text may have been converted to paths, or the figure may simply contain no text. |
| `SVG_FONT_SIZE_UNKNOWN` | info | A text size could not be resolved deterministically. |
| `SVG_FONT_SMALL` | warning | One or more resolved text sizes are below the configured minimum. |
| `SVG_FONT_LARGE` | warning | One or more resolved text sizes are above the configured maximum. |
| `SVG_STROKE_THIN` | warning | One or more resolved stroke widths are below the configured minimum. |
| `SVG_STROKE_THICK` | warning | One or more resolved stroke widths are above the configured maximum. |

The default preset enables only lower-bound SVG guardrails:

- minimum font size: **7 pt**
- minimum stroke width: **0.5 pt**
- no maximum font-size limit
- no maximum stroke-width limit

Upper bounds are available for publisher presets or explicit CLI use.

~~~bash
figurelint check figure.svg \
  --min-font-size-pt 5 \
  --max-font-size-pt 7 \
  --min-stroke-width-pt 0.25 \
  --max-stroke-width-pt 1
~~~

## What FigureLint resolves

The SVG implementation resolves:

- SVG presentation attributes such as `font-size`, `stroke`, and `stroke-width`
- inline `style="..."` declarations
- inherited font and stroke properties
- simple embedded CSS selectors:
  - element selectors such as `text`
  - class selectors such as `.axis-label`
  - id selectors such as `#legend`
  - combined selectors such as `text.axis-label`
- common absolute units: `px`, `pt`, `pc`, `in`, `cm`, `mm`, and `q`
- unitless root user units when a near-uniform `viewBox` mapping can be determined

## Deliberate limitations

FigureLint does **not** guess when a value cannot be resolved reliably.

The implementation does not fully evaluate:

- complex CSS selectors or the complete CSS cascade
- external stylesheets
- relative font units such as `em`, `rem`, or percentages
- the visual effect of arbitrary nested transforms
- script-driven SVG changes
- browser-specific font substitution or rendering

When a font size cannot be resolved, FigureLint reports an informational finding instead of inventing a value.

## Why "no editable text" is informational

Some valid scientific SVGs contain no labels at all. Others intentionally convert text to outlines for portability. For that reason, the absence of `<text>` elements is useful information, but not automatically a failure.

For publisher workflows that require editable text, this finding can be reviewed together with the publisher-specific documentation.
