"""Workbook level defined names that point at the register sheets.

The fixed drop-downs - categories, payment terms, movement types,
expense categories - define their own names on `Settings & Lists`.
The names here are the ones that have to follow live data: the SKUs
you actually stock, the suppliers you actually buy from, the stockists
who actually order. Each is a fixed prepared range; blank gaps do not
truncate the data and parallel lookup columns stay aligned.

`SKUList` is the important one.  It is the SKU column from the Product
& SKU Database, it feeds the drop-down on nine other tabs, and every
join in this workbook runs through it.  Get a SKU wrong and the row is
orphaned; that is why the SKU cell is a list rather than free text
everywhere except the one sheet where SKUs are created.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str]] = {
    # ---- the three join keys ------------------------------------------
    "SKUList": ("Product & SKU Database", "sku"),
    "SupplierList": ("Supplier Database", "id"),
    "CustomerList": ("Wholesale Customer CRM", "id"),

    # ---- product columns the lookups read ------------------------------
    "ProductNames": ("Product & SKU Database", "name"),
    "ProductCategoryCol": ("Product & SKU Database", "category"),
    "ProductCostCol": ("Product & SKU Database", "cost"),
    "ProductRetailCol": ("Product & SKU Database", "retail_price"),
    "ProductWholesaleCol": ("Product & SKU Database",
                            "wholesale_price"),
    "ProductFloorCol": ("Product & SKU Database", "min_price"),
    "ProductOpeningQty": ("Product & SKU Database", "opening_qty"),
    "ProductOpeningValue": ("Product & SKU Database",
                            "opening_value"),
    "ProductStatusCol": ("Product & SKU Database", "status"),
    "ProductSupplierCol": ("Product & SKU Database", "supplier"),
    "ProductMinStock": ("Product & SKU Database", "min_stock"),
    "ProductMaxStock": ("Product & SKU Database", "max_stock"),
    "ProductActive": ("Product & SKU Database", "is_active"),
    "ProductDupCount": ("Product & SKU Database", "dup_count"),
    "ProductAlert": ("Product & SKU Database", "alert"),

    # ---- the stock position - the busiest ranges in the workbook -------
    "StockSKU": ("Inventory Tracker", "sku"),
    "StockProduct": ("Inventory Tracker", "product"),
    "StockCategory": ("Inventory Tracker", "category"),
    "StockCurrent": ("Inventory Tracker", "current"),
    "StockReserved": ("Inventory Tracker", "reserved"),
    "StockAvailable": ("Inventory Tracker", "available"),
    "StockOnOrder": ("Inventory Tracker", "on_order"),
    "StockAvgCost": ("Inventory Tracker", "avg_cost"),
    "StockValueCol": ("Inventory Tracker", "stock_value"),
    "StockRetailValue": ("Inventory Tracker", "retail_value"),
    "StockDailySales": ("Inventory Tracker", "daily_sales"),
    "StockDaysCover": ("Inventory Tracker", "days_cover"),
    "StockState": ("Inventory Tracker", "stock_state"),
    "StockIsOut": ("Inventory Tracker", "is_out"),
    "StockIsLow": ("Inventory Tracker", "is_low"),
    "StockIsOver": ("Inventory Tracker", "is_over"),
    "StockIsDead": ("Inventory Tracker", "is_dead"),
    "StockAlert": ("Inventory Tracker", "alert"),

    # ---- movements -----------------------------------------------------
    "MovementSKU": ("Stock Movement Log", "sku"),
    "MovementDates": ("Stock Movement Log", "date_num"),
    "MovementMonths": ("Stock Movement Log", "month"),
    "MovementTypeCol": ("Stock Movement Log", "type"),
    "MovementQty": ("Stock Movement Log", "signed_qty"),
    "MovementValue": ("Stock Movement Log", "value"),
    "MovementDamaged": ("Stock Movement Log", "damaged"),
    "MovementAdjustment": ("Stock Movement Log", "adjustment"),
    "MovementIsWriteoff": ("Stock Movement Log", "is_writeoff"),
    "MovementIsManual": ("Stock Movement Log", "is_manual"),
    "MovementAlert": ("Stock Movement Log", "alert"),

    # ---- suppliers -----------------------------------------------------
    "SupplierNames": ("Supplier Database", "name"),
    "SupplierLeadTime": ("Supplier Database", "lead_time"),
    "SupplierActualLead": ("Supplier Database", "actual_lead"),
    "SupplierLeadGap": ("Supplier Database", "lead_gap"),
    "SupplierSpend": ("Supplier Database", "spend"),
    "SupplierOpenValue": ("Supplier Database", "open_value"),
    "SupplierOnTime": ("Supplier Database", "on_time_rate"),
    "SupplierStatusCol": ("Supplier Database", "status"),
    "SupplierRating": ("Supplier Database", "rating"),
    "SupplierAlert": ("Supplier Database", "alert"),

    # ---- purchase orders -----------------------------------------------
    "POId": ("Purchase Orders", "po_id"),
    "POSupplier": ("Purchase Orders", "supplier"),
    "POSKU": ("Purchase Orders", "sku"),
    "PODates": ("Purchase Orders", "order_num"),
    "POReceivedDates": ("Purchase Orders", "received_num"),
    "POMonths": ("Purchase Orders", "month"),
    "POQty": ("Purchase Orders", "qty"),
    "POReceived": ("Purchase Orders", "received"),
    "POReceivedValue": ("Purchase Orders", "received_value"),
    "POTotal": ("Purchase Orders", "total"),
    "POOutstanding": ("Purchase Orders", "outstanding"),
    "POOutstandingValue": ("Purchase Orders", "outstanding_value"),
    "POStatusCol": ("Purchase Orders", "status"),
    "POIsOpen": ("Purchase Orders", "is_open"),
    "POIsLate": ("Purchase Orders", "is_late"),
    "POIsOver": ("Purchase Orders", "is_over"),
    "PODupLine": ("Purchase Orders", "dup_line"),
    "PODaysLate": ("Purchase Orders", "days_late"),
    "POPaid": ("Purchase Orders", "paid"),
    "POExpected": ("Purchase Orders", "expected"),
    "POAlert": ("Purchase Orders", "alert"),

    # ---- wholesale customers -------------------------------------------
    "CustomerNames": ("Wholesale Customer CRM", "business"),
    "CustomerTierCol": ("Wholesale Customer CRM", "tier"),
    "CustomerTermsCol": ("Wholesale Customer CRM", "terms"),
    "CustomerDiscount": ("Wholesale Customer CRM", "discount"),
    "CustomerMinOrder": ("Wholesale Customer CRM", "min_order"),
    "CustomerCreditLimit": ("Wholesale Customer CRM",
                            "credit_limit"),
    "CustomerRevenue": ("Wholesale Customer CRM", "revenue"),
    "CustomerProfit": ("Wholesale Customer CRM", "profit"),
    "CustomerOwing": ("Wholesale Customer CRM", "owing"),
    "CustomerOverdue": ("Wholesale Customer CRM", "overdue"),
    "CustomerOrders": ("Wholesale Customer CRM", "orders"),
    "CustomerDaysSince": ("Wholesale Customer CRM", "days_since"),
    "CustomerStatusCol": ("Wholesale Customer CRM", "status"),
    "CustomerRank": ("Wholesale Customer CRM", "revenue_rank"),
    "CustomerAlert": ("Wholesale Customer CRM", "alert"),

    # ---- pricing --------------------------------------------------------
    "PricingSKU": ("Wholesale Pricing", "sku"),
    "PricingBase": ("Wholesale Pricing", "wholesale"),
    "PricingBest": ("Wholesale Pricing", "best_price"),
    "PricingBestGP": ("Wholesale Pricing", "best_gp"),
    "PricingBelowFloor": ("Wholesale Pricing", "below_floor"),
    "PricingThin": ("Wholesale Pricing", "thin_margin"),
    "PricingIsPriced": ("Wholesale Pricing", "is_priced"),
    "PricingCaseQty": ("Wholesale Pricing", "case_qty"),
    "PricingAlert": ("Wholesale Pricing", "alert"),

    # ---- wholesale orders ------------------------------------------------
    "OrderId": ("Wholesale Orders", "order_id"),
    "OrderCustomer": ("Wholesale Orders", "customer"),
    "OrderSKU": ("Wholesale Orders", "sku"),
    "OrderDates": ("Wholesale Orders", "date_num"),
    "OrderShipDates": ("Wholesale Orders", "ship_num"),
    "OrderMonths": ("Wholesale Orders", "month"),
    "OrderQty": ("Wholesale Orders", "qty"),
    "OrderTotal": ("Wholesale Orders", "line_total"),
    "OrderCost": ("Wholesale Orders", "line_cost"),
    "OrderProfit": ("Wholesale Orders", "line_profit"),
    "OrderStatusCol": ("Wholesale Orders", "status"),
    "OrderIsReserved": ("Wholesale Orders", "is_reserved"),
    "OrderIsShipped": ("Wholesale Orders", "is_shipped"),
    "OrderIsOpen": ("Wholesale Orders", "is_open"),
    "OrderIsOverdue": ("Wholesale Orders", "is_overdue"),
    "OrderFirstLine": ("Wholesale Orders", "is_first_line"),
    "OrderOutstanding": ("Wholesale Orders", "outstanding"),
    "OrderShortfall": ("Wholesale Orders", "shortfall"),
    "OrderAge": ("Wholesale Orders", "age_days"),
    "OrderDaysToShip": ("Wholesale Orders", "days_to_ship"),
    "OrderAlert": ("Wholesale Orders", "alert"),

    # ---- retail sales -----------------------------------------------------
    "SaleId": ("Retail Sales Tracker", "sale_id"),
    "SaleSKU": ("Retail Sales Tracker", "sku"),
    "SaleDates": ("Retail Sales Tracker", "date_num"),
    "SaleMonths": ("Retail Sales Tracker", "month"),
    "SaleWeekdays": ("Retail Sales Tracker", "weekday"),
    "SaleChannel": ("Retail Sales Tracker", "channel"),
    "SaleQty": ("Retail Sales Tracker", "qty"),
    "SaleGross": ("Retail Sales Tracker", "gross"),
    "SaleNet": ("Retail Sales Tracker", "net_revenue"),
    "SaleFees": ("Retail Sales Tracker", "platform_fee"),
    "SalePaymentFees": ("Retail Sales Tracker", "payment_fee"),
    "SaleCOGS": ("Retail Sales Tracker", "cogs"),
    "SaleProfit": ("Retail Sales Tracker", "profit"),
    "SaleIsSold": ("Retail Sales Tracker", "is_sold"),
    "SaleIsLoss": ("Retail Sales Tracker", "is_loss"),
    "SaleShipCharged": ("Retail Sales Tracker", "shipping_charged"),
    "SaleShipCost": ("Retail Sales Tracker", "shipping_cost"),
    "SaleAlert": ("Retail Sales Tracker", "alert"),

    # ---- reorder planning ---------------------------------------------------
    "ReorderSKU": ("Reorder Planner", "sku"),
    "ReorderSupplier": ("Reorder Planner", "supplier"),
    "ReorderQty": ("Reorder Planner", "order_rounded"),
    "ReorderValue": ("Reorder Planner", "order_value"),
    "ReorderUrgency": ("Reorder Planner", "urgency"),
    "ReorderPriority": ("Reorder Planner", "priority"),
    "ReorderNeeded": ("Reorder Planner", "needs_order"),
    "ReorderBy": ("Reorder Planner", "order_by"),
    "ReorderPoint": ("Reorder Planner", "reorder_point"),
    "ReorderAlert": ("Reorder Planner", "alert"),

    # ---- valuation ----------------------------------------------------------
    "ValuationSKU": ("Inventory Valuation & COGS", "sku"),
    "ValuationAvgCost": ("Inventory Valuation & COGS", "avg_cost"),
    "ValuationStockValue": ("Inventory Valuation & COGS",
                            "stock_value"),
    "ValuationCOGS": ("Inventory Valuation & COGS", "cogs"),
    "ValuationRevenue": ("Inventory Valuation & COGS", "revenue"),
    "ValuationProfit": ("Inventory Valuation & COGS",
                        "gross_profit"),
    "ValuationWriteoff": ("Inventory Valuation & COGS",
                          "writeoff_value"),
    "ValuationTurns": ("Inventory Valuation & COGS", "turns"),
    "ValuationABC": ("Inventory Valuation & COGS", "abc_class"),
    "ValuationDead": ("Inventory Valuation & COGS", "dead_value"),
    "ValuationAlert": ("Inventory Valuation & COGS", "alert"),

    # ---- returns -------------------------------------------------------------
    "ReturnSKU": ("Returns & Damaged Goods", "sku"),
    "ReturnDates": ("Returns & Damaged Goods", "date_num"),
    "ReturnMonths": ("Returns & Damaged Goods", "month"),
    "ReturnQty": ("Returns & Damaged Goods", "qty"),
    "ReturnReasonCol": ("Returns & Damaged Goods", "reason"),
    "ReturnRestocked": ("Returns & Damaged Goods", "restocked"),
    "ReturnLoss": ("Returns & Damaged Goods", "profit_effect"),
    "ReturnTotalCost": ("Returns & Damaged Goods", "total_cost"),
    "ReturnUnclaimed": ("Returns & Damaged Goods", "unclaimed"),
    "ReturnIsWriteoff": ("Returns & Damaged Goods", "is_writeoff"),
    "ReturnIsOpen": ("Returns & Damaged Goods", "is_open"),
    "ReturnAlert": ("Returns & Damaged Goods", "alert"),

    # ---- locations -----------------------------------------------------------
    "LocationSKU": ("Warehouse Locations", "sku"),
    "LocationCol": ("Warehouse Locations", "location"),
    "LocationQty": ("Warehouse Locations", "qty_here"),
    "LocationGap": ("Warehouse Locations", "placed_gap"),
    "LocationAlert": ("Warehouse Locations", "alert"),

    # ---- audit ----------------------------------------------------------------
    "AuditSKU": ("Stock Audit", "sku"),
    "AuditDates": ("Stock Audit", "date_num"),
    "AuditVariance": ("Stock Audit", "variance"),
    "AuditVarianceValue": ("Stock Audit", "variance_value"),
    "AuditAbsValue": ("Stock Audit", "abs_value"),
    "AuditHasVariance": ("Stock Audit", "has_variance"),
    "AuditUnposted": ("Stock Audit", "unposted"),
    "AuditAccuracy": ("Stock Audit", "accuracy"),
    "AuditAlert": ("Stock Audit", "alert"),

    # ---- performance ------------------------------------------------------------
    "PerfSKU": ("Product Performance", "sku"),
    "PerfProduct": ("Product Performance", "product"),
    "PerfCategory": ("Product Performance", "category"),
    "PerfUnits": ("Product Performance", "units_sold"),
    "PerfRevenue": ("Product Performance", "revenue"),
    "PerfProfit": ("Product Performance", "profit"),
    "PerfGP": ("Product Performance", "gp_pct"),
    "PerfPerUnit": ("Product Performance", "profit_per_unit"),
    "PerfReturnOnStock": ("Product Performance", "return_on_stock"),
    "PerfStockValue": ("Product Performance", "stock_value"),
    "PerfBand": ("Product Performance", "band"),
    "PerfIsDead": ("Product Performance", "is_dead"),
    "PerfIsStar": ("Product Performance", "is_star"),
    "PerfRevenueRank": ("Product Performance", "revenue_rank"),
    "PerfProfitRank": ("Product Performance", "profit_rank"),
    "PerfDaysSince": ("Product Performance", "days_since_sale"),
    "PerfAlert": ("Product Performance", "alert"),

    # ---- expenses -----------------------------------------------------------------
    "ExpenseDates": ("Expense Tracker", "date_num"),
    "ExpenseMonths": ("Expense Tracker", "month"),
    "ExpenseCategoryCol": ("Expense Tracker", "category"),
    "ExpenseAmount": ("Expense Tracker", "amount"),
    "ExpenseOperating": ("Expense Tracker", "operating"),
    "ExpenseInventory": ("Expense Tracker", "inventory_spend"),
    "ExpenseMonthly": ("Expense Tracker", "monthly"),
    "ExpenseReceipt": ("Expense Tracker", "receipt"),
    "ExpenseDuplicate": ("Expense Tracker", "duplicate"),
    "ExpenseAlert": ("Expense Tracker", "alert"),

    # ---- monthly profit --------------------------------------------------------------
    "ProfitMonths": ("Profit Analysis", "month"),
    "ProfitRevenue": ("Profit Analysis", "revenue"),
    "ProfitCOGS": ("Profit Analysis", "cogs"),
    "ProfitGross": ("Profit Analysis", "gross_profit"),
    "ProfitExpenses": ("Profit Analysis", "expenses"),
    "ProfitNet": ("Profit Analysis", "net_profit"),
    "ProfitMargin": ("Profit Analysis", "net_margin"),
    "ProfitStockSpend": ("Profit Analysis", "stock_spend"),
    "ProfitCash": ("Profit Analysis", "cash_effect"),
    "ProfitRetail": ("Profit Analysis", "retail_revenue"),
    "ProfitWholesale": ("Profit Analysis", "wholesale_revenue"),
    "ProfitAlert": ("Profit Analysis", "alert"),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create the live lookup names. Call after every register is built."""
    missing = []
    for name, (sheet, key) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            missing.append(f"{name}: no sheet {sheet!r}")
            continue
        spec = reg[sheet]
        if not any(c.key == key for c in spec.columns):
            missing.append(f"{name}: {sheet!r} has no column {key!r}")
            continue
        book.define_name(
            name,
            dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                         spec.last_data_row))
    if missing:
        raise KeyError("defined names point at nothing: "
                       + "; ".join(missing))
