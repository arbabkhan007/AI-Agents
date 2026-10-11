#!/usr/bin/env python3
"""
Write every source file of a generator into one clean markdown document.

    python tools/export_source_md.py                      # pet sitting
    python tools/export_source_md.py --product meal       # meal planner
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

PET_SECTIONS = [
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

MEAL_SECTIONS = [
    ("1. Run it",
     "Save the files below keeping these exact paths, then run the one "
     "liner. Nothing else is needed - no project file, no build step.\n\n"
     "```bash\n"
     "pip install XlsxWriter\n"
     "python build_meal_planner_workbook.py\n"
     "```\n\n"
     "The workbook lands in "
     "`output/Meal Planner & Grocery List.xlsx`.",
     ["build_meal_planner_workbook.py"]),
    ("2. The package",
     "Configuration, the formula template engine, cell formats, the sheet "
     "writer and the demo data. These are the parts every tab leans on.",
     ["meal_planner_spreadsheet/__init__.py",
      "meal_planner_spreadsheet/__main__.py",
      "meal_planner_spreadsheet/cli.py",
      "meal_planner_spreadsheet/config.py",
      "meal_planner_spreadsheet/layout.py",
      "meal_planner_spreadsheet/formats.py",
      "meal_planner_spreadsheet/writer.py",
      "meal_planner_spreadsheet/names.py",
      "meal_planner_spreadsheet/build.py",
      "meal_planner_spreadsheet/sample_data.py"]),
    ("3. The registers",
     "One module per data tab. Each returns a list of columns with their "
     "formulas, and the writer turns that into a formatted, validated, "
     "protected sheet.",
     ["meal_planner_spreadsheet/sheets/__init__.py",
      "meal_planner_spreadsheet/sheets/lists.py",
      "meal_planner_spreadsheet/sheets/settings.py",
      "meal_planner_spreadsheet/sheets/household.py",
      "meal_planner_spreadsheet/sheets/recipes.py",
      "meal_planner_spreadsheet/sheets/recipe_ingredients.py",
      "meal_planner_spreadsheet/sheets/ingredients.py",
      "meal_planner_spreadsheet/sheets/meal_plan.py",
      "meal_planner_spreadsheet/sheets/grocery_list.py",
      "meal_planner_spreadsheet/sheets/pantry.py",
      "meal_planner_spreadsheet/sheets/staples.py",
      "meal_planner_spreadsheet/sheets/leftovers.py",
      "meal_planner_spreadsheet/sheets/food_waste.py",
      "meal_planner_spreadsheet/sheets/meal_prep.py",
      "meal_planner_spreadsheet/sheets/dietary_filters.py",
      "meal_planner_spreadsheet/sheets/rotation.py",
      "meal_planner_spreadsheet/sheets/food_safety.py",
      "meal_planner_spreadsheet/sheets/fridge_freezer.py",
      "meal_planner_spreadsheet/sheets/grocery_spending.py",
      "meal_planner_spreadsheet/sheets/store_prices.py",
      "meal_planner_spreadsheet/sheets/stores.py",
      "meal_planner_spreadsheet/sheets/events.py",
      "meal_planner_spreadsheet/sheets/sustainability.py",
      "meal_planner_spreadsheet/sheets/recipe_costs.py",
      "meal_planner_spreadsheet/sheets/converter.py"]),
    ("4. The pages",
     "The tabs that read the registers: the dashboard, the weekly and "
     "monthly planners, the nutrition log, the budget, the goals, the "
     "reports, the welcome tab, the three printable pages and the help tab.",
     ["meal_planner_spreadsheet/sheets/dashboard.py",
      "meal_planner_spreadsheet/sheets/weekly_planner.py",
      "meal_planner_spreadsheet/sheets/monthly_planner.py",
      "meal_planner_spreadsheet/sheets/nutrition.py",
      "meal_planner_spreadsheet/sheets/budget.py",
      "meal_planner_spreadsheet/sheets/goals.py",
      "meal_planner_spreadsheet/sheets/reports.py",
      "meal_planner_spreadsheet/sheets/start_here.py",
      "meal_planner_spreadsheet/sheets/print_week.py",
      "meal_planner_spreadsheet/sheets/print_shopping.py",
      "meal_planner_spreadsheet/sheets/print_recipe.py",
      "meal_planner_spreadsheet/sheets/help.py"]),
    ("5. Quality checks (optional)",
     "Not needed to build the workbook - these are the checks that keep it "
     "honest. The first two need `openpyxl`, the third needs `formulas`.",
     ["tools/validate_meal_workbook.py",
      "tools/check_meal_sample.py",
      "tools/recalc_check.py",
      "tools/export_source_md.py",
      "tools/make_download_zip.py"]),
]

PET_APPENDIX = """\
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

