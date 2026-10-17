"""
Recipe Costs - what every dish really costs to put on the table.

The Recipes tab already shows a cost per serving; this tab puts the whole
book side by side, cheapest first, and breaks out the single most expensive
ingredient in each recipe so you can see exactly where the money goes.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, lookup
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, lookup
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    recipes = lists("Recipes", "recipe")

    def rec(key: str) -> str:
        return lists("Recipes", key)

    ri_recipe = lists("Recipe Ingredients", "recipe")
    ri_ing = lists("Recipe Ingredients", "ingredient")
    ri_cost = lists("Recipe Ingredients", "line_cost")

    columns = [
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes},
            note="Pick a recipe from your recipe book."),
        Col("category", "Category", 15, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes, rec("category")) + ")"),
        Col("servings", "Servings", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("servings")) + ")"),
        Col("ingredient_count", "Ingredients", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS(' + ri_recipe + ',{recipe}{r}))'),
        Col("total_cost", "Total cost", 12, "calc", group="cost",
            formula='=IF({recipe}{r}="","",'
                    'SUMIFS(' + ri_cost + ',' + ri_recipe + ','
                    '{recipe}{r}))'),
        Col("cost_per_serving", "Cost / serving", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("cost_per_serving")) + ")"),
        Col("cost_per_calorie", "Cost / 100 kcal", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{calories}{r}="",'
                    '{calories}{r}=0),"",'
                    'IFERROR({cost_per_serving}{r}/{calories}{r}*100,'
                    '""))'),
        Col("cost_rank", "Cost rank", 10, "calc", group="rankings",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'COUNTIFS({cost_per_serving_first}:'
                    '{cost_per_serving_last},"<"&'
                    '{cost_per_serving}{r})+1)'),
        Col("top_ingredient", "Priciest ingredient", 22, "calc",
            group="breakdown",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(INDEX(' + ri_ing + ',MATCH(1,INDEX(('
                    + ri_recipe + '={recipe}{r})*(' + ri_cost + '='
                    '{top_ingredient_cost}{r}),0),0)),""))'),
        Col("top_ingredient_cost", "Its cost", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'SUMPRODUCT(MAX((' + ri_recipe + '={recipe}{r})*'
                    + ri_cost + ')))'),
        Col("top_share", "Share of cost", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{total_cost}{r}="",'
                    '{total_cost}{r}=0),"",'
                    'IFERROR({top_ingredient_cost}{r}/{total_cost}{r},'
                    '""))'),
        Col("vs_average", "Vs average dish", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'IFERROR({cost_per_serving}{r}-AVERAGE('
                    '{cost_per_serving_first}:{cost_per_serving_last}),'
                    '""))'),
        Col("budget_flag", "Budget flag", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'IF({cost_per_serving}{r}<=Weekly_Budget/21,'
                    '"Within budget","Over budget"))'),
        Col("calories", "Calories", 10, "calc", group="value",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("calories")) + ")"),
        Col("calories_per_dollar", "kcal / $", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("calories_per_dollar")) + ")"),
        Col("protein_per_dollar", "Protein / $", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             rec("protein_per_dollar")) + ")"),
        Col("weekly_cost", "Cost per week", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    '{cost_per_serving}{r}*7*3)'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Recipe Costs",
        title="Recipe Costs",
        subtitle="Cost per serving for every recipe, cheapest first",
        columns=columns,
        rows=cfg.row_count("Recipe Costs"),
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Recipe Ingredients", "Budget", "Reports",
        "Help"])
