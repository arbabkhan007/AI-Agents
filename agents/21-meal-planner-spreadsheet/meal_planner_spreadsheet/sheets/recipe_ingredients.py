"""
Recipe Ingredients - what goes into each recipe, and what it costs.

One row per ingredient per recipe.  The price, category, store and
nutrition are looked up from the Ingredients tab by name, so the cost per
serving on the Recipes tab is always live: change a price once and every
recipe that uses it re-prices itself.
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

YES_NO = ["Yes", "No"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    recipes = registry.rng("Recipes", "recipe")
    units = registry.rng("Lists", "unit")
    ing_name = registry.rng("Ingredients", "ingredient")

    def ing(key: str) -> str:
        return registry.rng("Ingredients", key)

    columns = [
        Col("recipe", "Recipe", 28, "text",
            validate={"type": "list", "source": "=" + recipes},
            note="Pick the recipe this ingredient belongs to."),
        Col("ingredient", "Ingredient", 26, "text",
            validate={"type": "list", "source": "=" + ing_name},
            note="Must match a name on the Ingredients tab exactly."),
        Col("quantity", "Quantity", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("preparation", "Preparation", 16, "text",
            note="How it goes into the pan - sliced, diced, chopped..."),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + units}),
        Col("category", "Category", 16, "calc",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("category")) + ")"),
        Col("store", "Best store", 16, "calc",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("store")) + ")"),
        Col("price", "Price / unit", 11, "calc", group="cost",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("price")) + ")"),
        Col("line_cost", "Line cost", 11, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*{price}{r},""))'),
        Col("servings", "Recipe servings", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    + lookup("{recipe}{r}", recipes,
                             registry.rng("Recipes", "servings")) + ")"),
        Col("cost_per_serving", "Cost / serving", 12, "calc",
            formula='=IF(OR({line_cost}{r}="",{servings}{r}="",'
                    '{servings}{r}=0),"",'
                    'IFERROR({line_cost}{r}/{servings}{r},""))'),
        Col("calories", "Calories", 10, "calc", group="nutrition",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("calories_per_unit")) + ',""))'),
        Col("protein", "Protein (g)", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("protein_per_unit")) + ',""))'),
        Col("carbs", "Carbs (g)", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("carbs_per_unit")) + ',""))'),
        Col("fat", "Fat (g)", 9, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("fat_per_unit")) + ',""))'),
        Col("fibre", "Fibre (g)", 9, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'IFERROR({quantity}{r}*'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("fibre_per_unit")) + ',""))'),
        Col("share_of_recipe_cost", "Share of cost", 12, "calc",
            formula='=IF(OR({line_cost}{r}="",{recipe}{r}=""),"",'
                    'IFERROR({line_cost}{r}/SUMIFS('
                    '[[Recipe Ingredients.line_cost]],'
                    '[[Recipe Ingredients.recipe]],{recipe}{r}),""))'),
        Col("cost_rank", "Cost rank", 10, "calc",
            formula='=IF({line_cost}{r}="","",'
                    'COUNTIFS({line_cost_first}:{line_cost_last},'
                    '">"&{line_cost}{r})+1)'),
        Col("in_pantry", "In pantry", 10, "calc", group="pantry",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{ingredient}{r}))'),
        Col("shortfall", "To buy", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{quantity}{r}=""),"",'
                    'MAX(0,{quantity}{r}-{in_pantry}{r}))'),
        Col("pack_size", "Pack size", 10, "number", group="packs",
            validate={"type": "decimal", "between": 0, "and": 100000},
            note="Size of the pack you buy, in the same unit as the "
                 "quantity."),
        Col("pack_cost", "Pack cost", 11, "calc",
            formula='=IF(OR({pack_size}{r}="",{pack_size}{r}=0,'
                    '{price}{r}=""),"",{pack_size}{r}*{price}{r})'),
        Col("packs_needed", "Packs needed", 12, "calc",
            formula='=IF(OR({shortfall}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",CEILING({shortfall}{r}/'
                    '{pack_size}{r},1))'),
        Col("organic", "Organic", 9, "select",
            validate={"type": "list", "source": YES_NO}),
        Col("waste_factor", "Waste %", 9, "percent",
            validate={"type": "decimal", "between": 0, "and": 1},
            note="Peel, trim and spillage as a share of the quantity."),
        Col("effective_qty", "Qty incl. waste", 12, "calc",
            formula='=IF(OR({quantity}{r}="",{waste_factor}{r}=""),"",'
                    '{quantity}{r}*(1+{waste_factor}{r}))'),
        Col("staple", "Staple", 9, "calc",
            formula='=IF({ingredient}{r}="","",'
                    + lookup("{ingredient}{r}", ing("ingredient"),
                             ing("staple")) + ")"),
        Col("status", "Status", 14, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF({in_pantry}{r}>={quantity}{r},"In pantry",'
                    '"To buy"))'),
        Col("line_no", "Line in recipe", 11, "calc", group="order",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({recipe_first}:{recipe}{r},{recipe}{r}))'),
        Col("filter_flag", "Diet check", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF(COUNTIFS([[Dietary Filters.exclude]],'
                    '{ingredient}{r})>0,"Check","OK"))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Recipe Ingredients",
        title="Recipe Ingredients",
        subtitle="One row per ingredient per recipe - the cost engine behind "
                 "every recipe",
        columns=columns,
        rows=cfg.row_count("Recipe Ingredients"),
        tab_color=Palette.primary_mid,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Ingredients", "Recipe Costs", "Help"])
