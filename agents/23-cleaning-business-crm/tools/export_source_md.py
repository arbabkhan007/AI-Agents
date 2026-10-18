#!/usr/bin/env python3
"""Export the complete generator source to one Markdown file.

    python3 tools/export_source_md.py --product cleaning

Writes SOURCE_CODE_CLEANING.md next to the project root: every source
file, verbatim, with its line count - the rebuild-everything document.
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRODUCTS = {
    "cleaning": {
        "package": "cleaning_business_spreadsheet",
        "readme": "README_CLEANING.md",
        "out": "SOURCE_CODE_CLEANING.md",
        "title": "Cleaning Business CRM & Pricing Calculator",
    },
}


def emit_file(lines: list, path: Path, arc: str) -> None:
    text = path.read_text(encoding="utf-8")
    n = text.count("\n") + (0 if text.endswith("\n") else 1)
    lang = "python" if path.suffix == ".py" else (
        "markdown" if path.suffix == ".md" else "text")
    lines.append(f"## `{arc}`  ·  {n} lines\n")
    lines.append(f"```{lang}")
    lines.append(text.rstrip("\n"))
    lines.append("```")
    lines.append("")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", default="cleaning",
                        choices=sorted(PRODUCTS))
    args = parser.parse_args()
    product = PRODUCTS[args.product]

    lines = [
        f"# {product['title']} - Complete Source Code",
        "",
        "Every file of the generator, verbatim. Rebuild the workbook with:",
        "",
        "```",
        "python build_cleaning_workbook.py",
        "python build_cleaning_workbook.py --blank -o \"output/Cleaning "
        "Business CRM & Pricing Calculator (Blank).xlsx\"",
        "```",
        "",
        "---",
        "",
    ]

    files = []
    pkg = ROOT / product["package"]
    for path in sorted(pkg.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append((path, str(path.relative_to(ROOT))))
    for script in sorted(ROOT.glob("*.py")):
        files.append((script, script.name))
    for script in sorted((ROOT / "tools").glob("*.py")):
        files.append((script, "tools/" + script.name))
    readme = ROOT / product["readme"]
    if readme.exists():
        files.append((readme, product["readme"]))

    total = 0
    for path, arc in files:
        emit_file(lines, path, arc)
        total += 1

    out = ROOT / product["out"]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{out.name}: {total} files, "
          f"{out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
