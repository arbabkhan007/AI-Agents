# Ultimate Inventory & Wholesale Order Manager

Created by **Novality Store**. The package contains two Excel workbooks, each with 23 sheets in the supplied order:

- **Demo** — fictional catalogue, customers, orders, sales and expenses for exploration.
- **Blank** — empty registers and blank business contact fields, with editable settings and reference lists.

The sheet-protection password is **`premium`**. Prepared input cells are unlocked and formulas are locked. Sheet protection is not encryption; store sensitive business and customer data securely and keep backups.

## Start here

1. Open the blank workbook in Microsoft Excel desktop, save your own working copy and allow formulas to recalculate. Review **Getting Started** and set the business details, reporting year, currency, fees, tax assumptions, tiers and lists in **Settings & Lists**.
2. Enter a unique SKU for each stocked variant in **Product & SKU Database**. Enter both opening quantity and its total opening cost. Add suppliers, wholesale customers and pricing as needed. Inventory Tracker mirrors the product rows and is calculated rather than typed.
3. Enter each purchase-order line once. Put the running cumulative received quantity on that line, not a new line per partial shipment. Enter expected dates and costs manually. Record sales and wholesale orders with the correct SKU and status. Confirmed wholesale orders reserve stock; shipped, delivered and returned orders reduce stock. For retail, shipped, delivered, collected and refunded statuses count as sales. Use **Cancelled** for an order or sale that never shipped.
4. Record customer returns using their source and condition, and log damage, losses, samples and manual corrections on **Stock Movement Log** without duplicating the same stock event. Supplier and courier cases require manual review and an appropriate stock adjustment. Review the notes below before entering returns.
5. For **Stock Audit**, copy the current system quantity into **System at count** as a manual snapshot, then enter the physical count. Post any approved variance once as a signed adjustment on Stock Movement Log and record its reference. The snapshot keeps the historical variance stable when stock later changes.
6. Review alerts and reconcile stock, receivables, costs and reports with your actual records. The workbook is a manual organizer: it does not sync with any marketplace, bank, shipping service or inventory system.

## Important operating limits

- **Keep keys and rows stable.** Do not sort, move, insert or delete populated register rows. Several generated IDs and mirrored sheets depend on row position. Use filters instead. Do not change ID prefixes or rename a SKU after references exist, and do not clear a referenced row's trigger field. Resolve duplicate SKU warnings immediately; duplicate SKUs make lookups ambiguous.
- Registers have fixed prepared ranges: 300 products, 900 movement rows, 60 suppliers, 500 purchase-order lines, 120 wholesale customers, 600 wholesale-order lines, 900 retail sales, 200 returns, 200 locations and 300 stock audits. Do not enter beyond prepared rows. The source generator's `--rows` option scales most register capacities for a new workbook; it does not extend an existing file.
- A PO/SKU combination should appear once. Only the first matching row counts toward received stock, value and open balance; all duplicates are flagged and must be corrected. This cannot detect the same physical delivery entered under different PO numbers. A partial receipt is a cumulative quantity; the single received date is not a dated history of each shipment.
- Customer sale returns: sellable units add back to inventory; unsellable units do not subtract again because they already left when sold. Unsellable **Own warehouse** returns reduce inventory. Other source types do not automatically change stock: review supplier and courier cases, then record a suitable adjustment once if needed. Only use refunded/returned statuses for previously fulfilled sales; record the return and refund separately. A replacement requires its own stock movement or sale.
- Bin quantities are manually maintained placement records, not the stock ledger. A stock audit's system quantity is a manually recorded snapshot, not an automatically captured history. Review and update both when operations change.
- The printable PO and invoice show at most **14 lines** each; the picking list shows at most **16**. Check for omitted lines and verify all totals and tax treatment before sending. These are templates, not compliant invoicing or legal advice.

## Costing, reports and reconciliation

The workbook uses a **current cumulative average**, `(opening value + accepted PO received value) / (opening units + accepted PO received units)`, with landed cost on purchase lines. It is not a dated perpetual moving-average ledger: later purchases and edits change the cost applied to earlier sales and reports. Opening value, price, fee, discount and other shared assumptions may also change historical results. Save period-end copies and reconcile with your accountant.

Management profit estimates use recorded sales, the current average cost, fees, operating expenses and an approximate returns adjustment. The adjustment includes refunds and postage less supplier credits, adds warehouse write-offs and credits cost for restocked customer returns; refunds do not automatically reduce every revenue or tax report. Sales, shipment, receipt, refund and expense dates can fall in different reporting periods. Do not duplicate a shipping cost, write-off or return across sheets. Inventory purchases are excluded from operating expenses to avoid double-counting COGS. The cash-effect figure is an estimate, not a bank balance. These are management tools, **not accounting, tax, legal or inventory compliance advice**.

## Generator and validation

The supplied source has been extracted and repaired. Python 3 and XlsxWriter are required; `openpyxl` and `formulas` are optional testing dependencies. In the extracted source folder:

```bash
python -m pip install xlsxwriter openpyxl formulas
python build_inventory_workbook.py --blank -o "Inventory Blank.xlsx"
python build_inventory_workbook.py -o "Inventory Demo.xlsx"
python build_inventory_workbook.py --help
python tools/check_parens.py "Inventory Blank.xlsx"
python tools/validate_inventory_workbook.py "Inventory Blank.xlsx"
python tools/test_stock_scenario.py
```

Both full-size files passed XML, formula-balance, Excel-2010-function, protection, prepared-cell and source-validator checks. Smaller demo and blank builds were calculated with an independent Python formula engine, and a targeted scenario checked duplicate PO handling, stock, reservations, returns, weighted cost, gaps and audit snapshots. Full-size files were not recalculated with that engine. XlsxWriter initially caches formula results as zero until a spreadsheet application recalculates them.

**Windows Excel opening, repair-free behavior and recalculation have not been verified in this environment.** Test a copy in your Excel version before relying on it. Other spreadsheet applications are unverified and may behave differently.
