"""Small building blocks shared by the register sheets.

Everything a register needs more than once lives here: the
standard columns, the conditional format recipes, the
blank-row guards and the cross sheet lookups.  A register
module should read like a description of its table, not
like a formula library.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..config import (COMMITTED_PO_STATUSES, OPEN_PO_STATUSES,
                      RESERVING_STATUSES, SELLABLE_CONDITIONS,
                      SHIPPED_STATUSES, SOLD_RETAIL_STATUSES)
from ..layout import HEADER_ROW, Col
from ..writer import cf_text, list_from, yes_no

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
# Cross sheet lookups - the five join keys
# ---------------------------------------------------------------------------
# SKU is the join key for everything that moves. Supplier ID, Purchase
# Order ID, Customer ID and Wholesale Order ID join the paperwork. Every
# one of them is a drop-down somewhere, never a typed string.

def lookup_product(target: str, key: str = "sku",
                   missing: str = "Not in Product Database") -> str:
    """A field from the product record behind a SKU."""
    return lookup("Product & SKU Database", target, "sku", key, missing)


def lookup_product_num(target: str, key: str = "sku") -> str:
    return lookup_num("Product & SKU Database", target, "sku", key)


def lookup_product_num_zero(target: str, key: str = "sku") -> str:
    return lookup_num_zero("Product & SKU Database", target, "sku", key)


def lookup_supplier(target: str, key: str = "supplier",
                    missing: str = "Not in Supplier Database") -> str:
    return lookup("Supplier Database", target, "id", key, missing)


def lookup_supplier_num(target: str, key: str = "supplier") -> str:
    return lookup_num("Supplier Database", target, "id", key)


def lookup_customer(target: str, key: str = "customer",
                    missing: str = "Not in Wholesale Customer CRM") -> str:
    return lookup("Wholesale Customer CRM", target, "id", key, missing)


def lookup_customer_num(target: str, key: str = "customer") -> str:
    return lookup_num("Wholesale Customer CRM", target, "id", key)


def lookup_tier(target: str, key: str = "sku") -> str:
    """A price break from the Wholesale Pricing table for this SKU."""
    return lookup_num("Wholesale Pricing", target, "sku", key)


def product_name_col(key: str = "sku") -> Col:
    """Standard read-only product name beside a SKU column.

    Every register that touches stock shows the product name, and not
    one of them lets you type it: a name typed twice is a name spelled
    two ways, and then the SUMIFS stop agreeing with each other.
    """
    return Col("product", "Product name", 26, "text",
               formula=lookup_product("name", key, ""),
               note="Looked up from the Product & SKU Database. "
                    "Change the name there and it changes here.")


def sku_col(key: str = "sku", header: str = "SKU",
            note: str = "") -> Col:
    """The join key, as a drop-down off the live product list."""
    return Col(key, header, 14, "id",
               validate=list_from("SKUList"),
               note=note or ("Pick the SKU from the list. Never type "
                             "one by hand - a SKU that is not in the "
                             "Product Database silently disconnects "
                             "this row from stock, costing and "
                             "profit."))


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


def is_reserving(cell: str) -> str:
    """A wholesale order that has committed stock but not shipped it.

    This is the whole reason reserved stock exists as a separate
    figure. The goods are still on the shelf, so they are still in
    stock - but they are spoken for, so they are not available to sell
    to anybody else.
    """
    return in_list(cell, RESERVING_STATUSES)


def is_shipped(cell: str) -> str:
    """A wholesale order whose stock has physically left the building."""
    return in_list(cell, SHIPPED_STATUSES)


def is_sold_retail(cell: str) -> str:
    """A retail sale that has actually taken stock off the shelf."""
    return in_list(cell, SOLD_RETAIL_STATUSES)


def is_open_po(cell: str) -> str:
    """A purchase order still expected to arrive."""
    return in_list(cell, OPEN_PO_STATUSES)


def is_committed_po(cell: str) -> str:
    """A purchase order the supplier has agreed to - stock on order."""
    return in_list(cell, COMMITTED_PO_STATUSES)


def is_sellable(cell: str) -> str:
    """A returned item that can go back on the shelf."""
    return in_list(cell, SELLABLE_CONDITIONS)


# ---------------------------------------------------------------------------
# Stock arithmetic
# ---------------------------------------------------------------------------
# Rule one of this workbook: stock is never typed, it is always derived.
# The only way to change a stock figure is to add a row somewhere that
# says why it changed. These helpers are the sums that do it.

def sum_by_sku(sheet: str, value_col: str, sku_cell: str,
               *extra: str) -> str:
    """`SUMIFS` of a column on another sheet, matched on SKU.

    `extra` arrives as already-paired criteria range and criteria
    strings - a criterion is always *two* arguments, and collapsing
    them into one is the quickest way to a `#VALUE!`.
    """
    parts = [f"[[{sheet}.{value_col}]]", f"[[{sheet}.sku]]", sku_cell]
    parts.extend(extra)
    return f'SUMIFS({",".join(parts)})'


def count_by_sku(sheet: str, sku_cell: str, *extra: str) -> str:
    parts = [f"[[{sheet}.sku]]", sku_cell]
    parts.extend(extra)
    return f'COUNTIFS({",".join(parts)})'


def received_qty(sku_cell: str) -> str:
    """Units actually booked in against purchase orders.

    Read straight off the purchase order line, which is the single
    place a receipt is recorded. One PO line is one cell, so the same
    delivery physically cannot be counted twice.
    """
    return sum_by_sku("Purchase Orders", "received", sku_cell,
                      "[[Purchase Orders.valid_line]]", "1")


def sold_qty(sku_cell: str) -> str:
    """Units gone: shipped wholesale plus completed retail."""
    wholesale = sum_by_sku("Wholesale Orders", "qty", sku_cell,
                           "[[Wholesale Orders.is_shipped]]", "1")
    retail = sum_by_sku("Retail Sales Tracker", "qty", sku_cell,
                        "[[Retail Sales Tracker.is_sold]]", "1")
    return f"({wholesale}+{retail})"


def reserved_qty(sku_cell: str) -> str:
    """Units promised to a confirmed order that has not shipped."""
    return sum_by_sku("Wholesale Orders", "qty", sku_cell,
                      "[[Wholesale Orders.is_reserved]]", "1")


def returned_sellable_qty(sku_cell: str) -> str:
    """Returned units that went back on the shelf."""
    return sum_by_sku("Returns & Damaged Goods", "qty", sku_cell,
                      "[[Returns & Damaged Goods.restocked]]", "1",
                      "[[Returns & Damaged Goods.customer_return]]", "1")


def damaged_qty(sku_cell: str) -> str:
    """Units written off: returned unsellable, plus damage logged."""
    returns = sum_by_sku("Returns & Damaged Goods", "qty", sku_cell,
                         "[[Returns & Damaged Goods.warehouse_damage]]", "1")
    movements = sum_by_sku("Stock Movement Log", "damaged", sku_cell)
    return f"({returns}+{movements})"


def adjustment_qty(sku_cell: str) -> str:
    """Manual corrections, which only ever come from the movement log."""
    return sum_by_sku("Stock Movement Log", "adjustment", sku_cell)


# ---------------------------------------------------------------------------
# Money rules used in more than one place
# ---------------------------------------------------------------------------

def weighted_average_cost(sku_cell: str, key: str = "sku") -> str:
    """The costing method this workbook uses, in one place.

    Weighted average, not FIFO. Opening stock at its stated cost plus
    everything received at what it actually cost, divided by the units
    those two represent. It is the only method that survives a
    spreadsheet where rows get edited out of order, and mixing it with
    FIFO halfway through is how inventory numbers stop reconciling.
    """
    open_qty = lookup_product_num_zero("opening_qty", key)[1:]
    open_val = lookup_product_num_zero("opening_value", key)[1:]
    recv_qty = received_qty(sku_cell)
    recv_val = sum_by_sku("Purchase Orders", "received_value", sku_cell)
    return (f'IF(({open_qty})+({recv_qty})<=0,'
            f'{lookup_product_num_zero("cost", key)[1:]},'
            f'ROUND((({open_val})+({recv_val}))/'
            f'(({open_qty})+({recv_qty})),4))')


def tier_price(qty_cell: str, sku_cell: str,
               key: str = "sku") -> str:
    """The right price break for this quantity, off Wholesale Pricing.

    Checked from the largest break down, so a 100 unit order gets the
    100+ price rather than stopping at the first band it qualifies for.
    An unknown SKU falls back to the product's own wholesale price
    rather than to zero, because a price of nothing on an order line is
    a mistake that ships.
    """
    def band(n: int) -> str:
        return (f'IFERROR(INDEX([[Wholesale Pricing.tier{n}_qty]],'
                f'MATCH({sku_cell},[[Wholesale Pricing.sku]],0))*1,0)')

    def price(n: int) -> str:
        return (f'IFERROR(INDEX([[Wholesale Pricing.tier{n}_price]],'
                f'MATCH({sku_cell},[[Wholesale Pricing.sku]],0))*1,0)')

    base = (f'IFERROR(INDEX([[Wholesale Pricing.wholesale]],'
            f'MATCH({sku_cell},[[Wholesale Pricing.sku]],0))*1,'
            f'{lookup_product_num_zero("wholesale_price", key)[1:]})')
    out = base
    for n in (1, 2, 3):
        out = (f'IF(AND({band(n)}>0,{qty_cell}>={band(n)},'
               f'{price(n)}>0),{price(n)},{out})')
    return out


def sales_tax(amount: str) -> str:
    """Sales tax / VAT on an order total.

    Whether you charge it at all, and at what rate, is a local
    question - and a wholesale order to a reseller usually is not
    taxed. Both the rate and the switch live on Settings and the rate
    ships at zero.
    """
    return f'IF(TaxOnSales<>"Yes",0,ROUND({amount}*TaxRate,2))'


def monthly_equivalent(amount: str, frequency_cell: str) -> str:
    """Turn any recurring cost into what it really costs each month.

    A yearly software licence and a monthly warehouse rent are not
    comparable until both are expressed per month, and anybody looking
    at an expense breakdown is asking the per-month question.
    """
    return (f'IF({frequency_cell}="","",'
            f'IFERROR(INDEX(FrequencyPerYear,MATCH({frequency_cell},'
            f'FrequencyList,0))*{amount}/12,0))')


def margin(profit_cell: str, revenue_cell: str) -> str:
    """Margin, guarded. Dividing by a blank revenue cell is #DIV/0!."""
    return (f'IF({revenue_cell}<=0,"",'
            f'ROUND({profit_cell}/{revenue_cell},4))')


# ---------------------------------------------------------------------------
# Alert chains
# ---------------------------------------------------------------------------

def alert_chain(trigger: str, tests: List[Any],
                default: str = "OK") -> str:
    """Build the nested IF that drives a sheet's "what needs doing".

    Pass the tests in priority order as (condition, message) pairs and
    get back a balanced formula.  Hand nesting a dozen IFs is how a
    workbook ends up with a stray bracket on row 300 of one sheet, so
    nobody writes these by hand.

    A message may itself be a nested chain: pass a list of pairs as the
    message and it is expanded in place, which is how "this product is
    active, so now ask the stock questions" stays readable.
    """
    def build(pairs: List[Any], fallback: str) -> str:
        if not pairs:
            return fallback
        head = pairs[0]
        cond, msg = head[0], head[1]
        inner_default = head[2] if len(head) > 2 else ""
        rest = build(pairs[1:], fallback)
        if isinstance(msg, list):
            inner = build(msg, f'"{inner_default}"')
            return f'IF({cond},{inner},{rest})'
        return f'IF({cond},"{msg}",{rest})'

    body = build(list(tests), f'"{default}"')
    return f'=IF({{{trigger}}}{{r}}="","",{body})'
