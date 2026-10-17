"""
Weekly Planner - one week, day by day.

Set the week at the top, then choose what you are having for breakfast,
lunch and dinner each day.  The planner reads the Meal Plan tab, so the
grid shows whatever you have planned there and works out the calories, the
protein and the cost of the whole week as you go.

Tip: the easiest way to fill this in is to plan on the Meal Plan tab - one
row per meal - and this page fills itself in.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Weekly Planner",
        title="Weekly Planner",
        subtitle="One week, day by day - meals, calories and cost",
        columns=[
            Col("day", "Day", 12, "calc"),
            Col("date", "Date", 12, "calc"),
            Col("breakfast", "Breakfast", 26, "calc"),
            Col("lunch", "Lunch", 26, "calc"),
            Col("dinner", "Dinner", 26, "calc"),
            Col("snack", "Snacks", 22, "calc"),
            Col("dessert", "Dessert", 20, "calc"),
            Col("servings", "Servings", 10, "calc"),
            Col("calories", "Calories", 11, "calc"),
            Col("cost", "Cost", 11, "calc"),
            Col("notes", "Notes", 30, "input_text"),
        ],
        rows=7,
        header_row=8,
        tab_color=Palette.accent,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 10, "WEEKLY PLANNER", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 10,
                   "One week, day by day - meals, calories and cost",
                   f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 10,
                   "  |  Dashboard   |   Meal Plan   |   Grocery List   |   "
                   "Print Week   |   Monthly Planner", f["nav"])

    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_serv = reg.rng("Meal Plan", "servings")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 10, "  WHICH WEEK?", f["section"])
    ws.write(5, 0, "Week starting", f["label"])
    ws.write_string(5, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(5, 3, "Household", f["label"])
    ws.write_formula(5, 4, "=Household_Name", f["calc_text"])
    ws.write(5, 6, "People", f["label"])
    ws.write_formula(5, 7, "=Household_Size", f["calc_number"])
    ws.write(5, 9, "Budget", f["label"])
    ws.write_formula(5, 10, "=Weekly_Budget", f["calc_money"])
    ws.write(6, 0, "Planned", f["label"])
    ws.write_formula(6, 1,
                     f'=COUNTIFS({reg.rng("Meal Plan", "week_start")},'
                     f'$B$8)&" meals this week"', f["calc_bold"])
    ws.write(6, 3, "Week cost", f["label"])
    ws.write_formula(6, 4, f'=SUMIFS({mp_cost},'
                           f'{reg.rng("Meal Plan", "week_start")},$B$8)',
                     f["calc_money"])
    ws.write(6, 6, "Budget left", f["label"])
    ws.write_formula(6, 7, f'=Weekly_Budget-$E$7', f["calc_money"])
    ws.write(6, 9, "Calories / day", f["label"])
    ws.write_formula(6, 10,
                     f'=IFERROR(SUMIFS({mp_cal},'
                     f'{reg.rng("Meal Plan", "week_start")},$B$8)/'
                     f'MAX(1,Household_Size)/7,0)', f["calc_number"])
    ws.write_formula(7, 1, "=DATEVALUE($B$6)", f["calc_date"])

    # ---- header row ---------------------------------------------------------
    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, col in enumerate(spec.columns):
        ws.write(hrow, i, col.header, f["header"])

    # ---- the seven days ------------------------------------------------------
    for offset in range(7):
        row = spec.first_data_row + offset
        r = row + 1                       # Excel row number
        ws.write_formula(row, 0, f'=TEXT($B$8+{offset},"dddd")',
                         f["calc_bold"])
        ws.write_formula(row, 1, f'=$B$8+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack", "Dessert"]):
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$B{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 7, f'=SUMIFS({mp_serv},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 8, f'=SUMIFS({mp_cal},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 9, f'=SUMIFS({mp_cost},{mp_date},$B{r})',
                         f["calc_money"])
        ws.write_blank(row, 10, None, f["input_text_wrap"])
        ws.set_row(row, 22)

    # ---- totals --------------------------------------------------------------
    total_row = spec.last_data_row
    tr = total_row + 1
    ws.write(total_row, 0, "Week total", f["total_label"])
    for i in range(1, 7):
        ws.write_blank(total_row, i, None, f["total_label"])
    ws.write_formula(total_row, 7, f'=SUM($H${spec.first_data_row + 1}:'
                                   f'$H${spec.last_data_row})',
                     f["total_number"])
    ws.write_formula(total_row, 8, f'=SUM($I${spec.first_data_row + 1}:'
                                   f'$I${spec.last_data_row})',
                     f["total_number"])
    ws.write_formula(total_row, 9, f'=SUM($J${spec.first_data_row + 1}:'
                                   f'$J${spec.last_data_row})',
                     f["total_money"])
    ws.write_formula(total_row, 10,
                     f'=IFERROR(TEXT($I{tr}/MAX(1,Household_Size)/7,'
                     f'"#,##0")&" kcal a day","")', f["total_label"])

    ws.freeze_panes(spec.header_row, 2)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, total_row, 10)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
