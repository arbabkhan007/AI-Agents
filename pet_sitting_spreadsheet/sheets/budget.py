"""`Budget` - targets, budget vs actual, break-even, forecast and cash flow."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry, col_letter, quote_sheet
from ..sample_data import get as sample
from ..writer import SheetWriter, date_check, number_check

NAME = "Budget"
LAST_COL = 12
FIRST_CALC_ROW = 5
DRAW_ROWS = 24


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.good_text)
    ws = s.ws

    s.banner("Financial Planning & Profitability",
             "Set the targets, then watch budget against actual month by "
             "month. Break-even, forecast, cash flow and tax reserve are "
             "all worked out for you.",
             LAST_COL)

    s.set_col(0, 0, 26)
    s.set_col(1, 12, 13)

    def metric(row, col, label, value=None, formula=None, style="money",
               mode="calc", name=None, validate=None, span=1):
        s.merge(row, col, col + span - 1, label, fmts.chrome("label"))
        target_col = col + span
        fmt = fmts.calc(style) if mode == "calc" else fmts.input(style)
        if formula:
            ws.write_formula(row, target_col, reg.render(formula), fmt)
        else:
            s.write(row, target_col, value, fmt)
        if validate:
            ws.data_validation(row, target_col, row, target_col, validate)
        if name:
            book.define_name(
                name, f"={quote_sheet(NAME)}!"
                      f"${col_letter(target_col)}${row + 1}")
        return row + 1

    # ----------------------------------------------------------- targets
    row = 4
    row = s.section(row, "1. Targets for the dashboard year", LAST_COL)
    row = metric(row, 0, "Annual revenue target", 48000, style="money",
                 mode="input", name="Target_Revenue",
                 validate=number_check(0, 100000000))
    row = metric(row, 0, "Annual expense budget", 19000, style="money",
                 mode="input", name="Target_Expenses",
                 validate=number_check(0, 100000000))
    row = metric(row, 0, "Target profit",
                 formula="=Target_Revenue-Target_Expenses")
    row = metric(row, 0, "Target profit margin",
                 formula="=IFERROR((Target_Revenue-Target_Expenses)"
                         "/Target_Revenue,0)", style="percent")
    row = metric(row, 0, "Fixed costs per month", 650, style="money",
                 mode="input", name="FixedCosts",
                 validate=number_check(0, 1000000))
    row = metric(row, 0, "Average gross margin",
                 formula='=IFERROR(1-SUMIFS([[Services.staff_cost]],'
                         '[[Services.active]],"Yes")'
                         '/SUMIFS([[Services.rate]],[[Services.active]],'
                         '"Yes"),0.5)', style="percent")
    margin_row = row
    row = metric(row, 0, "Break-even revenue per month",
                 formula=f"=IFERROR(FixedCosts/B{margin_row},0)")
    row = metric(row, 0, "Break-even bookings per month",
                 formula=f'=IFERROR(B{margin_row + 1}'
                         f'/IFERROR(AVERAGEIF([[Bookings.total]],">0"),1),0)',
                 style="int")
    row = metric(row, 0, "Growth assumption for forecast", 0.05,
                 style="percent", mode="input", name="GrowthRate",
                 validate=number_check(-1, 5))
    row += 1

    # --------------------------------------------- budget versus actual --
    row = s.section(row, "2. Monthly budget vs actual", LAST_COL)
    headers = ["Month", "Revenue target", "Revenue actual", "Variance",
               "Achieved", "Expense budget", "Expense actual", "Variance",
               "Profit", "Margin", "Cumulative profit", "Forecast revenue"]
    row = s.table_head(row, 0, headers)
    first = row
    for i in range(12):
        r = first + i
        c = FIRST_CALC_ROW + i
        excel_row = r + 1
        prev = excel_row - 1
        ws.write_formula(r, 0, reg.render(f'=[[Calc.m_label#{c}]]'),
                         fmts.calc("text"))
        ws.write_formula(r, 1, "=ROUND(Target_Revenue/12,2)",
                         fmts.calc("money"))
        ws.write_formula(r, 2, reg.render(f'=[[Calc.m_rev#{c}]]'),
                         fmts.calc("money"))
        ws.write_formula(r, 3, f"=C{excel_row}-B{excel_row}",
                         fmts.calc("money"))
        ws.write_formula(r, 4, f'=IFERROR(C{excel_row}/B{excel_row},"")',
                         fmts.calc("percent"))
        ws.write_formula(r, 5, "=ROUND(Target_Expenses/12,2)",
                         fmts.calc("money"))
        ws.write_formula(r, 6, reg.render(f'=[[Calc.m_exp#{c}]]'),
                         fmts.calc("money"))
        ws.write_formula(r, 7, f"=F{excel_row}-G{excel_row}",
                         fmts.calc("money"))
        ws.write_formula(r, 8, f"=C{excel_row}-G{excel_row}",
                         fmts.calc("money"))
        ws.write_formula(r, 9, f'=IFERROR(I{excel_row}/C{excel_row},"")',
                         fmts.calc("percent"))
        ws.write_formula(
            r, 10,
            f"=I{excel_row}" if i == 0 else f"=K{prev}+I{excel_row}",
            fmts.calc("money"))
        ws.write_formula(
            r, 11,
            f'=IFERROR(ROUND(AVERAGE(C{first + 1}:C{excel_row})'
            f'*(1+GrowthRate),2),0)', fmts.calc("money"))

    last = first + 11
    total_row = last + 1
    s.write(total_row, 0, "Year", fmts.chrome("total_label"))
    for idx, style in enumerate(
            ["money", "money", "money", "percent", "money", "money",
             "money", "money", "percent", "money", "money"], start=1):
        letter = col_letter(idx)
        fmt = fmts.chrome("total_value", num_format=s.num_format(style))
        if idx == 4:
            ws.write_formula(total_row, idx,
                             f'=IFERROR(C{total_row + 1}/B{total_row + 1},"")',
                             fmt)
        elif idx == 9:
            ws.write_formula(total_row, idx,
                             f'=IFERROR(I{total_row + 1}/C{total_row + 1},"")',
                             fmt)
        elif idx == 10:
            ws.write_formula(total_row, idx, f"=K{last + 1}", fmt)
        else:
            ws.write_formula(total_row, idx,
                             f"=SUM({letter}{first + 1}:{letter}{last + 1})",
                             fmt)
    for col_idx, colour in ((2, "#6366F1"), (6, "#F43F5E"), (8, "#4338CA")):
        letter = col_letter(col_idx)
        try:
            ws.add_sparkline(total_row + 1, col_idx, {
                "range": (f"{quote_sheet(NAME)}!{letter}{first + 1}:"
                          f"{letter}{last + 1}"),
                "type": "column", "series_color": colour})
        except Exception:        # pragma: no cover
            pass
    s.write(total_row + 1, 0, "Trend", fmts.chrome("label_bold"))
    row = total_row + 3

    # ------------------------------------------------- real chart ----------
    # Budget versus actual revenue and expenses, month by month.
    chart_row = row
    money_fmt = f'{cfg.currency_symbol}#,##0'
    chart = book.add_chart({"type": "column"})
    chart.add_series({
        "name": "Revenue target",
        "categories": [NAME, first, 0, last, 0],
        "values": [NAME, first, 1, last, 1],
        "fill": {"color": Palette.primary_soft},
        "border": {"color": Palette.primary_mid},
        "gap": 60,
    })
    chart.add_series({
        "name": "Revenue actual",
        "categories": [NAME, first, 0, last, 0],
        "values": [NAME, first, 2, last, 2],
        "fill": {"color": Palette.primary_mid},
        "border": {"none": True},
    })
    chart.add_series({
        "name": "Expense budget",
        "categories": [NAME, first, 0, last, 0],
        "values": [NAME, first, 5, last, 5],
        "fill": {"color": Palette.accent_soft},
        "border": {"color": Palette.accent},
    })
    chart.add_series({
        "name": "Expense actual",
        "categories": [NAME, first, 0, last, 0],
        "values": [NAME, first, 6, last, 6],
        "fill": {"color": "#F43F5E"},
        "border": {"none": True},
    })
    chart.set_title({"name": "Budget versus actual, month by month",
                     "name_font": {"size": 12, "bold": True,
                                   "color": Palette.ink}})
    chart.set_x_axis({"num_font": {"size": 9, "color": Palette.grey_text},
                      "line": {"color": Palette.line}})
    chart.set_y_axis({"num_format": money_fmt,
                      "num_font": {"size": 9, "color": Palette.grey_text},
                      "major_gridlines": {"visible": True,
                                          "line": {"color": Palette.line}}})
    chart.set_legend({"position": "bottom",
                      "font": {"size": 9, "color": Palette.grey_text}})
    chart.set_chartarea({"border": {"color": Palette.line},
                         "fill": {"color": Palette.white}})
    chart.set_plotarea({"fill": {"color": Palette.white}})
    ws.insert_chart(chart_row, 0, chart, {"x_scale": 1.6, "y_scale": 1.3})
    row = chart_row + 21

    # ------------------------------------------------------- cash summary
    row = s.section(row, "3. Cash flow & owner money", LAST_COL)
    left = row
    left = metric(left, 0, "Opening cash balance", 1200, style="money",
                  mode="input", name="OpeningCash",
                  validate=number_check(-1000000, 10000000))
    left = metric(left, 0, "Cash in (payments received)",
                  formula='=SUMIFS([[Payments.received]],[[Payments.date]],'
                          '">="&DATE(Dash_Year,1,1),[[Payments.date]],'
                          '"<="&DATE(Dash_Year,12,31))')
    left = metric(left, 0, "Cash out (expenses paid)",
                  formula='=SUMIFS([[Expenses.amount]],[[Expenses.date]],'
                          '">="&DATE(Dash_Year,1,1),[[Expenses.date]],'
                          '"<="&DATE(Dash_Year,12,31))')
    left = metric(left, 0, "Owner withdrawals",
                  formula=f"=SUM(K{row + 3}:K{row + 2 + DRAW_ROWS})")
    left = metric(left, 0, "Closing cash balance",
                  formula=f"=B{row + 1}+B{row + 2}-B{row + 3}-B{row + 4}")
    left = metric(left, 0, "Money to set aside for tax",
                  formula='=MAX(0,SUMIFS([[Payments.received]],'
                          '[[Payments.date]],">="&DATE(Dash_Year,1,1),'
                          '[[Payments.date]],"<="&DATE(Dash_Year,12,31))'
                          '-SUMIFS([[Expenses.amount]],[[Expenses.date]],'
                          '">="&DATE(Dash_Year,1,1),[[Expenses.date]],'
                          '"<="&DATE(Dash_Year,12,31)))*TaxReservePct')
    left = metric(left, 0, "Business savings target", 2500, style="money",
                  mode="input", name="SavingsTarget",
                  validate=number_check(0, 10000000))
    left = metric(left, 0, "Savings set aside so far", 900, style="money",
                  mode="input", name="SavingsActual",
                  validate=number_check(0, 10000000))
    left = metric(left, 0, "Savings progress",
                  formula="=IFERROR(SavingsActual/SavingsTarget,0)",
                  style="percent")

    # Owner drawings register (right hand side).
    s.merge(row, 9, 12, "Owner withdrawals register",
            fmts.chrome("subsection"))
    s.table_head(row + 1, 9, ["Date", "Amount", "Notes", ""])
    draws = sample(cfg).drawings if cfg.include_sample_data else []
    for i in range(DRAW_ROWS):
        r = row + 2 + i
        date_fmt = fmts.input("date")
        money_fmt = fmts.input("money")
        text_fmt = fmts.input("text")
        if i < len(draws):
            s.write(r, 9, draws[i]["date"], date_fmt)
            s.write(r, 10, draws[i]["amount"], money_fmt)
            s.write(r, 11, draws[i]["notes"], text_fmt)
        else:
            ws.write_blank(r, 9, None, date_fmt)
            ws.write_blank(r, 10, None, money_fmt)
            ws.write_blank(r, 11, None, text_fmt)
        ws.write_blank(r, 12, None, text_fmt)
    ws.data_validation(row + 2, 9, row + 1 + DRAW_ROWS, 9, date_check())
    ws.data_validation(row + 2, 10, row + 1 + DRAW_ROWS, 10,
                       number_check(0, 1000000))
    row = max(left, row + 2 + DRAW_ROWS) + 1

    # -------------------------------------------------- year on year block
    row = s.section(row, "4. Year on year comparison", LAST_COL)
    row = s.table_head(row, 0, ["Measure", "This year", "Last year",
                                "Change", "Change %", "", "", "", "", "",
                                "", "", ""])
    yoy = [
        ("Revenue collected",
         '=SUMIFS([[Payments.received]],[[Payments.date]],'
         '">="&DATE(Dash_Year,1,1),[[Payments.date]],'
         '"<="&DATE(Dash_Year,12,31))',
         '=SUMIFS([[Payments.received]],[[Payments.date]],'
         '">="&DATE(Dash_Year-1,1,1),[[Payments.date]],'
         '"<="&DATE(Dash_Year-1,12,31))', "money"),
        ("Expenses",
         '=SUMIFS([[Expenses.amount]],[[Expenses.date]],'
         '">="&DATE(Dash_Year,1,1),[[Expenses.date]],'
         '"<="&DATE(Dash_Year,12,31),[[Expenses.type]],"<>Personal")',
         '=SUMIFS([[Expenses.amount]],[[Expenses.date]],'
         '">="&DATE(Dash_Year-1,1,1),[[Expenses.date]],'
         '"<="&DATE(Dash_Year-1,12,31),[[Expenses.type]],"<>Personal")',
         "money"),
        ("Bookings",
         '=COUNTIFS([[Bookings.date]],">="&DATE(Dash_Year,1,1),'
         '[[Bookings.date]],"<="&DATE(Dash_Year,12,31),'
         '[[Bookings.status]],"<>Cancelled")',
         '=COUNTIFS([[Bookings.date]],">="&DATE(Dash_Year-1,1,1),'
         '[[Bookings.date]],"<="&DATE(Dash_Year-1,12,31),'
         '[[Bookings.status]],"<>Cancelled")', "int"),
        ("New clients",
         '=COUNTIFS([[Clients.reg_date]],">="&DATE(Dash_Year,1,1),'
         '[[Clients.reg_date]],"<="&DATE(Dash_Year,12,31))',
         '=COUNTIFS([[Clients.reg_date]],">="&DATE(Dash_Year-1,1,1),'
         '[[Clients.reg_date]],"<="&DATE(Dash_Year-1,12,31))', "int"),
        ("Business distance",
         '=SUMIFS([[Mileage.total_km]],[[Mileage.date]],'
         '">="&DATE(Dash_Year,1,1),[[Mileage.date]],'
         '"<="&DATE(Dash_Year,12,31),[[Mileage.business]],"Business")',
         '=SUMIFS([[Mileage.total_km]],[[Mileage.date]],'
         '">="&DATE(Dash_Year-1,1,1),[[Mileage.date]],'
         '"<="&DATE(Dash_Year-1,12,31),[[Mileage.business]],"Business")',
         "number1"),
    ]
    for i, (label, this_year, last_year, style) in enumerate(yoy):
        r = row + i
        excel_row = r + 1
        s.calc_row(r, 0, [label, this_year, last_year,
                          f"=B{excel_row}-C{excel_row}",
                          f'=IFERROR(B{excel_row}/C{excel_row}-1,"")'],
                   ["text", style, style, style, "percent"])
    row += len(yoy) + 1

    s.note(row,
           "How the forecast works: it averages the actual revenue "
           "recorded so far this year and adds your growth assumption. "
           "Update the growth rate as the year unfolds.",
           LAST_COL, height=24)

    s.finish(freeze_row=4, gridlines=False, fit_width=True,
             print_area=f"A1:{col_letter(LAST_COL)}{row + 2}")
    return s
