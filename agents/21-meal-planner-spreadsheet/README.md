# 21 - Meal Planner & Grocery List Spreadsheet

Generates the **Meal Planner & Grocery List** Excel workbook: a 36-tab meal
planning system covering recipes, meal plans, automatic grocery lists,
pantry stock, batch cooking, food waste, nutrition and budgeting.

## What this project contains

| Path | What it is |
| --- | --- |
| `build_meal_planner_workbook.py` | Entry point - builds the workbook |
| `meal_planner_spreadsheet/` | The generator package (config, layout, formats, writer, names, build, sample data) |
| `meal_planner_spreadsheet/sheets/` | One module per workbook tab (36 tabs) |
| `tools/` | Validation, sample checks, recalculation and export scripts |
| `README_MEAL.md` | Product readme shipped with the download |
| `HOW_TO_USE_MEAL.md` | Product guide shipped with the download |

## Build

```bash
pip install -r requirements.txt
python build_meal_planner_workbook.py          # filled workbook
python build_meal_planner_workbook.py --blank  # blank workbook
python build_meal_planner_workbook.py --pair   # both
```

The workbook lands in `output/Meal Planner & Grocery List.xlsx`.

## Check

```bash
python tools/check_meal_sample.py           # sample data consistency
python tools/validate_meal_workbook.py      # Excel 2010 formula safety,
                                            # protection, print areas
python tools/recalc_check.py                # optional: full recalculation
```

## Export

```bash
python tools/export_source_md.py --product meal    # SOURCE_CODE_MEAL.md
python tools/make_download_zip.py --product meal   # download/*.zip
```

## Design notes

- **Excel 2010 safe.** No XLOOKUP, IFS, FILTER, LET or dynamic arrays.
  Formulas use SUMIFS, COUNTIFS, SUMPRODUCT, INDEX/MATCH and TEXT.
- **Protected.** Every sheet has `sheetProtection` with password
  `premium`; input cells are unlocked and cream-coloured.
- **Printable.** Every sheet has a print area, repeated header rows and
  fits to page width.
- **Named ranges** (`Weekly_Budget`, `Rotation_Gap_Days`, ...) keep the
  formulas readable and the Settings tab in charge.
- **Self-referencing lookups** are written as `INDEX(MATCH(1,INDEX((a=x)*
  (b=y),0),0))` - the Excel 2010 way to match two columns without CSE
  arrays.
