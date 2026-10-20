#!/usr/bin/env python3
"""Validate a Handmade Product Pricing & Profit Calculator workbook.

This is the gate between "the builder ran" and "the customer can open it".
Every check in here exists because something once went wrong in a shipped
workbook, or in one of its predecessors:

* raw sheet XML is scanned for cached ``<v>None</v>`` values and for braces
  left in a formula - both produce Excel's "Repaired Records" dialog;
* every formula is scanned for unbalanced parentheses and unclosed quotes,
  because Excel silently deletes a formula it cannot parse and then repairs
  the file;
* every formula is scanned for ``==``, ``#REF!``, unrendered ``{token}``
  leftovers and functions that did not exist in Excel 2010;
* merged ranges are checked for overlap, which also triggers a repair;
* every defined name is checked to resolve to a sheet that exists;
* named inputs must be unlocked and named calculations must be locked
  formulas, on every sheet, protected with the shipped password;
* ``precedence_slip`` catches ``A5-B5/60`` written where ``(A5-B5)/60`` was
  meant - the one silent arithmetic bug that no repair dialog reports.

    python3 tools/validate_handmade_workbook.py [file.xlsx ...] [--blank]

Exit status is 0 only when every file passes.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import openpyxl

EXPECTED_SHEETS = [
    "Start Here", "Settings", "Dashboard",
    "Products", "Materials", "Material Usage", "Labor",
    "Packaging", "Shipping", "Overhead", "Channels",
    "Retail Calculator", "Wholesale Calculator", "Profit & Break-Even",
    "Crochet", "Jewelry", "Candles", "Clothing", "Woodworking", "Digital",
    "Bundles", "Bundle Lines", "Variations", "Batches",
    "Sales", "Promotions", "Price History", "Competitors",
    "Waste Log", "Development", "Events",
    "Wholesale Customers", "Wholesale Orders",
    "Scenarios", "Reports",
    "Print Costing", "Print Quote", "Print Order",
    "Lists", "Help",
]

AUTHOR = "Novality Store"

BANNED = [
    "XLOOKUP", "XMATCH", "IFS", "LET", "MINIFS", "MAXIFS",
    "TEXTJOIN", "CONCAT", "UNIQUE", "FILTER", "SORT", "SORTBY", "SEQUENCE",
    "SWITCH", "LAMBDA", "BYROW", "BYCOL", "MAKEARRAY", "VSTACK",
    "HSTACK", "TEXTSPLIT", "TOROW", "TOCOL", "REDUCE", "SCAN",
    "MAP", "CHOOSECOLS", "CHOOSEROWS", "TAKE", "DROP", "EXPAND",
    "RANDARRAY", "IMAGE", "GROUPBY", "PIVOTBY",
]

BANNED_RE = re.compile(r"(?<![A-Z0-9_.])(" + "|".join(BANNED) + r")\s*\(")

TOKEN_LEFTOVER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")

CELLTOKEN = r"(?:\$?[A-Z]{1,3}\$?\d+)"

#: defined names that must point at an UNLOCKED cell the owner can type in
INPUT_NAMES = [
    # Settings - the shop
    "ShopName", "ShopOwner", "Brand", "Email", "Phone", "Address",
    # Settings - labour and overhead
    "HourlyRate", "MinimumWage", "PayrollBurden", "ProductiveHours",
    "UnitsPerMonth", "DefaultBatchSize", "SuppliesPerHour",
    "OverheadMethod", "DefaultWaste", "DefaultDefect",
    "DefaultPackaging", "DefaultShipping",
    # Settings - fees and pricing
    "DefaultChannel", "ListingFee", "TransactionFee", "ProcessingPercent",
    "ProcessingFixed", "OffsiteAdsFee", "OffsiteAdsShare", "RegulatoryFee",
    "CurrencyFee", "TargetRetailMargin", "TargetWholesaleMargin",
    "WholesaleDiscount", "MarginWarning", "RoundingRule", "TaxRate",
    "MinOrderQty", "MinOrderValue", "PriceReviewDays", "LowStockDays",
    "MonthlyRevenueTarget", "AnnualRevenueTarget", "MonthlyProfitTarget",
    "FeesReviewed", "FeeReviewDays",
    # the calculators
    "RcProduct", "WcCustomer", "WcProduct", "BeProduct", "ScProduct",
    "PrintProduct", "QuoteCustomer", "OrderProduct", "OrderQty", "OrderDue",
    "QuotePostage", "QuoteNumber", "OrderNumber", "OrderFor",
]

#: defined names that must point at a LOCKED formula
CALC_NAMES = [
    "TodayDate", "ReportYear", "MonthStart", "MonthEnd", "YearStart",
    "YearEnd", "FeeStale", "LaborCostHour", "TargetHourly",
    "OverheadMonthly", "OverheadPerHour", "OverheadPerUnit",
    "RevenuePerHourTarget", "DefaultFeeRate",
    "RcCost", "RcSuggested", "RcFeeRate", "WcTradePrice", "WcProfit",
    "WcRetailNeeded", "BeContribution", "BeFixed", "BeUnits",
    "PrintCost", "QuoteTotal", "QuoteTax", "RepProductCount",
]

#: formula shapes where `A-B/C` is deliberate, so precedence_slip stays quiet
PRECEDENCE_OK: Sequence[str] = (
    "ROW()-",
    "TEXT(ROW()",
)

#: names every workbook must define for its lookups to work
REQUIRED_NAMES = [
    "ProductIDs", "ProductNames", "MaterialIDs", "MaterialNames",
    "ChannelNames", "CategoryList", "CraftList", "YesNoList",
    "RoundingRules", "VolumeSteps",
]


# ---------------------------------------------------------------------------
# formula scanners
# ---------------------------------------------------------------------------

def paren_depth(formula: str) -> Tuple[bool, str]:
    """Return (ok, reason) after scanning quotes and parentheses."""
    depth = 0
    in_str = False
    i = 0
    n = len(formula)
    while i < n:
        ch = formula[i]
        if in_str:
            if ch == '"':
                if i + 1 < n and formula[i + 1] == '"':
                    i += 2
                    continue
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False, "more ')' than '('"
        i += 1
    if in_str:
        return False, "unclosed string quote"
    if depth != 0:
        return False, f"unbalanced parens (depth {depth} at end)"
    return True, ""


def precedence_slip(formula: str) -> Tuple[bool, str]:
    """Catch `A5-B5/60` where `(A5-B5)/60` was meant.

    Only the risky shape is flagged: a cell reference, minus a cell
    reference, immediately divided. Anything matching :data:`PRECEDENCE_OK`
    is left alone.
    """
    for ok in PRECEDENCE_OK:
        if ok in formula:
            return False, ""
    slim = re.sub(r'"[^"]*"', '""', formula)
    m = re.search(CELLTOKEN + r"\s*-\s*" + CELLTOKEN + r"\s*/", slim)
    if m:
        return True, f"possible precedence slip near '{m.group(0)}'"
    return False, ""


def raw_xml_problems(path: Path) -> List[str]:
    """Scan the sheets as raw XML for what openpyxl's view hides."""
    out: List[str] = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not (name.startswith("xl/worksheets/")
                    and name.endswith(".xml")):
                continue
            data = z.read(name).decode("utf-8", "replace")
            for bad in ("<v>None</v>", "<v>NaN</v>", "<v>Infinity</v>",
                        "<v>-Infinity</v>", "<v></v>"):
                n = data.count(bad)
                if n:
                    out.append(f"{name}: {n} cached {bad} values")
            for m in re.finditer(r"<f[^>]*>([^<]*)</f>", data):
                text = m.group(1)
                if "{" in text or "}" in text:
                    out.append(f"{name}: braces in raw formula :: {text[:70]}")
                if text.startswith("="):
                    out.append(f"{name}: stored formula starts with '=' "
                               f":: {text[:70]}")
            if data.count("<mergeCells ") and "ref=\"A1:A1\"" in data:
                out.append(f"{name}: single-cell merge present")
    return out


