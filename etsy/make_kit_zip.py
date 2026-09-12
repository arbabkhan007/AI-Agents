"""
make_kit_zip.py - bundle the complete Novality Store kit into ONE zip:

  products/   6 Excel workbooks (PREMIUM + BASIC, Festive + Minimal, EXAMPLE)
  etsy/       listing kit MD, 15 listing images, fonts + image scripts
  source      christmas_tracker package, entry point, tools, vendored xlsxwriter
  SOURCE_CODE.md   every Python file embedded in one Markdown document
  README.md   master guide + rebuild instructions

Run from the repo root:   python3 -m etsy.make_kit_zip
"""

import os
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Christmas_Gift_Tracker_COMPLETE_KIT.zip"
PREFIX = "Christmas_Gift_Tracker_COMPLETE_KIT"

DESCRIPTIONS = {
    "christmas_gift_tracker.py":
        "Entry point / CLI - builds every product workbook "
        "(--all --protect premium).",
    "christmas_tracker/__init__.py": "Package marker.",
    "christmas_tracker/config.py":
        "All constants: statuses, categories, columns, KPI map, occasions, "
        "presets - the single source of truth for every tab.",
    "christmas_tracker/theme.py":
        "Festive & Minimal colour themes (tab colours, series, soft tints).",
    "christmas_tracker/styles.py":
        "xlsxwriter format factory - every cell style used in the workbooks.",
    "christmas_tracker/demo.py":
        "The demo Model: recipients, gifts, orders, cards, stockings, "
        "to-dos, wish list + all aggregations (agg) for dashboards.",
    "christmas_tracker/workbook.py":
        "Workbook bootstrap: sheet order, tab colours, print setup, "
        "protection plumbing.",
    "christmas_tracker/book.py":
        "Book writer: title blocks, KPI cards, bars, charts, conditional "
        "formats, data validation, sheet protection + (c) Novality Store "
        "footer.",
    "christmas_tracker/sheets/__init__.py": "Sheet modules.",
    "christmas_tracker/sheets/common.py":
        "Shared sheet helpers: dropdowns (list_dv/fixed_dv), tables, "
        "headers.",
    "christmas_tracker/sheets/dashboard.py":
        "Dashboard tab: countdown band, KPI cards, progress bars, 6 "
        "charts, what's-left-to-do sentences, deadlines, per-recipient "
        "summary.",
    "christmas_tracker/sheets/gifts.py": "Gift Tracker tab.",
    "christmas_tracker/sheets/budget.py":
        "Budget tab: 10 categories, auto vs manual, alert banner.",
    "christmas_tracker/sheets/wishlist.py": "Wish List & Gift Ideas tab.",
    "christmas_tracker/sheets/shopping.py": "Shopping List tab.",
    "christmas_tracker/sheets/orders.py": "Online Order Tracker tab.",
    "christmas_tracker/sheets/wrapping.py": "Wrapping & Hiding tab.",
    "christmas_tracker/sheets/cards.py": "Christmas Card Tracker tab.",
    "christmas_tracker/sheets/stockings.py": "Stocking Stuffer tab.",
    "christmas_tracker/sheets/todo.py": "Christmas To-Do List tab.",
    "christmas_tracker/sheets/setup.py":
        "Setup tab: event, money, alerts, secret mode, your lists.",
    "christmas_tracker/sheets/guide.py": "Built-in Guide / manual tab.",
    "christmas_tracker/sheets/data.py":
        "Hidden _Data engine room: KPI formulas, deadline pool, lists.",
    "etsy/__init__.py": "Package marker.",
    "etsy/screenlib.py":
        "PIL rendering engine: emoji-aware text, fonts, tables, pills, "
        "charts, KPI cards - used to draw the listing images.",
    "etsy/screens.py":
        "Pixel 'screenshots' of every workbook tab, populated with the "
        "real demo data.",
    "etsy/make_listing_images.py":
        "Builds the 15 Etsy listing images (2400x1800 JPEG, <1 MB).",
    "etsy/make_kit_zip.py":
        "Bundles this complete kit zip + generates SOURCE_CODE.md.",
    "etsy/make_user_guide.py":
        "Builds the 12-page illustrated user-guide PDF (A4, 200 dpi) "
        "branded Novality Store.",
    "tools/make_banner_alpha.py":
        "Turns the raw AI banner art into the title-windowed PNG banners "
        "used on the cover sheet.",
}

