"""The `Start Here` tab - the front door."""

from __future__ import annotations

from ..writer import NAV_LINKS, SheetWriter

NAME = "Start Here"
LAST_COL = 7

STEPS = [
    ("1", "Set your settings",
     "Open the Settings tab and set your brand name, currency, planning "
     "year and default owner. Everything in the headers follows these."),
    ("2", "Fill the reference tabs",
     "Lists feeds every drop down. Accounts, Audience Personas and Content "
     "Pillars describe who you are posting as, for whom, and about what."),
    ("3", "Plan the calendar",
     "One row per post on the Content Calendar. Pick the pillar, format, "
     "platform and date - the IDs and weekdays write themselves."),
    ("4", "Build your swipe files",
     "Idea Bank catches sparks. Caption Bank and Hashtag Bank hold the "
     "words you reuse. Platform tabs go deeper per network."),
    ("5", "Run campaigns and launches",
     "Campaigns group posts around a push. Launch Planner adds the "
     "countdown. Seasonal Planner keeps the year's moments in view."),
    ("6", "Measure and report",
     "Log weekly numbers in Analytics and post results in Performance. "
     "Reports writes the summary, and the print tabs make it client-ready."),
]

FEATURES = [
    "43 connected tabs - one source of truth for the whole content machine",
    "600 row master Content Calendar with live IDs and status lookups",
    "Drop downs everywhere, fed from one Lists tab you can edit",
    "Hidden engine keeps every formula Excel 2010 safe - no fancy functions",
    "Month View turns the calendar into a month you can actually read",
    "Analytics, Performance, AB Tests and Ads - the numbers in one place",
    "Print Brief and Print Week are clean, client-ready print pages",
    "Every sheet protected with the password 'premium'; cream cells are "
    "yours to type in",
]


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#C98F5B")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner(
        "Social Media Content Calendar & Analytics Planner",
        f"{cfg.brand.name}  |  {cfg.today.year} planning year  |  "
        f"{cfg.author}  |  v{cfg.version}",
        LAST_COL)

    sheet.set_col(0, 0, 3)
    sheet.set_col(1, 1, 4)
    sheet.set_col(2, 3, 16)
    sheet.set_col(4, 5, 16)
    sheet.set_col(6, 7, 16)

    row = 4
    sheet.merge(row, 0, LAST_COL,
                "Plan a month of content in an afternoon - and know what "
                "worked.",
                f.chrome("print_title"))
    sheet.row_height(row, 24)
    row += 1
    sheet.merge(row, 0, LAST_COL,
                "This workbook is a small content studio: a master "
                "calendar, per-platform planners, swipe files for ideas and "
                "words, campaign and launch trackers, and the analytics "
                "that tell you what to make more of. Everything is wired "
                "together - one entry, and the dashboards move.",
                f.chrome("note"))
    sheet.row_height(row, 32)
    row += 2

    row = sheet.section(row, "How to use this planner", LAST_COL)
    for num, title, body in STEPS:
        sheet.merge(row, 0, 1, num, f.chrome("kpi_label"))
        sheet.merge(row, 2, 3, title, f.chrome("label_bold"))
        sheet.merge(row, 4, LAST_COL, body, f.chrome("note"))
        sheet.row_height(row, 28)
        row += 1

    row += 1
    row = sheet.section(row, "What is inside", LAST_COL)
    for feature in FEATURES:
        sheet.merge(row, 0, LAST_COL, f"•  {feature}", f.chrome("label"))
        row += 1

    row += 1
    row = sheet.section(row, "Legend", LAST_COL)
    sheet.merge(row, 0, 1, "Input", f.chrome("legend_label"))
    sheet.merge(row, 2, 3, "", f.chrome("legend_input"))
    sheet.merge(row, 4, LAST_COL,
                "Cream cells are unlocked - type straight into them.",
                f.chrome("note"))
    row += 1
    sheet.merge(row, 0, 1, "Calculated", f.chrome("legend_label"))
    sheet.merge(row, 2, 3, "", f.chrome("legend_calc"))
    sheet.merge(row, 4, LAST_COL,
                "Grey cells are locked formulas - they fill themselves in. "
                "The sheet password is 'premium' (change it under File > "
                "Protect Workbook if you like).",
                f.chrome("note"))
    sheet.row_height(row, 26)
    row += 2

    sheet.merge(row, 0, LAST_COL,
                "Made by " + cfg.author +
                " - enjoy building your content machine.",
                f.chrome("subtitle"))
    row += 2

    for label, target in NAV_LINKS:
        sheet.merge(row, 0, 2, "", f.chrome("nav"))
        sheet.ws.write_url(row, 0, f"internal:'{target}'!A1",
                           f.chrome("nav"), f"> {label}")
        row += 1

    sheet.finish(freeze_row=4, print_area=f"A1:{chr(65 + LAST_COL)}{row}")
    return sheet
