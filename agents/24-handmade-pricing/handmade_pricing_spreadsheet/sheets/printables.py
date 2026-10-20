"""The three printable pages: a cost sheet, a quote and a production docket.

These are the pages that leave the workbook. Each one is laid out for a single
portrait sheet, carries the shop's letterhead from Settings, and pulls its
numbers from the registers - so a cost sheet printed in March says the same
thing the catalog said in March.

* **Print Costing** - one product's full cost build-up, its bill of materials,
  the fees, the price the model asks for and what the current price earns.
* **Print Quote** - a wholesale quote on the shop's letterhead: pick the shop,
  type the lines, and the trade discount, tax and totals arrive.
* **Print Order** - a production docket for the workshop: what to make, how
  many, the materials needed for that quantity, and the steps to sign off.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..config import Config, Palette
from ..layout import lookup, quote_sheet
from ..writer import SheetWriter, list_from
from .common import (channel_fee_rate, channel_fixed_fee, fetch, other,
                     price_from, round_price)

P = Palette

SUBTITLE = ("Print one page: your letterhead, the product, and every number "
            "that supports the price.")

#: how many bill of materials lines the printables list
BOM_LINES = 12
#: how many lines a quote carries
QUOTE_LINES = 8


# ---------------------------------------------------------------------------
# shared page furniture
# ---------------------------------------------------------------------------

def _page(book, fmts, cfg: Config, reg, name: str, title: str,
          subtitle: str, last_col: int, badge: str) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, name, tab_color=P.primary_mid,
                        landscape=False)
    sheet.banner(title, subtitle, last_col, nav=False, badge=badge)
    sheet.set_col(0, 0, 2.5)
    sheet.ws.hide_gridlines(2)
    return sheet


def _letterhead(sheet, fmts, cfg: Config, reg, row: int, last_col: int) -> int:
    """The shop's details, read from Settings."""
    sheet.row_height(row, 26)
    sheet.merge(row, 1, last_col - 3, '=IF(ShopName="","",ShopName)',
                fmts.chrome("print_title"))
    sheet.merge(row, last_col - 2, last_col,
                '=IF(TodayDate=0,"",TodayDate)',
                fmts.chrome("print_sub", num_format=cfg.date_format,
                            align="right"))
    row += 1
    sheet.row_height(row, 15)
    sheet.merge(row, 1, last_col, '=IF(Tagline="","",Tagline)',
                fmts.chrome("print_sub"))
    row += 1
    for name in ("ShopAddress", "ShopEmail", "ShopPhone", "ShopWebsite"):
        sheet.row_height(row, 14)
        sheet.merge(row, 1, last_col, f'=IF({name}="","",{name})',
                    fmts.chrome("print_sub"))
        row += 1
    sheet.merge(row, 1, last_col, "", fmts.chrome("rule"))
    return row + 2


def _field(sheet, row: int, label: str, *, formula: Optional[str] = None,
           value: Any = None, name: Optional[str] = None,
           style: str = "money", input_cell: bool = False,
           validate: Optional[Dict[str, Any]] = None, help_text: str = "",
           label_col: int = 1, value_col: int = 4, value_end: int = 5,
           help_col: int = 6) -> int:
    return sheet.field(row, label, value, label_col=label_col,
                       value_col=value_col, value_end=value_end, style=style,
                       mode="input" if input_cell else "calc", name=name,
                       validate=validate, help_text=help_text,
                       help_col=help_col, formula=formula)


