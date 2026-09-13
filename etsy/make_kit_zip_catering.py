"""
make_kit_zip_catering.py - bundle the complete Novality Store catering kit
into ONE zip:

  products/   6 Excel workbooks (PREMIUM + BASIC, Classic + Fresh, EXAMPLE)
  etsy/       listing kit MD, 15 listing images, fonts + image scripts
  source      catering_tracker package, entry point, banner tool,
              vendored xlsxwriter
  SOURCE_CODE.md   every Python file embedded in one Markdown document
  README.md   master guide + rebuild instructions

Run from the repo root:   python3 -m etsy.make_kit_zip_catering
"""

import os
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Catering_Business_Manager_COMPLETE_KIT.zip"
PREFIX = "Catering_Business_Manager_COMPLETE_KIT"

DESCRIPTIONS = {
    "catering_business_tracker.py":
        "Entry point / CLI - builds every product workbook "
        "(--all --outdir products/ --protect premium).",
    "catering_tracker/__init__.py": "Package marker.",
    "catering_tracker/config.py":
        "All constants: tabs, editions, statuses, columns, KPI map, lists - "
        "the single source of truth for every tab.",
    "catering_tracker/theme.py":
        "Classic & Fresh colour themes (tab colours, series, soft tints).",
    "catering_tracker/styles.py":
        "xlsxwriter format factory - every cell style used in the "
        "workbooks.",
    "catering_tracker/demo.py":
        "The demo Model: clients, events, quote, menu, inventory, "
        "shopping, expenses, income, staff, equipment, suppliers, "
        "checklists + all aggregations (agg) for dashboards.",
    "catering_tracker/workbook.py":
        "Workbook bootstrap: sheet order, tab colours, print setup, "
        "protection plumbing.",
    "catering_tracker/book.py":
        "Book writer: title blocks, KPI cards, bars, charts, conditional "
        "formats, data validation, sheet protection + (c) Novality Store "
        "footer.",
    "catering_tracker/sheets/__init__.py": "Sheet modules.",
    "catering_tracker/sheets/common.py":
        "Shared sheet helpers: dropdowns (list_dv/fixed_dv), tables, "
        "headers.",
    "catering_tracker/sheets/dashboard.py":
        "Dashboard tab: banner cover, KPI cards, pipeline pills, 4 "
        "charts, upcoming events, payments due, alert cards.",
    "catering_tracker/sheets/clients.py": "Clients tab.",
    "catering_tracker/sheets/events.py":
        "Events tab: the booking pipeline with live profit per event.",
    "catering_tracker/sheets/quote.py":
        "Quote Builder tab: inputs, outputs, big price panel.",
    "catering_tracker/sheets/menu.py": "Menu Costing tab.",
    "catering_tracker/sheets/inventory.py": "Inventory tab.",
    "catering_tracker/sheets/shopping.py":
        "Shopping List tab - built from event menus minus stock.",
    "catering_tracker/sheets/expenses.py": "Expenses tab.",
    "catering_tracker/sheets/income.py": "Payments / income tab.",
    "catering_tracker/sheets/staff.py": "Staff & Shifts tab.",
    "catering_tracker/sheets/equipment.py": "Equipment tab.",
    "catering_tracker/sheets/suppliers.py": "Suppliers tab.",
    "catering_tracker/sheets/calendar.py": "Event Calendar tab.",
    "catering_tracker/sheets/reports.py":
        "P&L & Reports tab: season P&L, monthly chart, best performers.",
    "catering_tracker/sheets/tax.py": "Tax Tracker tab.",
    "catering_tracker/sheets/checklists.py":
        "Checklists tab: prep week, shopping, event day, wrap-up.",
    "catering_tracker/sheets/invoice.py":
        "Invoice & Proposal tab - branded, pre-filled invoice.",
    "catering_tracker/sheets/setup.py":
        "Setup tab: business details, money rules, editable lists.",
    "catering_tracker/sheets/guide.py": "Start Here guide tab.",
    "catering_tracker/sheets/data.py":
        "Hidden _Data engine room: KPI formulas, month pool, lists.",
    "etsy/__init__.py": "Package marker.",
    "etsy/catering_lib.py":
        "PIL rendering engine: emoji-aware text, fonts, tables, pills, "
        "charts, KPI cards - used to draw the listing images.",
    "etsy/catering_screens.py":
        "Pixel 'screenshots' of every workbook tab, populated with the "
        "real demo data.",
    "etsy/make_listing_images_catering.py":
        "Builds the 15 Etsy listing images (2400x1800 JPEG, <1 MB).",
    "etsy/make_user_guide_catering.py":
        "Builds the 12-page illustrated user-guide PDF (A4, 200 dpi) "
        "branded Novality Store.",
    "etsy/make_kit_zip_catering.py":
        "Bundles this complete kit zip + generates SOURCE_CODE.md.",
    "tools/make_banner_alpha_catering.py":
        "Turns the raw AI banner art into the title-windowed PNG banners "
        "used on the cover sheet.",
}

