"""The Shipping tab - postage bands and who really pays for them.

One row per posting option: a weight band, a carrier and a service, what it
costs you and what you charge the customer. The difference is `absorbed`, and
that is the figure the Products tab folds into a unit cost - postage you pay
out of the margin is a cost, not a fee.

`band_check` catches the two mistakes that lose money quietly: a band where the
top weight is below the bottom weight, and a band where the charge to the
customer is less than the postage costs.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, id_col, int_col, list_col, money_col, num_col,
                     pct_col, row_ref, samples, spec_defaults, text_col,
                     wrap_col, yesno_col)

P = Palette

NAME = "Shipping"

SUBTITLE = ("Postage bands: what it costs to send, what the customer pays, "
            "and what you absorb.")

HELP = ("List the posting options you actually use. 'Postage absorbed' is the "
        "part you pay - Products adds it to the unit cost. Match products by "
        "typing their IDs in 'Applies to', separated by commas.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    sid = row_ref("id")
    has_id = f'{sid}=""'
    base = f"N({row_ref('base_cost')})"
    per_oz = f"N({row_ref('per_oz')})"
    handling = f"N({row_ref('handling')})"
    top = f"N({row_ref('weight_to')})"
    bottom = f"N({row_ref('weight_from')})"
    charge = f"N({row_ref('retail_charge')})"
    absorbed = f"N({row_ref('absorbed')})"
    cost_at_max = f"{base}+{per_oz}*{top}+{handling}"

    cols: List[Any] = [
        id_col("PrefixShipping", trigger="label", width=11.0),
        text_col("label", "Option", 30.0,
                 note="The name the rest of the workbook uses for this band."),
        list_col("carrier", "Carrier", "CarrierList", 14.0),
        list_col("service", "Service", "ServiceList", 15.0),
        list_col("zone", "Zone", "ZoneList", 13.0),
        num_col("weight_from", "Weight from (oz)", 11.0),
        num_col("weight_to", "Weight to (oz)", 11.0),
        calc_col("band_check", "Band check",
                 f'IF({has_id},"",IF(AND({top}>0,{bottom}>{top}),'
                 f'"BAND REVERSED",IF({absorbed}>0.005,'
                 f'"YOU PAY THE POST","OK")))', 16.0, "status",
                 note="Bands run bottom weight to top weight; absorbed "
                      "postage is money out of the margin.",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "REVERSED", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "YOU PAY", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        money_col("base_cost", "Base postage", 12.0,
                  note="What the carrier charges for the band."),
        money_col("per_oz", "Cost an oz", 11.0, style="money4"),
        money_col("handling", "Handling cost", 12.0,
                  note="Your time and materials getting it out of the door."),
        calc_col("cost_at_max", "Cost at top weight",
                 f'IF({has_id},"",{cost_at_max})', 13.0, "money"),
        money_col("retail_charge", "Customer pays", 12.0,
                  note="The postage you charge on the listing."),
        money_col("absorbed", "Postage absorbed", 12.0,
                  note="The part of the postage you pay. This is a cost."),
        calc_col("absorbed_pct", "Absorbed %",
                 f'IF({has_id},"",IF({cost_at_max}=0,"",'
                 f'{absorbed}/{cost_at_max}))', 11.0, "percent"),
        yesno_col("tracking", "Tracked", 9.0),
        yesno_col("insurance", "Insured", 9.0),
        int_col("delivery_days", "Delivery days", 11.0),
        text_col("products", "Applies to", 26.0,
                 note="Product IDs separated by commas."),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.primary_mid))
