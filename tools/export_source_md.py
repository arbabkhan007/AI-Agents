"""Write every source file of the generator into one markdown document.

    python tools/export_source_md.py                 # -> SOURCE_CODE.md
    python tools/export_source_md.py -o /tmp/src.md

Handy when the code has to travel somewhere that is not a git checkout:
one file, every module in reading order, each in a fenced block with its
real path above it, plus a short description taken from the module's own
docstring so the two can never disagree.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE = "Pet Sitting & Dog Walking Business Spreadsheet"
SUBTITLE = ("Complete source code of the generator that writes the "
            "`.xlsx` product.")

#: (section heading, intro paragraph, [file paths])
SECTIONS = [
    ("1. Run it",
     "Save the files below keeping these exact paths, then run the one "
     "liner. Nothing else is needed - no project file, no build step.\n\n"
     "```bash\n"
     "pip install XlsxWriter\n"
     "python build_pet_sitting_workbook.py\n"
     "```\n\n"
     "The workbook lands in `output/Pet Sitting Business Spreadsheet.xlsx`.",
     ["build_pet_sitting_workbook.py"]),
    ("2. The package",
     "Configuration, the formula template engine, cell formats, the sheet "
     "writer and the demo data. These are the parts every tab leans on.",
     ["pet_sitting_spreadsheet/__init__.py",
      "pet_sitting_spreadsheet/__main__.py",
      "pet_sitting_spreadsheet/cli.py",
      "pet_sitting_spreadsheet/config.py",
      "pet_sitting_spreadsheet/layout.py",
      "pet_sitting_spreadsheet/formats.py",
      "pet_sitting_spreadsheet/writer.py",
      "pet_sitting_spreadsheet/names.py",
      "pet_sitting_spreadsheet/build.py",
      "pet_sitting_spreadsheet/sample_data.py"]),
    ("3. The registers",
     "One module per data tab. Each returns a `SheetSpec` - a list of "
     "columns with their formulas - and the writer turns that into a "
     "formatted, validated, protected sheet.",
     ["pet_sitting_spreadsheet/sheets/__init__.py",
      "pet_sitting_spreadsheet/sheets/common.py",
      "pet_sitting_spreadsheet/sheets/lists.py",
      "pet_sitting_spreadsheet/sheets/settings.py",
      "pet_sitting_spreadsheet/sheets/services.py",
      "pet_sitting_spreadsheet/sheets/clients.py",
      "pet_sitting_spreadsheet/sheets/pets.py",
      "pet_sitting_spreadsheet/sheets/bookings.py",
      "pet_sitting_spreadsheet/sheets/visits.py",
      "pet_sitting_spreadsheet/sheets/health.py",
      "pet_sitting_spreadsheet/sheets/incidents.py",
      "pet_sitting_spreadsheet/sheets/messages.py",
      "pet_sitting_spreadsheet/sheets/invoices.py",
      "pet_sitting_spreadsheet/sheets/payments.py",
      "pet_sitting_spreadsheet/sheets/expenses.py",
      "pet_sitting_spreadsheet/sheets/mileage.py",
      "pet_sitting_spreadsheet/sheets/staff.py",
      "pet_sitting_spreadsheet/sheets/inventory.py",
      "pet_sitting_spreadsheet/sheets/reminders.py"]),
    ("4. The pages",
     "The tabs that read the registers: the hidden calculation engine, the "
     "dashboard, the reports, the planner, the welcome tab, the printable "
     "pages and the help tab.",
     ["pet_sitting_spreadsheet/sheets/calc.py",
      "pet_sitting_spreadsheet/sheets/dashboard.py",
      "pet_sitting_spreadsheet/sheets/reports.py",
      "pet_sitting_spreadsheet/sheets/budget.py",
      "pet_sitting_spreadsheet/sheets/start_here.py",
      "pet_sitting_spreadsheet/sheets/printables.py",
      "pet_sitting_spreadsheet/sheets/help_tab.py"]),
    ("5. Quality checks (optional)",
     "Not needed to build the workbook - these are the checks that keep it "
     "honest. The first two need `openpyxl`, the third needs `formulas`.",
     ["tools/validate_workbook.py",
      "tools/check_sample_data.py",
      "tools/recalc_check.py",
      "tools/export_source_md.py",
      "tools/make_download_zip.py"]),
]


def blurb(path: str) -> str:
    """First sentence of the module docstring, as a one line description."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        source = handle.read()
    try:
        text = ast.get_docstring(ast.parse(source)) or ""
    except SyntaxError:                                  # pragma: no cover
        text = ""
    text = " ".join(text.split())
    if not text:
        return ""
    cut = re.search(r"\.(\s|$)", text)
    if cut:
        text = text[:cut.start()]
    return text.strip().rstrip(".")