SOURCE_FILES = list(DESCRIPTIONS.keys())

KIT_README = """# Christmas Gift Tracker — COMPLETE KIT
**Novality Store** • bundled {today}

Everything needed to sell, rebuild and extend the Christmas Gift Tracker
spreadsheet on Etsy, in one folder.

```
Christmas_Gift_Tracker_COMPLETE_KIT/
├── README.md                 <- you are here (master guide)
├── SOURCE_CODE.md            <- every Python file in one Markdown document
├── Christmas_Gift_Tracker_User_Guide.pdf  <- 12-page illustrated user guide
├── products/                 <- the 6 finished Excel workbooks (ready to sell)
├── etsy/
│   ├── LISTING_KIT.md        <- SEO title, 13 tags, description, alt texts
│   ├── images/               <- 15 listing images (2400x1800 JPEG, <1 MB)
│   ├── fonts/                <- OFL fonts used to render the images
│   ├── screenlib.py          <- image engine (emoji text, charts, tables)
│   ├── screens.py            <- pixel "screenshots" of every tab
│   ├── make_listing_images.py<- rebuild all 15 images: python3 -m etsy.make_listing_images
│   └── make_kit_zip.py       <- rebuild this zip: python3 -m etsy.make_kit_zip
├── christmas_gift_tracker.py <- build CLI (entry point)
├── christmas_tracker/        <- the spreadsheet generator (13 modules + 14 sheets)
├── tools/make_banner_alpha.py
├── assets/                   <- banner art used by cover sheet + hero image
└── xlsxwriter/               <- vendored xlsxwriter 3.2.9 (no pip needed)
```

## 1. The product (ready to sell)

| File | What it is |
|------|------------|
| `products/Christmas_Gift_Tracker_PREMIUM_Festive.xlsx` | Flagship - 13 tabs, 2,500+ formulas, 6 charts, 56 dropdowns, festive theme |
| `products/Christmas_Gift_Tracker_PREMIUM_Minimal.xlsx` | Same engine, minimal theme |
| `products/Christmas_Gift_Tracker_PREMIUM_Festive_EXAMPLE.xlsx` | Filled-in demo of the premium file |
| `products/Christmas_Gift_Tracker_BASIC_Festive.xlsx` | Basic edition - 7 tabs, ~1,245 formulas |
| `products/Christmas_Gift_Tracker_BASIC_Minimal.xlsx` | Basic edition, minimal theme |
| `products/Christmas_Gift_Tracker_BASIC_Festive_EXAMPLE.xlsx` | Filled-in demo of the basic file |

- Works in **Excel 2016+ / Microsoft 365 (Win & Mac)** and **Google Sheets**
  (File -> Import -> Upload -> Replace spreadsheet).
- **No macros.** All formula cells are **locked** (password: `premium`) so
  buyers can't break the maths; every input cell is open.
- Author/branding: **Novality Store** (baked into file properties, cover
  sheet and every tab footer).

## 2. The Etsy listing

Everything is in **`etsy/LISTING_KIT.md`**: title (129 chars), 13 tags
(<=20 chars each), the full 3,200-char description, alt texts for the 15
images and a publish checklist. Upload `etsy/images/01_hero.jpg` ..
`15_faq.jpg` in order - image 01 becomes the thumbnail.

## 3. Rebuilding everything from source

Requires Python 3.10+ and Pillow (`pip install pillow`) - xlsxwriter is
vendored, openpyxl is only needed for verification.

```bash
# rebuild all 6 workbooks (formulas locked with password 'premium')
python3 christmas_gift_tracker.py --all --protect premium

# rebuild the 15 listing images (needs etsy/fonts/ + assets/)
python3 -m etsy.make_listing_images

# re-bundle this kit zip
python3 -m etsy.make_kit_zip
```

See **SOURCE_CODE.md** for the annotated source of every file.

## 4. Licences

- Product workbooks: (c) Novality Store - personal use, one household per
  purchase, no resale or redistribution.
- Python source: same repository licence as the original repo.
- Fonts in `etsy/fonts/`: SIL Open Font License (Poppins, Gelasio, Playfair
  Display, Caveat, JetBrains Mono, Noto Color Emoji).
- Vendored xlsxwriter: BSD-2-Clause (John McNamara).
"""


