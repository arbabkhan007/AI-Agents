"""`Getting Started` - twenty minutes, in the right order.

Most inventory spreadsheets fail in the first hour, and almost always
for the same reason: somebody starts typing products before deciding
what a SKU means to them, and three weeks later there are four rows
for the same mug and no stock figure anybody believes.

So this page does not begin with "add your products". It begins with
the two decisions that cannot be undone cheaply - what counts as a
separate SKU, and what your opening stock really is - and only then
lets you loose on the tabs.
"""

from __future__ import annotations

from ..config import (COSTING_NOTE, DISCLAIMER, HONESTY_NOTE,
                      PRIVACY_NOTE, RESERVED_NOTE, STOCK_NOTE, Config,
                      Palette)
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Getting Started"
LAST_COL = 9

STEPS = [
    ("1. Decide what a SKU is, before you type anything",
     "A SKU is one thing you count separately. If you hold the "
     "350ml sage mug and the 250ml sage mug in different boxes and "
     "count them separately, they are two SKUs, not one product "
     "with a size option. The same goes for a six pack against a "
     "single, or a gift boxed version against a plain one. Get this "
     "wrong and no stock figure in the workbook can be right - and "
     "it is painful to fix after three hundred rows.",
     "Settings & Lists, then Product & SKU Database"),
    ("2. Set up your business and your rules",
     "Open Settings & Lists and work down it. Your name and "
     "address, your currency, your minimum acceptable margin, your "
     "lead times, and - this one matters more than it looks - what "
     "your sales channels actually charge you. The fee rates there "
     "decide whether the profit figures in this workbook are true "
     "or comforting.",
     "Settings & Lists"),
    ("3. Add your products and your opening stock",
     "One row per SKU on the Product & SKU Database. Fill in the "
     "cost, the retail price and the trade price. Then put in "
     "Opening stock and Opening value: how many you have right now "
     "and what they cost you in total. This is the only time you "
     "will ever type a stock quantity - from here on stock is "
     "calculated.",
     "Product & SKU Database"),
    ("4. Add your suppliers",
     "Who you buy from, their terms, and their quoted lead time. "
     "The lead time seeds the reorder planner until the workbook "
     "has enough of your own delivery history to know what they "
     "really take, at which point it quietly starts using that "
     "instead.",
     "Supplier Database"),
    ("5. Check the Inventory Tracker",
     "Go and look. Every product should have a line with your "
     "opening stock in it, calculated rather than typed. If a "
     "number is wrong, the fix is never to overwrite it - the fix "
     "is to correct the opening figure on the product record, "
     "because that is the only typed stock number in the workbook.",
     "Inventory Tracker"),
    ("6. Set your wholesale prices",
     "Wholesale Pricing already has a row per SKU. Put in your base "
     "trade price and up to three quantity breaks. Watch the GP% "
     "column next to each price rather than the price itself - that "
     "is the whole reason it is there.",
     "Wholesale Pricing"),
    ("7. Add your stockists",
     "Wholesale Customer CRM. The important cell is Price tier: "
     "every order they place prices itself off it, so you never "
     "quote by hand again. Set their payment terms and a credit "
     "limit while you are there.",
     "Wholesale Customer CRM"),
    ("8. Start trading",
     "Raise purchase orders when you buy, enter wholesale orders "
     "when a shop orders, and type or paste your retail sales in as "
     "they come. Move an order's status along as it progresses. "
     "That is the whole daily routine - everything else in the "
     "workbook is calculated from those three tabs.",
     "Purchase Orders, Wholesale Orders, Retail Sales Tracker"),
    ("9. Work off the Dashboard each morning",
     "Out of stock, below minimum, orders waiting to pick, "
     "deliveries running late, money overdue. Five minutes on the "
     "Dashboard replaces an hour of scrolling, and the four "
     "integrity counts in the middle should all read zero.",
     "Dashboard"),
    ("10. Count the shelf now and again",
     "Use Stock Audit. Count your highest value lines monthly and "
     "everything else once or twice a year. When a count disagrees "
     "with the system, write the difference on the Stock Movement "
     "Log as an adjustment with a reason - that is the step that "
     "actually moves the figure.",
     "Stock Audit, Stock Movement Log"),
]

