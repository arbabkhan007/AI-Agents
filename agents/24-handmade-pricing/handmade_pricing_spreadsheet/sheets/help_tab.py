"""The Help tab - the manual that lives inside the workbook.

Three kinds of question get answered here, in this order: how the pricing maths
works, what the words mean, and what to do when a number looks wrong. The
glossary is deliberately plain - every term is defined the way it is used on the
tabs, not the way a textbook defines it.

Nothing on this page calculates. It is the one sheet where reading is the work.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from ..config import Config, Palette
from ..writer import SheetWriter
from .common import CRAFT_LIST

P = Palette

NAME = "Help"

SUBTITLE = ("How the pricing maths works, what the words mean, and what to do "
            f"when a number looks wrong.")

HELP = ("Read top to bottom once. Come back to the glossary and the "
        "troubleshooting table whenever something does not add up.")

LAST_COL = 12

# ---------------------------------------------------------------------------
# the maths, in words
# ---------------------------------------------------------------------------

MATHS: List[Tuple[str, str]] = [
    ("The price formula",
     "Price = (cost of one item + fixed fees) / (1 - target margin - fee "
     "rate). The division is the whole trick: it grosses the cost up so that "
     "after the marketplace takes its percentage and you take your margin, "
     "what is left still covers the cost. Adding a percentage on top does "
     "not do that."),
    ("Why the fee rate is in the denominator",
     "A percentage fee is charged on the selling price, not on the cost. If "
     "you added 6.5% to the cost you would be short every time. Dividing by "
     "(1 - fee rate) is what makes the fee pay for itself."),
    ("Cost of one item",
     "Materials from the bill of materials, plus labour (minutes over sixty "
     "times the true cost of your hour), plus packaging, plus any postage you "
     "absorb, plus your share of overhead. Every part is on its own tab and "
     "every part is visible on Products."),
    ("The true cost of your hour",
     "What you pay yourself, loaded: HourlyRate x (1 + PayrollBurden). It "
     "sits on Settings as LaborCostHour. The burden covers the tax, insurance "
     "and admin that come with an hour of work but never show on a payslip."),
    ("Overhead, three ways",
     "Settings asks how you want the rent, the tools and the subscriptions "
     "spread: per hour of making, per unit made, or as a monthly total "
     "divided by the units you expect to make that month. The number that "
     "reaches Products is OverheadPerUnit either way."),
    ("Margin versus markup",
     "Margin is profit as a share of the price; markup is profit as a share "
     "of the cost. A 50% markup is a 33% margin. This workbook thinks in "
     "margin, because that is what a marketplace fee comes off."),
    ("Rounding",
     "The rounding rule on Settings turns $18.41 into $18.99 or $19.00 or "
     "leaves it alone. It is applied to the model's answer, so the price you "
     "see is a price a human would actually charge."),
    ("Wholesale price",
     "Retail price x (1 - WholesaleDiscount), rounded the same way. The "
     "Wholesale Calculator then checks what that leaves you after the trade "
     "fee, because a 40% discount on a thin retail margin can be a loss."),
    ("Effective hourly",
     "Profit an item divided by the hours it takes to make one. It is the "
     "only figure that tells you whether a product is worth your time rather "
     "than merely profitable on paper."),
    ("Break-even",
     "Fixed costs divided by the profit on one item: how many you have to "
     "sell before the month stops losing money. The Profit & Break-Even tab "
     "runs it six ways so you can see how sensitive it is."),
]

# ---------------------------------------------------------------------------
# glossary
# ---------------------------------------------------------------------------

GLOSSARY: List[Tuple[str, str]] = [
    ("Bill of materials (BOM)",
     "The list of materials one product uses, with a quantity for each. It "
     "lives on Material Usage and feeds the cost on Products."),
    ("Batch",
     "A run of the same product made at once. Batches spread setup time and "
     "waste over the units in the run, which lowers the cost of each."),
    ("Bundled product",
     "Two or more products sold together as one listing. Bundles re-price "
     "from their lines, never from a number typed by hand."),
    ("Contribution",
     "Price minus everything that moves with the sale: cost and fees. It is "
     "what each unit contributes to the fixed costs."),
    ("Craft tab",
     f"The six making calculators - {', '.join(CRAFT_LIST[:3])} and "
     f"{', '.join(CRAFT_LIST[3:])}. Each builds a product from the parts "
     "that craft actually uses and writes the result into the catalog."),
    ("Defect rate",
     "The share of a batch that fails quality control. It raises the cost of "
     "the pieces that pass."),
    ("Effective hourly",
     "What an hour of making this product earns you after costs and fees."),
    ("Fixed fees",
     "The fees that do not move with the price: a listing fee, a processing "
     "fee, a flat charge. They sit in the numerator of the price formula."),
    ("Loaded hourly rate",
     "Your hourly rate plus the payroll burden - the real cost of an hour."),
    ("Margin",
     "Profit as a share of the selling price. MarginWarning on Settings is "
     "the level below which a product is flagged THIN."),
    ("Offsite ads fee",
     "The extra percentage a marketplace takes when it brings the sale "
     "itself. It is applied to the share of sales you expect it to bring."),
    ("Overhead",
     "Costs that do not belong to one product: rent, tools, subscriptions, "
     "insurance. Spread by the method chosen on Settings."),
    ("Postage you absorb",
     "The part of the shipping cost you pay rather than charge. If the "
     "listing says free shipping, all of it is absorbed."),
    ("Price gap",
     "The difference between the price you charge and the price the model "
     "asks for. Positive means the listing is under-priced."),
    ("Productive hours",
     "The hours a month you actually spend making, not the hours you work."),
    ("Rank column",
     "A hidden column on a register that numbers its rows by some value. The "
     "Dashboard and Reports use it to find the top five without an array "
     "formula."),
    ("Re-order point",
     "The stock level at which a material should be ordered again, set from "
     "how much you use and how long an order takes."),
    ("Scrap",
     "Material lost in making - offcuts, spilled wax, a dropped bead. The "
     "scrap percentage raises the quantity bought, not the quantity used."),
    ("Scenario",
     "One product priced at several target margins side by side. The "
     "Scenarios tab shows five plus the price you charge today."),
    ("Suggested price",
     "What the formula asks for after rounding. It is a recommendation, not "
     "an override - your retail price stays yours until you change it."),
    ("Trade discount",
     "The percentage off retail a wholesale customer gets. Set per customer, "
     "defaulting to WholesaleDiscount on Settings."),
    ("Units per month",
     "How many items you expect to make in a month. It drives the per-unit "
     "share of overhead, so it matters more than it looks."),
    ("Waste",
     "Material or product that never earns: spoilage, seconds, returns that "
     "cannot be resold. The Waste Log costs each entry and Reports totals it."),
]

# ---------------------------------------------------------------------------
# how to
# ---------------------------------------------------------------------------

HOW_TO: List[Tuple[str, str]] = [
    ("Price a new product",
     "1. Add it on Products (or on its craft tab, which fills Products for "
     "you). 2. List its materials on Material Usage. 3. Record the time on "
     "Labor, or use the minutes the craft tab calculated. 4. Read the "
     "suggested price and set your retail price."),
    ("Check whether an item is worth making",
     "Open Products, find its Effective hourly and its flag. If the flag says "
     "LOSS, the price does not cover the cost and fees. If the hourly is "
     "below the minimum wage on Settings, it covers them but not your time."),
    ("Prepare for a craft fair",
     "Events tab: enter the stall fee, your hours and what you expect to "
     "sell. It returns profit, profit an hour and a verdict. Compare the "
     "verdicts before you book the same fair twice."),
    ("Quote a shop",
     "Wholesale Customers for the shop and its terms, then Print Quote: pick "
     "the shop, type the lines, print one page. The trade discount, tax and "
     "totals are already worked out."),
    ("Run a promotion without losing money",
     "Promotions tab: it takes the discount off the retail price and shows "
     "the profit and margin left. If the margin goes below MarginWarning it "
     "says so before you commit."),
    ("Find out what is eating the margin",
     "Reports: the by-category table shows where the money is, the worst "
     "margin table shows which products are dragging, and the waste figure "
     "shows what never earned anything at all."),
    ("See a year at a glance",
     "Reports, month by month, and the Dashboard for this month. Both follow "
     "the date on your computer, so neither goes stale."),
]

# ---------------------------------------------------------------------------
# troubleshooting
# ---------------------------------------------------------------------------

TROUBLE: List[Tuple[str, str]] = [
    ("I cannot type in a cell",
     "That cell is calculated. Every sheet is protected so that formulas "
     "cannot be overwritten by accident; the cells you are meant to fill are "
     "shaded. To unprotect a sheet: Review, Unprotect Sheet, password "
     "premium."),
    ("A number looks wrong",
     "Follow it back. Every calculated cell is a formula you can click and "
     "read: Formulas, Trace Precedents shows exactly which cells feed it. "
     "Almost always the answer is a blank input upstream - a missing cost, a "
     "missing minute count, a channel with no fee rate."),
    ("A dropdown is missing or empty",
     "Dropdowns read the Lists tab and the registers. If a product dropdown "
     "is empty there are no products yet; if a list is missing, check the "
     "Lists tab has not been overtyped."),
    ("The top-five tables are blank",
     "They need at least one row with a value on the register they read. "
     "They also need the hidden rank columns - unhide columns on Products if "
     "you hid them and the tables will come back."),
    ("Dates look like numbers",
     "The cell has lost its date format. Select it and apply a date format; "
     "the value underneath is fine."),
    ("My margins changed overnight",
     "The fee schedule is date sensitive: FeesReviewed on Settings counts the "
     "days since you last checked your marketplace's fees, and FeeStale says "
     "when that has gone past FeeReviewDays. Nothing in the workbook changes "
     "your fees by itself."),
    ("Printing cuts columns off",
     "Every sheet is set to fit one page wide with its own print area. If you "
     "added columns past the print area, set a new one: Page Layout, Print "
     "Area, Set Print Area."),
    ("Excel offers to repair the file",
     "It should not. This workbook is written with formulas Excel 2010 "
     "understands and no dynamic arrays. If it ever happens, keep a copy and "
     "tell us which version of Excel you are on."),
]

# ---------------------------------------------------------------------------
# compatibility and the small print
# ---------------------------------------------------------------------------

COMPAT: List[Tuple[str, str]] = [
    ("Excel versions",
     "Excel 2010 and later, on Windows and on the Mac, plus LibreOffice "
     "Calc, Google Sheets and Numbers. Every formula is written the "
     "old-fashioned way: no XLOOKUP, no LET, no IFS, no dynamic arrays, no "
     "spill."),
    ("Macros and scripts",
     "None. The file is a plain .xlsx, so no security prompt and nothing "
     "that a work computer will refuse to open."),
    ("Cloud",
     "It works on OneDrive, SharePoint, Google Drive and Dropbox. On the "
     "web versions of Excel the formulas calculate the same way; only "
     "printing and protection behave slightly differently."),
    ("Protection",
     "Sheets are protected with the password premium so formulas survive. "
     "Protection is a guard rail, not encryption - it does not hide "
     "anything, and you can remove it in two clicks."),
    ("Your data",
     "Everything lives in this one file on your own machine or your own "
     "cloud folder. Nothing is sent anywhere and nothing phones home."),
    ("Currency and units",
     "Settings changes the currency symbol and the units of measure. The "
     "maths does not care which you use, as long as it is the same "
     "throughout."),
]


def _height(text: str, chars: int = 96) -> int:
    """Row height for a wrapped line of text."""
    lines = max(1, -(-len(text) // chars))
    return 13 * lines + 6


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary_mid,
                        landscape=True)
    sheet.banner(NAME, SUBTITLE, LAST_COL, badge="Read me")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 3, 20.0)
    sheet.set_col(4, LAST_COL, 13.0)
    sheet.ws.hide_gridlines(2)

    def pair(row: int, question: str, answer: str,
             q_fmt=None, a_fmt=None) -> int:
        sheet.row_height(row, _height(answer))
        sheet.merge(row, 1, 3, question,
                    q_fmt or fmts.chrome("label_bold"))
        sheet.merge(row, 4, LAST_COL, answer,
                    a_fmt or fmts.chrome("label"))
        return row + 1

    r = sheet.note(3, HELP, LAST_COL, height=28)

    r = sheet.section(r, "The pricing maths, in plain words", LAST_COL)
    for question, answer in MATHS:
        r = pair(r, question, answer)
    r += 1

    r = sheet.section(r, "Glossary", LAST_COL)
    r = sheet.subsection(r, "Every term the tabs use, defined the way it is "
                            "used here", LAST_COL)
    for term, meaning in GLOSSARY:
        r = pair(r, term, meaning)
    r += 1

    r = sheet.section(r, "How to", LAST_COL)
    for task, steps in HOW_TO:
        r = pair(r, task, steps)
    r += 1

    r = sheet.section(r, "When something does not add up", LAST_COL)
    for symptom, fix in TROUBLE:
        r = pair(r, symptom, fix)
    r += 1

    r = sheet.section(r, "Compatibility and the small print", LAST_COL)
    for topic, text in COMPAT:
        r = pair(r, topic, text)
    r += 1

    r = sheet.section(r, "Where each thing lives", LAST_COL)
    groups: List[Tuple[str, str]] = [
        ("Set up", "Start Here, Settings, Lists, Help"),
        ("What you sell", "Products, Variations, Bundles, Bundle Lines, "
                          "Development"),
        ("What it costs", "Materials, Material Usage, Labor, Packaging, "
                          "Shipping, Overhead, Waste Log"),
        ("What it should cost", "Retail Calculator, Wholesale Calculator, "
                                "Profit & Break-Even, Scenarios"),
        ("Making it", "Crochet, Jewelry, Candles, Clothing, Woodworking, "
                      "Digital, Batches"),
        ("Selling it", "Sales, Channels, Promotions, Price History, "
                       "Competitors, Events"),
        ("Trade", "Wholesale Customers, Wholesale Orders, Print Quote"),
        ("Reading it back", "Dashboard, Reports, Print Costing, Print Order"),
    ]
    for group, tabs in groups:
        r = pair(r, group, tabs)
    r += 1

    r = sheet.note(
        r,
        f"{cfg.product_name} - version {cfg.version}, created by {cfg.author}. "
        f"Currency {cfg.currency_symbol} ({cfg.currency_code}). Every figure "
        f"in this "
        f"workbook is calculated from your own inputs; nothing is estimated "
        f"behind your back and nothing leaves the file.",
        LAST_COL, height=44)

    sheet.ws.freeze_panes(4, 0)
    sheet.ws.print_area(0, 0, r, LAST_COL)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet
