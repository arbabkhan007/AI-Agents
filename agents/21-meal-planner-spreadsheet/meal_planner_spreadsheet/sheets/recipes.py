"""
Recipes - the recipe book.

Every recipe carries its timings, the nutrition per serving, the dietary
flags and a set of live rankings: cheapest, most protein, best match to the
household, and how overdue it is for another turn in the plan.  The cost
columns are pulled from the Recipe Ingredients tab, so add the ingredients
first and the costs appear on their own.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec, unique_rank
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec, unique_rank
    from writer import Writer

CATEGORIES = ["Breakfast", "Lunch", "Dinner", "Snack", "Dessert", "Drink",
              "Side", "Sauce", "Base"]

CUISINES = ["Any", "Italian", "Mexican", "Indian", "Chinese", "Thai",
            "Japanese", "Mediterranean", "Middle Eastern", "French",
            "American", "British", "Caribbean", "African", "Vietnamese",
            "Korean", "Greek", "Spanish", "Turkish", "Moroccan"]

YES_NO = ["Yes", "No"]
SEASONS = ["Any", "Spring", "Summer", "Autumn", "Winter"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists_cat = registry.rng("Lists", "category")
    lists_cui = registry.rng("Lists", "cuisine")
    lists_yn = registry.rng("Lists", "yes_no")

    columns = [
        Col("recipe", "Recipe", 30, "text", group="basics",
            note="The recipe name. Spell it the same way everywhere else."),
        Col("category", "Category", 13, "select",
            validate={"type": "list",
                      "source": "=" + registry.rng("Lists",
                                                    "recipe_category")}),
        Col("cuisine", "Cuisine", 14, "select",
            validate={"type": "list", "source": "=" + lists_cui}),
        Col("meal_slot", "Best for", 14, "select",
            validate={"type": "list",
                      "source": "=" + registry.rng("Lists", "meal_slot")},
            note="Which meal this recipe usually suits."),
        Col("dietary_tags", "Dietary tags", 18, "text",
            note="Free text - e.g. vegetarian, nut free, kids love it."),
        Col("servings", "Servings", 10, "number",
            validate={"type": "integer", "between": 1, "and": 50},
            note="How many people this recipe feeds as written."),
        Col("prep_time", "Prep (min)", 10, "number",
            validate={"type": "integer", "between": 0, "and": 1440}),
        Col("cook_time", "Cook (min)", 10, "number",
            validate={"type": "integer", "between": 0, "and": 1440}),
        Col("difficulty", "Difficulty", 11, "select",
            validate={"type": "list",
                      "source": ["Easy", "Medium", "Hard"]},
            note="Easy, Medium or Hard - or leave blank."),
        Col("total_time", "Total (min)", 10, "calc",
            formula='=IF({recipe}{r}="","",{prep_time}{r}+{cook_time}{r})'),
        Col("calories", "Calories", 10, "number", group="nutrition",
            note="Per serving."),
        Col("protein", "Protein (g)", 10, "number"),
        Col("carbs", "Carbs (g)", 10, "number"),
        Col("fat", "Fat (g)", 9, "number"),
        Col("fibre", "Fibre (g)", 9, "number"),
        Col("sugar", "Sugar (g)", 9, "number"),
        Col("sodium", "Sodium (mg)", 11, "number"),
        Col("ingredient_count", "Ingredients", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.recipe]],{recipe}{r}))'),
        Col("total_cost", "Total cost", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'SUMIFS([[Recipe Ingredients.line_cost]],'
                    '[[Recipe Ingredients.recipe]],{recipe}{r}))',
            group="cost"),
        Col("cost_per_serving", "Cost / serving", 13, "calc",
            formula='=IF(OR({recipe}{r}="",{servings}{r}=0,{servings}{r}=""),'
                    '"",{total_cost}{r}/{servings}{r})'),
        Col("cost_per_1000_cal", "Cost / 1000 kcal", 14, "calc",
            formula='=IF(OR({recipe}{r}="",{calories}{r}=0,'
                    '{calories}{r}=""),"",'
                    'IFERROR({cost_per_serving}{r}/{calories}{r}*1000,""))'),
        Col("calories_per_dollar", "kcal / $", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}="",'
                    '{cost_per_serving}{r}=0),"",'
                    'IFERROR({calories}{r}/{cost_per_serving}{r},""))'),
        Col("protein_per_dollar", "Protein / $", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}="",'
                    '{cost_per_serving}{r}=0),"",'
                    'IFERROR({protein}{r}/{cost_per_serving}{r},""))'),
        Col("prep_efficiency", "kcal / 10 min", 12, "calc",
            formula='=IF(OR({recipe}{r}="",{total_time}{r}="",'
                    '{total_time}{r}=0),"",'
                    'IFERROR({calories}{r}/{total_time}{r}*10,""))'),
        Col("match_score", "Match score", 11, "calc", group="household fit",
            formula='=IF({recipe}{r}="","",'
                    '({vegetarian}{r}="Yes")*1+({vegan}{r}="Yes")*1'
                    '+({gluten_free}{r}="Yes")*1+({dairy_free}{r}="Yes")*1'
                    '+({nut_free}{r}="Yes")*1+({kid_friendly}{r}="Yes")*1)'),
        Col("times_planned", "Times cooked", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Cooked")'
                    '+COUNTIFS([[Meal Plan.recipe]],{recipe}{r},'
                    '[[Meal Plan.status]],"Eaten"))'),
        Col("last_planned", "Last cooked", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF(SUMPRODUCT(MAX(([[Meal Plan.recipe]]={recipe}{r})'
                    '*[[Meal Plan.date]]))=0,"",'
                    'SUMPRODUCT(MAX(([[Meal Plan.recipe]]={recipe}{r})'
                    '*[[Meal Plan.date]]))))'),
        Col("days_since", "Days since", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{last_planned}{r}=""),"",'
                    'TODAY()-{last_planned}{r})'),
        Col("rotation_ok", "Rotation", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({days_since}{r}="","Yes",'
                    'IF({days_since}{r}>=Rotation_Gap_Days,"Yes","No")))'),
        Col("plan_flag", "Plan flag", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({rotation_ok}{r}="No","Too soon",'
                    'IF(AND({rating}{r}<>"",{rating}{r}>=4),"Plan it",'
                    '"Available")))'),
        Col("favourite", "Favourite", 10, "select",
            validate={"type": "list", "source": "=" + lists_yn},
            group="flags"),
        Col("vegetarian", "Vegetarian", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("vegan", "Vegan", 9, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("gluten_free", "Gluten free", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("dairy_free", "Dairy free", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("nut_free", "Nut free", 10, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("kid_friendly", "Kid friendly", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("batch_friendly", "Batch cook", 11, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("freezer_friendly", "Freezer", 10, "select",
            validate={"type": "list", "source": "=" + lists_yn}),
        Col("quick_meal", "Quick (30 min)", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IF({total_time}{r}<=30,"Yes","No"))'),
        Col("seasonal", "Season", 11, "select",
            validate={"type": "list", "source": SEASONS}),
        Col("added_on", "Added on", 12, "date",
            note="When you added the recipe - used by the 'new recipes "
                 "tried' counter."),
        Col("rating", "Rating (1-5)", 11, "number",
            validate={"type": "decimal", "between": 0, "and": 5},
            group="notes"),
        Col("method", "Method", 60, "text_wrap", group="notes",
            note="How to cook it, step by step. Keep it simple."),
        Col("source", "Source", 20, "text"),
        Col("url", "Link", 20, "text"),
        Col("tags", "Tags", 26, "text"),
        Col("notes", "Notes", 40, "text_wrap"),
        # ---- rankings -----------------------------------------------------
        Col("calories_rank", "Calorie rank", 11, "calc", group="rankings",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({calories_first}:{calories_last},'
                    '">"&{calories}{r})+1)'),
        Col("protein_rank", "Protein rank", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({protein_first}:{protein_last},'
                    '">"&{protein}{r})+1)'),
        Col("fibre_rank", "Fibre rank", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({fibre_first}:{fibre_last},'
                    '">"&{fibre}{r})+1)'),
        Col("cost_rank", "Cost rank", 11, "calc",
            formula='=IF(OR({recipe}{r}="",{cost_per_serving}{r}=""),"",'
                    'COUNTIFS({cost_per_serving_first}:'
                    '{cost_per_serving_last},"<"&{cost_per_serving}{r})+1)'),
        Col("match_rank", "Match rank", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({match_score_first}:{match_score_last},'
                    '">"&{match_score}{r})+1)'),
        Col("rotation_rank", "Rotation rank", 12, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({days_since_first}:{days_since_last},'
                    '"<"&{days_since}{r})+1)'),
        Col("times_planned_rank", "Popularity rank", 13, "calc",
            formula='=IF({recipe}{r}="","",'
                    'COUNTIFS({times_planned_first}:{times_planned_last},'
                    '">"&{times_planned}{r})+1)'),
    ]

    spec = SheetSpec(
        name="Recipes",
        title="Recipes",
        subtitle="Your recipe book - timings, nutrition per serving, cost "
                 "and live rankings",
        columns=columns,
        rows=cfg.row_count("Recipes"),
        tab_color=Palette.primary,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipe Ingredients", "Ingredients", "Weekly Planner",
        "Meal Plan", "Recipe Costs", "Rotation", "Help"])
