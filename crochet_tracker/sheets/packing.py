"""
Packing Checklist - never leave the price tags on the kitchen table again.

Pick the fair, then tick your way down: products, booth kit, payment kit,
supplies. 'Where it lives' is yours to fill in once (blue crate, yarn
bag...) so packing next time is muscle memory.
"""

from .. import config as C
from ..book import r, ci
from . import common

LAST_COL = "F"


def build(bk):
    S, th, ws = bk.S, bk.th, bk.ws("packing")
    demo = bk.demo
    ticks = demo.packing if demo else {}
    packed = demo.agg["packed"] if demo else 0
    total_items = demo.agg["packed_total"] if demo else sum(
        len(items) for _, items in C.PACK_SECTIONS)

    common.sheet_head(bk, "packing", LAST_COL, "\U0001F392  Packing "
                      "Checklist", "Tick your way out the door - nothing "
                      "left behind")

    # ------------------------------------------------------- picker
    ws.set_row(r(5), 22)
    ws.write(r(C.PACK_EVENT_ROW), ci("B"), "", S.canvas)
    ws.write(r(C.PACK_EVENT_ROW), ci("C"), "Packing for:",
             S.f(**S.base(font_size=11, bold=True, font_color=th.ink,
                          bg_color=th.card, align="left", valign="vcenter",
                          border=1, border_color=th.border, indent=1)))
    ws.merge_range(r(C.PACK_EVENT_ROW), ci("D"), r(C.PACK_EVENT_ROW),
                   ci(LAST_COL), "", S.f(**S.base(
                       font_size=12, bold=True, font_color=th.primary,
                       bg_color=th.card, align="left", valign="vcenter",
                       border=1, border_color=th.border, indent=1,
                       locked=False)))
    ws.data_validation(
        r(C.PACK_EVENT_ROW), ci("D"), r(C.PACK_EVENT_ROW), ci("D"),
        {"validate": "list", "source": "=EventList", "ignore_blank": True,
         "show_input": True, "input_title": "Craft fair",
         "input_message": "Which fair are you packing for?",
         "show_error": False})
    bk.stats["validations"] += 1
    if demo:
        ws.write(r(C.PACK_EVENT_ROW), ci("D"), demo.profit_event,
                 S.f(**S.base(font_size=12, bold=True, font_color=th.primary,
                              bg_color=th.card, align="left",
                              valign="vcenter", border=1,
                              border_color=th.border, indent=1,
                              locked=False)))

    # ------------------------------------------------- progress chip
    first_tick = 9
    last_tick = 35
    common.chips(bk, "packing", [
        ('="Packed: "&TEXT(COUNTIF($B$%d:$B$%d,"%s"),"0")&" of %d"'
         % (first_tick, last_tick, C.TICK, total_items), "ok",
         "Packed: %d of %d" % (packed, total_items), 3),
        ('=IF(COUNTIF($B$%d:$B$%d,"%s")=%d,"Ready for the fair!",'
         '"Keep ticking...")' % (first_tick, last_tick, C.TICK,
                                 total_items), "gold",
         "Ready for the fair!" if packed == total_items else "Keep "
         "ticking...", 2),
    ])

    # ------------------------------------------------------ sections
    row = 8
    colors = {"Products": "accent", "Booth": "primary_2", "Payments": "info",
              "Supplies": "plum"}
    ws.write(r(row - 1), ci("B"), "#", S.header(th.muted))
    ws.write(r(row - 1), ci("C"), "Item", S.header(th.muted))
    ws.write(r(row - 1), ci("D"), "Where it lives", S.header(th.muted))
    ws.merge_range(r(row - 1), ci("E"), r(row - 1), ci(LAST_COL), "Notes",
                   S.header(th.muted))
    ws.set_row(r(row - 1), 20)
    for title, items in C.PACK_SECTIONS:
        ws.set_row(r(row), 22)
        bk.band("packing", row, 1, ci(LAST_COL), S.section, height=22)
        ws.write(r(row), 1, "  " + title, S.section)
        row += 1
        for item in items:
            ws.set_row(r(row), 20)
            a = common.alt(row)
            tick_fmt = S.cell("tick", a)
            ws.write_blank(r(row), ci("B"), None, tick_fmt)
            if ticks.get(item):
                ws.write(r(row), ci("B"), C.TICK, tick_fmt)
            ws.write(r(row), ci("C"), item, S.cell("text", a))
            ws.write_blank(r(row), ci("D"), None, S.cell("text", a))
            ws.merge_range(r(row), ci("E"), r(row), ci(LAST_COL), "",
                           S.cell("text", a))
            row += 1
        row += 1  # spacer between sections

    # ---------------------------------------------------------- DV/CF
    ws.data_validation(
        r(first_tick), ci("B"), r(last_tick), ci("B"),
        {"validate": "list", "source": "=Tick", "ignore_blank": True,
         "show_input": True, "input_title": "Tick it off",
         "input_message": "\u2713 = packed, blank = not yet, \u2717 = "
                          "not needed.", "show_error": False})
    bk.stats["validations"] += 1
    B = "B"
    bk.cond("packing", r(first_tick), ci("B"), r(last_tick), ci("B"), {
        "type": "formula", "criteria": '=$B%d="%s"' % (first_tick, C.TICK),
        "format": S.cf(bg=th.ok_soft, fg=th.ok, bold=True, size=13)})
    bk.cond("packing", r(first_tick), ci("B"), r(last_tick), ci("B"), {
        "type": "formula", "criteria": '=$B%d="\u2717 Skip"' % first_tick,
        "format": S.cf(bg=th.alt, fg=th.muted, bold=True, size=13)})

    # ---------------------------------------------------------- notes
    nrow = row + 1
    common.note_block(
        bk, "packing", nrow, 1, ci(LAST_COL), [
            "Fill in 'Where it lives' once - next season you'll pack from "
            "muscle memory.",
            "Use \u2717 Skip for things a specific fair doesn't need (some "
            "venues provide tables, some ban card readers).",
        ], title="  Packing pro tips")

    common.footer_nav(bk, "packing", nrow + 4, LAST_COL, zoom=100)
