"""Write every source file of the generator into one clean markdown document.

    python tools/export_source_md.py                 # -> SOURCE_CODE.md
    python tools/export_source_md.py -o /tmp/src.md

Handy when the code has to travel somewhere that is not a git checkout:
one file, every module in reading order, each in a fenced block with its
real path above it, plus a short description taken from the module's own
docstring so the two can never disagree.

The layout is deliberately plain - a short cover, a contents table, then
the code - so it reads well in any markdown viewer and survives being
printed to PDF.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE = "Pet Sitting & Dog Walking Business Spreadsheet"
SUBTITLE = "Complete source code of the generator that writes the .xlsx product"

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
     "One module per data tab. Each returns a list of columns with their "
     "formulas, and the writer turns that into a formatted, validated, "
     "protected sheet.",
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

APPENDIX = """\
## Appendix

### A. Build the workbook

```bash
python build_pet_sitting_workbook.py                       # demo data
python build_pet_sitting_workbook.py --blank               # empty workbook
python build_pet_sitting_workbook.py --business "Paws & Claws"
python build_pet_sitting_workbook.py --currency "£" --unit miles
python build_pet_sitting_workbook.py --rows 1000           # more capacity
python build_pet_sitting_workbook.py --password secret     # own password
python build_pet_sitting_workbook.py --author "Your Name"
```

### B. Check it

```bash
python tools/validate_workbook.py "output/Pet Sitting Business Spreadsheet.xlsx"
python tools/check_sample_data.py "output/Pet Sitting Business Spreadsheet.xlsx"

# real recalculation - build a small workbook first, the full one is slow
python build_pet_sitting_workbook.py --rows 120 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

### C. Colour palette

Defined once in `pet_sitting_spreadsheet/config.py`; every sheet module
reads it from there.

| Colour | Hex | Used for |
| --- | --- | --- |
| ink | `#0F172A` | titles, darkest text, overview tab colours |
| primary | `#4338CA` | header bands, profit series |
| primary_mid | `#6366F1` | section bands, revenue series, data bars |
| primary_soft | `#EEF2FF` | table headers, alternating rows |
| accent | `#F59E0B` | KPI tiles, accents, print tab colours |
| accent_soft | `#FFFBEB` | soft accent panels |
| input_bg | `#FFFDF5` | cells you type in (cream) |
| calc_bg | `#F1F5F9` | calculated cells (grey) |
| grey_text | `#64748B` | notes and secondary text |
| line | `#CBD5E1` | hairlines and borders |
| good | `#D1FAE5` / `#047857` | paid, in stock, resolved |
| warn | `#FEF3C7` / `#B45309` | due soon, low stock |
| bad | `#FFE4E6` / `#BE123C` | overdue, out of stock, expired |
| info | `#DBEAFE` / `#1D4ED8` | neutral information |
| note_bg | `#F8FAFC` | note boxes |

### D. File tree