DAILY = [
    "Enter yesterday's retail sales, or paste them from your "
    "marketplace export.",
    "Move any wholesale order that progressed to its new status - "
    "Confirmed, Packed, Shipped.",
    "Book in anything that arrived, by putting the quantity in the "
    "Qty received cell on its purchase order line.",
    "Glance at the Dashboard: anything Urgent or Overdue.",
]

WEEKLY = [
    "Work the Reorder Planner top down and raise the purchase "
    "orders it suggests.",
    "Chase late deliveries and overdue invoices from the Dashboard "
    "lists.",
    "Log any damage or loss on the Stock Movement Log while you "
    "still remember what happened.",
    "Check the four integrity counts on the Dashboard are all zero.",
]

MONTHLY = [
    "Cycle count your A lines - the few SKUs holding most of your "
    "money, listed on Inventory Valuation & COGS.",
    "Read the Monthly Report and compare the margin to last month.",
    "Review Product Performance by Return on stock without sorting rows, and "
    "decide what to clear.",
    "Review any price whose margin has drifted, on Wholesale "
    "Pricing.",
]

MISTAKES = [
    ("Typing over a stock figure",
     "There is nowhere to do it, and that is the single best thing "
     "about this workbook. Every quantity is derived from recorded "
     "events. If a figure is wrong, something is missing - a "
     "receipt, a sale, a breakage - and the fix is to record it."),
    ("Logging a purchase receipt on the Stock Movement Log",
     "Do not. Receipts belong in the Qty received cell on the "
     "purchase order line. The movement log is for damage, loss, "
     "gifts, production use, transfers and corrections only - "
     "anything else gets counted twice."),
    ("Two lines on one purchase order for the same SKU",
     "That is the one way to book the same delivery in twice. The "
     "Duplicate line column flags it in red. If a second shipment "
     "arrives against an existing line, update the received "
     "quantity to the running total instead."),
    ("Selling against In stock instead of Available",
     "In stock includes units already promised to a confirmed "
     "order. Available is what you can still sell. Quote from "
     "Available or you will sell the same pallet twice."),
    ("Typing stock purchases into the Expense Tracker",
     "They are already counted as cost of goods through the "
     "purchase orders. The workbook flags them and keeps them out "
     "of the operating cost total, but it is cleaner not to type "
     "them at all."),
    ("Leaving freight off a purchase order line",
     "Landed cost drives the weighted average, which drives every "
     "margin in the workbook. Carriage left off is margin you think "
     "you have and do not."),
]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.deep)

    s.banner("Getting Started",
             "Twenty minutes, in an order that will save you a "
             "fortnight.", LAST_COL)
    s.set_col(0, 0, 4)
    s.set_col(1, 1, 38)
    s.set_col(2, 7, 15)
    s.set_col(8, LAST_COL, 18)

    row = 4
    row = s.note(
        row,
        "This workbook has twenty-three tabs and you do not need "
        "most of them today. Do the ten steps below in order and "
        "you will have a working stock system this afternoon; the "
        "reporting tabs will have filled themselves in by the time "
        "you get round to looking at them.",
        LAST_COL, height=42)
    row += 1

    # ------------------------------------------------------ the rules --
    row = s.section(row, "Three things to know first", LAST_COL)
    row = s.note(row, STOCK_NOTE, LAST_COL, height=60)
    row += 1
    row = s.note(row, RESERVED_NOTE, LAST_COL, height=56)
    row += 1
    row = s.note(row, COSTING_NOTE, LAST_COL, height=80)
    row += 1

    # ---------------------------------------------------------- steps --
    row = s.section(row, "The ten steps", LAST_COL)
    for title, body, where in STEPS:
        s.merge(row, 0, 1, title, fmts.chrome("label_bold"))
        s.merge(row, 2, 7, body, fmts.chrome("note"))
        s.merge(row, 8, LAST_COL, where, fmts.chrome("legend_calc"))
        s.row_height(row, 54)
        row += 1
    row += 1

    # ------------------------------------------------------- routines --
    row = s.section(row, "The routine, once you are running", LAST_COL)
    s.merge(row, 0, 2, "Every day", fmts.chrome("header"))
    s.merge(row, 3, 6, "Every week", fmts.chrome("header"))
    s.merge(row, 7, LAST_COL, "Every month", fmts.chrome("header"))
    row += 1
    tallest = max(len(DAILY), len(WEEKLY), len(MONTHLY))
    for index in range(tallest):
        if index < len(DAILY):
            s.merge(row, 0, 2, f"- {DAILY[index]}",
                    fmts.chrome("note"))
        if index < len(WEEKLY):
            s.merge(row, 3, 6, f"- {WEEKLY[index]}",
                    fmts.chrome("note"))
        if index < len(MONTHLY):
            s.merge(row, 7, LAST_COL, f"- {MONTHLY[index]}",
                    fmts.chrome("note"))
        s.row_height(row, 34)
        row += 1
    row += 1

    # ------------------------------------------------------- mistakes --
    row = s.section(row, "Six ways to get it wrong", LAST_COL)
    row = s.note(
        row,
        "Every one of these has been designed against, so the "
        "workbook will usually stop you or shout at you. They are "
        "listed anyway, because understanding why a rule exists is "
        "how you remember it.",
        LAST_COL, height=32)
    row += 1
    for title, body in MISTAKES:
        s.merge(row, 0, 1, title, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, body, fmts.chrome("note"))
        s.row_height(row, 46)
        row += 1
    row += 1

    # ---------------------------------------------------- how it works --
    row = s.section(row, "How the tabs fit together", LAST_COL)
    chains = [
        ("Product -> SKU -> stock",
         "A product on the Product Database creates a SKU. The "
         "Inventory Tracker gives it a stock line automatically. "
         "Every other tab joins on that SKU."),
        ("Supplier -> purchase order -> receiving",
         "A supplier gets an ID. A purchase order line points at "
         "it. Putting a quantity in Qty received adds stock, "
         "updates the weighted average cost, and records how long "
         "that supplier really took."),
        ("Customer -> tier -> price -> order",
         "A stockist has a price tier. An order line reads the "
         "tier, finds the right quantity break on Wholesale "
         "Pricing, applies any account discount and shows you the "
         "margin before you confirm."),
        ("Movement -> reorder alert -> replenishment",
         "Sales and receipts move the stock figure. The Reorder "
         "Planner compares it against (daily sales x lead time) + "
         "safety stock and tells you what to buy and by when."),
        ("Sale -> COGS -> product profit",
         "A sale takes units out at weighted average cost. That "
         "cost becomes COGS on the valuation tab, which becomes "
         "profit per product on Product Performance, which becomes "
         "the business profit on Profit Analysis."),
    ]
    for title, body in chains:
        s.merge(row, 0, 1, title, fmts.chrome("label_bold"))
        s.merge(row, 2, LAST_COL, body, fmts.chrome("note"))
        s.row_height(row, 40)
        row += 1
    row += 1

    # ---------------------------------------------------------- honest --
    row = s.section(row, "What this workbook is not", LAST_COL)
    row = s.note(row, HONESTY_NOTE, LAST_COL, height=62)
    row += 1
    row = s.note(row, PRIVACY_NOTE, LAST_COL, height=48)
    row += 1
    row = s.note(row, DISCLAIMER, LAST_COL, height=76)
    row += 1

    row = s.section(row, "Protection", LAST_COL)
    row = s.note(
        row,
        f"Formula cells are locked so a stray paste cannot wipe out "
        f"a calculation, and every sheet is protected with the "
        f"password '{cfg.password}'. Input cells are left unlocked - "
        f"you can type in all of them without unprotecting anything. "
        f"If you do want to change a formula, unprotect the sheet in "
        f"Excel under Review, make the change, and protect it again.",
        LAST_COL, height=48)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
