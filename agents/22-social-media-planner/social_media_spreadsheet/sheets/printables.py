"""Print-ready pages: the one-post Content Brief and the weekly schedule.

Both are styled for paper: big titles, ruled form lines, no clutter. They
read everything from the Content Calendar through lookups - type once, in
the calendar.
"""

from __future__ import annotations

from ..writer import SheetWriter

BRIEF_NAME = "Print Brief"
WEEK_NAME = "Print Week"
LAST_COL = 7


# ---------------------------------------------------------------------------
# Print Brief
# ---------------------------------------------------------------------------

def build_brief(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, BRIEF_NAME,
                        tab_color="#B0B0A8")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Content Brief",
                 f"{cfg.brand.name}  |  Print this page and nothing gets "
                 f"lost between the idea and the post.",
                 LAST_COL)

    sheet.set_col(0, 0, 3)
    sheet.set_col(1, 1, 18)
    sheet.set_col(2, 3, 16)
    sheet.set_col(4, 5, 16)
    sheet.set_col(6, LAST_COL, 14)

    cal = reg["Content Calendar"]

    def lookup(key: str, blank: str = "") -> str:
        return sheet.reg.render(
            f"=IFERROR(INDEX([[Content Calendar.{key}]],"
            f"MATCH($C$5,[[Content Calendar.id]],0)),\"{blank}\")")

    row = 4
    sheet.merge(row, 0, 1, "Content ID", f.chrome("label_bold"))
    sheet.merge(row, 2, 3, None, f.input("id"))
    sheet.write(row, 2, "C-0001", f.input("id"))
    sheet.merge(row, 4, LAST_COL,
                "Type any Content ID from the Content Calendar - every line "
                "below fills itself.",
                f.chrome("note"))
    id_cell = f"$C${row + 1}"
    row += 2

    pairs = [
        ("Publish date", "date", "date"),
        ("Publish time", "time", "time"),
        ("Weekday", "weekday", "text"),
        ("Title / topic", "title", "wrap"),
        ("Platforms", "platforms", "wrap"),
        ("Pillar", "pillar", "text"),
        ("Format", "format", "text"),
        ("Campaign", "campaign", "text"),
        ("Owner", "owner", "text"),
        ("Status", "status", "text"),
        ("Goal", "goal", "text"),
        ("Caption ref", "caption_ref", "text"),
        ("Hashtag set", "hashtags", "text"),
        ("Asset ref", "asset", "text"),
    ]
    for label, key, style in pairs:
        sheet.merge(row, 0, 1, label, f.chrome("form_label"))
        sheet.merge(row, 2, LAST_COL, "", f.cell(style, "calc"))
        sheet.ws.write_formula(row, 2, lookup(key), f.cell(style, "calc"))
        row += 1

    sheet.merge(row, 0, 1, "CTA", f.chrome("form_label"))
    sheet.merge(row, 2, LAST_COL, "", f.cell("wrap", "calc"))
    sheet.ws.write_formula(row, 2, lookup("cta"), f.cell("wrap", "calc"))
    row += 1

    sheet.merge(row, 0, LAST_COL, "Brief / creative direction",
                f.chrome("section"))
    row += 1
    sheet.merge(row, 0, 1, "From calendar notes",
                f.chrome("form_label"))
    sheet.merge(row, 2, LAST_COL, "", f.cell("wrap", "calc"))
    sheet.ws.write_formula(row, 2, lookup("notes"), f.cell("wrap", "calc"))
    sheet.row_height(row, 54)
    row += 2

    sheet.merge(row, 0, LAST_COL, "Ready-to-post checklist",
                f.chrome("section"))
    row += 1
    for item in ["Hook written (first line earns the tap)",
                 "Visual shot and exported in the right ratios",
                 "Caption approved in the right voice",
                 "Hashtag set chosen (watch the tag count)",
                 "Link / UTM tested",
                 "Compliance cleared (music, rights, disclosures)",
                 "Scheduled in the platform or scheduler"]:
        sheet.merge(row, 0, LAST_COL - 1, f"□   {item}", f.chrome("label"))
        sheet.write(row, LAST_COL, None, f.cell("flag", "input"))
        row += 1

    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Sign-off: ___________________________     "
                "Date: _______________",
                f.chrome("form_label"))
    sheet.row_height(row, 24)

    sheet.finish(freeze_row=6,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet


# ---------------------------------------------------------------------------
# Print Week
# ---------------------------------------------------------------------------

def build_week(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, WEEK_NAME,
                        tab_color="#B0B0A8")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Weekly Schedule",
                 f"{cfg.brand.name}  |  One week, seven columns, every "
                 f"post in its place.",
                 LAST_COL)

    sheet.set_col(0, 0, 2)
    for col in range(1, 8):
        sheet.set_col(col, col, 18)

    row = 4
    sheet.merge(row, 0, 1, "Week starting", f.chrome("label_bold"))
    sheet.merge(row, 2, 3, None, f.input("date"))
    sheet.ws.write_formula(row, 2,
                           "='Calc'!$B$4", f.input("date"))
    sheet.merge(row, 4, LAST_COL,
                "Defaults to the planner's current week - type any Monday "
                "to print another.",
                f.chrome("note"))
    week_cell = f"$C${row + 1}"
    row += 2

    sheet.merge(row, 0, LAST_COL, "", f.chrome("print_title"))
    sheet.ws.write_formula(
        row, 0,
        sheet.reg.render(
            f"=\"Week of \"&TEXT({week_cell},\"d mmmm yyyy\")&\"  -  \"&"
            f"COUNTIFS([[Content Calendar.date]],\">=\"&{week_cell},"
            f"[[Content Calendar.date]],\"<\"&{week_cell}+7)&\" posts\""),
        f.chrome("print_title"))
    sheet.row_height(row, 24)
    row += 1

    dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
           "Saturday", "Sunday"]
    for i, day in enumerate(dow):
        sheet.write(row, 1 + i, day, f.chrome("header"))
        sheet.row_height(row, 18)
    date_row = row + 1
    for i in range(7):
        sheet.write(date_row, 1 + i, None, f.chrome("label_right"))
        sheet.ws.write_formula(
            date_row, 1 + i,
            f"={week_cell}+{i}", f.cell("date", "calc"))
    row = date_row + 1

    # Six card rows per day: time + title + owner/status.
    cal = reg["Content Calendar"]
    for n in range(1, 5):
        for i in range(7):
            date_expr = f"{week_cell}+{i}"
            key_expr = f'TEXT({date_expr},"0")&"#{n}"'
            fmt_time = f.cell("time", "calc")
            fmt_title = f.cell("wrap", "calc")
            fmt_meta = f.cell("text", "calc")
            sheet.write(row, 1 + i, None, fmt_time)
            sheet.ws.write_formula(
                row, 1 + i,
                sheet.reg.render(
                    f"=IFERROR(INDEX([[Content Calendar.time]],"
                    f"MATCH({key_expr},[[Content Calendar.nth_key]],0)),"
                    f"\"\")"), fmt_time)
            sheet.row_height(row + 1, 32)
            sheet.write(row + 1, 1 + i, None, fmt_title)
            sheet.ws.write_formula(
                row + 1, 1 + i,
                sheet.reg.render(
                    f"=IFERROR(INDEX([[Content Calendar.title]],"
                    f"MATCH({key_expr},[[Content Calendar.nth_key]],0)),"
                    f"\"\")"), fmt_title)
            sheet.row_height(row + 2, 14)
            sheet.write(row + 2, 1 + i, None, fmt_meta)
            sheet.ws.write_formula(
                row + 2, 1 + i,
                sheet.reg.render(
                    f"=IFERROR(INDEX([[Content Calendar.status]],"
                    f"MATCH({key_expr},[[Content Calendar.nth_key]],0))"
                    f"&\" - \"&INDEX([[Content Calendar.owner]],"
                    f"MATCH({key_expr},[[Content Calendar.nth_key]],0)),"
                    f"\"\")"), fmt_meta)
        row += 3

    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Four posts per day fit on one page. The Content Calendar "
                "holds the rest - filter it by this week to see everything.",
                f.chrome("note"))
    sheet.row_height(row, 26)

    sheet.finish(freeze_row=9,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet
