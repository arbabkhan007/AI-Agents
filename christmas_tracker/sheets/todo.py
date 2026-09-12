"""
\u2705 To-Do List - date-aware, so it shouts about the things that are about
to bite you.

Deadlines ship as formulas relative to your event date (``=EventDate-45``),
which means the whole plan re-dates itself when you move the event.
"""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "todo"
LAST_COL = "H"

COLUMNS = [
    ("done", "Done", "tick", None),
    ("task", "Task", "text", None),
    ("category", "Category", "center", None),
    ("deadline", "Deadline", "date", None),
    ("days", "Days left", "calc_num", "primary_2"),
    ("status", "Status (auto)", "calc_c", "primary_2"),
    ("notes", "Notes", "text", None),
]


def build(bk):
    ws = bk.ws(KEY)
    S, th, m = bk.S, bk.th, bk.demo

    bk.widths(KEY)
    bk.paint(KEY, 0, 0, C.last_row(KEY) + 28, ci(LAST_COL), S.canvas)
    bk.title_block(
        KEY,
        "  \u2705  Christmas To-Do List",
        "  Pre-loaded with the classic holiday checklist \u2014 every "
        "deadline is calculated from your event date.",
        LAST_COL)

    chips = [
        ("B", "C", "\U0001F4CB Tasks: ", "todo_total", "primary"),
        ("D", "D", "\u2705 Done: ", "todo_done", "ok"),
        ("E", "E", "\U0001F534 Overdue: ", "todo_overdue", "bad"),
        ("F", "F", "\U0001F7E0 Due soon: ", None, "warn"),
        ("G", LAST_COL, "\U0001F4CA Progress: ", None, "gold"),
    ]
    for c1, c2, label, kpi_key, color in chips:
        fmt = S.pill(th.soft(color), getattr(th, color), size=10.5, bold=True,
                     align="left")
        if c1 == c2:
            ws.write(r(C.ROW_STATS), ci(c1), "", fmt)
        else:
            ws.merge_range(r(C.ROW_STATS), ci(c1), r(C.ROW_STATS), ci(c2),
                           "", fmt)
        if kpi_key:
            formula = '="%s"&%s' % (label, bk.kpi(kpi_key))
            cached = "%s%d" % (label, m.agg[kpi_key])
        elif label.startswith("\U0001F7E0"):
            formula = _due_soon_formula(bk, label)
            cached = "%s%d" % (label, m.agg["todo_soon"])
        else:
            formula = ('="%s"&REPT("\u2588",ROUND(MIN(1,IFERROR(%s/%s,0))*14,0))'
                       '&REPT("\u2591",14-ROUND(MIN(1,IFERROR(%s/%s,0))*14,0))'
                       '&"  "&TEXT(IFERROR(%s/%s,0),"0%%")'
                       % ((label, bk.kpi("todo_done"), bk.kpi("todo_total"))
                          + (bk.kpi("todo_done"), bk.kpi("todo_total"))
                          + (bk.kpi("todo_done"), bk.kpi("todo_total"))))
            pct = (m.agg["todo_done"] / float(m.agg["todo_total"])
                   if m.agg["todo_total"] else 0)
            filled = int(round(min(1.0, pct) * 14))
            cached = "%s%s  %d%%" % (label, "\u2588" * filled +
                                     "\u2591" * (14 - filled),
                                     round(pct * 100))
        ws.write_formula(r(C.ROW_STATS), ci(c1), formula, fmt, cached)
        bk.stats["formulas"] += 1

    K.table_frame(bk, KEY, COLUMNS, height=20)
    for i in range(K.n_rows(KEY)):
        rownum = C.ROW_FIRST + i
        values = _formulas(bk, rownum)
        if i < len(m.todos):
            t = m.todos[i]
            values.update({"done": t["done"], "task": t["task"],
                           "category": t["category"],
                           "deadline": "=EventDate-%d" % t["offset"]
                           if t["offset"] >= 0 else
                           "=EventDate+%d" % abs(t["offset"]),
                           "notes": ""})
        K.write_row(bk, KEY, COLUMNS, rownum, values, _cached(m, i))

    ws.autofilter(r(C.ROW_HEADER), ci("B"), r(C.last_row(KEY)), ci(LAST_COL))
    ws.freeze_panes(r(C.ROW_FIRST), 0)

    K.list_dv(bk, KEY, "category", "todo_categories", title="Category")
    K.tick_dv(bk, KEY, ["done"], message="Tick \u2713 when it is done \u2014 "
                                         "the row greys out and the status "
                                         "turns green.")
    K.date_dv(bk, KEY, ["deadline"],
              message="Type a date, or a formula like =EventDate-14 so it "
                      "moves with your event date.")

    n = C.ROW_FIRST
    done = bk.col(KEY, "done")
    status = bk.col(KEY, "status")
    K.tick_cf(bk, KEY, ["done"])
    for text, (bg, fg) in (("\U0001F7E2 Complete", (th.ok_soft, th.ok)),
                           ("\U0001F534 OVERDUE", (th.bad_soft, th.bad)),
                           ("\U0001F7E0 Due soon", (th.warn_soft, th.warn)),
                           ("\U0001F535 Upcoming", (th.info_soft, th.info))):
        bk.cond(KEY, n, ci(status), C.last_row(KEY), ci(status), {
            "type": "formula",
            "criteria": '=$%s%d="%s"' % (status, n, text),
            "format": S.cf(bg=bg, fg=fg, bold=True)})
    K.deadline_cf(bk, KEY, "deadline", "done")
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula", "criteria": '=$%s%d="%s"' % (done, n, C.TICK),
        "format": S.cf(bg=th.ok_soft, fg=th.muted, strike=True)})
    bk.cond(KEY, n, ci("B"), C.last_row(KEY), ci(LAST_COL), {
        "type": "formula",
        "criteria": '=AND($%s%d<>"%s",$%s%d<>"",$%s%d<TODAY())'
                   % (done, n, C.TICK, bk.col(KEY, "deadline"), n,
                      bk.col(KEY, "deadline"), n),
        "format": S.cf(bg=th.bad_soft, fg=th.bad)})

    total_row = C.last_row(KEY) + 2
    fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                       bg_color=th.primary, align="center", valign="vcenter",
                       border=1, border_color=th.primary))
    K.totals_row(bk, KEY, total_row, {}, label="  CHECKLIST",
                 label_span=("B", "B"), last_col=LAST_COL)
    ws.merge_range(r(total_row), ci("C"), r(total_row), ci(LAST_COL), "", fmt)
    ws.write_formula(
        r(total_row), ci("C"),
        '="\u2705 "&%s&" of "&%s&" tasks done   \u2022   \U0001F534 "&%s'
        '&" overdue   \u2022   \U0001F7E0 "&%s&" due in the next "'
        '&DueSoonDays&" days"'
        % (bk.kpi("todo_done"), bk.kpi("todo_total"), bk.kpi("todo_overdue"),
           _due_soon_ref(bk)), fmt,
        "\u2705 %d of %d tasks done   \u2022   \U0001F534 %d overdue   "
        "\u2022   \U0001F7E0 %d due in the next %d days"
        % (m.agg["todo_done"], m.agg["todo_total"], m.agg["todo_overdue"],
           m.agg["todo_soon"], m.settings["duesoon"]))
    bk.stats["formulas"] += 1

    row = total_row + 2
    row = K.note_block(
        bk, KEY, row, "B", LAST_COL,
        ["\u2022  Deadlines are formulas like ``=EventDate-45`` so the whole "
         "plan re-dates itself when you change the event date in "
         "\u2699\uFE0F Setup. Want a fixed date? Just type over it.",
         "\u2022  Status is automatic: \U0001F7E2 Complete, \U0001F534 "
         "OVERDUE, \U0001F7E0 Due soon (inside your Setup window) or "
         "\U0001F535 Upcoming.",
         "\u2022  Overdue and due-soon tasks also appear on the dashboard's "
         "\u201CWhat's left to do\u201D and \u201CUpcoming deadlines\u201D "
         "panels."],
        title="  \U0001F4A1  How this tab works")
    row += 1
    ws.set_row(r(row), 26)
    row = bk.nav_row(KEY, row, first_col=1, span=2,
                     max_col=LAST_COL) + 2
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  %s v%s  \u2022  %s" % (C.PRODUCT, C.VERSION, C.TAGLINE),
                   S.footer)
    bk.page(KEY, LAST_COL, row + 2, landscape=True,
            title_rows=(0, C.ROW_HEADER - 1))
    return ws


