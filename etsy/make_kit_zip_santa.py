"""
make_kit_zip_santa.py - bundle the complete Novality Store Secret Santa &
White Elephant Party Tracker kit into ONE zip:

  products/   6 Excel workbooks (PREMIUM + BASIC, Noel + Arctic, EXAMPLE)
  the 12-page illustrated user-guide PDF
  source      santa_tracker package, entry point, QA tools, banner art
  SOURCE_CODE.md   every Python file embedded in one Markdown document
  README.md   master guide + rebuild instructions

Run from the repo root:   python3 -m etsy.make_kit_zip_santa
"""

import os
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "Secret_Santa_White_Elephant_Party_Tracker_COMPLETE_KIT.zip"
PREFIX = "Secret_Santa_White_Elephant_Party_Tracker_COMPLETE_KIT"

DESCRIPTIONS = {
    "secret_santa_party_tracker.py":
        "Entry point / CLI - builds every product workbook "
        "(--all --outdir products/ --protect premium).",
    "santa_tracker/__init__.py": "Package marker.",
    "santa_tracker/config.py":
        "All constants: tabs, editions, statuses, columns, KPI map, "
        "capacities - the single source of truth for every tab.",
    "santa_tracker/theme.py":
        "Noel & Arctic colour themes (tab colours, series, soft tints).",
    "santa_tracker/styles.py":
        "xlsxwriter format factory - every cell style used in the "
        "workbooks.",
    "santa_tracker/demo.py":
        "The demo party: people, draw, budgets, wishlists, white "
        "elephant game, history + all aggregations (agg) for the "
        "dashboard, KPI caches and guide images.",
    "santa_tracker/workbook.py":
        "Workbook bootstrap: sheet order, tab colours, print setup, "
        "protection plumbing, EXAMPLE vs blank modes.",
    "santa_tracker/book.py":
        "Book writer: title blocks, KPI cards, bars, charts, conditional "
        "formats, data validation, sheet protection + (c) Novality Store "
        "footer.",
    "santa_tracker/sheets/__init__.py": "Sheet modules.",
    "santa_tracker/sheets/common.py":
        "Shared sheet helpers: headers, chips, dropdowns, tables, "
        "footers - plus the chip cache label fix.",
    "santa_tracker/sheets/data.py":
        "Hidden _Data engine room: KPI formulas, status pools, lists.",
    "santa_tracker/sheets/setup.py":
        "Settings & Instructions tab: party basics, seeds, budget range.",
    "santa_tracker/sheets/dashboard.py":
        "Dashboard tab: hero, 12 KPI cards, progress bars, 4 live "
        "charts.",
    "santa_tracker/sheets/participants.py": "Participants tab.",
    "santa_tracker/sheets/draw.py":
        "Secret Santa Draw tab: seed-driven shuffle, flags, overrides.",
    "santa_tracker/sheets/rules.py":
        "Exclusions & Rules tab (PREMIUM): house rules + custom pairs.",
    "santa_tracker/sheets/budget.py": "Budget Tracker tab.",
    "santa_tracker/sheets/wishlists.py": "Wishlists tab (PREMIUM).",
    "santa_tracker/sheets/we.py":
        "White Elephant tab (PREMIUM): seats, gifts, holders, statuses.",
    "santa_tracker/sheets/history.py":
        "Game History tab (PREMIUM): turn log that drives the board.",
    "santa_tracker/sheets/cards.py":
        "Santa Cards tab (PREMIUM): fold-and-cut giver cards.",
    "santa_tracker/sheets/guide.py":
        "Start Here guide tab with watercolour banner cover.",
    "tools/verify_santa.py":
        "QA: structural audit - sheet refs, modern functions, hidden "
        "writes.",
    "tools/calc_check_santa.py":
        "QA: recalculates the whole workbook with the formulas engine "
        "and diffs every cached value.",
    "tools/layout_check_santa.py":
        "QA: finds clipped or overflowing text before buyers do.",
    "tools/render_preview_santa.py":
        "QA: renders any tab to PNG (real emoji glyphs) - powers the "
        "user-guide screenshots.",
    "tools/make_banner_alpha_santa.py":
        "Turns the generated banner art into the transparent PNG the "
        "workbook embeds.",
    "etsy/__init__.py": "Package marker.",
    "etsy/crochet_lib.py":
        "Shared PIL rendering engine (emoji-aware text, fonts, tables, "
        "pills, charts) - used to draw the user guide.",
    "etsy/make_user_guide_santa.py":
        "Builds the 12-page illustrated user-guide PDF from real "
        "workbook screenshots.",
    "etsy/make_kit_zip_santa.py":
        "Bundles this complete kit zip.",
    "etsy/make_listing_images_santa.py":
        "Draws the 15 Etsy listing images (2400x1800 JPEG) from real "
        "workbook screenshots.",
    "etsy/make_listing_zip_santa.py":
        "Bundles the standalone Etsy listing-kit zip (md + 15 images).",
}

