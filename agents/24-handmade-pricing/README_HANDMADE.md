# Handmade Product Pricing & Profit Calculator

**A 40-tab Excel workbook that prices handmade products from their real cost.**

Materials, labour, packaging, postage and overhead go in. A price comes out -
a price that still pays the marketplace fee *and* leaves the margin you asked
for. Then the same workbook tracks what you actually sold, what it actually
earned, and which products are quietly paying you less than the minimum wage.

Built by **Novality Store**. Version 1.0.0. Pure Python + XlsxWriter - no
macros, no templates, no manual editing of a spreadsheet: the whole workbook is
generated from source.

---

## The one formula everything hangs on

```
price = (cost of one item + fixed fees) / (1 - target margin - fee rate)
```

Dividing rather than adding is the entire point. A marketplace fee is charged on
the **selling price**, not on the cost, so adding 6.5% to a cost leaves you
short on every single sale. Dividing by `(1 - fee rate)` makes the fee pay for
itself.

Cost of one item is built from five visible parts, each on its own tab:

| Part | Where it comes from |
| --- | --- |
| Materials | Bill of materials on **Material Usage**, or the craft tab |
| Labour | minutes ÷ 60 × the *loaded* hourly rate (your rate + payroll burden) |
| Packaging | matched components on **Packaging**, or the default |
| Postage you absorb | the shipping option's absorbed figure |
| Overhead | per unit, per hour, or monthly ÷ units a month - your choice on **Settings** |

Nothing is hidden: **Products** shows every part in its own column, so a price
can always be argued with.

---

## What is in the workbook

**40 tabs, 98,940 formulas, 321 drop-down validations, 271 defined names.**

| Group | Tabs |
| --- | --- |
| Set up | Start Here · Settings · Lists · Help |
| What you sell | Products · Variations · Bundles · Bundle Lines · Development |
| What it costs | Materials · Material Usage · Labor · Packaging · Shipping · Overhead · Waste Log |
| What it should cost | Retail Calculator · Wholesale Calculator · Profit & Break-Even · Scenarios |
| Making it | Crochet · Jewelry · Candles · Clothing · Woodworking · Digital · Batches |
| Selling it | Sales · Channels · Promotions · Price History · Competitors · Events |
| Trade | Wholesale Customers · Wholesale Orders · Print Quote |
| Reading it back | Dashboard · Reports · Print Costing · Print Order |

### The six craft calculators

Each one costs a product from the parts that craft actually uses, then writes
the result into the catalog:

* **Crochet** - yarn by weight or yardage, hooks, notions, gauge, difficulty
  factor, pattern.
* **Jewelry** - metal by the gram, findings, stones, wire, the metal price per
  gram.
* **Candles** - wax, fragrance load percentage, wicks, vessels, batch pouring
  with cure days and a melt/pour temperature log.
* **Clothing** - fabric by the metre, notions, pattern pieces, sizes, sewing
  minutes per seam type.
* **Woodworking** - board feet by species, hardware, finish, machine time,
  joinery time.
* **Digital** - patterns and printables: creation hours amortised across a
  forecast of sales, so the cost *per sale* falls as the file sells.

A product priced on a craft tab takes its material cost from that tab. If it
also has bill-of-materials rows, the formula on **Products** prefers the craft
figure rather than adding both - materials are never counted twice, and
`tools/check_handmade_sample.py` verifies that the formula still says so.

### The pages that leave the workbook

