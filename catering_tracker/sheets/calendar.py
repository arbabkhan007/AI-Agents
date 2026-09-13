"""
The Event Calendar: the month on one screen.

The grid is pure formulas - it reads CalMonth / CalYear from Setup, lays
out a Monday-start month, and marks each day with a count of upcoming
events (\u25cf) and outstanding payment deadlines (\u25b2).  The side
panels list this month's events and dues straight from the hidden _Data
pools, so nothing is ever typed twice.
"""

import calendar as _cal
import datetime

from .. import config as C
from ..book import r
from .common import blank_row

DAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
COL_LETTERS = "BCDEFGH"
WEEKS = 6
LIST_ROWS = 12                     # side-panel slots

UP_FIRST = C.DATA_POOL_FIRST
UP_LAST = C.DATA_POOL_FIRST + C.DATA_POOL_ROWS - 1
DUE_FIRST = C.DATA_DUE_FIRST
DUE_LAST = C.DATA_DUE_FIRST + C.DATA_DUE_ROWS - 1


def build(bk):
    ws = bk.ws("calendar")
    S, th = bk.S, bk.th
    demo = bk.demo
    da = bk.name("data")

    bk.widths("calendar", {"A": 2.2, "B": 15, "C": 15, "D": 15, "E": 15,
                           "F": 15, "G": 15, "H": 15, "I": 2.5, "J": 12,
                           "K": 34, "L": 16, "M": 3, "N": 10})
    for row in range(0, 48):
        ws.set_row(row, 18)

    bk.title_block("calendar", "Event Calendar",
                   "One glance at the month - events, deliveries and "
                   "payment deadlines", "L")
    ws.write_formula(r(C.ROW_TITLE), 1,
                     '=TEXT(DATE(CalYear,CalMonth,1),"mmmm yyyy")',
                     S.sheet_title,
                     "%s %s" % (C.MONTH_NAMES[demo.settings["cal_month"] - 1],
                                demo.settings["cal_year"]))
    bk.stats["formulas"] += 1

    month_start = "DATE(CalYear,CalMonth,1)"
    month_end = "EOMONTH(DATE(CalYear,CalMonth,1),0)"
    ev_m = ("COUNTIFS('%s'!$AA$%d:$AA$%d,\">=\"&%s,'%s'!$AA$%d:$AA$%d,"
            "\"<=\"&%s)" % (da, UP_FIRST, UP_LAST, month_start,
                            da, UP_FIRST, UP_LAST, month_end))
    due_m = ("COUNTIFS('%s'!$AA$%d:$AA$%d,\">=\"&%s,'%s'!$AA$%d:$AA$%d,"
             "\"<=\"&%s)" % (da, DUE_FIRST, DUE_LAST, month_start,
                             da, DUE_FIRST, DUE_LAST, month_end))
    cached_ev, cached_due, cached_next = _month_stats(bk)
    bk.stats_strip("calendar", [
        ('="Events this month: "&%s' % ev_m, "accent",
         "Events this month: %d" % cached_ev),
        ('="Payments due: "&%s' % due_m, "warn",
         "Payments due: %d" % cached_due),
        ('="Next up: "&IF(\'%s\'!$AA$%d="","-",\'%s\'!$AB$%d)'
         % (da, UP_FIRST, da, UP_FIRST), "ok",
         "Next up: %s" % (cached_next or "-")),
    ])

    # day-of-week headers (row 11)
    for d, name in enumerate(DAY_HEADERS):
        fmt = S.thead if d < 5 else S.header(th.accent)
        ws.write(r(11), 1 + d, name, fmt)
    ws.set_row(r(11), 20)

    # ------------------------------------------------------------------
    # the grid: 6 weeks x (date row + chips row), Monday start
    # ------------------------------------------------------------------
    dates, chips = _demo_grid(bk)
    anchor = ("DATE(CalYear,CalMonth,1)-WEEKDAY(DATE(CalYear,CalMonth,1),2)"
              "+1")
    date_fmt = S.f(**S.base(font_size=10, bold=True, font_color=th.primary,
                            bg_color=th.card, align="right", valign="top",
                            border=1, border_color=th.border, num_format="d",
                            indent=1))
    chip_fmt = S.f(**S.base(font_size=9, font_color=th.ink, bg_color=th.alt,
                            align="left", valign="top", text_wrap=True,
                            border=1, border_color=th.border, indent=1))
    for w in range(WEEKS):
        drow = C.CAL_GRID_ROW + 2 * w
        crow = drow + 1
        ws.set_row(r(drow), 16)
        ws.set_row(r(crow), C.CAL_CELL_H - 16)
        for d in range(7):
            n = d + 7 * w
            L = COL_LETTERS[d]
            ws.write_formula(r(drow), 1 + d,
                             '=IF(MONTH(%s+%d)=CalMonth,%s+%d,"")'
                             % (anchor, n, anchor, n),
                             date_fmt, dates[w][d])
            ws.write_formula(r(crow), 1 + d, _chip_formula(bk, L, drow),
                             chip_fmt, chips[w][d])
            bk.stats["formulas"] += 2

    # conditional formats: today, event days, payment-due days
    for w in range(WEEKS):
        drow = C.CAL_GRID_ROW + 2 * w
        crow = drow + 1
        for d in range(7):
            L = COL_LETTERS[d]
            bk.cond("calendar", r(drow), 1 + d, r(drow), 1 + d, {
                "type": "formula", "criteria": '=$%s$%d=TODAY()' % (L, drow),
                "format": S.cf(bg=th.gold_soft, fg=th.gold, bold=True)})
            bk.cond("calendar", r(crow), 1 + d, r(crow), 1 + d, {
                "type": "text", "criteria": "containing",
                "value": "\u25cf",
                "format": S.cf(bg=th.info_soft, fg=th.info, bold=True)})
            bk.cond("calendar", r(crow), 1 + d, r(crow), 1 + d, {
                "type": "text", "criteria": "containing",
                "value": "\u25b2",
                "format": S.cf(bg=th.warn_soft, fg=th.warn, bold=True)})

    # ------------------------------------------------------------------
    # side panels: this month's events + payments due
    # ------------------------------------------------------------------
    ev_list, due_list = _demo_lists(bk)
    ws.merge_range(r(11), 9, r(11), 11, "This month's events",
                   S.header(th.primary))
    _panel(bk, 12, UP_FIRST, UP_LAST, 9, ev_list)
    due_top = 12 + LIST_ROWS + 2
    ws.merge_range(r(due_top - 1), 9, r(due_top - 1), 11, "Payments due",
                   S.header(th.warn))
    _panel(bk, due_top, DUE_FIRST, DUE_LAST, 10, due_list)

    # helper cells (column N - outside the print area)
    ws.write(r(8), 13, "calendar helpers", S.note_plain)
    ws.write_formula(r(9), 13,
                     '=IFERROR(MATCH(DATE(CalYear,CalMonth,1)-0.5,'
                     '\'%s\'!$AA$%d:$AA$%d,1)+1,1)'
                     % (da, UP_FIRST, UP_LAST), S.note_plain,
                     _list_start(bk, 0))
    ws.write_formula(r(10), 13,
                     '=IFERROR(MATCH(DATE(CalYear,CalMonth,1)-0.5,'
                     '\'%s\'!$AA$%d:$AA$%d,1)+1,1)'
                     % (da, DUE_FIRST, DUE_LAST), S.note_plain,
                     _list_start(bk, 1))
    bk.stats["formulas"] += 2

    blank_row(bk, "calendar", due_top + LIST_ROWS + 1, "A", "N", height=10)
    note_row = due_top + LIST_ROWS + 2
    ws.merge_range(r(note_row), 1, r(note_row), 11,
                   "Change the month and year in section 3 of the Setup "
                   "tab - the grid, the marks and both lists follow.   "
                   "\u25cf upcoming events    \u25b2 payment deadlines",
                   S.note)
    ws.set_row(r(note_row), 28)

    bk.nav_row("calendar", note_row + 2, first_col=1, span=2, max_col="L")
    bk.page("calendar", "M", note_row + 4, landscape=True, freeze=None,
            fit=True)


