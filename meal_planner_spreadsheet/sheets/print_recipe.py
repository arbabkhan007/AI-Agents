"""
Print Recipe - a printable recipe card.

Choose a recipe and it lays out the ingredients with their quantities, the
timings, the cost per serving and the nutrition for one page.  The method
notes come from the recipe itself, so write them once on the Recipes tab and
they print here.
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
        subtitle="A printable recipe card",
        columns=[
            Col("label", " ", 16, "text"),
            Col("value", "Value", 26, "text"),
            Col("ingredient", "Ingredient", 28, "calc"),
            Col("quantity", "Quantity", 12, "calc"),
            Col("unit", "Unit", 10, "calc"),
            Col("note", "Note", 40, "calc"),
        ],
        rows=25,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    ws.set_column(0, 0, 16)
    ws.set_column(1, 1, 26)
    ws.set_column(2, 2, 28)
    ws.set_column(3, 3, 12)
    ws.set_column(4, 4, 10)
    ws.set_column(5, 5, 40)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 5, "RECIPE CARD", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 5,
                   "Pick a recipe and print - one card, one page",
                   f["subtitle"])
    ws.set_row(2, 22)
    ws.write(2, 0, "Recipe", f["label"])
    ws.write_string(2, 1, "Chicken & veg traybake", f["input_text"])
    ws.write(3, 0, "Row found", f["label"])
    ws.write_formula(3, 1,
                     f'=IFERROR(MATCH($B$3,'
                     f'{reg.rng("Recipes", "recipe")},0),0)',
                     f["calc_number"])

    def rec(key: str) -> str:
        return reg.rng("Recipes", key)

    facts = [
        ("Category", rec("category"), "text"),
        ("Cuisine", rec("cuisine"), "text"),
        ("Servings", rec("servings"), "number"),
        ("Prep time (min)", rec("prep_time"), "number"),
        ("Cook time (min)", rec("cook_time"), "number"),
        ("Calories per serving", rec("calories"), "number"),
        ("Protein (g)", rec("protein"), "number"),
        ("Carbs (g)", rec("carbs"), "number"),
        ("Fat (g)", rec("fat"), "number"),
        ("Fibre (g)", rec("fibre"), "number"),
        ("Cost per serving", rec("cost_per_serving"), "money"),
        ("Total cost", rec("total_cost"), "money"),
        ("Rating", rec("rating"), "number"),
        ("Times cooked", rec("times_planned"), "number"),
    ]
    row = 5
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  THE RECIPE", f["section"])
    row += 1
    for i, (label, rng, kind) in enumerate(facts):
        col = (i % 2) * 3
        r = row + (i // 2)
        ws.write(r, col, label, f["label"])
        style = {"text": f["calc_text"], "number": f["calc_number"],
                 "money": f["calc_money"]}[kind]
        ws.write_formula(r, col + 1,
                         f'=IF($B$4=0,"",IFERROR(INDEX({rng},$B$4),""))',
                         style)
    row += (len(facts) + 1) // 2 + 1

    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  INGREDIENTS", f["section"])
    row += 1
    ws.set_row(row, 24)
    for i, head in enumerate(["#", "", "Ingredient", "Quantity", "Unit",
                              "Cost"]):
        ws.write(row, i, head, f["header"])
    row += 1

    ri_recipe = reg.rng("Recipe Ingredients", "recipe")
    ri_line = reg.rng("Recipe Ingredients", "line_no")
    ri_ingredients = reg.rng("Recipe Ingredients", "ingredient")
    ri_quantity = reg.rng("Recipe Ingredients", "quantity")
    ri_unit = reg.rng("Recipe Ingredients", "unit")
    ri_line_cost = reg.rng("Recipe Ingredients", "line_cost")

    def nth(rng: str, n_ref: str) -> str:
        return (f'IFERROR(INDEX({rng},MATCH(1,INDEX('
                f'({ri_recipe}=$B$3)*({ri_line}={n_ref}),0),0)),"")')

    for n in range(1, 26):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        ws.write_formula(row, 2,
                         f'=IF($B$4=0,"",{nth(ri_ingredients, f"$A{r}")})',
                         f["calc_text"])
        ws.write_formula(row, 3,
                         f'=IF($B$4=0,"",{nth(ri_quantity, f"$A{r}")})',
                         f["calc_number"])
        ws.write_formula(row, 4,
                         f'=IF($B$4=0,"",{nth(ri_unit, f"$A{r}")})',
                         f["calc_center"])
        ws.write_formula(row, 5,
                         f'=IF($B$4=0,"",{nth(ri_line_cost, f"$A{r}")})',
                         f["calc_money"])
        row += 1

    ws.write(row, 2, "Total", f["total_label"])
    ws.write_blank(row, 3, None, f["total_label"])
    ws.write_blank(row, 4, None, f["total_label"])
    ws.write_formula(row, 5,
                     f'=IF($B$4=0,"",IFERROR(INDEX({rec("total_cost")},'
                     f'$B$4),""))', f["total_money"])
    row += 2

    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  METHOD", f["section"])
    row += 1
    ws.merge_range(row, 0, row + 7, 5,
                   f'=IF($B$4=0,"",IFERROR(INDEX({rec("notes")},$B$4),'
                   f'"Write your method in the Notes column on the Recipes '
                   f'tab and it will appear here."))',
                   f["plain_wrap"])
    row += 9

    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  NOTE", f["section"])
    row += 1
    ws.merge_range(row, 0, row + 3, 5,
                   f'=IF($B$4=0,"",'
                   f'"This recipe needs "&'
                   f'TEXT(IFERROR(INDEX({rec("ingredient_count")},$B$4),0),'
                   f'"0")&" ingredients. Add them to the Grocery List tab '
                   f'with the quantities above and the rest of the list '
                   f'builds itself.")', f["plain_wrap"])

    ws.set_tab_color(Palette.accent)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.5, 0.5, 0.6, 0.6)
    ws.center_horizontally()
    ws.set_header(f"&L&\"Calibri,Bold\"{cfg.product_name}"
                  f"&R&\"Calibri,Italic\"Recipe card")
    ws.set_footer("&L&D&RPage &P of &N")
    ws.print_area(0, 0, row + 4, 5)
    ws.hide_gridlines(2)
