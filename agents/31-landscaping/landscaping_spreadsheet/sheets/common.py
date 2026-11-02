"""Small building blocks shared by the register sheets.

Everything a register needs more than once lives here: the
standard columns, the conditional format recipes, the
blank-row guards and the cross sheet lookups.  A register
module should read like a description of its table, not
like a formula library.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import (ACTIVE_CUSTOMER_STATUSES, CATCHUP_JOB_STATUSES,
                      DONE_JOB_STATUSES, JOB_COST_CATEGORIES,
                      LIVE_CONTRACT_STATUSES, LIVE_QUOTE_STATUSES,
                      OPEN_JOB_STATUSES, OWED_INVOICE_STATUSES,
                      PAID_INVOICE_STATUSES, USABLE_EQUIPMENT_STATUSES,
                      WON_QUOTE_STATUSES)
from ..layout import HEADER_ROW, Col
from ..writer import cf_text, list_from, number_check, yes_no

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
        cf_text("Won", "good"),
        cf_text("Clash", "bad"),
        cf_text("Double booked", "bad"),
        cf_text("Overdue", "bad"),
        cf_text("Late", "bad"),
        cf_text("Missing", "bad"),
        cf_text("Urgent", "bad"),
        cf_text("Loss", "bad"),
        cf_text("Unpaid", "bad"),
        cf_text("Unbilled", "bad"),
        cf_text("Under water", "bad"),
        cf_text("Out of service", "bad"),
        cf_text("Out of stock", "bad"),
        cf_text("No licence", "bad"),
        cf_text("Expired", "bad"),
        cf_text("Cancelled", "bad"),
        cf_text("Chase", "warn"),
        cf_text("Check", "warn"),
        cf_text("Action", "warn"),
        cf_text("Add", "warn"),
        cf_text("Send", "warn"),
        cf_text("Invoice", "warn"),
        cf_text("Order", "warn"),
        cf_text("Reorder", "warn"),
        cf_text("Low stock", "warn"),
        cf_text("Service", "warn"),
        cf_text("Renew", "warn"),
        cf_text("Follow up", "warn"),
        cf_text("Schedule", "warn"),
        cf_text("Reschedule", "warn"),
        cf_text("Catch up", "warn"),
        cf_text("Confirm", "warn"),
        cf_text("Thin margin", "warn"),
        cf_text("Over hours", "warn"),
        cf_text("Due", "warn"),
        cf_text("Today", "info"),
        cf_text("Tomorrow", "info"),
        cf_text("This week", "info"),
        cf_text("Upcoming", "info"),
        cf_text("Quoted", "info"),
        cf_text("Dormant", "muted"),
        cf_text("Paused", "muted"),
    ]


def status_cf() -> List[Dict[str, Any]]:
    """Colouring for booking, cleaning, payout and maintenance statuses."""
    return [
        cf_text("Active", "good"),
        cf_text("Completed", "good"),
        cf_text("Complete", "good"),
        cf_text("Accepted", "good"),
        cf_text("Paid", "good"),
        cf_text("In service", "good"),
        cf_text("In stock", "good"),
        cf_text("Resolved", "good"),
        cf_text("Compliment", "good"),
        cf_text("Ready", "good"),
        cf_text("Cancelled", "bad"),
        cf_text("Declined", "bad"),
        cf_text("Lost", "bad"),
        cf_text("Overdue", "bad"),
        cf_text("Disputed", "bad"),
        cf_text("Written off", "bad"),
        cf_text("Out of service", "bad"),
        cf_text("Out of stock", "bad"),
        cf_text("Broken", "bad"),
        cf_text("Complaint", "bad"),
        cf_text("Damage claim", "bad"),
        cf_text("Expired", "bad"),
        cf_text("Scheduled", "warn"),
        cf_text("Dispatched", "warn"),
        cf_text("In progress", "warn"),
        cf_text("Needs revisit", "warn"),
        cf_text("Rained off", "warn"),
        cf_text("Part paid", "warn"),
        cf_text("Sent", "warn"),
        cf_text("Followed up", "warn"),
        cf_text("Due renewal", "warn"),
        cf_text("Needs service", "warn"),
        cf_text("In repair", "warn"),
        cf_text("Worn", "warn"),
        cf_text("Low", "warn"),
        cf_text("Quality issue", "warn"),
        cf_text("Lead", "info"),
        cf_text("Draft", "info"),
        cf_text("Seasonal", "info"),
        cf_text("Spare", "info"),
        cf_text("Paused", "muted"),
        cf_text("Dormant", "muted"),
        cf_text("Skipped", "muted"),
        cf_text("On hold", "muted"),
        cf_text("Retired", "muted"),
        cf_text("Left", "muted"),
        cf_text("Inactive", "muted"),
    ]


def priority_cf() -> List[Dict[str, Any]]:
    return [
        cf_text("1 - Urgent", "bold_bad"),
        cf_text("2 - High", "bad"),
        cf_text("3 - Normal", "info"),
        cf_text("4 - Low", "muted"),
        cf_text("5 - When convenient", "muted"),
    ]


def bar_cf(color: str = "#40916C") -> List[Dict[str, Any]]:
    return [{"type": "data_bar", "bar_color": color}]


def scale_cf() -> List[Dict[str, Any]]:
    return [{"type": "3_color_scale", "min_color": "#F9DAD6",
             "mid_color": "#FCEBD4", "max_color": "#D8F3DC"}]


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
                         "(excellent). Half stars are fine.",
    }


def pick(name: str, note: str = "") -> Dict[str, Any]:
    """Drop-down fed by a defined name, with an optional hint bubble."""
    opts = dict(list_from(name))
    if note:
        opts["input_message"] = note
    return opts


def amount(minimum: float = 0, maximum: float = 1000000,
           note: str = "", decimal: bool = True) -> Dict[str, Any]:
    """Numeric entry check, with an optional hint bubble."""
    opts = dict(number_check(minimum, maximum, decimal))
    if note:
        opts["input_message"] = note
    return opts


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


# ---------------------------------------------------------------------------
# Cross sheet lookups - the four join keys
# ---------------------------------------------------------------------------
# A Customer ID owns Property IDs. A Property ID owns Jobs. A Job owns
# its labour, its materials and its line on an invoice. Every one of
# those IDs is a drop-down somewhere, never a typed string, because a
# mistyped ID is a row that silently stops being part of the business.

def lookup_customer(target: str, key: str = "customer",
                    missing: str = "Not in Customer CRM") -> str:
    """A field from the customer record behind a Customer ID."""
    return lookup("Customer CRM", target, "id", key, missing)


def lookup_customer_num(target: str, key: str = "customer") -> str:
    return lookup_num("Customer CRM", target, "id", key)


def lookup_property(target: str, key: str = "property",
                    missing: str = "Not in Property Database") -> str:
    """A field from the property record behind a Property ID."""
    return lookup("Property Database", target, "id", key, missing)


def lookup_property_num(target: str, key: str = "property") -> str:
    return lookup_num("Property Database", target, "id", key)


def lookup_property_num_zero(target: str, key: str = "property") -> str:
    return lookup_num_zero("Property Database", target, "id", key)


def lookup_service(target: str, key: str = "service",
                   missing: str = "Not in Service Catalog") -> str:
    """A field from the service record behind a service name."""
    return lookup("Service Catalog", target, "name", key, missing)


def lookup_service_num(target: str, key: str = "service") -> str:
    return lookup_num("Service Catalog", target, "name", key)


def lookup_service_num_zero(target: str, key: str = "service") -> str:
    return lookup_num_zero("Service Catalog", target, "name", key)


def lookup_job(target: str, key: str = "job",
               missing: str = "Not in Job & Work Orders") -> str:
    """A field from the job record behind a Job ID."""
    return lookup("Job & Work Orders", target, "id", key, missing)


def lookup_job_num(target: str, key: str = "job") -> str:
    return lookup_num("Job & Work Orders", target, "id", key)


def lookup_crew(target: str, key: str = "employee",
                missing: str = "Not in Crew Database") -> str:
    """A field from the employee record behind an Employee ID."""
    return lookup("Crew Database", target, "id", key, missing)


def lookup_crew_num(target: str, key: str = "employee") -> str:
    return lookup_num("Crew Database", target, "id", key)


def lookup_contract(target: str, key: str = "contract",
                    missing: str = "") -> str:
    return lookup("Recurring Contracts", target, "id", key, missing)


def lookup_invoice_num(target: str, key: str = "invoice") -> str:
    return lookup_num("Invoice & Payments", target, "id", key)


# ---------------------------------------------------------------------------
# The standard "who and where" columns
# ---------------------------------------------------------------------------

def customer_col(key: str = "customer", header: str = "Customer",
                 width: float = 11, note: str = "") -> Col:
    """A Customer ID chosen from the live list, never typed."""
    return Col(key, header, width, "id",
               validate=pick(
                   "CustomerList",
                   "Pick the Customer ID. Add the customer on the "
                   "Customer CRM tab first if they are not listed."),
               note=note or "Pick from the list. A typed ID disconnects "
                            "this row from the customer.")


def property_col(key: str = "property", header: str = "Property",
                 width: float = 11, note: str = "") -> Col:
    return Col(key, header, width, "id",
               validate=pick(
                   "PropertyList",
                   "Pick the Property ID. Add it on the Property "
                   "Database tab first if it is not listed."),
               note=note or "Pick from the list. One customer can own "
                            "several properties.")


def service_col(key: str = "service", header: str = "Service",
                width: float = 24, note: str = "") -> Col:
    return Col(key, header, width, "text",
               validate=pick(
                   "ServiceList",
                   "Pick the service. Add it to the Service Catalog "
                   "tab first if it is not listed."),
               note=note or "Drives the default price and the time "
                            "estimate.")


def customer_name_col(key: str = "customer", width: float = 22) -> Col:
    return Col("customer_name", "Customer name", width, "text",
               formula=lookup_customer("name", key),
               note="Automatic. If it says 'Not in Customer CRM' the ID "
                    "is wrong.")


def property_address_col(key: str = "property", width: float = 30) -> Col:
    return Col("address", "Address", width, "text",
               formula=lookup_property("address", key),
               note="Automatic, from the Property Database.")


# ---------------------------------------------------------------------------
# Status set tests - what a status MEANS, defined once
# ---------------------------------------------------------------------------

def in_list(cell: str, values) -> str:
    """`(c="a")+(c="b")>0` - membership without OR().

    OR() evaluates every argument, so a blank cell in an argument that
    an earlier test should have ruled out still reaches the comparison.
    Adding booleans avoids it and is shorter in the formula bar.
    """
    terms = "+".join(f'({cell}="{value}")' for value in values)
    return f"({terms}>0)"


def is_open_job(cell: str) -> str:
    """A job that still has to happen."""
    return in_list(cell, OPEN_JOB_STATUSES)


def is_done_job(cell: str) -> str:
    """A job that was done - the only kind that earns anything."""
    return in_list(cell, DONE_JOB_STATUSES)


def is_catchup_job(cell: str) -> str:
    """Rained off or needing a revisit: work you still owe."""
    return in_list(cell, CATCHUP_JOB_STATUSES)


def is_won_quote(cell: str) -> str:
    return in_list(cell, WON_QUOTE_STATUSES)


def is_live_quote(cell: str) -> str:
    """Out with the customer and not yet answered."""
    return in_list(cell, LIVE_QUOTE_STATUSES)


def is_owed_invoice(cell: str) -> str:
    """Money that is still yours and not yet in the bank."""
    return in_list(cell, OWED_INVOICE_STATUSES)


def is_paid_invoice(cell: str) -> str:
    return in_list(cell, PAID_INVOICE_STATUSES)


def is_live_contract(cell: str) -> str:
    return in_list(cell, LIVE_CONTRACT_STATUSES)


def is_active_customer(cell: str) -> str:
    return in_list(cell, ACTIVE_CUSTOMER_STATUSES)


def is_usable_equipment(cell: str) -> str:
    return in_list(cell, USABLE_EQUIPMENT_STATUSES)


def is_job_cost(cell: str) -> str:
    """An expense that belongs to a job, not to the business."""
    return in_list(cell, JOB_COST_CATEGORIES)


# ---------------------------------------------------------------------------
# Roll-ups across the registers
# ---------------------------------------------------------------------------

def sum_by(sheet: str, value_col: str, key_col: str, key_cell: str,
           *extra: str) -> str:
    """`SUMIFS` over one register, keyed on an ID.

    `extra` arrives in pairs - a column key and a criterion - because a
    SUMIFS criterion is always TWO arguments and writing it as one is
    the fastest way to a #VALUE! nobody can find.
    """
    parts = [f"[[{sheet}.{value_col}]]", f"[[{sheet}.{key_col}]]", key_cell]
    for index in range(0, len(extra), 2):
        parts.append(f"[[{sheet}.{extra[index]}]]")
        parts.append(extra[index + 1])
    return f"SUMIFS({','.join(parts)})"


def count_by(sheet: str, key_col: str, key_cell: str, *extra: str) -> str:
    parts = [f"[[{sheet}.{key_col}]]", key_cell]
    for index in range(0, len(extra), 2):
        parts.append(f"[[{sheet}.{extra[index]}]]")
        parts.append(extra[index + 1])
    return f"COUNTIFS({','.join(parts)})"


def jobs_done(key_col: str, key_cell: str) -> str:
    """Completed visits against a customer, property or service."""
    return count_by("Job & Work Orders", key_col, key_cell, "is_done", "1")


def revenue_from_jobs(key_col: str, key_cell: str) -> str:
    """What completed work was worth, before tax."""
    return sum_by("Job & Work Orders", "charge", key_col, key_cell,
                  "is_done", "1")


def labour_hours(job_cell: str) -> str:
    """Hours actually booked to a job on the timesheets."""
    return sum_by("Timesheets & Payroll", "hours", "job", job_cell)


def labour_cost(job_cell: str) -> str:
    """What those hours cost, at each person's own rate."""
    return sum_by("Timesheets & Payroll", "cost", "job", job_cell)


