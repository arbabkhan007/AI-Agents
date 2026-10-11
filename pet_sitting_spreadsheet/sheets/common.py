"""Small building blocks shared by the register sheets."""

from __future__ import annotations

from typing import Any, Dict, List

from ..layout import HEADER_ROW, Col
from ..writer import cf_text, yes_no

# Everything below assumes the standard geometry: headers on row 4, data from
# row 5 - ROW()-4 therefore gives a 1 based record number.
ROW_OFFSET = HEADER_ROW


def id_col(trigger: str, prefix: str, digits: int = 4, width: float = 11,
           header: str = "ID", note: str = "") -> Col:
    """Auto numbered ID column (blank until the trigger column is filled)."""
    zeros = "0" * digits
    return Col(
        "id", header, width, "id",
        formula=(f'=IF({{{trigger}}}{{r}}="","",'
                 f'{prefix}&TEXT(ROW()-{ROW_OFFSET},"{zeros}"))'),
        note=note or "Generated automatically from the row number. "
                     "Filter the list rather than re-sorting it so the IDs "
                     "keep matching your other tabs.")


def month_col(date_key: str, key: str = "month", header: str = "Month",
              width: float = 10) -> Col:
    return Col(key, header, width, "text",
               formula=(f'=IF({{{date_key}}}{{r}}="","",'
                        f'TEXT({{{date_key}}}{{r}},"yyyy-mm"))'))


def alert_cf() -> List[Dict[str, Any]]:
    """Traffic light colouring for the 'Alert' / 'Check' columns."""
    return [
        cf_text("OK", "good", "begins with"),
        cf_text("Overdue", "bad"),
        cf_text("Missed", "bad"),
        cf_text("Conflict", "bad"),
        cf_text("Expired", "bad"),
        cf_text("Duplicate", "bad"),
        cf_text("Action", "warn"),
        cf_text("Due", "warn"),
        cf_text("Check", "warn"),
        cf_text("Today", "info"),
        cf_text("Upcoming", "info"),
    ]


def status_cf() -> List[Dict[str, Any]]:
    return [
        cf_text("Completed", "good"),
        cf_text("Confirmed", "good"),
        cf_text("Paid", "good"),
        cf_text("Active", "good"),
        cf_text("Resolved", "good"),
        cf_text("Given", "good"),
        cf_text("Pending", "warn"),
        cf_text("Draft", "warn"),
        cf_text("Enquiry", "warn"),
        cf_text("Partially", "warn"),
        cf_text("In progress", "info"),
        cf_text("Scheduled", "info"),
        cf_text("Sent", "info"),
        cf_text("Cancelled", "bad"),
        cf_text("No show", "bad"),
        cf_text("Missed", "bad"),
        cf_text("Overdue", "bad"),
        cf_text("Inactive", "muted"),
        cf_text("Lost", "bad"),
    ]


def money_cf() -> List[Dict[str, Any]]:
    return [{"type": "cell", "criteria": ">", "value": 0, "fmt": "bold_good"}]


def owing_cf() -> List[Dict[str, Any]]:
    return [{"type": "cell", "criteria": ">", "value": 0.004, "fmt": "bad"}]


def dup_cf() -> List[Dict[str, Any]]:
    return [cf_text("Duplicate", "bad"), cf_text("OK", "good")]


def flag_yes_no_cf() -> List[Dict[str, Any]]:
    return [cf_text("No", "warn"), cf_text("Yes", "good")]


def yesno(note: str = "") -> Dict[str, Any]:
    return yes_no(note)


def rating_validation() -> Dict[str, Any]:
    return {
        "validate": "integer",
        "criteria": "between",
        "minimum": 1,
        "maximum": 5,
        "error_title": "Rating 1-5",
        "error_message": "Enter a whole number from 1 (poor) to 5 "
                         "(excellent).",
    }


def blank(trigger: str, body: str) -> str:
    """`=IF(trigger="","",body)` with the standard row placeholders."""
    return f'=IF({{{trigger}}}{{r}}="","",{body})'