# ----------------------------------------------------------------------
# formulas
# ----------------------------------------------------------------------
def _chip_formula(bk, L, drow):
    da = bk.name("data")
    up = "COUNTIF('%s'!$AA$%d:$AA$%d,$%s$%d)" % (da, UP_FIRST, UP_LAST,
                                                 L, drow)
    due = "COUNTIF('%s'!$AA$%d:$AA$%d,$%s$%d)" % (da, DUE_FIRST, DUE_LAST,
                                                  L, drow)
    return ('=IF($%s$%d="","",TRIM(IF(%s>0,"\u25cf "&%s&IF(%s>1,'
            '" events"," event"),"")&IF(%s>0," \u25b2 "&%s&" due","")))'
            % (L, drow, up, up, up, due, due))


def _panel(bk, top, first, last, helper_row, cached_rows):
    """12 rows pulling date / label / status from a sorted _Data pool."""
    ws = bk.ws("calendar")
    S = bk.S
    da = bk.name("data")
    helper = "$N$%d" % helper_row
    date_rng = "'%s'!$AA$%d:$AA$%d" % (da, first, last)
    label_rng = "'%s'!$AB$%d:$AB$%d" % (da, first, last)
    status_rng = "'%s'!$AC$%d:$AC$%d" % (da, first, last)
    for i in range(LIST_ROWS):
        row = top + i
        idx = "%s+%d" % (helper, i)
        cached = cached_rows[i] if i < len(cached_rows) else ("", "", "")
        ws.write_formula(
            r(row), 9,
            '=IFERROR(IF(INDEX(%s,%s)="","",IF(MONTH(INDEX(%s,%s))'
            '<>CalMonth,"",INDEX(%s,%s))),"")'
            % (date_rng, idx, date_rng, idx, date_rng, idx),
            S.cell("date"), cached[0])
        ws.write_formula(r(row), 10,
                         '=IF($J%d="","",INDEX(%s,%s))'
                         % (row, label_rng, idx), S.cell("text"),
                         cached[1])
        ws.write_formula(r(row), 11,
                         '=IF($J%d="","",INDEX(%s,%s))'
                         % (row, status_rng, idx), S.cell("center"),
                         cached[2])
        bk.stats["formulas"] += 3


