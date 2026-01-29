#!/usr/bin/env python3
"""Reorder PDF for booklet print. Pick from input/ → save to output/."""

import sys
from pathlib import Path

import questionary
from pypdf import PageObject, PdfReader, PdfWriter

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")


def booklet_order(n: int) -> list[int]:
    """4의 배수 n에 대해 책자 순서(0-based 인덱스) 반환."""
    return [
        x
        for i in range(n // 4)
        for x in (n - 2 * i - 1, 2 * i, 2 * i + 1, n - 2 * i - 2)
    ]


def pad4(num: int) -> int:
    """4의 배수로 올림."""
    return num if num % 4 == 0 else num + (4 - num % 4)


def print_layout(order: list[int], total: int) -> None:
    """Print booklet layout table (columns aligned)."""
    def cell(idx: int) -> str:
        return "blank" if idx >= total else str(idx + 1)

    headers = ("sheet", "front L", "front R", "back L", "back R")
    rows = []
    for i in range(len(order) // 4):
        fl, fr, bl, br = order[4 * i], order[4 * i + 1], order[4 * i + 2], order[4 * i + 3]
        rows.append((str(i + 1), cell(fl), cell(fr), cell(bl), cell(br)))

    w = [max(len(h), max(len(r[j]) for r in rows)) for j, h in enumerate(headers)]
    sep = "  "
    print(sep.join(h.ljust(w[j]) for j, h in enumerate(headers)))
    for row in rows:
        print(sep.join(row[j].ljust(w[j]) for j in range(5)))


def run(input_path: Path, output_path: Path) -> None:
    """Reorder selected PDF for booklet and save to output_path."""
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    if total == 0:
        raise ValueError("PDF has no pages.")

    n = pad4(total)
    order = booklet_order(n)
    print_layout(order, total)

    blank = None
    if n > total:
        blank_file = Path.cwd() / "blank.pdf"
        if blank_file.exists():
            try:
                br = PdfReader(str(blank_file))
                if br.pages:
                    blank = br.pages[0]
            except Exception:
                pass
        if blank is None:
            p0 = reader.pages[0]
            try:
                blank = PageObject.create_blank_page(
                    width=float(p0.mediabox.width), height=float(p0.mediabox.height)
                )
            except Exception:
                blank = None

    writer = PdfWriter()
    for idx in order:
        writer.add_page(reader.pages[idx] if idx < total else blank or reader.pages[total - 1])
    writer.write(str(output_path))
    print(f"\nSaved: {output_path}  ({len(order)} pages)")


def select_input() -> Path | None:
    """Pick a PDF from input/ with arrow keys. Returns None if not a TTY or cancelled."""
    if not sys.stdin.isatty():
        print("Run in a terminal.", file=sys.stderr)
        return None
    if not INPUT_DIR.is_dir():
        print(f"Create '{INPUT_DIR}/' and put PDFs in it.", file=sys.stderr)
        return None
    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs in '{INPUT_DIR}/'.", file=sys.stderr)
        return None
    chosen = questionary.select("Select PDF (↑↓ Enter):", choices=[questionary.Choice(p.name, p) for p in pdfs]).ask()
    return chosen


def main() -> None:
    inp = select_input()
    if inp is None:
        sys.exit(1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"{inp.stem}_booklet.pdf"
    try:
        run(inp, out)
    except (FileNotFoundError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
