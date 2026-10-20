"""The Competitors tab - what the market already pays.

One row per comparable listing: who sells it, what they charge, what postage
they add, and which of your products it compares with. Your price comes off the
Products tab, so the comparison never goes stale on your side.

`price_gap` is the honest figure - their price plus their postage against
yours. The example shop's chunky scarf is the reason this tab exists: it sells
at 68 while the closest comparable sells at 145 plus postage, which means the
problem is not the market, it is the price.

`check_flag` goes STALE after two months, because a competitor comparison that
has not been looked at for a season is a guess with a date on it.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, fetch, id_col, int_col, link_col,
                     list_col, money_col, num_col, product_col, row_ref,
                     samples, spec_defaults, text_col, wrap_col)

P = Palette

NAME = "Competitors"

SUBTITLE = ("Comparable listings: what they charge, what you charge, and how "
            "far apart the two are.")

HELP = ("One row per comparable listing. Pick which of your products it "
        "compares with and your price arrives from the catalog. Add their "
        "postage so the comparison is like for like.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    cid = row_ref("id")
    has_id = f'{cid}=""'
    mine = row_ref("my_product")
    their_price = f"N({row_ref('competitor_price')})"
    their_ship = f"N({row_ref('shipping')})"
    their_all_in = f"({their_price}+{their_ship})"
    my_price = f"N({row_ref('my_price')})"

    cols: List[Any] = [
        id_col("PrefixCompetitor", trigger="name", width=11.0),
        text_col("name", "Shop", 28.0,
                 note="Who sells it. Filling this in starts the row."),
        link_col("url", "Listing URL", 30.0),
        text_col("product", "Their product", 28.0),
        list_col("category", "Category", "CategoryList", 20.0),
        product_col("my_product", "Your product", 13.0,
                    note="Which of your products this compares with."),
        calc_col("my_product_name", "Your product name",
                 f'IF({mine}="","",{fetch("Products", "id", "name", mine)})',
                 28.0, "text"),
        money_col("competitor_price", "Their price", 12.0),
        money_col("shipping", "Their postage", 12.0,
                  note="What they charge to send it - free postage is 0."),
        calc_col("their_all_in", "Their all-in",
                 f'IF({has_id},"",{their_all_in})', 12.0, "money"),
        calc_col("my_price", "Your price",
                 f'IF({has_id},"",{fetch("Products", "id", "retail_price", mine, "0")})',
                 12.0, "money"),
        calc_col("my_absorbed_postage", "Postage you absorb",
                 f'IF({has_id},"",{fetch("Products", "id", "shipping_cost", mine, "0")})',
                 13.0, "money",
                 note="Postage you pay out of the margin - it widens the real "
                      "gap between you and them."),
        calc_col("price_gap", "Gap",
                 f'IF({has_id},"",{my_price}-{their_all_in})', 11.0, "money",
                 cf=[{"type": "cell", "criteria": "<", "value": 0,
                      "fmt": "info"},
                     {"type": "cell", "criteria": ">", "value": 0,
                      "fmt": "good"}]),
        calc_col("gap_pct", "Gap %",
                 f'IF({has_id},"",IF({their_all_in}=0,"",'
                 f'({my_price}-{their_all_in})/{their_all_in}))', 10.0,
                 "percent"),
        calc_col("position", "Position",
                 f'IF(OR({has_id},{their_all_in}=0),"",'
                 f'IF({my_price}<{their_all_in}*0.98,"Cheaper",'
                 f'IF({my_price}>{their_all_in}*1.02,"Premium","Same")))',
                 12.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "Cheaper", "fmt": "info"},
                     {"type": "text", "criteria": "containing",
                      "value": "Premium", "fmt": "good"}]),
        num_col("rating", "Their rating", 11.0,
                note="Out of 5, as shown on the listing."),
        int_col("reviews", "Their reviews", 11.0),
        text_col("sales", "Their sales", 13.0,
                 note="What the listing claims: 10k+, 500+, a number."),
        calc_col("their_strength", "How established",
                 f'IF({has_id},"",IF(N({row_ref("reviews")})>1000,'
                 f'"BIG SELLER",IF(N({row_ref("reviews")})>200,'
                 f'"ESTABLISHED",IF(N({row_ref("reviews")})>0,"NEW",'
                 f'"NO REVIEWS"))))', 15.0, "status"),
        calc_col("my_margin", "Your margin",
                 f'IF({has_id},"",{fetch("Products", "id", "margin", mine)})',
                 11.0, "percent",
                 note="From the catalog - handy when a comparable is much "
                      "more expensive than you."),
        date_col("last_checked", "Last checked", 13.0),
        calc_col("check_flag", "Check",
                 f'IF(OR({has_id},{row_ref("last_checked")}=""),"",'
                 f'IF(TodayDate-N({row_ref("last_checked")})>60,"STALE","OK"))',
                 10.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "STALE", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        wrap_col("notes", "Notes", 32.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