def _formulas(bk, n):
    def L(f):
        return bk.col(KEY, f)

    return {
        "days": '=IF(OR($%s%d="",$%s%d="%s"),"",$%s%d-TODAY())'
                % (L("deadline"), n, L("done"), n, C.TICK, L("deadline"), n),
        "status": ('=IF($%s%d="","",IF($%s%d="%s","\U0001F7E2 Complete",'
                   'IF($%s%d="","",IF($%s%d<TODAY(),"\U0001F534 OVERDUE",'
                   'IF($%s%d-TODAY()<=DueSoonDays,"\U0001F7E0 Due soon",'
                   '"\U0001F535 Upcoming")))))'
                   % (L("task"), n, L("done"), n, C.TICK, L("deadline"), n,
                      L("deadline"), n, L("deadline"), n)),
    }


def _due_soon_formula(bk, label):
    done = bk.rng(KEY, "done")
    dl = bk.rng(KEY, "deadline")
    return ('="%s"&SUMPRODUCT((%s<>"%s")*(%s<>"")*(%s>=TODAY())*'
            '(%s-TODAY()<=DueSoonDays))' % (label, done, C.TICK, dl, dl, dl))


def _due_soon_ref(bk):
    done = bk.rng(KEY, "done")
    dl = bk.rng(KEY, "deadline")
    return ('SUMPRODUCT((%s<>"%s")*(%s<>"")*(%s>=TODAY())*'
            '(%s-TODAY()<=DueSoonDays))' % (done, C.TICK, dl, dl, dl))


def _cached(m, i):
    from datetime import date
    today = date.today()
    if i >= len(m.todos):
        return {"days": "", "status": ""}
    t = m.todos[i]
    dl = t["deadline"]
    if t["done"] == C.TICK:
        return {"days": "", "status": "\U0001F7E2 Complete"}
    if not dl:
        return {"days": "", "status": ""}
    days = (dl - today).days
    if days < 0:
        status = "\U0001F534 OVERDUE"
    elif days <= m.settings["duesoon"]:
        status = "\U0001F7E0 Due soon"
    else:
        status = "\U0001F535 Upcoming"
    return {"days": days, "status": status}
