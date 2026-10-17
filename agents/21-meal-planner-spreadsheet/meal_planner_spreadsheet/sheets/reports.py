"""
Reports - the numbers behind the month.

Six ranked views of your data: the favourite recipes, the most expensive
dishes, the costliest things to throw away, where the money is going, the
aisles that eat the budget and how the meals are split across the week.
Pick the month at the top and everything updates.
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
        name="Reports",
        title="Reports",
        subtitle="The numbers behind the month - favourites, costs, waste "
                 "and habits",
        columns=[
            Col("rank", "Rank", 8, "calc"),
            Col("c1", "Label", 26, "calc"),
            Col("c2", "Value", 14, "calc"),
            Col("c3", "Extra", 14, "calc"),
            Col("c4", "Extra 2", 16, "calc"),
            Col("c5", "Extra 3", 14, "calc"),
            Col("c6", "Extra 4", 16, "calc"),
            Col("c7", "Extra 5", 18, "calc"),
        ],
        rows=6,
        header_row=8,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 8)
    ws.set_column(1, 1, 28)
    ws.set_column(2, 2, 15)
    ws.set_column(3, 3, 15)
    ws.set_column(4, 4, 17)
    ws.set_column(5, 5, 15)
    ws.set_column(6, 6, 17)
    ws.set_column(7, 7, 18)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 7, "REPORTS", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 7,
                   "The numbers behind the month - favourites, costs, waste "
                   "and habits", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 7,
                   "  |  Dashboard   |   Meal Plan   |   Grocery Spending   "
                   "|   Food Waste   |   Budget", f["nav"])

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 7, "  WHICH MONTH?", f["section"])
    ws.write(5, 0, "Month", f["label"])
    ws.write_string(5, 1, cfg.today.strftime("%b %Y"), f["input_text"])
    ws.write(5, 2, "Meals this month", f["label"])
    ws.write_formula(
        5, 3, '=COUNTIFS(' + reg.rng("Meal Plan", "month") + ',$B$6)',
        f["calc_number"])
    ws.write(5, 4, "Spend this month", f["label"])
    ws.write_formula(
        5, 5, '=SUMIFS(' + reg.rng("Grocery Spending", "line_total")
        + ',' + reg.rng("Grocery Spending", "month") + ',$B$6)',
        f["calc_money"])
    ws.write(5, 6, "Waste this month", f["label"])
    ws.write_formula(
        5, 7, '=SUMIFS(' + reg.rng("Food Waste", "cost")
        + ',' + reg.rng("Food Waste", "month") + ',$B$6)',
        f["calc_money"])

    # ---- ranked blocks -------------------------------------------------------
    row = 7
    blocks = [
        ("MOST COOKED RECIPES", ["Rank", "Recipe", "Times cooked",
                                 "Rating", "Last cooked",
                                 "Cost / serving", "Calories", "Cuisine"]),
        ("MOST EXPENSIVE DISHES", ["Rank", "Recipe", "Cost / serving",
                                   "Total cost", "Cost / 1000 kcal",
                                   "Servings", "Calories", "Category"]),
        ("BIGGEST WASTE", ["Rank", "Item", "Quantity", "Unit", "Cost binned",
                           "Reason", "Month", "Avoidable"]),
        ("WHERE THE MONEY GOES", ["Rank", "Store", "Total spend",
                                  "Average basket", "Shops", "Best for",
                                  "Delivers", "Distance (km)"]),
        ("MOST EXPENSIVE AISLES", ["Rank", "Aisle", "Spend", "Share",
                                   "Items", "Waste", "Stock", "Notes"]),
        ("MEALS BY SLOT", ["Rank", "Slot", "Meals planned", "Calories",
                           "Cost", "Average cost", "Average calories",
                           "Status"]),
    ]
    for title, headers in blocks:
        ws.set_row(row, 22)
        ws.merge_range(row, 0, row, 7, "  " + title, f["section"])
        row += 1
        for i, head in enumerate(headers):
            ws.write(row, i, head, f["header"])
        row += 1
        for n in range(1, 6):
            ws.write_number(row, 0, n, f["calc_center"])
            for i in range(1, 8):
                ws.write_blank(row, i, None, f["calc_text"])
            row += 1
        row += 1

    ws.write(row, 0, "Tips", f["total_label"])
    ws.merge_range(row, 1, row, 7,
                   "The ranking columns on the Recipes, Recipe Costs, Food "
                   "Waste, Stores, Ingredients and Meal Plan tabs power "
                   "these tables - use the MATCH formulas shown on those "
                   "tabs to pull the top rows into the blanks above.",
                   f["total_label"])
    row += 1

    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row, 7)


def _unused(writer, spec, reg):
    """Kept for reference: the MATCH formulas used to fill ranked blocks."""
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")
    return (mp_slot, mp_recipe, mp_cal, mp_cost)