MEAL_APPENDIX = """\
## Appendix

### A. Build the workbook

```bash
python build_meal_planner_workbook.py                       # demo data
python build_meal_planner_workbook.py --blank               # empty workbook
python build_meal_planner_workbook.py --household "The Khans"
python build_meal_planner_workbook.py --cook "Ayesha"
python build_meal_planner_workbook.py --currency "£" --units Imperial
python build_meal_planner_workbook.py --budget 150          # a week
python build_meal_planner_workbook.py --year 2027
python build_meal_planner_workbook.py --week-start Sunday
python build_meal_planner_workbook.py --rows 300            # more capacity
python build_meal_planner_workbook.py --password secret     # own password
python build_meal_planner_workbook.py --author "Your Name"
```

### B. Check it

```bash
python tools/validate_meal_workbook.py "output/Meal Planner & Grocery List.xlsx"
python tools/check_meal_sample.py "output/Meal Planner & Grocery List.xlsx"

# real recalculation - build a small workbook first, the full one is slow
python build_meal_planner_workbook.py --rows 100 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

### C. Colour palette

Defined once in `meal_planner_spreadsheet/config.py`; every sheet module
reads it from there.

| Colour | Hex | Used for |
| --- | --- | --- |
| ink | `#1E2C22` | titles, darkest text |
| primary | `#2F5E43` | header bands, tab colours |
| primary_mid | `#4E8A63` | section bands, navigation strip |
| primary_soft | `#E2EFE6` | totals, alternating rows |
| accent | `#D9703C` | terracotta accents, KPI money tiles |
| accent_soft | `#FBE9DC` | soft accent panels |
| input_bg | `#FFFDF7` | cells you type in (warm cream) |
| calc_bg | `#EFF4F0` | calculated cells (soft sage) |
| grey_text | `#5A6560` | notes and secondary text |
| line | `#C2D4C7` | hairlines and borders |
| good | `#D9F2E4` / `#0E6B45` | fresh, on target, in stock |
| warn | `#FFF1CF` / `#8A5A00` | use soon, close to budget |
| bad | `#FBD9DD` / `#9C1C2E` | expired, over budget, bin it |
| info | `#DEE8FA` / `#2A4A8B` | neutral information |
| note_bg | `#F7FAF8` | note boxes |

### D. How a formula is written

No sheet module contains a hard coded column letter.  Formulas are
templates, and the layout engine expands them:

```
"=IF({recipe}{r}=\"\",\"\",SUMIFS([[Recipe Ingredients.line_cost]],"
 "[[Recipe Ingredients.recipe]],{recipe}{r}))"
```

| Token | Becomes |
| --- | --- |
| `{r}` | the current Excel row number |
| `{key}` | the column letter of that column on the same sheet |
| `{key_first}` / `{key_last}` | the top and bottom of that column |
| `[[Sheet.key]]` | the whole data range of that column |
| `[[Sheet.key#r]]` | one cell of that column, on the same row |

So a column can be moved, widened or deleted in the sheet module and every
formula follows.

### E. File tree

```
build_meal_planner_workbook.py
README_MEAL.md
SOURCE_CODE_MEAL.md
meal_planner_spreadsheet/
    __init__.py   __main__.py   cli.py        config.py
    layout.py     formats.py    writer.py     names.py
    build.py      sample_data.py
    sheets/
        __init__.py    lists.py        settings.py      household.py
        recipes.py     recipe_ingredients.py            ingredients.py
        meal_plan.py   grocery_list.py pantry.py        staples.py
        leftovers.py   food_waste.py   meal_prep.py     dietary_filters.py
        rotation.py    food_safety.py  fridge_freezer.py grocery_spending.py
        store_prices.py stores.py      events.py        sustainability.py
        recipe_costs.py converter.py   dashboard.py     weekly_planner.py
        monthly_planner.py nutrition.py budget.py       goals.py
        reports.py     start_here.py   print_week.py    print_shopping.py
        print_recipe.py help.py
tools/
    validate_meal_workbook.py   check_meal_sample.py   recalc_check.py
    export_source_md.py         make_download_zip.py
```
"""

