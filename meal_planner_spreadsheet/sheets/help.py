"""
Help - questions, answers and troubleshooting.

Also documents the columns that are easy to misunderstand and what to do
when a number looks wrong.
"""

from __future__ import annotations

try:
    from ..config import AUTHOR, Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import AUTHOR, Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer

FAQ = [
    ("How do I start?",
     "Go to Settings and fill in your household, budget and targets. Then "
     "add the ingredients you buy most often to the Ingredients tab, add "
     "your favourite recipes, and plan your first week on the Weekly "
     "Planner tab."),
    ("How does the grocery list fill itself?",
     "Everything you plan on the Weekly Planner or the Meal Plan tab is "
     "copied to the Grocery List tab. Quantities are scaled by the servings "
     "you asked for and reduced by whatever you already have in the pantry, "
     "so the list only shows what you actually need to buy."),
    ("Why is a recipe showing a cost of zero?",
     "The recipe has no ingredients on the Recipe Ingredients tab yet, or "
     "the ingredient names there do not exactly match the names on the "
     "Ingredients tab. The cost is looked up by name, so keep the spelling "
     "identical."),
    ("Can I change the meal slots?",
     "Yes - edit the Meal slots column on the Lists tab. The planner grids, "
     "the nutrition log and the reports all follow the list."),
    ("What if I shop at more than one store?",
     "Add each shop on the Stores tab, then set the store on the "
     "Ingredients tab. The grocery list can be printed per store, and the "
     "Store Prices tab compares the same item across shops."),
    ("How do the pantry and expiry reminders work?",
     "Add an item, its quantity and the date you opened or bought it. The "
     "pantry works out the expiry date from the shelf life on the "
     "Ingredients tab and flags anything inside the 'use it or lose it' "
     "window you set on Settings."),
    ("Can I use ounces instead of grams?",
     "Set Measurement system to Imperial on the Settings tab and use the "
     "Converter tab when a recipe is written in the other system."),
    ("How do I record that we ate out?",
     "On the Meal Plan tab set the status to Takeaway or Eating out. The "
     "budget and the habit trackers pick it up, and the week is no longer "
     "counted as fully home cooked."),
    ("Can I print just the shopping list?",
     "Yes - Print Shopping. Choose the store and the week, then print. The "
     "list is grouped by aisle with check boxes down the side."),
    ("How do I add a recipe card?",
     "Print Recipe. Choose the recipe title and it lays out the "
     "ingredients, the method notes and the nutrition for one page."),
    ("Something looks wrong - what do I check first?",
     "Check that the ingredient and recipe names match exactly between "
     "tabs, that the dates are real dates and not text, and that Settings "
     "has a planning year. Most odd numbers come from a name typed "
     "slightly differently on two tabs."),
    ("Can I add my own columns?",
     "Yes, but the sheets are protected. Unprotect the sheet from Review > "
     "Unprotect Sheet, add your columns to the right of the existing ones, "
     "then protect it again."),
    ("How much of this do I have to fill in?",
     "Only what you use. If you never batch cook, leave Meal Prep and "
     "Fridge & Freezer empty. The planner still works from Recipes, Meal "
     "Plan and Grocery List alone."),
    ("Where do I get support?",
     f"Message {AUTHOR} through the shop where you bought this workbook "
     "and include the version number from the Start Here tab."),
]

TROUBLESHOOTING = [
    ("#REF! errors", "A row or column was deleted. Close without saving and "
                     "reopen the original file."),
    ("Zero calories for a planned meal",
     "The recipe has no nutrition entered, or the servings on the plan row "
     "are zero."),
    ("Grocery list is empty",
     "The Meal Plan rows have no date inside the week you are looking at, "
     "or the status is set to Skipped."),
    ("Costs look too high",
     "The price on the Ingredients tab is the price of one unit, not of a "
     "whole pack. Divide the pack price by the pack size."),
    ("A drop down will not let me type",
     "The cell is validated against a list on the Lists tab. Either pick "
     "from the list or add your value to the list."),
]


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Help",
        title="Help",
        subtitle="Frequently asked questions, column notes and "
                 "troubleshooting",
        columns=[
            Col("question", "Question", 40, "text"),
            Col("answer", "Answer", 92, "text_wrap"),
            Col("note", "Note", 20, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.grey_text,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    p, f = Palette, writer.fmt
    writer.grid_off(ws)
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 44)
    ws.set_column(2, 2, 92)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 2, "HELP", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 2,
                   "Frequently asked questions, column notes and "
                   "troubleshooting", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 2,
                   "  |  Start Here   |   Settings   |   Weekly Planner   |  "
                   " Grocery List   |   Reports", f["nav"])

    row = 4
    ws.merge_range(row, 0, row, 2, "  FREQUENTLY ASKED QUESTIONS",
                   f["section"])
    row += 1
    for question, answer in FAQ:
        ws.set_row(row, 46)
        ws.write(row, 1, question, f["label"])
        ws.write(row, 2, answer, f["plain_wrap"])
        row += 1

    row += 1
    ws.merge_range(row, 0, row, 2, "  TROUBLESHOOTING", f["section"])
    row += 1
    for problem, fix in TROUBLESHOOTING:
        ws.set_row(row, 30)
        ws.write(row, 1, problem, f["label"])
        ws.write(row, 2, fix, f["plain_wrap"])
        row += 1

    row += 1
    ws.merge_range(row, 0, row, 2, "  GOOD HABITS", f["section"])
    row += 1
    habits = [
        "Fill in Settings first - the rest of the workbook depends on it.",
        "Add your 20 most used ingredients before anything else.",
        "Type ingredient names exactly the same way on every tab.",
        "Plan one week at a time until the habit sticks.",
        "Record what you actually threw away - it is the fastest way to "
        "save money on food.",
        "Print the week and stick it on the fridge; the plan only works "
        "if you can see it.",
    ]
    for habit in habits:
        ws.set_row(row, 20)
        ws.write(row, 1, "-", f["plain_bold"])
        ws.write(row, 2, habit, f["plain_wrap"])
        row += 1

    row += 1
    ws.merge_range(row, 0, row, 2,
                   f"  {AUTHOR}  -  version {cfg.version}", f["section"])

    ws.set_tab_color(Palette.grey_text)
    ws.hide_gridlines(2)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row, 2)
