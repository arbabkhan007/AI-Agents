"""Gallery & Delivery - handing the photographs over, and what happens next.

Delivery is not the end of the job.  Galleries expire, albums get
ordered months later, print sales happen only if somebody mentions
them, and the review you want is easiest to ask for in the week the
couple first sees their photographs.
"""

from __future__ import annotations

from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from, number_check
from .common import (alert_cf, booking_client_col, blank, date_num_col, id_col, lookup_booking,
                     money_cf, status_cf, yesno, zero)

NAME = "Gallery & Delivery"


def spec(cfg) -> SheetSpec:
    columns = [
        id_col("booking", "GalleryPrefix", digits=cfg.digits("gallery"),
               header="Gallery ID"),

        Col("booking", "Booking ID", 11, "id",
            validate=list_from("BookingList"),
            note="One row per wedding gallery.", group="The gallery"),
        Col("couple", "Couple", 18, "text",
            formula=lookup_booking("client_name"), group="The gallery"),
        booking_client_col(),
        Col("wedding_date", "Wedding date", 12, "date",
            formula=lookup_booking("wedding_date", missing=""),
            group="The gallery"),
        Col("platform", "Where it lives", 15, "text",
            validate=list_from("GalleryPlatformList"),
            group="The gallery"),
        Col("gallery_name", "Gallery name", 20, "text",
            group="The gallery"),
        Col("link", "Link", 26, "link",
            note="Paste the address. The workbook stores the link, "
                 "not the photographs.",
            group="The gallery"),
        Col("has_password", "Password set", 11, "flag",
            validate=yesno("Yes or No only. Never type the password "
                           "itself into a spreadsheet you email to "
                           "anybody."),
            cf=status_cf(), group="The gallery"),

        # ---- delivery ------------------------------------------------------
        Col("status", "Status", 14, "status",
            validate=list_from("GalleryStatusList"), cf=status_cf(),
            group="Delivery"),
        Col("promised", "Promised by", 12, "date",
            formula=blank("booking",
                          'IFERROR(INDEX([[Editing Workflow.due]],'
                          'MATCH({booking}{r},'
                          '[[Editing Workflow.booking]],0)),'
                          'IF({wedding_date}{r}="","",'
                          '{wedding_date}{r}+DeliveryDays))'),
            group="Delivery"),
        Col("delivered_on", "Delivered", 11, "date",
            validate=date_check(), group="Delivery"),
        Col("days_late", "Days late", 10, "int",
            formula=zero("booking",
                         'IF({promised}{r}="",0,'
                         'IF({delivered_on}{r}<>"",'
                         'MAX(0,{delivered_on}{r}-{promised}{r}),'
                         'MAX(0,TodayDate-{promised}{r})))'),
            group="Delivery"),
        Col("images", "Images in it", 11, "int",
            validate=number_check(0, 100000), group="Delivery"),
        Col("expires", "Gallery expires", 13, "date",
            formula=blank("booking",
                          'IF({delivered_on}{r}="","",'
                          '{delivered_on}{r}+GalleryLiveDays)'),
            note="How long you keep it online, from Settings. Tell "
                 "the couple this date - it is the single most common "
                 "thing a photographer gets an angry email about.",
            group="Delivery"),
        Col("expiry_warned", "Expiry warning sent", 14, "flag",
            validate=yesno(), group="Delivery"),
        Col("archived", "Archived", 10, "flag",
            validate=yesno("Taken offline but kept on your own "
                           "storage."),
            group="Delivery"),

        # ---- what the couple did -------------------------------------------
        Col("first_viewed", "First opened", 12, "date",
            validate=date_check(), group="What they did"),
        Col("views", "Views", 8, "int",
            validate=number_check(0, 1000000), group="What they did"),
        Col("downloads", "Downloads", 10, "int",
            validate=number_check(0, 1000000), group="What they did"),
        Col("favourites", "Favourites picked", 13, "int",
            validate=number_check(0, 100000), group="What they did"),
        Col("usb_sent", "USB or print box sent", 14, "flag",
            validate=yesno(), group="What they did"),
        Col("opened", "Have they looked", 12, "flag",
            formula=blank("booking",
                          'IF({delivered_on}{r}="","",'
                          'IF({first_viewed}{r}<>"","Yes",'
                          'IF(IF({views}{r}="",0,{views}{r})>0,"Yes",'
                          '"No")))'),
            cf=status_cf(), group="What they did"),

        # ---- what it earned afterwards -------------------------------------
        Col("album_ordered", "Album ordered", 12, "flag",
            validate=yesno(), group="Afterwards"),
        Col("album_due", "Album due", 11, "date",
            formula=blank("booking",
                          'IF({album_ordered}{r}<>"Yes","",'
                          'IF({delivered_on}{r}="","",'
                          '{delivered_on}{r}+AlbumDays))'),
            group="Afterwards"),
        Col("album_sent", "Album sent", 11, "date",
            validate=date_check(), group="Afterwards"),
        Col("print_sales", "Print sales", 11, "money",
            validate=number_check(0, 100000),
            note="Money the gallery made after delivery. For a lot of "
                 "photographers this is the most under-collected "
                 "revenue in the business.",
            group="Afterwards"),
        Col("extra_sales", "Other extras", 11, "money",
            validate=number_check(0, 100000), group="Afterwards"),
        Col("after_total", "Earned after delivery", 14, "money",
            formula=zero("booking",
                         'IF({print_sales}{r}="",0,{print_sales}{r})+'
                         'IF({extra_sales}{r}="",0,{extra_sales}{r})'),
            cf=money_cf(), group="Afterwards"),
        Col("review_asked", "Review asked for", 13, "date",
            validate=date_check(),
            note="Ask in the week they first open the gallery. It is "
                 "the only week they will ever be this pleased with "
                 "you.",
            group="Afterwards"),
        Col("review_in", "Review received", 12, "flag",
            formula=blank("booking",
                          'IF(COUNTIFS('
                          '[[Reviews & Referrals.booking]],'
                          '{booking}{r},[[Reviews & Referrals.status]],"Received")>0,"Yes","No")'),
            cf=status_cf(), group="Afterwards"),
        Col("notes", "Notes", 26, "wrap", group="Afterwards"),

        date_num_col("wedding_date", "wed_num", "Wedding date number"),
        date_num_col("delivered_on", "delivered_num", "Delivered number"),
        Col("is_delivered", "Delivered flag", 9, "flag",
            formula=blank("booking",
                          'IF({delivered_on}{r}<>"","Yes","No")'),
            hidden=True),

        Col("alert", "What to do", 32, "status",
            formula=(
                '=IF({booking}{r}="","",'
                'IF({delivered_on}{r}="",'
                'IF({promised}{r}="","Check - no promised date",'
                'IF(TodayDate>{promised}{r},'
                '"Overdue - past the date you promised",'
                'IF({promised}{r}-TodayDate<=7,'
                '"Due - gallery due within the week","OK"))),'
                'IF({has_password}{r}<>"Yes",'
                '"Check - gallery has no password",'
                'IF({opened}{r}="No",'
                'IF(TodayDate-{delivered_on}{r}>7,'
                '"Chase - delivered, never opened","OK"),'
                'IF({album_ordered}{r}="Yes",'
                'IF({album_sent}{r}="",'
                'IF({album_due}{r}<>"",'
                'IF(TodayDate>{album_due}{r},'
                '"Overdue - album past its date",'
                '"Action - album still to send"),'
                '"Action - album still to send"),"OK"),'
                'IF({review_in}{r}="No",'
                'IF({review_asked}{r}="",'
                'IF(TodayDate-{delivered_on}{r}<=30,'
                '"Action - ask for a review now","OK"),"OK"),'
                'IF({expires}{r}<>"",'
                'IF({expiry_warned}{r}<>"Yes",'
                'IF({expires}{r}-TodayDate<=30,'
                '"Send - warn them the gallery is closing","OK"),'
                '"OK"),"OK")))))))'),
            cf=alert_cf(), group="Afterwards"),
    ]

    return SheetSpec(
        name=NAME,
        title="Gallery & Delivery",
        subtitle=("Handing the photographs over, and everything that "
                  "should happen in the month afterwards"),
        columns=columns,
        rows=cfg.row_count(NAME),
        tab_color=None,
        freeze_cols=3,
        samples=sample("gallery", cfg),
        help_text=(
            "One row per wedding gallery. The promised date comes from "
            "the editing job, the expiry date from your own setting, "
            "and the alert column walks you through the fortnight "
            "after delivery - open the gallery, ask for the review, "
            "chase the album, warn them before it closes."),
        extra_notes=[
            "Never type a gallery password into this workbook. The "
            "'Password set' column is a Yes or No, because a "
            "spreadsheet gets emailed to accountants and left open on "
            "laptops in coffee shops.",
            "Tell the couple the expiry date when you deliver, and "
            "warn them again a month before. Galleries closing with "
            "nothing downloaded is the most avoidable complaint in "
            "wedding photography.",
            "'Earned after delivery' is money most photographers never "
            "count. Prints, extra albums, a parents' copy - all of it "
            "comes from the gallery being open and somebody asking.",
        ],
    )