# ----------------------------------------------------------------------
# cached (demo) values
# ----------------------------------------------------------------------
def _demo_grid(bk):
    """(dates, chips) 6x7 grids of cached values for the shown month."""
    demo = bk.demo
    dates = [["" for _ in range(7)] for _ in range(WEEKS)]
    chips = [["" for _ in range(7)] for _ in range(WEEKS)]
    if not demo.demo:
        return dates, chips
    y = demo.settings["cal_year"]
    m = demo.settings["cal_month"]
    first_weekday, ndays = _cal.monthrange(y, m)          # Monday = 0
    up = {}
    for d, label, status in demo.agg.get("upcoming", []):
        if d.year == y and d.month == m:
            up[d.day] = up.get(d.day, 0) + 1
    dues = {}
    for d, label, bal in demo.agg.get("dues", []):
        if d.year == y and d.month == m:
            dues[d.day] = dues.get(d.day, 0) + 1
    for day in range(1, ndays + 1):
        slot = first_weekday + day - 1
        w, d = divmod(slot, 7)
        if w >= WEEKS:
            continue
        dates[w][d] = datetime.date(y, m, day)
        parts = []
        if up.get(day):
            parts.append("\u25cf %d event%s" % (up[day],
                                                "s" if up[day] > 1 else ""))
        if dues.get(day):
            parts.append("\u25b2 %d due" % dues[day])
        chips[w][d] = " ".join(parts)
    return dates, chips


def _demo_lists(bk):
    """Cached side-panel rows: [(date, label, status), ...]."""
    demo = bk.demo
    if not demo.demo:
        return [], []
    y = demo.settings["cal_year"]
    m = demo.settings["cal_month"]
    ev = [(d, label, status) for d, label, status in
          demo.agg.get("upcoming", []) if d.year == y and d.month == m]
    dues = [(d, label, status) for d, label, status in
            sorted(demo.agg.get("dues", []), key=lambda x: x[0])
            if d.year == y and d.month == m]
    return ev[:LIST_ROWS], dues[:LIST_ROWS]


def _month_stats(bk):
    demo = bk.demo
    if not demo.demo:
        return 0, 0, ""
    y = demo.settings["cal_year"]
    m = demo.settings["cal_month"]
    ev = sum(1 for d, _, _ in demo.agg.get("upcoming", [])
             if d.year == y and d.month == m)
    dues = sum(1 for d, _, _ in demo.agg.get("dues", [])
               if d.year == y and d.month == m)
    up = demo.agg.get("upcoming", [])
    nxt = up[0][1] if up else ""
    return ev, dues, nxt


def _list_start(bk, which):
    """Cached value for the MATCH helper cells."""
    demo = bk.demo
    if not demo.demo:
        return 1
    y = demo.settings["cal_year"]
    m = demo.settings["cal_month"]
    start = datetime.date(y, m, 1)
    pool = demo.agg.get("upcoming" if which == 0 else "dues", [])
    if which == 1:
        pool = sorted(pool, key=lambda x: x[0])
    k = 1
    for i, entry in enumerate(pool):
        if entry[0] < start:
            k = i + 2
        else:
            break
    return k
