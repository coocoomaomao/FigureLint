# Changelog

All notable changes to FigureLint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows Semantic Versioning.

## [Unreleased]

### Planned
- PDF font-size and vector stroke checks
- color accessibility checks
- stronger editable-text / outlined-text analysis
- additional source-verified publisher presets
- GitHub Action annotations

## [0.1.0] - 2026-09-19

### Added
- initial FigureLint command-line interface
- PNG and JPEG inspection
- unreadable image detection
- missing / low DPI warnings
- raster dimension and transparency checks
- JPEG lossy-format notice
- SVG file discovery and inspection
- malformed SVG detection
- editable-text detection
- configurable lower and upper SVG font-size checks
- configurable lower and upper SVG stroke-width checks
- simple embedded CSS, inline-style, and presentation-attribute resolution
- PDF file discovery and inspection
- malformed, encrypted, empty, and multi-page PDF checks
- PDF page-size guardrails
- PDF editable-text and font-embedding checks
- effective DPI checks for embedded PDF raster images
- PDF raster soft-mask / alpha detection
- recursive folder scanning
- strict mode and CI-friendly exit codes
- preset engine shared across raster, SVG, and PDF checks
- built-in convenience presets: `default`, `high-resolution`, `presentation`, and `journal-generic`
- source-verified `nature` preset with official provenance metadata
- Nature 5–7 pt ordinary SVG text range
- Nature 0.25–1 pt SVG stroke range
- conservative Nature multi-panel label recognition with 8 pt bold/upright validation
- Nature SVG font-family consistency and Arial/Helvetica preference guidance
- automated tests across Python 3.10, 3.11, and 3.12
- package build validation for wheel and source distributions
- PyPI Trusted Publishing workflow using GitHub Actions OIDC
- official black-cat visual identity and README demo assets

[Unreleased]: https://github.com/coocoomaomao/FigureLint/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/coocoomaomao/FigureLint/releases/tag/v0.1.0
