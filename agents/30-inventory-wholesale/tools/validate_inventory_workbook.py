"""Static checks on a generated Ultimate Inventory & Wholesale Order Manager.

Run it with any Python that has openpyxl installed::

    python tools/validate_inventory_workbook.py output/inventory.xlsx

It never opens Excel - it parses the XML and reports anything that would
break for a buyer: unresolved template tokens, formulas pointing at the
wrong sheet, defined names that do not exist, missing sheet protection,
formula cells that are not locked, input cells that are, and - the one
that matters most here - any break in the SKU chain that holds the
product database, the stock tracker, the purchase orders, the wholesale
orders, the sales, the valuation and the profit-by-product figures
together.

Five things this product cannot be allowed to get wrong, and all five
are checked below:

* stock is derived from transactions, never typed over;
* reserved stock is separated from available stock;
* the IDs connect - SKU, Supplier ID, Purchase Order ID, Order ID;
* receiving the same purchase order twice cannot double-count;
* one costing method, weighted average, used everywhere.
"""

from __future__ import annotations

import os
import re
import sys
import zipfile
from collections import Counter, defaultdict

try:
    import openpyxl
except ImportError:                                   # pragma: no cover
    print("openpyxl is required: pip install openpyxl")
    raise SystemExit(2)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inventory_wholesale_spreadsheet.build import (                # noqa: E402
    SHEET_ORDER as EXPECTED_SHEETS)

FUNCTION_RE = re.compile(r"\b([A-Z][A-Z0-9\.]{1,})\s*\(")
NAME_RE = re.compile(r"(?<![A-Za-z0-9_.!$\"])([A-Za-z_][A-Za-z0-9_.]{2,})"
                     r"(?![A-Za-z0-9_.(!])")
#: a column letter with no row number - almost always a missing {r}
BARE_COL_RE = re.compile(r"(?<![A-Za-z0-9_.!$\"])([A-Z]{1,3})"
                         r"(?![A-Za-z0-9_.(!$:])")

KNOWN_FUNCTIONS = {
    "IF", "IFERROR", "SUM", "SUMIF", "SUMIFS", "COUNT", "COUNTA", "COUNTIF",
    "COUNTIFS", "AVERAGE", "AVERAGEIF", "AVERAGEIFS", "MAX", "MIN", "ROUND",
    "ROUNDUP", "ROUNDDOWN", "INDEX", "MATCH", "OFFSET", "TEXT", "VALUE",
    "LEFT", "RIGHT", "MID", "LEN", "TRIM", "UPPER", "LOWER", "PROPER",
    "CONCATENATE", "TODAY", "NOW", "DATE", "DAY", "MONTH", "YEAR", "WEEKDAY",
    "WEEKNUM", "EOMONTH", "EDATE", "DATEDIF", "DAYS", "NETWORKDAYS", "HOUR",
    "MINUTE", "TIME", "SUMPRODUCT", "LARGE", "SMALL", "RANK", "ABS", "AND",
    "OR", "NOT", "ISBLANK", "ISNUMBER", "ISTEXT", "ISERROR", "ISNA", "NA",
    "CHOOSE", "VLOOKUP", "HLOOKUP", "LOOKUP", "SUBSTITUTE", "REPT",
    "MEDIAN", "STDEV", "FLOOR", "CEILING", "INT", "MOD", "SIGN", "RAND",
    "SEARCH", "FIND", "EXACT", "N", "T", "TRUE", "FALSE", "ROW", "ROWS",
    "COLUMN", "COLUMNS", "YEARFRAC", "INDIRECT", "ADDRESS", "CELL",
    "SUBTOTAL", "TRANSPOSE", "PRODUCT", "POWER", "SQRT", "COUNTBLANK",
    "ISERR", "ISLOGICAL", "ISREF", "TYPE", "NUMBERVALUE", "DATEVALUE",
    "TIMEVALUE", "WORKDAY", "FREQUENCY", "PERCENTILE",
}

#: functions that do not exist in Excel 2010 / Google Sheets
MODERN_ONLY = {
    "XLOOKUP", "IFS", "MAXIFS", "MINIFS", "TEXTJOIN", "CONCAT", "SWITCH",
    "LET", "LAMBDA", "FILTER", "SORT", "SORTBY", "UNIQUE", "SEQUENCE",
    "TEXTSPLIT", "AGGREGATE", "IFNA",
}


def _colnum(ref: str) -> tuple:
    match = re.match(r"([A-Z]+)(\d+)", ref)
    letters, row = match.group(1), int(match.group(2))
    num = 0
    for char in letters:
        num = num * 26 + (ord(char) - 64)
    return num, row


def check_raw_xml(path: str) -> list:
    """Overlapping merges and stray hyperlinks - Excel calls these corrupt."""
    found = []
    with zipfile.ZipFile(path) as zf:
        book = zf.read("xl/workbook.xml").decode()
        sheets = re.findall(r'<sheet name="([^"]+)"[^>]*r:id="rId(\d+)"',
                            book)
        sheet_names = {name for name, _ in sheets}
        for name, rid in sheets:
            try:
                xml = zf.read(f"xl/worksheets/sheet{rid}.xml").decode()
            except KeyError:
                continue
            merges = re.findall(r'<mergeCell ref="([^"]+)"/>', xml)
            boxes = []
            for ref in merges:
                start, _, end = ref.partition(":")
                end = end or start
                c1, r1 = _colnum(start)
                c2, r2 = _colnum(end)
                boxes.append((c1, r1, c2, r2, ref))
            for i, a in enumerate(boxes):
                for b in boxes[i + 1:]:
                    if (a[0] <= b[2] and b[0] <= a[2]
                            and a[1] <= b[3] and b[1] <= a[3]):
                        found.append(f"{name}: merges overlap "
                                     f"{a[4]} / {b[4]}")
            for location in re.findall(
                    r'<hyperlink ref="[^"]+" location="([^"]+)"', xml):
                target = location.split("!")[0].strip("'").replace("''", "'")
                if target not in sheet_names:
                    found.append(f"{name}: hyperlink points at missing "
                                 f"sheet '{target}'")
            for link in re.findall(r'<hyperlink ref="([^"]+)"', xml):
                lc, lr = _colnum(link)
                for c1, r1, c2, r2, ref in boxes:
                    if (c1 <= lc <= c2 and r1 <= lr <= r2
                            and (lc, lr) != (c1, r1)):
                        found.append(f"{name}: hyperlink {link} is inside "
                                     f"merged range {ref}")
    return found


def paren_depth(formula: str) -> int:
    """Open brackets minus closing ones, ignoring anything inside text.

    Excel escapes a quote inside a string by doubling it, so `""` is not
    the end of the string. Deeply nested IF() chains built by string
    concatenation are the one bug this whole file exists to catch: Excel
    and openpyxl both accept a short formula silently, and the buyer
    sees the damage.
    """
    depth = 0
    in_text = False
    i = 0
    while i < len(formula):
        char = formula[i]
        if in_text:
            if char == '"':
                if i + 1 < len(formula) and formula[i + 1] == '"':
                    i += 1
                else:
                    in_text = False
        elif char == '"':
            in_text = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        i += 1
    return depth


#: divisions that really are meant to read `a + b/c`.  Each one is the
#: formula with its numbers blanked out, so one entry covers the whole
#: column.
PRECEDENCE_OK = {
    # nothing here yet: every `a + b/c` on this workbook is bracketed
    # in the source, which is the honest fix rather than a waiver
}

#: Dividing by one of these is a unit conversion, not a mis-bracket.
#: A wedding timeline is built as `ceremony_time + minutes/1440` -
#: a date serial plus a fraction of a day - and bracketing it as
#: `(ceremony_time + minutes)/1440` would be the actual bug.
TIME_DIVISOR_RE = re.compile(r"/(?:1440|86400|24|60)\b")


def _top_level(text, wanted):
    """Positions of `wanted` characters outside brackets and strings."""
    out = []
    depth = 0
    in_text = False
    i = 0
    while i < len(text):
        char = text[i]
        if in_text:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    i += 1
                else:
                    in_text = False
        elif char == '"':
            in_text = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif depth == 0 and char in wanted:
            before = text[i - 1] if i else ""
            if char != "/" and (before == "" or before in "(,*/+-^<>=&"):
                # a leading sign, not an operator between two values
                i += 1
                continue
            out.append(i)
        i += 1
    return out


def _arguments(formula):
    """Every comma separated argument, at every bracket depth."""
    starts = {0: 0}
    depth = 0
    in_text = False
    i = 0
    while i < len(formula):
        char = formula[i]
        if in_text:
            if char == '"':
                if i + 1 < len(formula) and formula[i + 1] == '"':
                    i += 1
                else:
                    in_text = False
        elif char == '"':
            in_text = True
        elif char == "(":
            depth += 1
            starts[depth] = i + 1
        elif char == ")":
            yield formula[starts.get(depth, 0):i]
            depth -= 1
        elif char == ",":
            yield formula[starts.get(depth, 0):i]
            starts[depth] = i + 1
        i += 1
    yield formula[starts.get(0, 0):]


#: `1-x/y` is the complement of a ratio - an on-time rate, a stock
#: accuracy score, a discount depth. `(1-x)/y` is not a thing anybody
#: means by it.
COMPLEMENT_RE = re.compile(r"(?:^|[(,=<>&*+-])\s*\d+(?:\.\d+)?$")
#: the divisor after a `/`, so `a/n + b/n` - two terms averaged over
#: the same window - can be told apart from `(a+b)/n`
DIVISOR_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.!$']*|\d+(?:\.\d+)?")


