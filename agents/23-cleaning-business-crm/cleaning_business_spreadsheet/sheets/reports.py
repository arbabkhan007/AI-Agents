"""Reports - KPIs, rankings and the monthly trend."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet
from .settings import settings_ref


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Reports")
    ws.set_tab_color(Palette.primary_mid)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 6, 14)
    ws.set_column(7, 7, 3)
    ws.set_column(8, 13, 14)

    def rng(sheet: str, key: str) -> str:
        spec = reg[sheet]
        letter = spec.letter(key)
        return (f"{quote_sheet(sheet)}!${letter}${spec.first_data_row}:"
                f"${letter}${spec.last_data_row}")

    J_date, J_price, J_status = (rng("Jobs", "date"),
                                 rng("Jobs", "price"),
                                 rng("Jobs", "status"))
    J_client, J_service = (rng("Jobs", "client"),
                           rng("Jobs", "service"))
    I_date, I_total, I_balance = (rng("Invoices", "date"),
                                  rng("Invoices", "total"),
                                  rng("Invoices", "balance"))
    I_due, I_paid = rng("Invoices", "due"), rng("Invoices", "paid")
    P_date, P_amount = rng("Payments", "date"), rng("Payments", "amount")
    E_date, E_amount, E_cat = (rng("Expenses", "date"),
                               rng("Expenses", "amount"),
                               rng("Expenses", "category"))
    T_date, T_emp, T_hours = (rng("Timesheets", "date"),
                              rng("Timesheets", "employee"),
                              rng("Timesheets", "hours"))
    T_pay, T_ot = rng("Timesheets", "pay"), rng(
        "Timesheets", "overtime_pay")
    M_date, M_claim = rng("Mileage", "date"), rng("Mileage", "claim")
    Q_date, Q_status, Q_total = (rng("Quotes", "date"),
                                 rng("Quotes", "status"),
                                 rng("Quotes", "total"))
    C_rating, C_status = rng("Clients", "rating"), rng(
        "Clients", "status")

    ws.merge_range(0, 1, 0, 6, "Reports  ·  KPIs & Trends", fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 6,
                   f"Every number is live from the registers for "
                   f"{cfg.year}. The month table below is the shape of "
                   "the year; the panels to the right rank what is "
                   "working.",
                   fmts["subtitle"])

    r = 4

    def section(text: str, width: int = 6) -> None:
        nonlocal r
        ws.merge_range(r - 1, 1, r - 1, width, text, fmts["section"])
        r += 1

    def kpi(label: str, formula: str, style: str, target: str = "") -> int:
        nonlocal r
        row = r
        ws.write(row - 1, 1, label, fmts["label"])
        ws.write_formula(row - 1, 2, formula, fmts[style])
        if target:
            ws.write_formula(row - 1, 3, target, fmts[style])
        else:
            ws.write_blank(row - 1, 3, None, fmts["note"])
        ws.merge_range(row - 1, 4, row - 1, 6, "", fmts["note"])
        r += 1
        return row

    y = cfg.year
    ys = f"DATE({y},1,1)"
    ye = f"DATE({y + 1},1,1)-1"

    # ------------------------------------------------------------ KPI panel
    section("Key performance indicators")
    ws.write(r - 1, 1, "Indicator", fmts["header"])
    ws.write(r - 1, 2, "Value", fmts["header"])
    ws.write(r - 1, 3, "Target", fmts["header"])
    ws.merge_range(r - 1, 4, r - 1, 6, "Comment", fmts["header"])
    r += 1

    rev_row = kpi("Revenue this year",
                  f'=SUMIFS({J_price},{J_date},">="&{ys},{J_date},"<="&{ye},'
                  f'{J_status},"Completed")+SUMIFS({J_price},{J_date},'
                  f'">="&{ys},{J_date},"<="&{ye},{J_status},"Invoiced")',
                  "calc_money", '=Settings!$C$68')
    kpi("Costs this year",
        f'=SUMIFS({E_amount},{E_date},">="&{ys},{E_date},"<="&{ye})'
        f'+SUMIFS({T_pay},{T_date},">="&{ys},{T_date},"<="&{ye})'
        f'+SUMIFS({T_ot},{T_date},">="&{ys},{T_date},"<="&{ye})'
        f'+SUMIFS({M_claim},{M_date},">="&{ys},{M_date},"<="&{ye})',
        "calc_money")
    profit_row = kpi("Profit this year",
                     f'=C{r-2}-C{r-1}', "calc_money")
    kpi("Margin this year",
        f'=IF(C{r-3}=0,"",C{profit_row}/C{r-3})', "calc_pct",
        '=Settings!$C$63')
    kpi("Cash collected this year",
        f'=SUMIFS({P_amount},{P_date},">="&{ys},{P_date},"<="&{ye})',
        "calc_money")
    kpi("Outstanding now", f'=SUMIF({I_balance},">0")', "calc_money")
    kpi("Overdue now",
        f'=SUMIFS({I_balance},{I_due},"<"&TODAY(),{I_balance},">0")',
        "calc_money")
    kpi("Quotes sent this year",
        f'=COUNTIFS({Q_date},">="&{ys},{Q_date},"<="&{ye})', "calc_int")
    kpi("Quotes won this year",
        f'=COUNTIFS({Q_date},">="&{ys},{Q_date},"<="&{ye},'
        f'{Q_status},"Accepted")', "calc_int")
    kpi("Quote win rate",
        f'=IF(C{r-2}=0,"",C{r-1}/C{r-2})', "calc_pct",
        '=Settings!$C$73')
    kpi("Active clients", f'=COUNTIF({C_status},"Active")', "calc_int")
    kpi("Average satisfaction",
        f'=IF(COUNT({C_rating})=0,"",AVERAGE({C_rating}))',
        "calc_decimal", '=Settings!$C$72')
    kpi("Total jobs done",
        f'=COUNTIF({J_status},"Completed")+COUNTIF({J_status},'
        '"Invoiced")', "calc_int")
    kpi("Average job value",
        f'=IF((COUNTIF({J_status},"Completed")+COUNTIF({J_status},'
        f'"Invoiced"))=0,"",C{rev_row}/(COUNTIF({J_status},'
        f'"Completed")+COUNTIF({J_status},"Invoiced")))',
        "calc_money")
    r += 1

    # -------------------------------------------------------- month table
    section("Monthly trend")
    headers = ["Month", "Jobs", "Revenue", "Costs", "Profit", "Margin"]
    for c, text in enumerate(headers):
        ws.write(r - 1, 1 + c, text, fmts["header"])
    r += 1
    month_first_row = r
    for m in range(1, 13):
        ms = f"DATE({y},{m},1)"
        me = f"DATE({y},{m + 1},1)-1"
        ws.write_formula(r - 1, 1,
                         f'=DATE({y},{m},1)', fmts["calc_month"])
        ws.write_formula(
            r - 1, 2,
            f'=COUNTIFS({J_date},">="&{ms},{J_date},"<="&{me},'
            f'{J_status},"Completed")+COUNTIFS({J_date},">="&{ms},'
            f'{J_date},"<="&{me},{J_status},"Invoiced")',
            fmts["calc_int"])
        ws.write_formula(
            r - 1, 3,
            f'=SUMIFS({J_price},{J_date},">="&{ms},{J_date},"<="&{me},'
            f'{J_status},"Completed")+SUMIFS({J_price},{J_date},'
            f'">="&{ms},{J_date},"<="&{me},{J_status},"Invoiced")',
            fmts["calc_money"])
        ws.write_formula(
            r - 1, 4,
            f'=SUMIFS({E_amount},{E_date},">="&{ms},{E_date},"<="&{me})'
            f'+SUMIFS({T_pay},{T_date},">="&{ms},{T_date},"<="&{me})'
            f'+SUMIFS({T_ot},{T_date},">="&{ms},{T_date},"<="&{me})'
            f'+SUMIFS({M_claim},{M_date},">="&{ms},{M_date},"<="&{me})',
            fmts["calc_money"])
        ws.write_formula(r - 1, 5, f"=D{r}-E{r}", fmts["calc_money"])
        ws.write_formula(r - 1, 6,
                         f'=IF(D{r}=0,"",F{r}/D{r})', fmts["pct_locked"])
        r += 1
    ws.write(r - 1, 1, "Year", fmts["total_label"])
    for c, letter in enumerate(["C", "D", "E", "F"]):
        ws.write_formula(
            r - 1, 2 + c,
            f"=SUM({letter}{month_first_row}:{letter}{r-1})",
            fmts["total_int"] if c == 0 else fmts["total_money"])
    ws.write_formula(r - 1, 6,
                     f'=IF(D{r}=0,"",F{r}/D{r})', fmts["total_pct"])
    r += 2

    # --------------------------------------------------- revenue by service
    section("Revenue by service (top of the price list)")
    ws.write(r - 1, 1, "Service", fmts["header"])
    ws.write(r - 1, 2, "Jobs", fmts["header"])
    ws.write(r - 1, 3, "Revenue", fmts["header"])
    ws.merge_range(r - 1, 4, r - 1, 6, "Share of jobs", fmts["header"])
    r += 1
    e_spec = reg["Services"]
    n_services = 8
    for i in range(n_services):
        srow = e_spec.first_data_row + i
        name_ref = f"{quote_sheet('Services')}!" \
                   f"${e_spec.letter('name')}${srow}"
        ws.write_formula(
            r - 1, 1,
            f'=IF({name_ref}="","",{name_ref})', fmts["text_locked"])
        ws.write_formula(
            r - 1, 2,
            f'=IF($B{r}="","",COUNTIFS({J_service},$B{r},'
            f'{J_status},"<>Cancelled"))', fmts["calc_int"])
        ws.write_formula(
            r - 1, 3,
            f'=IF($B{r}="","",SUMIFS({J_price},{J_service},$B{r},'
            f'{J_status},"<>Cancelled"))', fmts["calc_money"])
        ws.write_formula(
            r - 1, 4,
            f'=IF($B{r}="","",IFERROR(C{r}/COUNTIFS({J_status},'
            f'"<>Cancelled"),0))', fmts["calc_pct"])
        r += 1
    r += 1

    # --------------------------------------------------------- top clients
    section("Top clients (first 8 on the Clients tab)")
    ws.write(r - 1, 1, "Client", fmts["header"])
    ws.write(r - 1, 2, "Jobs", fmts["header"])
    ws.write(r - 1, 3, "Revenue", fmts["header"])
    ws.merge_range(r - 1, 4, r - 1, 6, "Outstanding", fmts["header"])
    r += 1
    c_spec = reg["Clients"]
    for i in range(8):
        crow = c_spec.first_data_row + i
        name_ref = f"{quote_sheet('Clients')}!" \
                   f"${c_spec.letter('name')}${crow}"
        ws.write_formula(
            r - 1, 1,
            f'=IF({name_ref}="","",{name_ref})', fmts["text_locked"])
        ws.write_formula(
            r - 1, 2,
            f'=IF($B{r}="","",COUNTIFS({J_client},$B{r},'
            f'{J_status},"<>Cancelled"))', fmts["calc_int"])
        ws.write_formula(
            r - 1, 3,
            f'=IF($B{r}="","",SUMIFS({J_price},{J_client},$B{r},'
            f'{J_status},"<>Cancelled"))', fmts["calc_money"])
        ws.write_formula(
            r - 1, 4,
            f'=IF($B{r}="","",SUMIFS({I_balance},{rng("Invoices", "client")},'
            f'$B{r}))', fmts["calc_money"])
        r += 1
    r += 1

    # ---------------------------------------------------- expense categories
    section("Expenses by category (this year)")
    ws.write(r - 1, 1, "Category", fmts["header"])
    ws.write(r - 1, 2, "Total", fmts["header"])
    ws.write(r - 1, 3, "Share", fmts["header"])
    ws.merge_range(r - 1, 4, r - 1, 6, "", fmts["header"])
    r += 1
    cats = ["Payroll", "Supplies", "Equipment", "Fuel", "Insurance",
            "Rent", "Utilities", "Marketing", "Training", "Repairs",
            "Software", "Fees", "Taxes", "Other"]
    cat_first = r
    for cat in cats:
        ws.write(r - 1, 1, cat, fmts["input"])
        ws.write_formula(
            r - 1, 2,
            f'=SUMIFS({E_amount},{E_cat},$B{r},{E_date},">="&{ys},'
            f'{E_date},"<="&{ye})', fmts["calc_money"])
        r += 1
    # payroll as its own line (wages are not on the Expenses tab)
    ws.write(r - 1, 1, "Wages & payroll", fmts["input"])
    ws.write_formula(
        r - 1, 2,
        f'=SUMIFS({T_pay},{T_date},">="&{ys},{T_date},"<="&{ye})'
        f'+SUMIFS({T_ot},{T_date},">="&{ys},{T_date},"<="&{ye})',
        fmts["calc_money"])
    r += 1
    cat_last = r - 1
    for i, rr in enumerate(range(cat_first, cat_last + 1)):
        ws.write_formula(rr - 1, 3,
                         f'=IF(SUM($C${cat_first}:$C${cat_last})=0,"",'
                         f'C{rr}/SUM($C${cat_first}:$C${cat_last}))',
                         fmts["pct_locked"])
    r += 1

    # ---------------------------------------------------- staff leaderboard
    section("Staff leaderboard (first 8 on the Employees tab)")
    ws.write(r - 1, 1, "Employee", fmts["header"])
    ws.write(r - 1, 2, "Hours", fmts["header"])
    ws.write(r - 1, 3, "Cost", fmts["header"])
    ws.merge_range(r - 1, 4, r - 1, 6, "Jobs led", fmts["header"])
    r += 1
    emp_spec = reg["Employees"]
    for i in range(8):
        erow = emp_spec.first_data_row + i
        name_ref = f"{quote_sheet('Employees')}!" \
                   f"${emp_spec.letter('name')}${erow}"
        ws.write_formula(
            r - 1, 1,
            f'=IF({name_ref}="","",{name_ref})', fmts["text_locked"])
        ws.write_formula(
            r - 1, 2,
            f'=IF($B{r}="","",SUMIFS({T_hours},{T_emp},$B{r},'
            f'{T_date},">="&{ys},{T_date},"<="&{ye}))',
            fmts["calc_decimal"])
        ws.write_formula(
            r - 1, 3,
            f'=IF($B{r}="","",SUMIFS({T_pay},{T_emp},$B{r},'
            f'{T_date},">="&{ys},{T_date},"<="&{ye})'
            f'+SUMIFS({T_ot},{T_emp},$B{r},{T_date},">="&{ys},'
            f'{T_date},"<="&{ye}))', fmts["calc_money"])
        ws.write_formula(
            r - 1, 4,
            f'=IF($B{r}="","",COUNTIFS({rng("Jobs", "crew_lead")},$B{r},'
            f'{J_date},">="&{ys},{J_date},"<="&{ye},'
            f'{J_status},"<>Cancelled"))', fmts["calc_int"])
        r += 1

    r += 1
    ws.merge_range(r - 1, 1, r - 1, 6,
                   "Rankings show the first rows of each register - "
                   "sort the register itself to decide who those are.",
                   fmts["note"])

    ws.freeze_panes(3, 0)
    ws.set_zoom(90)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
