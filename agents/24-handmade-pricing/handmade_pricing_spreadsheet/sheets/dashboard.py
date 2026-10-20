"""The Dashboard - the whole shop on one screen.

Three bands of numbers (this month, this year, the workshop), a warnings panel
that counts everything needing a decision, the three top-five tables the hidden
rank columns on Products feed, the two lists nobody wants to look at - products
losing money and prices overdue a review - then trading by channel, by craft
and month by month, and a spotlight that follows whichever product you pick.

Nothing here is typed. Every figure is a SUMIFS, a COUNTIFS or an INDEX/MATCH
against a register, so the page is right the moment the registers are.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from ..config import Config, Palette
from ..layout import SheetSpec, lookup
from ..writer import SheetWriter, list_from
from .common import (FIRST_ROW, fetch, flag_list, other, row_ref, top_by,
                     top_value)

P = Palette

NAME = "Dashboard"

SUBTITLE = ("This month, this year, what is selling, what is losing money and "
            "what needs a decision today.")

HELP = ("Everything on this page is calculated from the registers. Pick a "
        "product in the spotlight at the bottom to see its numbers.")


def _sum(value_key: str, sheet: str, start: str, end: str,
         date_key: str = "date") -> str:
    """SUMIFS over a date window."""
    return (f"IFERROR(SUMIFS({other(sheet, value_key)},"
            f"{other(sheet, date_key)},\">=\"&{start},"
            f"{other(sheet, date_key)},\"<=\"&{end}),0)")


def _count(sheet: str, start: str, end: str,
           date_key: str = "date") -> str:
    return (f"IFERROR(COUNTIFS({other(sheet, date_key)},\">=\"&{start},"
            f"{other(sheet, date_key)},\"<=\"&{end}),0)")


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=True)
    last_col = 15
    sheet.banner(NAME, SUBTITLE, last_col, badge="Calculated - nothing to type")
    for i in range(last_col + 1):
        sheet.set_col(i, i, 2.5 if i == 0 else 13.5)
    sheet.set_col(1, 1, 22.0)
    sheet.ws.hide_gridlines(2)

    r = sheet.note(3, HELP, last_col, height=26)

    # ------------------------------------------------------------- this month
    r = sheet.section(r, "This month", last_col)
    month_revenue = _sum("gross", "Sales", "MonthStart", "MonthEnd")
    month_profit = _sum("profit", "Sales", "MonthStart", "MonthEnd")
    month_units = _sum("qty", "Sales", "MonthStart", "MonthEnd")
    month_minutes = _sum("minutes_total", "Sales", "MonthStart", "MonthEnd")
    month_orders = _count("Sales", "MonthStart", "MonthEnd")
    tiles = [
        ("Revenue", month_revenue, "money0", "Against the target on Settings"),
        ("Profit", month_profit, "money0", "After every fee and the cost of "
                                           "goods"),
        ("Margin", f"IF({month_revenue}=0,0,{month_profit}/{month_revenue})",
         "percent", "Profit as a share of revenue"),
        ("Orders", month_orders, "int", "Lines on the Sales tab"),
        ("Units", month_units, "int", "Items sold"),
        ("Hourly earned",
         f"IF({month_minutes}=0,0,{month_profit}/({month_minutes}/60))",
         "money", "What an hour of making earned"),
    ]
    r = _tile_row(sheet, r, 1, tiles, span=2)
    r = _target_row(
        sheet, fmts, r, 1, last_col,
        [("Revenue target", "MonthlyRevenueTarget", "money0", month_revenue),
         ("Profit target", "MonthlyProfitTarget", "money0", month_profit)])
    r += 1

    # -------------------------------------------------------------- this year
    r = sheet.section(r, "This year", last_col)
    year_revenue = _sum("gross", "Sales", "YearStart", "YearEnd")
    year_profit = _sum("profit", "Sales", "YearStart", "YearEnd")
    year_units = _sum("qty", "Sales", "YearStart", "YearEnd")
    tiles = [
        ("Revenue", year_revenue, "money0", "Against the annual target"),
        ("Profit", year_profit, "money0", "After fees and cost of goods"),
        ("Units", year_units, "int", "Items sold this year"),
        ("Waste", _sum("cost", "Waste Log", "YearStart", "YearEnd"), "money0",
         "What got broken, spoiled or mis-cut"),
        ("Overhead", "OverheadMonthly", "money0", "A month, from the Overhead "
                                                  "tab"),
        ("Stock value", f"IFERROR(SUM({other('Materials', 'stock_value')}),0)",
         "money0", "What is on the shelf"),
    ]
    r = _tile_row(sheet, r, 1, tiles, span=2)
    r = _target_row(
        sheet, fmts, r, 1, last_col,
        [("Revenue target", "AnnualRevenueTarget", "money0", year_revenue)])
    r += 1

    # ------------------------------------------------------- workshop & trade
    r = sheet.section(r, "The workshop and the trade", last_col)
    labour_hours = _sum("hours", "Labor", "MonthStart", "MonthEnd")
    labour_cost = _sum("loaded_cost", "Labor", "MonthStart", "MonthEnd")
    shop_hours = (f"IFERROR(SUMIFS({other('Labor', 'hours')},"
                  f"{other('Labor', 'date')},\">=\"&MonthStart,"
                  f"{other('Labor', 'date')},\"<=\"&MonthEnd,"
                  f"{other('Labor', 'product')},\"\"),0)")
    tiles = [
        ("Hours worked", labour_hours, "number", "This month, from the Labor "
                                                 "tab"),
        ("Labour cost", labour_cost, "money0", "With the payroll burden added"),
        ("Shop hours", shop_hours, "number", "Time not on one product"),
        ("Productive hours", "ProductiveHours", "number",
         "What Settings assumes a month"),
        ("Wholesale owed",
         f"IFERROR(SUM({other('Wholesale Orders', 'balance_outstanding')}),0)",
         "money0", "Trade orders not marked Paid"),
        ("Wholesale overdue",
         (f"IFERROR(SUMIFS({other('Wholesale Orders', 'balance_outstanding')},"
          f"{other('Wholesale Orders', 'aging_flag')},\"OVERDUE\"),0)"),
         "money0", "Past the due date"),
    ]
    r = _tile_row(sheet, r, 1, tiles, span=2)
    r += 1

    # --------------------------------------------------------------- warnings
    r = sheet.section(r, "What needs a decision", last_col)
    warnings = [
        ("Products losing money",
         f"IFERROR(COUNTIFS({other('Products', 'margin_flag')},\"LOSS\"),0)",
         "Products below cost after fees - the Dashboard lists them below."),
        ("Margins below target",
         f"IFERROR(COUNTIFS({other('Products', 'margin_flag')},\"THIN\"),0)",
         "Priced under the margin warning on Settings."),
        ("Paying below the minimum wage",
         (f"IFERROR(COUNTIFS({other('Products', 'hourly_flag')},"
          f"\"BELOW MIN WAGE\"),0)"),
         "An hour of making these earns less than the minimum."),
        ("Paying you to work",
         (f"IFERROR(COUNTIFS({other('Products', 'hourly_flag')},"
          f"\"PAYING TO WORK\"),0)"),
         "Negative profit per hour - every sale costs you money."),
        ("Prices overdue a review",
         f"IFERROR(COUNTIFS({other('Products', 'review_flag')},\"OVERDUE\"),0)",
         "Past the review window on Settings."),
        ("Materials to re-order",
         (f"IFERROR(COUNTIFS({other('Materials', 'stock_flag')},\"REORDER\")"
          f"+COUNTIFS({other('Materials', 'stock_flag')},\"ORDER NOW\"),0)"),
         "At or below the re-order point."),
        ("Waste above the target",
         f"IFERROR(COUNTIFS({other('Materials', 'waste_flag')},\"WASTE HIGH\"),0)",
         "Real losses running ahead of the guess."),
        ("Fee schedule out of date", "IF(FeeStale=\"Yes\",1,0)",
         "The fees on Settings have not been checked recently."),
        ("Wholesale orders overdue",
         (f"IFERROR(COUNTIFS({other('Wholesale Orders', 'aging_flag')},"
          f"\"OVERDUE\"),0)"),
         "Trade invoices past their due date."),
        ("Batches above the defect target",
         (f"IFERROR(COUNTIFS({other('Batches', 'defect_flag')},"
          f"\"ABOVE THE TARGET\"),0)"),
         "More seconds than the defect rate on Settings."),
        ("Events that lost money",
         f"IFERROR(COUNTIFS({other('Events', 'verdict')},\"LOST MONEY\"),0)",
         "Table fees and hours against what the day took."),
        ("Promotions still live past their end",
         (f"IFERROR(COUNTIFS({other('Promotions', 'state')},\"ENDED\","
          f"{other('Promotions', 'active')},\"Yes\"),0)"),
         "Switched on but out of date."),
    ]
    for i, (label, formula, note) in enumerate(warnings):
        col = 1 + (i % 2) * 7
        if i % 2 == 0:
            sheet.row_height(r, 30)
        sheet.merge(r, col, col + 1, label, fmts.chrome("kpi_label"))
        fmt = fmts.chrome("kpi_value", num_format="#,##0")
        sheet.ws.write_blank(r, col + 2, None, fmt)
        sheet.ws.write_formula(r, col + 2, _expand(formula), fmt)
        sheet.merge(r, col + 3, col + 6, note, fmts.chrome("kpi_note"))
        sheet.ws.conditional_format(
            r, col + 2, r, col + 2,
            {"type": "cell", "criteria": ">", "value": 0,
             "format": fmts.cf("bad")})
        if i % 2 == 1:
            r += 1
    if len(warnings) % 2:
        r += 1
    r += 1

    # ------------------------------------------------------------- top fives
    r = sheet.section(r, "The top five", last_col)
    tables = [
        ("By revenue", "rank_revenue", "revenue", "money0"),
        ("By profit", "rank_profit", "gross_profit", "money0"),
        ("By margin", "rank_margin", "margin", "percent"),
    ]
    sheet.row_height(r, 20)
    for i, (title, _rank, _value, _style) in enumerate(tables):
        col = 1 + i * 5
        sheet.merge(r, col, col + 4, title, fmts.chrome("subsection"))
    r += 1
    sheet.row_height(r, 18)
    for i in range(3):
        col = 1 + i * 5
        sheet.write(r, col, "#", fmts.chrome("header_left"))
        sheet.merge(r, col + 1, col + 3, "Product", fmts.chrome("header_left"))
        sheet.write(r, col + 4, tables[i][2].replace("_", " ").title(),
                    fmts.chrome("header"))
    r += 1
    for n in range(1, 6):
        sheet.row_height(r, 17)
        for i, (_title, rank_key, value_key, style) in enumerate(tables):
            col = 1 + i * 5
            sheet.write(r, col, n, fmts.cell("int", "plain"))
            name_formula = _expand(top_by("Products", rank_key, "Products",
                                          "name", n))
            value_formula = _expand(top_value("Products", rank_key, "Products",
                                              value_key, n))
            sheet.merge(r, col + 1, col + 3, "", fmts.cell("text", "plain"))
            sheet.ws.write_formula(r, col + 1, name_formula,
                                   fmts.cell("text", "plain"))
            sheet.ws.write_formula(r, col + 4, value_formula,
                                   fmts.cell(style, "plain"))
        r += 1
    r += 1

    # ------------------------------------------------------- needs attention
    r = sheet.section(r, "Needs attention", last_col)
    attention = [
        ("Losing money", "rank_loss",
         [("Price", "retail_price", "money"),
          ("Cost", "total_cost", "money"),
          ("Should be", "suggested_price", "money"),
          ("Margin", "margin", "percent")]),
        ("Review overdue", "rank_review",
         [("Price", "retail_price", "money"),
          ("Last review", "reviewed", "date"),
          ("Due", "next_review", "date"),
          ("Units sold", "units_sold", "int")]),
        ("Re-order", "rank_reorder",
         [("On hand", "on_hand", "number"),
          ("Re-order at", "reorder_point", "number"),
          ("Order qty", "reorder_qty", "number"),
          ("Order cost", "order_cost", "money")]),
    ]
    for title, rank_key, extras in attention:
        source = "Materials" if rank_key.startswith("rank_reorder") or \
            rank_key in ("rank_reorder", "rank_out") else "Products"
        r = sheet.subsection(r, title, last_col)
        sheet.row_height(r, 18)
        sheet.write(r, 1, "#", fmts.chrome("header_left"))
        sheet.merge(r, 2, 5, "Item", fmts.chrome("header_left"))
        col = 6
        for label, _key, _style in extras:
            sheet.merge(r, col, col + 1, label, fmts.chrome("header"))
            col += 2
        r += 1
        for n in range(1, 6):
            sheet.row_height(r, 17)
            sheet.write(r, 1, n, fmts.cell("int", "plain"))
            sheet.merge(r, 2, 5, "", fmts.cell("text", "plain"))
            sheet.ws.write_formula(
                r, 2, _expand(flag_list(source, rank_key, "name", n)),
                fmts.cell("text", "plain"))
            col = 6
            for _label, key, style in extras:
                formula = _expand(flag_list(source, rank_key, "name", n,
                                            value_key=key))
                sheet.ws.merge_range(r, col, r, col + 1, "",
                                     fmts.cell(style, "plain"))
                sheet.ws.write_formula(r, col, formula,
                                       fmts.cell(style, "plain"))
                col += 2
            r += 1
        r += 1

    # ----------------------------------------------------------- by channel
    r = sheet.section(r, "Trading by channel this month", last_col)
    sheet.row_height(r, 20)
    headers = ["Channel", "Orders", "Revenue", "Fees", "Profit", "Margin",
               "Effective fee"]
    for i, head in enumerate(headers):
        col = 1 + i * 2
        sheet.merge(r, col, col + 1, head, fmts.chrome("header_left"))
    r += 1
    channels = reg["Channels"]
    for n in range(1, 7):
        row_of = channels.first_data_row + n - 1
        name_formula = (f"IFERROR(INDEX({other('Channels', 'name')},"
                        f"MATCH({n},{other('Channels', 'rank_channel')},0)),\"\")"
                        if "rank_channel" in [c.key for c in channels.columns]
                        else f"IFERROR(INDEX({other('Channels', 'name')},{n}),\"\")")
        chan_cell = f"INDEX({other('Channels', 'name')},{n})"
        orders = (f"IFERROR(COUNTIFS({other('Sales', 'channel')},{chan_cell},"
                  f"{other('Sales', 'date')},\">=\"&MonthStart,"
                  f"{other('Sales', 'date')},\"<=\"&MonthEnd),0)")
        revenue = (f"IFERROR(SUMIFS({other('Sales', 'gross')},"
                   f"{other('Sales', 'channel')},{chan_cell},"
                   f"{other('Sales', 'date')},\">=\"&MonthStart,"
                   f"{other('Sales', 'date')},\"<=\"&MonthEnd),0)")
        fees = (f"IFERROR(SUMIFS({other('Sales', 'fees')},"
                f"{other('Sales', 'channel')},{chan_cell},"
                f"{other('Sales', 'date')},\">=\"&MonthStart,"
                f"{other('Sales', 'date')},\"<=\"&MonthEnd),0)")
        profit = (f"IFERROR(SUMIFS({other('Sales', 'profit')},"
                  f"{other('Sales', 'channel')},{chan_cell},"
                  f"{other('Sales', 'date')},\">=\"&MonthStart,"
                  f"{other('Sales', 'date')},\"<=\"&MonthEnd),0)")
        sheet.row_height(r, 17)
        sheet.ws.merge_range(r, 1, r, 2, "", fmts.cell("text", "plain"))
        sheet.ws.write_formula(
            r, 1, _expand(f"IFERROR({chan_cell},\"\")"),
            fmts.cell("text", "plain"))
        for i, (formula, style) in enumerate([
                (orders, "int"), (revenue, "money"), (fees, "money"),
                (profit, "money"),
                (f"IF({revenue}=0,\"\",{profit}/{revenue})", "percent"),
                (f"IF({revenue}=0,\"\",{fees}/{revenue})", "percent")]):
            col = 3 + i * 2
            sheet.ws.merge_range(r, col, r, col + 1, "",
                                 fmts.cell(style, "plain"))
            sheet.ws.write_formula(r, col, _expand(formula),
                                   fmts.cell(style, "plain"))
        r += 1
    r += 1

    # ------------------------------------------------------------ by craft
    r = sheet.section(r, "Trading by craft this year", last_col)
    sheet.row_height(r, 20)
    for i, head in enumerate(["Craft", "Units", "Revenue", "Profit", "Margin",
                              "Hourly earned"]):
        col = 1 + i * 2
        sheet.merge(r, col, col + 1, head, fmts.chrome("header_left"))
    r += 1
    for n, craft in enumerate(["Crochet", "Jewelry", "Candles", "Clothing",
                               "Woodworking", "Digital"]):
        units = (f"IFERROR(SUMIFS({other('Sales', 'qty')},"
                 f"{other('Sales', 'craft')},\"{craft}\","
                 f"{other('Sales', 'date')},\">=\"&YearStart,"
                 f"{other('Sales', 'date')},\"<=\"&YearEnd),0)")
        revenue = (f"IFERROR(SUMIFS({other('Sales', 'gross')},"
                   f"{other('Sales', 'craft')},\"{craft}\","
                   f"{other('Sales', 'date')},\">=\"&YearStart,"
                   f"{other('Sales', 'date')},\"<=\"&YearEnd),0)")
        profit = (f"IFERROR(SUMIFS({other('Sales', 'profit')},"
                  f"{other('Sales', 'craft')},\"{craft}\","
                  f"{other('Sales', 'date')},\">=\"&YearStart,"
                  f"{other('Sales', 'date')},\"<=\"&YearEnd),0)")
        minutes = (f"IFERROR(SUMIFS({other('Sales', 'minutes_total')},"
                   f"{other('Sales', 'craft')},\"{craft}\","
                   f"{other('Sales', 'date')},\">=\"&YearStart,"
                   f"{other('Sales', 'date')},\"<=\"&YearEnd),0)")
        sheet.row_height(r, 17)
        sheet.ws.merge_range(r, 1, r, 2, "", fmts.cell("text", "plain"))
        sheet.ws.write(r, 1, craft, fmts.cell("text", "plain"))
        for i, (formula, style) in enumerate([
                (units, "int"), (revenue, "money"), (profit, "money"),
                (f"IF({revenue}=0,\"\",{profit}/{revenue})", "percent"),
                (f"IF({minutes}=0,\"\",{profit}/({minutes}/60))", "money")]):
            col = 3 + i * 2
            sheet.ws.merge_range(r, col, r, col + 1, "",
                                 fmts.cell(style, "plain"))
            sheet.ws.write_formula(r, col, _expand(formula),
                                   fmts.cell(style, "plain"))
        r += 1
    r += 1

    # ----------------------------------------------------------- month by month
    r = sheet.section(r, f"Month by month - {cfg.year}", last_col)
    sheet.row_height(r, 20)
    for i, head in enumerate(["Month", "Orders", "Units", "Revenue", "Profit",
                              "Margin", "Against the target"]):
        col = 1 + i * 2
        sheet.merge(r, col, col + 1, head, fmts.chrome("header_left"))
    r += 1
    for month in range(1, 13):
        start = f"DATE(ReportYear,{month},1)"
        end = f"EOMONTH(DATE(ReportYear,{month},1),0)"
        revenue = _sum("gross", "Sales", start, end)
        profit = _sum("profit", "Sales", start, end)
        units = _sum("qty", "Sales", start, end)
        orders = _count("Sales", start, end)
        sheet.row_height(r, 17)
        sheet.ws.merge_range(r, 1, r, 2, "", fmts.cell("text", "plain"))
        sheet.ws.write_formula(r, 1, f'=TEXT({start},"mmm")',
                               fmts.cell("text", "plain"))
        for i, (formula, style) in enumerate([
                (orders, "int"), (units, "int"), (revenue, "money"),
                (profit, "money"),
                (f"IF({revenue}=0,\"\",{profit}/{revenue})", "percent"),
                (f"{revenue}-MonthlyRevenueTarget", "money")]):
            col = 3 + i * 2
            sheet.ws.merge_range(r, col, r, col + 1, "",
                                 fmts.cell(style, "plain"))
            sheet.ws.write_formula(r, col, _expand(formula),
                                   fmts.cell(style, "plain"))
        r += 1
    r += 1

    # ------------------------------------------------------------- spotlight
    r = sheet.section(r, "Product spotlight", last_col)
    sheet.row_height(r, 24)
    sheet.merge(r, 1, 2, "Pick a product", fmts.chrome("form_label"))
    spot_fmt = fmts.cell("id", "input")
    sheet.ws.merge_range(r, 3, r, 5, "", spot_fmt)
    sheet.ws.data_validation(r, 3, r, 5, list_from("ProductIDs"))
    book.define_name("DashProduct", f"='{NAME}'!$D${r + 1}")
    sheet.merge(r, 6, last_col,
                "Every figure below follows the product you pick.",
                fmts.chrome("note"))
    r += 1
    spotlight = [
        ("Product", "name", "text"), ("Craft", "craft", "text"),
        ("Status", "status", "text"), ("Price today", "retail_price", "money"),
        ("Total cost", "total_cost", "money"),
        ("Suggested price", "suggested_price", "money"),
        ("Gap to suggested", "price_gap", "money"),
        ("Profit a unit", "profit", "money"), ("Margin", "margin", "percent"),
        ("Minutes an item", "minutes_used", "number1"),
        ("Effective hourly", "effective_hourly", "money"),
        ("Wage check", "hourly_flag", "text"),
        ("Units sold", "units_sold", "int"), ("Revenue", "revenue", "money"),
        ("Gross profit", "gross_profit", "money"),
        ("Wholesale price", "wholesale_price", "money"),
        ("Wholesale margin", "wholesale_margin", "percent"),
        ("Last sale", "last_sale", "date"),
    ]
    for i, (label, key, style) in enumerate(spotlight):
        col = 1 + (i % 3) * 5
        if i % 3 == 0:
            sheet.row_height(r, 22)
        sheet.merge(r, col, col + 1, label, fmts.chrome("kpi_label"))
        formula = _expand(lookup("DashProduct", other("Products", "id"),
                                 other("Products", key)))
        fmt = fmts.cell(style, "plain")
        sheet.ws.merge_range(r, col + 2, r, col + 4, "", fmt)
        sheet.ws.write_formula(r, col + 2, formula, fmt)
        if i % 3 == 2:
            r += 1
    if len(spotlight) % 3:
        r += 1
    r += 1
    r = sheet.note(
        r,
        "A gap to suggested above zero means the listing is priced under what "
        "your own target margin asks for. A wage check that says BELOW MINIMUM "
        "WAGE means an hour of making it earns less than the floor on "
        "Settings - that is a pricing problem, not a productivity one.",
        last_col, height=40)

    sheet.ws.freeze_panes(FIRST_ROW - 1, 0)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet


# ---------------------------------------------------------------------------

def _expand(formula: str) -> str:
    """Make sure a formula body starts with = for write_formula."""
    text = formula.strip()
    if text.startswith("="):
        return text
    return "=" + text


def _tile_row(sheet, row: int, col: int,
              tiles: Sequence[Tuple[str, str, str, str]], span: int = 2) -> int:
    """A row of KPI tiles. Returns the row below them."""
    for i, (label, formula, style, note) in enumerate(tiles):
        sheet.kpi(row, col + i * span, label, _expand(formula), style=style,
                  span=span, note=note)
    return row + 3


def _target_row(sheet, fmts, row: int, col: int, last_col: int,
                targets: Sequence[Tuple[str, str, str, str]]) -> int:
    """Targets next to the actuals, with the gap."""
    for i, (label, name, style, actual) in enumerate(targets):
        start = col + i * 5
        sheet.merge(row, start, start + 1, label, fmts.chrome("label_bold"))
        fmt = fmts.cell(style, "plain")
        sheet.ws.write_formula(row, start + 2, f"={name}", fmt)
        sheet.ws.merge_range(row, start + 3, row, start + 4, "",
                             fmts.cell(style, "plain"))
        sheet.ws.write_formula(
            row, start + 3,
            _expand(f"IF({name}=0,\"\",({actual})/{name}-1)"),
            fmts.cell("percent", "plain"))
        sheet.ws.conditional_format(
            row, start + 3, row, start + 4,
            {"type": "cell", "criteria": "<", "value": 0,
             "format": fmts.cf("warn")})
    return row + 1