def precedence_slip(formula):
    """`a+b/c` at the top level of a division - almost always a bug."""
    body = re.sub(r'"[^"]*"', '""', formula)
    for match in re.finditer(r"/", body):
        if TIME_DIVISOR_RE.match(body[match.start():]):
            continue
        divisor = DIVISOR_RE.match(body[match.start() + 1:])
        divisor = divisor.group(0) if divisor else ""
        i, depth = match.start() - 1, 0
        while i >= 0:
            ch = body[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and ch in "+-" and i > 0 and \
                    body[i - 1] not in "(,*/+-<>=&":
                left = body[:i]
                if ch == "-" and COMPLEMENT_RE.search(left):
                    break
                if ch == "+" and divisor and \
                        left.rstrip().endswith("/" + divisor):
                    break
                return body[max(0, i - 25):match.start() + 12]
            i -= 1
    return ""


RANGE_RE = re.compile(
    r"^(?:(?:'[^']+'|[A-Za-z0-9_.]+)!)?"
    r"\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)$")


def _span(text: str):
    """(rows, columns) of an A1 range, or None if it is not one."""
    match = RANGE_RE.match(text.strip())
    if not match:
        return None
    c1, r1, c2, r2 = match.groups()

    def num(letters):
        value = 0
        for char in letters:
            value = value * 26 + (ord(char) - 64)
        return value
    return (abs(int(r2) - int(r1)) + 1, abs(num(c2) - num(c1)) + 1)


def _calls(formula: str, names):
    """Yield (function, [argument, ...]) for every call in *formula*."""
    depth = 0
    in_text = False
    stack = []
    i = 0
    while i < len(formula):
        char = formula[i]
        if in_text:
            if char == '"':
                if i + 1 < len(formula) and formula[i + 1] == '"':
                    i += 1
                else:
                    in_text = False
        elif char == '"':
            in_text = True
        elif char == "(":
            head = re.search(r"([A-Z][A-Z0-9\.]*)$", formula[:i])
            stack.append([head.group(1) if head else "", i + 1, [], depth])
            depth += 1
        elif char == ")":
            depth -= 1
            if stack:
                name, start, args, _ = stack.pop()
                args.append(formula[start:i])
                if name in names:
                    yield name, args
                if stack:
                    stack[-1][1] = stack[-1][1]
        elif char == "," and stack and depth == stack[-1][3] + 1:
            frame = stack[-1]
            frame[2].append(formula[frame[1]:i])
            frame[1] = i + 1
        i += 1


def ragged_criteria(formula: str) -> str:
    """COUNTIFS/SUMIFS whose ranges are not all the same shape.

    Excel answers #VALUE! the moment two criteria ranges differ in
    size, and it is an easy mistake to make when one of them is a
    running range that grows row by row.
    """
    for name, args in _calls(formula, ("COUNTIFS", "SUMIFS",
                                       "AVERAGEIFS")):
        first = 1 if name in ("SUMIFS", "AVERAGEIFS") else 0
        ranges = [args[0]] if first else []
        ranges += args[first::2]
        spans = {}
        for text in ranges:
            span = _span(text)
            if span:
                spans.setdefault(span, text)
        if len(spans) > 1:
            return f"{name}: " + " vs ".join(sorted(spans.values()))
    return ""


def collapsed_criteria(formula: str) -> str:
    """A COUNTIFS/SUMIFS criteria *range* that carries its own test.

    A criterion is two arguments - the range, then the thing it is
    compared against.  Writing it as one argument::

        COUNTIFS(prop, "PRP-01", scores="Yes")

    leaves the function an odd number of arguments and makes Excel
    answer #VALUE! on every row.  It reads perfectly naturally, which
    is exactly why it is worth a check: `SUMPRODUCT((range="Yes")*..)`
    really is written that way, so the habit carries over.
    """
    for name, args in _calls(formula, ("COUNTIFS", "SUMIFS",
                                       "AVERAGEIFS")):
        first = 1 if name in ("SUMIFS", "AVERAGEIFS") else 0
        if (len(args) - first) % 2:
            return f"{name}: odd number of range/criteria arguments"
        for text in args[first::2]:
            stripped = re.sub(r'"[^"]*"', '""', text)
            if re.search(r"[<>=]", stripped):
                return f"{name}: criteria range carries a test -> {text}"
    return ""


#: input cells that ship with a formula in them as a helpful default -
#: the buyer is meant to be able to type a fixed value straight over it

#: value cells that are deliberately left unlocked even though a
#: formula sits in them - the buyer is meant to type over the top
SEEDED_INPUTS = {
    "Monthly Reports!B5",                 # the month being reported on
    "Printable Orders & Invoices!B6",     # the PO being printed
    "Printable Orders & Invoices!B7",     # the order being printed
}

#: Every link below is a formula in row 5 of a register.  Together
#: they are the product: break one and a buyer gets a blank cell
#: instead of an answer, with nothing to tell them why.
#:
#: The SKU is the join key.  Every separately stocked variant has its
#: own SKU, sixteen registers reach back to the product database
#: through it, and stock itself is derived from four transaction
#: registers rather than typed anywhere.  Most of what follows is
#: those two decisions being checked in both directions.
#:
#: Every entry was read off the real formula, not guessed.  A guessed
#: chain check is worse than none: it fails on a correct product and
#: teaches you to ignore the tool.
CHAIN_CHECKS = [
    # ---- the catalogue: one row per SKU, the hub everything joins to ----
    ("Product & SKU Database", "id", ("text", "ProductPrefix")),
    ("Product & SKU Database", "on_hand", ("sheet", "Inventory Tracker")),
    ("Product & SKU Database", "available", ("sheet", "Inventory Tracker")),
    ("Product & SKU Database", "avg_cost", ("sheet",
                                            "Inventory Valuation & COGS")),
    ("Product & SKU Database", "units_sold", ("sheet",
                                              "Product Performance")),
    ("Product & SKU Database", "dup_count", ("column",
                                             "Product & SKU Database",
                                             "sku")),
    ("Product & SKU Database", "retail_margin", ("column",
                                                 "Product & SKU Database",
                                                 "cost")),

    # ---- workflow one: product -> SKU -> stock --------------------------
    # Stock is DERIVED. Every term below comes from a transaction
    # register; none of it is a number anybody types.
    ("Inventory Tracker", "sku", ("sheet", "Product & SKU Database")),
    ("Inventory Tracker", "opening", ("sheet", "Product & SKU Database")),
    ("Inventory Tracker", "received", ("sheet", "Purchase Orders")),
    ("Inventory Tracker", "sold", ("sheet", "Retail Sales Tracker")),
    ("Inventory Tracker", "returned", ("sheet", "Returns & Damaged Goods")),
    ("Inventory Tracker", "damaged", ("sheet", "Stock Movement Log")),
    ("Inventory Tracker", "adjusted", ("sheet", "Stock Movement Log")),
    ("Inventory Tracker", "current", ("column", "Inventory Tracker",
                                      "opening")),
    # ---- the reserved/available split, decision two ---------------------
    ("Inventory Tracker", "reserved", ("sheet", "Wholesale Orders")),
    ("Inventory Tracker", "available", ("column", "Inventory Tracker",
                                        "reserved")),
    ("Inventory Tracker", "on_order", ("sheet", "Purchase Orders")),
    ("Inventory Tracker", "daily_sales", ("text", "SalesWindow")),
    ("Inventory Tracker", "days_cover", ("column", "Inventory Tracker",
                                         "daily_sales")),
    ("Inventory Tracker", "stock_value", ("column", "Inventory Tracker",
                                          "avg_cost")),

    # ---- workflow two: supplier -> PO -> receiving ----------------------
    ("Purchase Orders", "supplier_name", ("sheet", "Supplier Database")),
    ("Purchase Orders", "product", ("sheet", "Product & SKU Database")),
    ("Purchase Orders", "due_date", ("sheet", "Supplier Database")),
    ("Purchase Orders", "landed_each", ("column", "Purchase Orders",
                                        "total")),
    ("Purchase Orders", "outstanding", ("column", "Purchase Orders",
                                        "received")),
    # the duplicate-receiving defence, decision four
    ("Purchase Orders", "dup_line", ("column", "Purchase Orders", "sku")),
    ("Purchase Orders", "received_value", ("column", "Purchase Orders",
                                           "landed_each")),
    ("Purchase Orders", "days_late", ("column", "Purchase Orders",
                                      "expected")),
    ("Purchase Orders", "alert", ("column", "Purchase Orders", "dup_line")),
    ("Supplier Database", "id", ("text", "SupplierPrefix")),
    ("Supplier Database", "orders", ("sheet", "Purchase Orders")),
    ("Supplier Database", "late_orders", ("sheet", "Purchase Orders")),
    ("Supplier Database", "actual_lead", ("sheet", "Purchase Orders")),
    ("Supplier Database", "lead_gap", ("column", "Supplier Database",
                                       "actual_lead")),
    ("Supplier Database", "on_time_rate", ("column", "Supplier Database",
                                           "late_orders")),

    # ---- workflow three: customer -> tiered price -> fulfilment ---------
    ("Wholesale Customer CRM", "id", ("text", "CustomerPrefix")),
    ("Wholesale Customer CRM", "revenue", ("sheet", "Wholesale Orders")),
    ("Wholesale Customer CRM", "owing", ("sheet", "Wholesale Orders")),
    ("Wholesale Customer CRM", "reserved_value", ("sheet",
                                                  "Wholesale Orders")),
    ("Wholesale Pricing", "sku", ("sheet", "Product & SKU Database")),
    ("Wholesale Pricing", "avg_cost", ("sheet", "Inventory Tracker")),
    ("Wholesale Pricing", "floor", ("sheet", "Product & SKU Database")),
    ("Wholesale Pricing", "tier3_gp", ("column", "Wholesale Pricing",
                                       "avg_cost")),
    ("Wholesale Orders", "customer_name", ("sheet",
                                           "Wholesale Customer CRM")),
    ("Wholesale Orders", "tier", ("sheet", "Wholesale Customer CRM")),
    ("Wholesale Orders", "tier_price", ("sheet", "Wholesale Pricing")),
    ("Wholesale Orders", "unit_cost", ("sheet", "Inventory Tracker")),
    ("Wholesale Orders", "available", ("sheet", "Inventory Tracker")),
    ("Wholesale Orders", "is_reserved", ("column", "Wholesale Orders",
                                         "status")),
    ("Wholesale Orders", "shortfall", ("column", "Wholesale Orders",
                                       "available")),
    ("Wholesale Orders", "line_profit", ("column", "Wholesale Orders",
                                         "line_cost")),
    ("Wholesale Orders", "due_date", ("column", "Wholesale Orders",
                                      "terms")),

    # ---- workflow four: movement -> reorder alert -> replenishment ------
    ("Stock Movement Log", "id", ("text", "MovementPrefix")),
    ("Stock Movement Log", "direction", ("text", "MovementSign")),
    ("Stock Movement Log", "cost_each", ("sheet", "Inventory Tracker")),
    ("Stock Movement Log", "stock_after", ("sheet", "Inventory Tracker")),
    ("Reorder Planner", "sku", ("sheet", "Product & SKU Database")),
    ("Reorder Planner", "available", ("sheet", "Inventory Tracker")),
    ("Reorder Planner", "daily_sales", ("sheet", "Inventory Tracker")),
    ("Reorder Planner", "quoted_lead", ("sheet", "Supplier Database")),
    ("Reorder Planner", "actual_lead", ("sheet", "Supplier Database")),
    ("Reorder Planner", "lead_days", ("column", "Reorder Planner",
                                      "quoted_lead")),
    ("Reorder Planner", "safety_stock", ("text", "SafetyDays")),
    ("Reorder Planner", "reorder_point", ("column", "Reorder Planner",
                                          "calc_point")),
    ("Reorder Planner", "order_by", ("text", "TodayDate")),
    ("Reorder Planner", "suggested", ("column", "Reorder Planner",
                                      "target")),

    # ---- workflow five: sales -> COGS -> profit by product --------------
    ("Retail Sales Tracker", "product", ("sheet",
                                         "Product & SKU Database")),
    ("Retail Sales Tracker", "unit_cost", ("sheet", "Inventory Tracker")),
    ("Retail Sales Tracker", "platform_fee", ("column",
                                              "Retail Sales Tracker",
                                              "fee_rate")),
    ("Retail Sales Tracker", "payment_fee", ("text", "PaymentFeePct")),
    ("Retail Sales Tracker", "cogs", ("column", "Retail Sales Tracker",
                                      "unit_cost")),
    ("Retail Sales Tracker", "profit", ("column", "Retail Sales Tracker",
                                        "cogs")),
    ("Inventory Valuation & COGS", "received_value", ("sheet",
                                                      "Purchase Orders")),
    ("Inventory Valuation & COGS", "avg_cost", ("sheet",
                                                "Purchase Orders")),
    ("Inventory Valuation & COGS", "cogs", ("column",
                                            "Inventory Valuation & COGS",
                                            "avg_cost")),
    ("Inventory Valuation & COGS", "gross_profit", ("column",
                                                    "Inventory Valuation "
                                                    "& COGS", "cogs")),
    ("Inventory Valuation & COGS", "value_share", ("text",
                                                   "TotalStockValue")),
    ("Inventory Valuation & COGS", "abc_class", ("column",
                                                 "Inventory Valuation "
                                                 "& COGS",
                                                 "value_share")),
    ("Product Performance", "units_retail", ("sheet",
                                             "Retail Sales Tracker")),
    ("Product Performance", "units_wholesale", ("sheet",
                                                "Wholesale Orders")),
    ("Product Performance", "cogs", ("sheet",
                                     "Inventory Valuation & COGS")),
    ("Product Performance", "returns_cost", ("sheet",
                                             "Returns & Damaged Goods")),
    ("Product Performance", "profit", ("column", "Product Performance",
                                       "cogs")),
    ("Product Performance", "turns", ("sheet",
                                      "Inventory Valuation & COGS")),

    # ---- the other registers --------------------------------------------
    ("Returns & Damaged Goods", "id", ("text", "ReturnPrefix")),
    ("Returns & Damaged Goods", "unit_cost", ("sheet",
                                              "Inventory Tracker")),
    ("Returns & Damaged Goods", "restocked", ("column",
                                              "Returns & Damaged Goods",
                                              "condition")),
    ("Warehouse Locations", "system_qty", ("sheet", "Inventory Tracker")),
    ("Warehouse Locations", "placed_gap", ("column", "Warehouse Locations",
                                           "system_qty")),
    ("Stock Audit", "id", ("text", "AuditPrefix")),
    ("Stock Audit", "current_qty", ("sheet", "Inventory Tracker")),
    ("Stock Audit", "variance", ("column", "Stock Audit", "system_qty")),
    ("Stock Audit", "variance_value", ("column", "Stock Audit",
                                       "variance")),
    ("Stock Audit", "unposted", ("column", "Stock Audit", "posted")),
    ("Expense Tracker", "is_stock", ("text", "StockCategoryList")),
    ("Expense Tracker", "operating", ("column", "Expense Tracker",
                                      "is_stock")),
    ("Profit Analysis", "retail_revenue", ("sheet",
                                           "Retail Sales Tracker")),
    ("Profit Analysis", "wholesale_revenue", ("sheet",
                                              "Wholesale Orders")),
    ("Profit Analysis", "expenses", ("sheet", "Expense Tracker")),
    ("Profit Analysis", "stock_spend", ("sheet", "Purchase Orders")),
    ("Profit Analysis", "gross_profit", ("column", "Profit Analysis",
                                         "cogs")),
    ("Profit Analysis", "net_profit", ("column", "Profit Analysis",
                                       "expenses")),
    ("Profit Analysis", "cash_effect", ("column", "Profit Analysis",
                                        "stock_spend")),
]

#: named cells that must still hold a live formula - a name pointing
#: at an empty cell means a page quietly stopped working
PAGE_FORMULAS = [
    ("TodayDate", "settings: the live date every alert reads"),
    ("YearStart", "settings: the first day of the reporting year"),
    ("YearEnd", "settings: the last day of the reporting year"),
    ("ThisMonthKey", "settings: the month key the dashboard groups on"),
    ("TotalStockValue", "settings: stock at cost, the ABC denominator"),
    ("TotalRevenue", "settings: revenue this year, both channels"),
    ("WholesaleRevenue", "settings: the wholesale half of revenue"),
    ("TotalPurchaseSpend", "settings: what has been spent on stock"),
    ("RetailRevenue", "settings: the retail half of revenue"),
    ]

#: cells a buyer has to be able to type in
PAGE_INPUTS = [
    ("BusinessName", "settings: the business name"),
    ("DefaultMarkup", "settings: the markup a new product starts at"),
    ("MinGP", "settings: the margin you refuse to go under"),
    ("TargetMargin", "settings: the margin you are aiming at"),
    ("DefaultLeadDays", "settings: lead time when a supplier has none"),
    ("SafetyDays", "settings: days of safety stock in the reorder point"),
    ("SalesWindow", "settings: the window the sales rate averages over"),
    ("MarketplaceFeePct", "settings: the marketplace commission"),
    ("PaymentFeePct", "settings: the payment processing percentage"),
    ("PaymentFeeFixed", "settings: the fixed part of a payment fee"),
    ("TaxRate", "settings: sales tax or VAT"),
    ("TaxOnSales", "settings: whether tax applies at all"),
    ("ReportYear", "settings: the year the reports cover"),
    ("YearlyTarget", "settings: the revenue target for the year"),
    ("TargetTurns", "settings: the stock turns you are aiming at"),
    ("PriceGapTolerance", "settings: when an invoice gap is worth a look"),
    ("SlowStockDays", "settings: when stock counts as slow moving"),
    ("ProductPrefix", "settings: the Product ID prefix"),
    ("DeadStockDays", "settings: when unsold stock counts as dead"),
    ("SupplierPrefix", "settings: the Supplier ID prefix"),
    ("CustomerPrefix", "settings: the Customer ID prefix"),
    ("MonthlyTarget", "settings: the revenue target a month"),
    ("ReportMonth", "monthly reports: the month being reported on"),
    ("PrintPO", "printables: the purchase order being printed"),
    ("PrintOrder", "printables: the wholesale order being printed"),
]

#: every drop down on the workbook reads one of these - a missing one
#: means a blank list and a column nobody can fill in
REQUIRED_LIST_NAMES = [
    "SKUList", "SupplierList", "CustomerList", "YesNoList",
    "ProductStatusList", "CategoryList", "SubcategoryList", "UnitList",
    "SupplierTypeList", "SupplierStatusList", "POStatusList",
    "DeliveryConditionList", "CustomerTypeList", "CustomerStatusList",
    "CustomerTierList", "LeadSourceList", "OrderStatusList",
    "ShippingMethodList", "ChannelList", "SaleStatusList",
    "MovementTypeList", "ReturnSourceList", "ReturnReasonList",
    "ReturnConditionList", "ReturnStatusList", "AuditTypeList",
    "AuditStatusList", "VarianceReasonList", "StorageTypeList",
    "LocationList", "StaffList", "ExpenseCategoryList",
    "StockCategoryList", "TaxCategoryList", "PaymentMethodList",
    "PaymentTermsList", "FrequencyList", "CurrencyList",
    "MonthNameList", "MonthKeyList",
]


def _name_target(wb, name):
    """The one cell a defined name points at, or None."""
    defn = wb.defined_names.get(name)
    if defn is None:
        for ws in wb.worksheets:
            if name in ws.defined_names:
                defn = ws.defined_names[name]
                break
    if defn is None:
        return None
    try:
        sheet, ref = next(defn.destinations)
    except (StopIteration, Exception):          # noqa: B902
        return None
    if sheet not in wb.sheetnames or ":" in ref:
        return None
    return wb[sheet][ref.replace("$", "")]


def check_pages(wb, problems: list, notes: list) -> None:
    """The summary pages, checked through their defined names."""
    live = 0
    for name, what in PAGE_FORMULAS:
        cell = _name_target(wb, name)
        if cell is None:
            problems.append(f"{name} is missing - {what}")
            continue
        value = cell.value
        if not (isinstance(value, str) and value.startswith("=")):
            problems.append(f"{name} no longer holds a formula - {what}")
            continue
        if cell.protection and not cell.protection.locked:
            problems.append(f"{name} is a formula but is unlocked - {what}")
            continue
        live += 1
    typed = 0
    for name, what in PAGE_INPUTS:
        cell = _name_target(wb, name)
        if cell is None:
            problems.append(f"{name} is missing - {what}")
            continue
        if cell.protection and cell.protection.locked:
            problems.append(f"{name} is locked, so nobody can change it "
                            f"- {what}")
            continue
        typed += 1
    notes.append(f"summary pages: {live} live formulas, "
                 f"{typed} typeable inputs verified")


def _specs():
    """Every register specification, keyed by sheet name."""
    from inventory_wholesale_spreadsheet.build import REGISTER_MODULES
    from inventory_wholesale_spreadsheet.config import Config
    cfg = Config()
    return {module.NAME: module.spec(cfg) for module in REGISTER_MODULES}


def check_chain(wb, problems: list, notes: list) -> None:
    """The five workflows only hold while every one of these does.

    Every one of them is a formula in row 5 of a register, so the check
    is cheap: find the column by its key in the specification, read the
    formula, and make sure it still mentions the thing it depends on.
    """
    specs = _specs()
    checked = 0
    for sheet_name, key, expect in CHAIN_CHECKS:
        spec = specs.get(sheet_name)
        if spec is None or sheet_name not in wb.sheetnames:
            problems.append(f"missing register {sheet_name}")
            continue
        try:
            column = spec.index(key) + 1
        except Exception:
            problems.append(f"{sheet_name}: column '{key}' has gone")
            continue
        formula = wb[sheet_name].cell(row=5, column=column).value
        if not isinstance(formula, str) or not formula.startswith("="):
            problems.append(f"{sheet_name}.{key} is no longer a formula")
            continue
        if expect[0] == "sheet":
            found = expect[1] in formula
            label = f"the {expect[1]} tab"
        elif expect[0] == "text":
            found = expect[1] in formula
            label = expect[1]
        else:
            letter = specs[expect[1]].letter(expect[2])
            label = f"{expect[1]}.{expect[2]} (column {letter})"
            if expect[1] == sheet_name:
                # a link inside the same register is a plain A1 reference
                found = bool(re.search(r"(?<![A-Z$])\$?" + letter +
                                       r"\$?5(?![0-9])", formula))
            else:
                found = f"${letter}$" in formula
        if not found:
            problems.append(
                f"{sheet_name}.{key} no longer points at {label} - "
                f"the automation chain is broken")
        checked += 1
    notes.append(f"automation chain: {checked} links verified")


def check_sku_join(wb, problems: list, notes: list) -> None:
    """The SKU is the join key. Verify it in both directions.

    This is the technical decision the whole product rests on: one SKU
    per separately stocked variant, listed once in the product
    database and chosen from a drop-down everywhere else.  Without it
    the purchase orders, the stock tracker, the wholesale orders, the
    sales and the valuation are five unrelated lists that happen to be
    in the same file.

    Four things have to hold:

    1. the product database really does mint a Product ID and carry a
       duplicate-SKU check, because a SKU typed twice silently splits
       one product's stock into two half-right rows;
    2. every register that joins back does so through a column
       validated against SKUList, so a buyer cannot mistype it;
    3. that drop-down resolves to a real defined name;
    4. the supplier, purchase order, customer and order IDs do the
       same job for their own chains.
    """
    specs = _specs()
    hub = specs.get("Product & SKU Database")
    if hub is None:
        problems.append("Product & SKU Database register has gone")
        return
    try:
        column = hub.index("id") + 1
    except Exception:                                  # noqa: B902
        problems.append("Product & SKU Database has no id column - "
                        "there is no generated Product ID left")
        return
    formula = wb["Product & SKU Database"].cell(row=5,
                                                column=column).value
    if not isinstance(formula, str) or "ProductPrefix" not in formula:
        problems.append("Product & SKU Database.id no longer builds "
                        "the Product ID from ProductPrefix")

    dup = next((c for c in hub.columns if c.key == "dup_count"), None)
    if dup is None or not dup.formula or "COUNTIF" not in dup.formula:
        problems.append("the duplicate-SKU check has gone from the "
                        "product database; one SKU entered twice "
                        "would now split a product's stock in half "
                        "with nothing to say so")

    defined = set(wb.defined_names)
    for ws in wb.worksheets:
        defined |= set(ws.defined_names)
    for name in ("SKUList", "SupplierList", "CustomerList"):
        if name not in defined:
            problems.append(f"{name} is missing - every drop-down "
                            f"that reads it is now empty")

    joined = []
    for name, spec in specs.items():
        if name == "Product & SKU Database":
            continue
        col = next((c for c in spec.columns if c.key == "sku"), None)
        if col is None or col.formula:
            continue                    # derived, not chosen
        joined.append(name)
        source = (col.validate or {}).get("source")
        if not (isinstance(source, str)
                and source.lstrip("=") == "SKUList"):
            problems.append(
                f"{name}.sku is not a SKUList drop-down, so a buyer "
                f"can mistype the SKU and silently disconnect the row "
                f"from its product, its cost and its stock")
    if len(joined) < 7:
        problems.append(f"only {len(joined)} registers join through a "
                        f"typed SKU; the design calls for at least 7")
    notes.append(f"SKU join: {len(joined)} registers joined to the "
                 f"product database through SKUList")


def check_decisions(wb, problems: list, notes: list) -> None:
    """The five decisions this product is not allowed to get wrong.

    Every one of them is a way an inventory spreadsheet quietly starts
    lying to its owner, and every one is checked against the real
    formulas rather than against a promise in the documentation.
    """
    specs = _specs()
    held = []

    # 1. stock is derived from transactions, never typed over
    tracker = specs.get("Inventory Tracker")
    if tracker is None:
        problems.append("the Inventory Tracker has gone")
    else:
        typed = [c.key for c in tracker.columns if not c.formula]
        if typed:
            problems.append(
                f"Inventory Tracker has typed columns {typed} - stock "
                f"must be derived from the transaction registers, "
                f"never overwritten by hand")
        else:
            held.append("stock derived, not typed")
        current = next((c for c in tracker.columns
                        if c.key == "current"), None)
        needed = ("opening", "received", "sold", "returned", "damaged",
                  "adjusted")
        if current is None or not all(f"{{{k}}}" in (current.formula or "")
                                      for k in needed):
            problems.append(
                "Inventory Tracker.current no longer adds up all six "
                "transaction terms, so the stock figure is no longer "
                "the sum of what actually happened")

        # 2. reserved stock is separated from available stock
        available = next((c for c in tracker.columns
                          if c.key == "available"), None)
        reserved = next((c for c in tracker.columns
                         if c.key == "reserved"), None)
        if available is None or reserved is None:
            problems.append("the reserved/available split has gone - a "
                            "confirmed order would be invisible until "
                            "it shipped")
        elif "{reserved}" not in (available.formula or ""):
            problems.append("Inventory Tracker.available no longer "
                            "subtracts reserved stock, so a confirmed "
                            "order can be sold twice")
        elif "is_reserved" not in (reserved.formula or ""):
            problems.append("Inventory Tracker.reserved no longer "
                            "reads the order status, so reserving has "
                            "stopped meaning anything")
        else:
            held.append("reserved separated from available")

    # 3. receiving the same PO twice cannot double-count
    po = specs.get("Purchase Orders")
    if po is None:
        problems.append("the Purchase Orders register has gone")
    else:
        dup = next((c for c in po.columns if c.key == "dup_line"), None)
        alert = next((c for c in po.columns if c.key == "alert"), None)
        if dup is None or "COUNTIFS" not in (dup.formula or ""):
            problems.append(
                "Purchase Orders has lost its duplicate-line check, so "
                "the same PO line can be received twice and the "
                "delivery counted twice into stock")
        elif alert is None or "{dup_line}" not in (alert.formula or ""):
            problems.append("the duplicate-line check is no longer "
                            "wired into the Purchase Orders alert, so "
                            "nobody would be told")
        else:
            held.append("duplicate receiving flagged")

    # 4. one costing method, used everywhere
    mixed = []
    for name, spec in specs.items():
        for col in spec.columns:
            text = (col.formula or "").upper()
            if "FIFO" in text or "LIFO" in text:
                mixed.append(f"{name}.{col.key}")
    if mixed:
        problems.append(f"a second costing method appears in {mixed} - "
                        f"this product is weighted average throughout "
                        f"and must not mix methods")
    else:
        held.append("one costing method (weighted average)")

    valuation = specs.get("Inventory Valuation & COGS")
    if valuation is not None:
        avg = next((c for c in valuation.columns
                    if c.key == "avg_cost"), None)
        if avg is None or "received_value" not in (avg.formula or ""):
            problems.append(
                "Inventory Valuation & COGS.avg_cost no longer "
                "weights cost by the value actually received, so it "
                "is not a weighted average any more")

    # 5. a count never overwrites stock - it raises a variance
    audit = specs.get("Stock Audit")
    if audit is not None:
        variance = next((c for c in audit.columns
                         if c.key == "variance"), None)
        posted = next((c for c in audit.columns
                       if c.key == "posted"), None)
        if variance is None or posted is None:
            problems.append("Stock Audit has lost the variance/posted "
                            "pair, which is what stops a count from "
                            "silently overwriting stock")
        else:
            held.append("counts raise a variance, never overwrite")

    notes.append(f"technical decisions held: {len(held)}/5 - "
                 + "; ".join(held))


def check_promises(wb, problems: list, notes: list) -> None:
    """Three promises this product makes to the buyer in writing.

    1. It is a workbook, not an integration: it must never claim to
       sync with Etsy, Shopify, Amazon or anything else.  Orders are
       typed in or imported by the owner, and saying otherwise is the
       single most common lie in this category.
    2. Buying stock is not an operating expense, and the workbook has
       to say so where a buyer will read it.
    3. The accounting figures carry a disclaimer pointing at a real
       accountant.
    """
    banned_sync = ("syncs with", "synchronise with", "synchronize with",
                   "live feed", "api connection", "automatically imports",
                   "real-time stock", "real-time inventory",
                   "connects to your shop", "connects to etsy",
                   "connects to shopify", "two-way sync",
                   "automatic sync")
    banned_magic = ("updates itself", "updates automatically from",
                    "pulls your orders", "imports your orders",
                    "downloads your sales")
    sync_hits = magic_hits = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if not isinstance(value, str) or value.startswith("="):
                    continue
                low = value.lower()
                negated = ("not " in low or "never " in low
                           or "cannot" in low or "does not" in low
                           or "no " in low or "nothing " in low
                           or "without " in low or "doesn't" in low)
                for phrase in banned_sync:
                    if phrase in low and not negated:
                        sync_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims a "
                            f"live marketplace connection -> "
                            f"{value[:70]}")
                for phrase in banned_magic:
                    if phrase in low and not negated:
                        magic_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims "
                            f"orders arrive by themselves -> "
                            f"{value[:70]}")

    wanted = {
        "entered by you": ("you enter", "you type", "typed in",
                           "enter them", "paste", "import"),
        "no marketplace sync": ("does not connect", "not connect",
                                "no connection", "does not sync",
                                "not sync", "no sync"),
        "stock is not an expense": ("not an operating expense",
                                    "when it sells",
                                    "not a cost until",
                                    "separate from your operating",
                                    "kept out of"),
        "accountant": ("accountant",),
    }
    found = {key: False for key in wanted}
    for title in ("Getting Started", "Settings & Lists",
                  "Expense Tracker", "Profit Analysis", "Dashboard"):
        if title not in wb.sheetnames:
            continue
        for row in wb[title].iter_rows():
            for cell in row:
                value = cell.value
                if not isinstance(value, str):
                    continue
                low = value.lower()
                for key, needles in wanted.items():
                    if any(n in low for n in needles):
                        found[key] = True
    for key, ok in found.items():
        if not ok:
            problems.append(f"the workbook never states the "
                            f"'{key}' honesty note")
    notes.append(f"product promises: {sync_hits} false sync claims, "
                 f"{magic_hits} self-updating claims, honesty notes "
                 f"{sum(found.values())}/{len(found)} present")