SOURCE_FILES = list(DESCRIPTIONS.keys())

KIT_README = """# Catering Business Manager — COMPLETE KIT
**Novality Store** • bundled {today}

Everything needed to sell, rebuild and extend the Catering Business
Manager spreadsheet on Etsy, in one folder.

```
Catering_Business_Manager_COMPLETE_KIT/
├── README.md                 <- you are here (master guide)
├── SOURCE_CODE.md            <- every Python file in one Markdown document
├── Catering_Business_Manager_User_Guide.pdf  <- 12-page illustrated user guide
├── products/                 <- the 6 finished Excel workbooks (ready to sell)
├── etsy/
│   ├── LISTING_KIT_CATERING.md <- SEO title, 13 tags, description, alt texts
│   ├── images_catering/      <- 15 listing images (2400x1800 JPEG, <1 MB)
│   ├── fonts/                <- OFL fonts used to render the images
│   ├── catering_lib.py       <- image engine (emoji text, charts, tables)
│   ├── catering_screens.py   <- pixel "screenshots" of every tab
│   ├── make_listing_images_catering.py  <- rebuild: python3 -m etsy.make_listing_images_catering
│   ├── make_user_guide_catering.py      <- rebuild: python3 -m etsy.make_user_guide_catering
│   └── make_kit_zip_catering.py         <- rebuild this zip: python3 -m etsy.make_kit_zip_catering
├── catering_business_tracker.py <- build CLI (entry point)
├── catering_tracker/         <- the spreadsheet generator (7 modules + 19 sheets)
├── tools/make_banner_alpha_catering.py
├── assets/                   <- banner art used by cover sheet + hero image
└── xlsxwriter/               <- vendored xlsxwriter 3.2.9 (no pip needed)
```

## 1. The product (ready to sell)

| File | What it is |
|------|------------|
| `products/Catering_Business_Manager_PREMIUM_Classic.xlsx` | Flagship - 20 tabs, 1,500+ formulas, 11 charts, 75 dropdowns, classic theme |
| `products/Catering_Business_Manager_PREMIUM_Fresh.xlsx` | Same engine, fresh theme |
| `products/Catering_Business_Manager_PREMIUM_Classic_EXAMPLE.xlsx` | Filled-in demo of the premium file |
| `products/Catering_Business_Manager_BASIC_Classic.xlsx` | Basic edition - 9 tabs, ~600 formulas |
| `products/Catering_Business_Manager_BASIC_Fresh.xlsx` | Basic edition, fresh theme |
| `products/Catering_Business_Manager_BASIC_Classic_EXAMPLE.xlsx` | Filled-in demo of the starter file |

- Works in **Excel 2016+ / Microsoft 365 (Win & Mac)** and **Google Sheets**
  (File -> Import -> Upload -> Replace spreadsheet).
- **No macros.** All formula cells are **locked** (password: `premium`) so
  buyers can't break the maths; every input cell is open.
- Author/branding: **Novality Store** (baked into file properties, cover
  sheet and every tab footer).

## 2. The Etsy listing

Everything is in **`etsy/LISTING_KIT_CATERING.md`**: title (132 chars),
13 tags (<=20 chars each), the full description, alt texts for the 15
images, pricing and a publish checklist. Upload
`etsy/images_catering/01_hero.jpg` .. `15_faq.jpg` in order - image 01
becomes the thumbnail.

## 3. Rebuilding everything from source

Requires Python 3.10+ and Pillow (`pip install pillow`) - xlsxwriter is
vendored, openpyxl is only needed for verification.

```bash
# rebuild all 6 workbooks (formulas locked with password 'premium')
python3 catering_business_tracker.py --all --outdir products/ --protect premium

# rebuild the 15 listing images (needs etsy/fonts/ + assets/)
python3 -m etsy.make_listing_images_catering

# rebuild the 12-page user guide
python3 -m etsy.make_user_guide_catering

# re-bundle this kit zip
python3 -m etsy.make_kit_zip_catering
```

See **SOURCE_CODE.md** for the annotated source of every file.

## 4. Licences

- Product workbooks: (c) Novality Store - one business per purchase, no
  resale or redistribution.
- Python source: same repository licence as the original repo.
- Fonts in `etsy/fonts/`: SIL Open Font License (Poppins, Gelasio, Playfair
  Display, Caveat, JetBrains Mono, Noto Color Emoji).
- Vendored xlsxwriter: BSD-2-Clause (John McNamara).
"""


