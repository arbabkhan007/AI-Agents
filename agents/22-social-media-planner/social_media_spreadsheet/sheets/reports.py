"""The `Reports` tab - the copy-and-send monthly report."""

from __future__ import annotations

from ..writer import NAV_LINKS, SheetWriter

NAME = "Reports"
LAST_COL = 7

MONTHS_ROW_LABELS = ["Mar-26", "Apr-26", "May-26", "Jun-26"]


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#2E7D8F")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Monthly Report",
                 f"{cfg.brand.name}  |  Numbers pulled live from the workbook - "
                 f"write the story beside them and send.",
                 LAST_COL)

    sheet.set_col(0, 0, 3)
    sheet.set_col(1, 1, 26)
    sheet.set_col(2, 3, 13)
    sheet.set_col(4, 5, 13)
    sheet.set_col(6, LAST_COL, 14)

    row = 4
    row = sheet.section(row, "The headline numbers", LAST_COL)
    kpis = [
        ("Posts published",
         "=COUNTIF([[Content Calendar.status]],\"Posted\")", "int"),
        ("Total reach", "=SUM([[Analytics.reach]])", "int"),
        ("Avg engagement",
         "=IF(COUNT([[Performance.engagement_rate]])=0,0,"
         "AVERAGE([[Performance.engagement_rate]]))", "percent"),
        ("Emails sent",
         "=COUNTIFS([[Content Calendar.platforms]],\"*Newsletter*\","
         "[[Content Calendar.status]],\"Posted\")", "int"),
    ]
    for i, (label, formula, style) in enumerate(kpis):
        sheet.kpi(row, i * 2 if i < 4 else 0, label, formula, style=style,
                  span=2, note="")
    row += 3

    # ---------------------------------------------- platform scorecard table
    row = sheet.section(row, "Platform scorecard", LAST_COL)
    for (c0, c1), head in zip([(0, 1), (2, 2), (3, 3), (4, 4), (5, 5),
                               (6, LAST_COL)],
                              ["Platform", "Posts", "Followers",
                               "Engagement", "Ad spend", "Note"]):
        sheet.merge(row, c0, c1, head, f.chrome("header"))
    row += 1
    notes = {
        "Instagram": "Flagship - watch saves",
        "TikTok": "Reach engine",
        "Pinterest": "Evergreen clicks",
        "YouTube": "Monthly vlog",
        "Facebook": "Local + events",
        "Newsletter": "Highest intent",
        "Blog": "Feeds the pins",
    }
    for platform, note in notes.items():
        fmt_label = f.cell("text", "plain")
        fmt_int = f.cell("int", "calc")
        fmt_pct = f.cell("percent", "calc")
        fmt_money = f.cell("money", "calc")
        sheet.merge(row, 0, 1, platform, fmt_label)
        sheet.write(row, 2, None, fmt_int)
        sheet.ws.write_formula(row, 2, sheet.reg.render(
            "=COUNTIF([[Content Calendar.platforms]],\"*\"&$A"
            + str(row + 1) + "&\"*\")"), fmt_int)
        sheet.write(row, 3, None, fmt_int)
        sheet.ws.write_formula(row, 3, sheet.reg.render(
            "=SUMIFS([[Accounts.followers]],[[Accounts.platform]],$A"
            + str(row + 1) + ",[[Accounts.status]],\"Active\")"), fmt_int)
        sheet.write(row, 4, None, fmt_pct)
        sheet.ws.write_formula(row, 4, sheet.reg.render(
            "=IFERROR(AVERAGEIFS([[Performance.engagement_rate]],"
            "[[Performance.platform]],$A" + str(row + 1) + "),0)"), fmt_pct)
        sheet.write(row, 5, None, fmt_money)
        sheet.ws.write_formula(row, 5, sheet.reg.render(
            "=SUMIFS([[Budget.spent]],[[Budget.channel]],$A"
            + str(row + 1) + ")"), fmt_money)
        sheet.merge(row, 6, LAST_COL, note, f.chrome("note"))
        row += 1

    row += 1

    # ------------------------------------------------- content pillar table
    row = sheet.section(row, "Content pillars - what carried the month",
                        LAST_COL)
    for (c0, c1), head in zip([(0, 1), (2, 3), (4, 5), (6, LAST_COL)],
                              ["Pillar", "Posted", "Avg engagement",
                               "Read"]):
        sheet.merge(row, c0, c1, head, f.chrome("header"))
    row += 1
    reads = ["Show the making - it earns the saves",
             "Product posts convert when the story is warm",
             "Personal posts build the relationship",
             "Teach generously - saves compound",
             "Social proof - ask every customer",
             "Keep it rare so it stays exciting"]
    pillars = (sample_pillars() if cfg.include_sample_data else
               ["Pillar " + str(i + 1) for i in range(6)])
    for pillar, read in zip(pillars, reads):
        fmt_label = f.cell("text", "plain")
        fmt_int = f.cell("int", "calc")
        fmt_pct = f.cell("percent", "calc")
        sheet.merge(row, 0, 1, pillar, fmt_label)
        sheet.merge(row, 2, 3, "", fmt_int)
        sheet.ws.write_formula(row, 2, sheet.reg.render(
            "=COUNTIFS([[Content Calendar.pillar]],$A" + str(row + 1)
            + ",[[Content Calendar.status]],\"Posted\")"), fmt_int)
        sheet.merge(row, 4, 5, "", fmt_pct)
        sheet.ws.write_formula(row, 4, sheet.reg.render(
            "=IFERROR(AVERAGEIFS([[Performance.engagement_rate]],"
            "[[Performance.pillar]],$A" + str(row + 1) + "),0)"), fmt_pct)
        sheet.merge(row, 6, LAST_COL, read, f.chrome("note"))
        row += 1

    row += 1

    # ---------------------------------------------------- month trend table
    row = sheet.section(row, "Month by month", LAST_COL)
    for (c0, c1), head in zip([(0, 1), (2, 3), (4, 5), (6, LAST_COL)],
                              ["Month", "Posted", "Est. revenue", "Trend"]):
        sheet.merge(row, c0, c1, head, f.chrome("header"))
    row += 1
    for month in MONTHS_ROW_LABELS:
        fmt_label = f.cell("text", "plain")
        fmt_int = f.cell("int", "calc")
        fmt_money = f.cell("money", "calc")
        fmt_text = f.cell("text", "calc")
        sheet.merge(row, 0, 1, month, fmt_label)
        # Month window as real dates from the label text ('1-Mar-26').
        bounds = ("DATEVALUE(\"1-\"&$A" + str(row + 1) + "),"
                  "EDATE(DATEVALUE(\"1-\"&$A" + str(row + 1) + "),1)")
        sheet.merge(row, 2, 3, "", fmt_int)
        sheet.ws.write_formula(row, 2, sheet.reg.render(
            "=COUNTIFS([[Content Calendar.status]],\"Posted\","
            "[[Content Calendar.date]],\">=\"&" + bounds.split(",")[0] + ","
            "[[Content Calendar.date]],\"<\"&" + bounds.split(",")[1]),
            fmt_int)
        sheet.merge(row, 4, 5, "", fmt_money)
        sheet.ws.write_formula(row, 4, sheet.reg.render(
            "=SUMIFS([[Performance.est_revenue]],[[Performance.date]],"
            "\">=\"&" + bounds.split(",")[0] + ",[[Performance.date]],"
            "\"<\"&" + bounds.split(",")[1]), fmt_money)
        sheet.merge(row, 6, LAST_COL, "", fmt_text)
        sheet.ws.write_formula(row, 6, sheet.reg.render(
            "=IF($E" + str(row + 1) + "=0,\"Quiet\",\"Revenue logged\")"),
            fmt_text)
        row += 1

    row += 1

    # ------------------------------------------------- narrative write-in box
    row = sheet.section(row, "The story (write it here)", LAST_COL)
    prompts = [
        "What worked - and why do we think so?",
        "What did not - what will we change?",
        "Audience notes - what are people asking for?",
        "Next month's focus - one sentence.",
    ]
    for prompt in prompts:
        sheet.merge(row, 0, 1, prompt, f.chrome("label_bold"))
        sheet.merge(row, 2, LAST_COL, "", f.input("wrap"))
        sheet.row_height(row, 40)
        row += 1

    row += 1
    row = sheet.section(row, "Copy this into an email", LAST_COL)
    sheet.merge(row, 0, LAST_COL, "", f.chrome("note_box"))
    sheet.ws.write_formula(row, 0, sheet.reg.render(
        "=\"Subject: \"&Setting_Brand&\" social report - \"&"
        "TEXT(Report_Date,\"mmmm yyyy\")&CHAR(10)&"
        "\"Hi team,\"&CHAR(10)&CHAR(10)&"
        "\"Published: \"&COUNTIF([[Content Calendar.status]],\"Posted\")&"
        "\" posts. Reach: \"&SUM([[Analytics.reach]])&"
        "\". Average engagement: \"&"
        "TEXT(AVERAGE([[Performance.engagement_rate]]),\"0.0%\")&\".\"&"
        "CHAR(10)&CHAR(10)&\"Full numbers in the planner.\""),
        f.chrome("note_box"))
    sheet.row_height(row, 80)
    row += 2

    for label, target in NAV_LINKS[:3]:
        sheet.merge(row, 0, 2, "", f.chrome("nav"))
        sheet.ws.write_url(row, 0, f"internal:'{target}'!A1",
                           f.chrome("nav"), f"> {label}")
        row += 1

    sheet.finish(freeze_row=4,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet


def sample_pillars():
    from .. import sample_data
    return [p["name"] for p in sample_data.pillars()]
