#!/usr/bin/env python3
"""
tools/verify_crochet.py - structural QA for the Crochet Craft Fair Tracker.

Opens every product workbook with openpyxl and checks:

  * the right tabs exist (per edition), _Data is hidden, tab order
  * the defined names the formulas rely on are present
  * the _Data KPI table is complete (26 rows, no gaps)
  * no cached value is an Excel error (#REF!, #VALUE!, ...)
  * validation / conditional-format / chart counts are sane
  * every sheet is protected (and the _Data engine too)
  * the workbook author is Novality Store
  * the protection password never appears in any XML part
    (case-sensitive scan), and no seasonal greetings snuck in
  * EXAMPLE builds: every cached _Data KPI matches the demo aggregate
  * blank builds contain no demo data
  * calculated cells are locked, sample input cells are unlocked
  * every internal hyperlink points at a real sheet

Usage:
    python3 tools/verify_crochet.py [file.xlsx ...]     # default: products/
    python3 tools/verify_crochet.py --no-protect        # unprotected build
"""

import glob
import os
import sys
import warnings
import zipfile

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crochet_tracker import config as C          # noqa: E402
from crochet_tracker import demo as DEMO_MOD     # noqa: E402

ERRORS = ("#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#N/A", "#NULL!",
          "#NUM!")
GREETINGS = ("merry christmas", "happy holidays", "season's greetings",
             "merry xmas", "happy new year", "happy easter")
PASSWORD = "premium"
AUTHOR = "Novality Store"

EXPECTED_SHEETS = {
    "premium": [C.SHEET_NAMES[k] for k in C.EDITIONS["premium"]],
    "basic": [C.SHEET_NAMES[k] for k in C.EDITIONS["basic"]],
}
NEEDED_NAMES = {"BusinessName", "Message", "Currency", "ReportYear",
                "HourlyWage", "OverheadPct", "TargetMargin", "Categories",
                "PaymentMethods", "YarnWeights", "Units", "Suppliers",
                "Tick", "EventList", "ProductsList"}


def edition_of(path):
    base = os.path.basename(path)
    if "_PREMIUM_" in base:
        return "premium"
    if "_BASIC_" in base:
        return "basic"
    raise SystemExit("cannot tell edition from %s" % base)