def build_source_md():
    parts = [
        "# Catering Business Manager — Complete Source Code\n\n",
        "**Novality Store** • bundled " + date.today().isoformat() + "\n\n",
        "Every Python file of the project in one document, for future "
        "reference.\nRebuild commands are in the kit `README.md`.\n\n"
        "## Contents\n\n",
    ]
    for i, f in enumerate(SOURCE_FILES, 1):
        desc = DESCRIPTIONS[f]
        parts.append(f"{i}. **`{f}`** — {desc}\n")
    parts.append("\n---\n\n")
    for f in SOURCE_FILES:
        path = os.path.join(ROOT, f)
        code = open(path, encoding="utf8").read()
        n_lines = code.count("\n") + 1
        parts.append(f"\n## `{f}`\n\n")
        parts.append(f"*{DESCRIPTIONS[f]}* ({n_lines:,} lines)\n\n")
        parts.append("```python\n" + code.rstrip("\n") + "\n```\n\n")
        parts.append("---\n")
    return "".join(parts)


def add_dir(z, src, arcdir,
             skip_prefixes=(".git", "__pycache__", ".pytest_cache")):
    n = 0
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames
                       if d not in ("__pycache__", ".pytest_cache")]
        for fn in sorted(filenames):
            if fn.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, src)
            z.write(full, os.path.join(arcdir, rel))
            n += 1
    return n


def main():
    out = os.path.join(ROOT, ZIP_NAME)
    source_md = build_source_md()
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        # master README
        z.writestr(os.path.join(PREFIX, "README.md"),
                   KIT_README.format(today=date.today().isoformat()))
        # SOURCE_CODE.md
        z.writestr(os.path.join(PREFIX, "SOURCE_CODE.md"), source_md)
        # products — ONLY the catering workbooks (never the Christmas ones)
        for fn in sorted(os.listdir(os.path.join(ROOT, "products"))):
            if fn.startswith("Catering_Business_Manager") and \
                    fn.endswith(".xlsx"):
                z.write(os.path.join(ROOT, "products", fn),
                        os.path.join(PREFIX, "products", fn))
                count += 1
        # etsy kit (listing md, images, fonts, scripts)
        z.write(os.path.join(ROOT, "etsy", "LISTING_KIT_CATERING.md"),
                os.path.join(PREFIX, "etsy", "LISTING_KIT_CATERING.md"))
        count += add_dir(z, os.path.join(ROOT, "etsy", "images_catering"),
                         os.path.join(PREFIX, "etsy", "images_catering"))
        count += add_dir(z, os.path.join(ROOT, "etsy", "fonts"),
                         os.path.join(PREFIX, "etsy", "fonts"))
        for fn in ("__init__.py", "catering_lib.py", "catering_screens.py",
                   "make_listing_images_catering.py",
                   "make_user_guide_catering.py", "make_kit_zip_catering.py"):
            z.write(os.path.join(ROOT, "etsy", fn),
                    os.path.join(PREFIX, "etsy", fn))
            count += 1
        # spreadsheet source
        z.write(os.path.join(ROOT, "catering_business_tracker.py"),
                os.path.join(PREFIX, "catering_business_tracker.py"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "catering_tracker"),
                         os.path.join(PREFIX, "catering_tracker"))
        # tools + assets (only the two finished banners)
        z.write(os.path.join(ROOT, "tools", "make_banner_alpha_catering.py"),
                os.path.join(PREFIX, "tools",
                             "make_banner_alpha_catering.py"))
        count += 1
        for fn in ("banner_classic.png", "banner_fresh.png"):
            z.write(os.path.join(ROOT, "assets", fn),
                    os.path.join(PREFIX, "assets", fn))
            count += 1
        # the illustrated user-guide PDF
        guide = os.path.join(ROOT, "Catering_Business_Manager_User_Guide.pdf")
        assert os.path.exists(guide), "build the user guide first"
        z.write(guide, os.path.join(
            PREFIX, "Catering_Business_Manager_User_Guide.pdf"))
        count += 1
        # vendored xlsxwriter (no pycache / dist-info)
        count += add_dir(z, os.path.join(ROOT, "xlsxwriter"),
                         os.path.join(PREFIX, "xlsxwriter"))
        total = len(z.namelist())
    # verify
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
        assert bad is None, f"corrupt member: {bad}"
        names = z.namelist()
    size = os.path.getsize(out)
    print(f"built {ZIP_NAME}")
    print(f"  members : {total}")
    print(f"  files   : {count}")
    print(f"  size    : {size/1024/1024:.1f} MB")
    print(f"  zip ok  : integrity verified")
    # sanity: every key artifact present, and NO christmas artifacts leaked
    for must in ("products/Catering_Business_Manager_PREMIUM_Classic.xlsx",
                 "products/Catering_Business_Manager_BASIC_Fresh.xlsx",
                 "Catering_Business_Manager_User_Guide.pdf",
                 "etsy/LISTING_KIT_CATERING.md",
                 "etsy/images_catering/01_hero.jpg",
                 "etsy/images_catering/15_faq.jpg",
                 "SOURCE_CODE.md", "README.md",
                 "catering_tracker/book.py", "xlsxwriter/__init__.py"):
        assert any(n.endswith(must) for n in names), f"missing {must}"
    assert not any("Christmas" in n for n in names), \
        "christmas artifact leaked into catering kit"
    print("  content : all key artifacts present, no Christmas files")


if __name__ == "__main__":
    main()
