"""Workbook level defined names.

Two families:

* **Dynamic** (OFFSET + COUNTIF) names back the drop downs, so a new
  client, service, product or supplier appears in every list the moment
  it is typed.
* **Static** full-column names back the aggregations (SUMIFS, COUNTIFS,
  SUMPRODUCT masks).  Whole-column ranges always agree in size, which is
  what keeps SUMIFS from ever returning #VALUE.

The static lists on `20 Settings & Lists` define their own names when
that tab is built.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .layout import Registry, dynamic_name

#: defined name -> (sheet, column key, dynamic?)
CROSS_SHEET_NAMES: Dict[str, Tuple[str, str, bool]] = {
    # drop down sources (dynamic)
    "ServiceNames": ("5 Services & Pricing", "name", True),
    "ProductNames": ("13 Product Inventory", "name", True),
    "StaffNames": ("8 Staff Management", "name", True),
    "ClientNames": ("4 Client CRM", "name", True),
    "SupplierNames": ("14 Suppliers & Purchases", "sup_name", True),

    # services
    "ServiceCat": ("5 Services & Pricing", "category", False),
    "ServicePrice": ("5 Services & Pricing", "price", False),
    "ServiceDur": ("5 Services & Pricing", "duration", False),
    "ServiceTaxable": ("5 Services & Pricing", "taxable", False),
    "RevenueAll": ("5 Services & Pricing", "revenue", False),
    "ServiceRank": ("5 Services & Pricing", "rank", False),
    "ServiceSold": ("5 Services & Pricing", "sold", False),

    # products
    "ProductRetail": ("13 Product Inventory", "retail", False),
    "ProductTaxable": ("13 Product Inventory", "taxable", False),
    "InvOnHand": ("13 Product Inventory", "on_hand", False),
    "InvLow": ("13 Product Inventory", "low", False),
    "InvValue": ("13 Product Inventory", "value", False),

    # staff
    "StaffMethod": ("8 Staff Management", "method", False),
    "StaffSvcRate": ("8 Staff Management", "svc_rate", False),
    "StaffRetRate": ("8 Staff Management", "retail_rate", False),
    "StaffHourly": ("8 Staff Management", "hourly", False),
    "StaffRevenue": ("8 Staff Management", "revenue", False),

    # clients
    "ClientVisits": ("4 Client CRM", "visits", False),
    "ClientReferrals": ("4 Client CRM", "referrals", False),
    "ClientSource": ("4 Client CRM", "source", False),
    "ClientStatus": ("4 Client CRM", "status", False),
    "ClientLast": ("4 Client CRM", "last", False),
    "ClientFirst": ("4 Client CRM", "first", False),

    # appointments
    "ApptIds": ("3 Appointment Planner", "id", False),
    "ApptDates": ("3 Appointment Planner", "date", False),
    "ApptClients": ("3 Appointment Planner", "client", False),
    "ApptStaff": ("3 Appointment Planner", "staff", False),
    "ApptService": ("3 Appointment Planner", "service", False),
    "ApptStatus": ("3 Appointment Planner", "status", False),
    "ApptDone": ("3 Appointment Planner", "done", False),
    "ApptKeys": ("3 Appointment Planner", "key", False),
    "ApptDeposit": ("3 Appointment Planner", "deposit", False),
    "ApptFollow": ("3 Appointment Planner", "followup", False),

    # sales
    "SalesDates": ("6 Sales & Transactions", "date", False),
    "SalesClients": ("6 Sales & Transactions", "client", False),
    "SalesStaff": ("6 Sales & Transactions", "staff", False),
    "SalesType": ("6 Sales & Transactions", "type", False),
    "SalesItem": ("6 Sales & Transactions", "item", False),
    "SalesQty": ("6 Sales & Transactions", "qty", False),
    "SalesNet": ("6 Sales & Transactions", "net", False),
    "SalesDisc": ("6 Sales & Transactions", "discount", False),
    "SalesRefund": ("6 Sales & Transactions", "refund", False),
    "SalesTax": ("6 Sales & Transactions", "tax", False),
    "SalesBalance": ("6 Sales & Transactions", "balance", False),
    "SalesFee": ("6 Sales & Transactions", "fee", False),
    "SalesCat": ("6 Sales & Transactions", "cat", False),
    "SalesRate": ("6 Sales & Transactions", "rate", False),

    # payments
    "PayDates": ("7 Payments & Deposits", "date", False),
    "PayKind": ("7 Payments & Deposits", "kind", False),
    "PayAmount": ("7 Payments & Deposits", "amount", False),
    "PayLinkStatus": ("7 Payments & Deposits", "link_status", False),

    # purchases / inventory flow
    "PurchDates": ("14 Suppliers & Purchases", "date", False),
    "PurchProduct": ("14 Suppliers & Purchases", "product", False),
    "PurchQty": ("14 Suppliers & Purchases", "qty", False),
    "PurchStatus": ("14 Suppliers & Purchases", "status", False),
    "PurchTotal": ("14 Suppliers & Purchases", "total", False),

    # expenses
    "ExpDates": ("11 Expenses", "date", False),
    "ExpCat": ("11 Expenses", "category", False),
    "ExpAmount": ("11 Expenses", "amount", False),

    # payroll
    "PayrollDates": ("10 Payroll & Tips", "date", False),
    "PayrollStaff": ("10 Payroll & Tips", "staff", False),
    "PayrollHours": ("10 Payroll & Tips", "hours", False),
    "PayrollCost": ("10 Payroll & Tips", "total_cost", False),
    "PayrollTipsIn": ("10 Payroll & Tips", "tips_in", False),
}


def define_cross_sheet_names(book, reg: Registry) -> None:
    """Create every lookup name. Call after all registers are built."""
    for name, (sheet, key, dynamic) in CROSS_SHEET_NAMES.items():
        if sheet not in reg:
            continue
        spec = reg[sheet]
        if key not in [c.key for c in spec.columns]:
            continue
        if dynamic:
            book.define_name(
                name,
                dynamic_name(sheet, spec.letter(key), spec.first_data_row,
                             spec.last_data_row))
        else:
            book.define_name(name, reg.rng(sheet, key))
