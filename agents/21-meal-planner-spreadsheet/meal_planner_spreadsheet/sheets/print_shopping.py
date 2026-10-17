"""
Print Shopping - the shopping list, sorted by aisle, ready to shop from.

Everything here is read from the Grocery List tab: the items that are still
to buy, the packs, the running total and the aisle order.  Print it, take
it to the shop and tick things off as you go.
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
        subtitle="The shopping list, sorted by aisle, ready to shop from",
        columns=[
            Col("aisle", "Aisle", 16, "calc"),
            Col("item", "Item", 26, "calc"),
            Col("quantity", "Qty", 9, "calc"),
            Col("unit", "Unit", 9, "calc"),
            Col("packs", "Packs", 8, "calc"),
            Col("store", "Store", 16, "calc"),
            Col("price", "Price", 10, "calc"),
            Col("line_total", "Total", 10, "calc"),
            Col("bought", "Bought", 10, "calc"),
        ],
        rows=24,
        header_row=8,
        tab_color=Palette.primary,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    reg = writer.registry
    writer.grid_off(ws)
    for i, col in enumerate(spec.columns):
        ws.set_column(i, i, col.width)

    ws.set_row(0, 32)
    ws.merge_range(0, 0, 0, 8, "SHOPPING LIST", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 8,
                   "Sorted by aisle - tick things off as you shop",
                   f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 8,
                   "  |  Grocery List   |   Print Week   |   Pantry   |   "
                   "Staples", f["nav"])

    gl_item = reg.rng("Grocery List", "item")
    gl_buy = reg.rng("Grocery List", "buy")
    gl_needed = reg.rng("Grocery List", "needed")
    gl_buy_rank = reg.rng("Grocery List", "buy_rank")
    gl_total = reg.rng("Grocery List", "line_total")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 8, "  THIS WEEK'S SHOP", f["section"])
    ws.write(5, 0, "Week starting", f["label"])
    ws.write_string(5, 1, cfg.start_date.strftime("%Y-%m-%d"), f["input_text"])
    ws.write(5, 3, "Items to buy", f["label"])
    ws.write_formula(5, 4, f'=COUNTIFS({gl_buy},"Yes")', f["calc_number"])
    ws.write(5, 6, "Estimated total", f["label"])
    ws.write_formula(5, 7,
                     f'=SUMIFS({gl_total},{gl_buy},"Yes")', f["calc_money"])
    ws.write(6, 0, "Household", f["label"])
    ws.write_formula(6, 1, "=Household_Name", f["calc_text"])
    ws.write(6, 3, "Budget left", f["label"])
    ws.write_formula(6, 4,
                     f'=Weekly_Budget-SUMIFS('
                     + reg.rng("Meal Plan", "cost") + ','
                     + reg.rng("Meal Plan", "week_start") + ',$B$7)',
                     f["calc_money"])
    ws.write(6, 6, "Items still needed", f["label"])
    ws.write_formula(6, 7, f'=COUNTIFS({gl_needed},">0")', f["calc_number"])
    ws.write_formula(7, 1, "=DATEVALUE($B$6)", f["calc_date"])

    hrow = spec.header_row - 1
    ws.set_row(hrow, 26)
    for i, col in enumerate(spec.columns):
        ws.write(hrow, i, col.header, f["header"])

    pulls = ["aisle", "item", "quantity", "unit", "packs", "store",
             "price", "line_total", "bought"]
    for n in range(1, 25):
        xrow = spec.first_data_row - 1 + n - 1   # 0-based writer row
        for i, key in enumerate(pulls):
            rng = reg.rng("Grocery List", key)
            ws.write_formula(
                xrow, i,
                f'=IFERROR(INDEX({rng},MATCH({n},{gl_buy_rank},0)),"")',
                f["calc_money"] if key in ("price", "line_total")
                else (f["calc_number"] if key in ("quantity", "packs")
                      else (f["calc_center"] if key == "bought"
                            else f["calc_text"])))
        ws.set_row(xrow, 20)

    total_row = spec.last_data_row
    tr = total_row + 1
    ws.write(total_row, 0, "Total", f["total_label"])
    for i in range(1, 6):
        ws.write_blank(total_row, i, None, f["total_label"])
    ws.write_formula(total_row, 6,
                     f'=SUMIFS({gl_total},{gl_buy},"Yes")', f["total_money"])
    ws.write_blank(total_row, 7, None, f["total_label"])
    ws.write_formula(total_row, 8,
                     f'=TEXT(COUNTIFS({gl_buy},"Yes"),"0")&" items"',
                     f["total_label"])

    writer.write_note(ws, total_row + 2, 0,
                      "The list fills itself from the Grocery List tab. "
                      "Tick the Bought column there and this page follows.",
                      width=8)

    ws.freeze_panes(spec.header_row, 1)
    ws.set_tab_color(Palette.primary)
    ws.set_portrait()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, total_row + 3, 8)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