def material_cost(job_cell: str) -> str:
    """Materials booked out to a job, at cost."""
    return sum_by("Expense Tracker", "amount", "job", job_cell,
                  "is_job_cost", "1")


def invoiced_amount(job_cell: str) -> str:
    return sum_by("Invoice & Payments", "total", "job", job_cell)


def paid_amount(invoice_cell: str) -> str:
    return sum_by("Invoice & Payments", "paid", "id", invoice_cell)


# ---------------------------------------------------------------------------
# The money
# ---------------------------------------------------------------------------

def quote_price(area_cell: str, service_cell: str) -> str:
    """The catalogue price for a service at a given lawn area.

    Everything in the Service Catalog is priced per unit, and the unit
    varies - per visit, per hour, per 1,000 sq ft, per linear foot. The
    catalogue carries the rate and the unit; this works out which
    multiplier applies so one formula covers all thirty services.
    """
    rate = f'IFERROR(INDEX([[Service Catalog.rate]],MATCH({service_cell},[[Service Catalog.name]],0))*1,0)'
    unit = f'IFERROR(INDEX([[Service Catalog.unit]],MATCH({service_cell},[[Service Catalog.name]],0))&"","")'
    return (f'IF({service_cell}="",0,'
            f'ROUND({rate}*'
            f'IF({unit}="Per 1,000 sq ft",{area_cell}/1000,'
            f'IF({unit}="Per sq ft",{area_cell},'
            f'IF({unit}="Per 100 sq ft",{area_cell}/100,1)))'
            ',2))')


