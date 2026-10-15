"""
Dashboard - the week at a glance.

Pick the week at the top and the page shows the meals you have planned, the
calories and the cost of the week, what is about to expire, which meals are
overdue for another turn and how your habits are going.  Everything here is
calculated - there is nothing to type in except the week itself.
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
        name="Dashboard",
        title="Dashboard",
        subtitle="The week at a glance - meals, calories, cost, expiry dates "
                 "and habits",
        columns=[
            Col("metric", "Metric", 26, "text"),
            Col("label", "Label", 22, "text"),
            Col("week_start", "Week starting", 14, "text"),
            Col("detail", "Detail", 16, "text"),
            Col("spacer", " ", 3, "text"),
            Col("month_name", "Month", 16, "text"),
            Col("value", "Value", 14, "text"),
            Col("note", "Note", 30, "text_wrap"),
            Col("trend", "Trend", 14, "text"),
            Col("target", "Target", 14, "text"),
            Col("status", "Status", 16, "text"),
            Col("action", "Action", 22, "text"),
            Col("kpi_a", "A", 12, "text"),
            Col("kpi_b", "B", 12, "text"),
            Col("kpi_c", "C", 12, "text"),
            Col("kpi_d", "D", 12, "text"),
            Col("kpi_e", "E", 12, "text"),
            Col("kpi_f", "F", 12, "text"),
        ],
        rows=1,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i in range(18):
        ws.set_column(i, i, 13 if i else 24)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 17, "DASHBOARD", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 17,
                   "The week at a glance - meals, calories, cost, expiry "
                   "dates and habits", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 17,
                   "  |  Start Here   |   Weekly Planner   |   Meal Plan   "
                   "|   Grocery List   |   Pantry   |   Reports",
                   f["nav"])

    # ---- week picker -------------------------------------------------------
    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 17, "  WHICH WEEK ARE YOU LOOKING AT?",
                   f["section"])
    ws.write(5, 1, "Week starting", f["label"])
    ws.write_string(5, 2, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write_formula(6, 2, "=DATEVALUE($C$6)", f["calc_date"])
    ws.write(5, 5, "Month", f["label"])
    ws.write_formula(5, 6, '=TEXT($C$7,"mmmm yyyy")', f["calc_bold"])
    ws.write(5, 8, "Household", f["label"])
    ws.write_formula(5, 9, "=Household_Name", f["calc_text"])
    ws.write(5, 11, "People", f["label"])
    ws.write_formula(5, 12, "=Household_Size", f["calc_number"])
    ws.write(5, 14, "Servings", f["label"])
    ws.write_formula(5, 15, "=Default_Servings", f["calc_number"])
    ws.write(6, 1, "Shopping day", f["label"])
    ws.write_formula(6, 2, "=Shopping_Day", f["calc_text"])
    ws.write(6, 5, "Prep day", f["label"])
    ws.write_formula(6, 6, "=Prep_Day", f["calc_text"])
    ws.write(6, 8, "Weekly budget", f["label"])
    ws.write_formula(6, 9, "=Weekly_Budget", f["calc_money"])

    mp_week = reg.rng("Meal Plan", "week_start")
    mp_date = reg.rng("Meal Plan", "date")
    mp_slot = reg.rng("Meal Plan", "slot")
    mp_recipe = reg.rng("Meal Plan", "recipe")
    mp_cal = reg.rng("Meal Plan", "calories")
    mp_cost = reg.rng("Meal Plan", "cost")
    mp_status = reg.rng("Meal Plan", "status")
    gl_buy = reg.rng("Grocery List", "buy")
    gl_needed = reg.rng("Grocery List", "needed")
    pan_status = reg.rng("Pantry", "use_by_status")
    lo_days = reg.rng("Leftovers", "days_left")

    # ---- KPI tiles ---------------------------------------------------------
    ws.set_row(8, 22)
    ws.merge_range(8, 0, 8, 17, "  THIS WEEK", f["section"])
    kpis = [
        ("Meals planned", f'=COUNTIFS({mp_week},$C$7)', "kpi_value",
         "rows on the Meal Plan", 0),
        ("Calories a day", f'=IFERROR(SUMIFS({mp_cal},{mp_week},$C$7)/'
                           f'MAX(1,Household_Size)/7,0)', "kpi_value",
         f'= "target "&TEXT(Calorie_Target,"#,##0")', 3),
        ("Grocery cost", f'=SUMIFS({mp_cost},{mp_week},$C$7)',
         "kpi_value_money", f'= "budget "&TEXT(Weekly_Budget,"#,##0.00")',
         6),
        ("Budget left", f'=Weekly_Budget-SUMIFS({mp_cost},{mp_week},$C$7)',
         "kpi_value_money", "planned vs budget", 9),
        ("Items to buy", f'=COUNTIFS({gl_buy},"Yes")', "kpi_value",
         "on the grocery list", 12),
        ("Use it or lose it", f'=COUNTIFS({pan_status},"Use soon")'
                              f'+COUNTIFS({pan_status},"Expired")',
         "kpi_value", "pantry items", 15),
    ]
    for label, formula, style, sub, col in kpis:
        ws.merge_range(9, col, 9, col + 2, label, f["kpi_label"])
        ws.merge_range(10, col, 10, col + 2, None, f[style])
        ws.write_formula(10, col, formula, f[style])
        ws.merge_range(11, col, 11, col + 2, None, f["kpi_sub"])
        if isinstance(sub, str) and sub.startswith("="):
            ws.write_formula(11, col, sub, f["kpi_sub"])
        else:
            ws.write_string(11, col, sub, f["kpi_sub"])
    ws.set_row(10, 34)

    # ---- the week day by day ------------------------------------------------
    row = 13
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17, "  YOUR WEEK", f["section"])
    row += 1
    headers = ["Day", "Date", "Breakfast", "Lunch", "Dinner", "Snack",
               "Calories", "Cost", "Status"]
    for i, head in enumerate(headers):
        ws.write(row, i, head, f["header"])
    row += 1
    for offset in range(7):
        r = row + 1
        ws.write_formula(row, 0, f'=TEXT($C$7+{offset},"ddd")',
                         f["calc_bold"])
        ws.write_formula(row, 1, f'=$C$7+{offset}', f["calc_date"])
        for i, slot in enumerate(["Breakfast", "Lunch", "Dinner",
                                  "Afternoon snack"]):
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({mp_recipe},MATCH(1,INDEX('
                f'({mp_date}=$B{r})*({mp_slot}="{slot}"),0),0)),"")',
                f["calc_text"])
        ws.write_formula(row, 6,
                         f'=SUMIFS({mp_cal},{mp_date},$B{r})',
                         f["calc_number"])
        ws.write_formula(row, 7,
                         f'=SUMIFS({mp_cost},{mp_date},$B{r})',
                         f["calc_money"])
        ws.write_formula(row, 8,
                         f'=IF(COUNTIFS({mp_date},$B{r})=0,"Nothing planned",'
                         f'TEXT(COUNTIFS({mp_date},$B{r},{mp_status},'
                         f'"Cooked")+COUNTIFS({mp_date},$B{r},{mp_status},'
                         f'"Eaten"),"0")&" of "&'
                         f'TEXT(COUNTIFS({mp_date},$B{r}),"0")&" cooked")',
                         f["calc_center"])
        row += 1
    ws.write(row, 0, "Week", f["total_label"])
    ws.write_blank(row, 1, None, f["total_label"])
    for i in range(2, 6):
        ws.write_blank(row, i, None, f["total_label"])
    ws.write_formula(row, 6, f'=SUMIFS({mp_cal},{mp_week},$C$7)',
                     f["total_number"])
    ws.write_formula(row, 7, f'=SUMIFS({mp_cost},{mp_week},$C$7)',
                     f["total_money"])
    ws.write_formula(row, 8,
                     f'=TEXT(IFERROR(SUMIFS({mp_cal},{mp_week},$C$7)/'
                     f'MAX(1,Household_Size)/7/Calorie_Target,0),"0%")'
                     f'&" of target"', f["total_label"])
    row += 2

    # ---- overdue meals -------------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17,
                   "  MEALS OVERDUE FOR ANOTHER TURN", f["section"])
    row += 1
    for i, head in enumerate(["Rank", "Recipe", "Last cooked", "Days since",
                              "Rating", "Cost / serving"]):
        ws.write(row, i, head, f["header"])
    row += 1
    rot = reg.rng("Recipes", "rotation_rank")
    for n in range(1, 6):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["recipe", "last_planned", "days_since",
                                 "rating", "cost_per_serving"]):
            rng = reg.rng("Recipes", key)
            ws.write_formula(
                row, 1 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{rot},0)),"")',
                f["calc_date"] if key == "last_planned"
                else (f["calc_money"] if key == "cost_per_serving"
                      else (f["calc_number"] if key in ("days_since",
                                                        "rating")
                            else f["calc_text"])))
        row += 1
    row += 1

    # ---- cheapest meals ------------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17,
                   "  CHEAPEST MEALS IN YOUR RECIPE BOOK", f["section"])
    row += 1
    for i, head in enumerate(["Rank", "Recipe", "Cost / serving",
                              "Calories", "Total time (min)",
                              "Cost / 1000 kcal"]):
        ws.write(row, i, head, f["header"])
    row += 1
    cost_rank = reg.rng("Recipes", "cost_rank")
    for n in range(1, 6):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["recipe", "cost_per_serving", "calories",
                                 "total_time", "cost_per_1000_cal"]):
            rng = reg.rng("Recipes", key)
            ws.write_formula(
                row, 1 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{cost_rank},0)),"")',
                f["calc_money"] if key in ("cost_per_serving",
                                           "cost_per_1000_cal")
                else (f["calc_number"] if key in ("calories", "total_time")
                      else f["calc_text"]))
        row += 1
    row += 1

    # ---- use it or lose it ----------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17,
                   "  USE IT OR LOSE IT", f["section"])
    row += 1
    for i, head in enumerate(["Rank", "Item", "Days left", "Quantity",
                              "Storage", "Status"]):
        ws.write(row, i, head, f["header"])
    row += 1
    fridge_rank = reg.rng("Pantry", "fridge_rank")
    for n in range(1, 7):
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["item", "days_left", "quantity",
                                 "storage", "use_by_status"]):
            rng = reg.rng("Pantry", key)
            ws.write_formula(
                row, 1 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{fridge_rank},0)),"")',
                f["calc_number"] if key in ("days_left", "quantity")
                else f["calc_text"])
        row += 1
    row += 1

    # ---- habits and alerts -----------------------------------------------------
    ws.set_row(row, 22)
    ws.merge_range(row, 0, row, 17, "  HABITS AND ALERTS", f["section"])
    row += 1
    ws.write(row, 0, "Habit", f["header"])
    ws.write(row, 2, "This month", f["header"])
    ws.write(row, 4, "Target", f["header"])
    ws.write(row, 6, "Status", f["header"])
    row += 1
    mp_month = reg.rng("Meal Plan", "month")
    month_cell = "$G$6"
    habits = [
        ("Home cooked meals", f'=COUNTIFS({mp_month},{month_cell},'
                              f'{mp_status},"Cooked")'
                              f'+COUNTIFS({mp_month},{month_cell},'
                              f'{mp_status},"Eaten")',
         "=Home_Cooked_Target*4", "number"),
        ("Takeaways and meals out", f'=COUNTIFS({mp_month},{month_cell},'
                                    f'{mp_status},"Takeaway")'
                                    f'+COUNTIFS({mp_month},{month_cell},'
                                    f'{mp_status},"Eating out")',
         "=Takeaway_Limit", "number"),
        ("New recipes tried", f'=COUNTIFS({reg.rng("Recipes", "added_on")},'
                              f'">="&DATE(Plan_Year,1,1),'
                              f'{reg.rng("Recipes", "added_on")},'
                              f'"<="&DATE(Plan_Year,12,31))',
         "=New_Recipe_Target*12", "number"),
    ]
    for label, formula, target, kind in habits:
        ws.merge_range(row, 0, row, 1, label, f["label"])
        ws.write_formula(row, 2, formula, f["calc_number"])
        ws.write_formula(row, 4, target, f["calc_number"])
        ws.write_formula(row, 6,
                         f'=IF($C{row + 1}>=$E{row + 1},"On target",'
                         f'"Behind target")', f["calc_badge"])
        row += 1

    alerts = [
        ("Grocery spend vs weekly budget",
         f'=Weekly_Budget-SUMIFS({mp_cost},{mp_week},$C$7)',
         f'=IF(SUMIFS({mp_cost},{mp_week},$C$7)>Weekly_Budget,'
         f'"Over budget","Within budget")'),
        ("Waste cost vs target",
         f'=Waste_Cost_Target-SUMIFS({reg.rng("Food Waste", "cost")},'
         f'{reg.rng("Food Waste", "month")},{month_cell})',
         f'=IF(SUMIFS({reg.rng("Food Waste", "cost")},'
         f'{reg.rng("Food Waste", "month")},{month_cell})>'
         f'Waste_Cost_Target,"Over target","On target")'),
        ("Items running low",
         f'=COUNTIFS({reg.rng("Ingredients", "buy_this_week")},"Yes")',
         f'=IF(COUNTIFS({reg.rng("Ingredients", "buy_this_week")},"Yes")'
         f'>0,"Add to the list","Nothing needed")'),
        ("Dietary checks flagged",
         f'=COUNTIFS({reg.rng("Meal Plan", "allergy_flag")},"Check")',
         f'=IF(COUNTIFS({reg.rng("Meal Plan", "allergy_flag")},"Check")>0,'
         f'"Check the plan","All clear")'),
        ("Leftovers to eat",
         f'=COUNTIFS({lo_days},">=0")',
         f'=IF(COUNTIFS({lo_days},"<=1")>0,"Eat something today",'
         f'"Nothing urgent")'),
    ]
    for label, formula, status in alerts:
        ws.merge_range(row, 0, row, 1, label, f["label"])
        ws.write_formula(row, 2, formula, f["calc_money"])
        ws.write_blank(row, 4, None, f["calc_text"])
        ws.merge_range(row, 6, row, 8, None, f["calc_badge"])
        ws.write_formula(row, 6, status, f["calc_badge"])
        row += 1

    writer.write_note(ws, row + 1, 0,
                      "Everything on this page is calculated. Change the "
                      "week at the top, or the month in the cell next to "
                      "'Month', and the whole dashboard follows.", width=17)

    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.hide_gridlines(2)
    ws.print_area(0, 0, row + 2, 17)