```
build_pet_sitting_workbook.py
README.md
SOURCE_CODE.md
pet_sitting_spreadsheet/
    __init__.py   __main__.py   cli.py        config.py
    layout.py     formats.py    writer.py     names.py
    build.py      sample_data.py
    sheets/
        __init__.py   common.py     lists.py       settings.py
        services.py   clients.py    pets.py        bookings.py
        visits.py     health.py     incidents.py   messages.py
        invoices.py   payments.py   expenses.py    mileage.py
        staff.py      inventory.py  reminders.py   calc.py
        dashboard.py  reports.py    budget.py      start_here.py
        printables.py help_tab.py
tools/
    validate_workbook.py   check_sample_data.py   recalc_check.py
    export_source_md.py    make_download_zip.py
```
"""


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read().rstrip("\n")


def blurb(path: str, limit: int = 78) -> str:
    """First sentence of the module docstring, as a one line description."""
    try:
        text = ast.get_docstring(ast.parse(read(path))) or ""
    except SyntaxError:                                  # pragma: no cover
        text = ""
    text = " ".join(text.split())
    cut = re.search(r"\.(\s|$)", text)
    if cut:
        text = text[:cut.start()]
    text = text.strip().rstrip(".")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


def anchor(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"\s+", "-", slug.strip())


def cover() -> list:
    """The short front page: what it is, how to run it, the key numbers."""
    return [
        f"# {TITLE}",
        "",
        f"*{SUBTITLE}*",
        "",
        "A pure Python program that writes a 27 tab Excel workbook for a pet "
        "sitting and dog walking business: clients, pets, bookings, visit "
        "logs, pricing, invoices, payments, expenses, mileage, staff, "
        "inventory, reminders, a dashboard, reports and a budget.",
        "",
        "**What it produces**",
        "",
        "| | |",
        "| --- | --- |",
        "| Tabs | 27 (26 visible + 1 hidden calculation engine) |",
        "| Formulas | about 50,800, all Excel 2010 safe |",
        "| Author | Novality Store |",
        "| Protection | every sheet, password `premium` |",
        "| Example data | 9 clients, 12 pets, 32 bookings, 23 invoices |",
        "| Dependency | XlsxWriter (openpyxl only for the checks) |",
        "",
        "**How to run it**",
        "",
        "```bash",
        "pip install XlsxWriter",
        "python build_pet_sitting_workbook.py",
        "```",
        "",
        "The workbook lands in `output/Pet Sitting Business Spreadsheet.xlsx`.",
        "Every formula cell is locked and every sheet is protected with the "
        "password `premium`, while the cream coloured cells you are meant to "
        "type in stay open.",
        "",
        "**Useful options**",
        "",
        "```text",
        "-o, --output PATH     where to write the file",
        "--blank               no example data, just the empty workbook",
        "--no-protect          leave the sheets unlocked",
        "--password TEXT       protection password (default: premium)",
        "--author TEXT         document author  (default: Novality Store)",
        "--business TEXT       business name on the cover and invoices",
        "--currency SYMBOL     currency symbol  (default: $)",
        "--unit {km,miles}     mileage unit",
        "--rows N              rows of capacity in the big registers",
        "--today YYYY-MM-DD    pretend it is this date (for the demo data)",
        "```",
        "",
        "Excel 2010 safe throughout: no dynamic arrays, no `XLOOKUP`, no "
        "`IFS`, nothing that needs array entry - so it opens in Excel 2010 "
        "and later, Google Sheets, LibreOffice and Numbers.",
        "",
        "---",
        "",
        "## Contents",
        "",
        "| # | File | Lines | What it does |",
        "| --- | --- | --- | --- |",
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="SOURCE_CODE.md")
    args = parser.parse_args(argv)

    lines = cover()
    total = 0
    files = 0
    for number, (heading, _intro, paths) in enumerate(SECTIONS, start=1):
        for path in paths:
            count = len(read(path).splitlines())
            total += count
            files += 1
            lines.append(
                f"| {number} | [`{path}`](#{anchor(path)}) | {count} | "
                f"{blurb(path) or '-'} |")

    lines += ["", "---", ""]

    for heading, intro, paths in SECTIONS:
        lines += [f"## {heading}", "", intro, ""]
        for path in paths:
            code = read(path)
            count = len(code.splitlines())
            note = blurb(path, limit=120)
            lines.append(f"### `{path}`")
            lines.append("")
            if note:
                lines.append(f"{note} *({count} lines)*")
            else:
                lines.append(f"*({count} lines)*")
            # four backticks, so a fence inside a docstring cannot
            # close the block early
            lines += ["", "````python", code, "````", ""]
        lines += ["---", ""]

    lines += [APPENDIX, ""]
    lines += [f"*{files} files, {total:,} lines of Python.*", ""]

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    size = os.path.getsize(args.output)
    print(f"{args.output}  ({files} files, {total:,} lines, "
          f"{size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
