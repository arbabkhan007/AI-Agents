"""Client Retention - keeping the clients you already have."""

from __future__ import annotations

from typing import Any

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Registry, quote_sheet
from .settings import settings_ref


def build_page(workbook: Any, fmts: FormatBook, reg: Registry,
               cfg: Config) -> None:
    ws = workbook.add_worksheet("Client Retention")
    ws.set_tab_color(Palette.accent)
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 2)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 18)
    ws.set_column(3, 5, 18)

    def rng(sheet: str, key: str) -> str:
        spec = reg[sheet]
        letter = spec.letter(key)
        return (f"{quote_sheet(sheet)}!${letter}${spec.first_data_row}:"
                f"${letter}${spec.last_data_row}")

    C_name = rng("Clients", "name")
    C_status = rng("Clients", "status")
    C_since = rng("Clients", "since")
    C_rating = rng("Clients", "rating")
    C_out = rng("Clients", "outstanding")
    C_jobs = rng("Clients", "active_jobs")
    C_last = rng("Clients", "last_job")
    C_billed = rng("Clients", "billed")
    J_client = rng("Jobs", "client")
    J_status = rng("Jobs", "status")
    I_balance = rng("Invoices", "balance")
    I_client = rng("Invoices", "client")
    CO_status = rng("Complaints", "status")
    CO_client = rng("Complaints", "client")
    CO_sev = rng("Complaints", "severity")
    CO_refund = rng("Complaints", "refund")

    ws.merge_range(0, 1, 0, 5, "Client Retention  ·  Keep Every Client",
                   fmts["title"])
    ws.set_row(0, 30)
    ws.merge_range(2, 1, 2, 5,
                   "It costs five times more to win a client than to keep "
                   "one. Watch the health numbers, then work the "
                   "drill-down before a call.",
                   fmts["subtitle"])

    r = 4

    def section(text: str) -> None:
        nonlocal r
        ws.merge_range(r - 1, 1, r - 1, 5, text, fmts["section"])
        r += 1

    def metric(label: str, formula: str, style: str, note: str = "") -> int:
        nonlocal r
        row = r
        ws.write(row - 1, 1, label, fmts["label"])
        ws.write_formula(row - 1, 2, formula, fmts[style])
        if note:
            ws.merge_range(row - 1, 3, row - 1, 5, note, fmts["note"])
        else:
            ws.merge_range(row - 1, 3, row - 1, 5, "", fmts["note"])
        r += 1
        return row

    # ----------------------------------------------------------- health
    section("Retention health")
    metric("Active clients", f'=COUNTIF({C_status},"Active")', "calc_int",
           "Clients marked Active on the Clients tab.")
    metric("Clients with 2+ jobs",
           f'=COUNTIF({J_client},"?*")*0+SUMPRODUCT((({C_name}<>"")*1)*'
           f'(COUNTIF({J_client},{C_name}&"")>=2))',
           "calc_int",
           "The clients who have already come back.")
    metric("Average jobs per client",
           f'=IF(COUNTIF({C_status},"Active")=0,"",'
           f'(COUNTIF({J_status},"Completed")+COUNTIF({J_status},'
           f'"Invoiced"))/COUNTIF({C_status},"Active"))',
           "calc_decimal", "")
    metric("Average satisfaction (1-5)",
           f'=IF(COUNT({C_rating})=0,"",AVERAGE({C_rating}))',
           "calc_decimal",
           "From the rating column on the Clients tab.")
    metric("Outstanding balances",
           f'=SUMIF({C_out},">0")', "calc_money",
           "Money owed by clients - friendly reminders work.")
    metric("Clients inactive too long",
           f'=SUMPRODUCT((({C_since}<>"")*1)*({C_last}<>"")*'
           f'(TODAY()-{C_last}>{settings_ref("inactive_client_days")}))'
           f'+SUMPRODUCT((({C_since}<>"")*1)*({C_last}="")*'
           f'(TODAY()-{C_since}>{settings_ref("inactive_client_days")}))',
           "calc_int",
           "No job within the inactive window on Settings.")
    metric("Open complaints",
           f'=COUNTIF({CO_status},"Open")+COUNTIF({CO_status},'
           '"Investigating")+COUNTIF({CO_status},"Escalated")',
           "calc_int", "")
    metric("Refunds / credits given",
           f'=SUM({CO_refund})', "calc_money",
           "Every refund is a lesson - log it on the Complaints tab.")
    metric("High severity complaints open",
           f'=COUNTIFS({CO_status},"<>Closed",{CO_sev},"High")'
           f'+COUNTIFS({CO_status},"<>Closed",{CO_sev},"Critical")',
           "calc_int", "Handle these within 24 hours.")
    r += 1

    # -------------------------------------------------------- drill-down
    section("Before the call - look up one client")
    ws.write(r - 1, 1, "Client name", fmts["label"])
    ws.write(r - 1, 2, "", fmts["input"])
    ws.data_validation(r - 1, 2, r - 1, 2,
                       {"validate": "list", "source": "=Clients_Names",
                        "ignore_blank": True})
    ws.merge_range(r - 1, 3, r - 1, 5,
                   "Pick a client - the panel below fills itself.",
                   fmts["note"])
    name_cell = f"$C${r}"
    r += 1

    def lookup_row(label: str, formula: str, style: str) -> None:
        nonlocal r
        ws.write(r - 1, 1, label, fmts["label"])
        ws.write_formula(r - 1, 2, formula, fmts[style])
        ws.merge_range(r - 1, 3, r - 1, 5, "", fmts["note"])
        r += 1

    match = f"MATCH({name_cell},{C_name},0)"
    lookup_row("Status",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_status},'
               f'{match}),"not found"))', "calc")
    lookup_row("Client since",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_since},'
               f'{match}),""))', "calc_date")
    lookup_row("Last job",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_last},'
               f'{match}),""))', "calc_date")
    lookup_row("Total billed",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_billed},'
               f'{match}),0))', "calc_money")
    lookup_row("Outstanding",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_out},'
               f'{match}),0))', "calc_money")
    lookup_row("Open jobs",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_jobs},'
               f'{match}),0))', "calc_int")
    lookup_row("Satisfaction",
               f'=IF({name_cell}="","",IFERROR(INDEX({C_rating},'
               f'{match}),""))', "calc_decimal")
    lookup_row("Total jobs done",
               f'=IF({name_cell}="","",COUNTIFS({J_client},{name_cell},'
               f'{J_status},"Completed")+COUNTIFS({J_client},{name_cell},'
               f'{J_status},"Invoiced"))', "calc_int")
    lookup_row("Money in (all invoices)",
               f'=IF({name_cell}="","",SUMIFS({rng("Invoices", "paid")},'
               f'{I_client},{name_cell}))', "calc_money")
    lookup_row("Complaints ever",
               f'=IF({name_cell}="","",COUNTIF({CO_client},{name_cell}))',
               "calc_int")
    r += 1

    # ----------------------------------------------------------- playbook
    section("Retention playbook")
    steps = [
        "Thank-you: after the first clean of a new client, send a short "
        "thank-you message the same evening.",
        "Check-in: every quarter, message clients who have not had a "
        "deep clean - upsell one.",
        "Birthday / anniversary: a small note beats an ad.",
        "Lapsed: anyone showing in 'inactive too long' gets a personal "
        "call, not a bulk email.",
        "Complaint recovery: fix it fast, then a small credit. A "
        "resolved complaint is more loyal than no complaint at all.",
        "Referrals: ask happy clients (rating 5) for one referral each; "
        "reward with a discount on their next clean.",
    ]
    for text in steps:
        ws.merge_range(r - 1, 1, r - 1, 5, "•  " + text, fmts["note"])
        ws.set_row(r - 1, 26)
        r += 1

    ws.freeze_panes(3, 0)
    ws.set_zoom(100)
    if cfg.protect_sheets:
        ws.protect(cfg.password, {
            "select_unlocked_cells": True,
            "select_locked_cells": True,
        })