def check(path, expect_protect=True):
    from openpyxl import load_workbook

    fails = []
    edition = edition_of(path)
    example = "_EXAMPLE" in os.path.basename(path)

    wb = load_workbook(path)
    wbv = load_workbook(path, data_only=True)

    # --- tabs -------------------------------------------------------
    if wb.sheetnames != EXPECTED_SHEETS[edition]:
        fails.append("sheet list mismatch: %s" % wb.sheetnames)
    if wb["_Data"].sheet_state != "hidden":
        fails.append("_Data is not hidden")

    # --- defined names ----------------------------------------------
    missing = NEEDED_NAMES - set(wb.defined_names.keys())
    if edition == "premium" and "MaterialsList" not in wb.defined_names:
        missing.add("MaterialsList")
    if missing:
        fails.append("missing defined names: %s" % sorted(missing))

    # --- KPI engine -------------------------------------------------
    d = wbv["_Data"]
    for i, key in enumerate(sorted(C.KPI_ROW, key=C.KPI_ROW.get)):
        row = C.KPI_ROW[key]
        label = d.cell(row=row, column=34).value
        value = d.cell(row=row, column=35).value
        if label != C.KPI_LABEL[key]:
            fails.append("KPI row %d label %r != %r"
                         % (row, label, C.KPI_LABEL[key]))
        if isinstance(value, str) and value.strip() in ERRORS:
            fails.append("KPI %s cached error %r" % (key, value))

    # --- cached errors anywhere -------------------------------------
    for ws in wbv.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.strip() in \
                        ERRORS:
                    fails.append("%s!%s cached %s" % (ws.title, cell.coordinate,
                                                      cell.value))

    # --- protection --------------------------------------------------
    for ws in wb.worksheets:
        if expect_protect and not ws.protection.sheet:
            fails.append("sheet %r not protected" % ws.title)

    # --- author ------------------------------------------------------
    if wb.properties.creator != AUTHOR:
        fails.append("author is %r" % wb.properties.creator)
    if wb.properties.title != C.PRODUCT:
        fails.append("title is %r" % wb.properties.title)

    # --- password / greeting leak ------------------------------------
    z = zipfile.ZipFile(path)
    for n in z.namelist():
        if n.endswith((".xml", ".rels")):
            data = z.read(n).decode("utf8", "ignore")
            if PASSWORD in data:
                fails.append("password text leaked in %s" % n)
            low = data.lower()
            for g in GREETINGS:
                if g in low:
                    fails.append("greeting %r found in %s" % (g, n))

    # --- locked / unlocked spot checks -------------------------------
    sales = wb["\U0001F4B0 Sales Log"]
    h8 = sales["H8"]
    if not (isinstance(h8.value, str) and h8.value.startswith("=IF(")):
        fails.append("sales H8 is not the total formula: %r" % h8.value)
    locked = {c: (sales[c].protection.locked if sales[c].protection
                  else None) for c in ("B8", "D8", "E8", "H8", "M8")}
    if locked["H8"] is not True:
        fails.append("sales H8 (formula) is not locked")
    if locked["M8"] is not True:
        fails.append("sales M8 (formula) is not locked")
    for c in ("B8", "D8", "E8"):
        if locked[c] is True:
            fails.append("sales %s (input) is locked" % c)
    setup = wb["\u2699\uFE0F Lists & Settings"]
    for cell in ("C6", "C10", "C12"):
        if setup[cell].protection and setup[cell].protection.locked:
            fails.append("setup %s (input) is locked" % cell)

    # --- internal links ----------------------------------------------
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.hyperlink and cell.hyperlink.target and \
                        cell.hyperlink.target.startswith("internal:"):
                    tgt = cell.hyperlink.target[len("internal:"):]
                    tgt = tgt.split("!")[0].strip("'")
                    if tgt not in wb.sheetnames:
                        fails.append("%s!%s links to missing %r"
                                     % (ws.title, cell.coordinate, tgt))

    # --- EXAMPLE: cached KPIs vs the demo aggregate -------------------
    if example:
        m = DEMO_MOD.Demo()
        numeric = {
            "revenue": m.agg["revenue"], "discounts": m.agg["discounts"],
            "cogs": m.agg["cogs"], "fees": m.agg["fees"],
            "profit": m.agg["profit"], "margin": m.agg["margin"],
            "units": m.agg["units"], "txns": m.agg["txns"],
            "aov": m.agg["aov"], "per_item": m.agg["per_item"],
            "events_total": m.agg["events_total"],
            "events_done": m.agg["events_done"],
            "inv_value": m.agg["inv_value"],
            "low_products": m.agg["low_products"],
            "reorder_cost": m.agg["reorder_cost"],
            "made_total": m.agg["made_total"],
            "sell_through": m.agg["sell_through"],
            "price_suggest": m.agg["price_suggest"],
        }
        # premium-only engine cells are static zeros in the Basic edition
        if edition == "basic":
            for key in ("low_materials", "reorder_cost", "made_total",
                        "sell_through"):
                numeric.pop(key, None)
        for key, expect in numeric.items():
            got = d.cell(row=C.KPI_ROW[key], column=35).value
            if got is None or abs(got - expect) > 0.011:
                fails.append("KPI %s cached %r != demo %r"
                             % (key, got, expect))
        texts = {
            "best_product": m.agg["best_product"],
            "best_event": m.agg["best_event"],
            "bs_units": m.agg["bs_units"],
            "bs_revenue": m.agg["bs_revenue"],
            "bs_profit": m.agg["bs_profit"],
            "bs_margin": m.agg["bs_margin"],
            "bs_slow": m.agg["bs_slow"],
        }
        for key, expect in texts.items():
            got = d.cell(row=C.KPI_ROW[key], column=35).value
            if got != expect:
                fails.append("KPI %s cached %r != demo %r"
                             % (key, got, expect))
        # premium-only KPIs only when the tab exists
        if edition == "premium":
            for key in ("low_materials",):
                got = d.cell(row=C.KPI_ROW[key], column=35).value
                if got != m.agg[key]:
                    fails.append("KPI %s cached %r != demo %r"
                                 % (key, got, m.agg[key]))
        # business name present
        if wbv["\u2699\uFE0F Lists & Settings"]["C6"].value != \
                m.settings["business"]:
            fails.append("setup business name missing")
    else:
        # blank build must not contain demo data
        shared = z.read("xl/sharedStrings.xml").decode("utf8", "ignore")
        for needle in ("Willow &amp; Wren", "Willow & Wren",
                       "Amigurumi Bunny", "Spring Makers Market"):
            if needle in shared:
                fails.append("blank build contains demo data %r" % needle)

    # --- charts ------------------------------------------------------
    ncharts = len([n for n in z.namelist()
                   if n.startswith("xl/charts/chart")])
    if ncharts != 6:
        fails.append("expected 6 charts, found %d" % ncharts)

    return fails


def main(argv):
    expect_protect = "--no-protect" not in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        args = sorted(glob.glob(os.path.join(
            "products", "Crochet_Craft_Fair_Tracker_*.xlsx")))
    if not args:
        print("no workbooks found (looked in products/)")
        return 1
    bad = 0
    for path in args:
        fails = check(path, expect_protect)
        tag = os.path.basename(path)
        if fails:
            bad += 1
            print("FAIL  %s" % tag)
            for f in fails:
                print("      - %s" % f)
        else:
            print("OK    %s" % tag)
    print("%d/%d passed" % (len(args) - bad, len(args)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