def build_source_md():
    parts = [
        "# Christmas Gift Tracker — Complete Source Code\n\n",
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


def add_dir(z, src, arcdir, skip_prefixes=(".git", "__pycache__", ".pytest_cache")):
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
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # master README
        z.writestr(os.path.join(PREFIX, "README.md"), KIT_README.format(
            today=date.today().isoformat()))
        # SOURCE_CODE.md
        z.writestr(os.path.join(PREFIX, "SOURCE_CODE.md"), source_md)
        # products
        for fn in sorted(os.listdir(os.path.join(ROOT, "products"))):
            if fn.endswith(".xlsx"):
                z.write(os.path.join(ROOT, "products", fn),
                        os.path.join(PREFIX, "products", fn))
                count += 1
        # etsy kit (listing md, images, fonts, scripts)
        z.write(os.path.join(ROOT, "etsy", "LISTING_KIT.md"),
                os.path.join(PREFIX, "etsy", "LISTING_KIT.md"))
        count += add_dir(z, os.path.join(ROOT, "etsy", "images"),
                         os.path.join(PREFIX, "etsy", "images"))
        count += add_dir(z, os.path.join(ROOT, "etsy", "fonts"),
                         os.path.join(PREFIX, "etsy", "fonts"))
        for fn in ("__init__.py", "screenlib.py", "screens.py",
                   "make_listing_images.py", "make_kit_zip.py",
                   "make_user_guide.py"):
            z.write(os.path.join(ROOT, "etsy", fn),
                    os.path.join(PREFIX, "etsy", fn))
            count += 1
        # spreadsheet source
        z.write(os.path.join(ROOT, "christmas_gift_tracker.py"),
                os.path.join(PREFIX, "christmas_gift_tracker.py"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "christmas_tracker"),
                         os.path.join(PREFIX, "christmas_tracker"))
        # tools + assets (only the two finished banners)
        z.write(os.path.join(ROOT, "tools", "make_banner_alpha.py"),
                os.path.join(PREFIX, "tools", "make_banner_alpha.py"))
        count += 1
        for fn in ("banner_festive.png", "banner_minimal.png"):
            z.write(os.path.join(ROOT, "assets", fn),
                    os.path.join(PREFIX, "assets", fn))
            count += 1
        # the illustrated user-guide PDF (if built)
        guide = os.path.join(ROOT, "Christmas_Gift_Tracker_User_Guide.pdf")
        if os.path.exists(guide):
            z.write(guide, os.path.join(PREFIX,
                                        "Christmas_Gift_Tracker_User_Guide.pdf"))
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
    # sanity: every key artifact present
    for must in ("products/Christmas_Gift_Tracker_PREMIUM_Festive.xlsx",
                 "Christmas_Gift_Tracker_User_Guide.pdf",
                 "etsy/LISTING_KIT.md", "etsy/images/01_hero.jpg",
                 "etsy/images/15_faq.jpg", "SOURCE_CODE.md", "README.md",
                 "christmas_tracker/book.py", "xlsxwriter/__init__.py"):
        assert any(n.endswith(must) for n in names), f"missing {must}"
    print("  content : all key artifacts present")


if __name__ == "__main__":
    main()