def _bom_row(sheet, fmts, reg, row: int, n: int, qty_multiplier: str = "") -> None:
    """One bill of materials line, taken from the hidden print rank."""
    rank = f"MATCH({n},{other('Material Usage', 'rank_for_print')},0)"
    material = f"IFERROR(INDEX({other('Material Usage', 'material_name')},{rank}),\"\")"
    qty = (f"IFERROR(INDEX({other('Material Usage', 'qty_with_scrap')},{rank}),"
           f"\"\")")
    unit_cost = f"IFERROR(INDEX({other('Material Usage', 'unit_cost')},{rank}),\"\")"
    line_cost = f"IFERROR(INDEX({other('Material Usage', 'cost')},{rank}),\"\")"
    if qty_multiplier:
        qty = f"IF({qty}=\"\",\"\",N({qty})*{qty_multiplier})"
        line_cost = f"IF({line_cost}=\"\",\"\",N({line_cost})*{qty_multiplier})"
    sheet.row_height(row, 16)
    fmt_text = fmts.cell("text", "plain")
    fmt_num = fmts.cell("number", "plain")
    fmt_money4 = fmts.cell("money4", "plain")
    fmt_money = fmts.cell("money", "plain")
    # merge first, then put the formula in the top left cell of the merge
    sheet.merge(row, 1, 3, None, fmt_text)
    sheet.ws.write_formula(row, 1, reg.render("=" + material), fmt_text)
    sheet.ws.write_formula(row, 4, reg.render("=" + qty), fmt_num)
    sheet.ws.write_formula(row, 5, reg.render("=" + unit_cost), fmt_money4)
    sheet.merge(row, 6, 7, None, fmt_money)
    sheet.ws.write_formula(row, 6, reg.render("=" + line_cost), fmt_money)


def _bom_head(sheet, fmts, row: int, qty_header: str = "Qty") -> int:
    sheet.row_height(row, 22)
    sheet.merge(row, 1, 3, "Material", fmts.chrome("header_left"))
    sheet.write(row, 4, qty_header, fmts.chrome("header"))
    sheet.write(row, 5, "Cost a unit", fmts.chrome("header"))
    sheet.merge(row, 6, 7, "Cost", fmts.chrome("header"))
    return row + 1


def _finish(sheet, row: int, last_col: int) -> None:
    sheet.ws.print_area(0, 0, row, last_col)
    sheet.ws.fit_to_pages(1, 1)
    sheet.ws.set_margins(0.5, 0.5, 0.6, 0.5)
    sheet.protect()


# ---------------------------------------------------------------------------
# Print Costing
# ---------------------------------------------------------------------------

COSTING = "Print Costing"


