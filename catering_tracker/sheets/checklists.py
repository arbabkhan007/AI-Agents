"""
Checklists: the four lists that get an event from "yes" to "packed up".

Master prep, shopping, the day-of timeline and the wrap-up - each with a
tick dropdown and a live progress bar, because the fastest way to lose
money in catering is to forget the one thing nobody wrote down.
"""

from .. import config as C
from ..book import r, ci
from .common import blank_row

LISTS = [
    ("prep", "1 \u00b7 Event prep - the master list",
     ["Confirm date, guest count and menu with the client",
      "Send the quote and get written approval",
      "Collect the deposit and log it on the Payments tab",
      "Book the venue walk-through and floor plan",
      "Finalise the menu and schedule a tasting if needed",
      "Confirm the crew and send the schedule (Staff tab)",
      "Reserve equipment and rentals (Equipment tab)",
      "Build the shopping list against inventory",
      "Order ingredients with long lead times",
      "Confirm delivery, setup and pack-down times"]),
    ("shop", "2 \u00b7 Shopping & supplies",
     ["Stock check against minimum levels (Inventory tab)",
      "Build the per-event shopping list",
      "Compare supplier prices before ordering",
      "Place bulk orders on account / net terms",
      "Buy dairy and proteins (2-3 days before)",
      "Buy fresh produce (1-2 days before)",
      "Confirm delivery slots with suppliers",
      "Receive, check, label and store everything",
      "Prepare anything that can be made ahead",
      "Stage crates per event so nothing walks off"]),
    ("day", "3 \u00b7 On the day - the timeline",
     ["Load the van the night before (use the packing order)",
      "Team briefing, uniforms and food-safety check",
      "Arrive, set up kitchen and service stations",
      "Start cooking on schedule",
      "Set tables, linen and garnishes",
      "Brief the service team on the run of play",
      "Service begins - plates land on time",
      "Clear and refresh between courses",
      "Pack down equipment and leftovers",
      "Final walk-through with the client before leaving"]),
    ("end", "4 \u00b7 Wrap-up & follow-up",
     ["Send the final invoice and log the balance",
      "Record actual costs on the Expenses tab",
      "Update inventory quantities after the event",
      "Pay the crew and tick the shifts off",
      "Log mileage, fuel and any parking costs",
      "Note what worked and what to change next time",
      "Ask for a review or a referral",
      "File receipts, photos and the signed quote",
      "Update the client's notes for next time",
      "Celebrate - you earned it"]),
]

TICK_COL = 1                # column B
TEXT_COL1, TEXT_COL2 = 2, 10  # C..K merged
LAST_COL = "K"
HEADER_ROW = 10


def _layout():
    """{key: (first_item_row, last_item_row, header_row)} + end row."""
    out, h = {}, HEADER_ROW
    for key, title, items in LISTS:
        out[key] = (h + 1, h + len(items), h)
        h += len(items) + 2
    return out, h


def build(bk):
    ws = bk.ws("checklists")
    S, th = bk.S, bk.th
    demo = bk.demo
    checks = demo.checks if demo.demo else {}
    rows, end = _layout()

    bk.widths("checklists", {"A": 2.2, "B": 6, "C": 12, "D": 12, "E": 12,
                             "F": 12, "G": 12, "H": 12, "I": 12, "J": 12,
                             "K": 12, "L": 3})
    for row in range(0, end + 10):
        ws.set_row(row, 19)

    bk.title_block("checklists", "Checklists",
                   "From \u201cyes\u201d to packed up - the four lists "
                   "that keep an event on the rails", LAST_COL)

    # ------------------------------------------------------------------
    # progress bars for all four lists (row 8)
    # ------------------------------------------------------------------
    ws.set_row(r(8), 24)
    col = 1
    for key, title, items in LISTS:
        first, last, _ = rows[key]
        ticked = len(checks.get(key, set()))
        colour = th.ok
        ws.merge_range(r(8), col, r(8), col + 1, "",
                       S.kpi_label(colour, size=9))
        ws.write_formula(r(8), col,
                         '=COUNTIF($B$%d:$B$%d,"%s")&"/"&%d&" done"'
                         % (first, last, C.TICK, len(items)),
                         S.kpi_label(colour, size=9),
                         "%d/%d done" % (ticked, len(items)))
        ws.merge_range(r(8), col + 2, r(8), col + 3, "", S.bar_text)
        ws.write_formula(r(8), col + 2,
                         bk.bar('COUNTIF($B$%d:$B$%d,"%s")'
                                % (first, last, C.TICK),
                                "%d" % len(items), 14),
                         S.bar_text, bk.bar_static(ticked, len(items), 14))
        bk.stats["formulas"] += 2
        col += 4

    # ------------------------------------------------------------------
    # the four lists
    # ------------------------------------------------------------------
    for key, title, items in LISTS:
        first, last, hrow = rows[key]
        ws.merge_range(r(hrow), 1, r(hrow), ci(LAST_COL) - 1, title,
                       S.section)
        ws.set_row(r(hrow), 24)
        for i, item in enumerate(items):
            row = first + i
            fmt = S.cell("tick", (row % 2) == 0)
            ws.write_blank(r(row), TICK_COL, None, fmt)
            text_fmt = S.cell("text", (row % 2) == 0)
            ws.merge_range(r(row), TEXT_COL1, r(row), TEXT_COL2, item,
                           text_fmt)
            if demo.demo and i in checks.get(key, set()):
                ws.write(r(row), TICK_COL, C.TICK, fmt)

    # one validation + one conditional format covers every tick cell
    ws.data_validation(
        r(HEADER_ROW), TICK_COL, r(end), TICK_COL,
        {"validate": "list", "source": "=Tick", "ignore_blank": True,
         "show_input": True, "input_title": "Tick it off",
         "input_message": "Pick \u2713 from the dropdown (blank = not "
                          "done yet)."})
    bk.stats["validations"] += 1
    ws.conditional_format(
        r(HEADER_ROW), TICK_COL, r(end), TICK_COL,
        {"type": "cell", "criteria": "==", "value": C.TICK,
         "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True, size=13)})
    bk.stats["cond_formats"] += 1

    blank_row(bk, "checklists", end, "A", LAST_COL, height=8)
    ws.merge_range(r(end + 1), 1, r(end + 1), ci(LAST_COL) - 1,
                   "Tweak these until they match how you work - then "
                   "never improvise at 6am again.", S.note)
    ws.set_row(r(end + 1), 26)

    bk.nav_row("checklists", end + 3, first_col=1, span=2, max_col=LAST_COL)
    bk.page("checklists", LAST_COL, end + 5, landscape=False, freeze=None,
            zoom=100)
