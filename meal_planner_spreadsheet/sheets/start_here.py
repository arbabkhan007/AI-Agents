"""
Start Here - the landing tab the buyer sees first.

A one page tour: what the workbook does, the five step set up, the colour
key (cream = type here, sage = calculated, do not touch) and an index of
every tab with a click-through link.
"""

from __future__ import annotations

try:
    from ..build import SHEET_ORDER
    from ..config import AUTHOR, Config, Palette, PRODUCT_NAME
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from build import SHEET_ORDER
    from config import AUTHOR, Config, Palette, PRODUCT_NAME
    from layout import Col, Registry, SheetSpec
    from writer import Writer

STEPS = [
    ("1. Set up your household",
     "Settings tab: household name, number of people, servings per meal, "
     "currency, measurement system, grocery budget and your nutrition "
     "targets. Everything else reads from here."),
    ("2. Add your ingredients",
     "Ingredients tab: name, category, unit, price and the nutrition per "
     "unit. These prices drive every recipe cost and grocery total, so add "
     "the staples you buy most often first."),
    ("3. Build your recipe book",
     "Recipes tab: title, category, servings, timings and the nutrition per "
     "serving. Recipe Ingredients tab: list each ingredient with its "
     "quantity and the cost per serving is calculated for you."),
    ("4. Plan the week",
     "Weekly Planner tab: pick a week starting date, then choose a recipe "
     "for each day and slot. The planner works out the calories, protein "
     "and cost of the whole week as you type."),
    ("5. Shop and cook",
     "Grocery List tab: everything you planned is already there, grouped "
     "by aisle, with quantities scaled to your household. Print it with "
     "Print Shopping, then tick items off as you fill the basket."),
]

COLOUR_KEY = [
    ("Cream cells", "You type here. These cells are unlocked.", "input_text"),
    ("Soft sage cells", "Calculated by the spreadsheet. Leave them alone.",
     "calc_text"),
    ("Green headers", "Column titles - hover for a note about the column.",
     "header"),
    ("Terracotta", "Totals, targets and anything that needs attention.",
     "kpi_value_money"),
]

