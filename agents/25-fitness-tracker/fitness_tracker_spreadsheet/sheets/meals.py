"""11 Meals & Macros - food log plus the shipped calorie database.

The buyer types calories and macros by row; when the food name matches
the reference database on the right of this tab, leaving a macro blank
pulls the reference value instead.  Nothing pretends to know your
portion: typed always wins, and incomplete rows say so instead of
silently counting as zero.
"""

from __future__ import annotations

from ..config import Config
from ..food_data import FOODS
from ..layout import Col, SheetSpec, col_letter, quote_sheet
from ..writer import (SheetWriter, cf_text, date_check, list_from,
                      number_check)
from .. import sample_data

NAME = "11 Meals & Macros"

#: database block starts two columns right of the register
DB_GAP = 2


def _ref(col_name: str) -> str:
    return f'IFERROR(INDEX({col_name},MATCH({{food}}{{r}},FoodNames,0)),"")'


def spec(cfg: Config) -> SheetSpec:
    cols = [
        Col("id", "ID", 8, "id",
            formula='="F-"&TEXT(ROW()-{first}+1,"000")'),
        Col("date", "Date", 12, "date", validate=date_check()),
        Col("meal", "Meal", 11, "text", validate=list_from("ListMeal")),
        Col("food", "Food", 28, "text",
            note="Type anything. If it matches the database on the "
                 "right, blank macro cells fill from it."),
        Col("cal_in", "kcal (typed)", 11, "int",
            validate=number_check(0, 5000, False)),
        Col("p_in", "Protein g", 10, "number1",
            validate=number_check(0, 300)),
        Col("c_in", "Carbs g", 10, "number1",
            validate=number_check(0, 500)),
        Col("f_in", "Fat g", 9, "number1",
            validate=number_check(0, 300)),
        Col("cal_ref", "kcal ref", 9, "int", hidden=True,
            formula="=" + _ref("FoodKcal")),
        Col("p_ref", "P ref", 8, "number1", hidden=True,
            formula="=" + _ref("FoodP")),
        Col("c_ref", "C ref", 8, "number1", hidden=True,
            formula="=" + _ref("FoodC")),
        Col("f_ref", "F ref", 8, "number1", hidden=True,
            formula="=" + _ref("FoodF")),
        Col("cal_used", "kcal used", 10, "int",
            formula='IF({date}{r}="","",IF({cal_in}{r}<>"",{cal_in}{r},'
                    '{cal_ref}{r}))'),
        Col("p_used", "Protein used", 11, "number1",
            formula='IF({date}{r}="","",IF({p_in}{r}<>"",{p_in}{r},'
                    '{p_ref}{r}))'),
        Col("c_used", "Carbs used", 10, "number1",
            formula='IF({date}{r}="","",IF({c_in}{r}<>"",{c_in}{r},'
                    '{c_ref}{r}))'),
        Col("f_used", "Fat used", 9, "number1",
            formula='IF({date}{r}="","",IF({f_in}{r}<>"",{f_in}{r},'
                    '{f_ref}{r}))'),
        Col("fibre", "Fibre g", 9, "number1",
            validate=number_check(0, 100)),
        Col("sugar", "Sugar g", 9, "number1",
            validate=number_check(0, 200)),
        Col("sodium", "Sodium mg", 10, "int",
            validate=number_check(0, 10000, False)),
        Col("x1", "Custom 1", 10, "number1"),
        Col("x2", "Custom 2", 10, "number1"),
        Col("complete", "Row status", 11, "status",
            formula='IF({date}{r}="","",IF(OR({cal_used}{r}="",{p_used}{r}'
                    '="",{c_used}{r}="",{f_used}{r}=""),"incomplete",'
                    '"logged"))',
            cf=[cf_text("incomplete", "warn"),
                cf_text("logged", "good")]),
        Col("notes", "Notes", 22, "wrap"),
    ]
    return SheetSpec(
        name=NAME,
        title="11  Meals & Macros",
        subtitle="Log by meal against your targets - the 200-item calorie "
                 "database on the right fills blanks, typed numbers win.",
        tab_color="#14655A",
        rows=cfg.row_count("Meals & Macros"),
        freeze_cols=4,
        help_text="Cream macro cells: type your number, or leave blank "
                  "and let the database fill it when the food name "
                  "matches. The day block under the register totals "
                  "everything against your targets.",
        columns=cols,
        samples=sample_data.meal_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    """The calorie database block + the day totals block."""
    spec_ = reg[NAME]
    q = quote_sheet(NAME)
    db_col0 = spec_.last_col_index + 1 + DB_GAP
    head = spec_.header_row - 1
    heads = ["Food", "Category", "Serving", "kcal", "Protein g",
             "Carbs g", "Fat g"]
    widths = [30, 13, 14, 8, 10, 9, 8]
    for i, text in enumerate(heads):
        sheet.write(head, db_col0 + i, text, sheet.f.chrome("header"))
        sheet.set_col(db_col0 + i, db_col0 + i, widths[i])
    sheet.merge(head, db_col0 + 7, db_col0 + 12,
                "CALORIE DATABASE - edit freely, blanks fill from here",
                sheet.f.chrome("section"))
    first = spec_.first_data_row
    capacity = cfg.row_count("Food Database")
    for offset, row in enumerate(FOODS):
        if offset >= capacity:
            break
        excel = first + offset
        for i, value in enumerate(row):
            style = "text" if i < 3 else ("int" if i == 3 else "number1")
            sheet.write(excel - 1, db_col0 + i, value,
                        sheet.f.input(style))
    last_db = first + min(capacity, len(FOODS)) - 1
    letters = [col_letter(db_col0 + i) for i in range(7)]
    for name, letter in [("FoodNames", letters[0]),
                         ("FoodKcal", letters[3]),
                         ("FoodP", letters[4]),
                         ("FoodC", letters[5]),
                         ("FoodF", letters[6])]:
        sheet.book.define_name(
            name,
            f"=OFFSET({q}!${letter}${first},0,0,MAX(1,COUNTIF("
            f"{q}!${letter}${first}:${letter}${last_db},\"?*\")),1)")

    # ---- day totals block under the register
    d = f"{q}!${spec_.letter('date')}${first}:${spec_.letter('date')}" \
        f"${spec_.last_data_row}"
    used = {k: f"{q}!${spec_.letter(k)}${first}:${spec_.letter(k)}"
                 f"${spec_.last_data_row}"
            for k in ("cal_used", "p_used", "c_used", "f_used")}
    top = spec_.last_data_row + 3
    row = sheet.section(top, "A DAY AGAINST YOUR TARGETS", 8)
    row = sheet.field(row, "Pick a date", cfg.today, style="date",
                      label_col=0, value_col=2,
                      help_text="Every total below reads this date.")
    pick = f"$C${row}"
    rows = [
        ("Calories", "cal_used", "CalTarget", "int"),
        ("Protein (g)", "p_used", "ProteinTarget", "int"),
        ("Carbohydrate (g)", "c_used", "CarbTarget", "int"),
        ("Fat (g)", "f_used", "FatTarget", "int"),
    ]
    row = sheet.table_head(row, 0, ["", "Logged", "Target", "Gap"],
                           widths=[22, 10, 10, 10])
    for label, key, target in [(a, b, c) for a, b, c, _ in rows]:
        sheet.write(row, 0, label, sheet.f.calc("text"))
        sheet.formula(row, 1, f'=SUMIFS({used[key]},{d},"="&{pick})',
                      sheet.f.calc("int"))
        sheet.formula(row, 2, f"={target}", sheet.f.calc("int"))
        sheet.formula(row, 3, f'=IF(B{row + 1}="","",B{row + 1}-C{row + 1})',
                      sheet.f.calc("int"))
        row += 1
    sheet.formula(row, 0,
                  f'=IF(SUMIFS({used["cal_used"]},{d},"="&{pick})=0,"No '
                  f'food logged for this date yet - the day block stays '
                  f'empty rather than pretending.","")',
                  sheet.f.chrome("note"))
    row += 2
    sheet.formula(row, 0,
                  f'=IF(OR(StartKg="",StartKg=0),"","Protein today per kg '
                  f'body weight: "&TEXT(IFERROR(SUMIFS({used["p_used"]},'
                  f'{d},"="&{pick})/StartKg,""),"0.00")&" g/kg")',
                  sheet.f.chrome("label"))
    sheet.finish(freeze_row=4, freeze_col=2,
                 print_area=f"$A$1:${col_letter(spec_.last_col_index)}$"
                            f"{spec_.last_data_row}")
