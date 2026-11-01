"""Static checks on a generated Wedding Photographer Business Manager.

Run it with any Python that has openpyxl installed::

    python tools/validate_wedding_workbook.py output/wedding.xlsx

It never opens Excel - it parses the XML and reports anything that would
break for a buyer: unresolved template tokens, formulas pointing at the
wrong sheet, defined names that do not exist, missing sheet protection,
formula cells that are not locked, input cells that are, and - the one
that matters most here - any break in the Booking ID chain that holds
the CRM, the payments, the timeline, the shot list, the editing queue
and the gallery together.
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
from wedding_photography_spreadsheet.build import (                # noqa: E402
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


def precedence_slip(formula):
    """`SUMIFS(..)+SUMIFS(..)/COUNTIFS(..)` - the sum is not divided.

    Excel divides before it adds, so a total built by adding two
    SUMIFS together has to be bracketed before it is divided by
    anything.  The file still opens, every bracket balances and the
    calculation engine returns a number - it is simply the wrong
    number, which is the worst kind of bug to ship.
    """
    for argument in _arguments(formula):
        if "/" not in argument:
            continue
        shape = re.sub(r"\$?[A-Z]{1,3}\$?\d+", "#", argument)
        shape = re.sub(r"\d+", "#", shape)
        if shape in PRECEDENCE_OK:
            continue
        if TIME_DIVISOR_RE.search(argument):
            continue
        sums = _top_level(argument, "+-")
        if not sums:
            continue
        if any(divide > sums[0] for divide in _top_level(argument, "/")):
            return argument
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
    "Booking Calendar!C10",       # the month the calendar opens on
    "Client Questionnaire!C10",   # the wedding being printed
    "Monthly & Annual Reports!C10",   # the month being reported on
}

#: Every link below is a formula in row 5 of a register.  Together
#: they are the product: break one and a buyer gets a blank cell
#: instead of an answer, with nothing to tell them why.
#:
#: The Booking ID (WED-nnnn) is the join key.  Nine registers reach
#: back to Wedding Bookings through it and Wedding Bookings reaches
#: forward to six of them, so most of what follows is that one
#: decision being checked in both directions.
CHAIN_CHECKS = [
    # ---- Wedding Bookings: the hub every other tab joins to -------------
    ("Wedding Bookings", "id", ("text", "BookingPrefix")),
    ("Wedding Bookings", "client_name", ("sheet", "Client CRM")),
    ("Wedding Bookings", "package_price", ("sheet", "Packages & Pricing")),
    ("Wedding Bookings", "photographer_name", ("sheet",
                                               "Photographer & Staff")),
    ("Wedding Bookings", "collected", ("sheet", "Payments & Invoices")),
    ("Wedding Bookings", "contract_state", ("sheet",
                                            "Contracts & Documents")),
    ("Wedding Bookings", "travel_used", ("sheet", "Travel & Mileage")),
    ("Wedding Bookings", "editing_cost", ("sheet", "Expense Tracker")),
    ("Wedding Bookings", "subtotal", ("column", "Wedding Bookings",
                                      "package_price")),
    ("Wedding Bookings", "total_value", ("column", "Wedding Bookings",
                                         "subtotal")),
    ("Wedding Bookings", "total_cost", ("column", "Wedding Bookings",
                                        "direct_costs")),
    ("Wedding Bookings", "profit", ("column", "Wedding Bookings",
                                    "total_cost")),
    ("Wedding Bookings", "margin", ("column", "Wedding Bookings",
                                    "total_value")),
    ("Wedding Bookings", "outstanding", ("column", "Wedding Bookings",
                                         "collected")),
    ("Wedding Bookings", "paid_pct", ("column", "Wedding Bookings",
                                      "collected")),
    ("Wedding Bookings", "team_cost", ("sheet", "Expense Tracker")),
    ("Wedding Bookings", "clash", ("column", "Wedding Bookings",
                                   "wed_num")),
    ("Wedding Bookings", "team_clash", ("column", "Wedding Bookings",
                                        "photographer")),
    ("Wedding Bookings", "alert", ("text", "UpcomingDays")),
    ("Wedding Bookings", "upcoming_rank", ("column", "Wedding Bookings",
                                           "upcoming_key")),
    ("Wedding Bookings", "month_key", ("column", "Wedding Bookings",
                                       "month_seq")),
    ("Wedding Bookings", "timeline_lines", ("sheet", "Wedding Timeline")),
    ("Wedding Bookings", "shot_lines", ("sheet", "Shot List Manager")),
    # ---- enquiry to booking: workflow one -------------------------------
    ("Lead Tracker", "id", ("text", "LeadPrefix")),
    ("Lead Tracker", "booked_value", ("sheet", "Wedding Bookings")),
    ("Lead Tracker", "is_won", ("column", "Lead Tracker", "status")),
    ("Lead Tracker", "overdue", ("text", "TodayDate")),
    ("Lead Tracker", "alert", ("text", "LeadChaseDays")),
    ("Client CRM", "id", ("text", "ClientPrefix")),
    # ---- package to payment: workflow two -------------------------------
    ("Packages & Pricing", "total_price", ("column", "Packages & Pricing",
                                           "base_price")),
    ("Packages & Pricing", "total_cost", ("column", "Packages & Pricing",
                                          "album_cost")),
    ("Packages & Pricing", "margin", ("column", "Packages & Pricing",
                                      "total_price")),
    ("Packages & Pricing", "hourly", ("column", "Packages & Pricing",
                                      "total_hours")),
    ("Packages & Pricing", "sold", ("sheet", "Wedding Bookings")),
    ("Packages & Pricing", "revenue", ("sheet", "Wedding Bookings")),
    ("Packages & Pricing", "conversion", ("column", "Packages & Pricing",
                                          "sold")),
    ("Packages & Pricing", "alert", ("text", "MinimumHourly")),
    ("Payments & Invoices", "id", ("text", "InvoicePrefix")),
    ("Payments & Invoices", "client", ("sheet", "Wedding Bookings")),
    ("Payments & Invoices", "balance", ("column", "Payments & Invoices",
                                        "received")),
    ("Payments & Invoices", "is_late", ("column", "Payments & Invoices",
                                        "days_overdue")),
    ("Payments & Invoices", "alert", ("text", "TodayDate")),
    ("Contracts & Documents", "is_done", ("column",
                                          "Contracts & Documents",
                                          "signed_date")),
    ("Contracts & Documents", "alert", ("text", "DocumentChaseDays")),
    # ---- the wedding day: workflow three --------------------------------
    ("Wedding Timeline", "start", ("column", "Wedding Timeline",
                                   "offset_used")),
    ("Wedding Timeline", "finish", ("column", "Wedding Timeline",
                                    "start")),
    ("Wedding Timeline", "staff_name", ("sheet", "Photographer & Staff")),
    ("Wedding Timeline", "day_key", ("column", "Wedding Timeline",
                                     "day_order")),
    ("Wedding Timeline", "alert", ("text", "TodayDate")),
    ("Shot List Manager", "status", ("column", "Shot List Manager",
                                     "done")),
    ("Shot List Manager", "print_key", ("column", "Shot List Manager",
                                        "print_seq")),
    ("Shot List Manager", "alert", ("text", "TodayDate")),
    # ---- editing to delivery: workflow four -----------------------------
    ("Editing Workflow", "stage", ("column", "Editing Workflow",
                                   "step_backed_up")),
    ("Editing Workflow", "cost", ("column", "Editing Workflow", "hours")),
    ("Editing Workflow", "due", ("text", "DeliveryDays")),
    ("Editing Workflow", "late", ("column", "Editing Workflow", "due")),
    ("Editing Workflow", "days_taken", ("column", "Editing Workflow",
                                        "finished")),
    ("Editing Workflow", "alert", ("text", "TodayDate")),
    ("Gallery & Delivery", "client", ("sheet", "Wedding Bookings")),
    ("Gallery & Delivery", "expires", ("text", "GalleryLiveDays")),
    ("Gallery & Delivery", "after_total", ("column", "Gallery & Delivery",
                                           "print_sales")),
    ("Gallery & Delivery", "alert", ("text", "TodayDate")),
    # ---- money per wedding: workflow five -------------------------------
    ("Profit Analysis", "couple", ("sheet", "Wedding Bookings")),
    ("Profit Analysis", "net_profit", ("column", "Profit Analysis",
                                       "total_cost")),
    ("Profit Analysis", "net_margin", ("column", "Profit Analysis",
                                       "revenue")),
    ("Profit Analysis", "per_hour", ("column", "Profit Analysis",
                                     "net_profit")),
    ("Profit Analysis", "net_profit_rank", ("column", "Profit Analysis",
                                            "net_profit")),
    ("Expense Tracker", "is_overhead", ("column", "Expense Tracker",
                                        "is_direct")),
    ("Expense Tracker", "alert", ("text", "ReceiptThreshold")),
    ("Travel & Mileage", "all_miles", ("column", "Travel & Mileage",
                                       "miles")),
    ("Travel & Mileage", "chargeable", ("column", "Travel & Mileage",
                                        "suggested")),
    ("Travel & Mileage", "total_cost", ("column", "Travel & Mileage",
                                        "mileage")),
    ("Travel & Mileage", "alert", ("text", "TravelLossLimit")),
    # ---- the rest of the business ---------------------------------------
    ("Equipment Inventory", "alert", ("text", "InsureAbove")),
    ("Marketing Calendar", "id", ("text", "MarketingPrefix")),
    ("Marketing Calendar", "alert", ("text", "TodayDate")),
    ("Reviews & Referrals", "client", ("sheet", "Wedding Bookings")),
    ("Reviews & Referrals", "has_review", ("column", "Reviews & Referrals",
                                           "received_on")),
    ("Reviews & Referrals", "alert", ("text", "ReviewChaseDays")),
]

#: named cells that must still hold a live formula - a name pointing
#: at an empty cell means a page quietly stopped working
PAGE_FORMULAS = [
    ("TodayDate", "settings: the live date every alert reads"),
    ("ClientCount", "settings: couples on the books"),
    ("OverheadsThisYear", "settings: overheads totalled from the expense tracker"),
    ("WeddingsThisYear", "settings: weddings counted from the bookings register"),
    ("ReportKey", "reports: the month key the totals group on"),
    ("ReportFrom", "reports: the first day of the month reported on"),
    ("ReportTo", "reports: the last day of the month reported on"),
]

#: cells a buyer has to be able to type in
PAGE_INPUTS = [
    ("StudioName", "settings: the studio name"),
    ("DepositPercent", "settings: the deposit that holds a date"),
    ("FinalPaymentDays", "settings: when the balance falls due"),
    ("ExtraHourRate", "settings: the charge for an extra hour"),
    ("SecondShooterRate", "settings: what a second shooter costs"),
    ("EngagementCost", "settings: what an engagement shoot costs"),
    ("MileageRate", "settings: the mileage rate"),
    ("FreeTravelMiles", "settings: miles included before charging"),
    ("EditingHours", "settings: honest editing hours a wedding"),
    ("EditingRate", "settings: what an hour of editing costs"),
    ("OwnerHourlyValue", "settings: what your own hour is worth"),
    ("DeliveryDays", "settings: the gallery turnaround you promise"),
    ("PreviewDays", "settings: the sneak peek turnaround"),
    ("AlbumDays", "settings: the album turnaround"),
    ("GalleryLiveDays", "settings: how long a gallery stays up"),
    ("TargetMargin", "settings: the margin you are aiming at"),
    ("TargetWeddings", "settings: weddings a year you want"),
    ("TargetAverageValue", "settings: the average booking you want"),
    ("MinimumHourly", "settings: the hourly rate you refuse to go under"),
    ("TaxRate", "settings: sales tax or VAT on packages"),
    ("TaxOnPackages", "settings: whether tax applies at all"),
    ("LeadChaseDays", "settings: when an unanswered enquiry warns"),
    ("UpcomingDays", "settings: the wedding-soon window"),
    ("ReviewChaseDays", "settings: when to chase a review"),
    ("BookingPrefix", "settings: the Booking ID prefix"),
    ("ClientPrefix", "settings: the Client ID prefix"),
    ("CalendarStart", "calendar: the first month shown in the grid"),
    ("CalendarMonths", "calendar: how many months the grid shows"),
    ("QuestionnaireBooking", "questionnaire: the wedding being printed"),
    ("ReportMonth", "reports: the month being reported on"),
    ("ReportYear", "reports: the year being reported on"),
]

#: every drop down on the workbook reads one of these - a missing one
#: means a blank list and a column nobody can fill in
REQUIRED_LIST_NAMES = [
    "BookingList", "ClientList", "PackageList", "StaffList",
    "CampaignList", "YesNoList", "BookingStatusList",
    "ClientStatusList", "LeadStatusList", "LeadSourceList",
    "PriorityList", "TierList", "VenueTypeList", "WeddingStyleList",
    "PhotoStyleList", "DeliveryPreferenceList", "DocumentTypeList",
    "DocumentStatusList", "PaymentStageList", "PaymentMethodList",
    "ShotGroupList", "ShotWhenList", "RequestSourceList",
    "StaffRoleList", "StaffStatusList", "StaffTypeList",
    "GalleryStatusList", "GalleryPlatformList",
    "EquipmentCategoryList", "EquipmentStatusList",
    "EquipmentConditionList", "TravelModeList", "TravelPurposeList",
    "MarketingPlatformList", "ContentTypeList", "ContentStatusList",
    "ExpenseCategoryList", "TaxCategoryList", "FrequencyList",
    "ReviewStatusList", "ReviewPlatformList", "ReviewAskMethodList",
    "CountryList", "TimelineEventList", "TimelineOffsetList",
    "TimelineDurationList", "TimelineRoleList", "MonthNameList",
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
    from wedding_photography_spreadsheet.build import REGISTER_MODULES
    from wedding_photography_spreadsheet.config import Config
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


def check_booking_join(wb, problems: list, notes: list) -> None:
    """The Booking ID is the join key. Verify it in both directions.

    This is the one technical decision the whole product rests on: a
    unique WED-nnnn per wedding, generated once on Wedding Bookings and
    chosen from a drop-down everywhere else.  Without it the payments
    tab, the timeline, the shot list, the editing queue and the gallery
    are five unrelated lists that happen to be in the same file.

    Three things have to hold:

    1. Wedding Bookings really does mint the ID from BookingPrefix;
    2. every register that joins back does so through a column
       validated against BookingList, so a buyer cannot mistype it;
    3. that drop-down resolves to a real defined name.
    """
    specs = _specs()
    hub = specs.get("Wedding Bookings")
    if hub is None:
        problems.append("Wedding Bookings register has gone")
        return
    try:
        column = hub.index("id") + 1
    except Exception:                                  # noqa: B902
        problems.append("Wedding Bookings has no id column - there is "
                        "no join key left")
        return
    formula = wb["Wedding Bookings"].cell(row=5, column=column).value
    if not isinstance(formula, str) or "BookingPrefix" not in formula:
        problems.append("Wedding Bookings.id no longer builds the "
                        "Booking ID from BookingPrefix")

    defined = set(wb.defined_names)
    for ws in wb.worksheets:
        defined |= set(ws.defined_names)
    if "BookingList" not in defined:
        problems.append("BookingList is missing - every Booking ID "
                        "drop-down in the workbook is now empty")

    joined = []
    for name, spec in specs.items():
        if name == "Wedding Bookings":
            continue
        col = next((c for c in spec.columns if c.key == "booking"), None)
        if col is None:
            continue
        joined.append(name)
        source = (col.validate or {}).get("source")
        if not (isinstance(source, str)
                and source.lstrip("=") == "BookingList"):
            problems.append(
                f"{name}.booking is not a BookingList drop-down, so a "
                f"buyer can mistype the Booking ID and silently "
                f"disconnect the row")
    if len(joined) < 9:
        problems.append(f"only {len(joined)} registers join through a "
                        f"Booking ID; the design calls for at least 9")
    notes.append(f"booking ID join: {len(joined)} registers joined to "
                 f"Wedding Bookings through BookingList")


def check_promises(wb, problems: list, notes: list) -> None:
    """Three promises this product makes to the buyer in writing.

    1. It is an organiser, not an integration: it must never claim to
       sync with a booking platform or a calendar service.
    2. It tracks documents; it does not pretend to generate or execute
       legally binding contracts.
    3. The accounting figures carry a disclaimer pointing at a real
       accountant.
    """
    banned_sync = ("syncs with", "synchronise with", "synchronize with",
                   "live feed", "api connection", "automatically imports",
                   "real-time booking", "connects to your calendar")
    banned_legal = ("legally binding", "legally-binding",
                    "e-signature", "esignature", "electronic signature",
                    "court", "solicitor-approved", "lawyer-approved")
    sync_hits = legal_hits = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if not isinstance(value, str) or value.startswith("="):
                    continue
                low = value.lower()
                negated = ("not " in low or "never " in low
                           or "cannot" in low or "does not" in low
                           or "no " in low)
                for phrase in banned_sync:
                    if phrase in low and not negated:
                        sync_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims a "
                            f"live booking connection -> {value[:70]}")
                for phrase in banned_legal:
                    if phrase in low and not negated:
                        legal_hits += 1
                        problems.append(
                            f"{ws.title}!{cell.coordinate}: claims to "
                            f"produce a binding contract -> "
                            f"{value[:70]}")

    wanted = {
        "organiser": ("organis", "organiz"),
        "not a contract tool": ("not a contract", "does not replace",
                                "track documents", "tracks documents",
                                "not legal advice"),
        "accountant": ("accountant",),
    }
    found = {key: False for key in wanted}
    for title in ("Getting Started", "Settings & Lists",
                  "Monthly & Annual Reports", "Contracts & Documents"):
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
                 f"{legal_hits} binding-contract claims, honesty notes "
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
    check_booking_join(wb, problems, notes)
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
