# pdf2booklet

Reorder a PDF for booklet printing (2 pages per sheet, double-sided). Fold the stack in half to read in order.

**Usage**

1. Put PDFs in `input/` (repo includes `input/example.pdf` so the folders exist after clone)
2. Run: `python pdf2booklet.py`
3. Pick a file with arrow keys + Enter
4. Get `output/<name>_booklet.pdf`

**Requires:** Python 3, `pypdf`, `questionary`. Put `blank.pdf` in the project folder if you want custom blank pages.

**Notes**
When printing make sure the setting is
- Double-sided
- 2 pages per sheet (two pages in landscape)
- Flip on short edge (위로 넘김)