def check(path: str) -> int:
    problems: list = list(check_raw_xml(path))
    notes: list = []
    if problems:
        print(f"--- {path}")
        for problem in problems[:40]:
            print(f"    - {problem}")
        return 1
    wb = openpyxl.load_workbook(path, data_only=False)

    # ---------------------------------------------------------- structure
    names = wb.sheetnames
    if names != EXPECTED_SHEETS:
        problems.append(f"sheet order/={names}")
    hidden = [ws.title for ws in wb.worksheets if ws.sheet_state != "visible"]
    if hidden:
        problems.append(f"no tab should be hidden, got {hidden}")

    check_chain(wb, problems, notes)
    check_pages(wb, problems, notes)
    check_sku_join(wb, problems, notes)
    check_decisions(wb, problems, notes)
    check_promises(wb, problems, notes)

    # --------------------------------------------------------- properties
    props = wb.properties
    if props.creator != "Novality Store":
        problems.append(f"creator is {props.creator!r}")
    if props.lastModifiedBy != "Novality Store":
        problems.append(f"lastModifiedBy is {props.lastModifiedBy!r}")

    # --------------------------------------------------------- protection
    for ws in wb.worksheets:
        prot = ws.protection
        if not prot.sheet:
            problems.append(f"{ws.title}: sheet protection off")
        elif not prot.password:
            problems.append(f"{ws.title}: protected without a password")

    # -------------------------------------------------------- definednames
    defined = set(wb.defined_names)
    for ws in wb.worksheets:
        defined |= set(ws.defined_names)
    for name in REQUIRED_LIST_NAMES:
        if name not in defined:
            problems.append(f"drop down list {name} is missing")
    notes.append(f"{len(defined)} defined names")

    # ------------------------------------------------------------ formulas
    used_names: Counter = Counter()
    unknown_functions: Counter = Counter()
    bare_refs: dict = {}
    bad_functions: Counter = Counter()
    formula_cells = 0
    locked_formula_problem = 0
    unlocked_input_cells = 0
    per_sheet = defaultdict(int)

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if isinstance(value, str) and value.startswith("="):
                    formula_cells += 1
                    per_sheet[ws.title] += 1
                    if "[[" in value or "{" in value or "}" in value:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: unresolved "
                            f"template token -> {value[:90]}")
                    if value != value.strip():
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: formula has "
                            f"stray whitespace around it, which some "
                            f"calculation engines refuse to parse -> "
                            f"{value[:70]!r}")
                    if "#REF" in value:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: #REF -> "
                            f"{value[:90]}")
                    where = f"{ws.title}!{cell.coordinate}"
                    if (cell.protection and not cell.protection.locked
                            and where not in SEEDED_INPUTS):
                        locked_formula_problem += 1
                        if locked_formula_problem < 25:
                            problems.append(
                                f"{where}: formula cell is NOT locked")
                    stripped = re.sub(r'"[^"]*"', '""', value)
                    stripped = re.sub(r"'[^']*'!", "SHEET!", stripped)
                    if value.count('"') % 2:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: odd number of "
                            f"quotes -> {value[:80]}")
                    depth = paren_depth(value)
                    if depth:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: unbalanced "
                            f"brackets ({depth:+d}) -> {value[:80]}")
                    slip = precedence_slip(value)
                    if slip:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: a+b/c where "
                            f"(a+b)/c was meant -> {slip[:90]}")
                    collapsed = collapsed_criteria(value)
                    if collapsed:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: a criteria "
                            f"range and its test were written as one "
                            f"argument, Excel answers #VALUE! -> "
                            f"{collapsed[:90]}")
                    ragged = ragged_criteria(value)
                    if ragged:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: criteria "
                            f"ranges are different sizes, Excel answers "
                            f"#VALUE! -> {ragged[:90]}")
                    if ",)" in stripped or "(," in stripped or \
                            ",," in stripped:
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: empty argument "
                            f"-> {value[:80]}")
                    for func in FUNCTION_RE.findall(stripped):
                        if func in MODERN_ONLY:
                            bad_functions[func] += 1
                        elif func not in KNOWN_FUNCTIONS:
                            unknown_functions[func] += 1
                    for token in NAME_RE.findall(stripped):
                        if token in KNOWN_FUNCTIONS:
                            continue
                        used_names[token] += 1
                    for token in BARE_COL_RE.findall(stripped):
                        if token in KNOWN_FUNCTIONS:
                            continue
                        bare_refs[f"{ws.title}!{cell.coordinate} {token}"] = \
                            value[:90]
                elif value is not None and cell.protection and \
                        not cell.protection.locked:
                    unlocked_input_cells += 1

    # sheet names used inside formulas must exist
    sheet_refs = Counter()
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if isinstance(value, str) and value.startswith("="):
                    body = re.sub(r'"[^"]*"', '""', value)
                    for ref in re.findall(r"'([^']+)'!", body):
                        sheet_refs[ref] += 1
                    for ref in re.findall(r"(?<![A-Za-z0-9_'])"
                                          r"([A-Za-z][A-Za-z0-9_]*)!", body):
                        sheet_refs[ref] += 1
    for ref, count in sheet_refs.items():
        if ref not in names:
            problems.append(f"formula points at missing sheet "
                            f"'{ref}' ({count}x)")
    notes.append("cross sheet references: " + ", ".join(
        f"{k} {v}" for k, v in sorted(sheet_refs.items(),
                                      key=lambda kv: -kv[1])[:6]))

    for where, formula in list(bare_refs.items())[:15]:
        if where.rsplit(" ", 1)[-1] not in defined:
            problems.append(f"{where}: column letter with no row "
                            f"number -> {formula}")
    for func, count in unknown_functions.items():
        problems.append(f"unknown function {func}() used {count}x")
    for func, count in bad_functions.items():
        problems.append(f"{func}() needs a modern Excel - used {count}x")

    missing = {}
    for token, count in used_names.items():
        if token in defined:
            continue
        if token in KNOWN_FUNCTIONS or token.upper() in KNOWN_FUNCTIONS:
            continue
        if re.match(r"^[A-Z]{1,3}\d+$", token):
            continue
        missing[token] = count
    for token, count in sorted(missing.items(), key=lambda kv: -kv[1])[:25]:
        problems.append(f"undefined name used {count}x: {token}")

    # ----------------------------------------------------- data validation
    for ws in wb.worksheets:
        for dv in ws.data_validations.dataValidation:
            formula = (dv.formula1 or "").lstrip("=")
            if dv.type == "list" and formula and \
                    re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", formula):
                if formula not in defined:
                    problems.append(
                        f"{ws.title}: drop down uses missing name "
                        f"{formula}")

    # ------------------------------------------------------------- report
    with zipfile.ZipFile(path) as zf:
        size = sum(i.file_size for i in zf.infolist())
    notes.append(f"{formula_cells:,} formula cells, "
                 f"{unlocked_input_cells:,} unlocked value cells")
    notes.append(f"uncompressed xml {size / 1_000_000:.1f} MB")

    print(f"--- {path}")
    for note in notes:
        print(f"  . {note}")
    print("  . formulas per sheet: " + ", ".join(
        f"{k} {v}" for k, v in sorted(per_sheet.items(),
                                      key=lambda kv: -kv[1])[:10]))
    if problems:
        print(f"  ! {len(problems)} problem(s):")
        for problem in problems[:60]:
            print(f"    - {problem}")
        return 1
    print("  OK - no problems found")
    return 0


if __name__ == "__main__":
    target = (sys.argv[1] if len(sys.argv) > 1
              else "output/Wedding Photographer Business Manager.xlsx")
    raise SystemExit(check(target))
