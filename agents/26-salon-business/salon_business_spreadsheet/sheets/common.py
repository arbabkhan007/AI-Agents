"""Shared formula fragments and chrome helpers for every tab.

All fragments here are Excel 2010 safe: no IFS, no XLOOKUP, no MAXIFS,
no TEXTJOIN, no dynamic arrays.  Conditional aggregation is done with
COUNTIFS / SUMIFS / SUMPRODUCT and defined names that point at whole
register columns, so range sizes always agree.
"""

from __future__ import annotations

from ..config import DISCLAIMER_SHORT


# ---------------------------------------------------------------------------
# Money helpers
# ---------------------------------------------------------------------------

def fee_rate(method_expr: str) -> str:
    """Processing fee rate for a payment method (Settings names)."""
    return (f'IF({method_expr}="Card",CardFeeRate,'
            f'IF({method_expr}="Cash",CashFeeRate,'
            f'IF({method_expr}="Bank Transfer",BankFeeRate,OtherFeeRate)))')


def money(expr: str) -> str:
    """Round to 2 dp, blank safe."""
    return f'IF({expr}="","",ROUND({expr},2))'


def n(expr: str) -> str:
    """Numeric coercion that treats blanks and text as zero."""
    return f'N({expr})'


# ---------------------------------------------------------------------------
# Lookups against the defined names
# ---------------------------------------------------------------------------

def svc_lookup(item: str, names: str) -> str:
    return f'IFERROR(INDEX({names},MATCH({item},ServiceNames,0)),"")'


def prod_lookup(item: str, names: str) -> str:
    return f'IFERROR(INDEX({names},MATCH({item},ProductNames,0)),"")'


def either_lookup(item: str, svc_names: str, prod_names: str) -> str:
    """Service table first, product table second, blank if neither."""
    return (f'IF({item}="","",IFERROR('
            f'INDEX({svc_names},MATCH({item},ServiceNames,0)),'
            f'IFERROR(INDEX({prod_names},MATCH({item},ProductNames,0)),"")))')


def taxable_flag(item: str) -> str:
    return (f'IF({either_lookup(item, "ServiceTaxable", "ProductTaxable")}'
            f'="Yes",1,0)')


# ---------------------------------------------------------------------------
# Months (TEXT based, so a P&L column is just a "yyyy-mm" string)
# ---------------------------------------------------------------------------

def month_of(date_expr: str) -> str:
    return f'TEXT({date_expr},"yyyy-mm")'


def ym_mask(date_range: str, ym_expr: str) -> str:
    """1/0 mask: rows of *date_range* that fall inside month *ym_expr*."""
    return (f'(YEAR({date_range})=VALUE(LEFT({ym_expr},4)))'
            f'*(MONTH({date_range})=VALUE(MID({ym_expr},6,2)))')


def cur_ym() -> str:
    return 'TEXT(TODAY(),"yyyy-mm")'


def prev_ym() -> str:
    return 'TEXT(EDATE(TODAY(),-1),"yyyy-mm")'


def week_start_of(date_expr: str) -> str:
    """Monday of the week containing the date."""
    return f'{date_expr}-WEEKDAY({date_expr},2)+1'


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
