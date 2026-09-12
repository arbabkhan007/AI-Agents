"""Shared worksheet furniture: headers, data rows, totals, validations."""

from datetime import date, datetime

from .. import config as C
from ..book import r, ci, cl


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def first_row():
    return C.ROW_FIRST


def last_row(key):
    return C.last_row(key)


def n_rows(key):
    return C.CAP[key]


def alt(rownum):
    """Zebra stripe: even spreadsheet rows get the tinted background."""
    return (rownum % 2) == 0


# ---------------------------------------------------------------------------
# headers
# ---------------------------------------------------------------------------
def header_row(bk, key, columns, row=None, height=36):
    """``columns`` = list of (field, label, kind, colour_key|None)."""
    ws = bk.ws(key)
    row = C.ROW_HEADER if row is None else row
    for field, label, kind, color in columns:
        col = ci(bk.col(key, field))
        ws.write(r(row), col, label,
                 bk.S.header(getattr(bk.th, color) if color else None))
    ws.set_row(r(row), height)
    return row


def data_rows(bk, key, height=20):
    ws = bk.ws(key)
    for i in range(n_rows(key)):
        ws.set_row(r(C.ROW_FIRST + i), height)


def table_frame(bk, key, columns, height=20):
    """Write the header and pre-format every empty data cell."""
    header_row(bk, key, columns)
    ws = bk.ws(key)
    data_rows(bk, key, height)
    for i in range(n_rows(key)):
        rownum = C.ROW_FIRST + i
        a = alt(rownum)
        for field, label, kind, color in columns:
            col = ci(bk.col(key, field))
            if kind == "idx":
                fmt = bk.S.idx(a)
            elif kind.startswith("calc"):
                fmt = bk.S.cell(kind)
            else:
                fmt = bk.S.cell(kind, a)
            ws.write_blank(r(rownum), col, None, fmt)
    return ws


# ---------------------------------------------------------------------------
# writing a single row of a tracker table
# ---------------------------------------------------------------------------
def write_row(bk, key, columns, rownum, values, cached=None):
    ws = bk.ws(key)
    a = alt(rownum)
    cached = cached or {}
    for field, label, kind, color in columns:
        col = ci(bk.col(key, field))
        value = values.get(field)
        if kind == "idx":
            fmt = bk.S.idx(a)
        elif kind.startswith("calc"):
            fmt = bk.S.cell(kind)
        else:
            fmt = bk.S.cell(kind, a)
        if value is None or value == "":
            ws.write_blank(r(rownum), col, None, fmt)
        elif isinstance(value, str) and value.startswith("="):
            ws.write_formula(r(rownum), col, value, fmt,
                             cached.get(field, 0))
            bk.stats["formulas"] += 1
            bk.stats["cells"] += 1
        elif isinstance(value, (date, datetime)):
            ws.write_datetime(r(rownum), col, value, fmt)
            bk.stats["cells"] += 1
        else:
            ws.write(r(rownum), col, value, fmt)
            bk.stats["cells"] += 1
    return ws


# ---------------------------------------------------------------------------
# validation presets
# ---------------------------------------------------------------------------
def list_dv(bk, key, field, list_key, title=None, message=None, error=None,
            first=None, last=None):
    return bk.validate(key, first or C.ROW_FIRST, ci(bk.col(key, field)),
                       last or C.last_row(key), ci(bk.col(key, field)),
                       "=" + bk.listname(list_key), title=title,
                       message=message, error=error)


def fixed_dv(bk, key, field, name, title=None, message=None, error=None):
    return bk.validate(key, C.ROW_FIRST, ci(bk.col(key, field)),
                       C.last_row(key), ci(bk.col(key, field)), "=" + name,
                       title=title, message=message, error=error)


def tick_dv(bk, key, fields, message="Pick \u2713 from the dropdown to tick "
                                     "it off (leave blank for not yet)."):
    for field in fields:
        bk.validate(key, C.ROW_FIRST, ci(bk.col(key, field)),
                    C.last_row(key), ci(bk.col(key, field)), "=Tick",
                    title="Tick it off", message=message)


def money_dv(bk, key, fields, label="money"):
    for field in fields:
        bk.ws(key).data_validation(
            r(C.ROW_FIRST), ci(bk.col(key, field)),
            r(C.last_row(key)), ci(bk.col(key, field)),
            {"validate": "decimal", "criteria": ">=", "value": 0,
             "ignore_blank": True, "show_error": True,
             "error_title": "Enter %s" % label,
             "error_message": "Please enter a positive number (no currency "
                              "symbol) - the symbol comes from Setup.",
             "error_type": "warning"})
        bk.stats["validations"] += 1


def date_dv(bk, key, fields, message="Type a date, or pick one from the "
                                     "calendar picker."):
    for field in fields:
        bk.ws(key).data_validation(
            r(C.ROW_FIRST), ci(bk.col(key, field)),
            r(C.last_row(key)), ci(bk.col(key, field)),
            {"validate": "date", "criteria": "between",
             "minimum": date(2000, 1, 1), "maximum": date(2100, 12, 31),
             "ignore_blank": True, "show_input": True, "input_title": "Date",
             "input_message": message, "show_error": True,
             "error_title": "That's not a date",
             "error_message": "Enter a date between 2000 and 2100.",
             "error_type": "warning"})
        bk.stats["validations"] += 1


def whole_dv(bk, key, fields, minimum=0, maximum=9999):
    for field in fields:
        bk.ws(key).data_validation(
            r(C.ROW_FIRST), ci(bk.col(key, field)),
            r(C.last_row(key)), ci(bk.col(key, field)),
            {"validate": "whole", "criteria": "between", "minimum": minimum,
             "maximum": maximum, "ignore_blank": True, "show_error": True,
             "error_title": "Whole numbers only",
             "error_message": "Please enter a whole number.",
             "error_type": "warning"})
        bk.stats["validations"] += 1


# ---------------------------------------------------------------------------
# conditional formatting presets
# ---------------------------------------------------------------------------
def tick_cf(bk, key, fields):
    """Green glow on any ticked box."""
    for field in fields:
        col = ci(bk.col(key, field))
        L = bk.col(key, field)
        bk.cond(key, C.ROW_FIRST, col, C.last_row(key), col, {
            "type": "formula", "criteria": '=$%s%d="%s"' % (L, C.ROW_FIRST,
                                                            C.TICK),
            "format": bk.S.cf(bg=bk.th.ok_soft, fg=bk.th.ok, bold=True,
                              size=13, border=bk.th.border)})


def secret_cf(bk, key, field):
    """Secret Mode: make the hiding-spot text invisible (white on white)."""
    col = ci(bk.col(key, field))
    bk.cond(key, C.ROW_FIRST, col, C.last_row(key), col, {
        "type": "formula", "criteria": '=SecretMode="Yes"',
        "format": bk.S.cf(bg=bk.th.card, fg=bk.th.card)})


def status_cf(bk, key, field, mapping, first=None, last=None):
    """Colour a status column.  ``mapping`` = {cell text: (bg, fg)}."""
    L = bk.col(key, field)
    col = ci(L)
    first = first or C.ROW_FIRST
    last = last or C.last_row(key)
    for text, (bg, fg) in mapping.items():
        bk.cond(key, first, col, last, col, {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (L, first, text),
            "format": bk.S.cf(bg=bg, fg=fg, bold=True, border=bk.th.border)})


