"""`Dashboard` - the page that answers "what do I need to do today?"

Everything here is worked out from the registers, so nothing is ever
out of date and there is nothing to refresh. The questions are in the
order somebody running stock actually asks them: what am I about to
run out of, what is somebody waiting for, where is my money, what is
my stock worth, and which products are actually earning their shelf.

The stock panel at the top is the one that matters. Out of stock,
critically low and reserved-but-not-shipped are three different kinds
of problem and they need three different responses, so they get three
different tiles rather than one vague "low stock" count.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Dashboard"
LAST_COL = 12
ACTION_ROWS = 10
LIST_ROWS = 8
MONTHS = 6


def _month_key(n: int) -> str:
    """The `yyyy-mm` key for n months before this one."""
    if n == 0:
        return 'TEXT(TodayDate,"yyyy-mm")'
    return (f'TEXT(DATE(YEAR(TodayDate),MONTH(TodayDate)-{n},1),'
            f'"yyyy-mm")')


def _by_rank(sheet: str, rank_key: str, field: str, n: int) -> str:
    """The nth row of a register by one of its hidden rank columns."""
    return (f'IFERROR(INDEX([[{sheet}.{field}]],MATCH({n},'
            f'[[{sheet}.{rank_key}]],0)),"")')


def _alert_count(sheet: str, prefix: str) -> str:
    """How many rows on a register are shouting a given prefix."""
    return f'COUNTIF([[{sheet}.alert]],"{prefix}*")'


#: every register that carries an alert column
ALERT_SHEETS = [
    "Product & SKU Database", "Inventory Tracker",
    "Stock Movement Log", "Supplier Database", "Purchase Orders",
    "Wholesale Customer CRM", "Wholesale Pricing", "Wholesale Orders",
    "Retail Sales Tracker", "Reorder Planner",
    "Inventory Valuation & COGS", "Returns & Damaged Goods",
    "Warehouse Locations", "Stock Audit", "Product Performance",
    "Expense Tracker", "Profit Analysis",
]


def _all_alerts(prefix: str) -> str:
    """Total rows across the workbook whose alert starts with prefix."""
    return "+".join(_alert_count(sheet, prefix)
                    for sheet in ALERT_SHEETS)


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary)

    s.banner("Inventory & Wholesale Dashboard",
             "Your stock, your orders and your money - worked out "
             "from the tabs you have already filled in.",
             LAST_COL)
    s.set_col(0, 0, 26)
    for column in range(1, LAST_COL + 1):
        s.set_col(column, column, 13)

    # ------------------------------------------------------------ head --
    row = 4
    s.merge(row, 0, 0, "Business", fmts.chrome("label_bold"))
    s.merge(row, 1, 3, None, fmts.calc("text"))
    s.formula(row, 1, "=BusinessName", fmts.calc("text"))
    s.merge(row, 4, 4, "Month", fmts.chrome("label_right"))
    s.formula(row, 5, '=TEXT(TodayDate,"mmmm yyyy")',
              fmts.calc("text"))
    s.merge(row, 6, 6, "SKUs", fmts.chrome("label_right"))
    s.formula(row, 7, "=SUM(ProductActive)", fmts.calc("int"))
    s.merge(row, 8, 8, "Today", fmts.chrome("label_right"))
    s.formula(row, 9, "=TodayDate", fmts.calc("date"))
    s.merge(row, 10, LAST_COL, None, fmts.chrome("note"))
    s.formula(
        row, 10,
        '="Figures update the moment you type. Nothing to refresh."',
        fmts.chrome("note"))
    row += 2

    # ----------------------------------------------------- stock panel --
    row = s.section(row, "Stock right now", LAST_COL)
    s.kpi(row, 0, "Out of stock", "=SUM(StockIsOut)", "int",
          note="Nothing available to sell")
    s.kpi(row, 2, "Below minimum", "=SUM(StockIsLow)", "int",
          note="Still sellable, but not for long")
    s.kpi(row, 4, "Needs reordering", "=SUM(ReorderNeeded)", "int",
          note="Lines the planner says to buy")
    s.kpi(row, 6, "Reserved units", "=SUM(StockReserved)", "int",
          note="Promised to confirmed orders, not yet shipped")
    s.kpi(row, 8, "Units on order", "=SUM(StockOnOrder)", "int",
          note="Ordered from suppliers, not arrived")
    row = s.kpi(row, 10, "Dead lines", "=SUM(StockIsDead)", "int",
                span=3, note="Holding stock with no recent sales")
    row += 1

    # ----------------------------------------------------- money panel --
    row = s.section(row, "The money", LAST_COL)
    s.kpi(row, 0, "Stock at cost", "=TotalStockValue", "money",
          note="Weighted average cost")
    s.kpi(row, 2, "Stock at retail", "=SUM(StockRetailValue)",
          "money", note="What it would fetch if it all sold")
    s.kpi(row, 4, "Owed to you", "=SUM(CustomerOwing)", "money",
          note="Invoiced wholesale, unpaid")
    s.kpi(row, 6, "Overdue", "=SUM(CustomerOverdue)", "money",
          note="Past its due date - chase these")
    s.kpi(row, 8, "Committed to suppliers",
          "=SUM(POOutstandingValue)", "money",
          note="Ordered and not yet delivered")
    row = s.kpi(row, 10, "To spend on reorders",
                "=SUM(ReorderValue)", "money", span=3,
                note="What the planner is suggesting")
    row += 1

    # --------------------------------------------------- trading panel --
    row = s.section(row, "Trading this month", LAST_COL)
    month_sale = ('SUMIFS(SaleGross,SaleMonths,ThisMonthKey,'
                  'SaleIsSold,1)')
    month_trade = ('SUMIFS(OrderTotal,OrderMonths,ThisMonthKey,'
                   'OrderIsShipped,1)')
    s.kpi(row, 0, "Revenue this month",
          f"={month_sale}+{month_trade}", "money",
          note="Retail and shipped wholesale")
    s.kpi(row, 2, "Retail", f"={month_sale}", "money")
    s.kpi(row, 4, "Wholesale", f"={month_trade}", "money")
    s.kpi(row, 6, "vs target",
          f'=IF(MonthlyTarget<=0,"",({month_sale}+{month_trade})/'
          f'MonthlyTarget)', "percent0",
          note="Against the Settings target")
    s.kpi(row, 8, "Gross margin",
          '=IFERROR(SUMIFS(ProfitGross,ProfitMonths,ThisMonthKey)/'
          'SUMIFS(ProfitRevenue,ProfitMonths,ThisMonthKey),"")',
          "percent0", note="This month, from Profit Analysis")
    row = s.kpi(row, 10, "Orders to pick",
                "=SUMPRODUCT(OrderIsReserved*OrderFirstLine)", "int",
                span=3, note="Confirmed and waiting to ship")
    row += 1

    # ------------------------------------------------------- integrity --
    row = s.section(row, "Things that would break the numbers",
                    LAST_COL)
    row = s.note(
        row,
        "These four counts should all be zero. A duplicate SKU means "
        "two products share one stock figure; a duplicate purchase "
        "order line means a delivery can be booked in twice; an "
        "unposted stock count means your shelf and your spreadsheet "
        "disagree and nobody has said why; negative stock means "
        "something was sold that was never received.",
        LAST_COL, height=44)
    row += 1
    s.kpi(row, 0, "Duplicate SKUs",
          "=SUMPRODUCT((ProductDupCount>1)*1)", "int",
          note="Two rows sharing one code")
    s.kpi(row, 2, "Duplicate PO lines",
          "=SUMPRODUCT((PODupLine>1)*1)", "int",
          note="Same PO, same SKU, twice")
    s.kpi(row, 4, "Counts not posted", "=SUM(AuditUnposted)", "int",
          note="Variance found, adjustment never written")
    s.kpi(row, 6, "Negative stock",
          "=SUMPRODUCT((StockCurrent<0)*1)", "int",
          note="Sold more than was ever received")
    s.kpi(row, 8, "Lines short of stock",
          "=SUMPRODUCT((OrderShortfall>0)*1)", "int",
          note="Promised more than you hold")
    row = s.kpi(row, 10, "Unclaimed supplier faults",
                "=SUM(ReturnUnclaimed)", "money", span=3,
                note="Their fault, no claim raised")
    row += 1

    # ------------------------------------------------- what needs doing --
    row = s.section(row, "What needs doing", LAST_COL)
    row = s.note(
        row,
        "Every register has a 'What needs doing' column. This is all "
        "of them added up, by how loudly they are shouting. Work "
        "down from the left.",
        LAST_COL, height=30)
    row += 1
    s.kpi(row, 0, "Urgent", f"={_all_alerts('Urgent -')}", "int",
          note="Something is wrong, not just late")
    s.kpi(row, 2, "Overdue", f"={_all_alerts('Overdue -')}", "int",
          note="Past a date that mattered")
    s.kpi(row, 4, "To order",
          f"={_all_alerts('Order -')}+{_all_alerts('Due -')}", "int",
          note="Stock decisions waiting")
    s.kpi(row, 6, "To chase or send",
          f"={_all_alerts('Chase -')}+{_all_alerts('Send -')}+"
          f"{_all_alerts('Follow up -')}", "int",
          note="Somebody is waiting on you")
    s.kpi(row, 8, "To check or add",
          f"={_all_alerts('Check -')}+{_all_alerts('Add -')}+"
          f"{_all_alerts('Action -')}+{_all_alerts('Missing -')}+"
          f"{_all_alerts('Duplicate -')}", "int",
          note="Housekeeping and gaps")
    row = s.kpi(row, 10, "All clear",
                f"={_all_alerts('OK')}", "int", span=3,
                note="Rows with nothing outstanding")
    row += 1

    # --------------------------------------------- reorder list (left) --
    top = row
    row = s.subsection(row, "Buy these first", 5)
    s.table_head(row, 0, ["SKU", "Product", "Available", "Order",
                          "Value", "By"],
                 widths=[15, 24, 11, 9, 11, 11])
    row += 1
    reorder_first = row
    for n in range(1, ACTION_ROWS + 1):
        line = reorder_first + n - 1
        for col, field, style in ((0, "sku", "id"),
                                  (1, "product", "text"),
                                  (2, "available", "int"),
                                  (3, "order_rounded", "int"),
                                  (4, "order_value", "money"),
                                  (5, "order_by", "date")):
            s.formula(
                line, col,
                f'=IFERROR(INDEX([[Reorder Planner.{field}]],'
                f'MATCH({n},[[Reorder Planner.buy_rank]],0)),"")',
                fmts.calc(style))

    # ------------------------------------------- orders to pick (right) --
    right = top
    right = s.subsection(right, "Orders waiting to go", LAST_COL,
                         first_col=7)
    s.table_head(right, 7, ["Order", "Customer", "SKU", "Qty",
                            "Short", "Age"],
                 widths=[12, 20, 15, 8, 9, 8])
    right += 1
    for n in range(1, ACTION_ROWS + 1):
        line = right + n - 1
        for col, field, style in ((7, "order_id", "id"),
                                  (8, "customer_name", "text"),
                                  (9, "sku", "id"),
                                  (10, "qty", "int"),
                                  (11, "shortfall", "int"),
                                  (12, "age_days", "int")):
            s.formula(
                line, col,
                f'=IFERROR(INDEX([[Wholesale Orders.{field}]],'
                f'MATCH({n},[[Wholesale Orders.pick_rank]],0)),"")',
                fmts.calc(style))
    row = max(reorder_first + ACTION_ROWS, right + ACTION_ROWS) + 1

    # ------------------------------------------------- best and worst --
    top = row
    row = s.subsection(row, "Earning their shelf", 5)
    s.table_head(row, 0, ["SKU", "Product", "Units", "Profit",
                          "GP%", "Return"],
                 widths=[15, 24, 9, 11, 9, 10])
    row += 1
    best_first = row
    for n in range(1, LIST_ROWS + 1):
        line = best_first + n - 1
        for col, field, style in ((0, "sku", "id"),
                                  (1, "product", "text"),
                                  (2, "units_sold", "int"),
                                  (3, "profit", "money"),
                                  (4, "gp_pct", "percent0"),
                                  (5, "return_on_stock", "percent0")):
            s.formula(line, col,
                      f"={_by_rank('Product Performance', 'profit_rank', field, n)}",
                      fmts.calc(style))

    right = top
    right = s.subsection(right, "Not earning it", LAST_COL,
                         first_col=7)
    s.table_head(right, 7, ["SKU", "Product", "Stock value",
                            "Days since", "State"],
                 widths=[15, 22, 12, 11, 12])
    right += 1
    for n in range(1, LIST_ROWS + 1):
        line = right + n - 1
        for col, field, style in ((7, "sku", "id"),
                                  (8, "product", "text"),
                                  (9, "stock_value", "money"),
                                  (10, "days_since_sale", "int"),
                                  (11, "band", "status")):
            s.formula(
                line, col,
                f'=IFERROR(INDEX([[Product Performance.{field}]],'
                f'MATCH({n},[[Product Performance.dead_rank]],0)),"")',
                fmts.calc(style))
    row = max(best_first + LIST_ROWS, right + LIST_ROWS) + 1

    # ----------------------------------------------- customers & money --
    top = row
    row = s.subsection(row, "Your best stockists", 5)
    s.table_head(row, 0, ["Customer", "Revenue", "Profit", "GP%",
                          "Owing", "Last order"],
                 widths=[22, 12, 11, 8, 11, 12])
    row += 1
    cust_first = row
    for n in range(1, LIST_ROWS + 1):
        line = cust_first + n - 1
        for col, field, style in ((0, "business", "text"),
                                  (1, "revenue", "money"),
                                  (2, "profit", "money"),
                                  (3, "gp_pct", "percent0"),
                                  (4, "owing", "money"),
                                  (5, "last_order", "date")):
            s.formula(
                line, col,
                f"={_by_rank('Wholesale Customer CRM', 'revenue_rank', field, n)}",
                fmts.calc(style))

    right = top
    right = s.subsection(right, "Deliveries you are waiting for",
                         LAST_COL, first_col=7)
    s.table_head(right, 7, ["PO", "Supplier", "SKU", "Due", "Late",
                            "Value"],
                 widths=[12, 18, 15, 11, 8, 11])
    right += 1
    for n in range(1, LIST_ROWS + 1):
        line = right + n - 1
        for col, field, style in ((7, "po_id", "id"),
                                  (8, "supplier_name", "text"),
                                  (9, "sku", "id"),
                                  (10, "expected", "date"),
                                  (11, "days_late", "int"),
                                  (12, "outstanding_value", "money")):
            s.formula(
                line, col,
                f'=IFERROR(INDEX([[Purchase Orders.{field}]],'
                f'MATCH({n},[[Purchase Orders.chase_rank]],0)),"")',
                fmts.calc(style))
    row = max(cust_first + LIST_ROWS, right + LIST_ROWS) + 1

    # ---------------------------------------------------- recent months --
    row = s.section(row, "The last six months", LAST_COL)
    s.table_head(row, 0, ["Month", "Revenue", "COGS", "Gross profit",
                          "Expenses", "Net profit", "Margin",
                          "Stock bought", "Cash effect"],
                 widths=[12, 12, 11, 12, 11, 12, 9, 12, 12])
    row += 1
    for n in range(MONTHS - 1, -1, -1):
        key = _month_key(n)
        s.formula(row, 0, f'={key}', fmts.calc("text"))
        for col, field, style in (
                (1, "ProfitRevenue", "money"),
                (2, "ProfitCOGS", "money"),
                (3, "ProfitGross", "money"),
                (4, "ProfitExpenses", "money"),
                (5, "ProfitNet", "money"),
        ):
            s.formula(row, col,
                      f'=SUMIFS({field},ProfitMonths,{key})',
                      fmts.calc(style))
        s.formula(
            row, 6,
            f'=IFERROR(SUMIFS(ProfitGross,ProfitMonths,{key})/'
            f'SUMIFS(ProfitRevenue,ProfitMonths,{key}),"")',
            fmts.calc("percent0"))
        s.formula(row, 7,
                  f'=SUMIFS(ProfitStockSpend,ProfitMonths,{key})',
                  fmts.calc("money"))
        s.formula(row, 8,
                  f'=SUMIFS(ProfitCash,ProfitMonths,{key})',
                  fmts.calc("money"))
        s.cf(f"F{row + 1}:F{row + 1}",
             {"type": "cell", "criteria": "<", "value": 0,
              "fmt": "bad"})
        row += 1
    row += 1

    # ------------------------------------------------------------ notes --
    row = s.note(
        row,
        "Everything on this page is calculated from the registers. "
        "There is no refresh button because there is nothing to "
        "refresh - type a sale on the Retail Sales Tracker and the "
        "stock, the margin and the reorder suggestion have already "
        "changed by the time you look back here.",
        LAST_COL, height=44)
    row += 1
    row = s.note(
        row,
        "Reserved is not the same as sold. Units on a confirmed "
        "wholesale order are still on your shelf and still counted "
        "in stock at cost - they simply are not available to promise "
        "to anybody else. They leave stock when the order ships.",
        LAST_COL, height=44)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
