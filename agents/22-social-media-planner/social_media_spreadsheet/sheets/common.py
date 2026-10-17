"""Shared building blocks for sheet modules: register helpers and a small
KPI-tile / summary-table kit used by the dashboard pages."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..layout import SheetSpec, col_letter, rows_to_last

BADGE_FILLS = {
    "good": ("#DDEEDB", "#1F6B2E"),
    "warn": ("#FBEBD0", "#B85C00"),
    "bad": ("#FBE3E3", "#B22222"),
    "info": ("#DCE7F3", "#24527A"),
    "muted": ("#F1F1EF", "#8A8A85"),
}


def sheet_spec(cfg, name: str, title: str, subtitle: str, columns: List,
               rows: int = 100,
               samples: Optional[List[Dict[str, Any]]] = None,
               help_text: str = "", tab_color: str = "#C98F5B",
               freeze_cols: int = 1, freeze_at: Optional[int] = None,
               extra_rows: int = 0) -> SheetSpec:
    return SheetSpec(
        name=name, title=title, subtitle=subtitle, columns=columns,
        rows=rows, samples=samples or [],
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text=help_text, tab_color=tab_color,
        freeze_cols=freeze_cols, freeze_at=freeze_at, extra_rows=extra_rows)


def badge_style(status: str) -> str:
    """Map a status word to a badge fill."""
    s = (status or "").strip().lower()
    good = {"posted", "done", "approved", "active", "published", "in use",
            "ready", "scheduled", "complete", "completed", "winner found"}
    warn = {"in progress", "in review", "running", "draft", "planned",
            "pending", "paused", "idea", "outreach", "prospect", "captured"}
    bad = {"overdue", "rejected", "expired", "blocked", "cancelled",
           "missed", "blocked"}
    if s in good:
        return "good"
    if s in warn:
        return "warn"
    if s in bad:
        return "bad"
    return "info"


def badge(sheet, row0: int, col: int, text: str, style: Optional[str] = None):
    """Paint a status cell like a pill using a plain cell format."""
    fill, color = BADGE_FILLS[style or badge_style(text)]
    fmt = sheet.book.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "align": "center", "valign": "vcenter",
        "bg_color": fill, "font_color": color,
        "border": 1, "border_color": "#E4E4E0", "locked": True})
    sheet.write(row0, col, text, fmt)


# ---------------------------------------------------------------- KPI tiles
def tile(sheet, row: int, col: int, label: str, value: Any,
         note: str = "", fmt_key: str = "int", span: int = 2,
         formula: Optional[str] = None):
    """Static (or formula) KPI tile in the cream brand look. Returns row+3."""
    f = sheet.f
    sheet.merge(row, col, col + span - 1, label, f.chrome("kpi_label"))
    sheet.row_height(row + 1, 30)
    num_fmt = sheet.num_format(fmt_key)
    base = f.chrome("kpi_value", num_format=num_fmt)
    sheet.merge(row + 1, col, row + 1, col + span - 1, "", base)
    if formula is not None:
        sheet.ws.write_formula(row + 1, col, sheet.reg.render(formula), base)
    else:
        sheet.write(row + 1, col, value, base)
    sheet.merge(row + 2, col, col + span - 1, note, f.chrome("kpi_note"))
    return row + 3


def mini_summary(sheet, row: int, title: str, pairs: Sequence[Tuple[str, str]],
                 last_col: int, first_col: int = 0):
    """Small label|value table. Values are engine formula strings."""
    f = sheet.f
    sheet.merge(row, first_col, last_col, title, f.chrome("subsection"))
    row += 1
    for label, formula in pairs:
        sheet.merge(row, first_col, first_col + 1, label, f.chrome("label"))
        sheet.ws.merge_range(row, first_col + 2, row, last_col, "",
                             f.cell("int", "calc"))
        sheet.ws.write_formula(row, first_col + 2,
                               sheet.reg.render(formula),
                               f.cell("int", "calc"))
        row += 1
    return row


def month_pairs(cfg) -> List[Tuple[str, str]]:
    """(Month label, SUMIFS formula) pairs for any month-total table."""
    return [(m, f"=SUMIFS(Budget.Spent, Budget.Month, \"{m}\")")
            for m in cfg.MONTHS]


def money(value) -> str:
    if value in (None, ""):
        return ""
    return f"{value:,.0f}"


def draw_badge_legend(sheet, row: int, col: int) -> int:
    """Tiny colour legend for the status colours."""
    items = [("Ready", "good"), ("Working", "warn"),
             ("Needs action", "bad"), ("Info", "info")]
    for label, style in items:
        badge(sheet, row, col, f"  {label}  ", style)
        col += 2
    return row + 1
