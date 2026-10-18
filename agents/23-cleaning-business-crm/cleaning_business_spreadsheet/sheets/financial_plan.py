"""Financial Plan - budget vs actuals, month by month."""

from __future__ import annotations

import datetime as dt
from typing import Any, List

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet
from .settings import settings_ref

# gentle seasonal shape of a cleaning year (Jan..Dec)
SEASONALITY = [0.88, 0.86, 0.95, 1.02, 1.08, 1.10, 1.05, 1.00,
               1.06, 1.02, 0.95, 1.03]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Financial Plan")
    ws.set_tab_color(Palette.primary_mid)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 12, 13)
    ws.set_column(13, 13, 16)

    def rng(sheet: str, key: str) -> str:
        spec = reg[sheet]
        letter = spec.letter(key)
        return (f"{quote_sheet(sheet)}!${letter}${spec.first_data_row}:"
                f"${letter}${spec.last_data_row}")

    J_date = rng("Jobs", "date")
    J_price = rng("Jobs", "price")
    J_status = rng("Jobs", "status")
    E_date = rng("Expenses", "date")
    E_amount = rng("Expenses", "amount")
    T_date = rng("Timesheets", "date")
    T_pay = rng("Timesheets", "pay")
    T_ot = rng("Timesheets", "overtime_pay")
    M_date = rng("Mileage", "date")
    M_claim = rng("Mileage", "claim")
    P_date = rng("Payments", "date")
    P_amount = rng("Payments", "amount")

    ws.merge_range(0, 1, 0, 13,
                   "Financial Plan  ·  Budget vs Actual",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 13,
                   f"The plan for {cfg.year}. Budget columns start you "
                   "off with a sensible split of your annual target - "
                   "overwrite them with your real plan. Actual columns "
                   "are live from the registers.",
                   fmts["subtitle"])

    ws.write(4, 1, "Plan year", fmts["label"])
    ws.write_formula(4, 2, '=Settings!$C$18', fmts["input_int"])
    ws.merge_range(4, 3, 4, 13,
                   "Change the year on Settings. Months are laid out "
                   "January to December below.", fmts["note"])
    year_cell = "$C$5"

    # header
    headers = [
        (1, "Month"), (2, "Rev budget"), (3, "Rev actual"), (4, "Var"),
        (5, "Cost budget"), (6, "Cost actual"), (7, "Var"),
        (8, "Profit plan"), (9, "Profit actual"), (10, "Var"),
        (11, "Cash in"), (12, "Status"), (13, "Notes"),
    ]
    for col, text in headers:
        ws.write(6, col, text, fmts["header"])
    ws.set_row(6, 30)

    rev_target = cfg.revenue_target_month
    cost_target = cfg.expense_budget_month

    for m in range(12):
        r = 8 + m
        month = m + 1
        ws.write(r - 1, 1, MONTH_NAMES[m], fmts["label"])
        # budgets (editable starting point)
        ws.write_number(r - 1, 2,
                        round(rev_target * SEASONALITY[m], -1),
                        fmts["input_money"])
        ws.write_number(r - 1, 5,
                        round(cost_target * SEASONALITY[m], -1),
                        fmts["input_money"])

        ms = f"DATE({year_cell},{month},1)"
        me = f"DATE({year_cell},{month + 1},1)-1"

        ws.write_formula(
            r - 1, 3,
            f'=SUMIFS({J_price},{J_date},">="&{ms},{J_date},"<="&{me},'
            f'{J_status},"Completed")+SUMIFS({J_price},{J_date},">="&{ms},'
            f'{J_date},"<="&{me},{J_status},"Invoiced")',
            fmts["calc_money"])
        ws.write_formula(r - 1, 4, f"=D{r}-C{r}", fmts["calc_money"])
        ws.write_formula(
            r - 1, 6,
            f'=SUMIFS({E_amount},{E_date},">="&{ms},{E_date},"<="&{me})'
            f'+SUMIFS({T_pay},{T_date},">="&{ms},{T_date},"<="&{me})'
            f'+SUMIFS({T_ot},{T_date},">="&{ms},{T_date},"<="&{me})'
            f'+SUMIFS({M_claim},{M_date},">="&{ms},{M_date},"<="&{me})',
            fmts["calc_money"])
        ws.write_formula(r - 1, 7, f"=G{r}-F{r}", fmts["calc_money"])
        ws.write_formula(r - 1, 8, f"=C{r}-F{r}", fmts["calc_money"])
        ws.write_formula(r - 1, 9, f"=D{r}-G{r}", fmts["calc_money"])
        ws.write_formula(r - 1, 10, f"=J{r}-I{r}", fmts["calc_money"])
        ws.write_formula(
            r - 1, 11,
            f'=SUMIFS({P_amount},{P_date},">="&{ms},{P_date},"<="&{me})',
            fmts["calc_money"])
        ws.write_formula(
            r - 1, 12,
            f'=IF(DATE({year_cell},{month},1)>TODAY(),"planned",'
            f'IF(E{r}>=0,"ON PLAN","BEHIND"))',
            fmts["calc"])
        ws.write_blank(r - 1, 13, None, fmts["input"])

    # totals
    tr = 20
    ws.write(tr - 1, 1, "Year", fmts["total_label"])
    for col in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
        letter = chr(ord("A") + col)
        ws.write_formula(tr - 1, col, f"=SUM({letter}8:{letter}19)",
                         fmts["total_money"])
    ws.write_blank(tr - 1, 12, None, fmts["total_text"])
    ws.write_blank(tr - 1, 13, None, fmts["total_text"])

    # summary
    r = 22
    ws.merge_range(r - 1, 1, r - 1, 13, "Plan health", fmts["section"])
    r += 1
    ws.write(r - 1, 1, "Planned margin", fmts["label"])
    ws.write_formula(r - 1, 2,
                     '=IF(C20=0,"",I20/C20)', fmts["calc_pct"])
    ws.merge_range(r - 1, 3, r - 1, 13,
                   "Profit plan / revenue budget for the year.",
                   fmts["note"])
    r += 1
    ws.write(r - 1, 1, "Actual margin YTD", fmts["label"])
    ws.write_formula(r - 1, 2, '=IF(D20=0,"",J20/D20)', fmts["calc_pct"])
    ws.merge_range(r - 1, 3, r - 1, 13,
                   "Live: earned profit / earned revenue.", fmts["note"])
    r += 1
    ws.write(r - 1, 1, "Revenue vs annual target", fmts["label"])
    ws.write_formula(r - 1, 2,
                     '=IF(Settings!$C$68=0,"",D20/Settings!$C$68)',
                     fmts["calc_pct"])
    ws.merge_range(r - 1, 3, r - 1, 13,
                   "100% means the year's target is banked.", fmts["note"])

    ws.freeze_panes(7, 2)
    ws.set_zoom(90)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
