"""
`Calc` - hidden helper sheet.

Excel has no SORT/FILTER in the 2007-2016 formula set, so the "top 10"
tables, the twelve month trend series and the category breakdowns are
pre-computed here with plain SUMIFS/COUNTIFS and then pulled into the
Dashboard and Reports tabs with LARGE + INDEX/MATCH.

Nothing here needs to be touched by the user; the tab is hidden and every
cell is a locked formula.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from . import lists

NAME = "Calc"

_PERIOD = ('[[Payments.date]],">="&PeriodStart,[[Payments.date]],'
           '"<="&PeriodEnd')


def spec(cfg: Config) -> SheetSpec:
    rows = max(cfg.row_count("Clients"), cfg.row_count("Services"),
               cfg.row_count("Staff"), 60)

    def mirror(sheet: str, key: str) -> str:
        return f'=IF([[{sheet}.{key}#]]="","",[[{sheet}.{key}#]])'

    columns = [
        # ---------------------------------------------------- clients block
        Col("c_name", "Client", 20, "text", formula=mirror("Clients", "name")),
        Col("c_rev_p", "Revenue (dashboard period)", 14, "money",
            formula='=IF({c_name}{r}="","",SUMIFS([[Payments.received]],'
                    '[[Payments.client]],{c_name}{r},' + _PERIOD + '))'),
        Col("c_key_p", "Rank key (period)", 14, "number",
            formula='=IF({c_name}{r}="","",IF({c_rev_p}{r}<=0,"",'
                    '{c_rev_p}{r}+ROW()/1000000))'),
        Col("c_rev_r", "Revenue (report range)", 14, "money",
            formula='=IF({c_name}{r}="","",SUMIFS([[Payments.received]],'
                    '[[Payments.client]],{c_name}{r},[[Payments.date]],'
                    '">="&RepFrom,[[Payments.date]],"<="&RepTo))'),
        Col("c_key_r", "Rank key (range)", 14, "number",
            formula='=IF({c_name}{r}="","",IF({c_rev_r}{r}<=0,"",'
                    '{c_rev_r}{r}+ROW()/1000000))'),
        Col("c_out", "Outstanding", 13, "money",
            formula='=IF({c_name}{r}="","",SUMIFS([[Invoices.balance]],'
                    '[[Invoices.client]],{c_name}{r},[[Invoices.status]],'
                    '"<>Cancelled"))'),
        Col("c_out_key", "Outstanding key", 14, "number",
            formula='=IF({c_name}{r}="","",IF({c_out}{r}<=0.004,"",'
                    '{c_out}{r}+ROW()/1000000))'),
        Col("c_bookings_r", "Bookings (range)", 12, "int",
            formula='=IF({c_name}{r}="","",COUNTIFS([[Bookings.client]],'
                    '{c_name}{r},[[Bookings.date]],">="&RepFrom,'
                    '[[Bookings.date]],"<="&RepTo,[[Bookings.status]],'
                    '"<>Cancelled"))'),
        # --------------------------------------------------- services block
        Col("s_name", "Service", 22, "text",
            formula=mirror("Services", "name")),
        Col("s_rev_p", "Service revenue (period)", 14, "money",
            formula='=IF({s_name}{r}="","",SUMIFS([[Bookings.total]],'
                    '[[Bookings.service]],{s_name}{r},[[Bookings.date]],'
                    '">="&PeriodStart,[[Bookings.date]],"<="&PeriodEnd,'
                    '[[Bookings.status]],"<>Cancelled"))'),
        Col("s_count_p", "Service bookings (period)", 12, "int",
            formula='=IF({s_name}{r}="","",COUNTIFS([[Bookings.service]],'
                    '{s_name}{r},[[Bookings.date]],">="&PeriodStart,'
                    '[[Bookings.date]],"<="&PeriodEnd,[[Bookings.status]],'
                    '"<>Cancelled"))'),
        Col("s_rev_r", "Service revenue (range)", 14, "money",
            formula='=IF({s_name}{r}="","",SUMIFS([[Bookings.total]],'
                    '[[Bookings.service]],{s_name}{r},[[Bookings.date]],'
                    '">="&RepFrom,[[Bookings.date]],"<="&RepTo,'
                    '[[Bookings.status]],"<>Cancelled"))'),
        Col("s_count_r", "Service bookings (range)", 12, "int",
            formula='=IF({s_name}{r}="","",COUNTIFS([[Bookings.service]],'
                    '{s_name}{r},[[Bookings.date]],">="&RepFrom,'
                    '[[Bookings.date]],"<="&RepTo,[[Bookings.status]],'
                    '"<>Cancelled"))'),
        Col("s_cost_r", "Service cost (range)", 13, "money",
            formula='=IF({s_name}{r}="","",{s_count_r}{r}'
                    '*IF([[Services.staff_cost#]]="",0,'
                    '[[Services.staff_cost#]]))'),
        Col("s_profit_r", "Service profit (range)", 13, "money",
            formula='=IF({s_name}{r}="","",{s_rev_r}{r}-{s_cost_r}{r})'),
        # ------------------------------------------- expense category block
        Col("e_cat", "Expense category", 20, "text",
            formula='=IF(' + lists.ref("ExpenseCategoryList") + '="","",'
                    + lists.ref("ExpenseCategoryList") + ')'),
        Col("e_total_p", "Spend (period)", 13, "money",
            formula='=IF({e_cat}{r}="","",SUMIFS([[Expenses.amount]],'
                    '[[Expenses.category]],{e_cat}{r},[[Expenses.date]],'
                    '">="&PeriodStart,[[Expenses.date]],"<="&PeriodEnd,'
                    '[[Expenses.type]],"<>Personal"))'),
        Col("e_total_r", "Spend (range)", 13, "money",
            formula='=IF({e_cat}{r}="","",SUMIFS([[Expenses.amount]],'
                    '[[Expenses.category]],{e_cat}{r},[[Expenses.date]],'
                    '">="&RepFrom,[[Expenses.date]],"<="&RepTo,'
                    '[[Expenses.type]],"<>Personal"))'),
        # ------------------------------------------------ 12 month series --
        Col("m_start", "Month start", 12, "date",
            formula='=IF(ROW()-4>12,"",DATE(Dash_Year,ROW()-4,1))'),
        Col("m_end", "Month end", 12, "date",
            formula='=IF({m_start}{r}="","",EOMONTH({m_start}{r},0))'),
        Col("m_label", "Month", 10, "text",
            formula='=IF({m_start}{r}="","",TEXT({m_start}{r},"mmm"))'),
        Col("m_rev", "Revenue", 13, "money",
            formula='=IF({m_start}{r}="","",SUMIFS([[Payments.received]],'
                    '[[Payments.date]],">="&{m_start}{r},'
                    '[[Payments.date]],"<="&{m_end}{r}))'),
        Col("m_inv", "Invoiced", 13, "money",
            formula='=IF({m_start}{r}="","",SUMIFS([[Invoices.total]],'
                    '[[Invoices.date]],">="&{m_start}{r},[[Invoices.date]],'
                    '"<="&{m_end}{r},[[Invoices.status]],"<>Cancelled"))'),
        Col("m_exp", "Expenses", 13, "money",
            formula='=IF({m_start}{r}="","",SUMIFS([[Expenses.amount]],'
                    '[[Expenses.date]],">="&{m_start}{r},[[Expenses.date]],'
                    '"<="&{m_end}{r},[[Expenses.type]],"<>Personal"))'),
        Col("m_profit", "Profit", 13, "money",
            formula='=IF({m_start}{r}="","",{m_rev}{r}-{m_exp}{r})'),
        Col("m_bookings", "Bookings", 10, "int",
            formula='=IF({m_start}{r}="","",COUNTIFS([[Bookings.date]],'
                    '">="&{m_start}{r},[[Bookings.date]],"<="&{m_end}{r},'
                    '[[Bookings.status]],"<>Cancelled"))'),
        Col("m_completed", "Completed", 10, "int",
            formula='=IF({m_start}{r}="","",COUNTIFS([[Bookings.date]],'
                    '">="&{m_start}{r},[[Bookings.date]],"<="&{m_end}{r},'
                    '[[Bookings.status]],"Completed"))'),
        Col("m_cancelled", "Cancelled", 10, "int",
            formula='=IF({m_start}{r}="","",COUNTIFS([[Bookings.date]],'
                    '">="&{m_start}{r},[[Bookings.date]],"<="&{m_end}{r},'
                    '[[Bookings.status]],"Cancelled"))'),
        Col("m_visits", "Visits", 10, "int",
            formula='=IF({m_start}{r}="","",COUNTIFS([[Visit Log.date]],'
                    '">="&{m_start}{r},[[Visit Log.date]],"<="&{m_end}{r},'
                    '[[Visit Log.status]],"Completed"))'),
        Col("m_new_clients", "New clients", 10, "int",
            formula='=IF({m_start}{r}="","",COUNTIFS([[Clients.reg_date]],'
                    '">="&{m_start}{r},[[Clients.reg_date]],'
                    '"<="&{m_end}{r}))'),
        Col("m_km", "Business distance", 11, "number1",
            formula='=IF({m_start}{r}="","",SUMIFS([[Mileage.total_km]],'
                    '[[Mileage.date]],">="&{m_start}{r},[[Mileage.date]],'
                    '"<="&{m_end}{r},[[Mileage.business]],"Business"))'),
        Col("m_prev_rev", "Revenue last year", 13, "money",
            formula='=IF({m_start}{r}="","",SUMIFS([[Payments.received]],'
                    '[[Payments.date]],">="&DATE(Dash_Year-1,ROW()-4,1),'
                    '[[Payments.date]],"<="&EOMONTH(DATE(Dash_Year-1,'
                    'ROW()-4,1),0)))'),
        # ---------------------------------------------------- staff block --
        Col("st_name", "Staff", 18, "text", formula=mirror("Staff", "name")),
        Col("st_visits_r", "Visits (range)", 11, "int",
            formula='=IF({st_name}{r}="","",COUNTIFS([[Visit Log.staff]],'
                    '{st_name}{r},[[Visit Log.date]],">="&RepFrom,'
                    '[[Visit Log.date]],"<="&RepTo,[[Visit Log.status]],'
                    '"Completed"))'),
        Col("st_hours_r", "Hours (range)", 11, "number",
            formula='=IF({st_name}{r}="","",ROUND(SUMIFS('
                    '[[Visit Log.duration]],[[Visit Log.staff]],'
                    '{st_name}{r},[[Visit Log.date]],">="&RepFrom,'
                    '[[Visit Log.date]],"<="&RepTo,[[Visit Log.status]],'
                    '"Completed")/60,2))'),
        Col("st_rev_r", "Revenue (range)", 13, "money",
            formula='=IF({st_name}{r}="","",SUMIFS([[Bookings.total]],'
                    '[[Bookings.staff]],{st_name}{r},[[Bookings.date]],'
                    '">="&RepFrom,[[Bookings.date]],"<="&RepTo,'
                    '[[Bookings.status]],"<>Cancelled"))'),
        Col("st_km_r", "Distance (range)", 11, "number1",
            formula='=IF({st_name}{r}="","",SUMIFS([[Mileage.total_km]],'
                    '[[Mileage.staff]],{st_name}{r},[[Mileage.date]],'
                    '">="&RepFrom,[[Mileage.date]],"<="&RepTo))'),
        # ------------------------------------------- cancellations/methods -
        Col("cr_reason", "Cancellation reason", 20, "text",
            formula='=IF(' + lists.ref("CancelReasonList") + '="","",'
                    + lists.ref("CancelReasonList") + ')'),
        Col("cr_count", "Cancellations (range)", 12, "int",
            formula='=IF({cr_reason}{r}="","",COUNTIFS('
                    '[[Bookings.cancel_reason]],{cr_reason}{r},'
                    '[[Bookings.date]],">="&RepFrom,[[Bookings.date]],'
                    '"<="&RepTo))'),
        Col("pm_method", "Payment method", 18, "text",
            formula='=IF(' + lists.ref("PaymentMethodList") + '="","",'
                    + lists.ref("PaymentMethodList") + ')'),
        Col("pm_total", "Collected (range)", 13, "money",
            formula='=IF({pm_method}{r}="","",SUMIFS([[Payments.received]],'
                    '[[Payments.method]],{pm_method}{r},[[Payments.date]],'
                    '">="&RepFrom,[[Payments.date]],"<="&RepTo))'),
        Col("ref_source", "Referral source", 18, "text",
            formula='=IF(' + lists.ref("ReferralSourceList") + '="","",'
                    + lists.ref("ReferralSourceList") + ')'),
        Col("ref_clients", "Clients from source", 12, "int",
            formula='=IF({ref_source}{r}="","",COUNTIFS('
                    '[[Clients.referral]],{ref_source}{r}))'),
        Col("ref_revenue", "Revenue from source", 13, "money",
            formula='=IF({ref_source}{r}="","",SUMIFS([[Clients.revenue]],'
                    '[[Clients.referral]],{ref_source}{r}))'),
    ]

    return SheetSpec(
        name=NAME,
        title="Calculation engine (do not edit)",
        subtitle="Helper tables for the dashboard and reports. This tab is "
                 "hidden by default - unhide it only if you want to audit "
                 "the maths.",
        columns=columns,
        rows=rows,
        tab_color="#94A3B8",
        freeze_cols=1,
        help_text="Every cell on this tab is a locked formula.",
    )
