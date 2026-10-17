"""
Print Recipe - one recipe, in a layout you can cook from.

Pick a recipe at the top and the page shows the ingredients, the method and
the numbers in a big friendly layout.  Print it, prop it up and cook.
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
        name="Print Recipe",
        title="Print Recipe",
        subtitle="One recipe, in a layout you can cook from",
        columns=[
            Col("recipe", "Recipe", 24, "text"),
            Col("detail", "Detail", 18, "text"),
            Col("ingredient", "Ingredient", 24, "calc"),
            Col("quantity", "Quantity", 11, "calc"),
            Col("unit", "Unit", 11, "calc"),
            Col("preparation", "Preparation", 20, "calc"),
            Col("method", "Method", 60, "calc"),
            Col("note", "Notes", 24, "calc"),
        ],
        rows=20,
        header_row=14,
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
    ws.merge_range(0, 0, 0, 6, "RECIPE CARD", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 6,
                   "Pick a recipe, print it, prop it up and cook",
                   f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 6,
                   "  |  Recipes   |   Print Week   |   Print Shopping   |   "
                   " Converter", f["nav"])

    recipe = reg.rng("Recipes", "recipe")
    ri_recipe = reg.rng("Recipe Ingredients", "recipe")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 6, "  WHICH RECIPE?", f["section"])
    ws.write(5, 0, "Recipe", f["label"])
    ws.write_string(5, 1, "Chicken curry", f["input_select"])
    ws.data_validation(5, 1, 5, 1,
                       {"validate": "list", "source": "=" + recipe})
    ws.write(5, 2, "Servings", f["label"])
    ws.write_formula(5, 3,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "servings")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_number"])
    ws.write(5, 4, "Prep time", f["label"])
    ws.write_formula(5, 5,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "prep_time")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_number"])
    ws.write(5, 6, None, f["calc_text"])

    ws.write(7, 0, "Category", f["label"])
    ws.write_formula(7, 1,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "category")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_text"])
    ws.write(7, 2, "Total time", f["label"])
    ws.write_formula(7, 3,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "total_time")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_number"])
    ws.write(7, 4, "Calories", f["label"])
    ws.write_formula(7, 5,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "calories")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_number"])

    ws.write(8, 0, "Cost / serving", f["label"])
    ws.write_formula(8, 1,
                     '=IFERROR(INDEX(' + reg.rng("Recipes",
                                                 "cost_per_serving")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_money"])
    ws.write(8, 2, "Difficulty", f["label"])
    ws.write_formula(8, 3,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "difficulty")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_text"])
    ws.write(8, 4, "Protein", f["label"])
    ws.write_formula(8, 5,
                     '=IFERROR(INDEX(' + reg.rng("Recipes", "protein")
                     + ',MATCH($B$6,' + recipe + ',0)),"")',
                     f["calc_number"])

    ws.write(10, 0, "Ingredients", f["section"])
    ws.write(10, 2, "How to cook it", f["section"])

    hrow = spec.header_row - 1
    ws.set_row(hrow, 24)
    for i, head in enumerate(["", "", "Ingredient", "Quantity", "Unit",
                              "Preparation", "Method", ""]):
        if head:
            ws.write(hrow, i, head, f["header"])

    ri_qty = reg.rng("Recipe Ingredients", "quantity")
    ri_unit = reg.rng("Recipe Ingredients", "unit")
    ri_prep = reg.rng("Recipe Ingredients", "preparation")
    ri_ing = reg.rng("Recipe Ingredients", "ingredient")
    ri_line = reg.rng("Recipe Ingredients", "line_no")
    method = reg.rng("Recipes", "method")

    def pick(rng: str, n: int) -> str:
        return (f'=IFERROR(INDEX({rng},MATCH(1,INDEX('
                f'({ri_recipe}=$B$6)*({ri_line}={n}),0),0)),"")')

    for n in range(1, 21):
        row = spec.first_data_row + n - 1
        ws.write_formula(row, 2, pick(ri_ing, n), f["calc_text"])
        ws.write_formula(row, 3, pick(ri_qty, n), f["calc_number"])
        ws.write_formula(row, 4, pick(ri_unit, n), f["calc_text"])
        ws.write_formula(row, 5, pick(ri_prep, n), f["calc_text"])
        if n == 1:
            ws.write_formula(row, 6,
                             f'=IFERROR(INDEX({method},'
                             f'MATCH($B$6,{recipe},0)),"")',
                             f["input_text_wrap"])
        else:
            ws.write_blank(row, 6, None, f["calc_text"])
        ws.set_row(row, 22)

    ws.freeze_panes(spec.header_row, 2)
    ws.set_tab_color(Palette.primary)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, 6)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
