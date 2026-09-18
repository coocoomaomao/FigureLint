# FigureLint

> Catch publication-quality problems in academic figures before submission.

FigureLint is an open-source linter for academic figures. Think **ESLint, but for paper figures**: point it at a figure or a folder and get fast, reproducible checks that can also run in CI.

## Why

A figure can look fine on screen and still cause trouble during submission or production: low effective resolution, missing DPI metadata, tiny raster dimensions, accidental transparency, or an export format that is hard to edit later. FigureLint turns those checks into a repeatable command.

## MVP: v0.1

FigureLint currently checks PNG and JPEG files for:

- unreadable/corrupt image files
- missing or low DPI metadata
- suspiciously small raster dimensions
- transparency that may need flattening for some workflows
- JPEG usage (informational, because it is lossy)
- folders of figures recursively
- CI-friendly exit codes with optional strict mode

Planned next:

- PDF and SVG inspection
- font size and embedded-font checks
- line-width checks
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

Check one image:

~~~bash
figurelint check path/to/figure.png
~~~

Check a whole folder:

~~~bash
figurelint check figures/
~~~

Use stricter CI behavior so warnings fail the command:

~~~bash
figurelint check figures/ --strict
~~~

Customize thresholds:

~~~bash
figurelint check figure.png --min-dpi 300 --min-short-side 600
~~~

Example output:

~~~text
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File       ┃ Severity ┃ Code        ┃ Message                          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ figure.png │ warning  │ DPI_MISSING │ No DPI metadata was found.       │
└────────────┴──────────┴─────────────┴──────────────────────────────────┘
~~~

## Exit codes

- `0`: no errors; warnings are allowed unless `--strict` is used
- `1`: warnings found in strict mode
- `2`: one or more errors were found

## Philosophy

FigureLint should flag **verifiable technical properties**, not pretend that every journal has the same rules. Thresholds are configurable, and future journal presets will be documented with their source guidelines.

## Contributing

Ideas, bug reports, and pull requests are welcome. The first milestones are tracked in GitHub Issues.

## License

MIT
