"""The `Workflow` tab - the kanban view of the Content Calendar."""

from __future__ import annotations

from ..writer import NAV_LINKS, SheetWriter

NAME = "Workflow"
LAST_COL = 14      # A spacer + 5 status lanes x ~2.5 cols

LANES = [
    ("Idea", "#F1F1EF"),
    ("Draft", "#FBEBD0"),
    ("In Progress", "#FBEBD0"),
    ("Ready", "#DCE7F3"),
    ("Scheduled", "#DCE7F3"),
    ("Posted", "#DDEEDB"),
]
LANE_ROWS = 8


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#2E7D8F")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Workflow",
                 "The Content Calendar, seen sideways: what is stuck in "
                 "each stage. Cards show live from the calendar.",
                 LAST_COL)

    sheet.set_col(0, 0, 2)
    for col in range(1, LAST_COL + 1):
        sheet.set_col(col, col, 13)

    cal = reg["Content Calendar"]
    status_key = "[[Content Calendar.status_key]]"
    title_rng = "[[Content Calendar.title]]"
    date_rng = "[[Content Calendar.date]]"
    owner_rng = "[[Content Calendar.owner]]"

    row = 4
    # Lane headers and counts
    lane_start_cols = [1 + i * 2 for i in range(len(LANES))]   # 1,3,5,7,9
    for (status, color), col in zip(LANES, lane_start_cols):
        fmt_head = sheet.book.add_format({
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": "#3D3B36", "bg_color": color,
            "align": "center", "valign": "vcenter",
            "border": 1, "border_color": "#E4E4E0", "locked": True})
        sheet.merge(row, col, col + 1, status, fmt_head)
        fmt_count = f.cell("int", "calc")
        sheet.merge(row + 1, col, col + 1, "", fmt_count)
        sheet.ws.write_formula(
            row + 1, col,
            sheet.reg.render(f"=COUNTIF({status_key},{_col(col)}${row + 1}"
                             f"&\"#*\")"), fmt_count)
    sheet.row_height(row, 22)
    sheet.row_height(row + 1, 18)
    row += 2

    # Cards
    for (status, color), col in zip(LANES, lane_start_cols):
        fmt_card = sheet.book.add_format({
            "font_name": "Calibri", "font_size": 9, "bold": True,
            "font_color": "#3D3B36", "bg_color": "#FFFFFF",
            "align": "left", "valign": "top", "text_wrap": True,
            "indent": 1, "border": 1, "border_color": "#E4E4E0",
            "locked": True})
        fmt_meta = sheet.book.add_format({
            "font_name": "Calibri", "font_size": 8,
            "font_color": "#8A8A85", "bg_color": "#FFFFFF",
            "align": "left", "valign": "top", "indent": 1,
            "border": 1, "border_color": "#E4E4E0", "locked": True})
        for n in range(1, LANE_ROWS + 1):
            card_row = row + (n - 1) * 2
            sheet.merge(card_row, col, col + 1, "", fmt_card)
            sheet.ws.write_formula(
                card_row, col,
                sheet.reg.render(
                    f"=IFERROR(INDEX({title_rng},MATCH({status_key},"
                    f"TEXT({_col(col)}${row - 1},\"@\")&\"#{n}\",0)),"
                    f"IF({n}=1,\"-- empty --\",\"\"))"),
                fmt_card)
            sheet.merge(card_row + 1, col, col + 1, "", fmt_meta)
            sheet.ws.write_formula(
                card_row + 1, col,
                sheet.reg.render(
                    f"=IFERROR(TEXT(INDEX({date_rng},MATCH({status_key},"
                    f"TEXT({_col(col)}${row - 1},\"@\")&\"#{n}\",0)),"
                    f"\"yyyy-mm-dd\")&\"  ·  \"&INDEX({owner_rng},"
                    f"MATCH({status_key},TEXT({_col(col)}${row - 1},\"@\")"
                    f"&\"#{n}\",0)),\"\")"),
                fmt_meta)
            sheet.row_height(card_row, 26)
            sheet.row_height(card_row + 1, 14)
    row += LANE_ROWS * 2 + 1

    # Workflow checklist
    row = sheet.section(row, "Weekly workflow checklist", 6)
    checks = [
        ("Mon", "Review last week's numbers, pick this week's ideas"),
        ("Tue", "Batch film / shoot - one session, many posts"),
        ("Wed", "Write captions, schedule the front half of the week"),
        ("Thu", "Community: reply, engage, reshare UGC"),
        ("Fri", "Schedule the back half, queue repurposing"),
        ("Sat", "Light touch - stories only"),
        ("Sun", "Rest. The planner keeps watch."),
    ]
    for day, task in checks:
        sheet.write(row, 1, day, f.chrome("label_bold"))
        sheet.merge(row, 2, 6, task, f.chrome("label"))
        row += 1

    row += 1
    row = sheet.section(row, "Production checklist (per post)", 6)
    for item in ["Idea logged in the Idea Bank",
                 "Brief written (see Print Brief)",
                 "Visual asset shot / made",
                 "Caption written and approved",
                 "Hashtag set chosen",
                 "Scheduled with the right link and UTM",
                 "Compliance checked (music, rights, disclosures)",
                 "Numbers logged in Performance within 7 days"]:
        sheet.merge(row, 1, 6, f"□   {item}", f.chrome("label"))
        row += 1

    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Cards move when the Status column moves - the Workflow "
                "tab never needs editing.",
                f.chrome("note"))
    row += 2

    for label, target in NAV_LINKS[:4]:
        sheet.merge(row, 0, 2, "", f.chrome("nav"))
        sheet.ws.write_url(row, 0, f"internal:'{target}'!A1",
                           f.chrome("nav"), f"> {label}")
        row += 1

    sheet.finish(freeze_row=6,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet


def _col(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters
