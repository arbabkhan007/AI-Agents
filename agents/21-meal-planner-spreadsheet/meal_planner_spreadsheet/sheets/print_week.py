"""
Print Week - the week on one page, ready for the fridge door.

Set the week at the top and print.  Everything on the page is calculated
from the Meal Plan tab, so it is always in step with your plan.
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
        name="Print Week",
        title="Print Week",
        subtitle="The week on one page, ready for the fridge door",
        columns=[
            Col("day", "Day", 12, "calc"),
            Col("date", "Date", 11, "calc"),
            Col("breakfast", "Breakfast", 24, "calc"),
            Col("lunch", "Lunch", 24, "calc"),
            Col("dinner", "Dinner", 26, "calc"),
            Col("snacks", "Snacks", 20, "calc"),
            Col("calories", "Calories", 10, "calc"),
            Col("cost", "Cost", 10, "calc"),
            Col("notes", "Notes", 22, "calc"),
        ],
        rows=7,
        header_row=8,
        tab_color=Palette.primary,
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
    ws.merge_range(0, 0, 0, 8, "WEEKLY MEAL PLAN", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "Print this page and stick it on the fridge", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 8,
                   "  |  Dashboard   |   Weekly Planner   |   Print "
                   "Shopping   |   Print Recipe", f["nav"])

    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 8, "  WHICH WEEK?", f["section"])
    ws.write(5, 0, "Week starting", f["label"])
    ws.write_string(5, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(5, 3, "Household", f["label"])
    ws.write_formula(5, 4, "=Household_Name", f["calc_text"])
    ws.write(5, 6, "People", f["label"])
    ws.write_formula(5, 7, "=Household_Size", f["calc_number"])
    ws.write(5, 8, None, f["calc_text"])
    ws.write_formula(6, 1, "=DATEVALUE($B$6)", f["calc_date"])
    ws.write(6, 3, "Budget", f["label"])
    ws.write_formula(6, 4, "=Weekly_Budget", f["calc_money"])
    ws.write(6, 6, "Week cost", f["label"])
    ws.write_formula(6, 7, f'=SUMIFS({mp_cost},'
                          f'{reg.rng("Meal Plan", "week_start")},$B$7)',
                     f["calc_money"])

    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, col in enumerate(spec.columns):
        ws.write(hrow, i, col.header, f["header"])

    for offset in range(7):
        row = spec.first_data_row - 1 + offset   # 0-based writer row
        r = row + 1
        ws.write_formula(row, 0, f'=TEXT($B$7+{offset},"dddd")',
                         f["calc_bold"])
        ws.write_formula(row, 1, f'=$B$7+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack"]):
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$B{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 6, f'=SUMIFS({mp_cal},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 7, f'=SUMIFS({mp_cost},{mp_date},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 8,
                         f'=IF(COUNTIFS({mp_date},$B{r})=0,"",'
                         f'TEXT(COUNTIFS({mp_date},$B{r}),"0")&" meals")',
                         f["calc_text"])
        ws.set_row(row, 26)

    total_row = spec.last_data_row
    tr = total_row + 1
    ws.write(total_row, 0, "Week", f["total_label"])
    for i in range(1, 6):
        ws.write_blank(total_row, i, None, f["total_label"])
    ws.write_formula(total_row, 6, f'=SUM($G${spec.first_data_row}:'
                                   f'$G${total_row})', f["total_number"])
    ws.write_formula(total_row, 7, f'=SUM($H${spec.first_data_row}:'
                                   f'$H${total_row})', f["total_money"])
    ws.write_formula(total_row, 8,
                     f'=TEXT(COUNTIFS(' + reg.rng("Meal Plan", "week_start")
                     + ',$B$7),"0")&" meals planned"', f["total_label"])

    writer.write_note(ws, total_row + 2, 0,
                      "Shopping list too? Print the Print Shopping tab the "
                      "same way.", width=8)

    ws.freeze_panes(spec.header_row, 2)
    ws.set_tab_color(Palette.primary)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, total_row + 3, 8)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
