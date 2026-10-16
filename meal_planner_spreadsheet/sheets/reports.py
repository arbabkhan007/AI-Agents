"""
Reports - any date range, on one page.

Set the from and to dates at the top and every table below re-calculates:
what you spent, where you spent it, what you threw away and why, how the
nutrition looked, which meals you cooked most and which ingredients you buy
most often.  Nothing here needs a chart - the numbers are the report.
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
        name="Reports",
        title="Reports",
        subtitle="Spend, nutrition, waste, variety and cooking habits for any "
                 "date range",
        columns=[
            Col("metric", "Metric", 30, "text"),
            Col("value", "Value", 16, "text"),
            Col("previous", "Previous", 16, "text"),
            Col("change", "Change", 14, "text"),
            Col("note", "Note", 40, "text_wrap"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.primary,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, width in enumerate([34, 18, 18, 16, 44]):
        ws.set_column(i, i, width)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 4, "REPORTS", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 4,
                   "Spend, nutrition, waste, variety and cooking habits for "
                   "any date range", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 4,
                   "  |  Dashboard   |   Grocery Spending   |   Food Waste   "
                   "|   Nutrition   |   Meal Plan", f["nav"])

    # ---- date range --------------------------------------------------------
    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 4, "  REPORTING PERIOD", f["section"])
    ws.write(5, 0, "From", f["label"])
    ws.write_string(5, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(5, 2, "To", f["label"])
    ws.write_string(5, 3, "", f["input_text"])
    ws.write(5, 4, "Type the dates as yyyy-mm-dd.", f["note"])

    # helper cells: real dates so SUMIFS can compare them
    ws.write_formula(6, 0, '=DATEVALUE($B$6)', f["calc_date"])
    ws.write_formula(6, 1, '=IF($D$6="",TODAY(),DATEVALUE($D$6))',
                     f["calc_date"])
    ws.write(6, 2, "Days in period", f["label"])
    ws.write_formula(6, 3, '=$B$7-$A$7+1', f["calc_number"])
    ws.write(6, 4, "The two grey cells turn your text into real dates.",
             f["note"])

    gs_date = reg.rng("Grocery Spending", "date")
    gs_total = reg.rng("Grocery Spending", "line_total")
    gs_store = reg.rng("Grocery Spending", "store")
    gs_item = reg.rng("Grocery Spending", "item")
    gs_cat = reg.rng("Grocery Spending", "category")
    fw_date = reg.rng("Food Waste", "date")
    fw_cost = reg.rng("Food Waste", "cost")
    fw_qty = reg.rng("Food Waste", "qty")
    fw_reason = reg.rng("Food Waste", "reason")
    mp_date = reg.rng("Meal Plan", "date")
    mp_status = reg.rng("Meal Plan", "status")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    nu_date = reg.rng("Nutrition", "date")
    nu_cal = reg.rng("Nutrition", "calories")

    def sumifs(value_rng, date_rng):
        return (f'SUMIFS({value_rng},{date_rng},">="&$A$7,'
                f'{date_rng},"<="&$B$7)')

    def countifs(date_rng, extra=""):
        return (f'COUNTIFS({date_rng},">="&$A$7,'
                f'{date_rng},"<="&$B$7{extra})')

    # ---- headline numbers --------------------------------------------------
    row = 8
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  HEADLINE NUMBERS", f["section"])
    row += 1
    cooked_total = (countifs(mp_date, ',"Cooked"') + "+"
                    + countifs(mp_date, ',"Eaten"'))
    takeaways_total = (countifs(mp_date, ',"Takeaway"') + "+"
                       + countifs(mp_date, ',"Eating out"'))
    headlines = [
        ("Grocery spend", sumifs(gs_total, gs_date), "money",
         "Everything recorded on the Grocery Spending tab."),
        ("Shops recorded", countifs(gs_date), "number",
         "How many spending rows fall inside the period."),
        ("Average shop", f'IFERROR({sumifs(gs_total, gs_date)}/'
                         f'MAX(1,{countifs(gs_date)}),0)', "money", ""),
        ("Weekly average", f'IFERROR({sumifs(gs_total, gs_date)}/'
                           f'MAX(1,$D$7/7),0)', "money",
         "Compared with the weekly budget on Settings."),
        ("Vs weekly budget", f'IFERROR({sumifs(gs_total, gs_date)}/'
                             f'MAX(1,$D$7/7)-Weekly_Budget,0)', "money", ""),
        ("Meals planned", countifs(mp_date), "number", ""),
        ("Meals cooked", cooked_total, "number", ""),
        ("Takeaways / eating out", takeaways_total, "number", ""),
        ("Home cooked %", f'IFERROR(({cooked_total})/'
                          f'MAX(1,{countifs(mp_date)}),0)', "percent", ""),
        ("Waste cost", sumifs(fw_cost, fw_date), "money", ""),
        ("Waste quantity", sumifs(fw_qty, fw_date), "number", ""),
        ("Waste as % of spend", f'IFERROR({sumifs(fw_cost, fw_date)}/'
                                f'MAX(1,{sumifs(gs_total, gs_date)}),0)',
         "percent", "Target is set on Settings."),
        ("Average calories a day", f'IFERROR({sumifs(nu_cal, nu_date)}/'
                                   f'MAX(1,COUNTIFS({nu_date},">="&$A$7,'
                                   f'{nu_date},"<="&$B$7)),0)', "number", ""),
    ]
    for label, formula, kind, note in headlines:
        ws.write(row, 0, label, f["label"])
        style = {"money": f["total_money"], "number": f["total_number"],
                 "percent": f["total_percent"]}[kind]
        ws.write_formula(row, 1, "=" + formula, style)
        if note:
            ws.write(row, 4, note, f["note"])
        row += 1

    # ---- spend by store ----------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  SPEND BY STORE", f["section"])
    row += 1
    for store in ["Greenfield Market", "Corner Grocer", "Bulk Barn",
                  "Farmers Market", "Asian Supermarket"]:
        ws.write(row, 0, store, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({gs_total},{gs_store},$A{row + 1},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=COUNTIFS({gs_store},$A{row + 1},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_number"])
        ws.write(row, 3, "visits", f["note"])
        row += 1

    # ---- spend by category --------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  SPEND BY CATEGORY", f["section"])
    row += 1
    for category in ["Vegetables", "Fruit", "Meat & Fish", "Dairy & Eggs",
                     "Bakery", "Grains & Pasta", "Tins & Jars", "Frozen",
                     "Snacks", "Drinks", "Household"]:
        ws.write(row, 0, category, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({gs_total},{gs_cat},$A{row + 1},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=IFERROR(SUMIFS({gs_total},{gs_cat},'
                         f'$A{row + 1},{gs_date},">="&$A$7,'
                         f'{gs_date},"<="&$B$7)/MAX(1,'
                         f'SUMIFS({gs_total},{gs_date},">="&$A$7,'
                         f'{gs_date},"<="&$B$7)),0)', f["total_percent"])
        ws.write(row, 3, "of spend", f["note"])
        row += 1

    # ---- waste by reason -----------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  WASTE BY REASON", f["section"])
    row += 1
    for reason in ["Expired", "Spoiled", "Mouldy", "Leftover not eaten",
                   "Cooked too much", "Burnt", "Tasted bad",
                   "Bought too much", "Child refused", "Plans changed"]:
        ws.write(row, 0, reason, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({fw_cost},{fw_reason},$A{row + 1},'
                         f'{fw_date},">="&$A$7,{fw_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=SUMIFS({fw_qty},{fw_reason},$A{row + 1},'
                         f'{fw_date},">="&$A$7,{fw_date},"<="&$B$7)',
                         f["total_number"])
        ws.write(row, 3, "quantity", f["note"])
        row += 1

    # ---- most cooked meals ---------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  MOST COOKED MEALS", f["section"])
    row += 1
    ws.write(row, 0, "Recipe", f["header"])
    ws.write(row, 1, "Times cooked", f["header"])
    ws.write(row, 2, "Last cooked", f["header"])
    ws.write(row, 3, "Cost / serving", f["header"])
    ws.write(row, 4, "Rating", f["header"])
    row += 1
    for recipe in ["Chicken & veg traybake", "Spaghetti bolognese",
                   "Vegetable curry", "Salmon & rice", "Beef chilli",
                   "Pizza night", "Pasta primavera", "Fish finger sandwich"]:
        r = row + 1
        ws.write(row, 0, recipe, f["label"])
        ws.write_formula(row, 1,
                         f'=COUNTIFS({mp_recipe},$A{r},{mp_date},'
                         f'">="&$A$7,{mp_date},"<="&$B$7,'
                         f'{mp_status},"Cooked")'
                         f'+COUNTIFS({mp_recipe},$A{r},{mp_date},'
                         f'">="&$A$7,{mp_date},"<="&$B$7,'
                         f'{mp_status},"Eaten")', f["total_number"])
        ws.write_formula(row, 2,
                         f'=IF(SUMPRODUCT(MAX(({mp_recipe}=$A{r})*'
                         f'{mp_date}))=0,"",'
                         f'SUMPRODUCT(MAX(({mp_recipe}=$A{r})*{mp_date})))',
                         f["calc_date"])
        ws.write_formula(row, 3,
                         '=IFERROR(INDEX(' + reg.rng("Recipes",
                                                     "cost_per_serving")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Recipes", "recipe") + ',0)),"")',
                         f["calc_money"])
        ws.write_formula(row, 4,
                         '=IFERROR(INDEX(' + reg.rng("Recipes", "rating")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Recipes", "recipe") + ',0)),"")',
                         f["calc_number"])
        row += 1

    # ---- top ingredients ------------------------------------------------------
    row += 1
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 4, "  TOP INGREDIENTS BY SPEND", f["section"])
    row += 1
    ws.write(row, 0, "Ingredient", f["header"])
    ws.write(row, 1, "Spend in period", f["header"])
    ws.write(row, 2, "Times bought", f["header"])
    ws.write(row, 3, "Last price", f["header"])
    ws.write(row, 4, "Average price", f["header"])
    row += 1
    for item in ["Chicken breast", "Rice", "Eggs", "Milk", "Bread",
                 "Cheddar cheese", "Pasta", "Tinned tomatoes"]:
        r = row + 1
        ws.write(row, 0, item, f["label"])
        ws.write_formula(row, 1,
                         f'=SUMIFS({gs_total},{gs_item},$A{r},'
                         f'{gs_date},">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_money"])
        ws.write_formula(row, 2,
                         f'=COUNTIFS({gs_item},$A{r},{gs_date},'
                         f'">="&$A$7,{gs_date},"<="&$B$7)',
                         f["total_number"])
        ws.write_formula(row, 3,
                         '=IFERROR(INDEX(' + reg.rng("Ingredients",
                                                     "last_price")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Ingredients", "ingredient") + ',0)),'
                         '"")', f["calc_money"])
        ws.write_formula(row, 4,
                         '=IFERROR(INDEX(' + reg.rng("Ingredients",
                                                     "avg_price")
                         + ',MATCH($A' + str(r) + ','
                         + reg.rng("Ingredients", "ingredient") + ',0)),'
                         '"")', f["calc_money"])
        row += 1

    writer.write_note(ws, row + 1, 0,
                      "Every table reads the Grocery Spending, Food Waste, "
                      "Meal Plan and Nutrition tabs, so they fill in as you "
                      "record your shops and your meals. Change the dates at "
                      "the top of the page to re-cut the whole report.",
                      width=4)

    ws.set_tab_color(Palette.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.hide_gridlines(2)
    ws.print_area(0, 0, row + 2, 4)
