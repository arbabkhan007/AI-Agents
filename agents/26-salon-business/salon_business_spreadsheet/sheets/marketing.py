"""15 Marketing & Promotions - campaigns, gift certs and packages."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import date_check, list_from, number_check
from .. import sample_data

NAME = "15 Marketing & Promotions"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="15  Marketing & Promotions",
        subtitle="Campaign log with spend versus attributed revenue, new "
                 "clients per channel, gift certificates and prepaid "
                 "packages.",
        tab_color="#96587A",
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        help_text="Log each campaign with its channel and dates. New "
                  "clients counts CRM rows whose source matches the "
                  "channel, so attribution stays honest.",
        columns=[
            Col("id", "Camp ID", 9, "id",
                formula='="M-"&TEXT(ROW()-{first}+1,"00")'),
            Col("campaign", "Campaign", 28, "text"),
            Col("channel", "Channel", 13, "text",
                validate=list_from("ListChannels")),
            Col("start", "Start", 12, "date", validate=date_check()),
            Col("end", "End", 12, "date", validate=date_check()),
            Col("spend", "Spend", 10, "money",
                validate=number_check(0, 100000)),
            Col("revenue", "Attributed revenue", 13, "money",
                validate=number_check(0, 1000000),
                note="Revenue you can honestly tie to the campaign."),
            Col("new_clients", "New clients", 10, "int",
                formula='IF({channel}{r}="","",COUNTIFS(ClientSource,'
                        '{channel}{r}))'),
            Col("roi", "ROI", 9, "percent",
                formula='IF(OR({spend}{r}="",N({spend}{r})=0),"",'
                        '({revenue}{r}-{spend}{r})/{spend}{r})'),
            Col("notes", "Offer & learning", 34, "wrap"),
        ],
        samples=sample_data.marketing_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet, fmts, cfg, reg) -> None:
    row = reg[NAME].last_data_row + 3
    last = 8
    sheet.section(row, "GIFT CERTIFICATE REGISTER", last)
    row += 1
    sheet.table_head(row, 0, ["Code", "Client", "Value", "Issued",
                              "Expires", "Redeemed", "Balance", "Notes"])
    for i in range(12):
        r = row + 1 + i
        for c in range(8):
            style = {0: "text", 1: "text", 2: "money", 3: "date",
                     4: "date", 5: "money", 7: "wrap"}[c] if c in (0, 1, 2, 3, 4, 5, 7) else "text"
            sheet.write(r, c, None, sheet.f.input(style))
        sheet.formula(r, 6, f'=IF($C${r}="","",ROUND(N($C${r})-N($F${r}),2))',
                      sheet.f.calc("money"))
    row += 15
    sheet.section(row, "PACKAGE & PREPAID SERVICE REGISTER", last)
    row += 1
    sheet.table_head(row, 0, ["Package", "Client", "Sessions included",
                              "Sessions used", "Paid", "Per session",
                              "Sessions left", "Notes"])
    for i in range(12):
        r = row + 1 + i
        for c in (0, 1, 2, 3, 4, 7):
            style = {0: "text", 1: "text", 2: "int", 3: "int",
                     4: "money", 7: "wrap"}[c]
            sheet.write(r, c, None, sheet.f.input(style))
        sheet.formula(r, 5, f'=IF(OR($C${r}="",N($C${r})=0),"",'
                            f'ROUND(N($E${r})/$C${r},2))',
                      sheet.f.calc("money"))
        sheet.formula(r, 6, f'=IF($C${r}="","",N($C${r})-N($D${r}))',
                      sheet.f.calc("int"))
    sheet.note(row + 14,
               "Gift certificates are a liability until redeemed - the "
               "balance column shows what you still owe in services.",
               last)
