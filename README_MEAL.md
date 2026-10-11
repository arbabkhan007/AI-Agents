# Automated Meal Planner & Grocery List Spreadsheet

A 36 tab Excel workbook that plans your meals and writes your shopping
list: a weekly and monthly planner, a recipe book with costings, an
automatic grocery list, a pantry with use-by dates, a food budget, a
nutrition log and printable pages for the fridge door.

* **36 tabs** - Start Here, Dashboard, Weekly Planner, Monthly Planner,
  Settings, Lists, Household, Recipes, Recipe Ingredients, Ingredients,
  Meal Plan, Grocery List, Pantry, Staples, Leftovers, Food Waste, Meal
  Prep, Dietary Filters, Nutrition, Budget, Recipe Costs, Converter,
  Rotation, Food Safety, Fridge & Freezer, Grocery Spending, Store Prices,
  Stores, Events, Goals, Sustainability, Reports, Print Week, Print
  Shopping, Print Recipe, Help.
* **About 79,000 formulas**, every one of them Excel 2010 safe - no
  dynamic arrays, no `XLOOKUP`, no `IFS`, nothing that needs array entry.
  It opens in Excel 2010 and later, Google Sheets, LibreOffice and Numbers.
* **No charts.** The numbers are the report; the Dashboard and Reports tabs
  read straight from the registers so nothing can go stale.
* **Every sheet is protected** with the password `premium`. Formula cells
  are locked; the cream coloured input cells are not.
* **Two workbooks ship in the box**: one filled with three weeks of example
  meals for a family of four, one completely blank.

---

## What is in this repository

| Path | What it is |
| --- | --- |
| `output/Meal Planner & Grocery List.xlsx` | The workbook, filled with example data. |
| `output/Meal Planner & Grocery List (Blank - No Example Data).xlsx` | The same workbook, empty. |
| `HOW_TO_USE_MEAL.md` | The walkthrough for the buyer. |
| `ETSY_LISTING_MEAL.md` | The listing copy: titles, description, tags, image plan. |
| `SOURCE_CODE_MEAL.md` | The whole generator in one readable document. |
| `build_meal_planner_workbook.py` | The front door - builds the workbook. |
| `meal_planner_spreadsheet/` | The generator package. |
| `tools/` | The quality checks and the packers. |
| `etsy-images/` | The listing images at 1024 px. |
| `etsy-images-2000px/` | The same images at 2000 px, which is what Etsy wants. |
| `download/` | The zips. |

---

## Build it

```bash
pip install XlsxWriter
python build_meal_planner_workbook.py
```

The workbook lands in `output/Meal Planner & Grocery List.xlsx`.

```bash
python build_meal_planner_workbook.py --blank          # empty workbook
python build_meal_planner_workbook.py --household "The Khans"
python build_meal_planner_workbook.py --cook "Ayesha"
python build_meal_planner_workbook.py --currency "£" --currency-code GBP
python build_meal_planner_workbook.py --units Imperial
python build_meal_planner_workbook.py --week-start Sunday
python build_meal_planner_workbook.py --year 2027
python build_meal_planner_workbook.py --budget 150
python build_meal_planner_workbook.py --servings 2
python build_meal_planner_workbook.py --rows 400        # more capacity
python build_meal_planner_workbook.py --password secret
python build_meal_planner_workbook.py --author "Your Name"
python build_meal_planner_workbook.py --today 2027-01-04
```

---

## Check it

```bash
python tools/validate_meal_workbook.py "output/Meal Planner & Grocery List.xlsx"
python tools/check_meal_sample.py "output/Meal Planner & Grocery List.xlsx"

# a real recalculation - build a small workbook first, the full one is slow
python build_meal_planner_workbook.py --rows 100 -o /tmp/small.xlsx
python tools/recalc_check.py /tmp/small.xlsx
```

`validate_meal_workbook.py` checks the tab order, that every sheet is
protected, that no formula uses a function newer than Excel 2010, that
every cross-sheet reference points at a tab that really exists, and that
there are no charts or drawings.

`check_meal_sample.py` checks that the example data hangs together - every
ingredient, recipe, store, unit and meal slot used on one tab exists on the
tab it is looked up from.

`recalc_check.py` builds a small workbook, recalculates it with the
`formulas` library and compares fifteen cells against values worked out
independently in Python.

---

## Pack it

```bash
python tools/export_source_md.py --product meal     # SOURCE_CODE_MEAL.md
python tools/upscale_etsy_images.py --prefix meal-  # 2000 px images
python tools/make_etsy_pack.py --product meal       # the buyer's zip
python tools/make_download_zip.py --product meal    # the developer's zip
```

---

## How the workbook is written

The workbook is generated, not hand built, so it can be rebuilt for a
different household, currency, measurement system or country in one
command.

* **`meal_planner_spreadsheet/config.py`** - everything a shop owner might
  want to re-brand: the palette, the currency, the nutrition targets, the
  reminder windows, the row capacity of every register.
* **`meal_planner_spreadsheet/layout.py`** - the formula template engine.
  No sheet module contains a hard coded column letter:

  ```
  "=IF({recipe}{r}=\"\",\"\",SUMIFS([[Recipe Ingredients.line_cost]],"
   "[[Recipe Ingredients.recipe]],{recipe}{r}))"
  ```

  `{r}` is the current row, `{key}` is the column letter of that column on
  the same sheet, `{key_first}` / `{key_last}` are the top and bottom of
  the column, and `[[Sheet.key]]` is the whole data range of that column on
  another tab. Columns can be moved, widened or deleted and every formula
  follows.
* **`meal_planner_spreadsheet/formats.py`** - one place builds every cell
  format, so the look stays consistent: warm cream inputs, soft sage
  calculated cells, herb green headers, terracotta accents.
* **`meal_planner_spreadsheet/writer.py`** - turns a column list into a
  real sheet: title band, frozen header row, one pre-built row per register
  slot with its validation, conditional format and formula, then the
  protection that locks the calculated columns.
* **`meal_planner_spreadsheet/names.py`** - the defined names, so formulas
  read `=Weekly_Budget` instead of `=Settings!$B$19`.
* **`meal_planner_spreadsheet/sheets/`** - one module per tab.
* **`meal_planner_spreadsheet/sample_data.py`** - the three weeks of example
  meals that go into the filled workbook.

Rankings are `COUNTIFS` based rather than `RANK.EQ`, so nothing needs the
`_xlfn.` prefix that newer functions require when written straight into the
file format.

---

## Palette

| Colour | Hex | Used for |
| --- | --- | --- |
| ink | `#1E2C22` | titles, darkest text |
| primary | `#2F5E43` | header bands, tab colours |
| primary_mid | `#4E8A63` | section bands, navigation strip |
| primary_soft | `#E2EFE6` | totals, alternating rows |
| accent | `#D9703C` | terracotta accents, money KPI tiles |
| input_bg | `#FFFDF7` | cells you type in |
| calc_bg | `#EFF4F0` | calculated cells |
| good | `#D9F2E4` / `#0E6B45` | fresh, on target |
| warn | `#FFF1CF` / `#8A5A00` | use soon, close to budget |
| bad | `#FBD9DD` / `#9C1C2E` | expired, over budget |

---

*Author: Novality Store. Version 1.0.0.*
