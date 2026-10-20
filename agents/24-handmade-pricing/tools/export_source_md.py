#!/usr/bin/env python3
"""Export the complete generator source to one Markdown file.

    python3 tools/export_source_md.py --product handmade

Writes ``SOURCE_CODE_HANDMADE.md`` in the project root: every source file of
the generator, verbatim, with its line count, plus the build script, the tools
and the README. That single file is enough to rebuild the whole product from
nothing - which is the point of keeping it.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent

PRODUCTS = {
    "handmade": {
        "package": "handmade_pricing_spreadsheet",
        "readme": "README_HANDMADE.md",
        "out": "SOURCE_CODE_HANDMADE.md",
        "title": "Handmade Product Pricing & Profit Calculator",
        "build": "build_handmade_workbook.py",
        "blank": "output/Handmade Product Pricing & Profit Calculator "
                 "(Blank).xlsx",
    },
}


def emit_file(lines: List[str], path: Path, arc: str) -> int:
    text = path.read_text(encoding="utf-8")
    n = text.count("\n") + (0 if text.endswith("\n") else 1)
    lang = "python" if path.suffix == ".py" else (
        "markdown" if path.suffix == ".md" else "text")
    lines.append(f"## `{arc}`  ·  {n} lines\n")
    lines.append(f"```{lang}")
    lines.append(text.rstrip("\n"))
    lines.append("```")
    lines.append("")
    return n


def collect(product: dict) -> List[Tuple[Path, str]]:
    """Every file that makes up the product, in a readable order."""
    files: List[Tuple[Path, str]] = []
    pkg = ROOT / product["package"]
    for path in sorted(pkg.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append((path, str(path.relative_to(ROOT))))
    for script in sorted(ROOT.glob("*.py")):
        files.append((script, script.name))
    tools = ROOT / "tools"
    if tools.is_dir():
        for script in sorted(tools.glob("*.py")):
            files.append((script, "tools/" + script.name))
    readme = ROOT / product["readme"]
    if readme.exists():
        files.append((readme, product["readme"]))
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        files.append((gitignore, ".gitignore"))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", default="handmade",
                        choices=sorted(PRODUCTS))
    args = parser.parse_args()
    product = PRODUCTS[args.product]

    lines = [
        f"# {product['title']} - Complete Source Code",
        "",
        "Every file of the generator, verbatim. Rebuild both workbooks with:",
        "",
        "```",
        f"python {product['build']}",
        f"python {product['build']} --blank -o \"{product['blank']}\"",
        "```",
        "",
        "Then check them:",
        "",
        "```",
        "python tools/validate_handmade_workbook.py",
        "python tools/check_handmade_sample.py",
        "```",
        "",
        "---",
        "",
    ]

    files = collect(product)
    total_lines = 0
    for path, arc in files:
        total_lines += emit_file(lines, path, arc)

    out = ROOT / product["out"]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{out.name}: {len(files)} files, {total_lines:,} source lines, "
          f"{out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
