"""Shared formula fragments and chrome helpers for every tab.

All fragments here are Excel 2010 safe: no IFS, no XLOOKUP, no MAXIFS,
no TEXTJOIN, no dynamic arrays.  Conditional aggregation is done with
COUNTIFS / SUMIFS / SUMPRODUCT(MAX(...)) and hidden helper columns.
"""

from __future__ import annotations

from ..config import DISCLAIMER_SHORT

# ---------------------------------------------------------------------------
# Unit conversions.  Every register stores a canonical metric value in a
# hidden column; the unit stamp on the row wins, then the workbook unit.
# KgPerLb / CmPerIn / KmPerMi / Units are defined names on Settings.
# ---------------------------------------------------------------------------


def kg_from(typed: str, stamp: str) -> str:
    return (f'IF({typed}="","",IF({stamp}="lb",{typed}*KgPerLb,'
            f'IF({stamp}="kg",{typed},'
            f'IF(Units="Imperial",{typed}*KgPerLb,{typed}))))')


def cm_from(typed: str, stamp: str) -> str:
    return (f'IF({typed}="","",IF({stamp}="in",{typed}*CmPerIn,'
            f'IF({stamp}="cm",{typed},'
            f'IF(Units="Imperial",{typed}*CmPerIn,{typed}))))')


def km_from(typed: str, stamp: str) -> str:
    return (f'IF({typed}="","",IF({stamp}="mi",{typed}*KmPerMi,'
            f'IF({stamp}="km",{typed},'
            f'IF(Units="Imperial",{typed}*KmPerMi,{typed}))))')


def disp_weight(kg: str) -> str:
    """Canonical kg -> the unit the buyer chose, blank safe."""
    return f'IF({kg}="","",IF(Units="Imperial",{kg}/KgPerLb,{kg}))'


def disp_length(cm: str) -> str:
    return f'IF({cm}="","",IF(Units="Imperial",{cm}/CmPerIn,{cm}))'


def disp_distance(km: str) -> str:
    return f'IF({km}="","",IF(Units="Imperial",{km}/KmPerMi,{km}))'


# ---------------------------------------------------------------------------
# Dates and weeks
# ---------------------------------------------------------------------------

def week_start_of(date_expr: str) -> str:
    """Monday of the week (or Sunday, per Settings) containing the date."""
    return (f'{date_expr}-WEEKDAY({date_expr},'
            f'IF(WeekStart="Sunday",1,2))+1')


def day_of_week(date_expr: str) -> str:
    """1..7 with day 1 = the week start chosen on Settings."""
    return f'WEEKDAY({date_expr},IF(WeekStart="Sunday",1,2))'


def mmss(minutes_expr: str) -> str:
    """92.5 minutes -> '92:30' (min:sec), blank safe, no array maths."""
    m = f'INT({minutes_expr})'
    s = f'ROUND(({minutes_expr}-{m})*60,0)'
    return (f'IF({minutes_expr}="","",IF({minutes_expr}=0,"0:00",'
            f'IF({s}=60,TEXT({m}+1,"0")&":00",'
            f'TEXT({m},"0")&":"&TEXT({s},"00"))))')


def pace_text(min_per: str) -> str:
    """A decimal min/km as mm:ss per unit, blank and zero safe."""
    return (f'IF(OR({min_per}="",{min_per}<=0),"",'
            f'TEXT(INT({min_per}),"0")&":"&'
            f'TEXT(IF(ROUND(({min_per}-INT({min_per}))*60,0)=60,0,'
            f'ROUND(({min_per}-INT({min_per}))*60,0)),"00"))')


# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------

def footer(sheet, cfg, last_col: int, row: int, extra: str = "") -> int:
    """The two lines every tab carries: disclaimer then credit."""
    text = DISCLAIMER_SHORT
    if extra:
        text = f"{extra}  |  {text}"
    sheet.merge(row, 0, last_col, text, sheet.f.chrome("note"))
    sheet.merge(row + 1, 0, last_col,
                f"{cfg.author}  |  {cfg.product_name} v{cfg.version}",
                sheet.f.chrome("note"))
    return row + 2


def empty_state(test: str, message: str) -> str:
    """Honest empty state: a blank file never looks broken."""
    return f'IF({test},"{message}","")'
