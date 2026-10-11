"""
Print Shopping - a printable grocery list.

Choose the store and print.  The list is pulled from the Grocery List tab in
buy order, grouped by aisle, with a tick box down the side and a running
total so you can see the cost of the basket as it fills.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    spec = SheetSpec(
        name="Print Shopping",
        title="Print Shopping",
        subtitle="A printable grocery list, in buy order",
        columns=[
            Col("label", " ", 14, "text"),
            Col("value", "Value", 18, "text"),
            Col("item", "Item", 28, "calc"),
            Col("category", "Aisle", 18, "calc"),
            Col("quantity", "Quantity", 11, "calc"),
            Col("unit", "Unit", 10, "calc"),
            Col("store", "Store", 18, "calc"),
            Col("bought", "Got it", 9, "calc"),
            Col("notes", "Notes", 24, "calc"),
        ],
        rows=60,
        header_row=4,
        tab_color=Palette.accent,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 34)
    ws.merge_range(0, 0, 0, 8, "GROCERY LIST", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "In buy order - tick each item off as you fill the basket",
                   f["subtitle"])
    ws.set_row(2, 22)
    ws.write(2, 0, "Store", f["label"])
    ws.write_string(2, 1, cfg.household.store, f["input_text"])
    ws.write(2, 3, "Week starting", f["label"])
    ws.write_formula(2, 4, "=Print_Week_Start", f["calc_date"])
    ws.write(2, 6, "Budget", f["label"])
    ws.write_formula(2, 7, "=Weekly_Budget", f["calc_money"])

    buy_rank = reg.rng("Grocery List", "buy_rank")

    hrow = spec.header_row - 1
    ws.set_row(hrow, 24)
    for i, head in enumerate(["", "", "Item", "Aisle", "Quantity", "Unit",
                              "Store", "Got it", "Notes"]):
        ws.write(hrow, i, head, f["header"])

    for n in range(1, spec.rows + 1):
        row = spec.first_data_row + n - 1
        r = row + 1
        ws.write_number(row, 0, n, f["calc_center"])
        for i, key in enumerate(["item", "category", "quantity", "unit",
                                 "store", "bought", "notes"]):
            rng = reg.rng("Grocery List", key)
            ws.write_formula(
                row, 2 + i,
                f'=IFERROR(INDEX({rng},MATCH($A{r},{buy_rank},0)),"")',
                f["calc_number"] if key == "quantity"
                else f["calc_text"])
        ws.set_row(row, 20)

    total = spec.last_data_row
    ws.write(total, 2, "Total to buy", f["total_label"])
    for i in (3, 4, 5, 6):
        ws.write_blank(total, i, None, f["total_label"])
    ws.write_formula(total, 7,
                     f'=COUNTIFS({reg.rng("Grocery List", "buy")},"Yes")'
                     f'&" items"', f["total_label"])
    ws.write_formula(total, 8,
                     f'=SUMIFS({reg.rng("Grocery List", "line_total")},'
                     f'{reg.rng("Grocery List", "buy")},"Yes")',
                     f["total_money"])

    ws.set_tab_color(Palette.accent)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.5, 0.5, 0.6, 0.6)
    ws.center_horizontally()
    ws.set_header(f"&L&\"Calibri,Bold\"{cfg.product_name}"
                  f"&R&\"Calibri,Italic\"Grocery list")
    ws.set_footer("&L&D&RPage &P of &N")
    ws.print_area(0, 0, total, 8)
    ws.hide_gridlines(2)
