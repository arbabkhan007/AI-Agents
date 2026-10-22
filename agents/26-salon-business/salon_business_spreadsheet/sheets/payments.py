"""7 Payments & Deposits - money in, against bookings and invoices."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import cf_text, date_check, list_from, number_check
from . import common as C
from .. import sample_data

NAME = "7 Payments & Deposits"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="7  Payments & Deposits",
        subtitle="Every money movement: deposits held, part payments, "
                 "refunds - with the processing fee per method.",
        tab_color="#96587A",
        rows=cfg.row_count(NAME),
        freeze_cols=4,
        help_text="Kind = Deposit for money taken before a visit, Payment "
                  "for money against an invoice, Refund for money back. "
                  "Applied to holds the Appt ID or Tx ID the money belongs "
                  "to.",
        columns=[
            Col("id", "Pay ID", 10, "id",
                formula='="P-"&TEXT(ROW()-{first}+1,"0000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("client", "Client", 20, "text",
                validate=list_from("ClientNames")),
            Col("kind", "Kind", 10, "flag", validate=list_from("ListKinds"),
                cf=[cf_text("Refund", "bad"), cf_text("Deposit", "info")]),
            Col("method", "Method", 13, "text",
                validate=list_from("ListMethods")),
            Col("applied_to", "Applied to", 12, "text",
                note="The Appt ID (deposits) or Tx ID (payments) this "
                     "money settles."),
            Col("amount", "Amount", 11, "money",
                validate=number_check(0, 100000)),
            Col("fee", "Processing fee", 11, "money",
                formula='IF({amount}{r}="","",ROUND(N({amount}{r})*'
                        + C.fee_rate("{method}{r}") + ',2))'),
            Col("link_status", "Booking status", 12, "status",
                formula='IF({applied_to}{r}="","",IFERROR(INDEX('
                        'ApptStatus,MATCH({applied_to}{r},ApptIds,0)),'
                        '""))',
                note="Shows whether a deposit's appointment has happened "
                     "yet - unearned deposits stay out of revenue."),
            Col("notes", "Notes", 30, "wrap"),
        ],
        samples=sample_data.payment_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Daily cash reconciliation: filter by date and method, then "
            "compare the Cash total with the drawer.",
            "Unearned deposits = Deposit rows whose booking status is not "
            "Completed - the dashboard reports them separately.",
        ],
    )
