<p align="center">
  <img src="assets/figurelint-banner.svg" alt="FigureLint — ESLint for academic figures" width="100%">
</p>

<p align="center">
  <a href="https://github.com/coocoomaomao/FigureLint/actions/workflows/ci.yml">
    <img src="https://github.com/coocoomaomao/FigureLint/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/status-alpha-orange" alt="Status Alpha">
</p>

> **ESLint for academic figures.**

**FigureLint** is an open-source linter for academic figures. It helps researchers and students catch common technical quality issues before submission.

## Why

A figure can look fine on screen and still cause trouble during submission or production: low effective resolution, missing DPI metadata, tiny raster dimensions, accidental transparency, text converted to outlines, tiny labels, or strokes that become too thin in print.

FigureLint turns those checks into a repeatable command.

## Current checks

### PNG / JPEG

- unreadable/corrupt image files
- missing or low DPI metadata
- suspiciously small raster dimensions
- transparency that may need flattening for some workflows
- JPEG usage (informational, because it is lossy)

### SVG

- malformed/unreadable SVG files
- whether editable `<text>` elements are present
- suspiciously small resolvable font sizes
- suspiciously thin resolvable strokes
- simple CSS resolution for tag, class, id, and `tag.class` selectors
- inline style and SVG presentation-attribute resolution

See [SVG inspection details and assumptions](docs/SVG_CHECKS.md).

### Workflow

- recursive folder scanning
- CI-friendly exit codes
- optional strict mode
- configurable thresholds

Planned next:

- PDF inspection
- embedded-font checks
- color contrast and color-blind safety
- Nature / Science / IEEE / Elsevier-style presets
- GitHub Action annotations

## Install

Requires Python 3.10+.

~~~bash
git clone https://github.com/coocoomaomao/FigureLint.git
cd FigureLint
python -m venv .venv
pip install -e .
~~~

For development:

~~~bash
pip install -e ".[dev]"
pytest
~~~

## Usage

Check one figure:

~~~bash
figurelint check path/to/figure.svg
~~~

Check a whole folder:

~~~bash
figurelint check figures/
~~~

Use stricter CI behavior so warnings fail the command:

~~~bash
figurelint check figures/ --strict
~~~

Customize raster thresholds:

~~~bash
figurelint check figure.png --min-dpi 300 --min-short-side 600
~~~

Customize SVG thresholds:

~~~bash
figurelint check figure.svg --min-font-size-pt 7 --min-stroke-width-pt 0.5
~~~

Example output:

~~~text
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File       ┃ Severity ┃ Code            ┃ Message                      ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ figure.svg │ warning  │ SVG_FONT_SMALL  │ Found text below 7 pt.       │
└────────────┴──────────┴─────────────────┴──────────────────────────────┘
~~~

## Exit codes

- `0`: no errors; warnings are allowed unless `--strict` is used
- `1`: warnings found in strict mode
- `2`: one or more errors were found

## Brand assets

The official FigureLint visual system uses a **black cat + magnifying glass + check mark** in navy, teal, orange, and soft gray.

- [README banner](assets/figurelint-banner.svg)
- [Primary logo](assets/figurelint-logo.svg)
- [Icon / favicon source](assets/figurelint-icon.svg)
- [Dark-background logo](assets/figurelint-logo-dark.svg)
- [Social preview artwork](assets/figurelint-social-preview.svg)
- [Brand guide](docs/BRAND.md)

## Philosophy

FigureLint should flag **verifiable technical properties**, not pretend that every journal has the same rules. Thresholds are configurable, and future journal presets will be documented with their source guidelines.

## Contributing

Ideas, bug reports, and pull requests are welcome. The first milestones are tracked in GitHub Issues.

## License

MIT