**Print Costing** (one product's full cost build-up and its bill of materials),
**Print Quote** (a wholesale quote on your letterhead, with trade discount, tax
and totals) and **Print Order** (a production docket: what to make, how many,
the materials for that quantity, and the steps to sign off). Each is laid out
for one portrait page.

---

## How the numbers stay honest

* **No typed-in summaries.** Dashboard, Reports, Scenarios and the three
  calculators read the registers with `SUMIFS`, `COUNTIFS`, `INDEX`/`MATCH` and
  `SUMPRODUCT`. Nothing can drift out of date.
* **No hidden scratch tab.** The "top five" and "needs attention" lists use
  hidden dense-rank columns (`COUNTIFS` + `MATCH`) rather than a secret Calc
  sheet, so the workbook has no tab you cannot see and check.
* **Live dates.** `TodayDate` is `TODAY()`, so reminders, aging, review windows
  and the monthly reports follow the calendar rather than the day the file was
  generated.
* **Excel 2010 safe.** No dynamic arrays, no `XLOOKUP`, `LET`, `IFS`, `MINIFS`,
  `TEXTJOIN`, `UNIQUE`, `FILTER` or `SORT`. Nothing that needs a 365
  subscription and nothing that spills.
* **Protected, not encrypted.** Every sheet is protected with the password
  `premium`; formula cells are locked and input cells are unlocked and shaded.
  Protection is a guard rail against overwriting a formula - it hides nothing.

---

## Build it

Requirements: Python 3.9+ and `xlsxwriter` (3.2 or newer). `openpyxl` is only
needed by the validation tools.

```bash
pip install xlsxwriter openpyxl

# the filled workbook, with the worked example
python3 build_handmade_workbook.py --today 2026-10-18

# the same workbook with every register empty
python3 build_handmade_workbook.py --blank \
    -o "output/Handmade Product Pricing & Profit Calculator (Blank).xlsx"
```

Both take about 25 seconds and write a ~2 MB file into `output/`.

### Every option

| Flag | What it does |
| --- | --- |
| `-o, --output PATH` | where to write the `.xlsx` |
| `--blank` | leave the registers empty (no example products) |
| `--no-protect` | do not protect the sheets (development only) |
| `--password PW` | sheet protection password (default `premium`) |
| `--author NAME` | document author / creator (default `Novality Store`) |
| `--shop NAME` | pre-fill the shop name on Settings |
| `--owner NAME` | pre-fill the maker / owner name |
| `--currency SYMBOL` | currency symbol, e.g. `$ £ € A$` |
| `--currency-code CODE` | three letter code, e.g. `USD`, `GBP` |
| `--year YEAR` | the year the reports open on |
| `--rate RATE` | what you pay yourself an hour |
| `--margin PCT` | target retail margin, e.g. `55` for 55% |
| `--wholesale-margin PCT` | target wholesale margin |
| `--wholesale-discount PCT` | trade price as % off retail, e.g. `50` |
| `--rounding RULE` | `None`, `Nearest 0.99`, `Nearest 0.95`, `Nearest 0.50`, `Nearest 1`, `Nearest 5`, `Up to whole 1`, `Up to whole 5` |
| `--transaction-fee PCT` | marketplace transaction fee, e.g. `6.5` |
| `--listing-fee AMOUNT` | fee to list one item |
| `--tax PCT` | sales tax / VAT rate |
| `--units SYSTEM` | `Metric` or `Imperial` |
| `--rows N` | scale every register to this many product rows |
| `--today DATE` | treat this ISO date as "today" for the example data |
| `--quiet` | print only the output path |

So a UK maker selling crochet at a 55% margin, priced to `£x.95`, paying
herself £18 an hour:

```bash
python3 build_handmade_workbook.py --currency "£" --currency-code GBP \
    --rate 18 --margin 55 --rounding "Nearest 0.95" --units Metric \
    --shop "Fern & Fold" --owner "Alice Bramley"
```

---

## Check it

Four tools, all of them runnable straight after a build:

```bash
python3 tools/validate_handmade_workbook.py          # both workbooks
python3 tools/check_handmade_sample.py               # the worked example
python3 tools/check_handmade_sample.py --blank \
    "output/Handmade Product Pricing & Profit Calculator (Blank).xlsx"
python3 tools/recalc_check.py                        # optional second opinion
```

`validate_handmade_workbook.py` is the gate. It scans the raw sheet XML for the
things that make Excel show *"We found a problem with some content"* - cached
`<v>None</v>` values, braces left in a formula, overlapping merges, single-cell
merges, links to sheets that do not exist - and then every one of the 98,940
formulas for unbalanced parentheses, unclosed quotes, a leading `==`, `#REF!`,
unrendered `{token}` leftovers and Excel-2011-and-later functions. It also
checks that each named input is unlocked, each named calculation is a locked
formula, every sheet is protected, and the document author is `Novality Store`.
It ends with a precedence check for `A5-B5/60` written where `(A5-B5)/60` was
meant - the one arithmetic bug that never produces a repair dialog.

`check_handmade_sample.py` reads the finished workbook through the register
specifications and checks that the example is a business that could exist:
unique, correctly-prefixed IDs; every product, material, bundle, customer,
channel and shipping reference resolving; 40+ sales spread over 90+ days and at
least two channels; quantities, prices, hours, discounts and fee rates inside
sane ranges; and no product costed twice.

Latest run:

```
[FILLED] Handmade Product Pricing & Profit Calculator.xlsx
  sheets         : 40
  formulas       : 98,940
  populated cells: 105,139
  validations    : 321
  defined names  : 271
  RESULT         : PASS

[BLANK] Handmade Product Pricing & Profit Calculator (Blank).xlsx
  formulas       : 98,940
  RESULT         : PASS

SAMPLE  products 14 · materials 31 · bom lines 51 · sales 57 over 150 days
        craft rows 16 · trade 5 shops / 10 orders        RESULT : PASS
circular groups found: 0
```

---

## The worked example

**Willow & Thread Handmade** (Maya Albright, Asheville NC): 14 products across
candles, crochet, jewellery, clothing, woodworking and two digital patterns,
31 materials, 51 bill-of-materials lines, 12 labour entries, 4 sales channels,
16 craft-tab rows, 3 bundles, 7 variations, 6 batches, 57 sales over 150 days,
4 promotions, 13 price changes, 10 competitors, 11 waste entries, 6 development
projects, 5 events, 5 wholesale shops and 10 trade orders.

It is deliberately not a tidy example. Two candle lines are healthy, a ring box
loses money at its current price, a couple of products sit below the margin
warning, one material is at its re-order point, and some sales were refunded -
so the Dashboard has something to warn about and the Reports tab has a worst
margin worth reading.

Build `--blank` for the same workbook with the registers empty and every
formula intact.

---

## How the source is organised

```
build_handmade_workbook.py          the entry point (17 lines)
handmade_pricing_spreadsheet/
    config.py        Config, Palette, the pricing constants, sheet sizes
    layout.py        Col, SheetSpec, Registry, [[Sheet.key]] rendering
    formats.py       FormatBook: every cell, chrome and conditional format
    writer.py        SheetWriter: banner, sections, KPI tiles, fields, grid
    names.py         the 21 cross-sheet lookup names (ProductIDs and friends)
    build.py         tab order, page builders, document properties
    sample_data.py   the worked example, register by register
    cli.py           argument parsing -> Config -> build_workbook
    sheets/          40 modules: 27 registers + 13 pages, and common.py,
                     the shared column factories, formula helpers and the
                     craft-tab contract (~8,000 lines in total)
tools/
    validate_handmade_workbook.py    the gate
    check_handmade_sample.py         the example must tie out
    recalc_check.py                  optional recalculation with `formulas`
    export_source_md.py              every source file into one .md
    make_download_zip.py             the two download archives
```

3,179 lines of package plumbing, 8,081 lines of sheets, 1,419 lines of tools.

```bash
python3 tools/export_source_md.py --product handmade   # SOURCE_CODE_HANDMADE.md
python3 tools/make_download_zip.py --product handmade  # download/*.zip
```

`download/handmade-pricing-calculator.zip` is what a customer gets (both
workbooks + a HOW TO RUN note); `handmade-pricing-calculator-source.zip` is
what you need to rebuild it with different rates, margins, currency or row
counts.

---

## Using it

1. Open **Start Here**. It walks through the first three steps and explains
   the maths.
2. Set the shop, the hourly rate, the fee schedule and the target margins on
   **Settings**. Everything else reads from there.
3. List materials on **Materials**, then give each product its bill of
   materials on **Material Usage** - or use a craft tab, which does both.
4. Read the suggested price on **Retail Calculator**, check the trade price on
   **Wholesale Calculator**, see how many you must sell on **Profit &
   Break-Even**, and compare five margins at once on **Scenarios**.
5. Record sales on **Sales**. **Dashboard** answers "how is this month going",
   **Reports** answers "how is the year going".

### Compatibility

Excel 2010 and later on Windows and Mac, Excel for the web, LibreOffice Calc,
Google Sheets and Numbers. No macros, so no security prompt and nothing a work
computer will refuse to open. Every file lives on your machine or your own
cloud folder; nothing is sent anywhere.

---

*Handmade Product Pricing & Profit Calculator - created by Novality Store,
version 1.0.0. Sheets are protected with the password `premium`.*