def overlap_problems(ws) -> List[str]:
    """Overlapping merged ranges make Excel repair the file."""
    out: List[str] = []
    ranges = list(ws.merged_cells.ranges)
    for i, a in enumerate(ranges):
        for b in ranges[i + 1:]:
            if (a.min_row <= b.max_row and b.min_row <= a.max_row
                    and a.min_col <= b.max_col and b.min_col <= a.max_col):
                out.append(f"{ws.title}: overlapping merges {a} and {b}")
                break
    return out


def hyperlink_problems(wb) -> List[str]:
    """Internal links must point at sheets that exist."""
    out: List[str] = []
    known = set(wb.sheetnames)
    for ws in wb.worksheets:
        for link in getattr(ws, "_hyperlinks", []) or []:
            target = getattr(link, "location", None) or ""
            if not target or target.startswith("http"):
                continue
            sheet = target.split("!")[0].strip("'")
            if sheet and sheet not in known:
                out.append(f"{ws.title}: link to missing sheet '{sheet}'")
    return out


def resolve_name(value: str) -> Tuple[str, str]:
    """'Sheet'!$C$7 -> ('Sheet', '$C$7'); ranges give their first cell.

    Dynamic names (``OFFSET(...)``) and names that hold a whole formula
    (``COUNTIF(...)``) return empty strings - there is no single cell to
    inspect, and their sheet references are inside function arguments.
    """
    text = value.lstrip("=")
    if "(" in text.split("!")[0]:
        return "", ""
    first = text.split(",")[0].strip()
    if "!" not in first:
        return "", first
    sheet, ref = first.rsplit("!", 1)
    sheet = sheet.strip("'")
    ref = ref.split(":")[0]
    return sheet, ref


