#!/usr/bin/env python3
"""Sanity checks on the example data written into the FILLED workbook.

The example has to be a business that could exist. If a sale points at a
product that is not in the catalog, or a bill of materials points at a
material nobody stocks, the workbook still opens - it just quietly shows
zeros, and the buyer concludes the calculator is broken.

These checks read the finished workbook (not the generator) through the
register specifications, so a column that moves does not silently break the
check:

* every ID is unique and shaped like its prefix;
* every cross-register reference resolves - product, material, bundle,
  customer, channel, shipping label;
* materials are never counted twice: a product priced on a craft tab takes
  its material cost from that tab, and the formula on Products must prefer
  it over the bill of materials when it is there;
* the sales history spans enough of the year for the monthly reports and
  the dashboard to mean something;
* quantities, prices, hours and fee rates are sane.

    python3 tools/check_handmade_sample.py [file.xlsx] [--blank]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from handmade_pricing_spreadsheet.build import REGISTER_MODULES   # noqa: E402
from handmade_pricing_spreadsheet.config import Config            # noqa: E402
from handmade_pricing_spreadsheet.layout import Registry          # noqa: E402
from handmade_pricing_spreadsheet.sample_data import (            # noqa: E402
    build_sample_data)

DEFAULT = ROOT / "output" / "Handmade Product Pricing & Profit Calculator.xlsx"

FIRST_ROW = 5
ID_RE = re.compile(r"^[A-Z]{1,4}-\d{4}$")

#: how many example rows each register must carry to be worth showing
MIN_ROWS = {
    "Products": 10, "Materials": 20, "Material Usage": 30, "Labor": 8,
    "Packaging": 3, "Shipping": 4, "Overhead": 6, "Channels": 3,
    "Crochet": 3, "Jewelry": 2, "Candles": 2, "Clothing": 2,
    "Woodworking": 2, "Digital": 2, "Bundles": 2, "Bundle Lines": 4,
    "Variations": 5, "Batches": 4, "Sales": 40, "Promotions": 3,
    "Price History": 8, "Competitors": 6, "Waste Log": 6, "Development": 4,
    "Events": 3, "Wholesale Customers": 3, "Wholesale Orders": 6,
}

#: register -> {column: register whose ID/name column it must match}
LINKS: Dict[str, Dict[str, Tuple[str, str]]] = {
    "Material Usage": {"product": ("Products", "id"),
                       "material": ("Materials", "id")},
    "Labor": {"product": ("Products", "id")},
    "Bundle Lines": {"bundle": ("Bundles", "id"),
                     "product": ("Products", "id")},
    "Variations": {"product": ("Products", "id")},
    "Batches": {"product": ("Products", "id")},
    "Sales": {"product": ("Products", "id"),
              "channel": ("Channels", "name")},
    "Price History": {"product": ("Products", "id")},
    "Waste Log": {"product": ("Products", "id"),
                  "material": ("Materials", "id")},
    "Development": {"product": ("Products", "id")},
    "Competitors": {"my_product": ("Products", "id")},
    "Wholesale Orders": {"customer": ("Wholesale Customers", "id")},
    "Crochet": {"product": ("Products", "id")},
    "Jewelry": {"product": ("Products", "id")},
    "Candles": {"product": ("Products", "id")},
    "Clothing": {"product": ("Products", "id")},
    "Woodworking": {"product": ("Products", "id")},
    "Digital": {"product": ("Products", "id")},
}

#: columns that may legitimately be blank even though they are links
OPTIONAL_LINKS = {
    ("Labor", "product"), ("Waste Log", "product"), ("Waste Log", "material"),
    ("Development", "product"), ("Competitors", "my_product"),
    ("Sales", "channel"), ("Crochet", "product"), ("Jewelry", "product"),
    ("Candles", "product"), ("Clothing", "product"),
    ("Woodworking", "product"), ("Digital", "product"),
}

CRAFT_TABS = ["Crochet", "Jewelry", "Candles", "Clothing", "Woodworking",
              "Digital"]


# ---------------------------------------------------------------------------
# reading
# ---------------------------------------------------------------------------

def registry() -> Registry:
    cfg = Config()
    reg = Registry()
    for module in REGISTER_MODULES:
        reg.add(module.spec(cfg))
    return reg


def is_formula(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("=")


def read_register(wb, spec) -> List[Dict[str, Any]]:
    """The populated rows of one register, keyed by column key.

    A row counts as populated only when one of its *typed* cells has
    something in it: every row of a register carries formulas, so "any
    non-empty cell" would report the whole sheet as full.
    """
    ws = wb[spec.name]
    columns = {col.key: i + 1 for i, col in enumerate(spec.columns)}
    out: List[Dict[str, Any]] = []
    for r in range(FIRST_ROW, spec.last_data_row + 1):
        row: Dict[str, Any] = {"_row": r}
        filled = False
        for key, col in columns.items():
            value = ws.cell(row=r, column=col).value
            if value not in (None, "") and not is_formula(value):
                filled = True
            row[key] = value
        if filled:
            out.append(row)
    return out


def allowed_keys(cfg: Config) -> Dict[str, set]:
    """The IDs and names the example data defines, per register and column.

    Taken from the generator rather than from the workbook, because ID
    columns are auto-numbering formulas - the workbook holds
    ``=IF(B5="","",...)`` where the example holds ``P-0001``.
    """
    data = build_sample_data(cfg)
    out: Dict[str, set] = {}
    for sheet, rows in data.items():
        for column in ("id", "name", "label", "code"):
            values = set()
            for row in rows:
                value = row.get(column)
                if value not in (None, ""):
                    values.add(str(value))
            if values:
                out[f"{sheet}.{column}"] = values
    return out


def as_date(value: Any) -> Optional[dt.date]:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return None


def as_number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or is_formula(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def check_ids(sample: Dict[str, List[Dict[str, Any]]],
              problems: List[str]) -> None:
    """IDs come from the example data - in the workbook they are formulas."""
    for sheet, rows in sample.items():
        seen: Dict[str, int] = {}
        for i, row in enumerate(rows):
            value = row.get("id")
            if value in (None, ""):
                continue
            text = str(value)
            if not ID_RE.match(text):
                problems.append(f"{sheet} row {i + 1}: id '{text}' does not "
                                f"match PREFIX-0000")
            if text in seen:
                problems.append(f"{sheet} row {i + 1}: duplicate id '{text}' "
                                f"(first in row {seen[text]})")
            else:
                seen[text] = i + 1


def check_links(rows_by_sheet: Dict[str, List[Dict[str, Any]]],
                allowed_keys: Dict[str, set], problems: List[str]) -> None:
    """Every typed link column must point at a row that exists."""
    for sheet, rules in LINKS.items():
        rows = rows_by_sheet.get(sheet) or []
        for column, (target_sheet, target_key) in rules.items():
            allowed = allowed_keys.get(f"{target_sheet}.{target_key}", set())
            optional = (sheet, column) in OPTIONAL_LINKS
            if not allowed:
                problems.append(f"{sheet}.{column}: nothing to match against "
                                f"on '{target_sheet}'")
                continue
            for row in rows:
                value = row.get(column)
                if value in (None, ""):
                    continue
                if is_formula(value):
                    continue
                text = str(value).strip()
                if text not in allowed and not optional:
                    problems.append(
                        f"{sheet}!{column} row {row['_row']}: '{text}' is not "
                        f"on {target_sheet}")
                elif text not in allowed and optional:
                    # optional links may hold a free-text note instead
                    if ID_RE.match(text):
                        problems.append(
                            f"{sheet}!{column} row {row['_row']}: '{text}' "
                            f"looks like an id but is not on {target_sheet}")


def check_promotions(rows_by_sheet: Dict[str, List[Dict[str, Any]]],
                     allowed_keys: Dict[str, set],
                     problems: List[str]) -> None:
    """`applies_to` may name products, bundles, or plain words like "All"."""
    products = allowed_keys.get("Products.id", set())
    bundles = allowed_keys.get("Bundles.id", set())
    known = products | bundles
    for row in rows_by_sheet.get("Promotions") or []:
        applies = row.get("applies_to")
        if applies in (None, "") or is_formula(applies):
            continue
        for token in str(applies).replace(";", ",").split(","):
            token = token.strip()
            if not token or token.lower() in ("all", "everything"):
                continue
            # free text ("Wholesale orders", "Candles") is allowed; anything
            # shaped like an id must resolve
            if ID_RE.match(token) and token not in known:
                problems.append(f"Promotions row {row['_row']}: applies_to "
                                f"'{token}' is not a product or a bundle")


def check_sales(rows: List[Dict[str, Any]], cfg: Config,
                problems: List[str]) -> None:
    if len(rows) < MIN_ROWS["Sales"]:
        problems.append(f"Sales: only {len(rows)} example rows")
    dates = [d for d in (as_date(r.get("date")) for r in rows) if d]
    if dates:
        span = (max(dates) - min(dates)).days
        if span < 90:
            problems.append(f"Sales: history spans only {span} days - the "
                            f"monthly reports need at least 90")
        if max(dates) > cfg.today + dt.timedelta(days=1):
            problems.append(f"Sales: a sale is dated in the future "
                            f"({max(dates)})")
    channels = {str(r["channel"]) for r in rows
                if r.get("channel") not in (None, "")}
    if len(channels) < 2:
        problems.append(f"Sales: only {len(channels)} channel(s) in the "
                        f"example - the by-channel report needs two")
    for row in rows:
        qty = as_number(row.get("qty"))
        price = as_number(row.get("unit_price"))
        if qty is not None and qty < 1:
            problems.append(f"Sales row {row['_row']}: qty {qty}")
        if price is not None and price <= 0:
            problems.append(f"Sales row {row['_row']}: price {price}")
        discount = as_number(row.get("discount_pct"))
        if discount is not None and not 0 <= discount < 1:
            problems.append(f"Sales row {row['_row']}: discount {discount}")


def check_numbers(rows_by_sheet: Dict[str, List[Dict[str, Any]]],
                  problems: List[str]) -> None:
    """Ranges that must hold in any believable example."""
    rules: Sequence[Tuple[str, str, float, float]] = [
        ("Products", "retail_price", 0.01, 100000.0),
        ("Materials", "unit_cost", 0.0, 100000.0),
        ("Materials", "on_hand", 0.0, 1000000.0),
        ("Labor", "hours", 0.01, 24.0),
        ("Labor", "rate", 0.0, 500.0),
        ("Material Usage", "qty", 0.0, 100000.0),
        ("Material Usage", "scrap_pct", 0.0, 0.9),
        ("Channels", "transaction_pct", 0.0, 0.5),
        ("Channels", "processing_pct", 0.0, 0.5),
        ("Shipping", "base_cost", 0.0, 10000.0),
        ("Shipping", "delivery_days", 0.0, 90.0),
        ("Batches", "qty_planned", 1.0, 100000.0),
        ("Batches", "qty_defect", 0.0, 100000.0),
        ("Events", "table_fee", 0.0, 100000.0),
        ("Wholesale Orders", "qty", 1.0, 100000.0),
        ("Wholesale Customers", "discount", 0.0, 0.9),
        ("Overhead", "amount", 0.0, 1000000.0),
    ]
    for sheet, column, low, high in rules:
        for row in rows_by_sheet.get(sheet) or []:
            value = as_number(row.get(column))
            if value is None:
                continue
            if not low <= value <= high:
                problems.append(f"{sheet} row {row['_row']}: {column} "
                                f"{value} outside {low}..{high}")


def check_double_costing(wb, reg: Registry,
                         rows_by_sheet: Dict[str, List[Dict[str, Any]]],
                         problems: List[str]) -> None:
    """Craft-tab materials must not also be billed through the BOM.

    Products takes its material cost from the craft tab when the craft tab
    produced one, and from Material Usage otherwise. If a product had both
    and the formula added them, every craft product would be costed twice -
    so the formula itself is checked, not just the data.
    """
    spec = reg["Products"]
    ws = wb["Products"]
    letter = spec.letter("material_cost")
    cell = ws[f"{letter}{FIRST_ROW}"]
    formula = cell.value if isinstance(cell.value, str) else ""
    craft_letter = spec.letter("craft_cost")
    bom_letter = spec.letter("bom_cost")
    if not formula.startswith("="):
        problems.append(f"Products!{letter}{FIRST_ROW}: material cost is not "
                        f"a formula")
        return
    if craft_letter not in formula or bom_letter not in formula:
        problems.append(f"Products!{letter}{FIRST_ROW}: material cost does "
                        f"not choose between the craft tab "
                        f"({craft_letter}) and the bill of materials "
                        f"({bom_letter}) :: {formula[:90]}")
    if craft_letter + "+" + bom_letter in formula.replace(" ", ""):
        problems.append(f"Products!{letter}{FIRST_ROW}: material cost ADDS "
                        f"the craft tab and the bill of materials - that "
                        f"counts materials twice")

    # the example itself: a craft product may have BOM rows only if the
    # formula above prefers the craft figure, which it now must
    craft_products = set()
    for tab in CRAFT_TABS:
        for row in rows_by_sheet.get(tab) or []:
            value = row.get("product")
            if value not in (None, "") and not is_formula(value):
                craft_products.add(str(value))
    bom_products = {str(r["product"]) for r in rows_by_sheet.get(
        "Material Usage") or []
        if r.get("product") not in (None, "") and not is_formula(r.get("product"))}
    both = sorted(craft_products & bom_products)
    if both and (craft_letter not in formula):
        problems.append(f"{len(both)} products are costed on a craft tab and "
                        f"on Material Usage: {', '.join(both[:5])}")


def check_shipping(rows_by_sheet: Dict[str, List[Dict[str, Any]]],
                   problems: List[str]) -> None:
    labels: Dict[str, int] = {}
    for row in rows_by_sheet.get("Shipping") or []:
        label = row.get("label")
        if label in (None, "") or is_formula(label):
            continue
        text = str(label)
        if text in labels:
            problems.append(f"Shipping row {row['_row']}: duplicate label "
                            f"'{text}'")
        else:
            labels[text] = row["_row"]
        charge = as_number(row.get("retail_charge"))
        base = as_number(row.get("base_cost"))
        if charge is not None and base is not None and charge < 0:
            problems.append(f"Shipping row {row['_row']}: negative charge")


def check_blank(wb, reg: Registry, problems: List[str]) -> None:
    """A blank workbook must have empty registers and live formulas."""
    for module in REGISTER_MODULES:
        spec = reg[module.NAME]
        ws = wb[spec.name]
        keys = [c.key for c in spec.columns]
        typed = [c.key for c in spec.columns if not c.is_formula and not c.hidden]
        # Channels has no auto id: probe the first column the owner types in
        probe = typed[0] if typed else keys[0]
        probe_letter = spec.letter(probe)
        for r in range(FIRST_ROW, min(FIRST_ROW + 5, spec.last_data_row + 1)):
            value = ws[f"{probe_letter}{r}"].value
            if value in (None, "", 0) or is_formula(value):
                continue
            problems.append(f"BLANK {spec.name}!{probe_letter}{r} still "
                            f"holds '{value}'")
        cost_letter = None
        if "total_cost" in [c.key for c in spec.columns]:
            cost_letter = spec.letter("total_cost")
        if cost_letter:
            formula = ws[f"{cost_letter}{FIRST_ROW}"].value
            if not (isinstance(formula, str) and formula.startswith("=")):
                problems.append(f"BLANK {spec.name}!{cost_letter}{FIRST_ROW} "
                                f"lost its formula")


# ---------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default=str(DEFAULT))
    parser.add_argument("--blank", action="store_true",
                        help="expect empty registers instead of the example")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"check_handmade_sample: not found: {path}")
        return 1

    cfg = Config()
    reg = registry()
    wb = openpyxl.load_workbook(path, data_only=False)

    print(f"{'BLANK' if args.blank else 'SAMPLE'} {path.name}")
    if args.blank:
        problems: List[str] = []
        check_blank(wb, reg, problems)
        if problems:
            print(f"  PROBLEMS: {len(problems)}")
            for p in problems[:30]:
                print(f"    - {p}")
            return 1
        print(f"  registers  : {len(REGISTER_MODULES)} all empty, formulas "
              f"intact")
        print("  RESULT     : PASS")
        return 0

    rows_by_sheet: Dict[str, List[Dict[str, Any]]] = {}
    for module in REGISTER_MODULES:
        rows_by_sheet[module.NAME] = read_register(wb, reg[module.NAME])

    sample = build_sample_data(cfg)
    keys = allowed_keys(cfg)

    problems = []
    for sheet, minimum in MIN_ROWS.items():
        found = len(rows_by_sheet.get(sheet) or [])
        if found < minimum:
            problems.append(f"{sheet}: {found} example rows, expected at "
                            f"least {minimum}")
        expected = len(sample.get(sheet) or [])
        if expected and found != expected:
            problems.append(f"{sheet}: workbook holds {found} example rows "
                            f"but the data defines {expected}")

    products = keys.get("Products.id", set())

    check_ids(sample, problems)
    check_links(rows_by_sheet, keys, problems)
    check_promotions(rows_by_sheet, keys, problems)
    check_sales(rows_by_sheet["Sales"], cfg, problems)
    check_numbers(rows_by_sheet, problems)
    check_double_costing(wb, reg, rows_by_sheet, problems)
    check_shipping(rows_by_sheet, problems)

    dates = [d for d in (as_date(r.get("date"))
                         for r in rows_by_sheet["Sales"]) if d]
    span = (max(dates) - min(dates)).days if dates else 0
    print(f"  products   : {len(products)}")
    print(f"  materials  : {len(rows_by_sheet['Materials'])}")
    print(f"  bom lines  : {len(rows_by_sheet['Material Usage'])}")
    print(f"  sales      : {len(rows_by_sheet['Sales'])} over {span} days")
    print(f"  craft rows : "
          f"{sum(len(rows_by_sheet[t]) for t in CRAFT_TABS)} across "
          f"{len(CRAFT_TABS)} craft tabs")
    print(f"  trade      : {len(rows_by_sheet['Wholesale Customers'])} shops, "
          f"{len(rows_by_sheet['Wholesale Orders'])} orders")

    if problems:
        print(f"  PROBLEMS   : {len(problems)}")
        for p in problems[:40]:
            print(f"    - {p}")
        if len(problems) > 40:
            print(f"    ... and {len(problems) - 40} more")
        return 1
    print("  RESULT     : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
