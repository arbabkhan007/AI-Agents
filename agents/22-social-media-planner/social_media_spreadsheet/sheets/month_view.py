"""The `Month View` tab - a real month wall, built from calendar rows.

Each day shows up to two posts (plus a 'more' count). The lookups use the
Content Calendar's hidden ``day_nth_key`` column - a TEXT key of the date
plus the nth post that day - so the whole page works with plain MATCH,
no dynamic arrays, no CSE.
"""

from __future__ import annotations

from ..writer import SheetWriter, number_check

NAME = "Month View"
LAST_COL = 7        # A spacer + B..H Mon..Sun

DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
BLOCKS = 6
ROWS_PER_BLOCK = 3  # day header + 2 content rows


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#2E7D8F")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Month View",
                 "The calendar as a wall planner. Set the month up top - "
                 "every block fills itself from the Content Calendar.",
                 LAST_COL)

    sheet.set_col(0, 0, 2)
    for col in range(1, 8):
        sheet.set_col(col, col, 17)

    cal = reg["Content Calendar"]
    title_rng = (f"[[Content Calendar.title]]")
    nth_rng = "[[Content Calendar.nth_key]]"
    date_rng = "[[Content Calendar.date]]"

    row = 4
    sheet.merge(row, 0, 2, "Viewing:", f.chrome("label_bold"))
    sheet.write(row, 3, cfg.today.year, f.input("int"))
    sheet.ws.data_validation(row, 3, row, 3, number_check(2020, 2100,
                                                          decimal=False))
    sheet.write(row, 4, cfg.today.month, f.input("int"))
    sheet.ws.data_validation(row, 4, row, 4, number_check(1, 12,
                                                          decimal=False))
    sheet.merge(row, 5, LAST_COL,
                "Year and month number are yours - the grid below follows.",
                f.chrome("note"))
    year_cell = f"$D${row + 1}"
    month_cell = f"$E${row + 1}"
    row += 1

    # Month title
    sheet.merge(row, 0, LAST_COL, "", f.chrome("print_title"))
    sheet.ws.write_formula(
        row, 0,
        f"=TEXT(DATE({year_cell},{month_cell},1),\"mmmm yyyy\")"
        f"&\" - \"&COUNTIFS({date_rng},\">=\"&DATE({year_cell},{month_cell},1),"
        f"{date_rng},\"<\"&DATE({year_cell},{month_cell}+1,1))&\" posts planned\"",
        f.chrome("print_title"))
    sheet.row_height(row, 24)
    row += 1

    # Weekday headers
    for i, day in enumerate(DOW):
        sheet.write(row, 1 + i, day, f.chrome("header"))
    sheet.row_height(row, 18)
    row += 1

    # Day blocks
    for block in range(BLOCKS):
        for i in range(7):
            offset = block * 7 + i
            date_expr = (f"(DATE({year_cell},{month_cell},1)"
                         f"-WEEKDAY(DATE({year_cell},{month_cell},1),2)"
                         f"+1+{offset})")
            col = 1 + i

            # Day header: day number for days in this month.
            fmt_day = f.chrome("day_number")
            sheet.write(row, col, None, fmt_day)
            sheet.ws.write_formula(
                row, col,
                f"=IF(MONTH({date_expr})={month_cell},DAY({date_expr}),\"\")",
                fmt_day)

            # Up to two posts + a count on the second line.
            fmt_item = f.chrome("day_item")
            sheet.row_height(row + 1, 30)
            sheet.write(row + 1, col, None, fmt_item)
            sheet.ws.write_formula(
                row + 1, col,
                sheet.reg.render(
                    f"=IFERROR(INDEX({title_rng},MATCH(TEXT({date_expr},"
                    f"\"0\")&\"#1\",{nth_rng},0)),\"\")"),
                fmt_item)
            sheet.row_height(row + 2, 30)
            sheet.write(row + 2, col, None, fmt_item)
            sheet.ws.write_formula(
                row + 2, col,
                sheet.reg.render(
                    f"=IF(COUNTIFS({date_rng},{date_expr})>2,"
                    f"IFERROR(INDEX({title_rng},MATCH(TEXT({date_expr},"
                    f"\"0\")&\"#2\",{nth_rng},0))&\" +\"&(COUNTIFS("
                    f"{date_rng},{date_expr})-2)&\" more\",\"\"),"
                    f"IFERROR(INDEX({title_rng},MATCH(TEXT({date_expr},"
                    f"\"0\")&\"#2\",{nth_rng},0)),\"\"))"),
                fmt_item)
        row += ROWS_PER_BLOCK

    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Two lines fit on a wall planner by design: the second "
                "line tucks a '+n more' count behind it. The Content "
                "Calendar holds the full list.",
                f.chrome("note"))
    sheet.row_height(row, 26)

    sheet.finish(freeze_row=6,
                 print_area=f"A1:{chr(65 + LAST_COL)}{row + 1}")
    return sheet