TAB_GUIDE = [
    ("Start Here", "This page."),
    ("Dashboard", "The week at a glance: calories, budget, what to cook, "
                  "what is expiring and how your habits are going."),
    ("Weekly Planner", "Pick the meals for one week, day by day."),
    ("Monthly Planner", "The whole month on one page with the food budget "
                        "per week."),
    ("Settings", "Household, budget, nutrition targets and reminder "
                 "windows."),
    ("Lists", "Every drop down source: meal slots, units, categories, "
              "cuisines, stores, diets."),
    ("Household", "Who you are cooking for, their diets, allergies and "
                  "calorie needs."),
    ("Recipes", "Your recipe book with nutrition, cost and rankings."),
    ("Recipe Ingredients", "What goes into each recipe and what it costs."),
    ("Ingredients", "Master ingredient list with prices and nutrition."),
    ("Meal Plan", "Every planned meal in one long register - the engine "
                  "behind the planner."),
    ("Grocery List", "The automatic shopping list, grouped by aisle."),
    ("Pantry", "What you have, what is running low, what expires next."),
    ("Staples", "The things you buy every week, with buy-by reminders."),
    ("Leftovers", "What is in the fridge or freezer and when to eat it."),
    ("Food Waste", "What got thrown away, why, and what it cost."),
    ("Meal Prep", "Batch cooking tasks and what to do when."),
    ("Dietary Filters", "Allergies and dietary needs, and which recipes "
                        "are safe."),
    ("Nutrition", "Daily nutrition log against your targets."),
    ("Budget", "Planned versus actual food spend, month by month."),
    ("Recipe Costs", "Cost per serving for every recipe."),
    ("Converter", "Unit conversions plus a live converter you can use."),
    ("Rotation", "How often each meal repeats, so nothing gets boring."),
    ("Food Safety", "How long food keeps, and safe storage temperatures."),
    ("Fridge & Freezer", "Batch cooked portions and their use-by dates."),
    ("Grocery Spending", "Every shop you record, against the budget."),
    ("Store Prices", "Price comparison for the same item across stores."),
    ("Stores", "Your shops, with spend and best-for notes."),
    ("Events", "Parties, holidays and dinner guests, with a menu budget."),
    ("Event Menu", "The recipes and quantities for each event."),
    ("Goals", "Habit goals with live progress."),
    ("Sustainability", "Waste, packaging and local shopping metrics."),
    ("Reports", "Any date range: spend, nutrition, waste, variety."),
    ("Print Week", "A printable weekly meal plan for the fridge door."),
    ("Print Shopping", "A printable grocery list."),
    ("Print Recipe", "A printable recipe card."),
    ("Help", "Frequently asked questions and troubleshooting."),
]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Start Here",
        title="Start Here",
        subtitle=cfg.product_subtitle,
        columns=[
            Col("section", "Section", 30, "text"),
            Col("heading", "Heading", 26, "text"),
            Col("body", "Body", 90, "text_wrap"),
            Col("note", "Note", 26, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    p, f = Palette, writer.fmt
    writer.grid_off(ws)
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 78)
    ws.set_column(3, 3, 22)

    ws.set_row(0, 42)
    ws.merge_range(0, 0, 0, 3, "MEAL PLANNER & GROCERY LIST", f["title"])
    ws.set_row(1, 20)
    ws.merge_range(1, 0, 1, 3, cfg.product_subtitle, f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 3,
                   f"  Version {cfg.version}   |   {AUTHOR}   |   "
                   f"36 tabs   |   Start at Settings, then Recipes, "
                   f"then Weekly Planner", f["nav"])

    row = 4
    ws.merge_range(row, 0, row, 3,
                   "  WELCOME - THIS WORKBOOK PLANS YOUR MEALS AND WRITES "
                   "YOUR SHOPPING LIST", f["section"])
    row += 1
    intro = ("Plan breakfast, lunch and dinner for the week, see the calories "
             "and the cost of every meal, keep an eye on what is in the "
             "pantry, and print a grocery list that is already grouped by "
             "aisle. Fill in the cream cells only - the soft sage cells "
             "calculate themselves.")
    ws.merge_range(row, 1, row + 2, 3, intro, f["plain_wrap"])
    row += 4

    ws.merge_range(row, 0, row, 3, "  SET IT UP IN FIVE STEPS", f["section"])
    row += 1
    for heading, body in STEPS:
        ws.set_row(row, 34)
        ws.write(row, 1, heading, f["label"])
        ws.merge_range(row, 2, row, 3, body, f["plain_wrap"])
        row += 1
    row += 1

    ws.merge_range(row, 0, row, 3, "  COLOUR KEY", f["section"])
    row += 1
    for label, body, style in COLOUR_KEY:
        ws.set_row(row, 22)
        ws.write(row, 1, label, f[style])
        ws.merge_range(row, 2, row, 3, body, f["plain_wrap"])
        row += 1
    row += 1

    ws.merge_range(row, 0, row, 3, "  WHAT IS ON EACH TAB", f["section"])
    row += 1
    for tab, what in TAB_GUIDE:
        ws.set_row(row, 20)
        ws.write_url(row, 1, f"internal:'{tab}'!A1", f["link"], string=tab)
        ws.merge_range(row, 2, row, 3, what, f["plain_wrap"])
        row += 1
    row += 1

    ws.merge_range(row, 0, row, 3,
                   "  SHEET PROTECTION", f["section"])
    row += 1
    ws.set_row(row, 40)
    ws.merge_range(row, 1, row, 3,
                   "Every tab is protected so the formulas cannot be "
                   "deleted by accident. The cream input cells stay "
                   "editable. If you want to change the look of the whole "
                   "workbook, unprotect the sheets from Review > Unprotect "
                   f"Sheet (password: {cfg.password}) and re-protect them "
                   "when you are done.", f["plain_wrap"])
    row += 2
    ws.merge_range(row, 0, row, 3,
                   f"  {AUTHOR}  -  thank you for buying this workbook!",
                   f["section"])

    ws.set_tab_color(Palette.accent)
    ws.hide_gridlines(2)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row, 3)
