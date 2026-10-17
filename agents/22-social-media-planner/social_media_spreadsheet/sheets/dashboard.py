"""The `Dashboard` tab - the one screen you look at every morning."""

from __future__ import annotations

from ..writer import NAV_LINKS, SheetWriter

NAME = "Dashboard"
LAST_COL = 11      # A..L

PLATFORMS = ["Instagram", "TikTok", "Pinterest", "YouTube", "Facebook",
             "Newsletter", "Blog"]


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#2E7D8F")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Dashboard",
                 f"{cfg.brand.name}  |  Week of the report date  |  "
                 f"Everything below counts itself from your tabs.",
                 LAST_COL)

    for col in range(0, LAST_COL + 1):
        sheet.set_col(col, col, 12)
    sheet.set_col(0, 0, 13)

    row = 4
    row = sheet.section(row, "This week at a glance", LAST_COL)
    week_row = row

    tiles_a = [
        ("Posts this week",
         "=COUNTIFS([[Content Calendar.date]],\">=\"&Window_Start,"
         "[[Content Calendar.date]],\"<=\"&Window_End)",
         "int", "In the 7 day window"),
        ("Waiting to go live",
         "=COUNTIFS([[Content Calendar.status]],\"<>Posted\","
         "[[Content Calendar.date]],\"<\"&Report_Date,"
         "[[Content Calendar.date]],\">0\")",
         "int", "Dated and still not posted"),
        ("Posted (all time)",
         "=COUNTIF([[Content Calendar.status]],\"Posted\")",
         "int", "Rows marked Posted"),
        ("Avg engagement",
         "=IF(COUNT([[Performance.engagement_rate]])=0,0,"
         "AVERAGE([[Performance.engagement_rate]]))",
         "percent", "Across all measured posts"),
    ]
    for i, (label, formula, style, note) in enumerate(tiles_a):
        sheet.kpi(row, i * 3, label, formula, style=style, span=3, note=note)
    row += 3

    tiles_b = [
        ("Total reach",
         "=SUM([[Analytics.reach]])", "int", "From the Analytics tab"),
        ("Total impressions",
         "=SUM([[Analytics.impressions]])", "int", "From the Analytics tab"),
        ("Est. revenue",
         "=SUM([[Performance.est_revenue]])", "money",
         "Clicks x average order value"),
        ("Open tasks",
         "=COUNTIF([[Tasks.status]],\"To Do\")+COUNTIF([[Tasks.status]],"
         "\"In Progress\")", "int", "Not done yet"),
    ]
    for i, (label, formula, style, note) in enumerate(tiles_b):
        sheet.kpi(row, i * 3, label, formula, style=style, span=3, note=note)
    row += 4

    # ---------------------------------------------------- platform scoreboard
    row = sheet.section(row, "Platform scoreboard", LAST_COL)
    headers = ["Platform", "Posts", "Followers", "Avg engagement",
               "Ad spend"]
    spans = [(0, 1), (2, 3), (4, 5), (6, 7), (8, LAST_COL)]
    for (c0, c1), head in zip(spans, headers):
        sheet.merge(row, c0, c1, head, f.chrome("header"))
    row += 1
    for platform in PLATFORMS:
        fmt_label = f.cell("text", "plain")
        fmt_int = f.cell("int", "calc")
        fmt_pct = f.cell("percent", "calc")
        fmt_money = f.cell("money", "calc")
        sheet.merge(row, 0, 1, platform, fmt_label)
        sheet.merge(row, 2, 3, "", fmt_int)
        sheet.ws.write_formula(
            row, 2,
            reg.render("=COUNTIF([[Content Calendar.platforms]],"
                       f"\"*\"&$A{row + 1}&\"*\")"), fmt_int)
        sheet.merge(row, 4, 5, "", fmt_int)
        sheet.ws.write_formula(
            row, 4,
            reg.render("=SUMIFS([[Accounts.followers]],"
                       "[[Accounts.platform]],$A" + str(row + 1) + ","
                       "[[Accounts.status]],\"Active\")"), fmt_int)
        sheet.merge(row, 6, 7, "", fmt_pct)
        sheet.ws.write_formula(
            row, 6,
            reg.render("=IFERROR(AVERAGEIFS([[Performance.engagement_rate]],"
                       "[[Performance.platform]],$A" + str(row + 1) + "),0)"),
            fmt_pct)
        sheet.merge(row, 8, LAST_COL, "", fmt_money)
        sheet.ws.write_formula(
            row, 8,
            reg.render("=SUMIFS([[Budget.spent]],[[Budget.channel]],"
                       "$A" + str(row + 1) + ")"), fmt_money)
        row += 1

    row += 1

    # ------------------------------------------- queue + campaigns, side by side
    left = sheet.section(row, "Next up in the queue", 5)
    right = sheet.section(row, "Campaign health", LAST_COL, first_col=6)
    q_row = left
    c_row = right
    for (c0, c1), head in zip([(0, 2), (3, 3), (4, 5)],
                              ["Post", "Date", "Status"]):
        sheet.merge(q_row, c0, c1, head, f.chrome("header"))
    for (c0, c1), head in zip([(6, 8), (9, 9), (10, LAST_COL)],
                              ["Campaign", "Budget", "Health"]):
        sheet.merge(c_row, c0, c1, head, f.chrome("header"))
    q_row += 1
    c_row += 1

    # Queue: earliest five unposted rows via the hidden queue_key.
    cal = reg["Content Calendar"]
    qk = reg.rng("Content Calendar", "queue_key")
    title_rng = reg.rng("Content Calendar", "title")
    date_rng = reg.rng("Content Calendar", "date")
    status_rng = reg.rng("Content Calendar", "status")
    for n in range(1, 6):
        fmt_label = f.cell("text", "calc")
        fmt_date = f.cell("date", "calc")
        fmt_text = f.cell("text", "calc")
        sheet.merge(q_row, 0, 2, "", fmt_label)
        sheet.ws.write_formula(
            q_row, 0,
            reg.render(f"=IFERROR(INDEX({title_rng},MATCH(SMALL({qk},{n}),"
                       f"{qk},0)),\"\")"), fmt_label)
        sheet.write(q_row, 3, None, fmt_date)
        sheet.ws.write_formula(
            q_row, 3,
            reg.render(f"=IFERROR(INDEX({date_rng},MATCH(SMALL({qk},{n}),"
                       f"{qk},0)),\"\")"), fmt_date)
        sheet.merge(q_row, 4, 5, "", fmt_text)
        sheet.ws.write_formula(
            q_row, 4,
            reg.render(f"=IFERROR(INDEX({status_rng},MATCH(SMALL({qk},{n}),"
                       f"{qk},0)),\"\")"), fmt_text)
        q_row += 1

    cmp = reg["Campaigns"]
    ck = reg.rng("Campaigns", "rank_key")
    name_rng = reg.rng("Campaigns", "name")
    budget_rng = reg.rng("Campaigns", "budget")
    health_rng = reg.rng("Campaigns", "health")
    for n in range(1, 6):
        fmt_label = f.cell("text", "calc")
        fmt_money = f.cell("money", "calc")
        sheet.merge(c_row, 6, 8, "", fmt_label)
        sheet.ws.write_formula(
            c_row, 6,
            reg.render(f"=IFERROR(INDEX({name_rng},MATCH(SMALL({ck},{n}),"
                       f"{ck},0)),\"\")"), fmt_label)
        sheet.write(c_row, 9, None, fmt_money)
        sheet.ws.write_formula(
            c_row, 9,
            reg.render(f"=IFERROR(INDEX({budget_rng},MATCH(SMALL({ck},{n}),"
                       f"{ck},0)),\"\")"), fmt_money)
        sheet.merge(c_row, 10, LAST_COL, "", fmt_label)
        sheet.ws.write_formula(
            c_row, 10,
            reg.render(f"=IFERROR(INDEX({health_rng},MATCH(SMALL({ck},{n}),"
                       f"{ck},0)),\"\")"), fmt_label)
        c_row += 1

    row = max(q_row, c_row) + 1

    # ------------------------------------------------------------- the funnel
    row = sheet.section(row, "The content funnel", LAST_COL)
    funnel = [
        ("Ideas captured", "=COUNTIF([[Idea Bank.idea]],\"?*\")",
         "Every spark in the Idea Bank"),
        ("Scheduled posts", "=COUNT([[Content Calendar.date]])",
         "Dated calendar rows"),
        ("Published", "=COUNTIF([[Content Calendar.status]],\"Posted\")",
         "Status = Posted"),
        ("High performers",
         "=COUNTIF([[Performance.engagement_rate]],\">0.05\")",
         "Posts above 5% engagement"),
        ("Repurposed", "=COUNTIF([[Repurposing.status]],\"Done\")",
         "Second lives created"),
    ]
    for i, (label, formula, note) in enumerate(funnel):
        sheet.kpi(row, i * 2 if i < 5 else 0, label, formula, style="int",
                  span=2 if i < 5 else 2, note=note)
        if i == 2:
            pass
    row += 3

    # 5 tiles of span 2 cover columns 0..9; fill 10..11 with the last note.
    sheet.merge(row, 10, LAST_COL,
                "Read the funnel top to bottom: if ideas dry up, the "
                "calendar starves in a month.",
                f.chrome("note"))
    sheet.row_height(row, 26)

    sheet.finish(freeze_row=4,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet
