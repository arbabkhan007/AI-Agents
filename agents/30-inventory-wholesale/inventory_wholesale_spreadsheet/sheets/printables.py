"""`Printable Orders & Invoices` - three documents, ready to send.

Type an ID at the top of each block and the document fills itself in:
a purchase order to send a supplier, a wholesale invoice to send a
customer, and a picking list for whoever is packing the boxes.

Each one gathers every line that shares the ID you typed, which is
why purchase order and order lines repeat their reference across
rows. Nothing here is typed twice.

Set your print area to the block you want and it comes out on one
page.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Printable Orders & Invoices"
LAST_COL = 8
PO_LINES = 14
INV_LINES = 14
PICK_LINES = 16


def _line(sheet: str, key_name: str, id_cell: str, field: str,
          n: int) -> str:
    """The nth line of whichever document the user asked for.

    Walks the register looking for the nth row whose ID matches, by
    counting matches as it goes - no array formula, no helper tab.
    """
    return (f'IFERROR(IF({id_cell}="","",'
            f'INDEX([[{sheet}.{field}]],'
            f'MATCH({n},[[{sheet}.{key_name}]],0))),"")')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.accent)

    s.banner("Printable Orders & Invoices",
             "Type an ID, print the document. Everything else is "
             "filled in for you.", LAST_COL)
    s.set_col(0, 0, 22)
    s.set_col(1, 1, 30)
    for column in range(2, LAST_COL + 1):
        s.set_col(column, column, 15)

    row = 4
    row = s.note(
        row,
        "Three documents, one below the other. Each needs one thing "
        "from you: the PO number, the order ID or the order ID "
        "again. Every line that shares that reference is gathered "
        "automatically, so a six-line order prints as six lines.",
        LAST_COL, height=36)
    row += 1

    # =====================================================================
    # 1. PURCHASE ORDER
    # =====================================================================
    row = s.section(row, "Purchase order - to send to a supplier",
                    LAST_COL)
    s.merge(row, 0, 0, "PO number", fmts.chrome("label_bold"))
    s.write(row, 1, None, fmts.input("id"))
    po_cell = f"$B${row + 1}"
    book.define_name("PrintPO", f"='{NAME}'!{po_cell}")
    s.merge(row, 2, LAST_COL,
            "Type a PO number from the Purchase Orders tab",
            fmts.chrome("note"))
    row += 2

    s.merge(row, 0, 1, None, fmts.chrome("print_title"))
    s.formula(row, 0, '="PURCHASE ORDER"', fmts.chrome("print_title"))
    s.merge(row, 2, 4, None, fmts.calc("text"))
    s.formula(row, 2, f'=IF({po_cell}="","",{po_cell})',
              fmts.calc("id"))
    s.merge(row, 5, 6, "Date", fmts.chrome("label_right"))
    s.formula(
        row, 7,
        f'={_line("Purchase Orders", "po_print_rank", po_cell, "order_date", 1)}',
        fmts.calc("date"))
    row += 1

    s.merge(row, 0, 1, None, fmts.chrome("print_sub"))
    s.formula(row, 0, "=BusinessName", fmts.chrome("print_sub"))
    s.merge(row, 2, 4, "To", fmts.chrome("label_bold"))
    s.merge(row, 5, LAST_COL, None, fmts.calc("text"))
    s.formula(
        row, 5,
        f'={_line("Purchase Orders", "po_print_rank", po_cell, "supplier_name", 1)}',
        fmts.calc("text"))
    row += 1

    for label, field in (("Expected delivery", "expected"),
                         ("Supplier reference", "supplier")):
        s.merge(row, 0, 1, label, fmts.chrome("label_bold"))
        style = "date" if field == "expected" else "id"
        s.formula(
            row, 2,
            f'={_line("Purchase Orders", "po_print_rank", po_cell, field, 1)}',
            fmts.calc(style))
        row += 1
    row += 1

    s.table_head(row, 0, ["SKU", "Product", "Their code", "Qty",
                          "Unit cost", "Discount", "Freight",
                          "Line total"],
                 widths=[16, 30, 15, 10, 13, 11, 11, 14])
    row += 1
    for n in range(1, PO_LINES + 1):
        for col, field, style in ((0, "sku", "id"),
                                  (1, "product", "text"),
                                  (2, "supplier_sku", "text"),
                                  (3, "qty", "int"),
                                  (4, "unit_cost", "money"),
                                  (5, "discount", "percent0"),
                                  (6, "freight", "money"),
                                  (7, "total", "money")):
            s.formula(
                row, col,
                f'={_line("Purchase Orders", "po_print_rank", po_cell, field, n)}',
                fmts.calc(style))
        row += 1
    s.merge(row, 0, 6, "Order total", fmts.chrome("total_label"))
    s.formula(row, 7,
              f'=IF({po_cell}="","",SUMIF(POId,{po_cell},POTotal))',
              fmts.chrome("total_value",
                          num_format=cfg.money_format))
    row += 1
    s.merge(row, 0, 6, "Already received", fmts.chrome("label_right"))
    s.formula(
        row, 7,
        f'=IF({po_cell}="","",SUMIF(POId,{po_cell},POReceivedValue))',
        fmts.calc("money"))
    row += 1
    s.merge(row, 0, 6, "Still outstanding", fmts.chrome("label_right"))
    s.formula(
        row, 7,
        f'=IF({po_cell}="","",SUMIF(POId,{po_cell},'
        f'POOutstandingValue))', fmts.calc("money"))
    row += 2

    s.merge(row, 0, LAST_COL,
            "Please confirm receipt of this order and advise if any "
            "line cannot be supplied in full.", fmts.chrome("note"))
    row += 2

    # =====================================================================
    # 2. WHOLESALE INVOICE
    # =====================================================================
    row = s.section(row, "Wholesale invoice - to send to a customer",
                    LAST_COL)
    s.merge(row, 0, 0, "Order ID", fmts.chrome("label_bold"))
    s.write(row, 1, None, fmts.input("id"))
    ord_cell = f"$B${row + 1}"
    book.define_name("PrintOrder", f"='{NAME}'!{ord_cell}")
    s.merge(row, 2, LAST_COL,
            "Type an Order ID from the Wholesale Orders tab",
            fmts.chrome("note"))
    row += 2

    s.merge(row, 0, 1, None, fmts.chrome("print_title"))
    s.formula(row, 0, '="INVOICE"', fmts.chrome("print_title"))
    s.merge(row, 2, 4, None, fmts.calc("text"))
    s.formula(
        row, 2,
        f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "invoice_no", 1)}',
        fmts.calc("id"))
    s.merge(row, 5, 6, "Invoice date", fmts.chrome("label_right"))
    s.formula(
        row, 7,
        f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "ship_date", 1)}',
        fmts.calc("date"))
    row += 1

    s.merge(row, 0, 1, None, fmts.chrome("print_sub"))
    s.formula(row, 0, "=BusinessName", fmts.chrome("print_sub"))
    s.merge(row, 2, 4, "Bill to", fmts.chrome("label_bold"))
    s.merge(row, 5, LAST_COL, None, fmts.calc("text"))
    s.formula(
        row, 5,
        f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "customer_name", 1)}',
        fmts.calc("text"))
    row += 1

    s.merge(row, 0, 1, "Order reference", fmts.chrome("label_bold"))
    s.formula(row, 2, f'=IF({ord_cell}="","",{ord_cell})',
              fmts.calc("id"))
    s.merge(row, 3, 4, "Their PO", fmts.chrome("label_right"))
    s.formula(
        row, 5,
        f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "po_ref", 1)}',
        fmts.calc("text"))
    s.merge(row, 6, 6, "Due", fmts.chrome("label_right"))
    s.formula(
        row, 7,
        f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "due_date", 1)}',
        fmts.calc("date"))
    row += 2

    s.table_head(row, 0, ["SKU", "Product", "Qty", "Unit price",
                          "Discount", "Line total"],
                 widths=[16, 34, 10, 14, 12, 15])
    row += 1
    for n in range(1, INV_LINES + 1):
        for col, field, style in ((0, "sku", "id"),
                                  (1, "product", "text"),
                                  (2, "qty", "int"),
                                  (3, "unit_price", "money"),
                                  (4, "line_discount", "percent0"),
                                  (5, "line_total", "money")):
            s.formula(
                row, col,
                f'={_line("Wholesale Orders", "order_print_rank", ord_cell, field, n)}',
                fmts.calc(style))
        row += 1

    goods = f'SUMIF(OrderId,{ord_cell},OrderTotal)'
    s.merge(row, 0, 4, "Goods total", fmts.chrome("label_right"))
    s.formula(row, 5, f'=IF({ord_cell}="","",{goods})',
              fmts.calc("money"))
    row += 1
    s.merge(row, 0, 4, "Shipping", fmts.chrome("label_right"))
    s.formula(
        row, 5,
        f'=IF({ord_cell}="","",SUMIF(OrderId,{ord_cell},'
        f'[[Wholesale Orders.shipping_charge]]))', fmts.calc("money"))
    ship_row = row
    row += 1
    s.merge(row, 0, 4, None, fmts.chrome("label_right"))
    s.formula(row, 0, '=TaxName&IF(TaxOnSales="Yes"," at "&'
                      'TEXT(TaxRate,"0%")," - not charged")',
              fmts.chrome("label_right"))
    s.formula(
        row, 5,
        f'=IF({ord_cell}="","",IF(TaxOnSales<>"Yes",0,'
        f'ROUND(({goods}+$F${ship_row + 1})*TaxRate,2)))',
        fmts.calc("money"))
    tax_row = row
    row += 1
    s.merge(row, 0, 4, "TOTAL DUE", fmts.chrome("total_label"))
    s.formula(
        row, 5,
        f'=IF({ord_cell}="","",{goods}+$F${ship_row + 1}+'
        f'$F${tax_row + 1})',
        fmts.chrome("total_value", num_format=cfg.money_format))
    row += 1
    s.merge(row, 0, 4, "Already paid", fmts.chrome("label_right"))
    s.formula(
        row, 5,
        f'=IF({ord_cell}="","",SUMIF(OrderId,{ord_cell},'
        f'[[Wholesale Orders.paid_amount]]))', fmts.calc("money"))
    row += 1
    s.merge(row, 0, 4, "Outstanding", fmts.chrome("label_right"))
    s.formula(
        row, 5,
        f'=IF({ord_cell}="","",SUMIF(OrderId,{ord_cell},'
        f'OrderOutstanding))', fmts.calc("money"))
    row += 2
    s.merge(row, 0, LAST_COL, None, fmts.chrome("note"))
    s.formula(
        row, 0,
        '="Payment terms: "&IFERROR(INDEX(CustomerTermsCol,'
        'MATCH(IFERROR(INDEX(OrderCustomer,MATCH(PrintOrder,'
        'OrderId,0)),""),CustomerList,0)),"as agreed")&'
        '". Please quote the order reference when paying."',
        fmts.chrome("note"))
    row += 2

    # =====================================================================
    # 3. PICKING LIST
    # =====================================================================
    row = s.section(row, "Picking list - for whoever packs the box",
                    LAST_COL)
    row = s.note(
        row,
        "Same order ID as the invoice above. This one shows where "
        "each item is stored and whether there is enough on the "
        "shelf to pick it, which is the only question the packer "
        "actually has.",
        LAST_COL, height=32)
    row += 1

    s.merge(row, 0, 1, None, fmts.chrome("print_title"))
    s.formula(row, 0, '="PICKING LIST"', fmts.chrome("print_title"))
    s.merge(row, 2, 4, None, fmts.calc("text"))
    s.formula(row, 2, f'=IF({ord_cell}="","",{ord_cell})',
              fmts.calc("id"))
    s.merge(row, 5, 6, "Customer", fmts.chrome("label_right"))
    s.formula(
        row, 7,
        f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "customer_name", 1)}',
        fmts.calc("text"))
    row += 2

    s.table_head(row, 0, ["SKU", "Product", "Location", "Qty to "
                          "pick", "Available", "Enough?", "Picked"],
                 widths=[16, 30, 14, 12, 12, 12, 10])
    row += 1
    for n in range(1, PICK_LINES + 1):
        sku = _line("Wholesale Orders", "order_print_rank", ord_cell,
                    "sku", n)
        s.formula(row, 0, f'={sku}', fmts.calc("id"))
        s.formula(
            row, 1,
            f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "product", n)}',
            fmts.calc("text"))
        s.formula(
            row, 2,
            f'=IFERROR(IF({sku}="","",INDEX(LocationCol,'
            f'MATCH({sku},LocationSKU,0))&""),"")',
            fmts.calc("text"))
        s.formula(
            row, 3,
            f'={_line("Wholesale Orders", "order_print_rank", ord_cell, "qty", n)}',
            fmts.calc("int"))
        s.formula(
            row, 4,
            f'=IFERROR(IF({sku}="","",INDEX(StockCurrent,'
            f'MATCH({sku},StockSKU,0))),"")', fmts.calc("int"))
        s.formula(
            row, 5,
            f'=IF({sku}="","",IF(IFERROR(INDEX(StockCurrent,'
            f'MATCH({sku},StockSKU,0)),0)>='
            f'IFERROR(INDEX([[Wholesale Orders.qty]],'
            f'MATCH({n},[[Wholesale Orders.order_print_rank]],0)),0),'
            f'"Yes","SHORT"))', fmts.calc("status"))
        s.write(row, 6, None, fmts.chrome("form_box"))
        s.cf(f"F{row + 1}:F{row + 1}",
             {"type": "text", "criteria": "containing",
              "value": "SHORT", "fmt": "bad"})
        row += 1
    row += 1
    s.merge(row, 0, 2, "Picked by", fmts.chrome("label_bold"))
    s.merge(row, 3, 5, None, fmts.chrome("form_line"))
    s.merge(row, 6, 6, "Date", fmts.chrome("label_right"))
    s.merge(row, 7, LAST_COL, None, fmts.chrome("form_line"))
    row += 2

    row = s.note(
        row,
        "Available on the picking list is the physical stock, not "
        "the available-to-sell figure - the packer wants to know "
        "whether the units are on the shelf, including the ones "
        "this very order has reserved.",
        LAST_COL, height=34)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
