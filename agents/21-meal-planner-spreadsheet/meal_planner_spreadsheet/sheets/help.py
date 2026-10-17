"""
Help - the questions people actually ask.

Q and A on the way the workbook works, and a key to the colours.  Nothing
here needs typing in.
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
        name="Help",
        title="Help",
        subtitle="The questions people actually ask",
        columns=[
            Col("question", "Question", 40, "text"),
            Col("answer", "Answer", 62, "text"),
            Col("colour", "Colour", 18, "text"),
            Col("meaning", "What it means", 40, "text"),
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
    ws.set_column(0, 0, 42)
    ws.set_column(1, 1, 64)
    ws.set_column(2, 2, 18)
    ws.set_column(3, 3, 42)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 3, "HELP", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 3,
                   "The questions people actually ask", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 3,
                   "  |  Start Here   |   Dashboard   |   Settings   |   "
                   "Lists", f["nav"])

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 1, "  QUESTIONS AND ANSWERS", f["section"])
    ws.write(5, 0, "Question", f["header"])
    ws.write(5, 1, "Answer", f["header"])

    qa = [
        ("How does the Grocery List fill itself in?",
         "Every row on the Meal Plan that has a recipe contributes its "
         "ingredients. The quantities are scaled to the servings you "
         "planned, reduced by what the Pantry tab says you already have "
         "and grouped by aisle."),
        ("Why can't I change a grey cell?",
         "Grey cells are calculated. The sheet is protected so they cannot "
         "be overwritten by accident. If you want to edit one, use Review "
         "then Unprotect Sheet with the password."),
        ("Why does a price not show on the Grocery List?",
         "The item name on the Grocery List or Recipe Ingredients tab does "
         "not match the name on the Ingredients tab exactly. Fix the "
         "spelling - the prices follow."),
        ("What is the password to unprotect a sheet?",
         "premium - all lowercase."),
        ("How do I add my own recipes?",
         "Add a row on the Recipes tab, then add each ingredient on the "
         "Recipe Ingredients tab. Both tabs have a sample to copy from."),
        ("What is the difference between input and calculated cells?",
         "Yellow cells are yours to type in. Grey cells are formulas. "
         "Anything red is a warning."),
        ("How do I plan leftovers?",
         "Cook a double batch, mark the meal as Cooked on the Meal Plan "
         "tab, then add the extra portions to the Leftovers tab. Plan the "
         "leftovers as meals later in the week using the Leftover of "
         "column."),
        ("Can I use this for just me?",
         "Yes. Set Household Size to 1 on the Settings tab and everything "
         "follows."),
        ("What happens at the end of the month?",
         "Add a new month row on the Budget tab, copy the Grocery "
         "Spending and Food Waste rows into a new sheet if you want to "
         "archive them, and start again."),
        ("How do I print the week?",
         "The Print Week tab is laid out for one page. Set the week at the "
         "top and print. The Print Shopping tab works the same way."),
        ("Which formulas can I use?",
         "The workbook is built for Excel 2010: SUM, SUMIFS, COUNTIFS, "
         "INDEX, MATCH, IF, IFERROR, TEXT and their friends. Avoid "
         "XLOOKUP, FILTER, SORT and the other newer functions."),
        ("Why does the Calendar week start on Monday?",
         "That is the house style for this workbook. WEEKDAY(date,2) is "
         "used throughout so Monday is day 1."),
        ("How do I track events and dinner parties?",
         "The Events tab. Give the event a date, a guest count and a "
         "budget, then pick the dishes and the tab works out the cost per "
         "head."),
        ("What is the waste reduction target?",
         "A percentage of the grocery spend you are aiming to throw away. "
         "Set it on the Settings tab - 5% is a good target to start with."),
    ]
    row = 6
    for q, a in qa:
        ws.write(row, 0, q, f["calc_bold"])
        ws.write(row, 1, a, f["input_text_wrap"])
        ws.set_row(row, 32)
        row += 1

    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 1, "  WHAT THE COLOURS MEAN", f["section"])
    row += 1
    ws.write(row, 0, "Colour", f["header"])
    ws.write(row, 1, "What it means", f["header"])
    row += 1
    colours = [
        ("Yellow / cream", "Your input - type here", "input_text"),
        ("Grey", "Calculated - leave alone", "calc_text"),
        ("Dark green", "Headers and titles", "header"),
        ("Green", "Within budget / goal hit / fresh", "status_good"),
        ("Amber", "Close to budget / use soon", "status_warn"),
        ("Red", "Over budget / expired / missed", "status_bad"),
    ]
    for label, meaning, key in colours:
        ws.write(row, 0, label, f[key])
        ws.write(row, 1, meaning, f["calc_text"])
        row += 1

    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 1, "  STILL STUCK?", f["section"])
    row += 1
    ws.set_row(row, 28)
    ws.merge_range(row, 0, row, 1,
                   "Every calculated cell shows its formula in the formula "
                   "bar - click one and read it. The formulas are written "
                   "to be read: the piece in square brackets is the column "
                   "they are reading from.", f["card_value"])

    ws.set_tab_color(Palette.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.print_area(0, 0, row + 1, 3)
