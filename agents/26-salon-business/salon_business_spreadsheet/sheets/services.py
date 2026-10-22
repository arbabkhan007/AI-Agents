"""5 Services & Pricing - the menu with costs, margins and ranking."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import list_from, number_check, yes_no
from .. import sample_data

NAME = "5 Services & Pricing"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="5  Services & Pricing",
        subtitle="Your menu: price, duration, direct costs, gross profit "
                 "and a live popularity ranking from the sales register.",
        tab_color="#B98A2F",
        rows=cfg.row_count(NAME),
        freeze_cols=3,
        help_text="Add every service you sell. Gross profit = price - "
                  "product cost - labour cost; the ranking column counts "
                  "sales on tab 6 so popular services rise by themselves.",
        columns=[
            Col("id", "Svc ID", 9, "id",
                formula='="S-"&TEXT(ROW()-{first}+1,"000")'),
            Col("category", "Category", 11, "text",
                validate=list_from("ListCats")),
            Col("name", "Service", 30, "text",
                note="The exact name your drop downs and sales rows use."),
            Col("description", "What it includes", 40, "wrap"),
            Col("duration", "Mins", 7, "int",
                validate=number_check(5, 600, False)),
            Col("price", "Price", 10, "money",
                validate=number_check(0, 100000)),
            Col("addon", "Add-on price", 11, "money",
                validate=number_check(0, 100000),
                note="Optional extra sold with the service."),
            Col("promo", "Promo price", 11, "money",
                validate=number_check(0, 100000),
                note="Campaign price - use it on tab 15 and invoice it "
                     "on tab 6 with a discount line."),
            Col("product_cost", "Product cost", 11, "money",
                validate=number_check(0, 100000),
                note="Backbar product used per service, at cost."),
            Col("labour_cost", "Labour cost", 11, "money",
                validate=number_check(0, 100000),
                note="Minutes / 60 x the hourly cost of the chair."),
            Col("gross", "Gross profit", 11, "money",
                formula='IF({price}{r}="","",ROUND(N({price}{r})'
                        '-N({product_cost}{r})-N({labour_cost}{r}),2))'),
            Col("margin", "Margin", 8, "percent",
                formula='IF(OR({price}{r}="",N({price}{r})=0),"",'
                        '({gross}{r})/{price}{r})'),
            Col("taxable", "Taxable", 8, "flag",
                validate=list_from("ListConsent"),
                note="Yes applies the tax rate from Settings on sales."),
            Col("active", "On menu", 8, "flag", validate=yes_no()),
            Col("sold", "Times sold", 9, "int",
                formula='IF({name}{r}="","",COUNTIFS(SalesItem,{name}{r},'
                        'SalesType,"Service"))'),
            Col("revenue", "Revenue", 12, "money",
                formula='IF({name}{r}="","",ROUND(SUMIFS(SalesNet,'
                        'SalesItem,{name}{r},SalesType,"Service"),2))'),
            Col("rank", "Rank", 7, "int",
                formula='IF(OR({name}{r}="",{revenue}{r}=""),"",RANK('
                        '{revenue}{r},RevenueAll))',
                note="1 = your best earner. RANK ignores blank rows."),
            Col("planned", "Planned new price", 12, "money",
                validate=number_check(0, 100000),
                note="Price-increase planning: type it here first, then "
                     "move it to Price when you are ready."),
        ],
        samples=sample_data.service_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Margin under about 50% usually means the price, the product "
            "cost or the time needs a second look.",
            "The Rank column feeds the top-services blocks on the "
            "Dashboard and Analytics tabs.",
        ],
    )