def build_costing(book, fmts, cfg: Config, reg) -> SheetWriter:
    last_col = 8
    sheet = _page(book, fmts, cfg, reg, COSTING, COSTING, SUBTITLE, last_col,
                  badge="One page, portrait")
    sheet.set_col(1, 3, 22.0)
    sheet.set_col(4, 5, 15.0)
    sheet.set_col(6, last_col, 16.0)

    r = _letterhead(sheet, fmts, cfg, reg, 3, last_col)
    r = sheet.section(r, "Cost sheet", last_col)

    prod = lambda key: lookup("PrintProduct", other("Products", "id"),
                              other("Products", key))
    channel_of = f'IFERROR({prod("channel")},DefaultChannel)'
    rate = channel_fee_rate(channel_of)
    fixed = channel_fixed_fee(channel_of)

    r = _field(sheet, r, "Product", name="PrintProduct", style="id",
               input_cell=True, validate=list_from("ProductIDs"),
               help_text="Pick a product and the whole sheet follows.")
    for label, key, style in [("Product name", "name", "text"),
                              ("SKU", "sku", "text"),
                              ("Category", "category", "text"),
                              ("Craft", "craft", "text"),
                              ("Status", "status", "text")]:
        r = _field(sheet, r, label, style=style,
                   formula=f'=IFERROR({prod(key)},"")')

    r = sheet.subsection(r, "What one item costs", last_col)
    cost_rows = [
        ("Materials", "material_cost", "money",
         "From the bill of materials below, or from the craft tab."),
        ("Minutes of work", "minutes_used", "number1", ""),
        ("Labour", "labor_cost", "money",
         "Minutes over sixty times the true cost of your hour."),
        ("Packaging", "packaging_cost", "money", ""),
        ("Postage you absorb", "shipping_cost", "money", ""),
        ("Share of overhead", "overhead_cost", "money", ""),
    ]
    for label, key, style, note in cost_rows:
        r = _field(sheet, r, label, style=style,
                   formula=f'=IFERROR({prod(key)},"")', help_text=note)
    total_row = r
    sheet.row_height(r, 22)
    sheet.merge(r, 1, 3, "Total cost of one item",
                fmts.chrome("total_label"))
    sheet.merge(r, 4, 5, None, fmts.chrome("total_value"))
    sheet.ws.write_formula(r, 4,
                           reg.render(f'=IFERROR({prod("total_cost")},"")'),
                           fmts.chrome("total_value"))
    sheet.merge(r, 6, last_col,
                "Materials + labour + packaging + postage + overhead.",
                fmts.chrome("note"))
    book.define_name("PrintCost",
                     f"={quote_sheet(COSTING)}!$E${total_row + 1}")
    r += 1

    r = sheet.subsection(r, "What selling it costs", last_col)
    r = _field(sheet, r, "Channel", style="text",
               formula=f'=IFERROR({prod("channel")},DefaultChannel)')
    r = _field(sheet, r, "Fee rate", style="percent", formula=f"={rate}")
    r = _field(sheet, r, "Fixed fees an order", style="money",
               formula=f"={fixed}")
    r = _field(sheet, r, "Fees at the current price", style="money",
               formula=f'=IFERROR({prod("total_fees")},"")')

    r = sheet.subsection(r, "The price", last_col)
    for label, key, style, note in [
            ("Price today", "retail_price", "money", ""),
            ("Suggested price", "suggested_price", "money",
             "(cost + fixed fees) / (1 - target margin - fee rate)."),
            ("Gap to the model price", "price_gap", "money",
             "Positive means the listing is under what your margin asks for."),
            ("Wholesale price", "wholesale_price", "money", ""),
            ("RRP / MSRP", "msrp", "money", ""),
            ("Profit an item", "profit", "money", ""),
            ("Margin", "margin", "percent", ""),
            ("Effective hourly", "effective_hourly", "money",
             "What an hour of making this earns."),
            ("Wage check", "hourly_flag", "text", "")]:
        r = _field(sheet, r, label, style=style,
                   formula=f'=IFERROR({prod(key)},"")', help_text=note)

    r = sheet.subsection(r, "Bill of materials", last_col)
    r = _bom_head(sheet, fmts, r)
    for n in range(1, BOM_LINES + 1):
        _bom_row(sheet, fmts, reg, r, n)
        r += 1
    r = _field(sheet, r, "Total from the bill", style="money",
               formula=f'=IFERROR({prod("bom_cost")},"")')

    r += 1
    r = sheet.subsection(r, "Prepared by", last_col)
    sheet.row_height(r, 22)
    sheet.merge(r, 1, 3, "", fmts.chrome("form_line"))
    sheet.merge(r, 4, 5, "=TodayDate", fmts.chrome("form_line"))
    sheet.ws.write_formula(r, 4, "=TodayDate", fmts.cell("date", "plain"))
    sheet.merge(r, 6, last_col, "Name and date", fmts.chrome("note"))
    r += 2
    r = sheet.note(r, f"{cfg.product_name} - created by {cfg.author}, "
                      f"version {cfg.version}. Figures are read live from the "
                      f"catalog, so a printed sheet matches the workbook it "
                      f"came from.", last_col, height=28, boxed=False)

    _finish(sheet, r, last_col)
    return sheet


# ---------------------------------------------------------------------------
# Print Quote
# ---------------------------------------------------------------------------

QUOTE = "Print Quote"