SOURCE_FILES = list(DESCRIPTIONS.keys())

KIT_README = """# Secret Santa & White Elephant Party Tracker — COMPLETE KIT
**Novality Store** • bundled {today}

Everything needed to sell, rebuild and extend the Secret Santa & White
Elephant Party Tracker spreadsheet on Etsy, in one folder.

```
Secret_Santa_White_Elephant_Party_Tracker_COMPLETE_KIT/
├── README.md                 <- you are here (master guide)
├── SOURCE_CODE.md            <- every Python file in one Markdown document
├── Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf
│                               <- 12-page illustrated user guide
├── products/                 <- the 6 finished Excel workbooks (ready to sell)
├── etsy/
│   ├── LISTING_KIT_SANTA.md  <- SEO title, 13+7 tags, description, alt texts
│   ├── images_santa/         <- 15 listing images (2400x1800 JPEG, <1 MB)
│   ├── fonts/                <- OFL fonts used to render the guide
│   ├── crochet_lib.py        <- shared image engine (emoji text, charts)
│   ├── make_listing_images_santa.py <- rebuild images: python3 -m etsy.make_listing_images_santa
│   ├── make_user_guide_santa.py   <- rebuild guide: python3 -m etsy.make_user_guide_santa
│   └── make_kit_zip_santa.py      <- rebuild this zip: python3 -m etsy.make_kit_zip_santa
├── secret_santa_party_tracker.py  <- build CLI (entry point)
├── santa_tracker/            <- the spreadsheet generator (8 modules + 14 sheets)
├── tools/                    <- QA suite + banner alpha tool
├── assets/                   <- banner art used by the Start Here tab
└── xlsxwriter/               <- vendored xlsxwriter 3.2.9 (no pip needed)
```

## 1. The product (ready to sell)

| File | What it is |
|------|------------|
| `products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel.xlsx` | Flagship - 12 tabs, 700+ formulas, 4 charts, Noel theme |
| `products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Arctic.xlsx` | Same engine, Arctic theme |
| `products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx` | Filled-in demo of the premium file |
| `products/Secret_Santa_White_Elephant_Tracker_BASIC_Noel.xlsx` | Basic edition - 7 tabs, ~400 formulas |
| `products/Secret_Santa_White_Elephant_Tracker_BASIC_Arctic.xlsx` | Basic edition, Arctic theme |
| `products/Secret_Santa_White_Elephant_Tracker_BASIC_Noel_EXAMPLE.xlsx` | Filled-in demo of the starter file |

- Works in **Excel 2016+ / Microsoft 365 (Win & Mac)** and **Google Sheets**
  (File -> Import -> Upload -> Replace spreadsheet).
- **No macros.** All formula cells are **locked** (password: `premium`) so
  buyers can't break the maths; every input cell is open. The Start Here
  tab documents unlocking for buyers - the PDF guide never mentions the
  password.
- Author/branding: **Novality Store** (baked into file properties, cover
  sheet and every tab footer).

## 2. The Etsy listing

Everything is in **`etsy/LISTING_KIT_SANTA.md`**: title (127 chars), 13
recommended tags + 7 spares, the full description, alt texts for the 15
images, pricing and a publish checklist. Upload
`etsy/images_santa/01_hero.jpg` .. `15_faq.jpg` in order - image 01
becomes the thumbnail.

## 3. The buyer guide

`Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf` is the 12-page
illustrated how-to (real screenshots, chart figures, ten tips, FAQ). Attach
it to the Etsy listing as a supporting PDF or drop it into the digital
download.

## 4. Rebuilding everything from source

Requires Python 3.10+ and Pillow (`pip install pillow`) - xlsxwriter is
vendored, openpyxl is only needed for verification.

```bash
# rebuild all 6 workbooks (formulas locked with password 'premium')
python3 secret_santa_party_tracker.py --all --outdir products/ --protect premium

# QA: structure audit, full recalculation, layout audit
python3 tools/verify_santa.py "products/Secret_Santa_White_Elephant_Tracker_*.xlsx"
python3 tools/calc_check_santa.py products/Secret_Santa_White_Elephant_Tracker_PREMIUM_Noel_EXAMPLE.xlsx
python3 tools/layout_check_santa.py "products/Secret_Santa_White_Elephant_Tracker_*.xlsx"

# rebuild the 15 listing images (needs etsy/fonts/ + products/)
python3 -m etsy.make_listing_images_santa

# rebuild the 12-page user guide
python3 -m etsy.make_user_guide_santa

# re-bundle this kit zip
python3 -m etsy.make_kit_zip_santa
```

See **SOURCE_CODE.md** for the annotated source of every file.

## 5. Licences

- Product workbooks: (c) Novality Store - one party organiser per purchase,
  no resale or redistribution.
- Python source: same repository licence as the original repo.
- Fonts in `etsy/fonts/`: SIL Open Font License (Poppins, Gelasio, Playfair
  Display, Caveat, JetBrains Mono, Noto Color Emoji).
- Vendored xlsxwriter: BSD-2-Clause (John McNamara).
"""


