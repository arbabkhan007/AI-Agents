"""
Monthly Planner - the whole month on one page.

Set the month at the top and the six weeks of that month are laid out with
a theme for each week, what the planned meals cost, what you actually spent
and how that compares with the weekly budget.  It is the page to look at
when you are deciding whether next month needs a cheaper plan.
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
        name="Monthly Planner",
        title="Monthly Planner",
        subtitle="The whole month on one page - themes, planned cost and "
                 "actual spend",
        columns=[
            Col("week", "Week", 10, "calc"),
            Col("week_start", "Week starting", 13, "calc"),
            Col("breakfast_theme", "Breakfast theme", 22, "text"),
            Col("lunch_theme", "Lunch theme", 22, "text"),
            Col("dinner_theme", "Dinner theme", 24, "text"),
            Col("planned_cost", "Planned cost", 12, "calc"),
            Col("actual_cost", "Actual spend", 12, "calc"),
            Col("budget", "Budget", 12, "calc"),
            Col("variance", "Variance", 11, "calc"),
            Col("notes", "Notes", 30, "text_wrap"),
        ],
        rows=6,
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
    ws.merge_range(0, 0, 0, 9, "MONTHLY PLANNER", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 9,
                   "The whole month on one page - themes, planned cost and "
                   "actual spend", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 9,
                   "  |  Dashboard   |   Weekly Planner   |   Meal Plan   |   "
                   "Grocery Spending   |   Budget", f["nav"])

    mp_week = reg.rng("Meal Plan", "week_start")
    mp_cost = reg.rng("Meal Plan", "cost")
    gs_week = reg.rng("Grocery Spending", "week_start")
    gs_total = reg.rng("Grocery Spending", "line_total")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 9, "  WHICH MONTH?", f["section"])
    ws.write(5, 0, "Month", f["label"])
    ws.write_string(5, 1, cfg.today.strftime("%B %Y"), f["input_text"])
    ws.write(5, 3, "Weeks in the month", f["label"])
    ws.write_formula(5, 4, '=6', f["calc_number"])
    ws.write(5, 6, "Monthly budget", f["label"])
    ws.write_formula(5, 7, "=Monthly_Budget", f["calc_money"])
    ws.write_formula(6, 1, '=DATEVALUE("1 "&$B$6)', f["calc_date"])
    ws.write(6, 3, "Month planned", f["label"])
    ws.write_formula(6, 4, f'=SUM($F$9:$F$14)', f["calc_money"])
    ws.write(6, 6, "Month actual", f["label"])
    ws.write_formula(6, 7, f'=SUM($G$9:$G$14)', f["calc_money"])
    ws.write(6, 9, "Variance", f["label"])
    ws.write_formula(6, 10, '=$E$7-$H$7', f["calc_money"])

    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, col in enumerate(spec.columns):
        ws.write(hrow, i, col.header, f["header"])

    for offset in range(6):
        row = spec.first_data_row - 1 + offset   # 0-based writer row
        r = row + 1
        ws.write_number(row, 0, offset + 1, f["calc_center"])
        ws.write_formula(row, 1,
                         f'=$B$7+{offset}*7-WEEKDAY($B$7,2)+1',
                         f["calc_date"])
        ws.write_blank(row, 2, None, f["input_text"])
        ws.write_blank(row, 3, None, f["input_text"])
        ws.write_blank(row, 4, None, f["input_text"])
        ws.write_formula(row, 5, f'=SUMIFS({mp_cost},{mp_week},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 6, f'=SUMIFS({gs_total},{gs_week},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 7, "=Weekly_Budget", f["calc_money"])
        ws.write_formula(row, 8, f'=$H{r}-$G{r}', f["calc_money"])
        ws.write_blank(row, 9, None, f["input_text_wrap"])
        ws.set_row(row, 22)

    total_row = spec.last_data_row
    ws.write(total_row, 0, "Month", f["total_label"])
    for i in range(1, 5):
        ws.write_blank(total_row, i, None, f["total_label"])
    ws.write_formula(total_row, 5, f'=SUM($F$9:$F${total_row})',
                     f["total_money"])
    ws.write_formula(total_row, 6, f'=SUM($G$9:$G${total_row})',
                     f["total_money"])
    ws.write_formula(total_row, 7, f'=SUM($H$9:$H${total_row})',
                     f["total_money"])
    ws.write_formula(total_row, 8, f'=$H{total_row + 1}-$G{total_row + 1}',
                     f["total_money"])
    ws.write_formula(total_row, 9,
                     f'=IF($H{total_row + 1}=0,"",'
                     f'TEXT(($G{total_row + 1}-$H{total_row + 1})/'
                     f'$H{total_row + 1},"0%")&" of budget left")',
                     f["total_label"])

    ws.freeze_panes(spec.header_row, 2)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, total_row, 9)
