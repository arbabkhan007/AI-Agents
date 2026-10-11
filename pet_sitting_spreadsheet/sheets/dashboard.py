"""`Dashboard` - the one page view of the business."""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry, col_letter, quote_sheet
from ..writer import SheetWriter, list_from, number_check

NAME = "Dashboard"
LAST_COL = 17            # column R - six KPI tiles of three columns each
MONTH_ROWS = 12
FIRST_CALC_ROW = 5       # Calc sheet data starts on row 5


def _period(field_sheet: str, field: str) -> str:
    return (f'[[{field_sheet}.{field}]],">="&PeriodStart,'
            f'[[{field_sheet}.{field}]],"<="&PeriodEnd')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.ink)
    ws = s.ws

    s.banner("Business Dashboard",
             "Pick a period, then read the business at a glance. Every "
             "number is live - it updates as you fill in the other tabs.",
             LAST_COL)

    for c in range(0, LAST_COL + 1):
        s.set_col(c, c, 12.5)

    # ------------------------------------------------------ period picker
    row = 4
    row = s.section(row, "Reporting period", LAST_COL)
    s.merge(row, 0, 1, "Year", fmts.chrome("label_bold"))
    s.write(row, 2, cfg.today.year, fmts.input("int"))
    ws.data_validation(row, 2, row, 2, number_check(2000, 2100, False))
    book.define_name("Dash_Year",
                     f"={quote_sheet(NAME)}!$C${row + 1}")

    s.merge(row, 3, 4, "Month", fmts.chrome("label_bold"))
    # Opens on the whole year so the first screen is full of numbers;
    # pick a month from the drop down to narrow everything down.
    s.merge(row, 5, 6, "All year", fmts.input("text"))
    ws.data_validation(row, 5, row, 5, list_from("MonthList"))
    book.define_name("Dash_MonthName",
                     f"={quote_sheet(NAME)}!$F${row + 1}")

    s.merge(row, 7, 8, "Period start", fmts.chrome("label_bold"))
    s.merge(row, 9, 10, None, fmts.calc("date"))
    ws.write_formula(
        row, 9,
        '=IF(Dash_MonthName="All year",DATE(Dash_Year,1,1),'
        'DATE(Dash_Year,MAX(1,MATCH(Dash_MonthName,MonthList,0)-1),1))',
        fmts.calc("date"))
    book.define_name("PeriodStart", f"={quote_sheet(NAME)}!$J${row + 1}")

    s.merge(row, 11, 12, "Period end", fmts.chrome("label_bold"))
    s.merge(row, 13, 14, None, fmts.calc("date"))
    ws.write_formula(
        row, 13,
        '=IF(Dash_MonthName="All year",DATE(Dash_Year,12,31),'
        'EOMONTH(PeriodStart,0))', fmts.calc("date"))
    book.define_name("PeriodEnd", f"={quote_sheet(NAME)}!$N${row + 1}")

    s.merge(row, 15, 16, "Today", fmts.chrome("label_bold"))
    s.write(row, 17, "=TODAY()", fmts.calc("date"))
    row += 2

    # ------------------------------------------------------- money tiles --
    row = s.section(row, "Money", LAST_COL)
    revenue = ('=SUMIFS([[Payments.received]],'
               + _period("Payments", "date") + ')')
    invoiced = ('=SUMIFS([[Invoices.total]],' + _period("Invoices", "date")
                + ',[[Invoices.status]],"<>Cancelled")')
    expenses = ('=SUMIFS([[Expenses.amount]],' + _period("Expenses", "date")
                + ',[[Expenses.type]],"<>Personal")')

    s.kpi(row, 0, "Revenue collected", revenue, "money", 3,
          "Payments received in the period")
    book.define_name("Dash_Revenue", f"={quote_sheet(NAME)}!$A${row + 2}")
    s.kpi(row, 3, "Invoiced", invoiced, "money", 3,
          "Value of invoices raised")
    s.kpi(row, 6, "Outstanding", '=SUMIFS([[Invoices.balance]],'
                                 '[[Invoices.status]],"<>Cancelled")',
          "money", 3, "Unpaid balance, all invoices")
    s.kpi(row, 9, "Overdue", '=SUMIFS([[Invoices.balance]],'
                             '[[Invoices.pay_status]],"Overdue")'
                             '+SUMIFS([[Invoices.balance]],'
                             '[[Invoices.pay_status]],"Overdue - part paid")',
          "money", 3, "Past the due date - chase today")
    s.kpi(row, 12, "Expenses", expenses, "money", 3,
          "Business costs in the period")
    book.define_name("Dash_Expenses", f"={quote_sheet(NAME)}!$M${row + 2}")
    s.kpi(row, 15, "Net profit", "=Dash_Revenue-Dash_Expenses", "money", 3,
          "Revenue collected less expenses")
    book.define_name("Dash_Profit", f"={quote_sheet(NAME)}!$P${row + 2}")
    row += 3

    s.kpi(row, 0, "Profit margin",
          '=IFERROR(Dash_Profit/Dash_Revenue,0)', "percent", 3,
          "Net profit as a share of revenue")
    s.kpi(row, 3, "Average booking value",
          '=IFERROR(SUMIFS([[Bookings.total]],'
          + _period("Bookings", "date")
          + ',[[Bookings.status]],"<>Cancelled")/COUNTIFS('
          + _period("Bookings", "date")
          + ',[[Bookings.status]],"<>Cancelled"),0)', "money", 3,
          "Booked value per job")
    s.kpi(row, 6, "Revenue per active client",
          '=IFERROR(Dash_Revenue/COUNTIF([[Clients.status]],"Active"),0)',
          "money", 3, "Period revenue / active clients")
    s.kpi(row, 9, "Mileage claim",
          '=SUMIFS([[Mileage.claimable]],' + _period("Mileage", "date") + ')',
          "money", 3, "Travel you can claim back")
    s.kpi(row, 12, "Tax to set aside",
          '=MAX(0,Dash_Profit)*TaxReservePct', "money", 3,
          "Profit x tax reserve % from Settings")
    s.kpi(row, 15, "Cash collected per visit",
          '=IFERROR(Dash_Revenue/COUNTIFS(' + _period("Visit Log", "date")
          + ',[[Visit Log.status]],"Completed"),0)', "money", 3,
          "Revenue / completed visits")
    row += 4

    # -------------------------------------------------- operations tiles --
    row = s.section(row, "Bookings, visits & clients", LAST_COL)
    s.kpi(row, 0, "Bookings in period",
          '=COUNTIFS(' + _period("Bookings", "date")
          + ',[[Bookings.status]],"<>Cancelled")', "int", 3,
          "Excludes cancellations")
    s.kpi(row, 3, "Completed",
          '=COUNTIFS(' + _period("Bookings", "date")
          + ',[[Bookings.status]],"Completed")', "int", 3,
          "Jobs delivered")
    s.kpi(row, 6, "Cancelled",
          '=COUNTIFS(' + _period("Bookings", "date")
          + ',[[Bookings.status]],"Cancelled")', "int", 3,
          "Watch the cancellation rate")
    s.kpi(row, 9, "Upcoming (7 days)",
          '=COUNTIFS([[Bookings.date]],">="&TODAY(),[[Bookings.date]],'
          '"<="&TODAY()+7,[[Bookings.status]],"<>Cancelled")', "int", 3,
          "Next seven days")
    s.kpi(row, 12, "Visits completed",
          '=COUNTIFS(' + _period("Visit Log", "date")
          + ',[[Visit Log.status]],"Completed")', "int", 3,
          "Logged in the Visit Log")
    s.kpi(row, 15, "Missed visits",
          '=COUNTIFS(' + _period("Visit Log", "date")
          + ',[[Visit Log.status]],"Missed")', "int", 3,
          "Investigate every one")
    row += 3

    s.kpi(row, 0, "Active clients",
          '=COUNTIF([[Clients.status]],"Active")', "int", 3,
          "Clients marked Active")
    s.kpi(row, 3, "Pets on the books",
          '=COUNTIF([[Pets.name]],"?*")', "int", 3,
          "All registered pets")
    s.kpi(row, 6, "New clients",
          '=COUNTIFS(' + _period("Clients", "reg_date") + ')', "int", 3,
          "Registered in the period")
    s.kpi(row, 9, "Repeat clients",
          '=COUNTIF([[Clients.bookings]],">1")', "int", 3,
          "More than one booking")
    s.kpi(row, 12, "Unconfirmed bookings",
          '=COUNTIFS([[Bookings.date]],">="&TODAY(),'
          '[[Bookings.confirm_sent]],"<>Yes",[[Bookings.status]],'
          '"<>Cancelled")', "int", 3, "Send a confirmation")
    s.kpi(row, 15, "Average rating",
          '=IFERROR(AVERAGEIFS([[Messages.rating]],'
          + _period("Messages", "date") + '),"-")', "number", 3,
          "Client satisfaction, 1 to 5")
    row += 4

    # ------------------------------------------------- 12 month trend ----
    row = s.section(row,
                    "Monthly performance - trends for the selected year",
                    LAST_COL)
    headers = ["Month", "Revenue", "Invoiced", "Expenses", "Profit",
               "Margin", "Bookings", "Completed", "Cancelled", "Visits",
               "New clients", "Distance", "Last year", "Change"]
    s.table_head(row, 0, headers)
    first_table_row = row + 1
    styles = ["text", "money", "money", "money", "money", "percent", "int",
              "int", "int", "int", "int", "number1", "money", "percent"]
    for i in range(MONTH_ROWS):
        r = first_table_row + i
        calc_row = FIRST_CALC_ROW + i
        values = [
            f'=[[Calc.m_label#{calc_row}]]',
            f'=[[Calc.m_rev#{calc_row}]]',
            f'=[[Calc.m_inv#{calc_row}]]',
            f'=[[Calc.m_exp#{calc_row}]]',
            f'=[[Calc.m_profit#{calc_row}]]',
            f'=IFERROR([[Calc.m_profit#{calc_row}]]'
            f'/[[Calc.m_rev#{calc_row}]],"")',
            f'=[[Calc.m_bookings#{calc_row}]]',
            f'=[[Calc.m_completed#{calc_row}]]',
            f'=[[Calc.m_cancelled#{calc_row}]]',
            f'=[[Calc.m_visits#{calc_row}]]',
            f'=[[Calc.m_new_clients#{calc_row}]]',
            f'=[[Calc.m_km#{calc_row}]]',
            f'=[[Calc.m_prev_rev#{calc_row}]]',
            f'=IFERROR([[Calc.m_rev#{calc_row}]]'
            f'/[[Calc.m_prev_rev#{calc_row}]]-1,"")',
        ]
        s.calc_row(r, 0, values, styles)
    last_table_row = first_table_row + MONTH_ROWS - 1

    total_row = last_table_row + 1
    s.write(total_row, 0, "Year total", fmts.chrome("total_label"))
    for i, style in enumerate(styles[1:], start=1):
        letter = col_letter(i)
        fmt = fmts.chrome("total_value",
                          num_format=s.num_format(style))
        if style == "percent":
            formula = (f'=IFERROR(E{total_row + 1}/B{total_row + 1},"")'
                       if i == 5 else
                       f'=IFERROR(B{total_row + 1}/M{total_row + 1}-1,"")')
            ws.write_formula(total_row, i, formula, fmt)
        else:
            ws.write_formula(
                total_row, i,
                f"=SUM({letter}{first_table_row + 1}:"
                f"{letter}{last_table_row + 1})", fmt)

    # Sparklines (supported by XlsxWriter 3.1.0 and later).
    spark_row = total_row + 1
    s.write(spark_row, 0, "Trend", fmts.chrome("label_bold"))
    spark_specs = [(1, "#6366F1"), (3, "#F43F5E"), (4, "#4338CA"),
                   (6, "#F59E0B")]
    for col_idx, colour in spark_specs:
        letter = col_letter(col_idx)
        try:
            ws.add_sparkline(spark_row, col_idx, {
                "range": (f"{quote_sheet(NAME)}!{letter}"
                          f"{first_table_row + 1}:{letter}"
                          f"{last_table_row + 1}"),
                "type": "column",
                "series_color": colour,
            })
        except Exception:        # pragma: no cover - older/newer libraries
            pass
    for col_idx in range(1, len(headers)):
        if col_idx not in [c for c, _ in spark_specs]:
            ws.write_blank(spark_row, col_idx, None,
                           fmts.chrome("legend_calc"))
    row = spark_row + 2

    # ------------------------------------------------- real chart ----------
    # Revenue and expenses as columns, profit as a line on top, all fed by
    # the month table above.  XlsxWriter charts work in Excel 2007 and later.
    chart_row = row
    money_fmt = f'{cfg.currency_symbol}#,##0'
    column_chart = book.add_chart({"type": "column"})
    column_chart.add_series({
        "name": "Revenue",
        "categories": [NAME, first_table_row, 0, last_table_row, 0],
        "values": [NAME, first_table_row, 1, last_table_row, 1],
        "fill": {"color": Palette.primary_mid},
        "border": {"none": True},
        "gap": 60,
    })
    column_chart.add_series({
        "name": "Expenses",
        "categories": [NAME, first_table_row, 0, last_table_row, 0],
        "values": [NAME, first_table_row, 3, last_table_row, 3],
        "fill": {"color": "#F43F5E"},
        "border": {"none": True},
    })
    line_chart = book.add_chart({"type": "line"})
    line_chart.add_series({
        "name": "Profit",
        "categories": [NAME, first_table_row, 0, last_table_row, 0],
        "values": [NAME, first_table_row, 4, last_table_row, 4],
        "line": {"color": Palette.primary, "width": 2.25},
        "marker": {
            "type": "circle",
            "size": 6,
            "fill": {"color": Palette.primary},
            "border": {"color": Palette.primary},
        },
    })
    column_chart.combine(line_chart)
    column_chart.set_title({
        "name": f"Revenue, expenses and profit - {cfg.today.year}",
        "name_font": {"size": 12, "bold": True, "color": Palette.ink},
    })
    column_chart.set_x_axis({
        "num_font": {"size": 9, "color": Palette.grey_text},
        "line": {"color": Palette.line},
    })
    column_chart.set_y_axis({
        "num_format": money_fmt,
        "num_font": {"size": 9, "color": Palette.grey_text},
        "major_gridlines": {"visible": True, "line": {"color": Palette.line}},
    })
    column_chart.set_legend({"position": "bottom",
                             "font": {"size": 9, "color": Palette.grey_text}})
    column_chart.set_chartarea({
        "border": {"color": Palette.line},
        "fill": {"color": Palette.white},
    })
    column_chart.set_plotarea({"fill": {"color": Palette.white}})
    ws.insert_chart(chart_row, 0, column_chart, {"x_scale": 1.55,
                                                 "y_scale": 1.25})
    row = chart_row + 20

    # ------------------------------------------ service / category tables
    row = s.section(row, "Where the money comes from - and where it goes",
                    LAST_COL)
    s.merge(row, 0, 5, "Revenue by service (selected period)",
            fmts.chrome("subsection"))
    s.merge(row, 7, 12, "Expenses by category (selected period)",
            fmts.chrome("subsection"))
    row += 1
    s.table_head(row, 0, ["Service", "Bookings", "Revenue", "Share"])
    s.table_head(row, 7, ["Category", "Spend", "Share", ""])
    first_split = row + 1
    service_rows = min(16, cfg.row_count("Services"))
    for i in range(service_rows):
        r = first_split + i
        calc_row = FIRST_CALC_ROW + i
        s.calc_row(r, 0, [
            f'=IF([[Calc.s_name#{calc_row}]]="","",'
            f'[[Calc.s_name#{calc_row}]])',
            f'=IF([[Calc.s_name#{calc_row}]]="","",'
            f'[[Calc.s_count_p#{calc_row}]])',
            f'=IF([[Calc.s_name#{calc_row}]]="","",'
            f'[[Calc.s_rev_p#{calc_row}]])',
            f'=IFERROR([[Calc.s_rev_p#{calc_row}]]'
            f'/SUM([[Calc.s_rev_p]]),"")',
        ], ["text", "int", "money", "percent"])
    ws.conditional_format(first_split, 2, first_split + service_rows - 1, 2,
                          {"type": "data_bar", "bar_color": "#6366F1"})

    category_rows = 19
    for i in range(category_rows):
        r = first_split + i
        calc_row = FIRST_CALC_ROW + i
        s.calc_row(r, 7, [
            f'=IF([[Calc.e_cat#{calc_row}]]="","",'
            f'[[Calc.e_cat#{calc_row}]])',
            f'=IF([[Calc.e_cat#{calc_row}]]="","",'
            f'[[Calc.e_total_p#{calc_row}]])',
            f'=IFERROR([[Calc.e_total_p#{calc_row}]]'
            f'/SUM([[Calc.e_total_p]]),"")',
            "",
        ], ["text", "money", "percent", "text"])
    ws.conditional_format(first_split, 8, first_split + category_rows - 1, 8,
                          {"type": "data_bar", "bar_color": "#F43F5E"})
    row = first_split + max(service_rows, category_rows) + 1

    # ------------------------------------------------ top clients + alerts
    row = s.section(row, "Top clients & action list", LAST_COL)
    s.merge(row, 0, 5, "Top 10 clients this period",
            fmts.chrome("subsection"))
    s.merge(row, 7, 12, "What needs attention right now",
            fmts.chrome("subsection"))
    row += 1
    s.table_head(row, 0, ["#", "Client", "Revenue", "Share"])
    s.table_head(row, 7, ["Alert", "Count", "Value", ""])
    first_top = row + 1
    for i in range(10):
        r = first_top + i
        n = i + 1
        s.calc_row(r, 0, [
            n,
            f'=IFERROR(INDEX([[Calc.c_name]],MATCH(LARGE([[Calc.c_key_p]],'
            f'{n}),[[Calc.c_key_p]],0)),"")',
            f'=IFERROR(INDEX([[Calc.c_rev_p]],MATCH(LARGE([[Calc.c_key_p]],'
            f'{n}),[[Calc.c_key_p]],0)),"")',
            f'=IFERROR(INDEX([[Calc.c_rev_p]],MATCH(LARGE([[Calc.c_key_p]],'
            f'{n}),[[Calc.c_key_p]],0))/SUM([[Calc.c_rev_p]]),"")',
        ], ["int", "text", "money", "percent"])
    ws.conditional_format(first_top, 2, first_top + 9, 2,
                          {"type": "data_bar", "bar_color": "#F59E0B"})

    alerts = [
        ("Overdue invoices",
         '=COUNTIFS([[Invoices.pay_status]],"Overdue")'
         '+COUNTIFS([[Invoices.pay_status]],"Overdue - part paid")',
         '=SUMIFS([[Invoices.balance]],[[Invoices.pay_status]],"Overdue")'
         '+SUMIFS([[Invoices.balance]],[[Invoices.pay_status]],'
         '"Overdue - part paid")'),
        ("Unconfirmed bookings",
         '=COUNTIFS([[Bookings.date]],">="&TODAY(),'
         '[[Bookings.confirm_sent]],"<>Yes",[[Bookings.status]],'
         '"<>Cancelled")',
         '=SUMIFS([[Bookings.total]],[[Bookings.date]],">="&TODAY(),'
         '[[Bookings.confirm_sent]],"<>Yes",[[Bookings.status]],'
         '"<>Cancelled")'),
        ("Booking conflicts",
         '=COUNTIF([[Bookings.conflict]],"Conflict*")', ""),
        ("Visits to log",
         '=COUNTIFS([[Bookings.status]],"Completed",'
         '[[Bookings.visit_logged]],"No")', ""),
        ("Vaccinations expired or due",
         '=COUNTIF([[Pets.vacc_status]],"Expired")'
         '+COUNTIF([[Pets.vacc_status]],"Due in*")', ""),
        ("Medication follow-ups",
         '=COUNTIF([[Health Log.status]],"Missed")'
         '+COUNTIF([[Health Log.refill_alert]],"Overdue*")', ""),
        ("Open incidents",
         '=COUNTIF([[Incidents.status]],"Open")'
         '+COUNTIF([[Incidents.status]],"In progress")', ""),
        ("Low or out of stock",
         '=COUNTIF([[Inventory.stock_status]],"Low*")'
         '+COUNTIF([[Inventory.stock_status]],"Out of stock")',
         '=SUMIFS([[Inventory.value]],[[Inventory.stock_status]],'
         '"Out of stock")'),
        ("Inactive clients to win back",
         '=COUNTIFS([[Clients.alert]],"Inactive*")', ""),
        ("Unresolved complaints",
         '=COUNTIFS([[Messages.complaint]],"Yes",[[Messages.resolution]],'
         '"<>Resolved")', ""),
    ]
    for i, (label, count, value) in enumerate(alerts):
        r = first_top + i
        s.calc_row(r, 7, [label, count, value or "", ""],
                   ["text", "int", "money", "text"])
        ws.conditional_format(r, 8, r, 8, {
            "type": "cell", "criteria": ">", "value": 0,
            "format": fmts.cf("bad")})
    row = first_top + 11

    s.note(row,
           "Tip: the Reminders tab lists every one of these alerts row by "
           "row, and the Reports tab turns the same data into printable "
           "monthly, quarterly and year-end reports.",
           LAST_COL, height=24)

    s.finish(freeze_row=4, gridlines=False, fit_width=True,
             print_area=f"A1:{col_letter(LAST_COL)}{row + 2}")
    return s
