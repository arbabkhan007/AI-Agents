"""
Print Week - a weekly meal plan for the fridge door.

Set the week at the top and print.  The page is laid out to fit one sheet of
A4 in portrait: seven days, three meals and the snacks, with the calories
and the cost of the week at the bottom.
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
        subtitle="A weekly meal plan for the fridge door",
        columns=[
            Col("label", " ", 18, "text"),
            Col("value", "Value", 16, "text"),
            Col("day", "Day", 12, "calc"),
            Col("date", "Date", 12, "calc"),
            Col("breakfast", "Breakfast", 26, "calc"),
            Col("lunch", "Lunch", 26, "calc"),
            Col("dinner", "Dinner", 26, "calc"),
            Col("snacks", "Snacks", 20, "calc"),
            Col("servings", "Servings", 10, "calc"),
            Col("notes", "Notes", 22, "calc"),
        ],
        rows=7,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 9, "WEEKLY MEAL PLAN", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 9,
                   "Stick this on the fridge - one page, one week",
                   f["subtitle"])
    ws.set_row(2, 22)
    ws.write(2, 0, "Week starting", f["label"])
    ws.write_string(2, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(2, 3, "Household", f["label"])
    ws.write_formula(2, 4, "=Household_Name", f["calc_text"])
    ws.write(2, 6, "People", f["label"])
    ws.write_formula(2, 7, "=Household_Size", f["calc_number"])
    ws.write(2, 9, "Budget", f["label"])
    ws.write_formula(2, 10, "=Weekly_Budget", f["calc_money"])
    ws.write_formula(3, 1, "=DATEVALUE($B$3)", f["calc_date"])

    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")

    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, head in enumerate(["", "", "Day", "Date", "Breakfast", "Lunch",
                              "Dinner", "Snacks", "Calories", "Cost"]):
        ws.write(hrow, i, head, f["header"])

    for offset in range(7):
        row = spec.first_data_row + offset
        r = row + 1
        ws.write_formula(row, 2, f'=TEXT($B$4+{offset},"dddd")',
                         f["calc_bold"])
        ws.write_formula(row, 3, f'=$B$4+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack"]):
            ws.write_formula(
                row, 4 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$D{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 8, f'=SUMIFS({mp_cal},{mp_date},$D{r})',
                         f["calc_number"])
        ws.write_formula(row, 9, f'=SUMIFS({mp_cost},{mp_date},$D{r})',
                         f["calc_money"])
        ws.set_row(row, 26)

    total = spec.last_data_row
    ws.write(total, 2, "Week", f["total_label"])
    for i in (3, 4, 5, 6, 7):
        ws.write_blank(total, i, None, f["total_label"])
    ws.write_formula(total, 8, f'=SUM($I${spec.first_data_row + 1}:'
                               f'$I${spec.last_data_row})',
                     f["total_number"])
    ws.write_formula(total, 9, f'=SUM($J${spec.first_data_row + 1}:'
                               f'$J${spec.last_data_row})',
                     f["total_money"])

    ws.set_tab_color(Palette.accent)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.5, 0.5, 0.6, 0.6)
    ws.center_horizontally()
    ws.set_header(f"&L&\"Calibri,Bold\"{cfg.product_name}"
                  f"&R&\"Calibri,Italic\"Weekly meal plan")
    ws.set_footer("&L&D&RPage &P of &N")
    ws.print_area(0, 0, total, 9)
    ws.hide_gridlines(2)
