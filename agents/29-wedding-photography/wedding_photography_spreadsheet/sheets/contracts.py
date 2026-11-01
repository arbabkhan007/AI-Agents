"""Contracts & Documents - a register of paperwork, not a contract tool.

This tab records which documents exist for a wedding, where they are
kept and whether they have come back signed.  It does not draft them,
it does not sign them and it is not a substitute for a contract written
for your jurisdiction.
"""

from __future__ import annotations

from ..config import CONTRACT_NOTE
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, blank, date_num_col, id_col, lookup_booking,
                     lookup_booking_num, status_cf, yesno, zero)

NAME = "Contracts & Documents"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "ContractPrefix", digits=cfg.digits("contract"),
               header="Document ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="Which wedding this document belongs to. One booking "
                 "can have several documents.",
            group="The document"),
        Col("couple", "Couple", 20, "text",
            formula=lookup_booking("client_name"), group="The document"),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The document"),
        Col("doc_type", "Document", 18, "text",
            validate=list_from("DocumentTypeList"),
            note="Contract, model release, venue permit, invoice, "
                 "insurance certificate - whatever the wedding needs.",
            group="The document"),
        Col("title", "Title or reference", 26, "text",
            group="The document"),
        Col("required", "Needed", 9, "flag",
            validate=yesno("No for optional paperwork, so it stops "
                           "showing up as missing."),
            group="The document"),

        # ---- where it is up to ----------------------------------------------
        Col("status", "Status", 15, "status",
            validate=list_from("DocumentStatusList"), cf=status_cf(),
            group="Where it is up to"),
        Col("sent_date", "Sent", 11, "date",
            validate=date_check(), group="Where it is up to"),
        Col("signed_date", "Signed or received", 13, "date",
            validate=date_check(), group="Where it is up to"),
        Col("expires", "Expires", 11, "date",
            validate=date_check(),
            note="For anything with a shelf life - a venue permit, a "
                 "certificate of insurance.",
            group="Where it is up to"),
        Col("stored_at", "Where it is kept", 26, "text",
            note="A folder name, a cloud link, a filing cabinet "
                 "drawer. The workbook does not hold the file itself.",
            group="Where it is up to"),
        Col("signers", "Who signs", 18, "text",
            group="Where it is up to"),
        Col("notes", "Notes", 28, "wrap", group="Where it is up to"),

        # ---- the chase --------------------------------------------------------
        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        Col("is_done", "Complete", 9, "flag",
            formula=blank("booking",
                          'IF({signed_date}{r}<>"","Yes",'
                          'IF({status}{r}="Signed","Yes",'
                          'IF({status}{r}="Counter-signed","Yes",'
                          'IF({status}{r}="Filed","Yes",'
                          'IF({status}{r}="Not needed","Yes","No")))))'),
            hidden=True),
        Col("days_out", "Days since sent", 11, "int",
            formula=blank("booking",
                          'IF({sent_date}{r}="","",'
                          'IF({is_done}{r}="Yes","",'
                          'TodayDate-{sent_date}{r}))'),
            group="The chase"),
        Col("turnaround", "Days to sign", 11, "int",
            formula=blank("booking",
                          'IF({sent_date}{r}="","",'
                          'IF({signed_date}{r}="","",'
                          '{signed_date}{r}-{sent_date}{r}))'),
            group="The chase"),
        Col("days_to_wedding", "Days to wedding", 13, "int",
            formula=blank("booking",
                          'IF({wedding_date}{r}="","",'
                          '{wedding_date}{r}-TodayDate)'),
            group="The chase"),
        Col("booking_value", "Booking value", 13, "money",
            formula=zero("booking", lookup_booking_num("total_value")[1:]),
            note="What is riding on this piece of paper.",
            group="The chase"),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({required}{r}="No","",'
                'IF({is_done}{r}="Yes",'
                'IF({expires}{r}="","OK",'
                'IF({expires}{r}<TodayDate,"Expired - needs renewing",'
                'IF({expires}{r}-TodayDate<=30,'
                '"Due - expires within a month","OK"))),'
                'IF({sent_date}{r}="",'
                'IF({days_to_wedding}{r}<>"",'
                'IF({days_to_wedding}{r}<=30,'
                '"Urgent - not sent and the wedding is close",'
                '"Send - not sent yet"),"Send - not sent yet"),'
                'IF({days_to_wedding}{r}<>"",'
                'IF({days_to_wedding}{r}<=14,'
                '"Urgent - still unsigned, wedding is next",'
                'IF({days_out}{r}>DocumentChaseDays,'
                '"Chase - sent a while ago, nothing back","OK")),'
                'IF({days_out}{r}>DocumentChaseDays,'
                '"Chase - sent a while ago, nothing back","OK"))))))'),
            cf=alert_cf(), group="The chase"),
    ]

    return SheetSpec(
        name=NAME,
        title="Contracts & Documents",
        subtitle=("A register of the paperwork for each wedding - what "
                  "exists, where it is kept and what is still missing"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("contracts", cfg),
        help_text=(
            "One row per document per wedding. Record what you sent, "
            "when it came back and where the signed copy lives. The "
            "booking row shows the status of its contract, and this "
            "tab chases anything unsigned as the wedding gets closer."),
        extra_notes=[
            CONTRACT_NOTE,
            "This is a tracking register. It does not draft documents, "
            "it cannot sign anything, and it is not legal advice. Have "
            "your contract written or checked by somebody qualified in "
            "your country - a wedding contract that has never been "
            "read by a lawyer is worth what you paid for it.",
            "The workbook stores a location, not the file. Keep the "
            "signed copies wherever you normally keep them and put the "
            "folder name or link in 'Where it is kept'.",
        ],
    )
