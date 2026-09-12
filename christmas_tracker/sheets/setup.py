"""
The ⚙️ Setup tab: event details, money/alert settings and every editable
dropdown list in the workbook.
"""

from datetime import date

from .. import config as C
from ..book import r, ci
from . import common as K

LAST_COL = "J"


def _suggested_date(occasion):
    """Python twin of the suggested-date formula on the Setup tab."""
    today = date.today()
    for name, month, day in C.OCCASIONS:
        if name != occasion:
            continue
        if not month:
            return ""
        year = today.year
        try:
            candidate = date(year, month, day)
        except ValueError:
            return ""
        if candidate < today:
            candidate = date(year + 1, month, day)
        return candidate
    return ""


def build(bk):
    key = "setup"
    ws = bk.ws(key)
    S = bk.S
    th = bk.th
    m = bk.demo

    bk.widths(key, {"A": 2.2, "B": 34, "C": 24, "D": 18, "E": 18, "F": 18,
                    "G": 22, "H": 18, "I": 18, "J": 18})
    bk.paint(key, 0, 0, 84, ci(LAST_COL), S.canvas)

    # ------------------------------------------------------------------
    # title band
    # ------------------------------------------------------------------
    ws.set_row(r(1), 7)
    ws.set_row(r(2), 32)
    ws.set_row(r(3), 18)
    ws.merge_range(r(2), 1, r(2), ci(LAST_COL) - 3,
                   "\u2699\uFE0F  Setup \u2014 make it yours", S.sheet_title)
    ws.merge_range(r(3), 1, r(3), ci(LAST_COL) - 3,
                   "  Change these settings once and every tab, countdown, "
                   "alert and dropdown follows automatically.", S.sheet_sub)
    ws.merge_range(r(3), ci(LAST_COL) - 2, r(3), ci(LAST_COL), "",
                   S.home_link)
    ws.write_url(r(3), ci(LAST_COL) - 2,
                 "internal:%s!A1" % bk.q("dashboard"), S.home_link,
                 "\U0001F3E0  Back to Dashboard")
    bk.stats["links"] += 1
    ws.set_row(r(4), 7)

    label = S.f(**S.base(font_size=11, bold=True, font_color=th.ink,
                         bg_color=th.card, align="left", valign="vcenter",
                         border=1, border_color=th.border, indent=1))
    note_f = S.f(**S.base(font_size=9.5, italic=True, font_color=th.muted,
                          bg_color=th.card, align="left", valign="vcenter",
                          border=1, border_color=th.border, indent=1))
    input_f = S.f(**S.base(font_size=11, bold=True, font_color=th.primary,
                           bg_color=th.gold_soft, align="center",
                           valign="vcenter", border=2, border_color=th.gold,
                           locked=False))
    auto_f = S.f(**S.base(font_size=11, bold=True, font_color=th.primary_2,
                          bg_color=th.primary_soft, align="center",
                          valign="vcenter", border=1, border_color=th.border))

    def setting(row, text, note, value, fmt, cached=None, height=24):
        ws.set_row(r(row), height)
        ws.write(r(row), ci("B"), text, label)
        if isinstance(value, str) and value.startswith("="):
            ws.write_formula(r(row), ci("C"), value, fmt,
                             cached if cached is not None else 0)
            bk.stats["formulas"] += 1
        elif isinstance(value, date):
            ws.write_datetime(r(row), ci("C"), value, fmt)
        else:
            ws.write(r(row), ci("C"), value, fmt)
        ws.merge_range(r(row), ci("D"), r(row), ci(LAST_COL), note, note_f)

    def section(row, text, style=None):
        ws.set_row(r(row), 24)
        ws.merge_range(r(row), 1, r(row), ci(LAST_COL), text,
                       style or S.section)

    # ------------------------------------------------------------------
    # 1. your event
    # ------------------------------------------------------------------
    section(5, "  \U0001F384  YOUR EVENT")
    date_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.primary,
                            bg_color=th.gold_soft, align="center",
                            valign="vcenter", border=2, border_color=th.gold,
                            num_format="dd mmm yyyy", locked=False))
    money_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.primary,
                             bg_color=th.gold_soft, align="center",
                             valign="vcenter", border=2, border_color=th.gold,
                             num_format="#,##0.00", locked=False))
    pct_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.primary,
                           bg_color=th.gold_soft, align="center",
                           valign="vcenter", border=2, border_color=th.gold,
                           num_format="0%", locked=False))
    num_fmt = S.f(**S.base(font_size=11, bold=True, font_color=th.primary,
                           bg_color=th.gold_soft, align="center",
                           valign="vcenter", border=2, border_color=th.gold,
                           num_format="0", locked=False))

    setting(C.SU_EVENT_NAME, "Event name",
            "Christmas, 40th Birthday, Baby Shower\u2026 it appears on the "
            "dashboard and in every message.",
            m.settings["event_name"], input_f)
    setting(C.SU_EVENT_DATE, "Event date",
            "The countdown, the deadline alerts and the to-do dates all work "
            "from this one cell.",
            date(*C.DEFAULT_EVENT_DATE), date_fmt)
    setting(C.SU_DAYS, "Days to go  (auto)",
            "Recalculates every day by itself.",
            "=IF($C$%d=\"\",\"\",$C$%d-TODAY())"
            % (C.SU_EVENT_DATE, C.SU_EVENT_DATE), auto_f,
            cached=m.agg["days_to_event"])
    setting(C.SU_YEAR, "Event year  (auto)", "",
            "=IF($C$%d=\"\",\"\",YEAR($C$%d))"
            % (C.SU_EVENT_DATE, C.SU_EVENT_DATE), auto_f,
            cached=m.agg["event_year"])
    setting(C.SU_WEEKS, "Weeks to go  (auto)",
            "Rough planning guide: gifts by week 4, cards by week 3, "
            "wrapping by week 1.",
            "=IF($C$%d=\"\",\"\",MAX(0,ROUNDUP(($C$%d-TODAY())/7,0)))"
            % (C.SU_EVENT_DATE, C.SU_EVENT_DATE), auto_f,
            cached=m.agg["weeks_to_event"])
    ws.set_row(r(C.SU_MESSAGE), 26)
    ws.write(r(C.SU_MESSAGE), ci("B"), "Countdown message  (auto)", label)
    msg = ("=IF($C$%d=\"\",\"\U0001F449  Enter your event date to start the "
           "countdown\",IF($C$%d-TODAY()>1,\"\u23F3  \"&($C$%d-TODAY())&\" "
           "days until \"&$C$%d&\"  \u2022  \"&TEXT($C$%d,\"dddd d mmmm "
           "yyyy\"),IF($C$%d-TODAY()=1,\"\u23F3  Tomorrow is \"&$C$%d&\"!  "
           "\U0001F381\",IF($C$%d=TODAY(),\"\U0001F389  It's \"&$C$%d&\" "
           "today!  \U0001F384\",\"\U0001F384  \"&$C$%d&\" \"&TEXT($C$%d,"
           "\"yyyy\")&\" has been and gone \u2014 change the date above to "
           "plan the next one.\"))))"
           % ((C.SU_EVENT_DATE, C.SU_EVENT_DATE, C.SU_EVENT_DATE,
               C.SU_EVENT_NAME, C.SU_EVENT_DATE, C.SU_EVENT_DATE,
               C.SU_EVENT_NAME, C.SU_EVENT_DATE, C.SU_EVENT_NAME,
               C.SU_EVENT_NAME, C.SU_EVENT_DATE)))
    ws.merge_range(r(C.SU_MESSAGE), ci("C"), r(C.SU_MESSAGE), ci(LAST_COL),
                   "", S.f(**S.base(font_size=11, bold=True,
                                    font_color=th.white, bg_color=th.accent,
                                    align="left", valign="vcenter", indent=1)))
    ws.write_formula(r(C.SU_MESSAGE), ci("C"), msg,
                     S.f(**S.base(font_size=11, bold=True, font_color=th.white,
                                  bg_color=th.accent, align="left",
                                  valign="vcenter", indent=1)),
                     m.agg["countdown"])
    bk.stats["formulas"] += 1
    ws.set_row(r(12), 8)

    # ------------------------------------------------------------------
    # 2. reuse for any occasion
    # ------------------------------------------------------------------
    section(13, "  \u267B\uFE0F  REUSE IT FOR ANY OCCASION  "
                "(birthdays, Valentine's, Mother's Day, weddings, "
                "Secret Santa\u2026)")
    setting(C.SU_OCCASION, "Pick an occasion",
            "Just a helper \u2014 it suggests a name and a date for you.",
            m.settings["occasion"], input_f)
    setting(C.SU_SUG_NAME, "Suggested event name  (auto)", "",
            "=IF($C$%d=\"\",\"\",$C$%d)" % (C.SU_OCCASION, C.SU_OCCASION),
            auto_f, cached=m.settings["occasion"])
    d = bk.q("data")
    auto_date = S.f(**S.base(font_size=11, bold=True, font_color=th.primary_2,
                             bg_color=th.primary_soft, align="center",
                             valign="vcenter", border=1,
                             border_color=th.border,
                             num_format="dd mmm yyyy"))
    suggested = _suggested_date(m.settings["occasion"])
    setting(C.SU_SUG_DATE, "Suggested date  (auto)",
            "Copy the two suggestions above into Event name / Event date and "
            "the whole workbook switches occasion.",
            "=IF(%s!$E$2=\"\",\"\",DATE(YEAR(TODAY())+IF(DATE(YEAR(TODAY()),"
            "%s!$E$2,%s!$F$2)<TODAY(),1,0),%s!$E$2,%s!$F$2))"
            % (d, d, d, d, d), auto_date, cached=suggested)
    ws.set_row(r(17), 18)
    ws.merge_range(r(17), 1, r(17), ci(LAST_COL),
                   "  \U0001F4A1  The workbook is date-driven, not "
                   "year-driven: nothing is hard-coded to 2026, so you can "
                   "keep using it every year (and for every other gift-giving "
                   "occasion) just by changing the event date.",
                   S.f(**S.base(font_size=10, italic=True, font_color=th.ink,
                                bg_color=th.gold_soft, align="left",
                                valign="vcenter", indent=1)))
    ws.set_row(r(18), 8)

    # ------------------------------------------------------------------
    # 3. money, alerts & privacy
    # ------------------------------------------------------------------
    section(20, "  \U0001F4B0  MONEY, ALERTS & PRIVACY")
    setting(C.SU_CURRENCY, "Currency symbol",
            "Used by every dashboard and summary readout. To show it inside "
            "the tables too: select the money columns \u2192 Home \u2192 "
            "Number format \u2192 Currency.",
            m.settings["currency"], input_f)
    setting(C.SU_BUDGET, "Total budget target",
            "Your headline number for the whole event (the \U0001F4B0 Budget "
            "tab breaks it down by category).",
            m.settings["budget"] or 0, money_fmt)
    setting(C.SU_ALERT, "Warn me when spending reaches",
            "e.g. 85% \u2014 the dashboard and the Budget tab start shouting "
            "at this point.",
            m.settings["alert"], pct_fmt)
    setting(C.SU_DUESOON, "\u201CDue soon\u201D window (days)",
            "Deadlines inside this many days turn orange everywhere.",
            m.settings["duesoon"], num_fmt)
    setting(C.SU_SECRET, "\U0001F648 Secret Mode",
            "Yes = hiding spots on the \U0001F380 Wrapping and \U0001F9E6 "
            "Stockings tabs go invisible (white on white) so nobody can "
            "spoil the surprise over your shoulder.",
            m.settings["secret"], input_f)
    setting(C.SU_COUNT_ORDERED, "Count \u201COrdered\u201D as purchased?",
            "Yes = gifts that are ordered but not yet delivered still count "
            "as bought on the dashboard.",
            m.settings["count_ordered"], input_f)
    ws.set_row(r(27), 8)

    # ------------------------------------------------------------------
    # 4. editable lists
    # ------------------------------------------------------------------
    section(28, "  \U0001F4CB  YOUR LISTS  \u2014  edit any time, every "
                "dropdown in the workbook updates itself")
    ws.set_row(r(C.SU_LIST_HEADER), 30)
    for lk, col in sorted(C.LIST_COLS.items(), key=lambda kv: kv[1]):
        ws.write(r(C.SU_LIST_HEADER), ci(col), C.LIST_TITLES[lk],
                 S.header(th.primary))
    values = {
        "recipients": m.recipients,
        "relationships": C.RELATIONSHIPS,
        "gift_categories": C.GIFT_CATEGORIES,
        "stores": C.STORES,
        "shop_categories": C.SHOP_CATEGORIES,
        "hiding_spots": C.HIDING_SPOTS,
        "todo_categories": C.TODO_CATEGORIES,
        "stocking_owners": m.owners,
        "stocking_items": C.STOCKING_ITEMS,
    }
    list_fmt = S.f(**S.base(font_size=10, font_color=th.ink, bg_color=th.card,
                            align="left", valign="vcenter", border=1,
                            border_color=th.border, indent=1, locked=False))
    list_fmt_alt = S.f(**S.base(font_size=10, font_color=th.ink,
                                bg_color=th.alt, align="left",
                                valign="vcenter", border=1,
                                border_color=th.border, indent=1,
                                locked=False))
    for i in range(C.SU_LIST_ROWS):
        row = C.SU_LIST_FIRST + i
        ws.set_row(r(row), 18)
        for lk, col in C.LIST_COLS.items():
            vals = values[lk]
            value = vals[i] if i < len(vals) else ""
            ws.write(r(row), ci(col), value,
                     list_fmt_alt if i % 2 else list_fmt)
    ws.set_row(r(50), 26)
    ws.merge_range(r(50), 1, r(51), ci(LAST_COL),
                   "  \u2022  Type over the example names with your own \u2014 "
                   "add as many as you like (20 rows each).\n"
                   "  \u2022  Don't leave a blank row in the middle of a list: "
                   "the dropdown stops at the first gap.\n"
                   "  \u2022  Deleting a name here does NOT delete your gifts "
                   "\u2014 it only removes it from the dropdown.",
                   S.note)
    ws.set_row(r(51), 26)
    ws.set_row(r(52), 8)

    # ------------------------------------------------------------------
    # 5. fixed lists
    # ------------------------------------------------------------------
    section(52, "  \U0001F512  FIXED LISTS  \u2014  the colours, counts and "
                "dashboard maths depend on this exact wording, so please "
                "leave them alone", S.section_accent)
    ws.set_row(r(C.SU_FIXED_HEADER), 26)
    fixed_titles = {"statuses": "Gift status", "order_statuses": "Order status",
                    "priorities": "Priority", "tick": "Tick box"}
    for fk, col in sorted(C.FIXED_COLS.items(), key=lambda kv: kv[1]):
        ws.write(r(C.SU_FIXED_HEADER), ci(col), fixed_titles[fk],
                 S.header(th.accent))
    ws.merge_range(r(C.SU_FIXED_HEADER), ci("F"), r(C.SU_FIXED_HEADER),
                   ci(LAST_COL),
                   "  Status order = your gift pipeline: idea \u2192 need to "
                   "buy \u2192 ordered \u2192 purchased \u2192 wrapped "
                   "\u2192 delivered.", S.note)
    fixed_values = {"statuses": C.STATUSES, "order_statuses": C.ORDER_STATUSES,
                    "priorities": C.PRIORITIES, "tick": [C.TICK, ""]}
    fixed_fmt = S.f(**S.base(font_size=10, font_color=th.ink, bg_color=th.alt,
                             align="left", valign="vcenter", border=1,
                             border_color=th.border, indent=1))
    for i in range(6):
        row = C.SU_FIXED_FIRST + i
        ws.set_row(r(row), 18)
        for fk, col in C.FIXED_COLS.items():
            vals = fixed_values[fk]
            value = vals[i] if i < len(vals) else ""
            ws.write(r(row), ci(col), value, fixed_fmt)
        for col in ("F", "G", "H", "I", "J"):
            ws.write_blank(r(row), ci(col), None, S.canvas)
    ws.set_row(r(60), 20)
    ws.merge_range(r(60), 1, r(61), ci(LAST_COL),
                   "  \u2713  The tick column holds the \u201Ccheckbox\u201D "
                   "used all over the workbook: pick \u2713 from a dropdown to "
                   "tick something off, pick the empty option to untick it.\n"
                   "  \u2713  Want different wording? Change it here AND in "
                   "the cells that already use it (Find & Replace does the "
                   "job in two clicks).",
                   S.note)
    ws.set_row(r(61), 20)
    ws.set_row(r(62), 8)

    # ------------------------------------------------------------------
    # 6. navigation
    # ------------------------------------------------------------------
    section(63, "  \U0001F9ED  WHERE TO GO NEXT")
    ws.set_row(r(64), 26)
    ws.set_row(r(65), 26)
    row = bk.nav_row(key, 64, first_col=1, span=1,
                     max_col=LAST_COL) + 2
    ws.set_row(r(row - 1), 10)
    ws.merge_range(r(row), 1, r(row), ci(LAST_COL),
                   "  %s v%s  \u2022  %s  \u2022  works in Excel 2016+ and "
                   "Google Sheets  \u2022  no macros, nothing to install"
                   % (C.PRODUCT, C.VERSION, C.TAGLINE), S.footer)

    # ------------------------------------------------------------------
    # validation
    # ------------------------------------------------------------------
    dv = ws.data_validation
    dv(r(C.SU_OCCASION), ci("C"), r(C.SU_OCCASION), ci("C"),
       {"validate": "list", "source": "=Occasions", "ignore_blank": True})
    dv(r(C.SU_CURRENCY), ci("C"), r(C.SU_CURRENCY), ci("C"),
       {"validate": "list", "source": C.CURRENCIES, "ignore_blank": True})
    for row in (C.SU_SECRET, C.SU_COUNT_ORDERED):
        dv(r(row), ci("C"), r(row), ci("C"),
           {"validate": "list", "source": C.YESNO, "ignore_blank": True,
            "show_error": True, "error_title": "Yes or No",
            "error_message": "Please choose Yes or No."})
    dv(r(C.SU_EVENT_DATE), ci("C"), r(C.SU_EVENT_DATE), ci("C"),
       {"validate": "date", "criteria": "between", "minimum": date(2000, 1, 1),
        "maximum": date(2100, 12, 31), "ignore_blank": True,
        "show_error": True, "error_title": "Enter a date",
        "error_message": "Please enter a real date, e.g. 25/12/2026.",
        "error_type": "warning"})
    dv(r(C.SU_BUDGET), ci("C"), r(C.SU_BUDGET), ci("C"),
       {"validate": "decimal", "criteria": ">=", "value": 0,
        "ignore_blank": True, "show_error": True, "error_title": "Budget",
        "error_message": "Enter a positive number (no currency symbol).",
        "error_type": "warning"})
    dv(r(C.SU_ALERT), ci("C"), r(C.SU_ALERT), ci("C"),
       {"validate": "decimal", "criteria": "between", "minimum": 0.05,
        "maximum": 1, "ignore_blank": True, "show_input": True,
        "input_title": "Alert threshold",
        "input_message": "0.85 = warn me when I have spent 85%.",
        "show_error": True, "error_title": "Percentage",
        "error_message": "Enter a percentage between 5% and 100% (0.05-1).",
        "error_type": "warning"})
    dv(r(C.SU_DUESOON), ci("C"), r(C.SU_DUESOON), ci("C"),
       {"validate": "whole", "criteria": "between", "minimum": 1,
        "maximum": 60, "ignore_blank": True, "show_error": True,
        "error_title": "Days", "error_message": "Enter a number of days "
        "between 1 and 60.", "error_type": "warning"})
    bk.stats["validations"] += 8

    # ------------------------------------------------------------------
    # page setup
    # ------------------------------------------------------------------
    bk.page(key, LAST_COL, row + 3, landscape=True, freeze=(r(5), 0),
            zoom=100,
            title_rows=(0, 4))
    return ws
