"""
Start Here - the first page.

A short guide to the tabs, the first week of setup and the one golden rule
about ingredient names.  Nothing here needs typing in.
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
        name="Start Here",
        title="Start Here",
        subtitle="How the workbook fits together - and what to do first",
        columns=[
            Col("tab", "Tab", 20, "text"),
            Col("purpose", "What it does", 48, "text"),
            Col("fill_in", "Fill it in?", 12, "text"),
            Col("priority", "When", 16, "text"),
            Col("start", "Start", 8, "text"),
            Col("goal", "Goal", 40, "text"),
            Col("time", "Time", 10, "text"),
            Col("done", "Done", 8, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.primary,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    writer.grid_off(ws)
    ws.set_column(0, 0, 22)
    ws.set_column(1, 1, 50)
    ws.set_column(2, 2, 12)
    ws.set_column(3, 3, 18)
    ws.set_column(4, 4, 8)
    ws.set_column(5, 5, 42)
    ws.set_column(6, 6, 10)
    ws.set_column(7, 7, 8)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 5, "MEAL PLANNER & GROCERY LIST", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 5,
                   "Plan the week, shop the list, cook the food, waste "
                   "less", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 5,
                   "  |  Dashboard   |   Start Here   |   Settings   |   "
                   "Meal Plan   |   Grocery List", f["nav"])

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 5, "  THE TABS - AND WHO FILLS THEM IN",
                   f["section"])
    headers = ["Tab", "What it does", "Fill it in?", "When"]
    for i, head in enumerate(headers):
        ws.write(5, i, head, f["header"])

    tab_guide = [
        ("Start Here", "This page - how the workbook fits together.",
         "No", "Read first"),
        ("Dashboard", "The week at a glance: meals, calories, cost and "
                      "alerts.", "No", "Every day"),
        ("Settings", "Your household, budget and dietary settings.",
         "Yes", "First"),
        ("Household", "Who eats with you, and how much they need.",
         "Yes", "First"),
        ("Recipes", "Your recipe book - one row per recipe.",
         "Yes", "First"),
        ("Recipe Ingredients", "What goes into each recipe.",
         "Yes", "First"),
        ("Ingredients", "Your ingredient list with prices and shelf life.",
         "Yes", "First"),
        ("Meal Plan", "Every planned meal - the engine of the workbook.",
         "Yes", "Weekly"),
        ("Weekly Planner", "The same week laid out day by day.",
         "No", "Weekly"),
        ("Monthly Planner", "The whole month, with themes per week.",
         "Sometimes", "Monthly"),
        ("Grocery List", "The automatic shopping list, by aisle.",
         "Yes - tick things off", "Weekly"),
        ("Pantry", "What you have, and what is about to expire.",
         "Yes", "As you shop"),
        ("Staples", "The things you buy every week, so nothing gets "
                    "forgotten.", "Yes", "Monthly"),
        ("Leftovers", "Batch cooked food waiting to be eaten.",
         "Yes", "As you cook"),
        ("Fridge & Freezer", "Batch cooking stock, with use-by dates.",
         "Yes", "As you cook"),
        ("Meal Prep", "Batch cooking tasks for your prep day.",
         "Yes", "Weekly"),
        ("Food Waste", "What you binned, why, and what it cost.",
         "Yes", "As it happens"),
        ("Nutrition", "Daily nutrition log against your targets.",
         "Sometimes", "As you like"),
        ("Recipe Costs", "Cost per serving for every recipe.",
         "No", "Monthly"),
        ("Grocery Spending", "What you actually spent, week by week.",
         "Yes", "As you shop"),
        ("Store Prices", "The same item, priced at every shop.",
         "Yes", "As you notice"),
        ("Stores", "Where you shop and what each shop is good for.",
         "Yes", "Once"),
        ("Events", "Parties and dinner guests, with a menu budget.",
         "Yes", "As needed"),
        ("Dietary Filters", "Allergies and things to avoid.",
         "Yes", "First"),
        ("Food Safety", "How long food keeps, and at what temperature.",
         "No", "Reference"),
        ("Converter", "Unit conversions, with a live calculator.",
         "No", "Reference"),
        ("Rotation", "How often each meal repeats.",
         "No", "Monthly"),
        ("Budget", "Planned versus actual, month by month.",
         "Sometimes", "Monthly"),
        ("Goals", "Habit goals with a progress bar.",
         "Yes", "Monthly"),
        ("Sustainability", "Waste, packaging and how local you shop.",
         "Sometimes", "Monthly"),
        ("Reports", "The ranked tables behind the month.",
         "No", "Monthly"),
        ("Print Week", "The week on one printable page.",
         "No", "Weekly"),
        ("Print Shopping", "The shopping list, sorted by aisle.",
         "No", "Weekly"),
        ("Print Recipe", "One recipe, in a big friendly layout.",
         "No", "As you cook"),
        ("Lists", "The dropdown lists the workbook uses.",
         "Rarely", "Setup"),
        ("Help", "Questions and answers, and the colours key.",
         "No", "Any time"),
    ]
    row = 6
    for tab, purpose, fill, when in tab_guide:
        ws.write(row, 0, tab, f["calc_bold"])
        ws.write(row, 1, purpose, f["calc_text"])
        ws.write(row, 2, fill, f["calc_center"])
        ws.write(row, 3, when, f["calc_center"])
        row += 1

    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  YOUR FIRST WEEK", f["section"])
    row += 1
    ws.write(row, 4, "Start", f["header"])
    ws.write(row, 5, "Goal", f["header"])
    ws.write(row, 6, "Time", f["header"])
    ws.write(row, 7, "Done", f["header"])
    row += 1
    first_week = [
        ("1", "Set the household, budget and targets on Settings.",
         "10 min"),
        ("2", "Add the recipes you cook most - aim for five to start with.",
         "20 min"),
        ("3", "Add the ingredients those recipes use, with a price.",
         "15 min"),
        ("4", "Plan the meals for the next seven days on Meal Plan.",
         "15 min"),
        ("5", "Check the Grocery List, tick what you already have, and "
              "shop.", "10 min"),
        ("6", "Record what you actually spent on Grocery Spending.",
         "5 min"),
        ("7", "Log anything you bin on Food Waste - and why.", "2 min"),
    ]
    for step, goal, minutes in first_week:
        ws.write(row, 4, step, f["calc_center"])
        ws.write(row, 5, goal, f["calc_text"])
        ws.write(row, 6, minutes, f["calc_center"])
        ws.write_blank(row, 7, None, f["input_select"])
        row += 1

    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 5, "  THE GOLDEN RULE", f["section"])
    row += 1
    ws.set_row(row, 30)
    ws.merge_range(row, 0, row, 5,
                   "Ingredient names must match exactly. If 'Chicken "
                   "breast' is spelled one way on the Ingredients tab and "
                   "another way on Recipe Ingredients, the price cannot be "
                   "found. Pick one spelling and stick to it.",
                   f["card_value"])
    row += 2

    writer.write_note(ws, row, 0,
                      "Everything is sample data to show you how the "
                      "workbook works. Clear the yellow input cells and "
                      "type your own - the calculated cells are grey and "
                      "do the rest.", width=5)

    ws.set_tab_color(Palette.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row + 1, 7)
