"""
make_kit_zip_crochet.py - bundle the complete Novality Store crochet kit
into ONE zip:

  products/   6 Excel workbooks (PREMIUM + BASIC, Berry + Mint, EXAMPLE)
  etsy/       listing kit MD, 15 listing images, fonts + image scripts
  source      crochet_tracker package, entry point, banner tool,
              vendored xlsxwriter
  SOURCE_CODE.md   every Python file embedded in one Markdown document
  README.md   master guide + rebuild instructions

Run from the repo root:   python3 -m etsy.make_kit_zip_crochet
"""

import os
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Crochet_Craft_Fair_Tracker_COMPLETE_KIT.zip"
PREFIX = "Crochet_Craft_Fair_Tracker_COMPLETE_KIT"

DESCRIPTIONS = {
    "crochet_craft_fair_tracker.py":
        "Entry point / CLI - builds every product workbook "
        "(--all --outdir products/ --protect premium).",
    "crochet_tracker/__init__.py": "Package marker.",
    "crochet_tracker/config.py":
        "All constants: tabs, editions, statuses, columns, KPI map, "
        "lists - the single source of truth for every tab.",
    "crochet_tracker/theme.py":
        "Berry & Mint colour themes (tab colours, series, soft tints).",
    "crochet_tracker/styles.py":
        "xlsxwriter format factory - every cell style used in the "
        "workbooks.",
    "crochet_tracker/demo.py":
        "The demo business: products, materials, production batches, "
        "events, sales, packing + all aggregations (agg) for the "
        "dashboards and listing images.",
    "crochet_tracker/workbook.py":
        "Workbook bootstrap: sheet order, tab colours, print setup, "
        "protection plumbing.",
    "crochet_tracker/book.py":
        "Book writer: title blocks, KPI cards, bars, charts, conditional "
        "formats, data validation, sheet protection + (c) Novality Store "
        "footer.",
    "crochet_tracker/sheets/__init__.py": "Sheet modules.",
    "crochet_tracker/sheets/common.py":
        "Shared sheet helpers: dropdowns (list_dv/fixed_dv), tables, "
        "headers.",
    "crochet_tracker/sheets/dashboard.py":
        "Dashboard tab: banner cover, KPI cards, pipeline pills, 4 "
        "charts, best performers, restock radar alerts.",
    "crochet_tracker/sheets/catalog.py": "Product Catalog tab.",
    "crochet_tracker/sheets/materials.py":
        "Yarn & Materials tab: the stash with costs and reorder flags.",
    "crochet_tracker/sheets/production.py":
        "Made & Stocked tab: production batches, live stock counts.",
    "crochet_tracker/sheets/events.py":
        "Craft Fairs tab: the season with live profit per fair.",
    "crochet_tracker/sheets/sales.py": "Sales Log tab.",
    "crochet_tracker/sheets/eventprofit.py":
        "Event Profit tab: money in / money out, breakeven and ROI.",
    "crochet_tracker/sheets/reorder.py":
        "Reorder List tab - products and materials to buy, priced.",
    "crochet_tracker/sheets/packing.py":
        "Packing Checklist tab - four tick-lists per fair.",
    "crochet_tracker/sheets/pricing.py":
        "Pricing Calculator tab: true cost, margin price, charm price.",
    "crochet_tracker/sheets/monthly.py":
        "Monthly Summary tab: revenue, costs and net per month.",
    "crochet_tracker/sheets/setup.py":
        "Lists & Settings tab: studio basics + editable dropdown lists.",
    "crochet_tracker/sheets/guide.py": "Start Here guide tab.",
    "crochet_tracker/sheets/data.py":
        "Hidden _Data engine room: KPI formulas, month pool, lists.",
    "etsy/__init__.py": "Package marker.",
    "etsy/crochet_lib.py":
        "PIL rendering engine: emoji-aware text, fonts, tables, pills, "
        "charts, KPI cards - used to draw the listing images.",
    "etsy/crochet_screens.py":
        "Pixel 'screenshots' of every workbook tab, populated with the "
        "real demo data.",
    "etsy/make_listing_images_crochet.py":
        "Builds the 15 Etsy listing images (2400x1800 JPEG, <1 MB).",
    "etsy/make_user_guide_crochet.py":
        "Builds the 12-page illustrated user-guide PDF (A4, 200 dpi) "
        "branded Novality Store.",
    "etsy/make_kit_zip_crochet.py":
        "Bundles this complete kit zip + generates SOURCE_CODE.md.",
    "tools/make_banner_alpha_crochet.py":
        "Turns the raw AI banner art into the title-windowed PNG banners "
        "used on the cover sheet.",
}

