"""6 Sales & Transactions - the money register."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import cf_text, date_check, list_from, number_check
from . import common as C
from .. import sample_data

NAME = "6 Sales & Transactions"


def spec(cfg: Config) -> SheetSpec:
    taxflag = C.taxable_flag("{item}{r}")
    return SheetSpec(
        name=NAME,
        title="6  Sales & Transactions",
        subtitle="One row per invoice line - unit price, tax, net, fees "
                 "and the outstanding balance calculate as you type.",
        tab_color="#6D2E4F",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="Log every sale: services completed and retail products. "
                  "Unit price looks itself up from the service menu or the "
                  "product list; tax follows the taxable flag and the rate "
                  "on Settings.",
        columns=[
            Col("id", "Tx ID", 10, "id",
                formula='="T-"&TEXT(ROW()-{first}+1,"0000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("client", "Client", 20, "text",
                validate=list_from("ClientNames")),
            Col("staff", "Staff", 16, "text",
                validate=list_from("StaffNames")),
            Col("type", "Type", 9, "flag", validate=list_from("ListTxType"),
                note="Service or Retail - drives which price list and "
                     "which commission rule applies."),
            Col("item", "Service / product", 28, "text",
                note="Pick the exact menu or product name."),
            Col("qty", "Qty", 6, "int", validate=number_check(0, 99, False)),
            Col("unit", "Unit price", 10, "money",
                formula='IF({item}{r}="","",IFERROR(INDEX(ServicePrice,'
                        'MATCH({item}{r},ServiceNames,0)),IFERROR(INDEX('
                        'ProductRetail,MATCH({item}{r},ProductNames,0)),'
                        '"")))'),
            Col("gross", "Gross", 10, "money",
                formula='IF({unit}{r}="","",ROUND(N({qty}{r})'
                        '*N({unit}{r}),2))'),
            Col("discount", "Discount", 10, "money",
                validate=number_check(0, 100000)),
            Col("refund", "Refund", 10, "money",
                validate=number_check(0, 100000)),
            Col("tax", "Tax", 9, "money",
                formula='IF({gross}{r}="","",ROUND((N({gross}{r})'
                        '-N({discount}{r})-N({refund}{r}))*TaxRate*'
                        + taxflag + ',2))'),
            Col("net", "Net", 10, "money",
                formula='IF({gross}{r}="","",ROUND(N({gross}{r})'
                        '-N({discount}{r})-N({refund}{r})+N({tax}{r}),2))',
                note="Net sales = gross - discounts - refunds + tax. "
                     "This is the number every report uses."),
            Col("method", "Method", 13, "text",
                validate=list_from("ListMethods")),
            Col("paid", "Paid", 10, "money",
                validate=number_check(0, 100000),
                note="What the client actually paid on this line. Split "
                     "payments: log the rest on tab 7 against this Tx ID."),
            Col("balance", "Owing", 10, "money",
                formula='IF({net}{r}="","",ROUND(N({net}{r})'
                        '-N({paid}{r}),2))',
                cf=[cf_text("-", "bad")]),
            Col("fee", "Processing fee", 11, "money",
                formula='IF({net}{r}="","",ROUND(N({net}{r})*'
                        + C.fee_rate("{method}{r}") + ',2))'),
            Col("cat", "Category", 11, "text",
                formula='IF({item}{r}="","",IFERROR(INDEX(ServiceCat,'
                        'MATCH({item}{r},ServiceNames,0)),"Retail"))'),
            Col("rate", "Comm rate", 9, "percent", hidden=True,
                formula='IF({type}{r}<>"Service","",IF(IFERROR(INDEX('
                        'StaffMethod,MATCH({staff}{r},StaffNames,0)),'
                        '"Percentage")="Category",IFERROR(INDEX('
                        'CatCommRate,MATCH({cat}{r},CatNames,0)),0),'
                        'IFERROR(INDEX(StaffSvcRate,MATCH({staff}{r},'
                        'StaffNames,0)),0)))'),
            Col("dup", "dup", 7, "flag", hidden=True,
                formula='IF({id}{r}="","",IF(COUNTIFS({id_first}:{id_last},'
                        '{id}{r})>1,"DUP",""))'),
            Col("notes", "Notes", 30, "wrap"),
        ],
        samples=sample_data.sales_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Deposits are recorded on tab 7, never as a second sale - so "
            "revenue is never counted twice.",
            "The hidden DUP column flags a repeated Tx ID; the Owing "
            "column turns red while a balance remains.",
        ],
    )


def decorate(sheet, fmts, cfg, reg) -> None:
    spec_ = reg[NAME]
    sheet.ws.conditional_format(
        spec_.first_data_row - 1, spec_.index("balance"),
        spec_.last_data_row - 1, spec_.index("balance"),
        {"type": "cell", "criteria": ">", "value": 0.001,
         "format": sheet.f.cf("bad")})
    sheet.ws.conditional_format(
        spec_.first_data_row - 1, spec_.index("dup"),
        spec_.last_data_row - 1, spec_.index("dup"),
        {"type": "text", "criteria": "containing", "value": "DUP",
         "format": sheet.f.cf("bad")})
