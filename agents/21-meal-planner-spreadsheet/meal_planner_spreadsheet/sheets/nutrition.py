"""
Nutrition - the daily log against your targets.

Either type a recipe in (the nutrition is looked up from the Recipes tab)
or type the numbers straight in.  The percentages compare the day with the
targets you set on Settings, and the summary block at the top shows the
monthly averages for whatever month you pick.
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

    columns = [
        Col("date", "Date", 12, "date", group="when"),
        Col("month", "Month", 11, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"mmm yyyy"))'),
        Col("weekday", "Day", 8, "calc",
            formula='=IF({date}{r}="","",TEXT({date}{r},"ddd"))'),
        Col("slot", "Meal slot", 15, "select",
            validate={"type": "list",
                      "source": "=" + lists("Lists", "meal_slot")}),
        Col("recipe", "Recipe", 26, "select",
            validate={"type": "list", "source": "=" + recipes}),
        Col("servings", "Servings", 10, "number",
            validate={"type": "decimal", "between": 0, "and": 100}),
        Col("calories", "Calories", 10, "calc", group="actual",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("calories"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("protein", "Protein (g)", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("protein"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("carbs", "Carbs (g)", 10, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("carbs"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("fat", "Fat (g)", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("fat"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("fibre", "Fibre (g)", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("fibre"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("sugar", "Sugar (g)", 9, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("sugar"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("sodium", "Sodium (mg)", 11, "calc",
            formula='=IF({recipe}{r}="","",'
                    'IFERROR(' + lookup("{recipe}{r}", recipes,
                                        rec("sodium"))
                    + '*IF({servings}{r}="",1,{servings}{r}),""))'),
        Col("water_glasses", "Water (glasses)", 12, "number",
            validate={"type": "decimal", "between": 0, "and": 30}),
        Col("calorie_target", "Calories target", 12, "calc",
            group="targets",
            formula='=IF({date}{r}="","",Calorie_Target*Household_Size)'),
        Col("calorie_pct", "% calories", 11, "calc",
            formula='=IF(OR({date}{r}="",{calorie_target}{r}=0),"",'
                    'IFERROR({calories}{r}/{calorie_target}{r},""))'),
        Col("protein_pct", "% protein", 11, "calc",
            formula='=IF(OR({date}{r}="",Protein_Target=0),"",'
                    'IFERROR({protein}{r}/(Protein_Target*'
                    'Household_Size),""))'),
        Col("carb_pct", "% carbs", 10, "calc",
            formula='=IF(OR({date}{r}="",Carb_Target=0),"",'
                    'IFERROR({carbs}{r}/(Carb_Target*'
                    'Household_Size),""))'),
        Col("fat_pct", "% fat", 10, "calc",
            formula='=IF(OR({date}{r}="",Fat_Target=0),"",'
                    'IFERROR({fat}{r}/(Fat_Target*Household_Size),""))'),
        Col("fibre_pct", "% fibre", 10, "calc",
            formula='=IF(OR({date}{r}="",Fibre_Target=0),"",'
                    'IFERROR({fibre}{r}/(Fibre_Target*Household_Size),'
                    '""))'),
        Col("sugar_pct", "% sugar limit", 11, "calc",
            formula='=IF(OR({date}{r}="",Sugar_Limit=0),"",'
                    'IFERROR({sugar}{r}/(Sugar_Limit*Household_Size),'
                    '""))'),
        Col("sodium_pct", "% sodium limit", 11, "calc",
            formula='=IF(OR({date}{r}="",Sodium_Limit=0),"",'
                    'IFERROR({sodium}{r}/(Sodium_Limit*Household_Size),'
                    '""))'),
        Col("status", "Status", 13, "calc",
            formula='=IF({date}{r}="","",'
                    'IF({calorie_pct}{r}="","",'
                    'IF({calorie_pct}{r}>1.1,"Over target",'
                    'IF({calorie_pct}{r}<0.8,"Under target",'
                    '"On target"))))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Nutrition",
        title="Nutrition",
        subtitle="Daily nutrition log against the targets set on Settings",
        columns=columns,
        rows=cfg.row_count("Nutrition"),
        header_row=18,
        tab_color=Palette.primary,
        freeze_cols=3,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    writer.grid_off(ws)
    ws.set_column(0, 0, 12)
    ws.set_column(1, 1, 11)
    ws.set_column(2, 2, 8)
    ws.set_column(3, 3, 15)
    ws.set_column(4, 4, 26)
    ws.set_column(5, 5, 10)
    for i in range(6, 21):
        ws.set_column(i, i, 11)
    ws.set_column(21, 21, 13)
    ws.set_column(22, 22, 30)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 8, "NUTRITION", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "Daily nutrition log against the targets set on "
                   "Settings", f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 8,
                   "  |  Dashboard   |   Settings   |   Meal Plan   |   "
                   "Recipes   |   Reports", f["nav"])

    # ---- month picker and monthly averages -------------------------------
    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 8, "  MONTH SUMMARY", f["section"])
    ws.write(5, 0, "Month", f["label"])
    ws.write_string(5, 1, cfg.today.strftime("%b %Y"), f["input_text"])
    ws.write(5, 2, "days logged", f["label"])
    ws.write_formula(
        5, 3, '=COUNTIFS(' + writer.registry.rng("Nutrition", "month")
        + ',$B$6)', f["calc_number"])

    cal = writer.registry.rng("Nutrition", "calories")
    mon = writer.registry.rng("Nutrition", "month")
    pro = writer.registry.rng("Nutrition", "protein")
    carb = writer.registry.rng("Nutrition", "carbs")
    fat = writer.registry.rng("Nutrition", "fat")
    fib = writer.registry.rng("Nutrition", "fibre")
    sug = writer.registry.rng("Nutrition", "sugar")
    sod = writer.registry.rng("Nutrition", "sodium")

    kpis = [
        ("Average calories", cal, "#,##0", 7),
        ("Average protein (g)", pro, "#,##0", 8),
        ("Average carbs (g)", carb, "#,##0", 9),
        ("Average fat (g)", fat, "#,##0", 10),
        ("Average fibre (g)", fib, "#,##0", 11),
        ("Average sugar (g)", sug, "#,##0", 12),
        ("Average sodium (mg)", sod, "#,##0", 13),
    ]
    for label, rng, num_format, col in kpis:
        ws.write(7, col, label, f["kpi_label"])
        ws.write_formula(8, col,
                         f'=IFERROR(AVERAGEIFS({rng},{mon},$B$6),0)',
                         f["kpi_value"])
        ws.write(9, col, f"= {label.split()[1]}", f["kpi_sub"])
    ws.set_row(8, 30)

    ws.write(11, 0, "Target", f["label"])
    ws.write_formula(11, 1, "=Calorie_Target*Household_Size",
                     f["calc_number"])
    ws.write(11, 2, "vs target", f["label"])
    ws.write_formula(11, 3,
                     '=IFERROR(AVERAGEIFS(' + cal + ',' + mon
                     + ',$B$6)/(Calorie_Target*Household_Size),"")',
                     f["calc_percent"])
    ws.write(11, 4, "days on target", f["label"])
    ws.write_formula(11, 5,
                     '=COUNTIFS(' + mon + ',$B$6,'
                     + writer.registry.rng("Nutrition", "status")
                     + ',"On target")', f["calc_number"])
    ws.write(11, 6, "days over", f["label"])
    ws.write_formula(11, 7,
                     '=COUNTIFS(' + mon + ',$B$6,'
                     + writer.registry.rng("Nutrition", "status")
                     + ',"Over target")', f["calc_number"])
    ws.write(11, 8, "days under", f["label"])
    ws.write_formula(11, 9,
                     '=COUNTIFS(' + mon + ',$B$6,'
                     + writer.registry.rng("Nutrition", "status")
                     + ',"Under target")', f["calc_number"])

    writer.write_note(ws, 13, 0,
                      "Type a recipe name in the Recipe column and the "
                      "nutrition is looked up for you. To enter the "
                      "numbers by hand instead, leave Recipe blank and "
                      "type over the calculated cells - the sheet is "
                      "protected, so unprotect it first if you want to "
                      "keep your own numbers.", width=9)

    # ---- the daily log ----------------------------------------------------
    writer.register(ws, spec)
    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.primary)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
