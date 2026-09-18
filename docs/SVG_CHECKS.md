# SVG inspection

FigureLint's SVG checker focuses on technical properties that can be inspected reproducibly without rendering the file in a browser.

## Default checks

| Code | Severity | Meaning |
| --- | --- | --- |
| `SVG_UNREADABLE` | error | The SVG is malformed or cannot be parsed. |
| `SVG_ROOT_INVALID` | error | The document root is not an `<svg>` element. |
| `SVG_NO_EDITABLE_TEXT` | info | No editable `<text>` elements were found. Text may have been converted to paths, or the figure may simply contain no text. |
| `SVG_FONT_SIZE_UNKNOWN` | info | A text size could not be resolved deterministically. |
| `SVG_FONT_SMALL` | warning | One or more resolved text sizes are below the configured threshold. |
| `SVG_STROKE_THIN` | warning | One or more resolved stroke widths are below the configured threshold. |

The default thresholds are:

- minimum font size: **7 pt**
- minimum stroke width: **0.5 pt**

These are configurable guardrails, not claims that every journal requires the same values.

~~~bash
figurelint check figure.svg --min-font-size-pt 8 --min-stroke-width-pt 0.6
~~~

## What FigureLint resolves

The first SVG implementation resolves:

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

The first implementation does not fully evaluate:

- complex CSS selectors or the complete CSS cascade
- external stylesheets
- relative font units such as `em`, `rem`, or percentages
- the visual effect of arbitrary nested transforms
- script-driven SVG changes
- browser-specific font substitution or rendering

When a font size cannot be resolved, FigureLint reports an informational finding instead of inventing a value.

## Why "no editable text" is informational

Some valid scientific SVGs contain no labels at all. Others intentionally convert text to outlines for portability. For that reason, the absence of `<text>` elements is useful information, but not automatically a failure.

For workflows that require editable text, this finding can still be reviewed manually or promoted by a future preset.
