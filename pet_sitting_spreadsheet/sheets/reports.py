"""`Reports` - printable business analytics for any date range."""

from __future__ import annotations

import datetime as _dt

from ..config import Config, Palette
from ..layout import Registry, col_letter, quote_sheet
from ..writer import SheetWriter, date_check

NAME = "Reports"
LAST_COL = 11            # column L
FIRST_CALC_ROW = 5


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME, tab_color=Palette.ink)
    ws = s.ws

    s.banner("Reports & Business Analytics",
             "Set a date range once at the top - every report below "
             "recalculates. Print the whole tab for your accountant or "
             "year-end review.",
             LAST_COL)

    s.set_col(0, 0, 30)
    s.set_col(1, 1, 16)
    s.set_col(2, 2, 16)
    s.set_col(3, 3, 16)
    s.set_col(4, 4, 3)
    s.set_col(5, 5, 30)
    s.set_col(6, 8, 16)
    s.set_col(9, LAST_COL, 14)

    def metric(row, col, label, formula, style="money", label_span=1):
        s.merge(row, col, col + label_span - 1, label,
                fmts.chrome("label"))
        fmt = fmts.calc(style)
        ws.write_formula(row, col + label_span,
                         reg.render(formula), fmt)
        return row + 1

    def table(row, col, headers, widths=None):
        return s.table_head(row, col, headers, widths)

    # ------------------------------------------------------- range picker
    row = 4
    row = s.section(row, "Report period", LAST_COL)
    s.merge(row, 0, 0, "From", fmts.chrome("label_bold"))
    s.write(row, 1, _start_of_year(cfg), fmts.input("date"))
    ws.data_validation(row, 1, row, 1, date_check())
    book.define_name("RepFrom", f"={quote_sheet(NAME)}!$B${row + 1}")
    s.merge(row, 2, 2, "To", fmts.chrome("label_bold"))
    s.write(row, 3, _end_of_year(cfg), fmts.input("date"))
    ws.data_validation(row, 3, row, 3, date_check())
    book.define_name("RepTo", f"={quote_sheet(NAME)}!$D${row + 1}")
    s.merge(row, 5, LAST_COL,
            "Try 1st to 31st of a month for a monthly report, or 1 Jan to "
            "31 Dec for the year-end pack.", fmts.chrome("note"))
    row += 2

    # ------------------------------------------------------ booking report
    row = s.section(row, "1. Booking & service delivery report", LAST_COL)
    bk_range = ('[[Bookings.date]],">="&RepFrom,[[Bookings.date]],'
                '"<="&RepTo')
    vs_range = ('[[Visit Log.date]],">="&RepFrom,[[Visit Log.date]],'
                '"<="&RepTo')
    left = row
    left = metric(left, 0, "Bookings taken",
                  f'=COUNTIFS({bk_range})', "int")
    left = metric(left, 0, "Completed bookings",
                  f'=COUNTIFS({bk_range},[[Bookings.status]],"Completed")',
                  "int")
    left = metric(left, 0, "Cancelled bookings",
                  f'=COUNTIFS({bk_range},[[Bookings.status]],"Cancelled")',
                  "int")
    left = metric(left, 0, "No shows",
                  f'=COUNTIFS({bk_range},[[Bookings.status]],"No show")',
                  "int")
    left = metric(left, 0, "Still to deliver",
                  f'=COUNTIFS({bk_range},[[Bookings.status]],"Confirmed")'
                  f'+COUNTIFS({bk_range},[[Bookings.status]],"Pending")',
                  "int")
    left = metric(left, 0, "Completion rate",
                  f'=IFERROR(COUNTIFS({bk_range},[[Bookings.status]],'
                  f'"Completed")/COUNTIFS({bk_range}),0)', "percent")
    left = metric(left, 0, "Cancellation rate",
                  f'=IFERROR(COUNTIFS({bk_range},[[Bookings.status]],'
                  f'"Cancelled")/COUNTIFS({bk_range}),0)', "percent")

    right = row
    right = metric(right, 5, "Visits completed",
                   f'=COUNTIFS({vs_range},[[Visit Log.status]],'
                   f'"Completed")', "int")
    right = metric(right, 5, "Visits missed",
                   f'=COUNTIFS({vs_range},[[Visit Log.status]],"Missed")',
                   "int")
    right = metric(right, 5, "Hours of care delivered",
                   f'=ROUND(SUMIFS([[Visit Log.duration]],{vs_range},'
                   f'[[Visit Log.status]],"Completed")/60,1)', "number")
    right = metric(right, 5, "Walk distance logged",
                   f'=SUMIFS([[Visit Log.walk_distance]],{vs_range})',
                   "number1")
    right = metric(right, 5, "On-time arrival rate",
                   f'=IFERROR(COUNTIFS({vs_range},[[Visit Log.punctual]],'
                   f'"On time")/COUNTIFS({vs_range},'
                   f'[[Visit Log.status]],"Completed"),0)', "percent")
    right = metric(right, 5, "Medication doses given",
                   '=COUNTIFS([[Health Log.date]],">="&RepFrom,'
                   '[[Health Log.date]],"<="&RepTo,[[Health Log.status]],'
                   '"Given")', "int")
    right = metric(right, 5, "Medication doses missed",
                   '=COUNTIFS([[Health Log.date]],">="&RepFrom,'
                   '[[Health Log.date]],"<="&RepTo,[[Health Log.status]],'
                   '"Missed")', "int")
    row = max(left, right) + 1

    # ----------------------------------------------------- financial report
    row = s.section(row, "2. Profit & loss for the period", LAST_COL)
    inc = ('[[Payments.date]],">="&RepFrom,[[Payments.date]],"<="&RepTo')
    exp = ('[[Expenses.date]],">="&RepFrom,[[Expenses.date]],"<="&RepTo,'
           '[[Expenses.type]],"<>Personal"')
    pl_first = row
    row = metric(row, 0, "Service income collected",
                 f'=SUMIFS([[Payments.amount]],{inc})'
                 f'-SUMIFS([[Payments.refund]],{inc})')
    row = metric(row, 0, "Tips & gratuities",
                 f'=SUMIFS([[Payments.tip]],{inc})')
    row = metric(row, 0, "Late fees collected",
                 f'=SUMIFS([[Payments.late_fee]],{inc})')
    income_row = row
    row = metric(row, 0, "TOTAL INCOME",
                 f'=SUM(B{pl_first + 1}:B{row})')
    row = metric(row, 0, "Wages & contractor payments",
                 f'=SUMIFS([[Expenses.amount]],{exp},'
                 f'[[Expenses.category]],"Staff wages")'
                 f'+SUMIFS([[Expenses.amount]],{exp},'
                 f'[[Expenses.category]],"Contractor payments")')
    wages_row = row
    row = metric(row, 0, "Gross profit",
                 f'=B{income_row + 1}-B{wages_row}')
    gross_row = row
    row = metric(row, 0, "Other operating expenses",
                 f'=SUMIFS([[Expenses.amount]],{exp})'
                 f'-B{wages_row}')
    other_row = row
    row = metric(row, 0, "NET PROFIT",
                 f'=B{gross_row}-B{other_row}')
    profit_row = row
    row = metric(row, 0, "Profit margin",
                 f'=IFERROR(B{profit_row}/B{income_row + 1},0)', "percent")
    row = metric(row, 0, "Tax to set aside",
                 f'=MAX(0,B{profit_row})*TaxReservePct')

    money_right = pl_first
    money_right = metric(money_right, 5, "Invoiced in period",
                         '=SUMIFS([[Invoices.total]],[[Invoices.date]],'
                         '">="&RepFrom,[[Invoices.date]],"<="&RepTo,'
                         '[[Invoices.status]],"<>Cancelled")')
    money_right = metric(money_right, 5, "Collected in period",
                         f'=SUMIFS([[Payments.received]],{inc})')
    money_right = metric(money_right, 5, "Refunds issued",
                         f'=SUMIFS([[Payments.refund]],{inc})')
    money_right = metric(money_right, 5, "Outstanding right now",
                         '=SUMIFS([[Invoices.balance]],[[Invoices.status]],'
                         '"<>Cancelled")')
    money_right = metric(money_right, 5, "Overdue right now",
                         '=SUMIFS([[Invoices.balance]],'
                         '[[Invoices.pay_status]],"Overdue")'
                         '+SUMIFS([[Invoices.balance]],'
                         '[[Invoices.pay_status]],"Overdue - part paid")')
    money_right = metric(money_right, 5, "Tax charged on invoices",
                         '=SUMIFS([[Invoices.tax]],[[Invoices.date]],'
                         '">="&RepFrom,[[Invoices.date]],"<="&RepTo,'
                         '[[Invoices.status]],"<>Cancelled")')
    money_right = metric(money_right, 5, "Tax paid inside expenses",
                         f'=SUMIFS([[Expenses.tax]],{exp})')
    money_right = metric(money_right, 5, "Mileage claim",
                         '=SUMIFS([[Mileage.claimable]],[[Mileage.date]],'
                         '">="&RepFrom,[[Mileage.date]],"<="&RepTo)')
    money_right = metric(money_right, 5, "Business distance travelled",
                         '=SUMIFS([[Mileage.total_km]],[[Mileage.date]],'
                         '">="&RepFrom,[[Mileage.date]],"<="&RepTo,'
                         '[[Mileage.business]],"Business")', "number1")
    row = max(row, money_right) + 1

    # ------------------------------------------------- revenue by service
    row = s.section(row, "3. Revenue & profit by service", LAST_COL)
    row = table(row, 0, ["Service", "Bookings", "Revenue", "Est. cost",
                         "Est. profit", "Margin"])
    first = row
    service_rows = min(16, cfg.row_count("Services"))
    for i in range(service_rows):
        c = FIRST_CALC_ROW + i
        s.calc_row(first + i, 0, [
            f'=IF([[Calc.s_name#{c}]]="","",[[Calc.s_name#{c}]])',
            f'=IF([[Calc.s_name#{c}]]="","",[[Calc.s_count_r#{c}]])',
            f'=IF([[Calc.s_name#{c}]]="","",[[Calc.s_rev_r#{c}]])',
            f'=IF([[Calc.s_name#{c}]]="","",[[Calc.s_cost_r#{c}]])',
            f'=IF([[Calc.s_name#{c}]]="","",[[Calc.s_profit_r#{c}]])',
            f'=IFERROR([[Calc.s_profit_r#{c}]]/[[Calc.s_rev_r#{c}]],"")',
        ], ["text", "int", "money", "money", "money", "percent"])
    ws.conditional_format(first, 2, first + service_rows - 1, 2,
                          {"type": "data_bar", "bar_color": "#6366F1"})
    row = first + service_rows + 1

    # --------------------------------------------------- clients & ageing
    row = s.section(row, "4. Clients, outstanding money & invoice ageing",
                    LAST_COL)
    s.merge(row, 0, 3, "Top 10 clients in the period",
            fmts.chrome("subsection"))
    s.merge(row, 5, 8, "Largest outstanding balances",
            fmts.chrome("subsection"))
    row += 1
    table(row, 0, ["#", "Client", "Revenue", "Bookings"])
    table(row, 5, ["#", "Client", "Owed", "Unpaid invoices"])
    first = row + 1
    for i in range(10):
        n = i + 1
        s.calc_row(first + i, 0, [
            n,
            f'=IFERROR(INDEX([[Calc.c_name]],MATCH(LARGE([[Calc.c_key_r]],'
            f'{n}),[[Calc.c_key_r]],0)),"")',
            f'=IFERROR(INDEX([[Calc.c_rev_r]],MATCH(LARGE([[Calc.c_key_r]],'
            f'{n}),[[Calc.c_key_r]],0)),"")',
            f'=IFERROR(INDEX([[Calc.c_bookings_r]],'
            f'MATCH(LARGE([[Calc.c_key_r]],{n}),[[Calc.c_key_r]],0)),"")',
        ], ["int", "text", "money", "int"])
        client_lookup = (f'INDEX([[Calc.c_name]],MATCH(LARGE('
                         f'[[Calc.c_out_key]],{n}),[[Calc.c_out_key]],0))')
        s.calc_row(first + i, 5, [
            n,
            f'=IFERROR({client_lookup},"")',
            f'=IFERROR(INDEX([[Calc.c_out]],MATCH(LARGE('
            f'[[Calc.c_out_key]],{n}),[[Calc.c_out_key]],0)),"")',
            f'=IFERROR(COUNTIFS([[Invoices.client]],{client_lookup},'
            f'[[Invoices.balance]],">0.004"),"")',
        ], ["int", "text", "money", "int"])
    row = first + 11

    s.merge(row, 0, 3, "Invoice ageing", fmts.chrome("subsection"))
    s.merge(row, 5, 8, "How clients pay", fmts.chrome("subsection"))
    row += 1
    table(row, 0, ["Bucket", "Invoices", "Amount", "Share"])
    table(row, 5, ["Method", "Collected", "Share", ""])
    first = row + 1
    buckets = ["Not due", "Current", "1-30 days", "31-60 days",
               "61-90 days", "90+ days"]
    for i, bucket in enumerate(buckets):
        s.calc_row(first + i, 0, [
            bucket,
            f'=COUNTIFS([[Invoices.aging]],"{bucket}")',
            f'=SUMIFS([[Invoices.balance]],[[Invoices.aging]],"{bucket}")',
            f'=IFERROR(SUMIFS([[Invoices.balance]],[[Invoices.aging]],'
            f'"{bucket}")/SUMIFS([[Invoices.balance]],'
            f'[[Invoices.status]],"<>Cancelled"),"")',
        ], ["text", "int", "money", "percent"])
    for i in range(8):
        c = FIRST_CALC_ROW + i
        s.calc_row(first + i, 5, [
            f'=IF([[Calc.pm_method#{c}]]="","",[[Calc.pm_method#{c}]])',
            f'=IF([[Calc.pm_method#{c}]]="","",[[Calc.pm_total#{c}]])',
            f'=IFERROR([[Calc.pm_total#{c}]]/SUM([[Calc.pm_total]]),"")',
            "",
        ], ["text", "money", "percent", "text"])
    row = first + max(len(buckets), 8) + 1

    # ------------------------------------------------- real chart ----------
    # Outstanding money by how old the invoice is - always six full bars.
    chart_row = row
    chart = book.add_chart({"type": "bar"})
    chart.add_series({
        "name": "Outstanding",
        "categories": [NAME, first, 0, first + len(buckets) - 1, 0],
        "values": [NAME, first, 2, first + len(buckets) - 1, 2],
        "fill": {"color": Palette.primary_mid},
        "border": {"none": True},
        "gap": 50,
        "data_labels": {"value": True, "num_format": f'{cfg.currency_symbol}#,##0',
                        "font": {"size": 8, "color": Palette.grey_text}},
    })
    chart.set_title({"name": "Who owes you money, by invoice age",
                     "name_font": {"size": 12, "bold": True,
                                   "color": Palette.ink}})
    chart.set_x_axis({"num_format": f'{cfg.currency_symbol}#,##0',
                      "num_font": {"size": 9, "color": Palette.grey_text},
                      "major_gridlines": {"visible": True,
                                          "line": {"color": Palette.line}}})
    chart.set_y_axis({"reverse": True,
                      "num_font": {"size": 9, "color": Palette.grey_text}})
    chart.set_legend({"none": True})
    chart.set_chartarea({"border": {"color": Palette.line},
                         "fill": {"color": Palette.white}})
    chart.set_plotarea({"fill": {"color": Palette.white}})
    ws.insert_chart(chart_row, 0, chart, {"x_scale": 1.35, "y_scale": 1.15})
    row = chart_row + 19

    # ------------------------------------------------ expenses & mileage
    row = s.section(row, "5. Expense report by category", LAST_COL)
    row = table(row, 0, ["Category", "Spend", "Share", "", "", ""])
    first = row
    for i in range(19):
        c = FIRST_CALC_ROW + i
        s.calc_row(first + i, 0, [
            f'=IF([[Calc.e_cat#{c}]]="","",[[Calc.e_cat#{c}]])',
            f'=IF([[Calc.e_cat#{c}]]="","",[[Calc.e_total_r#{c}]])',
            f'=IFERROR([[Calc.e_total_r#{c}]]/SUM([[Calc.e_total_r]]),"")',
            "", "", "",
        ], ["text", "money", "percent", "text", "text", "text"])
    ws.conditional_format(first, 1, first + 18, 1,
                          {"type": "data_bar", "bar_color": "#F43F5E"})
    s.calc_row(first + 19, 0, ["Total business expenses",
                               f'=SUM(B{first + 1}:B{first + 19})', "",
                               "", "", ""],
               ["text", "money", "text", "text", "text", "text"])
    row = first + 21

    # --------------------------------------------------- staff & retention
    row = s.section(row, "6. Staff performance", LAST_COL)
    row = table(row, 0, ["Team member", "Visits", "Hours", "Revenue",
                         "Revenue / hour", "Distance"])
    first = row
    staff_rows = min(12, cfg.row_count("Staff"))
    for i in range(staff_rows):
        c = FIRST_CALC_ROW + i
        s.calc_row(first + i, 0, [
            f'=IF([[Calc.st_name#{c}]]="","",[[Calc.st_name#{c}]])',
            f'=IF([[Calc.st_name#{c}]]="","",[[Calc.st_visits_r#{c}]])',
            f'=IF([[Calc.st_name#{c}]]="","",[[Calc.st_hours_r#{c}]])',
            f'=IF([[Calc.st_name#{c}]]="","",[[Calc.st_rev_r#{c}]])',
            f'=IFERROR([[Calc.st_rev_r#{c}]]/[[Calc.st_hours_r#{c}]],"")',
            f'=IF([[Calc.st_name#{c}]]="","",[[Calc.st_km_r#{c}]])',
        ], ["text", "int", "number", "money", "money", "number1"])
    row = first + staff_rows + 1

    row = s.section(row, "7. Client retention & marketing", LAST_COL)
    ret = row
    ret = metric(ret, 0, "Clients served in the period",
                 '=COUNTIF([[Calc.c_bookings_r]],">0")', "int")
    ret = metric(ret, 0, "Clients with repeat bookings",
                 '=COUNTIF([[Calc.c_bookings_r]],">1")', "int")
    ret = metric(ret, 0, "Repeat booking rate",
                 '=IFERROR(COUNTIF([[Calc.c_bookings_r]],">1")'
                 '/COUNTIF([[Calc.c_bookings_r]],">0"),0)', "percent")
    ret = metric(ret, 0, "New clients registered",
                 '=COUNTIFS([[Clients.reg_date]],">="&RepFrom,'
                 '[[Clients.reg_date]],"<="&RepTo)', "int")
    ret = metric(ret, 0, "Returning client rate",
                 '=IFERROR((COUNTIF([[Calc.c_bookings_r]],">0")'
                 '-COUNTIFS([[Clients.reg_date]],">="&RepFrom,'
                 '[[Clients.reg_date]],"<="&RepTo))'
                 '/COUNTIF([[Calc.c_bookings_r]],">0"),0)', "percent")
    ret = metric(ret, 0, "Inactive clients to win back",
                 '=COUNTIF([[Clients.alert]],"Inactive*")', "int")
    ret = metric(ret, 0, "Average client lifetime revenue",
                 '=IFERROR(AVERAGEIF([[Clients.revenue]],">0"),0)')
    ret = metric(ret, 0, "Average satisfaction rating",
                 '=IFERROR(AVERAGEIFS([[Messages.rating]],'
                 '[[Messages.date]],">="&RepFrom,[[Messages.date]],'
                 '"<="&RepTo),"-")', "number")
    ret = metric(ret, 0, "Complaints logged",
                 '=COUNTIFS([[Messages.complaint]],"Yes",'
                 '[[Messages.date]],">="&RepFrom,[[Messages.date]],'
                 '"<="&RepTo)', "int")
    ret = metric(ret, 0, "Complaints still open",
                 '=COUNTIFS([[Messages.complaint]],"Yes",'
                 '[[Messages.resolution]],"<>Resolved")', "int")

    s.merge(row, 5, 8, "Where clients come from", fmts.chrome("subsection"))
    s.table_head(row + 1, 5, ["Referral source", "Clients", "Revenue", ""])
    for i in range(10):
        c = FIRST_CALC_ROW + i
        s.calc_row(row + 2 + i, 5, [
            f'=IF([[Calc.ref_source#{c}]]="","",[[Calc.ref_source#{c}]])',
            f'=IF([[Calc.ref_source#{c}]]="","",[[Calc.ref_clients#{c}]])',
            f'=IF([[Calc.ref_source#{c}]]="","",[[Calc.ref_revenue#{c}]])',
            "",
        ], ["text", "int", "money", "text"])
    row = max(ret, row + 12) + 1

    # ------------------------------------------------ cancellation reasons
    row = s.section(row, "8. Cancellation analysis", LAST_COL)
    row = table(row, 0, ["Reason", "Cancellations", "Share", "", "", ""])
    first = row
    for i in range(10):
        c = FIRST_CALC_ROW + i
        s.calc_row(first + i, 0, [
            f'=IF([[Calc.cr_reason#{c}]]="","",[[Calc.cr_reason#{c}]])',
            f'=IF([[Calc.cr_reason#{c}]]="","",[[Calc.cr_count#{c}]])',
            f'=IFERROR([[Calc.cr_count#{c}]]/SUM([[Calc.cr_count]]),"")',
            "", "", "",
        ], ["text", "int", "percent", "text", "text", "text"])
    row = first + 11

    s.note(row,
           "Printing: this tab is set up to print on A4 at one page wide. "
           "Use File > Print and choose 'Print active sheet'. For a single "
           "report, select the block you need and print the selection.",
           LAST_COL, height=26)

    s.finish(freeze_row=4, gridlines=False, fit_width=True,
             print_area=f"A1:{col_letter(LAST_COL)}{row + 2}")
    return s


def _start_of_year(cfg: Config) -> _dt.date:
    return _dt.date(cfg.today.year, 1, 1)


def _end_of_year(cfg: Config) -> _dt.date:
    return _dt.date(cfg.today.year, 12, 31)
