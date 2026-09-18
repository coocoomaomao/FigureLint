# PDF inspection

FigureLint's PDF checker focuses on technical properties that can be inspected reproducibly from the PDF structure.

## Default checks

| Code | Severity | Meaning |
| --- | --- | --- |
| `PDF_UNREADABLE` | error | The file cannot be opened as a PDF. |
| `PDF_ENCRYPTED` | error | The PDF is password-protected. |
| `PDF_NO_PAGES` | error | The PDF contains no pages. |
| `PDF_MULTI_PAGE` | warning | The PDF contains more than one page. |
| `PDF_PAGE_SMALL` | warning | A page is smaller than the configured short-side threshold. |
| `PDF_PAGE_LARGE` | warning | A page is larger than the configured long-side threshold. |
| `PDF_NO_EDITABLE_TEXT` | info | No editable text words were detected. |
| `PDF_FONT_NOT_EMBEDDED` | warning | A referenced font program is not embedded in the PDF. |
| `PDF_FONT_EMBEDDING_UNKNOWN` | info | Font embedding status could not be determined reliably. |
| `PDF_IMAGE_LOW_DPI` | warning | An embedded raster image has low effective resolution at its placed size. |
| `PDF_IMAGE_SOFT_MASK` | info | An embedded raster image uses a soft mask / alpha channel. |

## Default thresholds

- embedded raster image minimum: **300 DPI**
- page short side minimum: **1 inch**
- page long side maximum: **20 inches**

These are configurable guardrails, not claims that every publisher requires the same values.

~~~bash
figurelint check figure.pdf \
  --min-dpi 300 \
  --min-pdf-short-side-in 1 \
  --max-pdf-long-side-in 20
~~~

## Effective raster DPI

For embedded images, FigureLint estimates effective DPI from:

1. the image's pixel dimensions, and
2. the physical size of each placement on the PDF page.

For example, a 600×600 px image displayed at 2×2 inches is approximately 300 DPI.

If the placement cannot be resolved reliably, FigureLint does not invent a DPI value.

## Font embedding

FigureLint asks the PDF parser whether a referenced font program can be extracted from the PDF.

- extractable font bytes → treated as embedded
- no embedded font bytes → warning
- parser cannot determine status → informational finding

This is deliberately narrower than trying to predict how every PDF viewer or publisher will substitute fonts.

## Editable text

If no editable words can be extracted, FigureLint reports an informational finding.

That may mean:

- text was converted to vector outlines,
- the figure contains only vector/raster graphics, or
- text extraction is not available for the document structure.

It is therefore not automatically treated as an error.

## Transparency

The first PDF implementation checks raster soft masks / alpha channels. It does not yet attempt to fully model arbitrary vector transparency groups or blend modes.

## Deliberate limitations

The first implementation does not yet inspect:

- minimum PDF font sizes
- minimum vector stroke widths
- ICC/color-space compliance
- overprint settings
- arbitrary transparency groups / blend modes
- publisher-specific PDF/X requirements

Those checks can be added later where they can be implemented deterministically.
