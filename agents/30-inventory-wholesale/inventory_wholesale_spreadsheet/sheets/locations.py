"""16. Warehouse Locations - where the thing actually is.

A stock figure that is right and a picker who cannot find the box are
the same problem. One row per SKU per location, so a line split
across two shelves gets two rows and both of them say how many.

The sheet also answers the question nobody asks until it is too late:
does the sum of the bin quantities match what the Inventory Tracker
thinks you have? When those two disagree, one of them is wrong, and
it is usually the bin.
"""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from .common import (alert_cf, alert_chain, date_num_col,
                     lookup_product, product_name_col, sku_col,
                     yesno, zero)
from ..writer import date_check, list_from, number_check

NAME = "Warehouse Locations"


def spec(cfg: Config) -> SheetSpec:
    cols = [
        sku_col(),
        product_name_col(),
        Col("category", "Category", 13, "text",
            formula=lookup_product("category"), hidden=True),
        Col("location", "Location", 12, "text",
            validate=list_from("LocationList"),
            note="The site or room: a unit, a garage, a shop floor, "
                 "a third party warehouse. Set the list up on "
                 "Settings."),
        Col("zone", "Zone", 9, "text",
            note="Aisle, rack or room within the location."),
        Col("bin", "Bin / shelf", 12, "text",
            note="The exact spot. 'B-14-3' beats 'the back' every "
                 "time somebody else is picking."),
        Col("qty_here", "Qty here", 10, "int",
            validate=number_check(0, 1000000),
            note="How many of this SKU are in this bin. This is a "
                 "placement record, not the stock figure - the "
                 "Inventory Tracker owns that."),
        Col("is_primary", "Primary", 8, "flag",
            validate=yesno("The first place a picker should look."),
            cf=[{"type": "text", "criteria": "containing",
                 "value": "Yes", "fmt": "good"}]),
        Col("capacity", "Capacity", 10, "int",
            validate=number_check(0, 1000000),
            note="How many fit in this bin, if it matters."),
        Col("fill", "Full", 7, "percent0",
            formula='=IF({sku}{r}="","",IF({capacity}{r}<=0,"",'
                    'ROUND({qty_here}{r}/{capacity}{r},4)))',
            cf=[{"type": "cell", "criteria": ">", "value": 1,
                 "fmt": "bad"},
                {"type": "cell", "criteria": ">", "value": 0.9,
                 "fmt": "warn"}]),
        Col("type", "Storage type", 13, "text",
            validate=list_from("StorageTypeList"),
            note="Shelf, pallet, cold store, fragile. Worth "
                 "recording for anything with a handling "
                 "requirement."),
        Col("checked", "Last checked", 12, "date",
            validate=date_check()),
        Col("notes", "Notes", 24, "wrap"),

        # ---- reconciliation ---------------------------------------
        Col("total_here", "All bins", 9, "int",
            formula=zero("sku", 'SUMIFS({qty_here_first}:'
                                '{qty_here_last},{sku_first}:'
                                '{sku_last},{sku}{r})'),
            hidden=True,
            note="Everything recorded for this SKU across every "
                 "bin."),
        Col("system_qty", "System says", 11, "int",
            formula=zero("sku", 'IFERROR(INDEX('
                                '[[Inventory Tracker.current]],'
                                'MATCH({sku}{r},'
                                '[[Inventory Tracker.sku]],0))*1,0)'),
            note="What the Inventory Tracker calculates you hold."),
        Col("placed_gap", "Unplaced", 10, "int",
            formula=zero("sku", '{system_qty}{r}-{total_here}{r}'),
            cf=[{"type": "cell", "criteria": "!=", "value": 0,
                 "fmt": "warn"}],
            note="Stock the system believes in that no bin claims. "
                 "Not necessarily missing - often just not put away "
                 "yet - but worth knowing about."),
        Col("bins_used", "Bins", 6, "int",
            formula=zero("sku", 'COUNTIFS({sku_first}:{sku_last},'
                                '{sku}{r})'),
            hidden=True),
        Col("dup_bin", "Dup", 6, "int",
            formula=zero("sku", 'IF({location}{r}="",0,'
                                'COUNTIFS({sku_first}:{sku_last},'
                                '{sku}{r},{location_first}:'
                                '{location_last},{location}{r},'
                                '{bin_first}:{bin_last},'
                                '{bin}{r}))'),
            hidden=True),
        Col("primary_count", "Primaries", 9, "int",
            formula=zero("sku", 'COUNTIFS({sku_first}:{sku_last},'
                                '{sku}{r},{is_primary_first}:'
                                '{is_primary_last},"Yes")'),
            hidden=True),

        date_num_col("checked", "checked_num"),

        Col("alert", "What needs doing", 30, "text", cf=alert_cf(),
            formula=_alert()),
    ]

    return SheetSpec(
        name=NAME,
        title="Warehouse Locations",
        subtitle=("Which shelf, which bin, how many. One row per SKU "
                  "per location."),
        columns=cols,
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        samples=sample("locations", cfg),
        help_text=("Record where things live. A SKU split across "
                   "three shelves gets three rows; mark one of them "
                   "Primary so a picker knows where to start."),
        extra_notes=[
            "The quantities here are a placement record, not the "
            "stock figure. The Inventory Tracker owns stock and "
            "always will. Unplaced simply shows the gap between the "
            "two, which is how you find the pallet nobody put away.",
            "If you only have one storage place, fill in the "
            "location and leave the zone and bin blank. The sheet "
            "is as detailed as you need it to be and no more.",
        ],
    )


def _alert() -> str:
    return alert_chain("sku", [
        ('{location}{r}=""', "Add - which location"),
        ('{dup_bin}{r}>1',
         "Duplicate - this SKU is already recorded in this exact "
         "bin"),
        ('{primary_count}{r}>1',
         "Check - more than one bin marked primary for this SKU"),
        ('AND({bins_used}{r}>1,{primary_count}{r}=0)',
         "Add - stored in several places and none marked primary"),
        ('{qty_here}{r}<=0',
         "Check - bin recorded with nothing in it"),
        ('AND({capacity}{r}>0,{qty_here}{r}>{capacity}{r})',
         "Action - more in the bin than it holds"),
        ('{placed_gap}{r}<0',
         "Check - bins hold more than the system thinks exists"),
        ('{placed_gap}{r}>0',
         "Check - stock on the system that no bin claims"),
        ('AND({checked}{r}<>"",TodayDate-{checked}{r}>180)',
         "Check - this location has not been looked at in six "
         "months"),
        ('{checked}{r}=""', "Add - date you last checked this bin"),
    ])
