"""Small building blocks shared by the register sheets.

Everything a register needs more than once lives here: the
standard columns, the conditional format recipes, the
blank-row guards and the cross sheet lookups.  A register
module should read like a description of its table, not
like a formula library.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import (CAPITAL_CATEGORIES, DIRECT_CATEGORIES,
                      EARNING_STATUSES, HOLDING_STATUSES,
                      OPEN_LEAD_STATUSES, SHOT_STATUSES,
                      WON_LEAD_STATUSES)
from ..layout import HEADER_ROW, Col
from ..writer import cf_text, yes_no

# Everything below assumes the standard geometry: headers on row 4, data from
# row 5 - ROW()-4 therefore gives a 1 based record number.
ROW_OFFSET = HEADER_ROW


# ---------------------------------------------------------------------------
# Standard columns
# ---------------------------------------------------------------------------

def id_col(trigger: str, prefix: str, digits: int = 4, width: float = 11,
           header: str = "ID", note: str = "") -> Col:
    """Auto numbered ID column (blank until the trigger column is filled).

    `prefix` is a formula fragment - either a defined name such as
    ``BookingPrefix`` or a quoted literal such as ``'"BKG-"'``.
    """
    zeros = "0" * digits
    return Col(
        "id", header, width, "id",
        formula=(f'=IF({{{trigger}}}{{r}}="","",'
                 f'{prefix}&TEXT(ROW()-{ROW_OFFSET},"{zeros}"))'),
        note=note or "Generated automatically from the row number. "
                     "Filter the list rather than re-sorting it so the IDs "
                     "keep matching your other tabs.")


def month_col(date_key: str, key: str = "month", header: str = "Month",
              width: float = 10, hidden: bool = True) -> Col:
    """`yyyy-mm` text column - the key every monthly roll-up groups on."""
    return Col(key, header, width, "text",
               formula=(f'=IF({{{date_key}}}{{r}}="","",'
                        f'TEXT({{{date_key}}}{{r}},"yyyy-mm"))'),
               hidden=hidden,
               note="Automatic. Every monthly report groups on this.")


def year_col(date_key: str, key: str = "year", header: str = "Year",
             width: float = 8) -> Col:
    return Col(key, header, width, "int",
               formula=(f'=IF({{{date_key}}}{{r}}="","",'
                        f'YEAR({{{date_key}}}{{r}}))'),
               hidden=True)


def weekday_col(date_key: str, key: str = "weekday", header: str = "Day",
                width: float = 8, hidden: bool = False) -> Col:
    return Col(key, header, width, "text",
               formula=(f'=IF({{{date_key}}}{{r}}="","",'
                        f'TEXT({{{date_key}}}{{r}},"ddd"))'),
               hidden=hidden)


def week_start_col(date_key: str, key: str = "week_start",
                   header: str = "Week beginning", width: float = 12) -> Col:
    """The Monday of that week - a far safer grouping key than WEEKNUM."""
    return Col(key, header, width, "date",
               formula=(f'=IF({{{date_key}}}{{r}}="","",'
                        f'{{{date_key}}}{{r}}-WEEKDAY({{{date_key}}}{{r}},3))'),
               hidden=True,
               note="The Monday of that week. Weekly totals group on it.")


def date_num_col(date_key: str, key: str, header: str = "",
                 width: float = 10) -> Col:
    """Hidden numeric mirror of a date column that is **never blank**.

    A blank cell inside a `SUMPRODUCT(cond * range)` is fine, but a
    formula column that returns `""` is not: Excel answers `#VALUE!` the
    moment it multiplies a zero by an empty string.  The calendar, the
    double-booking test and the availability strip all multiply date
    columns, so each one gets a mirror that returns a real 0 instead.
    """
    return Col(key, header or f"{date_key} (number)", width, "number",
               formula=(f'=IF({{{date_key}}}{{r}}="",0,'
                        f'{{{date_key}}}{{r}}*1)'),
               hidden=True,
               note="Automatic. The calendar and the clash checks read this "
                    "instead of the date column, because a blank date would "
                    "break the arithmetic.")


def seq_num_col(trigger: str, key: str = "seq_num",
                header: str = "Row number") -> Col:
    """Hidden never-blank row counter, so INDEX/MATCH can find a row."""
    return Col(key, header, 9, "int",
               formula=(f'=IF({{{trigger}}}{{r}}="",0,ROW()-{ROW_OFFSET})'),
               hidden=True,
               note="Automatic. The calendar uses this to find which "
                    "booking covers a date.")


# ---------------------------------------------------------------------------
# Conditional formatting sets
# ---------------------------------------------------------------------------

def alert_cf() -> List[Dict[str, Any]]:
    """Traffic light colouring for the 'Action' / 'Check' columns."""
    return [
        cf_text("OK", "good", "begins with"),
        cf_text("Ready", "good"),
        cf_text("Double booked", "bad"),
        cf_text("Clash", "bad"),
        cf_text("Overdue", "bad"),
        cf_text("Late", "bad"),
        cf_text("Missing", "bad"),
        cf_text("Not cleaned", "bad"),
        cf_text("Urgent", "bad"),
        cf_text("Out of stock", "bad"),
        cf_text("Loss", "bad"),
        cf_text("Unpaid", "bad"),
        cf_text("Cancelled", "bad"),
        cf_text("Chase", "warn"),
        cf_text("Check", "warn"),
        cf_text("Action", "warn"),
        cf_text("Order", "warn"),
        cf_text("Low stock", "warn"),
        cf_text("Add", "warn"),
        cf_text("Send", "warn"),
        cf_text("Confirm", "warn"),
        cf_text("Follow up", "warn"),
        cf_text("Schedule", "warn"),
        cf_text("Same day", "warn"),
        cf_text("Tight turn", "warn"),
        cf_text("Due", "warn"),
        cf_text("Today", "info"),
        cf_text("Tomorrow", "info"),
        cf_text("Arriving", "info"),
        cf_text("Leaving", "info"),
        cf_text("Upcoming", "info"),
        cf_text("Staying", "info"),
        cf_text("Blocked", "muted"),
    ]


def status_cf() -> List[Dict[str, Any]]:
    """Colouring for booking, cleaning, payout and maintenance statuses."""
    return [
        cf_text("Active", "good"),
        cf_text("Completed", "good"),
        cf_text("Complete", "good"),
        cf_text("Confirmed", "good"),
        cf_text("Checked in", "good"),
        cf_text("Received", "good"),
        cf_text("Paid in full", "good"),
        cf_text("In stock", "good"),
        cf_text("Ready", "good"),
        cf_text("Cancelled", "bad"),
        cf_text("Out of stock", "bad"),
        cf_text("Disputed", "bad"),
        cf_text("Written off", "bad"),
        cf_text("Do not use", "bad"),
        cf_text("Late", "bad"),
        cf_text("Urgent", "bad"),
        cf_text("Order now", "bad"),
        cf_text("Inquiry", "warn"),
        cf_text("Scheduled", "warn"),
        cf_text("In progress", "warn"),
        cf_text("Part paid", "warn"),
        cf_text("Part received", "warn"),
        cf_text("Awaiting payout", "warn"),
        cf_text("Expected", "warn"),
        cf_text("Reported", "warn"),
        cf_text("Quoted", "warn"),
        cf_text("Waiting", "warn"),
        cf_text("Low", "warn"),
        cf_text("Requested", "warn"),
        cf_text("Trial", "warn"),
        cf_text("Under maintenance", "warn"),
        cf_text("Owner block", "info"),
        cf_text("Maintenance block", "info"),
        cf_text("Not due yet", "muted"),
        cf_text("Not scheduled", "muted"),
        cf_text("Not requested", "muted"),
        cf_text("Not tracked", "muted"),
        cf_text("Inactive", "muted"),
        cf_text("Ended", "muted"),
        cf_text("Skipped", "muted"),
    ]


def priority_cf() -> List[Dict[str, Any]]:
    return [
        cf_text("Urgent", "bold_bad"),
        cf_text("High", "bad"),
        cf_text("Normal", "info"),
        cf_text("Low", "muted"),
        cf_text("When convenient", "muted"),
    ]


def bar_cf(color: str = "#3F97A0") -> List[Dict[str, Any]]:
    return [{"type": "data_bar", "bar_color": color}]


def scale_cf() -> List[Dict[str, Any]]:
    return [{"type": "3_color_scale", "min_color": "#F9DAD6",
             "mid_color": "#FCEBD4", "max_color": "#D8EDDD"}]


def money_cf() -> List[Dict[str, Any]]:
    return [{"type": "cell", "criteria": ">", "value": 0, "fmt": "bold_good"}]


def loss_cf() -> List[Dict[str, Any]]:
    """Red when a profit column goes negative."""
    return [{"type": "cell", "criteria": "<", "value": 0, "fmt": "bold_bad"},
            {"type": "cell", "criteria": ">", "value": 0, "fmt": "good"}]


def owing_cf() -> List[Dict[str, Any]]:
    """Amber on anything still owed, blue on an overpayment."""
    return [{"type": "cell", "criteria": ">", "value": 0.004, "fmt": "warn"},
            {"type": "cell", "criteria": "<", "value": -0.004, "fmt": "info"}]


def flag_yes_no_cf() -> List[Dict[str, Any]]:
    return [cf_text("No", "warn"), cf_text("Yes", "good")]


def flag_no_bad_cf() -> List[Dict[str, Any]]:
    """For the ones where 'No' is a real problem, not a preference."""
    return [cf_text("No", "bad"), cf_text("Yes", "good")]


def target_cf(target_name: str) -> List[Dict[str, Any]]:
    """Green at or above a named target, amber below it."""
    return [
        {"type": "cell", "criteria": ">=", "value": f"={target_name}",
         "fmt": "good"},
        {"type": "cell", "criteria": "<", "value": f"={target_name}",
         "fmt": "warn"},
    ]


def rating_cf() -> List[Dict[str, Any]]:
    return [
        {"type": "cell", "criteria": ">=", "value": 4.8, "fmt": "bold_good"},
        {"type": "cell", "criteria": ">=", "value": 4.5, "fmt": "good"},
        {"type": "cell", "criteria": ">=", "value": 4.0, "fmt": "warn"},
        {"type": "cell", "criteria": "<", "value": 4.0, "fmt": "bad"},
    ]


def yesno(note: str = "") -> Dict[str, Any]:
    return yes_no(note)


def score_validation(maximum: int = 5) -> Dict[str, Any]:
    return {
        "validate": "decimal",
        "criteria": "between",
        "minimum": 1,
        "maximum": maximum,
        "error_title": f"Rating 1-{maximum}",
        "error_message": f"Enter a rating from 1 (poor) to {maximum} "
                         f"(excellent). Half stars are fine.",
    }


def blank(trigger: str, body: str) -> str:
    """`=IF(trigger="","",body)` with the standard row placeholders."""
    return f'=IF({{{trigger}}}{{r}}="","",{body})'


def zero(trigger: str, body: str) -> str:
    """`=IF(trigger="",0,body)` - for columns that must never return "".

    Any column a `SUMPRODUCT`, `MAX(cond*range)` or calendar lookup reads
    has to be numeric on every single row, including the ones that do not
    apply, or Excel multiplies a number by an empty string and answers
    `#VALUE!`.
    """
    return f'=IF({{{trigger}}}{{r}}="",0,{body})'


# ---------------------------------------------------------------------------
# Cross sheet lookups.  Every one is blank-row safe and says what to do
# when the ID does not exist, because a typo in an ID is the single most
# common thing that goes wrong in a workbook like this.
# ---------------------------------------------------------------------------

def lookup(sheet: str, target: str, key_col: str, key: str,
           missing: str = "") -> str:
    """Generic `INDEX/MATCH` against any register, blank row safe."""
    return (f'=IF({{{key}}}{{r}}="","",IFERROR(INDEX([[{sheet}.'
            f'{target}]],MATCH({{{key}}}{{r}},'
            f'[[{sheet}.{key_col}]],0)),"{missing}"))')


def lookup_num(sheet: str, target: str, key_col: str, key: str) -> str:
    """Numeric `INDEX/MATCH` - 0 when the ID is missing or the cell empty.

    `INDEX` on an empty cell returns 0, not "", so numeric lookups are
    coerced with `*1` inside the `IFERROR` rather than compared to "".
    """
    return (f'=IF({{{key}}}{{r}}="","",IFERROR(INDEX([[{sheet}.'
            f'{target}]],MATCH({{{key}}}{{r}},'
            f'[[{sheet}.{key_col}]],0))*1,0))')


def lookup_num_zero(sheet: str, target: str, key_col: str, key: str) -> str:
    """As :func:`lookup_num`, but returns 0 rather than "" on a blank row."""
    return (f'=IF({{{key}}}{{r}}="",0,IFERROR(INDEX([[{sheet}.'
            f'{target}]],MATCH({{{key}}}{{r}},'
            f'[[{sheet}.{key_col}]],0))*1,0))')


def lookup_client(target: str, key: str = "client",
                  missing: str = "Not in Client CRM") -> str:
    return lookup("Client CRM", target, "id", key, missing)


def lookup_client_num(target: str, key: str = "client") -> str:
    return lookup_num("Client CRM", target, "id", key)


def lookup_booking(target: str, key: str = "booking",
                   missing: str = "Not in Wedding Bookings") -> str:
    return lookup("Wedding Bookings", target, "id", key, missing)


def lookup_booking_num(target: str, key: str = "booking") -> str:
    return lookup_num("Wedding Bookings", target, "id", key)


def lookup_booking_num_zero(target: str, key: str = "booking") -> str:
    return lookup_num_zero("Wedding Bookings", target, "id", key)


def booking_client_col(key: str = "booking") -> Col:
    """Hidden column carrying the Client ID behind a Booking ID.

    The Client CRM rolls payments, galleries and reviews up per couple.
    Storing the client against each row keeps those `COUNTIFS` one
    dimensional instead of a lookup inside a lookup inside a criteria
    argument, which Excel will not do.
    """
    return Col("client", "Client ID", 11, "id",
               formula=(f'=IF({{{key}}}{{r}}="","",'
                        f'IFERROR(INDEX([[Wedding Bookings.client]],'
                        f'MATCH({{{key}}}{{r}},'
                        f'[[Wedding Bookings.id]],0))&"",""))'),
               hidden=True)


def lookup_package(target: str, key: str = "package",
                   missing: str = "Not in Packages & Pricing") -> str:
    return lookup("Packages & Pricing", target, "name", key, missing)


def lookup_package_num(target: str, key: str = "package") -> str:
    return lookup_num("Packages & Pricing", target, "name", key)


def lookup_staff(target: str, key: str = "photographer",
                 missing: str = "Not in Photographer & Staff") -> str:
    return lookup("Photographer & Staff", target, "id", key, missing)


def lookup_staff_num(target: str, key: str = "photographer") -> str:
    return lookup_num("Photographer & Staff", target, "id", key)


def lookup_lead(target: str, key: str = "lead",
                missing: str = "Not in Lead Tracker") -> str:
    return lookup("Lead Tracker", target, "id", key, missing)


def lookup_equipment(target: str, key: str = "equipment",
                     missing: str = "Not in Equipment Inventory") -> str:
    return lookup("Equipment Inventory", target, "id", key, missing)


# ---------------------------------------------------------------------------
# Shared formula fragments
# ---------------------------------------------------------------------------

def in_list(cell: str, values: List[str]) -> str:
    """`TRUE` when `cell` matches any of `values`.

    `OR()` evaluates every argument whatever happens, which is how a
    perfectly good formula ends up returning `#VALUE!`, so membership is
    tested by adding the comparisons instead.
    """
    tests = "+".join(f'({cell}="{v}")' for v in values)
    return f"({tests}>0)"


def is_holding(cell: str) -> str:
    """The booking still occupies the date in the calendar."""
    return in_list(cell, HOLDING_STATUSES)


def is_earning(cell: str) -> str:
    """The booking counts towards revenue."""
    return in_list(cell, EARNING_STATUSES)


def is_shot(cell: str) -> str:
    """The wedding day has happened, so editing and delivery apply."""
    return in_list(cell, SHOT_STATUSES)


def is_open_lead(cell: str) -> str:
    """A lead that is still live and still worth chasing."""
    return in_list(cell, OPEN_LEAD_STATUSES)


def is_won_lead(cell: str) -> str:
    return in_list(cell, WON_LEAD_STATUSES)


def is_capital(cell: str) -> str:
    """A capital purchase rather than a running cost."""
    return in_list(cell, CAPITAL_CATEGORIES)


def is_direct_cost(cell: str) -> str:
    """A cost that belongs to one wedding rather than to the business."""
    return in_list(cell, DIRECT_CATEGORIES)


def rank_desc(key: str, guard: str = '{name}{r}=""',
              header: str = "Rank", width: float = 9,
              note: str = "") -> Col:
    """Hidden dense rank, 1 = the biggest value in `key`.

    Ties are broken by row order, so the ranks come out 1, 2, 3 ... with
    no gaps and no duplicates.  Pages then read the nth row with an
    ordinary `MATCH(n, rank, 0)` - no array formula, so nothing in the
    workbook needs Ctrl+Shift+Enter.
    """
    return Col(f"{key}_rank", header, width, "int",
               formula=(f'=IF({guard},"",COUNTIFS({{{key}_first}}:'
                        f'{{{key}_last}},">"&{{{key}}}{{r}})+'
                        f'COUNTIFS({{{key}_first}}:{{{key}}}{{r}},'
                        f'{{{key}}}{{r}}))'),
               hidden=True, note=note or f"1 = the largest {key}.")


def rank_asc(key: str, guard: str = '{name}{r}=""',
             header: str = "Rank", width: float = 9,
             note: str = "") -> Col:
    """Hidden dense rank, 1 = the smallest value in `key`."""
    return Col(f"{key}_rank", header, width, "int",
               formula=(f'=IF({guard},"",COUNTIFS({{{key}_first}}:'
                        f'{{{key}_last}},"<"&{{{key}}}{{r}})+'
                        f'COUNTIFS({{{key}_first}}:{{{key}}}{{r}},'
                        f'{{{key}}}{{r}}))'),
               hidden=True, note=note or f"1 = the smallest {key}.")


def seq_key(parent: str, trigger: str = "") -> List[Col]:
    """Hidden `1, 2, 3 ...` within a parent, plus a `parent|n` key.

    Printables and per-parent summaries use `MATCH(parent & "|" & n, key, 0)`
    to pull the nth line of one record without an array formula.
    """
    trig = trigger or parent
    return [
        Col("seq", "Line", 6, "int",
            formula=blank(
                trig,
                f'COUNTIFS({{{parent}_first}}:{{{parent}}}{{r}},'
                f'{{{parent}}}{{r}})'),
            hidden=True),
        Col("key", "Key", 14, "text",
            formula=blank(trig, f'{{{parent}}}{{r}}&"|"&{{seq}}{{r}}'),
            hidden=True),
    ]


# ---------------------------------------------------------------------------
# Money rules used in more than one place
# ---------------------------------------------------------------------------

def package_value(column: str, package_cell: str) -> str:
    """A figure from the editable package table on Packages & Pricing.

    An unknown package name is worth zero rather than breaking the row,
    because a photographer who types a new package should get a number
    they can correct, not an error across twenty columns.
    """
    return (f'IFERROR(INDEX({column},MATCH({package_cell},'
            f'PackageNameList,0))*1,0)')


def package_text(column: str, package_cell: str) -> str:
    """As :func:`package_value` but for an inclusion written in words."""
    return (f'IFERROR(INDEX({column},MATCH({package_cell},'
            f'PackageNameList,0))&"","")')


def days_until(date_cell: str) -> str:
    """Whole days from today to a date - negative once it has passed."""
    return f'({date_cell}-TodayDate)'


def countdown_band(days_cell: str) -> str:
    """Turn a day count into the band the dashboard groups on."""
    return (f'IF({days_cell}<0,"Past",'
            f'IF({days_cell}<=7,"This week",'
            f'IF({days_cell}<=30,"Next 30 days",'
            f'IF({days_cell}<=90,"1-3 months",'
            f'IF({days_cell}<=180,"3-6 months",'
            f'IF({days_cell}<=365,"6-12 months","Over a year"))))))')


def hours_between(start: str, end: str) -> str:
    """Hours between two time cells, tolerating a finish after midnight."""
    return (f'IF({start}="",0,IF({end}="",0,'
            f'ROUND((({end}-{start})+({end}<{start}))*24,2)))')


def sales_tax(amount: str) -> str:
    """Sales tax / VAT on a package total.

    Whether photography is taxable at all, and at what rate, is a local
    question, so the rate and the switch both live on Settings and the
    rate ships at zero.
    """
    return (f'IF(TaxOnPackages<>"Yes",0,ROUND({amount}*TaxRate,2))')


def monthly_equivalent(amount: str, frequency_cell: str) -> str:
    """Turn any recurring cost into what it really costs each month.

    A yearly insurance premium and a monthly software subscription are
    not comparable until both are expressed per month, and anybody
    looking at an expense breakdown is asking the per-month question.
    """
    return (f'IF({frequency_cell}="","",'
            f'IFERROR(INDEX(FrequencyPerYear,MATCH({frequency_cell},'
            f'FrequencyList,0))*{amount}/12,0))')


def mileage_cost(miles: str, allowance: str = "") -> str:
    """Mileage charged at the configured rate, past the free allowance."""
    free = allowance or "FreeTravelMiles"
    return f'ROUND(MAX(0,{miles}-{free})*MileageRate,2)'