def deadline_cf(bk, key, date_field, tick_field=None):
    """Overdue = red, due inside the DueSoonDays window = amber."""
    L = bk.col(key, date_field)
    col = ci(L)
    first, last = C.ROW_FIRST, C.last_row(key)
    done = ""
    if tick_field:
        done = '*($%s%d<>"%s")' % (bk.col(key, tick_field), first, C.TICK)
    bk.cond(key, first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d<>"",$%s%d<TODAY()%s)' % (L, first, L, first,
                                                         done),
        "format": bk.S.cf(bg=bk.th.bad_soft, fg=bk.th.bad, bold=True)})
    bk.cond(key, first, col, last, col, {
        "type": "formula",
        "criteria": '=AND($%s%d>=TODAY(),$%s%d-TODAY()<=DueSoonDays%s)'
                   % (L, first, L, first, done),
        "format": bk.S.cf(bg=bk.th.warn_soft, fg=bk.th.warn, bold=True)})


def databar(bk, key, field, color=None, first=None, last=None):
    col = ci(bk.col(key, field))
    bk.cond(key, first or C.ROW_FIRST, col, last or C.last_row(key), col, {
        "type": "data_bar", "bar_color": color or bk.th.primary_2,
        "bar_solid": True, "min_type": "num", "min_value": 0,
        "max_type": "num", "max_value": 1})


# ---------------------------------------------------------------------------
# totals row
# ---------------------------------------------------------------------------
def totals_row(bk, key, row, cells, first_col="B", last_col=None,
               label="TOTALS", label_span=None):
    """``cells`` = {field: (formula, kind, cached)}."""
    ws = bk.ws(key)
    th = bk.th
    lab_fmt = bk.S.f(**bk.S.base(font_size=11, bold=True, font_color=th.white,
                                 bg_color=th.primary, align="right",
                                 valign="vcenter", border=1,
                                 border_color=th.primary, indent=1))
    if label_span:
        c1, c2 = label_span
        if c1 == c2:
            ws.write(r(row), ci(c1), label, lab_fmt)
        else:
            ws.merge_range(r(row), ci(c1), r(row), ci(c2), label, lab_fmt)
    else:
        ws.write(r(row), ci(first_col), label, lab_fmt)
    for field, (formula, kind, cached) in cells.items():
        col = ci(bk.col(key, field))
        fmt = bk.S.f(**bk.S.base(
            font_size=11, bold=True, font_color=th.white, bg_color=th.primary,
            align="right" if kind != "center" else "center",
            valign="vcenter", border=1, border_color=th.primary,
            num_format=kind))
        if isinstance(formula, str) and formula.startswith("="):
            ws.write_formula(r(row), col, formula, fmt, cached or 0)
            bk.stats["formulas"] += 1
        else:
            ws.write(r(row), col, formula, fmt)
    if last_col:
        span_end = ci(label_span[1]) if label_span else ci(first_col)
        for c in range(ci(first_col), ci(last_col) + 1):
            letter = cl(c)
            if letter not in [bk.col(key, f) for f in cells] and \
                    c > span_end:
                ws.write_blank(r(row), c, None, bk.S.f(**bk.S.base(
                    bg_color=th.primary, border=1, border_color=th.primary)))
    ws.set_row(r(row), 24)
    return row


def blank_row(bk, key, row, first_col="A", last_col="N", height=8, fmt=None):
    ws = bk.ws(key)
    fmt = fmt or bk.S.canvas
    ws.set_row(r(row), height)
    for c in range(ci(first_col), ci(last_col) + 1):
        ws.write_blank(r(row), c, None, fmt)
    return row


def note_block(bk, key, row, first_col, last_col, lines, title=None):
    """A bordered, wrapped tip box."""
    ws = bk.ws(key)
    width = sum((C.WIDTHS.get(key, {}) or {}).get(cl(c), 10)
                for c in range(ci(first_col), ci(last_col) + 1))
    if title:
        ws.merge_range(r(row), ci(first_col), r(row), ci(last_col), title,
                       bk.S.section_soft)
        ws.set_row(r(row), 22)
        row += 1
    text = "\n".join(lines)
    from ..styles import wrap_height
    h = wrap_height(text, width, minimum=20)
    ws.merge_range(r(row), ci(first_col), r(row), ci(last_col), text,
                   bk.S.note)
    ws.set_row(r(row), h)
    return row + 1