def build_source_md():
    parts = [
        "# Secret Santa & White Elephant Party Tracker — Complete Source "
        "Code\n\n",
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
        parts.append("---")
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
        # master README + annotated source
        z.writestr(os.path.join(PREFIX, "README.md"),
                   KIT_README.format(today=date.today().isoformat()))
        z.writestr(os.path.join(PREFIX, "SOURCE_CODE.md"), source_md)
        # products — ONLY the santa workbooks (never the other products)
        for fn in sorted(os.listdir(os.path.join(ROOT, "products"))):
            if fn.startswith("Secret_Santa_White_Elephant_Tracker") and \
                    fn.endswith(".xlsx"):
                z.write(os.path.join(ROOT, "products", fn),
                        os.path.join(PREFIX, "products", fn))
                count += 1
        # guide engine + scripts + fonts
        for fn in ("__init__.py", "crochet_lib.py",
                   "make_user_guide_santa.py", "make_kit_zip_santa.py",
                   "make_listing_images_santa.py",
                   "make_listing_zip_santa.py"):
            z.write(os.path.join(ROOT, "etsy", fn),
                    os.path.join(PREFIX, "etsy", fn))
            count += 1
        count += add_dir(z, os.path.join(ROOT, "etsy", "fonts"),
                         os.path.join(PREFIX, "etsy", "fonts"))
        # Etsy listing kit (md + 15 listing images)
        z.write(os.path.join(ROOT, "etsy", "LISTING_KIT_SANTA.md"),
                os.path.join(PREFIX, "etsy", "LISTING_KIT_SANTA.md"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "etsy", "images_santa"),
                         os.path.join(PREFIX, "etsy", "images_santa"))
        # spreadsheet source
        z.write(os.path.join(ROOT, "secret_santa_party_tracker.py"),
                os.path.join(PREFIX, "secret_santa_party_tracker.py"))
        count += 1
        count += add_dir(z, os.path.join(ROOT, "santa_tracker"),
                         os.path.join(PREFIX, "santa_tracker"))
        # QA tools
        for fn in ("verify_santa.py", "calc_check_santa.py",
                   "layout_check_santa.py", "render_preview_santa.py",
                   "make_banner_alpha_santa.py"):
            z.write(os.path.join(ROOT, "tools", fn),
                    os.path.join(PREFIX, "tools", fn))
            count += 1
        # banner art (finished PNGs the workbook embeds + raw sources)
        for fn in ("banner_noel.png", "banner_arctic.png",
                   "raw_banner_noel.png", "raw_banner_arctic.png"):
            z.write(os.path.join(ROOT, "assets", fn),
                    os.path.join(PREFIX, "assets", fn))
            count += 1
        # the illustrated user-guide PDF
        guide = os.path.join(
            ROOT, "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf")
        assert os.path.exists(guide), "build the user guide first"
        z.write(guide, os.path.join(
            PREFIX,
            "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf"))
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
    # sanity: every key artifact present, no other-product artifacts leaked
    for must in ("etsy/LISTING_KIT_SANTA.md",
                 "etsy/images_santa/01_hero.jpg",
                 "etsy/images_santa/15_faq.jpg",
                 "products/Secret_Santa_White_Elephant_Tracker_PREMIUM_"
                 "Noel.xlsx",
                 "products/Secret_Santa_White_Elephant_Tracker_BASIC_"
                 "Arctic.xlsx",
                 "Secret_Santa_White_Elephant_Party_Tracker_User_Guide.pdf",
                 "santa_tracker/book.py", "tools/verify_santa.py",
                 "assets/banner_noel.png", "etsy/fonts/NotoColorEmoji.ttf",
                 "SOURCE_CODE.md", "README.md", "xlsxwriter/__init__.py"):
        assert any(n.endswith(must) for n in names), f"missing {must}"
    assert not any(("Crochet" in n) or ("Catering" in n) or
                   ("Christmas_Gift" in n) for n in names), \
        "other-product artifact leaked into santa kit"
    print("  content : all key artifacts present, no other-product files")


if __name__ == "__main__":
    main()
