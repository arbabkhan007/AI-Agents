"""The `Annual Dashboard` tab - the year at a glance, month by month."""

from __future__ import annotations

from ..writer import SheetWriter

NAME = "Annual Dashboard"
LAST_COL = 14      # A+B label, C..N twelve months, O year total

MONTH_START = "DATE(Setting_Year,COLUMN()-2,1)"
MONTH_END = "DATE(Setting_Year,COLUMN()-1,1)"


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#2E7D8F")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Annual Dashboard",
                 f"{cfg.brand.name}  |  The whole {cfg.today.year} on one page - "
                 f"every column counts itself from your tabs.",
                 LAST_COL)

    sheet.set_col(0, 0, 3)
    sheet.set_col(1, 1, 22)
    sheet.set_col(2, LAST_COL, 10)

    row = 4
    row = sheet.section(row, "Year totals by month", LAST_COL)
    # Month header row (Excel row = row + 1). Labels are text like 'Mar-26'.
    header_row = row
    sheet.merge(row, 0, 1, "Metric", f.chrome("header"))
    for i, month in enumerate(cfg.MONTHS):
        sheet.write(row, 2 + i, month, f.chrome("header"))
    sheet.write(row, LAST_COL, "Year", f.chrome("header"))
    sheet.row_height(row, 24)
    row += 1

    cal = reg["Content Calendar"]
    perf = reg["Performance"]
    ana = reg["Analytics"]

    def ws_rng(sheet, key):
        letter = sheet.letter(key)
        return (f"'{sheet.name}'!${letter}${sheet.first_data_row}:"
                f"${letter}${sheet.last_data_row}")

    cal_date = ws_rng(cal, "date")
    cal_status = ws_rng(cal, "status")
    cal_platforms = ws_rng(cal, "platforms")
    perf_date = ws_rng(perf, "date")
    perf_rev = ws_rng(perf, "est_revenue")
    ana_date = ws_rng(ana, "date")
    ana_reach = ws_rng(ana, "reach")

    metrics = [
        ("Posts planned",
         f"=SUMPRODUCT(({cal_date}>={MONTH_START})*({cal_date}<{MONTH_END}))",
         "int"),
        ("Posts published",
         f"=SUMPRODUCT(({cal_date}>={MONTH_START})*({cal_date}<{MONTH_END})"
         f"*({cal_status}=\"Posted\"))", "int"),
        ("Instagram posts",
         f"=SUMPRODUCT(({cal_date}>={MONTH_START})*({cal_date}<{MONTH_END})"
         f"*ISNUMBER(SEARCH(\"Instagram\",{cal_platforms})))", "int"),
        ("TikTok posts",
         f"=SUMPRODUCT(({cal_date}>={MONTH_START})*({cal_date}<{MONTH_END})"
         f"*ISNUMBER(SEARCH(\"TikTok\",{cal_platforms})))", "int"),
        ("Pinterest pins",
         f"=SUMPRODUCT(({cal_date}>={MONTH_START})*({cal_date}<{MONTH_END})"
         f"*ISNUMBER(SEARCH(\"Pinterest\",{cal_platforms})))", "int"),
        ("Emails sent",
         f"=SUMPRODUCT(({cal_date}>={MONTH_START})*({cal_date}<{MONTH_END})"
         f"*ISNUMBER(SEARCH(\"Newsletter\",{cal_platforms})))", "int"),
        ("Budget spent",
         "=SUMIFS([[Budget.spent]],[[Budget.month]],"
         + "${col}${header})", "money"),
        ("Est. revenue",
         f"=SUMIFS({perf_rev},{perf_date},\">=\"&{MONTH_START},"
         f"{perf_date},\"<\"&{MONTH_END})", "money"),
        ("Reach (logged)",
         f"=SUMIFS({ana_reach},{ana_date},\">=\"&{MONTH_START},"
         f"{ana_date},\"<\"&{MONTH_END})", "int"),
    ]

    for label, formula, style in metrics:
        fmt_label = f.cell("text", "plain")
        fmt_cell = f.cell(style, "calc")
        sheet.merge(row, 0, 1, label, fmt_label)
        for i in range(12):
            col = 2 + i
            if "{col}" in formula:
                rendered = formula.replace("{col}", sheet.ws.col) \
                    if False else formula.replace(
                        "{col}", _col_letter(col)).replace(
                        "{header}", str(header_row + 1))
                sheet.ws.write_formula(row, col,
                                       sheet.reg.render(rendered), fmt_cell)
            else:
                sheet.ws.write_formula(row, col,
                                       sheet.reg.render(formula), fmt_cell)
        sheet.write(row, LAST_COL, None, fmt_cell)
        sheet.ws.write_formula(row, LAST_COL,
                               sheet.reg.render(f"=SUM(C{row + 1}:"
                                                f"N{row + 1})"), fmt_cell)
        row += 1

    row += 1
    row = sheet.section(row, "How the year is shaping up", LAST_COL)
    first_metric_row = header_row + 2   # 'Posts planned' row (Excel)
    planned = f"$C${first_metric_row}:$N${first_metric_row}"
    row = _insight(sheet, row, "Busiest month",
                   f"=INDEX($C${header_row + 1}:$N${header_row + 1},"
                   f"MATCH(MAX({planned}),{planned},0))", "text",
                   "Most posts planned in one month.")
    row = _insight(sheet, row, "Quietest month",
                   f"=INDEX($C${header_row + 1}:$N${header_row + 1},"
                   f"MATCH(MIN({planned}),{planned},0))", "text",
                   "The month to fill next.")
    total_row = first_metric_row + len(metrics) - 2   # Est. revenue row
    rev = f"$C${total_row}:$N${total_row}"
    row = _insight(sheet, row, "Best revenue month",
                   f"=INDEX($C${header_row + 1}:$N${header_row + 1},"
                   f"MATCH(MAX({rev}),{rev},0))", "text",
                   "Where the money actually came from.")
    row = _insight(sheet, row, "Posts planned for the year",
                   f"=SUM({planned})", "int",
                   "Across every platform and channel.")

    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Fill the calendar and this page rebuilds itself. Empty "
                "months are not failures - they are the plan talking to you.",
                f.chrome("note"))
    sheet.row_height(row, 26)

    sheet.finish(freeze_row=header_row + 1,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet


def _insight(sheet, row, label, formula, style, note):
    f = sheet.f
    fmt_label = f.chrome("label_bold")
    fmt_cell = f.cell(style, "calc")
    sheet.merge(row, 0, 2, label, fmt_label)
    sheet.merge(row, 3, 5, "", fmt_cell)
    sheet.ws.write_formula(row, 3, sheet.reg.render(formula), fmt_cell)
    sheet.merge(row, 6, LAST_COL, note, f.chrome("note"))
    return row + 1


def _col_letter(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters
