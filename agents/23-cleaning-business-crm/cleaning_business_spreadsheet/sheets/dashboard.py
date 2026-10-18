"""Dashboard - the business at a glance, live.

Every column letter is derived from the registry, so the dashboard can
never drift out of sync with the register layouts.
"""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet
from .settings import settings_ref

MONTH_START = 'DATE(YEAR(TODAY()),MONTH(TODAY()),1)'
MONTH_END = 'DATE(YEAR(TODAY()),MONTH(TODAY())+1,1)-1'


class _Dash:
    def __init__(self, ws: Any, fmts: FormatBook, reg: Registry) -> None:
        self.ws, self.fmts, self.reg = ws, fmts, reg
        self.r = 4

    def col(self, sheet: str, key: str) -> str:
        return f"{quote_sheet(sheet)}!${self.reg.letter(sheet, key)}:$" \
               f"{self.reg.letter(sheet, key)}"

    def section(self, text: str) -> None:
        self.ws.merge_range(self.r - 1, 1, self.r - 1, 5, text,
                            self.fmts["section"])
        self.r += 1

    def head(self, a: str, b: str, c: str, d: str) -> None:
        ws, f = self.ws, self.fmts
        ws.write(self.r - 1, 1, a, f["header"])
        ws.write(self.r - 1, 2, b, f["header"])
        ws.write(self.r - 1, 3, c, f["header"])
        ws.merge_range(self.r - 1, 4, self.r - 1, 5, d, f["header"])
        self.r += 1

    def metric(self, label: str, formula: str, style: str,
               target: str = "", status: str = "") -> int:
        """Write one metric row; returns its 1-based Excel row."""
        ws, f = self.ws, self.fmts
        row = self.r
        ws.write(row - 1, 1, label, f["label"])
        ws.write_formula(row - 1, 2, formula, f[style])
        if target:
            ws.write_formula(row - 1, 3, target, f[style])
        else:
            ws.write_blank(row - 1, 3, None, f["note"])
        if status:
            ws.merge_range(row - 1, 4, row - 1, 5, "", f["calc"])
            ws.write_formula(row - 1, 4, status, f["calc"])
        else:
            ws.merge_range(row - 1, 4, row - 1, 5, "", f["note"])
        self.r += 1
        return row

    def alert(self, label: str, formula: str, action: str) -> None:
        ws, f = self.ws, self.fmts
        ws.write(self.r - 1, 1, label, f["label"])
        ws.write_formula(self.r - 1, 2, formula, f["calc_int"])
        ws.write_blank(self.r - 1, 3, None, f["note"])
        ws.merge_range(self.r - 1, 4, self.r - 1, 5, action, f["note"])
        self.r += 1


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Dashboard")
    ws.set_tab_color(Palette.accent)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 32)
    ws.set_column(2, 2, 16)
    ws.set_column(3, 3, 16)
    ws.set_column(4, 5, 18)

    ws.merge_range(0, 1, 0, 5, "Dashboard  ·  The Business Today",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 5,
                   "Everything below is live: it recalculates from the "
                   "registers the moment you change a row. Pale teal "
                   "cells are formulas; the numbers only move when the "
                   "data does.",
                   fmts["subtitle"])

    d = _Dash(ws, fmts, reg)

    J_date = d.col("Jobs", "date")
    J_status = d.col("Jobs", "status")
    J_price = d.col("Jobs", "price")
    J_hours = d.col("Jobs", "hours")
    J_cleaners = d.col("Jobs", "cleaners")
    J_crew = d.col("Jobs", "crew_lead")

    I_date = d.col("Invoices", "date")
    I_due = d.col("Invoices", "due")
    I_total = d.col("Invoices", "total")
    I_balance = d.col("Invoices", "balance")

    P_date = d.col("Payments", "date")
    P_amount = d.col("Payments", "amount")

    Q_date = d.col("Quotes", "date")
    Q_status = d.col("Quotes", "status")
    Q_total = d.col("Quotes", "total")
    Q_follow = d.col("Quotes", "follow_up")

    C_since = d.col("Clients", "since")
    C_status = d.col("Clients", "status")

    L_status = d.col("Leads", "status")
    L_follow = d.col("Leads", "follow_up")

    E_amount = d.col("Expenses", "amount")
    E_date = d.col("Expenses", "date")
    T_date = d.col("Timesheets", "date")
    T_pay = d.col("Timesheets", "pay")
    T_ot = d.col("Timesheets", "overtime_pay")
    M_date = d.col("Mileage", "date")
    M_claim = d.col("Mileage", "claim")
    S_flag = d.col("Supplies", "flag")
    EQ_due = d.col("Equipment", "service_due")
    CO_status = d.col("Complaints", "status")

    # ---------------------------------------------------------------- today
    d.section("Today")
    d.head("Metric", "Value", "Target", "Status")
    d.metric("Jobs today",
             f'=COUNTIFS({J_date},TODAY(),{J_status},"<>Cancelled")',
             "calc_int")
    d.metric("Cleaners scheduled today",
             f'=SUMIFS({J_cleaners},{J_date},TODAY(),{J_status},'
             '"<>Cancelled")', "calc_int")
    d.metric("Hours scheduled today",
             f'=SUMIFS({J_hours},{J_date},TODAY(),{J_status},'
             '"<>Cancelled")', "calc_decimal")
    d.metric("Revenue scheduled today",
             f'=SUMIFS({J_price},{J_date},TODAY(),{J_status},'
             '"<>Cancelled")', "calc_money")
    d.metric("Jobs completed today",
             f'=COUNTIFS({J_date},TODAY(),{J_status},"Completed")'
             f'+COUNTIFS({J_date},TODAY(),{J_status},"Invoiced")',
             "calc_int")
    d.r += 1

    # ------------------------------------------------------------ this month
    d.section("This Month")
    d.head("Metric", "Value", "Target", "Status")

    rev_row = d.r
    d.metric(
        "Revenue earned (completed work)",
        f'=SUMIFS({J_price},{J_date},">="&{MONTH_START},{J_date},'
        f'"<="&TODAY(),{J_status},"Completed")'
        f'+SUMIFS({J_price},{J_date},">="&{MONTH_START},{J_date},'
        f'"<="&TODAY(),{J_status},"Invoiced")',
        "calc_money",
        f'={settings_ref("revenue_target_month")}',
        f'=IF(C{rev_row}>=D{rev_row},"ON TARGET",'
        f'IF(C{rev_row}>=D{rev_row}*0.8,"CLOSE","BEHIND"))')

    cost_row = d.r
    d.metric(
        "Costs (payroll + expenses + travel)",
        f'=SUMIFS({E_amount},{E_date},">="&{MONTH_START})'
        f'+SUMIFS({T_pay},{T_date},">="&{MONTH_START})'
        f'+SUMIFS({T_ot},{T_date},">="&{MONTH_START})'
        f'+SUMIFS({M_claim},{M_date},">="&{MONTH_START})',
        "calc_money",
        f'={settings_ref("expense_budget_month")}',
        f'=IF(C{cost_row}<=D{cost_row},"UNDER BUDGET","OVER BUDGET")')

    profit_row = d.r
    d.metric(
        "Profit this month", f"=C{rev_row}-C{cost_row}", "calc_money",
        "", f'=IF(C{rev_row}-C{cost_row}>0,"PROFIT","LOSS")')

    margin_row = d.r
    d.metric(
        "Margin this month",
        f'=IF(C{rev_row}=0,"",C{profit_row}/C{rev_row})', "calc_pct",
        "", f'=IF(C{rev_row}=0,"-",IF(C{margin_row}>=0.4,"STRONG",'
        f'IF(C{margin_row}>=0.2,"OK","THIN")))')

    d.metric("Booked (rest of month)",
             f'=SUMIFS({J_price},{J_date},">="&TODAY(),{J_date},'
             f'"<="&{MONTH_END},{J_status},"<>Cancelled")', "calc_money")
    d.metric("Invoiced this month",
             f'=SUMIFS({I_total},{I_date},">="&{MONTH_START})',
             "calc_money")
    d.metric("Cash collected this month",
             f'=SUMIFS({P_amount},{P_date},">="&{MONTH_START})',
             "calc_money")
    out_row = d.r
    d.metric("Outstanding (all invoices)",
             f'=SUMIF({I_balance},">0")', "calc_money",
             "", f'=IF(C{out_row}>0,"CHASE","CLEAR")')
    over_row = d.r
    d.metric(
        "Overdue amount",
        f'=SUMIFS({I_balance},{I_due},"<"&TODAY(),{I_balance},">0")',
        "calc_money", "", f'=IF(C{over_row}>0,"OVERDUE","CLEAR")')
    d.r += 1

    # --------------------------------------------------------------- sales
    d.section("Sales & Clients")
    d.head("Metric", "Value", "Target", "Status")
    sent_row = d.metric(
        "Quotes sent this month",
        f'=COUNTIFS({Q_date},">="&{MONTH_START})', "calc_int")
    won_row = d.metric(
        "Quotes won this month",
        f'=COUNTIFS({Q_date},">="&{MONTH_START},{Q_status},"Accepted")',
        "calc_int")
    d.metric("Win rate this month",
             f'=IF(C{sent_row}=0,"",C{won_row}/C{sent_row})',
             "calc_pct", f'={settings_ref("quote_win_target")}',
             f'=IF(C{sent_row}=0,"-",IF(C{won_row}/C{sent_row}>=D{sent_row + 2},'
             '"ON TARGET","BELOW"))')
    d.metric("Live pipeline value",
             f'=SUMIFS({Q_total},{Q_status},"Sent")'
             f'+SUMIFS({Q_total},{Q_status},"Followed up")'
             f'+SUMIFS({Q_total},{Q_status},"Draft")', "calc_money")
    d.metric("Active clients", f'=COUNTIF({C_status},"Active")',
             "calc_int")
    d.metric("New clients this month",
             f'=COUNTIFS({C_since},">="&{MONTH_START})', "calc_int")
    d.metric("Jobs done all time",
             f'=COUNTIF({J_status},"Completed")'
             f'+COUNTIF({J_status},"Invoiced")', "calc_int")
    d.r += 1

    # --------------------------------------------------------------- alerts
    d.section("Alerts - what needs you today")
    d.head("Check", "Count", "", "Action")
    d.alert("Jobs today still only 'Booked'",
            f'=COUNTIFS({J_date},TODAY(),{J_status},"Booked")',
            "Confirm them with the client.")
    d.alert("Overdue invoices",
            f'=COUNTIFS({I_due},"<"&TODAY(),{I_balance},">0")',
            "Call or email today.")
    d.alert("Quotes needing a follow-up",
            f'=COUNTIFS({Q_follow},"<"&TODAY(),{Q_status},"Sent")'
            f'+COUNTIFS({Q_follow},"<"&TODAY(),{Q_status},"Followed up")',
            "Chase before they go cold.")
    d.alert("Leads to chase",
            f'=COUNTIFS({L_follow},"<"&TODAY(),{L_status},"New")'
            f'+COUNTIFS({L_follow},"<"&TODAY(),{L_status},"Contacted")'
            f'+COUNTIFS({L_follow},"<"&TODAY(),{L_status},"Quoted")',
            "One call each.")
    d.alert("Supplies to reorder", f'=COUNTIF({S_flag},"REORDER")',
            "Order today.")
    d.alert("Open complaints",
            f'=COUNTIF({CO_status},"Open")'
            f'+COUNTIF({CO_status},"Investigating")'
            f'+COUNTIF({CO_status},"Escalated")',
            "Resolve within 48 hours.")
    d.alert("Equipment service due",
            f'=COUNTIF({EQ_due},"DUE SOON")', "Book the service.")
    d.alert("Jobs this week with no crew",
            f'=COUNTIFS({J_date},">="&TODAY(),{J_date},"<="&TODAY()+7,'
            f'{J_status},"Booked",{J_crew},"")',
            "Assign a crew lead.")

    d.r += 1
    ws.merge_range(d.r - 1, 1, d.r - 1, 5,
                   "Whole-column formulas are deliberate: they keep "
                   "counting no matter how many rows you add.",
                   fmts["note"])

    ws.freeze_panes(3, 0)
    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