def build_quote(book, fmts, cfg: Config, reg) -> SheetWriter:
    last_col = 9
    sheet = _page(book, fmts, cfg, reg, QUOTE, "Print Quote", SUBTITLE,
                  last_col, badge="One page, portrait")
    sheet.set_col(1, 1, 6.0)
    sheet.set_col(2, 3, 20.0)
    sheet.set_col(4, 5, 12.0)
    sheet.set_col(6, 7, 13.0)
    sheet.set_col(8, last_col, 14.0)

    r = _letterhead(sheet, fmts, cfg, reg, 3, last_col)
    r = sheet.section(r, "Wholesale quote", last_col)

    cust = lambda key: lookup("QuoteCustomer",
                              other("Wholesale Customers", "id"),
                              other("Wholesale Customers", key))

    r = _field(sheet, r, "Quote number", name="QuoteNumber", style="text",
               input_cell=True, value="Q-0001", label_col=1, value_col=4,
               value_end=5, help_col=6)
    r = _field(sheet, r, "Date", style="date", formula="=TodayDate",
               label_col=1, value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Valid until", style="date", name="QuoteValidUntil",
               formula="=TodayDate+30", label_col=1, value_col=4,
               value_end=5, help_col=6)
    r = _field(sheet, r, "Shop", name="QuoteCustomer", style="id",
               input_cell=True, validate=list_from("CustomerIDs"),
               label_col=1, value_col=4, value_end=5, help_col=6,
               help_text="From the Wholesale Customers tab.")
    r = _field(sheet, r, "Contact", style="text",
               formula=f'=IFERROR({cust("contact")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Address", style="text",
               formula=f'=IFERROR({cust("address")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Terms", style="text", name="QuoteTerms",
               formula=f'=IFERROR({cust("terms")},"Net 30")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Trade discount", style="percent",
               name="QuoteDiscount",
               formula=f'=IFERROR({cust("discount")},WholesaleDiscount)',
               label_col=1, value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Tax rate", style="percent", name="QuoteTaxRate",
               formula=f'=IF(EXACT(TRIM(IFERROR({cust("tax_exempt")},"No")),'
                       f'"Yes"),0,TaxRate)', label_col=1, value_col=4,
               value_end=5, help_col=6,
               help_text="Zero for a tax exempt shop.")

    r = sheet.subsection(r, "Lines", last_col)
    head = r
    sheet.row_height(head, 24)
    sheet.write(head, 1, "#", fmts.chrome("header"))
    sheet.merge(head, 2, 3, "Product", fmts.chrome("header_left"))
    sheet.write(head, 4, "Qty", fmts.chrome("header"))
    sheet.write(head, 5, "Retail", fmts.chrome("header"))
    sheet.write(head, 6, "Discount", fmts.chrome("header"))
    sheet.merge(head, 7, 8, "Trade price", fmts.chrome("header"))
    sheet.write(head, last_col, "Line total", fmts.chrome("header"))
    r += 1

    first_line = r
    for n in range(1, QUOTE_LINES + 1):
        sheet.row_height(r, 18)
        sheet.write(r, 1, n, fmts.cell("int", "plain"))
        fmt_id = fmts.cell("id", "input")
        sheet.ws.merge_range(r, 2, r, 3, "", fmt_id)
        sheet.ws.data_validation(r, 2, r, 3, list_from("ProductIDs"))
        sheet.write(r, 4, None, fmts.cell("int", "input"))
        product_cell = f"$C${r + 1}"
        qty_cell = f"$E${r + 1}"
        retail = (f"IFERROR(INDEX({other('Products', 'retail_price')},"
                  f"MATCH({product_cell},{other('Products', 'id')},0)),0)")
        sheet.ws.write_formula(r, 5, reg.render("=" + retail),
                               fmts.cell("money", "plain"))
        sheet.ws.write_formula(r, 6, "=QuoteDiscount",
                               fmts.cell("percent", "plain"))
        trade = f"{round_price(f'{retail}*(1-QuoteDiscount)')}"
        sheet.ws.merge_range(r, 7, r, 8, "", fmts.cell("money", "plain"))
        sheet.ws.write_formula(r, 7, reg.render("=" + trade),
                               fmts.cell("money", "plain"))
        total = (f"IF(N({qty_cell})=0,\"\",N({qty_cell})*N($H${r + 1}))")
        sheet.ws.write_formula(r, last_col, reg.render("=" + total),
                               fmts.cell("money", "plain"))
        r += 1
    last_line = r - 1
    book.define_name("QuoteLines",
                     f"={quote_sheet(QUOTE)}!$J${first_line + 1}"
                     f":$J${last_line + 1}")

    r = sheet.subsection(r, "Totals", last_col)
    r = _field(sheet, r, "Subtotal", style="money",
               formula="=IFERROR(SUM(QuoteLines),0)", label_col=6,
               value_col=8, value_end=8)
    r = _field(sheet, r, "Postage", style="money", input_cell=True,
               name="QuotePostage", label_col=6, value_col=8, value_end=8)
    r = _field(sheet, r, "Tax", style="money", name="QuoteTax",
               formula="=IFERROR(SUM(QuoteLines)*QuoteTaxRate,0)",
               label_col=6, value_col=8, value_end=8)
    total_row = r
    sheet.row_height(r, 22)
    sheet.merge(r, 1, 5, "Trade prices exclude postage unless stated.",
                fmts.chrome("note"))
    sheet.merge(r, 6, 7, "Quote total", fmts.chrome("total_label"))
    sheet.merge(r, 8, 8, None, fmts.chrome("total_value"))
    sheet.ws.write_formula(
        r, 8, reg.render("=IFERROR(SUM(QuoteLines)+QuotePostage+QuoteTax,0)"),
        fmts.chrome("total_value"))
    book.define_name("QuoteTotal", f"={quote_sheet(QUOTE)}!$I${total_row + 1}")
    r += 1

    r += 1
    r = sheet.subsection(r, "Terms", last_col)
    for line in [
        "=QuoteTerms & \" from the date of invoice.\"",
        '="Minimum order " & TEXT(MinOrderValue,"$#,##0") & " or " & '
        'TEXT(MinOrderQty,"0") & " units a product."',
        '="Prices hold until " & TEXT(QuoteValidUntil,"dd mmm yyyy") & "."',
        '="Trade prices exclude postage unless stated. Tax ID " & TaxID & "."',
    ]:
        sheet.row_height(r, 15)
        sheet.merge(r, 1, last_col, "", fmts.chrome("label"))
        sheet.ws.write_formula(r, 1, reg.render(line), fmts.chrome("label"))
        r += 1
    r += 1
    sheet.row_height(r, 24)
    sheet.merge(r, 1, 4, "", fmts.chrome("form_line"))
    sheet.merge(r, 6, last_col, "", fmts.chrome("form_line"))
    r += 1
    sheet.merge(r, 1, 4, '=IF(ShopName="","",ShopName)',
                fmts.chrome("note"))
    sheet.merge(r, 6, last_col, "Accepted by (signature and date)",
                fmts.chrome("note"))
    r += 2

    _finish(sheet, r, last_col)
    return sheet