def anchor(heading: str) -> str:
    slug = heading.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug.strip())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="SOURCE_CODE.md")
    args = parser.parse_args(argv)

    lines = [f"# {TITLE} - source code", "", SUBTITLE, ""]
    lines += [
        "Writes a 27 tab `.xlsx` workbook with about 50,000 formulas: client "
        "and pet records, bookings, visit logs, pricing, invoices, payments, "
        "expenses, mileage, a dashboard, reports and automatic reminders. "
        "Document author is **Novality Store**; every formula cell is locked "
        "and every sheet protected with the password **`premium`**, while "
        "the cells you are meant to type in stay open.",
        "",
        "Pure Python, one dependency. Tested on XlsxWriter 3.2.0 and on the "
        "much older 0.3.0, so it does not rely on anything recent. The "
        "workbook itself is Excel 2010 safe - no dynamic arrays, no "
        "`XLOOKUP`, no `IFS`, nothing that needs array entry - and it opens "
        "in Google Sheets, LibreOffice and Numbers.",
        "",
        "```bash",
        "python build_pet_sitting_workbook.py --help",
        "",
        "  -o, --output PATH     where to write the file",
        "  --blank               no example data, just the empty workbook",
        "  --no-protect          leave the sheets unlocked",
        "  --password TEXT       protection password (default: premium)",
        "  --author TEXT         document author  (default: Novality Store)",
        "  --business TEXT       business name on the cover and invoices",
        "  --currency SYMBOL     currency symbol  (default: $)",
        "  --unit {km,miles}     mileage unit",
        "  --rows N              rows of capacity in the big registers",
        "  --today YYYY-MM-DD    pretend it is this date (for the demo data)",
        "```",
        "",
        "---",
        "",
        "## Contents",
        "",
    ]

    for heading, _intro, paths in SECTIONS:
        lines.append(f"* [{heading}](#{anchor(heading)})")
        for path in paths:
            lines.append(f"  * [`{path}`](#{anchor(path)})")
    lines += ["", "---", ""]

    total = 0
    for heading, intro, paths in SECTIONS:
        lines += [f"## {heading}", "", intro, ""]
        for path in paths:
            full = os.path.join(ROOT, path)
            with open(full, encoding="utf-8") as handle:
                code = handle.read().rstrip("\n")
            count = len(code.splitlines())
            total += count
            note = blurb(path)
            lines.append(f"### `{path}`")
            lines.append("")
            if note:
                lines.append(f"{note}. *({count} lines)*")
            else:
                lines.append(f"*({count} lines)*")
            # four backticks, so a fence inside a docstring cannot
            # close the block early
            lines += ["", "````python", code, "````", ""]
        lines.append("---")
        lines.append("")

    lines += [f"*{total:,} lines of Python in "
              f"{sum(len(p) for _h, _i, p in SECTIONS)} files.*", ""]

    out = args.output
    with open(out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    size = os.path.getsize(out)
    print(f"{out}  ({total:,} lines of source, {size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
