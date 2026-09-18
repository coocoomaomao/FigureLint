# Contributing to FigureLint

Thanks for helping improve FigureLint. Contributions from researchers, students, designers, and developers are welcome.

## Good first contributions

Useful beginner-friendly contributions include:

- adding test images for edge cases
- improving documentation
- reporting figure-export problems seen in real workflows
- proposing deterministic checks for SVG or PDF files
- improving accessibility and color-safety checks

## Development setup

~~~bash
git clone https://github.com/coocoomaomao/FigureLint.git
cd FigureLint
python -m venv .venv
pip install -e ".[dev]"
pytest
~~~

## Design principles

FigureLint should:

1. report verifiable technical properties
2. avoid pretending one journal rule fits every publication
3. keep thresholds configurable
4. explain warnings clearly
5. remain useful from both the CLI and CI

## Pull requests

Please keep pull requests focused. Add or update tests when behavior changes, and explain the problem the change is intended to solve.

## Issues

Bug reports and feature ideas are welcome. When possible, include the file format, export tool, expected behavior, and a minimal example.

## Brand

Please follow the project visual system documented in [docs/BRAND.md](docs/BRAND.md) when adding public-facing graphics.