# ---------------------------------------------------------------------------
# Print Order - the production docket
# ---------------------------------------------------------------------------

ORDER = "Print Order"

STEPS = ["Cutting / preparing materials", "Making", "Finishing",
         "Quality check", "Packaging", "Label and care card", "Dispatch"]


def build_order(book, fmts, cfg: Config, reg) -> SheetWriter:
    last_col = 9
    sheet = _page(book, fmts, cfg, reg, ORDER, "Print Order", SUBTITLE,
                  last_col, badge="One page, portrait")
    sheet.set_col(1, 1, 6.0)
    sheet.set_col(2, 3, 24.0)
    sheet.set_col(4, 5, 13.0)
    sheet.set_col(6, 7, 13.0)
    sheet.set_col(8, last_col, 16.0)

    r = _letterhead(sheet, fmts, cfg, reg, 3, last_col)
    r = sheet.section(r, "Production docket", last_col)

    prod = lambda key: lookup("OrderProduct", other("Products", "id"),
                              other("Products", key))

    r = _field(sheet, r, "Docket number", name="OrderNumber", style="text",
               input_cell=True, value="DO-0001", label_col=1, value_col=4,
               value_end=5, help_col=6)
    r = _field(sheet, r, "Product", name="OrderProduct", style="id",
               input_cell=True, validate=list_from("ProductIDs"),
               label_col=1, value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Product name", style="text",
               formula=f'=IFERROR({prod("name")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "SKU", style="text",
               formula=f'=IFERROR({prod("sku")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Craft", style="text",
               formula=f'=IFERROR({prod("craft")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Difficulty", style="text",
               formula=f'=IFERROR({prod("difficulty")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Quantity to make", name="OrderQty", style="int",
               input_cell=True, value=cfg.default_batch_size, label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Needed by", name="OrderDue", style="date",
               input_cell=True, label_col=1, value_col=4, value_end=5,
               help_col=6)
    r = _field(sheet, r, "Made for", name="OrderFor", style="text",
               input_cell=True, label_col=1, value_col=4, value_end=5,
               help_col=6, help_text="Stock, an order, a fair, a shop.")
    r = _field(sheet, r, "Minutes an item", style="number1",
               formula=f'=IFERROR({prod("minutes_used")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Hours for the whole docket", style="number",
               name="OrderHours",
               formula=f'=IFERROR(N({prod("minutes_used")})*OrderQty/60,"")',
               label_col=1, value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Labour cost of the docket", style="money",
               formula="=N(OrderHours)*LaborCostHour", label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Cost a unit from the catalog", style="money",
               formula=f'=IFERROR({prod("total_cost")},"")', label_col=1,
               value_col=4, value_end=5, help_col=6)
    r = _field(sheet, r, "Cost of the whole docket", style="money",
               formula=f'=IFERROR(N({prod("total_cost")})*OrderQty,"")',
               label_col=1, value_col=4, value_end=5, help_col=6)

    r = sheet.subsection(r, "Materials needed", last_col)
    r = _bom_head(sheet, fmts, r, qty_header="Qty for the docket")
    for n in range(1, BOM_LINES + 1):
        _bom_row(sheet, fmts, reg, r, n, qty_multiplier="N(OrderQty)")
        r += 1

    r = sheet.subsection(r, "Steps", last_col)
    sheet.row_height(r, 20)
    sheet.merge(r, 1, 4, "Step", fmts.chrome("header_left"))
    sheet.write(r, 5, "Done", fmts.chrome("header"))
    sheet.merge(r, 6, 7, "Initials", fmts.chrome("header"))
    sheet.merge(r, 8, last_col, "Date", fmts.chrome("header"))
    r += 1
    for step in STEPS:
        sheet.row_height(r, 20)
        sheet.merge(r, 1, 4, step, fmts.chrome("label"))
        sheet.write(r, 5, None, fmts.cell("flag", "input"))
        sheet.ws.data_validation(r, 5, r, 5, list_from("YesNoList"))
        sheet.merge(r, 6, 7, None, fmts.cell("text", "input"))
        sheet.merge(r, 8, last_col, None, fmts.cell("date", "input"))
        r += 1

    r += 1
    r = sheet.subsection(r, "Notes for the maker", last_col)
    sheet.row_height(r, 60)
    sheet.merge(r, 1, last_col, None, fmts.chrome("form_box"))
    r += 2
    sheet.row_height(r, 24)
    sheet.merge(r, 1, 4, "", fmts.chrome("form_line"))
    sheet.merge(r, 6, last_col, "", fmts.chrome("form_line"))
    r += 1
    sheet.merge(r, 1, 4, "Made by", fmts.chrome("note"))
    sheet.merge(r, 6, last_col, "Checked by", fmts.chrome("note"))
    r += 2

    _finish(sheet, r, last_col)
    return sheet