PRODUCTS = {
    "pet": {
        "title": "Pet Sitting & Dog Walking Business Spreadsheet",
        "subtitle": "Complete source code of the generator that writes the "
                    ".xlsx product",
        "output": "SOURCE_CODE.md",
        "sections": PET_SECTIONS,
        "appendix": PET_APPENDIX,
        "cover": [
            "A pure Python program that writes a 27 tab Excel workbook for a "
            "pet sitting and dog walking business: clients, pets, bookings, "
            "visit logs, pricing, invoices, payments, expenses, mileage, "
            "staff, inventory, reminders, a dashboard, reports and a budget.",
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
        ],
        "options": [
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
        ],
        "script": "build_pet_sitting_workbook.py",
    },
    "meal": {
        "title": "Automated Meal Planner & Grocery List Spreadsheet",
        "subtitle": "Complete source code of the generator that writes the "
                    ".xlsx product",
        "output": "SOURCE_CODE_MEAL.md",
        "sections": MEAL_SECTIONS,
        "appendix": MEAL_APPENDIX,
        "cover": [
            "A pure Python program that writes a 36 tab Excel workbook for a "
            "household: a weekly and monthly meal planner, a recipe book "
            "with costings, an automatic grocery list, a pantry with use-by "
            "dates, a food budget, a nutrition log and printable pages for "
            "the fridge door.",
            "",
            "**What it produces**",
            "",
            "| | |",
            "| --- | --- |",
            "| Tabs | 36, all visible |",
            "| Formulas | about 79,000, all Excel 2010 safe |",
            "| Author | Novality Store |",
            "| Protection | every sheet, password `premium` |",
            "| Charts | none - the numbers are the report |",
            "| Example data | 38 recipes, 62 ingredients, 107 planned meals |",
            "| Dependency | XlsxWriter (openpyxl only for the checks) |",
        ],
        "options": [
            "-o, --output PATH     where to write the file",
            "--blank               no example data, just the empty workbook",
            "--no-protect          leave the sheets unlocked",
            "--password TEXT       protection password (default: premium)",
            "--author TEXT         document author  (default: Novality Store)",
            "--household TEXT      household name on the Settings tab",
            "--cook TEXT           main cook's name",
            "--currency SYMBOL     currency symbol  (default: $)",
            "--currency-code TEXT  three letter code  (default: USD)",
            "--units {Metric,Imperial}  measurement system",
            "--week-start {Monday,Sunday}",
            "--year N              planning year",
            "--budget N            weekly grocery budget",
            "--servings N          default servings per meal",
            "--rows N              rows of capacity in the big registers",
            "--today YYYY-MM-DD    pretend it is this date (for the demo data)",
        ],
        "script": "build_meal_planner_workbook.py",
    },
}


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read().rstrip("\n")


def blurb(path: str, limit: int = 78) -> str:
    """First sentence of the module docstring, as a one line description."""
    try:
        text = ast.get_docstring(ast.parse(read(path))) or ""
    except (SyntaxError, OSError):                     # pragma: no cover
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


def cover(product: dict) -> list:
    """The short front page: what it is, how to run it, the key numbers."""
    return [
        f"# {product['title']}",
        "",
        f"*{product['subtitle']}*",
        "",
    ] + product["cover"] + [
        "",
        "**How to run it**",
        "",
        "```bash",
        "pip install XlsxWriter",
        f"python {product['script']}",
        "```",
        "",
        "Every formula cell is locked and every sheet is protected with the "
        "password `premium`, while the cream coloured cells you are meant to "
        "type in stay open.",
        "",
        "**Useful options**",
        "",
        "```text",
    ] + product["options"] + [
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
    parser.add_argument("--product", choices=sorted(PRODUCTS), default="pet")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args(argv)

    product = PRODUCTS[args.product]
    output = args.output or product["output"]

    lines = cover(product)
    total = 0
    files = 0
    for number, (heading, _intro, paths) in enumerate(product["sections"],
                                                      start=1):
        for path in paths:
            count = len(read(path).splitlines())
            total += count
            files += 1
            lines.append(
                f"| {number} | [`{path}`](#{anchor(path)}) | {count} | "
                f"{blurb(path) or '-'} |")

    lines += ["", "---", ""]

    for heading, intro, paths in product["sections"]:
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

    lines += [product["appendix"], ""]
    lines += [f"*{files} files, {total:,} lines of Python.*", ""]

    with open(output, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    size = os.path.getsize(output)
    print(f"{output}  ({files} files, {total:,} lines, "
          f"{size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