SOURCE_FILES = list(DESCRIPTIONS.keys())

KIT_README = """# Crochet Craft Fair Tracker — COMPLETE KIT
**Novality Store** • bundled {today}

Everything needed to sell, rebuild and extend the Crochet Craft Fair
Tracker spreadsheet on Etsy, in one folder.

```
Crochet_Craft_Fair_Tracker_COMPLETE_KIT/
├── README.md                 <- you are here (master guide)
├── SOURCE_CODE.md            <- every Python file in one Markdown document
├── Crochet_Craft_Fair_Tracker_User_Guide.pdf  <- 12-page illustrated user guide
├── products/                 <- the 6 finished Excel workbooks (ready to sell)
├── etsy/
│   ├── LISTING_KIT_CROCHET.md <- SEO title, 13 tags, description, alt texts
│   ├── images_crochet/       <- 15 listing images (2400x1800 JPEG, <1 MB)
│   ├── fonts/                <- OFL fonts used to render the images
│   ├── crochet_lib.py        <- image engine (emoji text, charts, tables)
│   ├── crochet_screens.py    <- pixel "screenshots" of every tab
│   ├── make_listing_images_crochet.py  <- rebuild: python3 -m etsy.make_listing_images_crochet
│   ├── make_user_guide_crochet.py      <- rebuild: python3 -m etsy.make_user_guide_crochet
│   └── make_kit_zip_crochet.py         <- rebuild this zip: python3 -m etsy.make_kit_zip_crochet
├── crochet_craft_fair_tracker.py <- build CLI (entry point)
├── crochet_tracker/          <- the spreadsheet generator (7 modules + 15 sheets)
├── tools/make_banner_alpha_crochet.py
├── assets/                   <- banner art used by cover sheet + hero image
└── xlsxwriter/               <- vendored xlsxwriter 3.2.9 (no pip needed)
```

## 1. The product (ready to sell)

| File | What it is |
|------|------------|
| `products/Crochet_Craft_Fair_Tracker_PREMIUM_Berry.xlsx` | Flagship - 14 tabs, 1,250+ formulas, 12 charts, berry theme |
| `products/Crochet_Craft_Fair_Tracker_PREMIUM_Mint.xlsx` | Same engine, mint theme |
| `products/Crochet_Craft_Fair_Tracker_PREMIUM_Berry_EXAMPLE.xlsx` | Filled-in demo of the premium file |
| `products/Crochet_Craft_Fair_Tracker_BASIC_Berry.xlsx` | Basic edition - 8 tabs, ~400 formulas |
| `products/Crochet_Craft_Fair_Tracker_BASIC_Mint.xlsx` | Basic edition, mint theme |
| `products/Crochet_Craft_Fair_Tracker_BASIC_Berry_EXAMPLE.xlsx` | Filled-in demo of the starter file |

- Works in **Excel 2016+ / Microsoft 365 (Win & Mac)** and **Google Sheets**
  (File -> Import -> Upload -> Replace spreadsheet).
- **No macros.** All formula cells are **locked** (password: `premium`) so
  buyers can't break the maths; every input cell is open.
- Author/branding: **Novality Store** (baked into file properties, cover
  sheet and every tab footer).

## 2. The Etsy listing

Everything is in **`etsy/LISTING_KIT_CROCHET.md`**: title, 13 tags
(<=20 chars each), the full description, alt texts for the 15 images,
pricing and a publish checklist. Upload
`etsy/images_crochet/01_hero.jpg` .. `15_faq.jpg` in order - image 01
becomes the thumbnail.

## 3. Rebuilding everything from source

Requires Python 3.10+ and Pillow (`pip install pillow`) - xlsxwriter is
vendored, openpyxl is only needed for verification.

```bash
# rebuild all 6 workbooks (formulas locked with password 'premium')
python3 crochet_craft_fair_tracker.py --all --outdir products/ --protect premium

# rebuild the 15 listing images (needs etsy/fonts/ + assets/)
python3 -m etsy.make_listing_images_crochet

# rebuild the 12-page user guide
python3 -m etsy.make_user_guide_crochet

# re-bundle this kit zip
python3 -m etsy.make_kit_zip_crochet
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
        "# Crochet Craft Fair Tracker — Complete Source Code\n\n",
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
        # products — ONLY the crochet workbooks (never the other products)
        for fn in sorted(os.listdir(os.path.join(ROOT, "products"))):
            if fn.startswith("Crochet_Craft_Fair_Tracker") and \
                    fn.endswith(".xlsx"):
                z.write(os.path.join(ROOT, "products", fn),
                        os.path.join(PREFIX, "products", fn))
                count += 1
        # etsy kit (listing md, images, fonts, scripts)
        z.write(os.path.join(ROOT, "etsy", "LISTING_KIT_CROCHET.md"),
                os.path.join(PREFIX, "etsy", "LISTING_KIT_CROCHET.md"))
        count += add_dir(z, os.path.join(ROOT, "etsy", "images_crochet"),
                         os.path.join(PREFIX, "etsy", "images_crochet"))
        count += add_dir(z, os.path.join(ROOT, "etsy", "fonts"),
                         os.path.join(PREFIX, "etsy", "fonts"))
        for fn in ("__init__.py", "crochet_lib.py", "crochet_screens.py",
                   "make_listing_images_crochet.py",
                   "make_user_guide_crochet.py", "make_kit_zip_crochet.py"):
            z.write(os.path.join(ROOT, "etsy", fn),
                    os.path.join(PREFIX, "etsy", fn))
            count += 1
        # spreadsheet source
        z.write(os.path.join(ROOT, "crochet_craft_fair_tracker.py"),
                os.path.join(PREFIX, "crochet_craft_fair_tracker.py"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "crochet_tracker"),
                         os.path.join(PREFIX, "crochet_tracker"))
        # tools + assets (only the two finished banners)
        z.write(os.path.join(ROOT, "tools", "make_banner_alpha_crochet.py"),
                os.path.join(PREFIX, "tools",
                             "make_banner_alpha_crochet.py"))
        count += 1
        for fn in ("banner_berry.png", "banner_mint.png"):
            z.write(os.path.join(ROOT, "assets", fn),
                    os.path.join(PREFIX, "assets", fn))
            count += 1
        # the illustrated user-guide PDF
        guide = os.path.join(ROOT, "Crochet_Craft_Fair_Tracker_User_Guide.pdf")
        assert os.path.exists(guide), "build the user guide first"
        z.write(guide, os.path.join(
            PREFIX, "Crochet_Craft_Fair_Tracker_User_Guide.pdf"))
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
    # sanity: every key artifact present, and NO other-product artifacts leaked
    for must in ("products/Crochet_Craft_Fair_Tracker_PREMIUM_Berry.xlsx",
                 "products/Crochet_Craft_Fair_Tracker_BASIC_Mint.xlsx",
                 "Crochet_Craft_Fair_Tracker_User_Guide.pdf",
                 "etsy/LISTING_KIT_CROCHET.md",
                 "etsy/images_crochet/01_hero.jpg",
                 "etsy/images_crochet/15_faq.jpg",
                 "SOURCE_CODE.md", "README.md",
                 "crochet_tracker/book.py", "xlsxwriter/__init__.py"):
        assert any(n.endswith(must) for n in names), f"missing {must}"
    assert not any("Christmas" in n or "Catering" in n for n in names), \
        "other-product artifact leaked into crochet kit"
    print("  content : all key artifacts present, no other-product files")


if __name__ == "__main__":
    main()
