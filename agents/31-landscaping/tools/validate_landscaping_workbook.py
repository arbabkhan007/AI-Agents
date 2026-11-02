"""Static checks on a generated Ultimate Landscaping & Lawn Care Business Manager.

Run it with any Python that has openpyxl installed::

    python tools/validate_landscaping_workbook.py output/landscaping.xlsx

It never opens Excel - it parses the XML and reports anything that would
break for a buyer: unresolved template tokens, formulas pointing at the
wrong sheet, defined names that do not exist, missing sheet protection,
formula cells that are not locked, input cells that are, and - the one
that matters most here - any break in the chain of IDs that holds the
customers, properties, quotes, jobs, contracts, crew, equipment,
materials, invoices and profit figures together.

Six things this product cannot be allowed to get wrong, and all six
are checked below:

* the four IDs connect - Customer, Property, Job and Invoice;
* a quote is priced from lawn size, labour, materials, equipment,
  travel and a margin, not from a number somebody guessed;
* a job is costed twice, estimated and actual, and the gap is shown;
* recurring contracts work out their own next visit date;
* equipment warns on engine hours *and* on elapsed months;
* the route planner is described as manual organisation - never as
  GPS navigation or automatic route optimisation - and nothing in the
  file claims to sync with accounting, payroll or booking software.
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
from landscaping_spreadsheet.build import (                # noqa: E402
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
    "Monthly Reports!D5",                 # the month being reported on
    "Route Planner!C6",                   # the day being printed
    "Route Planner!C7",                   # the crew being printed
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
    # ---- the customer, the hub every other register joins to -----------
    ("Customer CRM", "id", ("text", "CustomerPrefix")),
    ("Customer CRM", "jobs_done", ("sheet", "Job & Work Orders")),
    ("Customer CRM", "lifetime", ("sheet", "Job & Work Orders")),
    ("Customer CRM", "invoiced", ("sheet", "Invoice & Payments")),
    ("Customer CRM", "owing", ("column", "Customer CRM", "invoiced")),
    ("Customer CRM", "profit", ("column", "Customer CRM", "lifetime")),
    ("Customer CRM", "properties", ("sheet", "Property Database")),

    # ---- the property: where the work happens, and what it costs -------
    ("Property Database", "id", ("text", "PropertyPrefix")),
    ("Property Database", "customer_name", ("sheet", "Customer CRM")),
    ("Property Database", "revenue", ("sheet", "Job & Work Orders")),
    ("Property Database", "jobs_done", ("sheet", "Job & Work Orders")),
    ("Property Database", "mowing_minutes", ("text",
                                             "MowMinutesPer1000")),

    # ---- workflow one: quote from size, labour, materials, travel ------
    # This is the headline feature. Every term of the price has to be
    # traceable, or it is just a number somebody typed.
    ("Quote Calculator", "id", ("text", "QuotePrefix")),
    ("Quote Calculator", "area", ("sheet", "Property Database")),
    ("Quote Calculator", "cat_minutes", ("sheet", "Service Catalog")),
    ("Quote Calculator", "est_minutes", ("column", "Quote Calculator",
                                         "cat_minutes")),
    ("Quote Calculator", "site_hours", ("column", "Quote Calculator",
                                        "est_minutes")),
    ("Quote Calculator", "drive_hours", ("sheet",
                                         "Property Database")),
    ("Quote Calculator", "labour_cost", ("text", "LabourRate")),
    ("Quote Calculator", "travel_cost", ("text", "TravelRate")),
    ("Quote Calculator", "overhead_cost", ("text", "OverheadRate")),
    ("Quote Calculator", "materials_used", ("sheet",
                                            "Service Catalog")),
    ("Quote Calculator", "materials_charge", ("text",
                                              "MaterialMarkup")),
    ("Quote Calculator", "total_cost", ("column", "Quote Calculator",
                                        "equipment_cost")),
    ("Quote Calculator", "margin_used", ("text", "TargetMargin")),
    ("Quote Calculator", "calc_price", ("column", "Quote Calculator",
                                        "margin_used")),
    ("Quote Calculator", "price_used", ("column", "Quote Calculator",
                                        "quoted_price")),
    ("Quote Calculator", "annual_value", ("column",
                                          "Quote Calculator",
                                          "visits_year")),

    # ---- workflow two: the job, and what it really cost ----------------
    ("Job & Work Orders", "id", ("text", "JobPrefix")),
    ("Job & Work Orders", "customer_name", ("sheet", "Customer CRM")),
    ("Job & Work Orders", "address", ("sheet", "Property Database")),
    ("Job & Work Orders", "cat_price", ("sheet", "Service Catalog")),
    ("Job & Work Orders", "contract_price", ("sheet",
                                             "Recurring Contracts")),
    ("Job & Work Orders", "charge", ("column", "Job & Work Orders",
                                     "price_quoted")),
    ("Job & Work Orders", "hours_est", ("column", "Job & Work Orders",
                                        "cat_minutes")),
    ("Job & Work Orders", "hours_logged", ("sheet",
                                           "Timesheets & Payroll")),
    ("Job & Work Orders", "labour_cost", ("sheet",
                                          "Timesheets & Payroll")),
    ("Job & Work Orders", "expense_cost", ("sheet",
                                           "Expense Tracker")),
    ("Job & Work Orders", "travel_cost", ("sheet",
                                          "Property Database")),
    ("Job & Work Orders", "cost_est", ("text", "LabourRate")),
    ("Job & Work Orders", "cost_var", ("column", "Job & Work Orders",
                                       "cost_est")),
    ("Job & Work Orders", "hours_var", ("column", "Job & Work Orders",
                                        "hours_est")),
    ("Job & Work Orders", "profit", ("column", "Job & Work Orders",
                                     "cost")),
    ("Job & Work Orders", "invoiced", ("sheet",
                                       "Invoice & Payments")),
    ("Job & Work Orders", "route_match", ("text", "RouteDate")),

    # ---- workflow three: the contract schedules itself -----------------
    ("Recurring Contracts", "id", ("text", "ContractPrefix")),
    ("Recurring Contracts", "visits_year", ("text", "VisitsPerYear")),
    ("Recurring Contracts", "gap_days", ("text", "DaysBetween")),
    ("Recurring Contracts", "visits_done", ("sheet",
                                            "Job & Work Orders")),
    ("Recurring Contracts", "next_num", ("column",
                                         "Recurring Contracts",
                                         "gap_days")),
    ("Recurring Contracts", "booked_next", ("sheet",
                                            "Job & Work Orders")),
    ("Recurring Contracts", "annual_value", ("column",
                                             "Recurring Contracts",
                                             "visit_price")),
    ("Recurring Contracts", "days_to_renew", ("column",
                                              "Recurring Contracts",
                                              "renewal_date")),

    # ---- workflow four: crew hours become job costs --------------------
    ("Crew Database", "id", ("text", "CrewPrefix")),
    ("Crew Database", "hours_total", ("sheet",
                                      "Timesheets & Payroll")),
    ("Crew Database", "revenue", ("sheet", "Timesheets & Payroll")),
    ("Timesheets & Payroll", "rate", ("sheet", "Crew Database")),
    ("Timesheets & Payroll", "overtime_hours", ("text",
                                                "OvertimeAfter")),
    ("Timesheets & Payroll", "cost", ("column",
                                      "Timesheets & Payroll",
                                      "overtime_hours")),
    ("Timesheets & Payroll", "job_value", ("sheet",
                                           "Job & Work Orders")),
    ("Crew Schedule", "name", ("sheet", "Crew Database")),
    ("Crew Schedule", "logged", ("sheet", "Timesheets & Payroll")),

    # ---- workflow five: equipment warns before it breaks ---------------
    ("Equipment Inventory", "id", ("text", "EquipmentPrefix")),
    ("Equipment Inventory", "hours_used", ("column",
                                           "Equipment Inventory",
                                           "last_service_hours")),
    ("Equipment Inventory", "hours_interval", ("text",
                                               "ServiceHours")),
    ("Equipment Inventory", "hours_left", ("column",
                                           "Equipment Inventory",
                                           "hours_interval")),
    ("Equipment Inventory", "days_to_service", ("text", "EDATE")),
    ("Equipment Inventory", "service_due", ("column",
                                            "Equipment Inventory",
                                            "hours_left")),
    ("Equipment Inventory", "service_soon", ("text",
                                             "ServiceWarnHours")),
    ("Equipment Inventory", "maintenance_cost", ("sheet",
                                                 "Expense Tracker")),

    # ---- workflow six: materials and fuel become costs -----------------
    ("Materials Inventory", "id", ("text", "MaterialPrefix")),
    ("Materials Inventory", "purchased", ("sheet", "Expense Tracker")),
    ("Materials Inventory", "used", ("sheet", "Expense Tracker")),
    ("Materials Inventory", "on_hand", ("column",
                                        "Materials Inventory",
                                        "opening")),
    ("Materials Inventory", "is_low", ("column",
                                       "Materials Inventory",
                                       "reorder_at")),
    ("Materials Inventory", "order_value", ("column",
                                            "Materials Inventory",
                                            "reorder_qty")),
    ("Expense Tracker", "job_address", ("sheet", "Job & Work Orders")),
    ("Vehicle & Fuel Tracker", "miles", ("column",
                                         "Vehicle & Fuel Tracker",
                                         "odometer")),
    ("Vehicle & Fuel Tracker", "economy", ("column",
                                           "Vehicle & Fuel Tracker",
                                           "gallons")),

    # ---- workflow seven: invoices, payments and what is owed -----------
    ("Invoice & Payments", "id", ("text", "InvoicePrefix")),
    ("Invoice & Payments", "customer_name", ("sheet", "Customer CRM")),
    ("Invoice & Payments", "job_charge", ("sheet",
                                          "Job & Work Orders")),
    ("Invoice & Payments", "net", ("column", "Invoice & Payments",
                                   "job_charge")),
    ("Invoice & Payments", "term_days", ("text", "TermDays")),
    ("Invoice & Payments", "due_date", ("column",
                                        "Invoice & Payments",
                                        "term_days")),
    ("Invoice & Payments", "outstanding", ("column",
                                           "Invoice & Payments",
                                           "paid")),
    ("Invoice & Payments", "days_late", ("text", "TodayDate")),
    ("Invoice & Payments", "age_band", ("column",
                                        "Invoice & Payments",
                                        "days_late")),

    # ---- workflow eight: feedback and profit ---------------------------
    ("Customer Feedback", "customer_name", ("sheet", "Customer CRM")),
    ("Customer Feedback", "days_open", ("text", "TodayDate")),
    ("Profit Analysis", "revenue", ("sheet", "Job & Work Orders")),
    ("Profit Analysis", "labour", ("sheet", "Timesheets & Payroll")),
    ("Profit Analysis", "materials", ("sheet", "Expense Tracker")),
    ("Profit Analysis", "fuel", ("sheet", "Vehicle & Fuel Tracker")),
    ("Profit Analysis", "profit", ("column", "Profit Analysis",
                                   "total_costs")),
    ("Profit Analysis", "margin_pct", ("column", "Profit Analysis",
                                       "profit")),
    ("Profit Analysis", "profit_hour", ("column", "Profit Analysis",
                                        "hours")),
    ("Service Catalog", "times_sold", ("sheet", "Job & Work Orders")),
    ("Service Catalog", "avg_actual", ("sheet", "Job & Work Orders")),
    ("Service Catalog", "win_rate", ("column", "Service Catalog",
                                     "quoted")),
]

#: named cells that must still hold a live formula - a name pointing
#: at an empty cell means a page quietly stopped working
PAGE_FORMULAS = [
    ("TodayDate", "settings: the live date every alert reads"),
    ("YearStart", "settings: the first day of the reporting year"),
    ("YearEnd", "settings: the last day of the reporting year"),
    ("ThisMonthKey", "settings: the month key the dashboard groups on"),
    ]

#: cells a buyer has to be able to type in
PAGE_INPUTS = [
    ("BusinessName", "settings: the business name"),
    ("OwnerName", "settings: who runs it"),
    ("BusinessPhone", "settings: the number on the printed work order"),
    ("LabourRate", "settings: what an hour of crew time costs you"),
    ("ChargeRate", "settings: what you charge for an hour on site"),
    ("OverheadRate", "settings: overhead carried by every crew hour"),
    ("TargetMargin", "settings: the margin the quote calculator aims at"),
    ("MinMargin", "settings: the margin you refuse to go under"),
    ("MinimumVisit", "settings: the smallest price you will turn out for"),
    ("MaterialMarkup", "settings: the markup on materials"),
    ("TravelRate", "settings: the cost of a mile"),
    ("DriveMinutes", "settings: default drive time between stops"),
    ("MowMinutesPer1000", "settings: minutes to mow a thousand square feet"),
    ("CrewSize", "settings: the default crew size"),
    ("WorkingHours", "settings: hours in a working day"),
    ("OvertimeAfter", "settings: the weekly hours overtime starts after"),
    ("OvertimeRate", "settings: the overtime multiplier"),
    ("QuoteValidDays", "settings: how long a quote stands"),
    ("ChaseQuoteDays", "settings: when an unanswered quote needs chasing"),
    ("UpcomingDays", "settings: how far ahead 'coming up' looks"),
    ("OverdueDays", "settings: the grace period on an invoice"),
    ("RenewalWarnDays", "settings: the contract renewal warning window"),
    ("DormantDays", "settings: when a customer counts as gone quiet"),
    ("FeedbackChaseDays", "settings: when an open complaint is too old"),
    ("ServiceHours", "settings: engine hours between services"),
    ("ServiceMonths", "settings: months between services"),
    ("ServiceWarnHours", "settings: the engine hours warning window"),
    ("ServiceWarnDays", "settings: the service date warning window"),
    ("SeasonStart", "settings: the first month of your season"),
    ("SeasonEnd", "settings: the last month of your season"),
    ("RevenueTarget", "settings: the revenue target for the year"),
    ("JobsTarget", "settings: the visits a week you are aiming at"),
    ("FuelPrice", "settings: the pump price the fuel figures assume"),
    ("TaxRate", "settings: sales tax or VAT"),
    ("TaxOnServices", "settings: whether tax applies at all"),
    ("ReportYear", "settings: the year the annual report covers"),
    ("CustomerPrefix", "settings: the Customer ID prefix"),
    ("PropertyPrefix", "settings: the Property ID prefix"),
    ("JobPrefix", "settings: the Job ID prefix"),
    ("InvoicePrefix", "settings: the Invoice ID prefix"),
    ("ReportMonth", "monthly reports: the month being reported on"),
    ("PrintQuote", "route planner: the quote being printed"),
    ("PrintInvoice", "route planner: the invoice being printed"),
    ("RouteDate", "route planner: the day being printed"),
    ("RouteCrew", "route planner: the crew being printed"),
]

#: every drop down on the workbook reads one of these - a missing one
#: means a blank list and a column nobody can fill in
REQUIRED_LIST_NAMES = [
    "CustomerList", "PropertyList", "ServiceList", "CrewIDList",
    "CrewNameList", "MaterialIDList", "EquipmentIDList", "JobIDList",
    "QuoteIDList", "ContractIDList", "InvoiceIDList", "YesNoList",
    "CustomerTypeList", "CustomerStatusList", "LeadSourceList",
    "PropertyTypeList", "PropertyStatusList", "TerrainList",
    "AccessList", "ServiceCategoryList", "ServiceStatusList",
    "PricingUnitList", "FrequencyList", "QuoteStatusList",
    "JobStatusList", "PriorityList", "WeatherList",
    "ContractStatusList", "CrewRoleList", "CrewStatusList",
    "EmploymentTypeList", "AbsenceList", "TaskTypeList",
    "EquipmentCategoryList", "EquipmentStatusList",
    "EquipmentConditionList", "MaintenanceTypeList", "VehicleList",
    "VehicleCostList", "MaterialCategoryList", "MaterialUnitList",
    "MaterialStatusList", "StockMoveList", "InvoiceStatusList",
    "PaymentMethodList", "PaymentTermsList", "ExpenseCategoryList",
    "TaxCategoryList", "FeedbackSourceList", "FeedbackTypeList",
    "FeedbackStatusList", "FeedbackCauseList", "SeasonList",
    "WeekdayList", "MonthNameList", "MonthKeyList", "CurrencyList",
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
    from landscaping_spreadsheet.build import REGISTER_MODULES
    from landscaping_spreadsheet.config import Config
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


def check_id_joins(wb, problems: list, notes: list) -> None:
    """Four IDs hold the workbook together. Verify them both ways.

    Customer ID, Property ID, Job ID and Invoice ID are the join keys.
    Each one is minted by exactly one register, as a formula nobody can
    overtype, and every other register that refers to it picks it from
    a drop-down.  Break that and the twenty-three tabs stop being a
    business manager and become twenty-three unrelated lists.
    """
    specs = _specs()
    hubs = [
        ("Customer CRM", "id", "CustomerPrefix", "customer",
         "CustomerList"),
        ("Property Database", "id", "PropertyPrefix", "property",
         "PropertyList"),
        ("Job & Work Orders", "id", "JobPrefix", "job", "JobIDList"),
        ("Invoice & Payments", "id", "InvoicePrefix", "invoice",
         "InvoiceIDList"),
    ]
    joined_total = 0
    for home, key, prefix, ref_key, list_name in hubs:
        spec = specs.get(home)
        if spec is None:
            problems.append(f"the {home} register has gone")
            continue
        column = next((c for c in spec.columns if c.key == key), None)
        if column is None or not column.formula:
            problems.append(
                f"{home}.{key} is not a formula - the ID has to be "
                f"minted by the workbook, not typed, or two rows end "
                f"up sharing one key")
            continue
        if prefix not in column.formula:
            problems.append(
                f"{home}.{key} no longer reads {prefix}, so the ID "
                f"prefix on Settings & Lists does nothing")
        # every register that refers to this hub must do it by ID
        joined = []
        for name, other in specs.items():
            if name == home:
                continue
            col = next((c for c in other.columns if c.key == ref_key),
                       None)
            if col is None or col.formula:
                continue                 # derived, not chosen
            joined.append(name)
            source = (col.validate or {}).get("source")
            if not (isinstance(source, str)
                    and source.lstrip("=") == list_name):
                problems.append(
                    f"{name}.{ref_key} is not a {list_name} "
                    f"drop-down, so a buyer can mistype the ID and "
                    f"silently disconnect the row from "
                    f"{home}")
        joined_total += len(joined)
        if ref_key == "customer" and len(joined) < 5:
            problems.append(
                f"only {len(joined)} registers join to the customer "
                f"by ID; the design calls for at least 5")
        if ref_key == "job" and len(joined) < 4:
            problems.append(
                f"only {len(joined)} registers join to the job by ID; "
                f"the design calls for at least 4")
    notes.append(f"ID joins: {joined_total} register columns joined "
                 f"through Customer, Property, Job and Invoice IDs")


def check_decisions(wb, problems: list, notes: list) -> None:
    """The decisions this product is not allowed to get wrong.

    Every one of them is a way a landscaping spreadsheet quietly starts
    lying to its owner, and every one is checked against the real
    formulas rather than against a promise in the documentation.
    """
    specs = _specs()
    held = []

    def column(sheet, key):
        spec = specs.get(sheet)
        if spec is None:
            problems.append(f"the {sheet} register has gone")
            return None
        col = next((c for c in spec.columns if c.key == key), None)
        if col is None:
            problems.append(f"{sheet}.{key} has gone")
        return col

    def needs(sheet, key, terms, why):
        col = column(sheet, key)
        if col is None or not col.formula:
            problems.append(f"{sheet}.{key} is no longer a formula "
                            f"- {why}")
            return False
        missing = [t for t in terms if t not in col.formula]
        if missing:
            problems.append(
                f"{sheet}.{key} no longer uses {', '.join(missing)} "
                f"- {why}")
            return False
        return True

    # 1. the quote is built from the job, not guessed
    ok = needs("Quote Calculator", "total_cost",
               ("{labour_cost}", "{materials_used}",
                "{equipment_cost}", "{travel_cost}",
                "{overhead_cost}"),
               "a quote has to cost labour, materials, equipment, "
               "travel and overhead or it is a guess")
    ok &= needs("Quote Calculator", "calc_price",
                ("{margin_used}", "MinimumVisit"),
                "the price has to come off the cost at the margin you "
                "asked for, and never go under your minimum visit")
    ok &= needs("Quote Calculator", "area",
                ("Property Database.lawn_area",),
                "lawn size has to come from the property record")
    if ok:
        held.append("quote priced from size, labour, materials, "
                    "equipment, travel and margin")

    # 2. estimated against actual, on every job
    ok = needs("Job & Work Orders", "hours_actual",
               ("{hours_logged}", "{hours_typed}"),
               "actual hours must prefer the crew's timesheets")
    ok &= needs("Job & Work Orders", "cost",
                ("{labour_cost}", "{expense_cost}"),
                "the real cost of a job is its timesheets and its "
                "expenses")
    ok &= needs("Job & Work Orders", "cost_var",
                ("{cost_est}", "{cost}"),
                "estimated against actual is the whole point of "
                "job-level profitability")
    ok &= needs("Job & Work Orders", "hours_var",
                ("{hours_est}", "{hours_actual}"),
                "estimated hours against actual hours")
    if ok:
        held.append("job profit compares estimated with actual")

    # 3. the recurring schedule works itself out
    ok = needs("Recurring Contracts", "next_num",
               ("{gap_days}", "{last_num}"),
               "the next visit date has to follow from the frequency "
               "and the last visit")
    ok &= needs("Recurring Contracts", "is_due",
                ("UpcomingDays", "{booked_next}"),
                "a contract is only due if nothing is booked yet")
    if ok:
        held.append("recurring contracts schedule themselves")

    # 4. equipment warns on hours AND on months
    ok = needs("Equipment Inventory", "service_due",
               ("{hours_left}", "{days_to_service}"),
               "a service falls due on engine hours or on the "
               "calendar, whichever comes first")
    ok &= needs("Equipment Inventory", "service_soon",
                ("ServiceWarnHours", "ServiceWarnDays"),
                "the warning window has to work both ways too")
    if ok:
        held.append("equipment warns on hours and on months")

    # 5. stock and cost are derived, never typed over
    materials = specs.get("Materials Inventory")
    if materials is not None:
        for key in ("purchased", "used", "on_hand"):
            col = next((c for c in materials.columns if c.key == key),
                       None)
            if col is None or not col.formula:
                problems.append(
                    f"Materials Inventory.{key} is typed, not derived "
                    f"- material stock has to come from the purchases "
                    f"and usage logged in the Expense Tracker")
                break
        else:
            held.append("material stock derived from expenses")
    jobs = specs.get("Job & Work Orders")
    if jobs is not None:
        for key in ("labour_cost", "expense_cost", "cost", "profit",
                    "margin_pct", "charge"):
            col = next((c for c in jobs.columns if c.key == key), None)
            if col is None or not col.formula:
                problems.append(
                    f"Job & Work Orders.{key} is typed, not derived - "
                    f"job money has to follow from the timesheets, "
                    f"the expenses and the agreed price")
                break
        else:
            held.append("job money derived, not typed")

    # 6. the route planner is a view of the jobs, not a second diary
    route = [c for c in (jobs.columns if jobs else [])
             if c.key in ("route_key", "route_seq", "route_match")]
    if len(route) < 3:
        problems.append(
            "Job & Work Orders has lost its route_key/route_seq/"
            "route_match columns, so the Route Planner would need its "
            "own copy of the day's work")
    elif not all(c.formula for c in route):
        problems.append("the route columns are typed, not derived")
    else:
        match = next(c for c in route if c.key == "route_match")
        if "RouteDate" not in (match.formula or "") or \
                "RouteCrew" not in (match.formula or ""):
            problems.append(
                "Job & Work Orders.route_match no longer reads "
                "RouteDate and RouteCrew, so the Route Planner cannot "
                "pick a day and a crew")
        else:
            held.append("route planner reads the job register")

    notes.append(f"decisions held: {len(held)} of 7 - " +
                 "; ".join(held))


def check_promises(wb, problems: list, notes: list) -> None:
    """Four promises this product makes to the buyer in writing.

    1. The route planner organises stops by hand.  It is not GPS
       navigation and it does not optimise anything, and saying
       otherwise is the single most common lie in this category.
    2. It is a workbook, not an integration: it never syncs with
       accounting, payroll or booking software.
    3. Payroll totals are gross figures for pricing, not a filing.
    4. The tax and accounting figures point at a real accountant.
    """
    banned_route = ("gps navigation", "gps route", "turn-by-turn",
                    "turn by turn", "optimises your route",
                    "optimizes your route", "optimised route",
                    "optimized route", "route optimisation",
                    "route optimization", "best route",
                    "shortest route", "live traffic", "satnav",
                    "sat nav", "automatic routing")
    banned_sync = ("syncs with", "synchronise with", "synchronize with",
                   "live feed", "api connection",
                   "automatically imports", "real-time", "real time "
                   "update", "connects to quickbooks",
                   "connects to xero", "connects to your bank",
                   "two-way sync", "automatic sync", "files your tax",
                   "files your payroll", "runs your payroll")
    banned_magic = ("updates itself", "updates automatically from",
                    "pulls your bookings", "imports your bookings",
                    "downloads your jobs", "knows the weather",
                    "weather feed")
    route_hits = sync_hits = magic_hits = 0
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
                           or "without " in low or "doesn't" in low
                           or "there is no" in low)
                for phrase in banned_route:
                    if phrase in low and not negated:
                        route_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims "
                            f"navigation or route optimisation -> "
                            f"{value[:70]}")
                for phrase in banned_sync:
                    if phrase in low and not negated:
                        sync_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims a "
                            f"live connection to other software -> "
                            f"{value[:70]}")
                for phrase in banned_magic:
                    if phrase in low and not negated:
                        magic_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims "
                            f"the workbook knows something nobody "
                            f"told it -> {value[:70]}")

    wanted = {
        "entered by you": ("you enter", "you type", "typed in",
                           "enter them", "you record", "you give"),
        "no GPS, no optimisation": ("not gps", "no gps",
                                    "not optimise", "not optimize",
                                    "does not optimise",
                                    "does not optimize"),
        "no accounting or payroll sync": ("does not sync",
                                          "not sync with",
                                          "no connection",
                                          "does not connect",
                                          "not connect"),
        "payroll is not a filing": ("not a payroll", "payroll filing",
                                    "whoever runs your payroll",
                                    "not payroll software"),
        "accountant": ("accountant",),
    }
    found = {key: False for key in wanted}
    for title in ("Getting Started", "Settings & Lists",
                  "Route Planner", "Timesheets & Payroll",
                  "Profit Analysis", "Dashboard"):
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
    notes.append(f"product promises: {route_hits} navigation claims, "
                 f"{sync_hits} false sync claims, {magic_hits} "
                 f"self-updating claims, honesty notes "
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
    check_id_joins(wb, problems, notes)
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
              else "output/landscaping.xlsx")
    raise SystemExit(check(target))
