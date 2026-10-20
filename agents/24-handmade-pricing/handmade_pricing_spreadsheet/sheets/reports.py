"""The Reports tab - the year on one page.

Month by month, then by category, by channel and by craft, then the top ten
products and the ten worst margins, then stock, wholesale, promotions, events
and labour. Everything is a SUMIFS, a COUNTIFS or an INDEX/MATCH against a
register, so the page is a report of what is really in the workbook rather than
a copy somebody typed in.

The worst-margin table is the one worth reading. It is built from the hidden
rank column on Products by counting backwards from the number of products, so
it needs no array formula and it works in Excel 2010.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..config import (PRODUCT_CATEGORIES, Config, Palette)
from ..writer import SheetWriter
from .common import CRAFT_LIST, other

P = Palette

NAME = "Reports"

SUBTITLE = (f"The year month by month, by category, by channel and by craft, "
            f"with the best and the worst of the catalog.")

HELP = ("Nothing to type here. Change the year by changing the date on your "
        "computer - the reports follow TODAY().")


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=P.primary,
                        landscape=True)
    last_col = 17
    sheet.banner(NAME, SUBTITLE, last_col, badge="Calculated")
    sheet.set_col(0, 0, 2.5)
    sheet.set_col(1, 2, 26.0)
    for i in range(3, last_col + 1):
        sheet.set_col(i, i, 13.0)
    sheet.ws.hide_gridlines(2)

    def x(formula: str) -> str:
        text = formula.strip()
        if not text.startswith("="):
            text = "=" + text
        return reg.render(text)

    def put(row: int, col: int, formula: str, style: str = "money",
            span: int = 1) -> None:
        fmt = fmts.cell(style, "plain")
        if span > 1:
            sheet.ws.merge_range(row, col, row, col + span - 1, "", fmt)
        sheet.ws.write_formula(row, col, x(formula), fmt)

    def put_text(row: int, col: int, text: str, style: str = "text",
                 span: int = 1) -> None:
        fmt = fmts.cell(style, "plain")
        if span > 1:
            sheet.ws.merge_range(row, col, row, col + span - 1, text, fmt)
        else:
            sheet.ws.write(row, col, text, fmt)

    def window(sheet_name: str, value_key: str, start: str, end: str,
               extra: Sequence[Tuple[str, str]] = ()) -> str:
        pairs = [f"{other(sheet_name, 'date')},\">=\"&{start}",
                 f"{other(sheet_name, 'date')},\"<=\"&{end}"]
        pairs += [f"{rng},{crit}" for rng, crit in extra]
        return ("IFERROR(SUMIFS(" + ",".join(
            [other(sheet_name, value_key)] + pairs) + "),0)")

    def count_window(sheet_name: str, start: str, end: str,
                     extra: Sequence[Tuple[str, str]] = ()) -> str:
        pairs = [f"{other(sheet_name, 'date')},\">=\"&{start}",
                 f"{other(sheet_name, 'date')},\"<=\"&{end}"]
        pairs += [f"{rng},{crit}" for rng, crit in extra]
        return ("IFERROR(COUNTIFS(" + ",".join(pairs) + "),0)")

    def table(row: int, headers: Sequence[Tuple[str, int]]) -> int:
        sheet.row_height(row, 24)
        col = 1
        for head, span in headers:
            sheet.merge(row, col, col + span - 1, head,
                        fmts.chrome("header_left"))
            col += span
        return row + 1

    r = sheet.note(3, HELP, last_col, height=26)

    # ------------------------------------------------------------ year in brief
    r = sheet.section(r, f"The year in brief - {cfg.year}", last_col)
    year_revenue = window("Sales", "gross", "YearStart", "YearEnd")
    year_profit = window("Sales", "profit", "YearStart", "YearEnd")
    year_units = window("Sales", "qty", "YearStart", "YearEnd")
    year_minutes = window("Sales", "minutes_total", "YearStart", "YearEnd")
    year_cogs = window("Sales", "cost", "YearStart", "YearEnd")
    year_fees = window("Sales", "fees", "YearStart", "YearEnd")
    year_waste = window("Waste Log", "cost", "YearStart", "YearEnd")
    year_orders = count_window("Sales", "YearStart", "YearEnd")
    tiles = [
        ("Revenue", year_revenue, "money0"),
        ("Cost of goods", year_cogs, "money0"),
        ("Fees", year_fees, "money0"),
        ("Profit", year_profit, "money0"),
        ("Margin", f"IF({year_revenue}=0,\"\",{year_profit}/{year_revenue})",
         "percent"),
        ("Units", year_units, "int"),
        ("Orders", year_orders, "int"),
        ("Waste", year_waste, "money0"),
        ("Hourly earned",
         f"IF({year_minutes}=0,0,{year_profit}/({year_minutes}/60))",
         "money"),
    ]
    for i, (label, formula, style) in enumerate(tiles):
        if i and i % 5 == 0:
            r += 3
        sheet.kpi(r, 1 + (i % 5) * 3, label, x(formula), style=style,
                  span=3, note="")
    r += 4

    # ----------------------------------------------------------- month by month
    r = sheet.section(r, "Month by month", last_col)
    r = table(r, [("Month", 2), ("Orders", 1), ("Units", 1), ("Revenue", 2),
                  ("Cost of goods", 2), ("Fees", 2), ("Profit", 2),
                  ("Margin", 2), ("Waste", 2), ("Labour hours", 1)])
    for month in range(1, 13):
        start = f"DATE(ReportYear,{month},1)"
        end = f"EOMONTH(DATE(ReportYear,{month},1),0)"
        revenue = window("Sales", "gross", start, end)
        profit = window("Sales", "profit", start, end)
        sheet.row_height(r, 17)
        put_text(r, 1, "", "text", span=2)
        sheet.ws.write_formula(r, 1, f'=TEXT({start},"mmm")',
                               fmts.cell("text", "plain"))
        put(r, 3, count_window("Sales", start, end), "int")
        put(r, 4, window("Sales", "qty", start, end), "int")
        put(r, 5, revenue, "money", span=2)
        put(r, 7, window("Sales", "cost", start, end), "money", span=2)
        put(r, 9, window("Sales", "fees", start, end), "money", span=2)
        put(r, 11, profit, "money", span=2)
        put(r, 13, f'IF({revenue}=0,"",{profit}/{revenue})', "percent",
            span=2)
        put(r, 15, window("Waste Log", "cost", start, end), "money", span=2)
        put(r, 17, window("Labor", "hours", start, end), "number")
        r += 1
    sheet.row_height(r, 18)
    put_text(r, 1, "Year", "status", span=2)
    put(r, 3, year_orders, "int")
    put(r, 4, year_units, "int")
    put(r, 5, year_revenue, "money", span=2)
    put(r, 7, year_cogs, "money", span=2)
    put(r, 9, year_fees, "money", span=2)
    put(r, 11, year_profit, "money", span=2)
    put(r, 13, f'IF({year_revenue}=0,"",{year_profit}/{year_revenue})',
        "percent", span=2)
    put(r, 15, year_waste, "money", span=2)
    put(r, 17, window("Labor", "hours", "YearStart", "YearEnd"), "number")
    r += 2

    # --------------------------------------------------------------- by category
    r = sheet.section(r, "By category", last_col)
    r = table(r, [("Category", 4), ("Products", 1), ("Units", 1),
                  ("Revenue", 2), ("Cost of goods", 2), ("Profit", 2),
                  ("Margin", 2), ("Average price", 2)])
    for category in PRODUCT_CATEGORIES:
        # Sales carries a hidden `category` column, so these are plain SUMIFS
        cat = (other("Sales", "category"), f'"{category}"')
        rev = window("Sales", "gross", "YearStart", "YearEnd", [cat])
        prof = window("Sales", "profit", "YearStart", "YearEnd", [cat])
        units = window("Sales", "qty", "YearStart", "YearEnd", [cat])
        cogs = window("Sales", "cost", "YearStart", "YearEnd", [cat])
        products = (f"IFERROR(COUNTIFS({other('Products', 'category')},"
                    f"\"{category}\"),0)")
        sheet.row_height(r, 17)
        put_text(r, 1, category, "text", span=4)
        put(r, 5, products, "int")
        put(r, 6, units, "int")
        put(r, 7, rev, "money", span=2)
        put(r, 9, cogs, "money", span=2)
        put(r, 11, prof, "money", span=2)
        put(r, 13, f'IF({rev}=0,"",{prof}/{rev})', "percent", span=2)
        put(r, 15, f'IF({units}=0,"",{rev}/{units})', "money", span=2)
        r += 1
    r += 1

    # ----------------------------------------------------------- by channel/craft
    r = sheet.section(r, "By channel and by craft", last_col)
    r = table(r, [("Channel", 3), ("Orders", 1), ("Revenue", 2), ("Fees", 2),
                  ("Profit", 2), ("Margin", 2), ("Craft", 2), ("Units", 1),
                  ("Revenue", 2)])
    for n in range(1, 7):
        chan = f"IFERROR(INDEX({other('Channels', 'name')},{n}),\"\")"
        orders = (f"IFERROR(COUNTIFS({other('Sales', 'channel')},{chan},"
                  f"{other('Sales', 'date')},\">=\"&YearStart,"
                  f"{other('Sales', 'date')},\"<=\"&YearEnd),0)")
        revenue = window("Sales", "gross", "YearStart", "YearEnd",
                         [(other("Sales", "channel"), chan)])
        fees = window("Sales", "fees", "YearStart", "YearEnd",
                      [(other("Sales", "channel"), chan)])
        profit = window("Sales", "profit", "YearStart", "YearEnd",
                        [(other("Sales", "channel"), chan)])
        sheet.row_height(r, 17)
        put_text(r, 1, "", "text", span=3)
        sheet.ws.write_formula(r, 1, f'=IFERROR({chan},"")',
                               fmts.cell("text", "plain"))
        put(r, 4, orders, "int")
        put(r, 5, revenue, "money", span=2)
        put(r, 7, fees, "money", span=2)
        put(r, 9, profit, "money", span=2)
        put(r, 11, f'IF({revenue}=0,"",{profit}/{revenue})', "percent",
            span=2)
        if n <= len(CRAFT_LIST):
            craft = CRAFT_LIST[n - 1]
            c_units = window("Sales", "qty", "YearStart", "YearEnd",
                             [(other("Sales", "craft"), f'"{craft}"')])
            c_revenue = window("Sales", "gross", "YearStart", "YearEnd",
                               [(other("Sales", "craft"), f'"{craft}"')])
            put_text(r, 13, craft, "text", span=2)
            put(r, 15, c_units, "int")
            put(r, 16, c_revenue, "money", span=2)
        r += 1
    r += 1

    # ------------------------------------------------------------- top and worst
    r = sheet.section(r, "The catalog ranked", last_col)
    product_count = f'COUNTIF({other("Products", "id")},"?*")'
    book.define_name("RepProductCount", f"={reg.render(product_count)}")
    r = table(r, [("#", 1), ("Most revenue", 4), ("Revenue", 2),
                  ("Most profit", 4), ("Profit", 2),
                  ("Worst margin", 4)])
    for n in range(1, 11):
        by_revenue = (f'IFERROR(INDEX({other("Products", "name")},'
                      f'MATCH({n},{other("Products", "rank_revenue")},0)),"")')
        rev_value = (f'IFERROR(INDEX({other("Products", "revenue")},'
                     f'MATCH({n},{other("Products", "rank_revenue")},0)),"")')
        by_profit = (f'IFERROR(INDEX({other("Products", "name")},'
                     f'MATCH({n},{other("Products", "rank_profit")},0)),"")')
        profit_value = (f'IFERROR(INDEX({other("Products", "gross_profit")},'
                        f'MATCH({n},{other("Products", "rank_profit")},0)),"")')
        worst = (f'IFERROR(INDEX({other("Products", "name")},'
                 f'MATCH(RepProductCount-{n - 1},'
                 f'{other("Products", "rank_margin")},0)),"")')
        worst_margin = (f'IFERROR(INDEX({other("Products", "margin")},'
                        f'MATCH(RepProductCount-{n - 1},'
                        f'{other("Products", "rank_margin")},0)),"")')
        sheet.row_height(r, 17)
        put_text(r, 1, n, "int")
        put_text(r, 2, "", "text", span=4)
        sheet.ws.write_formula(r, 2, x(by_revenue), fmts.cell("text", "plain"))
        put(r, 6, rev_value, "money", span=2)
        put_text(r, 8, "", "text", span=4)
        sheet.ws.write_formula(r, 8, x(by_profit), fmts.cell("text", "plain"))
        put(r, 12, profit_value, "money", span=2)
        put_text(r, 14, "", "text", span=2)
        sheet.ws.write_formula(r, 14, x(worst), fmts.cell("text", "plain"))
        put(r, 16, worst_margin, "percent", span=2)
        r += 1
    r += 1

    # ------------------------------------------------- stock, trade, promotions
    r = sheet.section(r, "Stock, trade, promotions, events and labour",
                      last_col)
    blocks: List[Tuple[str, List[Tuple[str, str, str]]]] = [
        ("Stock and purchasing", [
            ("Materials listed", f'COUNTIF({other("Materials", "id")},"?*")',
             "int"),
            ("Value of the stock",
             f'IFERROR(SUM({other("Materials", "stock_value")}),0)', "money"),
            ("Lines to re-order",
             f'IFERROR(COUNTIFS({other("Materials", "stock_flag")},"REORDER")'
             f'+COUNTIFS({other("Materials", "stock_flag")},"ORDER NOW"),0)',
             "int"),
            ("Cost of an order run",
             f'IFERROR(SUMIF({other("Materials", "stock_flag")},"REORDER",'
             f'{other("Materials", "order_cost")}),0)', "money"),
            ("Waste this year", year_waste, "money"),
            ("Waste against materials used",
             f'IFERROR({year_waste}/'
             f'(SUM({other("Materials", "used_cost")})+{year_waste}),"")',
             "percent"),
        ]),
        ("Wholesale", [
            ("Shops on the books",
             f'COUNTIF({other("Wholesale Customers", "id")},"?*")', "int"),
            ("Orders this year",
             f'IFERROR(SUMPRODUCT(({other("Wholesale Orders", "date")}>=YearStart)'
             f'*({other("Wholesale Orders", "date")}<=YearEnd)),0)', "int"),
            ("Trade value this year",
             f'IFERROR(SUMPRODUCT(({other("Wholesale Orders", "date")}>=YearStart)'
             f'*({other("Wholesale Orders", "date")}<=YearEnd)'
             f'*({other("Wholesale Orders", "wholesale_total")})),0)', "money"),
            ("Profit on trade this year",
             f'IFERROR(SUMPRODUCT(({other("Wholesale Orders", "date")}>=YearStart)'
             f'*({other("Wholesale Orders", "date")}<=YearEnd)'
             f'*({other("Wholesale Orders", "profit")})),0)', "money"),
            ("Outstanding now",
             f'IFERROR(SUM({other("Wholesale Orders", "balance_outstanding")}),0)',
             "money"),
            ("Overdue now",
             f'IFERROR(SUMIFS({other("Wholesale Orders", "balance_outstanding")},'
             f'{other("Wholesale Orders", "aging_flag")},"OVERDUE"),0)',
             "money"),
        ]),
        ("Promotions", [
            ("Offers live now",
             f'IFERROR(COUNTIFS({other("Promotions", "state")},"LIVE"),0)',
             "int"),
            ("Redemptions",
             f'IFERROR(SUM({other("Promotions", "redemptions")}),0)', "int"),
            ("Revenue with a code",
             f'IFERROR(SUM({other("Promotions", "revenue_with_promo")}),0)',
             "money"),
            ("Discount given away",
             f'IFERROR(SUM({other("Promotions", "discount_given")}),0)',
             "money"),
            ("Profit on those orders",
             f'IFERROR(SUM({other("Promotions", "profit_with_promo")}),0)',
             "money"),
        ]),
        ("Events", [
            ("Events this year",
             f'IFERROR(SUMPRODUCT(({other("Events", "date")}>=YearStart)'
             f'*({other("Events", "date")}<=YearEnd)),0)', "int"),
            ("Revenue at events",
             f'IFERROR(SUMPRODUCT(({other("Events", "date")}>=YearStart)'
             f'*({other("Events", "date")}<=YearEnd)'
             f'*({other("Events", "revenue")})),0)', "money"),
            ("Cost of events",
             f'IFERROR(SUMPRODUCT(({other("Events", "date")}>=YearStart)'
             f'*({other("Events", "date")}<=YearEnd)'
             f'*({other("Events", "total_cost")})),0)', "money"),
            ("Profit at events",
             f'IFERROR(SUMPRODUCT(({other("Events", "date")}>=YearStart)'
             f'*({other("Events", "date")}<=YearEnd)'
             f'*({other("Events", "profit")})),0)', "money"),
            ("Hours on the road",
             f'IFERROR(SUMPRODUCT(({other("Events", "date")}>=YearStart)'
             f'*({other("Events", "date")}<=YearEnd)'
             f'*({other("Events", "total_hours")})),0)', "number"),
        ]),
        ("Labour", [
            ("Hours recorded",
             f'IFERROR(SUM({other("Labor", "hours")}),0)', "number"),
            ("Cost of those hours",
             f'IFERROR(SUM({other("Labor", "loaded_cost")}),0)', "money"),
            ("Hours on products",
             f'IFERROR(SUMIFS({other("Labor", "hours")},'
             f'{other("Labor", "is_production")},"Yes"),0)', "number"),
            ("Shop time cost",
             f'IFERROR(SUM({other("Labor", "overhead_share")}),0)', "money"),
            ("Below the minimum wage",
             f'IFERROR(COUNTIFS({other("Labor", "rate_check")},'
             f'"BELOW MIN WAGE"),0)', "int"),
        ]),
    ]
    for title, items in blocks:
        r = sheet.subsection(r, title, last_col)
        for i, (label, formula, style) in enumerate(items):
            col = 1 + (i % 3) * 6
            if i % 3 == 0:
                sheet.row_height(r, 20)
            sheet.merge(r, col, col + 3, label, fmts.chrome("label"))
            put(r, col + 4, formula, style, span=2)
            if i % 3 == 2:
                r += 1
        if len(items) % 3:
            r += 1
        r += 1

    r = sheet.note(
        r,
        "Every figure on this page comes from a register - nothing is typed "
        "here, so nothing can drift out of date. Print it landscape on one "
        "page wide; it is laid out for that.",
        last_col, height=30)

    sheet.ws.freeze_panes(4, 3)
    sheet.ws.print_area(0, 0, r, last_col)
    sheet.ws.fit_to_pages(1, 0)
    sheet.protect()
    return sheet