# ---------------------------------------------------------------------------
# the validation pass
# ---------------------------------------------------------------------------

def validate(path: Path, blank: bool = False) -> int:
    problems: List[str] = []
    if not path.is_file():
        print(f"[{'BLANK' if blank else 'FILLED'}] {path.name}")
        print("  RESULT         : FILE NOT FOUND")
        return 1

    problems += raw_xml_problems(path)

    wb = openpyxl.load_workbook(path, data_only=False)

    # ---------------------------------------------------------- metadata
    creator = wb.properties.creator or ""
    if creator != AUTHOR:
        problems.append(f"creator is '{creator}', expected '{AUTHOR}'")
    modified_by = wb.properties.lastModifiedBy or ""
    if modified_by and modified_by != AUTHOR:
        problems.append(f"lastModifiedBy is '{modified_by}'")
    if not (wb.properties.title or ""):
        problems.append("document title is empty")

    # --------------------------------------------------------- sheet list
    if wb.sheetnames != EXPECTED_SHEETS:
        problems.append("sheet order mismatch")
        missing = set(EXPECTED_SHEETS) - set(wb.sheetnames)
        extra = set(wb.sheetnames) - set(EXPECTED_SHEETS)
        if missing:
            problems.append(f"  missing: {sorted(missing)}")
        if extra:
            problems.append(f"  extra: {sorted(extra)}")
        if not missing and not extra:
            problems.append(f"  order: {wb.sheetnames}")

    # ----------------------------------------------------------- formulas
    total_formulas = 0
    total_cells = 0
    banned_hits = 0
    for ws in wb.worksheets:
        if not ws.protection.sheet:
            problems.append(f"{ws.title}: sheet is NOT protected")
        elif not ws.protection.password:
            problems.append(f"{ws.title}: protected with no password hash")
        problems += overlap_problems(ws)
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if value is None:
                    continue
                total_cells += 1
                if not isinstance(value, str) or not value.startswith("="):
                    continue
                total_formulas += 1
                where = f"{ws.title}!{cell.coordinate}"

                if value.startswith("=="):
                    problems.append(f"{where}: formula starts with '=='")

                ok, reason = paren_depth(value)
                if not ok:
                    problems.append(f"{where}: {reason} :: {value[:110]}")

                slip, why = precedence_slip(value)
                if slip:
                    problems.append(f"{where}: {why} :: {value[:90]}")

                if "#REF!" in value:
                    problems.append(f"{where}: contains #REF!")

                leftover = TOKEN_LEFTOVER.search(value)
                if leftover:
                    problems.append(f"{where}: unreplaced template token "
                                    f"'{leftover.group(0)}' :: {value[:90]}")

                if "{" in value or "}" in value:
                    problems.append(f"{where}: braces in formula :: "
                                    f"{value[:80]}")

                upper = value.upper()
                for m in BANNED_RE.finditer(upper):
                    banned_hits += 1
                    if banned_hits <= 10:
                        problems.append(f"{where}: banned function "
                                        f"'{m.group(1)}' :: {value[:80]}")

    # ------------------------------------------------------- defined names
    names: Dict[str, str] = {}
    for name, dn in dict(wb.defined_names).items():
        names[name] = dn.value or ""
    for needed in REQUIRED_NAMES:
        if needed not in names:
            problems.append(f"defined name '{needed}' missing")

    for name, value in names.items():
        sheet, ref = resolve_name(value)
        if not ref:
            continue
        if sheet and sheet not in wb.sheetnames:
            problems.append(f"defined name '{name}' points at missing sheet "
                            f"'{sheet}' :: {value[:60]}")
            continue
        if not sheet:
            continue
        ws = wb[sheet]
        if not re.fullmatch(r"\$?[A-Z]{1,3}\$?\d+", ref):
            continue
        cell = ws[ref.replace("$", "")]
        if name in INPUT_NAMES:
            if cell.protection.locked:
                problems.append(f"{name} ({sheet}!{ref}): input is LOCKED")
        elif name in CALC_NAMES:
            if not cell.protection.locked:
                problems.append(f"{name} ({sheet}!{ref}): calc is unlocked")
            if not (isinstance(cell.value, str)
                    and cell.value.startswith("=")):
                problems.append(f"{name} ({sheet}!{ref}): calc holds "
                                f"'{str(cell.value)[:30]}', not a formula")

    # --------------------------------------------------------- validations
    n_validations = 0
    for ws in wb.worksheets:
        n_validations += len(ws.data_validations.dataValidation)
    if n_validations < 60:
        problems.append(f"only {n_validations} data validations found")

    # ------------------------------------------------------------ contents
    problems += hyperlink_problems(wb)
    if not blank:
        empty = []
        for sheet in ("Products", "Materials", "Sales", "Channels"):
            ws = wb[sheet]
            rows = sum(1 for row in ws.iter_rows(min_row=5, max_col=2)
                       if row[0].value not in (None, ""))
            if rows < 3:
                empty.append(f"{sheet} ({rows} rows)")
        if empty:
            problems.append("filled workbook looks empty: " + ", ".join(empty))
    else:
        ws = wb["Products"]
        if ws["B5"].value not in (None, ""):
            problems.append("blank workbook still has sample data")

    # ------------------------------------------------------------ zip file
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad:
            problems.append(f"corrupt member in xlsx zip: {bad}")

    # ------------------------------------------------------------- report
    label = "BLANK" if blank else "FILLED"
    print(f"[{label}] {path.name}")
    print(f"  sheets         : {len(wb.sheetnames)}")
    print(f"  formulas       : {total_formulas:,}")
    print(f"  populated cells: {total_cells:,}")
    print(f"  validations    : {n_validations}")
    print(f"  defined names  : {len(names)}")

    if problems:
        print(f"  PROBLEMS       : {len(problems)}")
        for p in problems[:40]:
            print(f"    - {p}")
        if len(problems) > 40:
            print(f"    ... and {len(problems) - 40} more")
        return 1
    print("  RESULT         : PASS")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    forced_blank = "--blank" in argv
    argv = [a for a in argv if not a.startswith("--")]
    base = Path(__file__).resolve().parent.parent / "output"
    if argv:
        files = [Path(a) for a in argv]
        blank = True if forced_blank else None
    else:
        files = [
            base / "Handmade Product Pricing & Profit Calculator.xlsx",
            base / "Handmade Product Pricing & Profit Calculator (Blank).xlsx",
        ]
        blank = None
    rc = 0
    for f in files:
        is_blank = blank if blank is not None else ("Blank" in f.name)
        rc |= validate(f, blank=is_blank)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
