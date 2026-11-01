"""`Annual Reports` - the year, and whether it was a good one.

Twelve months side by side, then the questions you only ask once a
year: what is the stock actually worth at the year end, how many
times did it turn, what proportion of it never sold, which
twenty per cent of products made eighty per cent of the profit, and
what is the business worth keeping doing.

This is also the page to print for an accountant. The closing stock
valuation, the cost of goods sold and the costing method are all
stated on it explicitly, which is the first thing they will ask for.
"""

from __future__ import annotations

from ..config import COSTING_NOTE, DISCLAIMER, Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Annual Reports"
LAST_COL = 13
TOP_ROWS = 12
CATEGORY_ROWS = 8


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.deep)

    s.banner("Annual Reports",
             "The whole year, and the figures an accountant will ask "
             "for.", LAST_COL)
    s.set_col(0, 0, 24)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 12)

    row = 4
    s.merge(row, 0, 0, "Year", fmts.chrome("label_bold"))
    s.formula(row, 1, "=ReportYear", fmts.calc("int"))
    s.merge(row, 2, 4, "Set on Settings & Lists",
            fmts.chrome("note"))
    s.merge(row, 5, 5, "Business", fmts.chrome("label_right"))
    s.merge(row, 6, 9, None, fmts.calc("text"))
    s.formula(row, 6, "=BusinessName", fmts.calc("text"))
    s.merge(row, 10, 10, "Printed", fmts.chrome("label_right"))
    s.formula(row, 11, "=TodayDate", fmts.calc("date"))
    row += 2

    # ------------------------------------------------- the year's totals --
    row = s.section(row, "The year", LAST_COL)
    s.kpi(row, 0, "Revenue", "=SUM(ProfitRevenue)", "money")
    s.kpi(row, 2, "COGS", "=SUM(ProfitCOGS)", "money",
          note="Weighted average")
    s.kpi(row, 4, "Gross profit", "=SUM(ProfitGross)", "money")
    s.kpi(row, 6, "Operating costs", "=SUM(ProfitExpenses)", "money")
    s.kpi(row, 8, "Net profit", "=SUM(ProfitNet)", "money")
    s.kpi(row, 10, "Net margin",
          '=IFERROR(SUM(ProfitNet)/SUM(ProfitRevenue),"")',
          "percent0")
    row = s.kpi(row, 12, "vs target",
                '=IF(YearlyTarget<=0,"",SUM(ProfitRevenue)/'
                'YearlyTarget-1)', "percent0", span=1)
    row += 1

    # ------------------------------------------------------- the months --
    row = s.section(row, "Month by month", LAST_COL)
    s.table_head(row, 0, ["", "Jan", "Feb", "Mar", "Apr", "May",
                          "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                          "Dec"],
                 widths=[24] + [12] * 12)
    row += 1
    lines = [
        ("Revenue", "revenue", "money"),
        ("Retail", "retail_revenue", "money"),
        ("Wholesale", "wholesale_revenue", "money"),
        ("COGS", "cogs", "money"),
        ("Gross profit", "gross_profit", "money"),
        ("Margin", "gross_margin", "percent0"),
        ("Operating costs", "expenses", "money"),
        ("Net profit", "net_profit", "money"),
        ("Stock bought", "stock_spend", "money"),
        ("Cash effect", "cash_effect", "money"),
    ]
    for label, key, style in lines:
        s.write(row, 0, label, fmts.chrome("label_bold"))
        for month in range(1, 13):
            s.formula(
                row, month,
                f'=IFERROR(INDEX([[Profit Analysis.{key}]],'
                f'{month}),"")', fmts.calc(style))
        if style == "money":
            s.cf(f"B{row + 1}:M{row + 1}",
                 {"type": "cell", "criteria": "<", "value": 0,
                  "fmt": "bad"})
        row += 1
    row += 1

    # ------------------------------------------------ the stock position --
    row = s.section(row, "Stock at the year end", LAST_COL)
    row = s.note(
        row,
        "These are the numbers an accountant asks for. Closing "
        "stock is valued at weighted average cost, the same method "
        "used in every calculation in this workbook.",
        LAST_COL, height=32)
    row += 1
    s.kpi(row, 0, "Closing stock at cost", "=TotalStockValue",
          "money", note="Weighted average")
    s.kpi(row, 2, "At retail value", "=SUM(StockRetailValue)",
          "money")
    s.kpi(row, 4, "SKUs held",
          "=SUMPRODUCT((StockCurrent>0)*1)", "int")
    s.kpi(row, 6, "Units held", "=SUM(StockCurrent)", "int")
    s.kpi(row, 8, "Stock turns",
          '=IFERROR(SUM(ProfitCOGS)/TotalStockValue,"")', "number1",
          note="COGS divided by stock held")
    s.kpi(row, 10, "Dead stock value", "=SUM(ValuationDead)",
          "money", note="No sales in the window")
    row = s.kpi(row, 12, "Written off",
                "=SUM(ValuationWriteoff)", "money", span=1)
    row += 1

    # --------------------------------------------------- by category --
    row = s.section(row, "By category", LAST_COL)
    s.table_head(row, 0, ["Category", "SKUs", "Units sold",
                          "Revenue", "COGS", "Gross profit", "GP%",
                          "Stock held", "Share of stock"],
                 widths=[20, 9, 12, 13, 12, 13, 9, 13, 14])
    row += 1
    for n in range(1, CATEGORY_ROWS + 1):
        cat = f'IFERROR(INDEX(CategoryList,{n}),"")'
        s.formula(row, 0, f'={cat}', fmts.calc("text"))
        s.formula(row, 1,
                  f'=IF({cat}="","",COUNTIFS(PerfCategory,{cat}))',
                  fmts.calc("int"))
        s.formula(row, 2,
                  f'=IF({cat}="","",SUMIFS(PerfUnits,PerfCategory,'
                  f'{cat}))', fmts.calc("int"))
        s.formula(row, 3,
                  f'=IF({cat}="","",SUMIFS(PerfRevenue,'
                  f'PerfCategory,{cat}))', fmts.calc("money"))
        s.formula(row, 4,
                  f'=IF({cat}="","",SUMIFS(ValuationCOGS,'
                  f'StockCategory,{cat}))', fmts.calc("money"))
        s.formula(row, 5,
                  f'=IF({cat}="","",SUMIFS(PerfProfit,PerfCategory,'
                  f'{cat}))', fmts.calc("money"))
        s.formula(row, 6,
                  f'=IF({cat}="","",IFERROR(SUMIFS(PerfProfit,'
                  f'PerfCategory,{cat})/SUMIFS(PerfRevenue,'
                  f'PerfCategory,{cat}),""))',
                  fmts.calc("percent0"))
        s.formula(row, 7,
                  f'=IF({cat}="","",SUMIFS(StockValueCol,'
                  f'StockCategory,{cat}))', fmts.calc("money"))
        s.formula(row, 8,
                  f'=IF({cat}="","",IFERROR(SUMIFS(StockValueCol,'
                  f'StockCategory,{cat})/TotalStockValue,""))',
                  fmts.calc("percent0"))
        row += 1
    row += 1

    # ------------------------------------------------------ top products --
    row = s.section(row, "The products that carried the year",
                    LAST_COL)
    s.table_head(row, 0, ["Rank", "SKU", "Product", "Units",
                          "Revenue", "Profit", "GP%",
                          "Return on stock", "Running share"],
                 widths=[7, 16, 26, 10, 13, 13, 9, 14, 14])
    row += 1
    first_top = row
    for n in range(1, TOP_ROWS + 1):
        s.write(row, 0, n, fmts.calc("int"))
        for col, field, style in ((1, "PerfSKU", "id"),
                                  (2, "PerfProduct", "text"),
                                  (3, "PerfUnits", "int"),
                                  (4, "PerfRevenue", "money"),
                                  (5, "PerfProfit", "money"),
                                  (6, "PerfGP", "percent0"),
                                  (7, "PerfReturnOnStock",
                                   "percent0")):
            s.formula(row, col,
                      f'=IFERROR(INDEX({field},MATCH({n},'
                      f'PerfProfitRank,0)),"")', fmts.calc(style))
        s.formula(
            row, 8,
            f'=IFERROR(SUM($F${first_top + 1}:$F{row + 1})/'
            f'SUM(PerfProfit),"")', fmts.calc("percent0"))
        row += 1
    row = s.note(
        row,
        "Running share is the cumulative profit of the lines above, "
        "as a share of the whole year. If three products get you "
        "past sixty per cent, that is where your attention belongs "
        "- and it is also a concentration risk worth naming out "
        "loud.",
        LAST_COL, height=38)
    row += 1

    # --------------------------------------------------- the suppliers --
    row = s.section(row, "Suppliers", LAST_COL)
    s.kpi(row, 0, "Suppliers used",
          '=SUMPRODUCT((SupplierSpend>0)*1)', "int")
    s.kpi(row, 2, "Total spend", "=TotalPurchaseSpend", "money")
    s.kpi(row, 4, "Still committed", "=SUM(SupplierOpenValue)",
          "money", note="Ordered, not delivered")
    s.kpi(row, 6, "Late deliveries", "=SUM(POIsLate)", "int")
    s.kpi(row, 8, "Biggest supplier share",
          '=IFERROR(MAX(SupplierSpend)/TotalPurchaseSpend,"")',
          "percent0", note="Over half is a risk")
    row = s.kpi(row, 10, "Avg lead gap",
                '=IFERROR(SUMPRODUCT(SupplierLeadGap)/'
                'SUMPRODUCT((SupplierLeadGap<>"")*1),"")',
                "number1", span=3,
                note="Days slower than quoted, on average")
    row += 1

    # ---------------------------------------------------- the customers --
    row = s.section(row, "Wholesale customers", LAST_COL)
    s.kpi(row, 0, "Customers who ordered",
          "=SUMPRODUCT((CustomerOrders>0)*1)", "int")
    s.kpi(row, 2, "Wholesale revenue", "=WholesaleRevenue", "money")
    s.kpi(row, 4, "Wholesale profit", "=SUM(CustomerProfit)",
          "money")
    s.kpi(row, 6, "Still owed", "=SUM(CustomerOwing)", "money")
    s.kpi(row, 8, "Overdue", "=SUM(CustomerOverdue)", "money")
    row = s.kpi(row, 10, "Biggest account share",
                '=IFERROR(MAX(CustomerRevenue)/WholesaleRevenue,"")',
                "percent0", span=3,
                note="A third or more is a concentration risk")
    row += 1

    # ------------------------------------------------------- year notes --
    row = s.section(row, "For your accountant", LAST_COL)
    row = s.note(row, COSTING_NOTE, LAST_COL, height=80)
    row += 1
    row = s.note(
        row,
        "Closing stock at cost, cost of goods sold and gross "
        "profit are all on this page and all computed on the same "
        "weighted average basis. Operating expenses exclude stock "
        "purchases, which are capitalised into inventory and "
        "released through COGS as goods sell.",
        LAST_COL, height=44)
    row += 1
    row = s.note(row, DISCLAIMER, LAST_COL, height=76)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
