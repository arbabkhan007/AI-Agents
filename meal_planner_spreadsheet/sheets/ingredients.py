"""
Ingredients - the master list of everything you buy.

Price and nutrition live here once and are looked up by name from the Recipe
Ingredients tab, so a single price change re-prices every recipe that uses
the ingredient.  The right hand columns watch stock, spend and waste: what
is running low, what you bought last, how the price is moving and which
ingredients you throw away most.
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

STORAGE = ["Pantry", "Cupboard", "Fridge", "Freezer"]
YES_NO = ["Yes", "No"]
SEASONS = ["Any", "Spring", "Summer", "Autumn", "Winter"]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_item = lists("Grocery Spending", "item")
    gs_price = lists("Grocery Spending", "price")
    gs_date = lists("Grocery Spending", "date")
    fw_item = lists("Food Waste", "item")
    fw_qty = lists("Food Waste", "qty")

    columns = [
        Col("ingredient", "Ingredient", 26, "text", group="basics",
            note="The name used everywhere else. Keep the spelling "
                 "identical on every tab."),
        Col("category", "Category", 16, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "category")}),
        Col("unit", "Unit", 10, "select",
            validate={"type": "list", "source": "=" + lists("Lists", "unit")},
            note="The unit the price and the nutrition are quoted in."),
        Col("price", "Price / unit", 11, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("store", "Usual store", 18, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "store")}),
        Col("pack_size", "Pack size", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("price_per_unit", "Price per unit", 12, "calc",
            formula='=IF(OR({price}{r}="",{pack_size}{r}="",'
                    '{pack_size}{r}=0),"",{price}{r}/{pack_size}{r})'),
        Col("calories_per_unit", "Calories / unit", 12, "number",
            group="nutrition"),
        Col("protein_per_unit", "Protein / unit", 12, "number"),
        Col("carbs_per_unit", "Carbs / unit", 11, "number"),
        Col("fat_per_unit", "Fat / unit", 10, "number"),
        Col("fibre_per_unit", "Fibre / unit", 11, "number"),
        Col("shelf_life_days", "Shelf life (days)", 12, "number",
            validate={"type": "integer", "between": 0, "and": 3650},
            note="Used to work out expiry dates on the Pantry tab."),
        Col("storage", "Storage", 11, "select",
            validate={"type": "list", "source": STORAGE}),
        Col("staple", "Staple", 9, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")},
            note="Yes = you buy it every week, so it is re-added to the "
                 "grocery list automatically."),
        Col("organic", "Organic", 9, "select",
            validate={"type": "list", "source": "=" + lists("Lists",
                                                            "yes_no")}),
        Col("seasonal", "Season", 11, "select",
            validate={"type": "list", "source": SEASONS}),
        Col("allergens", "Allergens", 18, "text",
            note="Free text: nuts, dairy, gluten ..."),
        Col("in_pantry", "In pantry", 10, "calc", group="stock",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Pantry.quantity]],[[Pantry.item]],'
                    '{ingredient}{r}))'),
        Col("on_grocery_list", "On list", 9, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'COUNTIFS([[Grocery List.item]],{ingredient}{r},'
                    '[[Grocery List.buy]],"Yes"))'),
        Col("weekly_need", "Needed this week", 13, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Grocery List.needed]],'
                    '[[Grocery List.item]],{ingredient}{r}))'),
        Col("recipe_count", "Used in recipes", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'COUNTIFS([[Recipe Ingredients.ingredient]],'
                    '{ingredient}{r}))'),
        Col("total_qty_used", "Qty used in recipes", 13, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS([[Recipe Ingredients.quantity]],'
                    '[[Recipe Ingredients.ingredient]],{ingredient}{r}))'),
        Col("weeks_of_stock", "Weeks of stock", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF({weekly_need}{r}<=0,IF({in_pantry}{r}>0,99,0),'
                    'ROUND({in_pantry}{r}/{weekly_need}{r},1)))'),
        Col("need_score", "Need score", 11, "calc", group="buying",
            formula='=IF({ingredient}{r}="","",'
                    '{weekly_need}{r}*10'
                    '+IF({staple}{r}="Yes",5,0)'
                    '+IF({weeks_of_stock}{r}<1,10,0)'
                    '+IF({in_pantry}{r}<=0,3,0))'),
        Col("need_rank", "Need rank", 10, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'COUNTIFS({need_score_first}:{need_score_last},'
                    '">"&{need_score}{r})+1)'),
        Col("buy_this_week", "Buy this week", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF(OR({weekly_need}{r}>0,'
                    'AND({staple}{r}="Yes",{weeks_of_stock}{r}<2)),'
                    '"Yes","No"))'),
        Col("value_in_pantry", "Pantry value", 12, "calc",
            formula='=IF(OR({ingredient}{r}="",{price}{r}=""),"",'
                    '{in_pantry}{r}*{price}{r})'),
        Col("spend_rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF({value_in_pantry}{r}="","",'
                    'COUNTIFS({value_in_pantry_first}:'
                    '{value_in_pantry_last},">"&{value_in_pantry}{r})+1)'),
        Col("waste_qty", "Wasted qty", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMIFS(' + fw_qty + ',' + fw_item + ','
                    '{ingredient}{r}))'),
        Col("waste_rank", "Waste rank", 10, "calc",
            formula='=IF(OR({ingredient}{r}="",{waste_qty}{r}=0),"",'
                    'COUNTIFS({waste_qty_first}:{waste_qty_last},'
                    '">"&{waste_qty}{r})+1)'),
        Col("last_purchased", "Last bought", 12, "calc", group="prices",
            formula='=IF({ingredient}{r}="","",'
                    'IF(SUMPRODUCT(MAX((' + gs_item + '={ingredient}{r})*'
                    + gs_date + '))=0,"",'
                    'SUMPRODUCT(MAX((' + gs_item + '={ingredient}{r})*'
                    + gs_date + '))))'),
        Col("last_price", "Last price", 11, "calc",
            formula='=IF(OR({ingredient}{r}="",{last_purchased}{r}=""),"",'
                    'IFERROR(AVERAGEIFS(' + gs_price + ',' + gs_item + ','
                    '{ingredient}{r},' + gs_date + ','
                    '{last_purchased}{r}),""))'),
        Col("avg_price", "Average price", 12, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IFERROR(AVERAGEIFS(' + gs_price + ',' + gs_item + ','
                    '{ingredient}{r}),""))'),
        Col("min_price", "Lowest price", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF(SUMPRODUCT(MIN((' + gs_item + '={ingredient}{r})*'
                    + gs_price + '+(' + gs_item + '<>{ingredient}{r})'
                    '*1000000))>=1000000,"",'
                    'SUMPRODUCT(MIN((' + gs_item + '={ingredient}{r})*'
                    + gs_price + '+(' + gs_item + '<>{ingredient}{r})'
                    '*1000000))))'),
        Col("max_price", "Highest price", 11, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'SUMPRODUCT(MAX((' + gs_item + '={ingredient}{r})*'
                    + gs_price + ')))'),
        Col("price_spread", "Price spread", 11, "calc",
            formula='=IF(OR({ingredient}{r}="",{min_price}{r}="",'
                    '{max_price}{r}=0),"",{max_price}{r}-{min_price}{r})'),
        Col("price_change", "Change vs average", 13, "calc",
            formula='=IF(OR({ingredient}{r}="",{last_price}{r}="",'
                    '{avg_price}{r}=""),"",{last_price}{r}-{avg_price}{r})'),
        Col("price_trend", "Trend", 10, "calc",
            formula='=IF({ingredient}{r}="","",'
                    'IF({price_change}{r}="","",'
                    'IF({price_change}{r}>0.01,"Up",'
                    'IF({price_change}{r}<-0.01,"Down","Flat"))))'),
        Col("notes", "Notes", 34, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Ingredients",
        title="Ingredients",
        subtitle="Everything you buy, with price, nutrition, stock and spend "
                 "in one place",
        columns=columns,
        rows=cfg.row_count("Ingredients"),
        tab_color=Palette.primary,
        freeze_cols=2,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    writer.register(ws, spec)
    writer.finish_sheet(ws, spec, links=[
        "Dashboard", "Recipes", "Recipe Ingredients", "Pantry",
        "Grocery List", "Store Prices", "Help"])
