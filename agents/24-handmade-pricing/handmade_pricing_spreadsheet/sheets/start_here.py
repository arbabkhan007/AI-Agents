"""The Start Here tab - the front door of the workbook.

What it is for, the three things to do first, how a price is actually worked
out, what the colours mean, and a guide to all forty tabs so nobody has to open
them one by one to find out. Every tab name on this page is a link.
"""

from __future__ import annotations

from typing import Any, List, Sequence, Tuple

from ..config import PRODUCT_NAME, PRODUCT_SUBTITLE, Config, Palette
from ..layout import quote_sheet
from ..writer import SheetWriter
from .common import FIRST_ROW

P = Palette

NAME = "Start Here"

SUBTITLE = PRODUCT_SUBTITLE

#: tab, what it does, what you type in it
TAB_GUIDE: List[Tuple[str, str, str]] = [
    ("Start Here", "This page: what the workbook does and how to start.",
     "Nothing - read it."),
    ("Settings", "Your rates, fees, margins, targets and ID prefixes. "
                 "Every other tab reads this one.",
     "Your hourly rate, fees, target margin, rounding rule."),
    ("Dashboard", "The whole shop on one screen: this month, this year, the "
                  "best sellers and everything that needs a decision.",
     "Nothing - it reads the registers."),
    ("Products", "The catalog, and what each product costs and earns.",
     "Product names, prices, the minutes they take."),
    ("Materials", "Everything you buy in, what a unit costs and what is on "
                  "the shelf.",
     "Materials, unit costs, stock, re-order points."),
    ("Material Usage", "Bills of materials: what each product is made of.",
     "Product, material, quantity, scrap."),
    ("Labor", "Every hour worked, and whether it was making or running the "
              "shop.",
     "Date, who, task, hours, rate."),
    ("Packaging", "What it costs to pack one order.",
     "Components, quantities, which products they go with."),
    ("Shipping", "Postage bands, what they cost and what you absorb.",
     "Bands, costs, what the customer pays."),
    ("Overhead", "Rent, power, insurance, subscriptions - the cost of having "
                 "a studio.",
     "Each cost and how often it is paid."),
    ("Channels", "What each place you sell charges you.",
     "The fee schedule per channel."),
    ("Retail Calculator", "Price one item from scratch and see what it earns.",
     "A product, or costs typed straight in."),
    ("Wholesale Calculator", "Work out a trade price and whether it still "
                             "pays you.",
     "A product, the quantity, the discount."),
    ("Profit & Break-Even", "How many you have to sell to cover the costs, "
                            "and what different volumes earn.",
     "A product and the volumes to test."),
    ("Crochet", "Yarn, notions and hours at the hook, costed per item.",
     "Yarn, skeins, minutes, price."),
    ("Jewelry", "Metal, stones, findings and bench time.",
     "Stones, findings, minutes, price."),
    ("Candles", "One pour costed down to a single jar.",
     "Wax, fragrance load, vessels, jars poured."),
    ("Clothing", "Fabric, notions and the time cutting, sewing, finishing.",
     "Fabric, yards, the three times, price."),
    ("Woodworking", "Lumber, hardware, finish and the four stages of time.",
     "Board feet, hardware, the four times, price."),
    ("Digital", "Downloads: the investment spread over the sales you expect.",
     "Hours to create, sales expected, price."),
    ("Bundles", "Kits and gift boxes, and whether the discount still pays.",
     "Bundle name, price, packaging, postage."),
    ("Bundle Lines", "What is inside each bundle.",
     "Bundle, product, quantity."),
    ("Variations", "Sizes, colours, scents - what each option adds.",
     "Option, value, price and cost adjustments."),
    ("Batches", "What a run of making really cost, defects included.",
     "Quantities, minutes, materials."),
    ("Sales", "Every order: price, fees, postage, cost and profit.",
     "Date, product, quantity, price paid."),
    ("Promotions", "Discounts, when they run and what they gave away.",
     "Code, discount, dates."),
    ("Price History", "Every price change and what happened next.",
     "Old price, new price, why, cost at the time."),
    ("Competitors", "What comparable listings charge.",
     "Their price and postage, which of yours it matches."),
    ("Waste Log", "What got broken or spoiled, and what it cost.",
     "Date, material, quantity, reason."),
    ("Development", "What it costs to bring something new to market.",
     "Project, hours, spend, target price."),
    ("Events", "Fairs and markets costed properly, including your hours.",
     "Fees, travel, hours, revenue."),
    ("Wholesale Customers", "The shops that buy from you.",
     "Contacts, terms, discount, credit limit."),
    ("Wholesale Orders", "Trade orders from quote to paid.",
     "Shop, retail value, status."),
    ("Scenarios", "The same product priced five ways, side by side.",
     "A product and the margins to compare."),
    ("Reports", "Twelve months of trading, by product, channel and craft.",
     "Nothing - it reads the registers."),
    ("Print Costing", "A one page cost sheet for a product, to print.",
     "The product ID at the top."),
    ("Print Quote", "A wholesale quote on your shop's letterhead.",
     "The customer and the lines."),
    ("Print Order", "A production docket for the workshop.",
     "The product, the quantity, the due date."),
    ("Lists", "Every drop down in the workbook lives here.",
     "Your own values for any list."),
    ("Help", "How the maths works, how to extend the workbook, and what to "
             "do when something looks wrong.",
     "Nothing - read it."),
]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=False)
    last_col = 8
    sheet.banner(NAME, f"{cfg.product_name} - {SUBTITLE}", last_col,
                 nav=False, badge=f"{cfg.author}  |  v{cfg.version}")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 1, 22.0)
    sheet.set_col(2, 3, 26.0)
    sheet.set_col(4, last_col, 17.0)
    sheet.ws.hide_gridlines(2)

    r = 3
    r = sheet.section(r, f"Welcome to {cfg.product_name}", last_col)
    r = sheet.note(
        r,
        "This workbook costs a handmade product properly - materials, your own "
        "time at a real rate, packaging, the postage you absorb, a share of "
        "the studio overhead and the fees the channel takes - and then works "
        "out the price your target margin asks for. It does the same for six "
        "crafts, for bundles, for sizes and scents, for wholesale, and for a "
        "day at a craft fair.",
        last_col, height=58)
    r = sheet.note(
        r,
        f"It opens with an example shop in it - {cfg.shop.name}, run by "
        f"{cfg.shop.owner} - so every tab has something to look at and every "
        f"number agrees with the ones next to it. To start clean, rebuild with "
        f"the --blank flag, or delete the example rows: the formulas run the "
        f"whole way down every register, so a cleared row is simply a row that "
        f"waits.",
        last_col, height=46)
    r += 1

    # ---------------------------------------------------------- first steps
    r = sheet.section(r, "Three things to do first", last_col)
    steps = [
        ("1", "Settings", "Put in what you pay yourself an hour, the fees "
                          "your marketplace charges, and the margin you want "
                          "to be left with. Everything else reads these."),
        ("2", "Materials", "List what you buy in and what one unit costs. "
                           "Then add each product on Products and its bill of "
                           "materials on Material Usage - or cost it on the "
                           "craft tab that matches."),
        ("3", "Retail Calculator", "Pick a product and read the price the "
                                   "model asks for next to the price you "
                                   "charge. The gap between the two is the "
                                   "whole point of the workbook."),
    ]
    for number, tab, text in steps:
        sheet.row_height(r, 34)
        sheet.write(r, 1, number, fmts.chrome("kpi_label"))
        _link(sheet, fmts, r, 2, tab)
        sheet.merge(r, 3, last_col, text, fmts.chrome("note_box"))
        r += 1
    r += 1

    # --------------------------------------------------------- the maths
    r = sheet.section(r, "How a price is worked out", last_col)
    for line in [
        "Total unit cost = materials + labour + packaging + the postage you "
        "absorb + a share of overhead.",
        "Labour = minutes / 60 x the true cost of your hour, which is your "
        "rate plus the payroll burden on Settings.",
        "Suggested price = (total cost + fixed fees) / (1 - target margin - "
        "channel fee rate), rounded the way Settings says.",
        "Wholesale price = retail price less the trade discount.",
        "Profit = price - fees - total cost.    Margin = profit / price.    "
        "Effective hourly = profit / hours spent.",
    ]:
        r = sheet.note(r, line, last_col, height=17, boxed=False)
    r = sheet.note(
        r,
        "Why the margin is in the denominator: a 30% margin is not cost plus "
        "30%. If a piece costs 20 and the channel takes 10%, then 20 x 1.3 = "
        "26 leaves 6.60 after fees against a cost of 20 - a loss. The formula "
        "above asks for 33.99 and leaves the 30% you meant.",
        last_col, height=44)
    r += 1

    # ------------------------------------------------------- colour code
    r = sheet.section(r, "The colour code, and the password", last_col)
    sheet.row_height(r, 20)
    sheet.write(r, 1, "Type here", fmts.chrome("legend_label"))
    sheet.write(r, 2, "", fmts.chrome("legend_input"))
    sheet.merge(r, 3, last_col, "Cream with a soft border - yours to fill in.",
                fmts.chrome("label"))
    r += 1
    sheet.row_height(r, 20)
    sheet.write(r, 1, "Calculated", fmts.chrome("legend_label"))
    sheet.write(r, 2, "", fmts.chrome("legend_calc"))
    sheet.merge(r, 3, last_col,
                "Warm grey - a formula. Locked, so it cannot be typed over.",
                fmts.chrome("label"))
    r += 1
    r = sheet.note(
        r,
        f"Every sheet is protected with the password '{cfg.password}'. "
        f"Protection is there to stop a formula being deleted by accident, "
        f"not to keep you out: unprotect a sheet from Review > Unprotect "
        f"Sheet whenever you want to change the layout, and the input cells "
        f"stay editable either way.",
        last_col, height=44)
    r += 1

    # ---------------------------------------------------------- tab guide
    r = sheet.section(r, "What is in this workbook", last_col)
    sheet.row_height(r, 22)
    sheet.write(r, 1, "Tab", fmts.chrome("header_left"))
    sheet.merge(r, 2, 4, "What it does", fmts.chrome("header_left"))
    sheet.merge(r, 5, last_col, "What you type", fmts.chrome("header_left"))
    r += 1
    for i, (tab, does, types) in enumerate(TAB_GUIDE):
        sheet.row_height(r, 26)
        band = fmts.chrome("band") if i % 2 else None
        _link(sheet, fmts, r, 1, tab, band=band)
        sheet.merge(r, 2, 4, does, fmts.cell("wrap", "plain"))
        sheet.merge(r, 5, last_col, types, fmts.cell("wrap", "plain"))
        r += 1
    r += 1

    # ------------------------------------------------------------ the end
    r = sheet.section(r, "Compatibility, and who made it", last_col)
    for line in [
        "Formulas are written for Excel 2010 and later - no dynamic arrays, "
        "no XLOOKUP, no IFS, no LET - so the workbook also opens in Excel "
        "2010, LibreOffice and Google Sheets.",
        "It is a plain .xlsx with no macros, so nothing is blocked when you "
        "download or email it.",
        f"Created by {cfg.author}. Version {cfg.version}.",
    ]:
        r = sheet.note(r, line, last_col, height=30, boxed=False)

    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet


def _link(sheet, fmts, row: int, col: int, tab: str, band=None) -> None:
    """An internal link to another tab, in the house style."""
    fmt = band or fmts.chrome("nav")
    sheet.ws.write_url(row, col, f"internal:{quote_sheet(tab)}!A1", fmt,
                       f"> {tab}")