def service_minutes(area_cell: str, service_cell: str) -> str:
    """How long the catalogue says this service takes on this lawn."""
    mins = f'IFERROR(INDEX([[Service Catalog.minutes]],MATCH({service_cell},[[Service Catalog.name]],0))*1,0)'
    unit = f'IFERROR(INDEX([[Service Catalog.unit]],MATCH({service_cell},[[Service Catalog.name]],0))&"","")'
    return (f'IF({service_cell}="",0,'
            f'ROUND({mins}*'
            f'IF({unit}="Per 1,000 sq ft",{area_cell}/1000,'
            f'IF({unit}="Per sq ft",{area_cell},'
            f'IF({unit}="Per 100 sq ft",{area_cell}/100,1)))'
            ',0))')


def travel_cost(miles_cell: str) -> str:
    """What getting there costs the job."""
    return f'ROUND({miles_cell}*TravelRate,2)'


def overhead_cost(hours_cell: str) -> str:
    """The yard, the insurance and the admin, per crew hour.

    Leaving this out is how a job that looks profitable turns out not
    to be: a three-hour visit carries three hours of the business
    whether or not anybody thought about it.
    """
    return f'ROUND({hours_cell}*OverheadRate,2)'


def service_tax(amount: str) -> str:
    """Sales tax or VAT, only if the business is registered for it."""
    return f'IF(TaxOnServices<>"Yes",0,ROUND({amount}*TaxRate,2))'


