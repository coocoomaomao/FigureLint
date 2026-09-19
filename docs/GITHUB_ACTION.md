# GitHub Action

FigureLint can run directly in GitHub Actions and emit native workflow annotations for figure findings.

## Basic use

Pin the action to the current release tag:

~~~yaml
name: Figure QA

on:
  pull_request:
  push:
    branches: [main]

jobs:
  figurelint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: coocoomaomao/FigureLint@v0.1.0
        with:
          path: figures/
          preset: nature
~~~

## Pull-request annotations

The action always enables FigureLint's GitHub annotation output.

Findings are mapped to GitHub workflow commands as follows:

| FigureLint severity | GitHub annotation |
| --- | --- |
| error | error |
| warning | warning |
| info | notice |

A warning such as `SVG_FONT_SMALL` will therefore appear directly in the GitHub Actions UI and can be associated with the affected file.

## Strict mode

By default, warnings are annotated but do not fail the action.

To make warnings fail CI:

~~~yaml
- uses: coocoomaomao/FigureLint@v0.1.0
  with:
    path: figures/
    preset: nature
    strict: "true"
~~~

Errors always fail with FigureLint's error exit code.

## Threshold overrides

The action exposes the same main threshold overrides as the CLI:

~~~yaml
- uses: coocoomaomao/FigureLint@v0.1.0
  with:
    path: figures/
    preset: nature
    min-dpi: "300"
    min-font-size-pt: "5"
    max-font-size-pt: "7"
    min-stroke-width-pt: "0.25"
    max-stroke-width-pt: "1"
~~~

Available inputs:

- `path`
- `preset`
- `strict`
- `python-version`
- `min-dpi`
- `min-short-side`
- `min-font-size-pt`
- `max-font-size-pt`
- `min-stroke-width-pt`
- `max-stroke-width-pt`
- `min-pdf-short-side-in`
- `max-pdf-long-side-in`

## Direct CLI use inside Actions

If you already install FigureLint yourself, native annotations can also be enabled directly:

~~~bash
figurelint check figures/ --preset nature --github-annotations
~~~

Add `--strict` if warnings should fail the workflow.
