"""`Monthly Reports` - one month, properly examined.

Pick a month at the top and everything below it follows: what sold,
what it cost, what the platforms took, what moved in and out of
stock, which products carried the month and which quietly lost money.

The month is a real drop-down, not a formula you have to edit, and
every figure on the page is driven from that one cell.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter, list_from

NAME = "Monthly Reports"
LAST_COL = 11
TOP_ROWS = 10
CHANNEL_ROWS = 10

KEY = "ReportMonth"


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary_mid)

    s.banner("Monthly Reports",
             "Pick a month. Everything below it is worked out from "
             "the registers.", LAST_COL)
    s.set_col(0, 0, 26)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 14)

    row = 4
    s.merge(row, 0, 0, "Month", fmts.chrome("label_bold"))
    s.formula(row, 1, '=TEXT(TODAY(),"yyyy-mm")', fmts.input("text"))
    s.ws.data_validation(row, 1, row, 1, list_from("MonthKeyList"))
    book.define_name(KEY, f"='{NAME}'!$B${row + 1}")
    s.merge(row, 2, 3, "Pick any month in yyyy-mm form",
            fmts.chrome("note"))
    s.merge(row, 4, 4, "Business", fmts.chrome("label_right"))
    s.merge(row, 5, 7, None, fmts.calc("text"))
    s.formula(row, 5, "=BusinessName", fmts.calc("text"))
    s.merge(row, 8, 8, "Printed", fmts.chrome("label_right"))
    s.formula(row, 9, "=TodayDate", fmts.calc("date"))
    row += 2

    # -------------------------------------------------- the headlines --
    row = s.section(row, "The month at a glance", LAST_COL)
    retail = f"SUMIFS(SaleGross,SaleMonths,{KEY},SaleIsSold,1)"
    trade = f"SUMIFS(OrderTotal,OrderMonths,{KEY},OrderIsShipped,1)"
    s.kpi(row, 0, "Revenue", f"={retail}+{trade}", "money",
          note="Retail plus shipped wholesale")
    s.kpi(row, 2, "COGS", f"=SUMIFS(ProfitCOGS,ProfitMonths,{KEY})",
          "money", note="At weighted average cost")
    s.kpi(row, 4, "Gross profit",
          f"=SUMIFS(ProfitGross,ProfitMonths,{KEY})", "money")
    s.kpi(row, 6, "Operating costs",
          f"=SUMIFS(ProfitExpenses,ProfitMonths,{KEY})", "money",
          note="Stock purchases excluded")
    s.kpi(row, 8, "Net profit",
          f"=SUMIFS(ProfitNet,ProfitMonths,{KEY})", "money")
    row = s.kpi(row, 10, "Margin",
                f'=IFERROR(SUMIFS(ProfitNet,ProfitMonths,{KEY})/'
                f'SUMIFS(ProfitRevenue,ProfitMonths,{KEY}),"")',
                "percent0", span=2)
    row += 1

    # ------------------------------------------------------ the split --
    row = s.section(row, "Where the money came from", LAST_COL)
    s.table_head(row, 0, ["", "Retail", "Wholesale", "Total",
                          "Share retail"],
                 widths=[26, 14, 14, 14, 14])
    row += 1
    rows = [
        ("Revenue", retail, trade),
        ("Units sold",
         f"SUMIFS(SaleQty,SaleMonths,{KEY},SaleIsSold,1)",
         f"SUMIFS(OrderQty,OrderMonths,{KEY},OrderIsShipped,1)"),
        ("Cost of goods",
         f"SUMIFS(SaleCOGS,SaleMonths,{KEY},SaleIsSold,1)",
         f"SUMIFS(OrderCost,OrderMonths,{KEY},OrderIsShipped,1)"),
        ("Gross profit",
         f"SUMIFS(SaleProfit,SaleMonths,{KEY},SaleIsSold,1)",
         f"SUMIFS(OrderProfit,OrderMonths,{KEY},OrderIsShipped,1)"),
    ]
    for label, left, right in rows:
        style = "int" if label == "Units sold" else "money"
        s.write(row, 0, label, fmts.chrome("label_bold"))
        s.formula(row, 1, f"={left}", fmts.calc(style))
        s.formula(row, 2, f"={right}", fmts.calc(style))
        s.formula(row, 3, f"={left}+{right}", fmts.calc(style))
        s.formula(row, 4,
                  f'=IFERROR(({left})/(({left})+({right})),"")',
                  fmts.calc("percent0"))
        row += 1
    row += 1

    # ---------------------------------------------------- what it cost --
    row = s.section(row, "What came off the top", LAST_COL)
    s.table_head(row, 0, ["Cost", "Amount", "As % of revenue",
                          "Where it is recorded"],
                 widths=[26, 14, 16, 40])
    row += 1
    costs = [
        ("Cost of goods sold",
         f"SUMIFS(ProfitCOGS,ProfitMonths,{KEY})",
         "Weighted average cost of the units that shipped"),
        ("Marketplace and payment fees",
         f"SUMIFS(SaleFees,SaleMonths,{KEY},SaleIsSold,1)+"
         f"SUMIFS(SalePaymentFees,SaleMonths,{KEY},SaleIsSold,1)",
         "Retail Sales Tracker, from the rates on Settings"),
        ("Postage you paid",
         f"SUMIFS(SaleShipCost,SaleMonths,{KEY},SaleIsSold,1)",
         "Retail Sales Tracker"),
        ("Operating expenses",
         f"SUMIFS(ExpenseOperating,ExpenseMonths,{KEY})",
         "Expense Tracker, with stock purchases excluded"),
        ("Returns and refunds",
         f"SUMIFS(ReturnLoss,ReturnMonths,{KEY})",
         "Returns & Damaged Goods, net of supplier credits"),
        ("Stock written off",
         f"SUMIFS(MovementValue,MovementMonths,{KEY},"
         f"MovementIsWriteoff,1)",
         "Stock Movement Log - damage, loss and breakage"),
    ]
    for label, formula, where in costs:
        s.write(row, 0, label, fmts.chrome("label_bold"))
        s.formula(row, 1, f"={formula}", fmts.calc("money"))
        s.formula(row, 2,
                  f'=IFERROR(({formula})/'
                  f'SUMIFS(ProfitRevenue,ProfitMonths,{KEY}),"")',
                  fmts.calc("percent0"))
        s.merge(row, 3, LAST_COL, where, fmts.chrome("note"))
        row += 1
    row += 1

    # ---------------------------------------------------- stock moves --
    row = s.section(row, "What happened to the stock", LAST_COL)
    s.kpi(row, 0, "Stock bought",
          f"=SUMIFS(ProfitStockSpend,ProfitMonths,{KEY})", "money",
          note="Received at landed cost")
    s.kpi(row, 2, "Units received",
          f"=SUMIFS(POReceived,POMonths,{KEY})", "int")
    s.kpi(row, 4, "Units out",
          f"=SUMIFS(SaleQty,SaleMonths,{KEY},SaleIsSold,1)+"
          f"SUMIFS(OrderQty,OrderMonths,{KEY},OrderIsShipped,1)",
          "int")
    s.kpi(row, 6, "Units written off",
          f"=SUMIFS(MovementDamaged,MovementMonths,{KEY})", "int",
          note="Damage and loss")
    s.kpi(row, 8, "Returns",
          f"=SUMIFS(ReturnQty,ReturnMonths,{KEY})", "int")
    row = s.kpi(row, 10, "Cash effect",
                f"=SUMIFS(ProfitCash,ProfitMonths,{KEY})", "money",
                span=2, note="Profit, adjusted for stock buying")
    row += 1

    # ---------------------------------------------------- by channel --
    row = s.section(row, "By sales channel", LAST_COL)
    s.table_head(row, 0, ["Channel", "Orders", "Units", "Revenue",
                          "Fees", "Net profit", "Margin"],
                 widths=[20, 10, 10, 14, 12, 13, 10])
    row += 1
    for n in range(1, CHANNEL_ROWS + 1):
        channel = f'IFERROR(INDEX(ChannelList,{n}),"")'
        s.formula(row, 0, f'={channel}', fmts.calc("text"))
        base = (f'SaleMonths,{KEY},SaleIsSold,1,SaleChannel,'
                f'{channel}')
        s.formula(row, 1,
                  f'=IF({channel}="","",COUNTIFS({base}))',
                  fmts.calc("int"))
        s.formula(row, 2,
                  f'=IF({channel}="","",SUMIFS(SaleQty,{base}))',
                  fmts.calc("int"))
        s.formula(row, 3,
                  f'=IF({channel}="","",SUMIFS(SaleGross,{base}))',
                  fmts.calc("money"))
        s.formula(row, 4,
                  f'=IF({channel}="","",SUMIFS(SaleFees,{base})+'
                  f'SUMIFS(SalePaymentFees,{base}))',
                  fmts.calc("money"))
        s.formula(row, 5,
                  f'=IF({channel}="","",SUMIFS(SaleProfit,{base}))',
                  fmts.calc("money"))
        s.formula(row, 6,
                  f'=IF({channel}="","",IFERROR(SUMIFS(SaleProfit,'
                  f'{base})/SUMIFS(SaleGross,{base}),""))',
                  fmts.calc("percent0"))
        row += 1
    row += 1

    # ------------------------------------------------- top performers --
    row = s.section(row, "What sold", LAST_COL)
    s.table_head(row, 0, ["SKU", "Product", "Units this month",
                          "Revenue this month", "Stock left",
                          "Days cover"],
                 widths=[16, 26, 16, 18, 13, 12])
    row += 1
    for n in range(1, TOP_ROWS + 1):
        sku = (f'IFERROR(INDEX(PerfSKU,MATCH({n},PerfRevenueRank,'
               f'0)),"")')
        s.formula(row, 0, f'={sku}', fmts.calc("id"))
        s.formula(row, 1,
                  f'=IFERROR(INDEX(PerfProduct,MATCH({n},'
                  f'PerfRevenueRank,0)),"")', fmts.calc("text"))
        s.formula(
            row, 2,
            f'=IF({sku}="","",SUMIFS(SaleQty,SaleMonths,{KEY},'
            f'SaleIsSold,1,SaleSKU,{sku})+SUMIFS(OrderQty,'
            f'OrderMonths,{KEY},OrderIsShipped,1,OrderSKU,{sku}))',
            fmts.calc("int"))
        s.formula(
            row, 3,
            f'=IF({sku}="","",SUMIFS(SaleGross,SaleMonths,{KEY},'
            f'SaleIsSold,1,SaleSKU,{sku})+SUMIFS(OrderTotal,'
            f'OrderMonths,{KEY},OrderIsShipped,1,OrderSKU,{sku}))',
            fmts.calc("money"))
        s.formula(
            row, 4,
            f'=IF({sku}="","",IFERROR(INDEX(StockAvailable,'
            f'MATCH({sku},StockSKU,0)),""))', fmts.calc("int"))
        s.formula(
            row, 5,
            f'=IF({sku}="","",IFERROR(INDEX(StockDaysCover,'
            f'MATCH({sku},StockSKU,0)),""))', fmts.calc("int"))
        row += 1
    row += 1

    # -------------------------------------------------- what went wrong --
    row = s.section(row, "What to look at", LAST_COL)
    s.table_head(row, 0, ["Question", "Answer", "Worth a look if"],
                 widths=[30, 14, 50])
    row += 1
    checks = [
        ("Sales that lost money",
         f"SUMIFS(SaleIsLoss,SaleMonths,{KEY},SaleIsSold,1)", "int",
         "More than a handful - check your fee rates and postage"),
        ("Stock counts with a variance",
         f"SUMIFS(AuditHasVariance,AuditDates,\">=\"&DATE(VALUE("
         f"LEFT({KEY},4)),VALUE(RIGHT({KEY},2)),1),AuditDates,"
         f"\"<=\"&DATE(VALUE(LEFT({KEY},4)),VALUE(RIGHT({KEY},2))"
         f"+1,0))", "int",
         "Any at all - and every one should be posted as an "
         "adjustment"),
        ("Deliveries that arrived late",
         f"SUMIFS(POIsLate,POMonths,{KEY})", "int",
         "A pattern from one supplier means raising their lead "
         "time"),
        ("Returns logged",
         f"COUNTIFS(ReturnMonths,{KEY})", "int",
         "Rising month on month, or clustered on one product"),
        ("Expenses with no receipt",
         f'COUNTIFS(ExpenseMonths,{KEY},ExpenseReceipt,"No")', "int",
         "Anything over zero, before your accountant asks"),
    ]
    for label, formula, style, when in checks:
        s.write(row, 0, label, fmts.chrome("label_bold"))
        s.formula(row, 1, f"={formula}", fmts.calc(style))
        s.merge(row, 2, LAST_COL, when, fmts.chrome("note"))
        row += 1
    row += 1

    row = s.note(
        row,
        "Revenue is recognised when goods ship, not when an order "
        "is placed. An order confirmed on the 28th and shipped on "
        "the 2nd belongs to the following month, which is why a "
        "busy end of month can look quiet here and busy next time.",
        LAST_COL, height=38)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