def overtime_split(hours_cell: str) -> str:
    """Hours over the weekly threshold, which cost more."""
    return f'MAX(0,{hours_cell}-OvertimeAfter)'


def margin(part: str, whole: str) -> str:
    """A percentage that is blank rather than wrong when there is no base."""
    return f'IF({whole}<=0,"",ROUND({part}/{whole},4))'


def visits_per_year(frequency_cell: str) -> str:
    """Turn 'Fortnightly' into 26 - the parallel list does the work."""
    return ('IFERROR(INDEX(VisitsPerYear,'
            f'MATCH({frequency_cell},FrequencyList,0))*1,0)')


def days_between_visits(frequency_cell: str) -> str:
    return ('IFERROR(INDEX(DaysBetween,'
            f'MATCH({frequency_cell},FrequencyList,0))*1,0)')


def term_days(terms_cell: str) -> str:
    return f'IFERROR(INDEX(TermDays,MATCH({terms_cell},PaymentTermsList,0)),0)'


def season_of(date_cell: str) -> str:
    """Which season a date falls in, for the seasonal roll-ups."""
    return (f'IF({date_cell}="","",'
            f'IF(MONTH({date_cell})<=2,"Winter",'
            f'IF(MONTH({date_cell})<=5,"Spring",'
            f'IF(MONTH({date_cell})<=8,"Summer",'
            f'IF(MONTH({date_cell})<=11,"Autumn / Fall","Winter")))))')


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def alert_chain(trigger: str, tests, default: str = "OK") -> str:
    """Nested IFs from `(condition, message)` pairs, most urgent first.

    Nested rather than OR() or IFS(): OR() evaluates every argument
    even after one is already true, and IFS() needs a modern Excel.
    """
    body = f'"{default}"'
    for condition, message in reversed(tests):
        body = f'IF({condition},"{message}",{body})'
    return f'=IF({{{trigger}}}{{r}}="","",{body})'
