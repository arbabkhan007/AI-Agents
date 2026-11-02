"""`Route Planner` - one crew, one day, one sheet to take with them.

Pick a date and a crew at the top and the day builds itself from the
Job & Work Orders tab: every stop, in the order it is booked, with the
address, the gate code, the dog warning, the service, the time it
should take and what to charge. Print it and hand it over.

What this page is not, and the listing says so too: it is not GPS
navigation and it does not optimise anything. It will not tell you
that visiting Mill Lane before Oak Avenue saves eleven minutes. It
organises the stops you have chosen, in the order you have chosen
them, onto one piece of paper - which is the thing most crews are
actually missing.

Stops are ordered by start time; ties follow job row order and blank
times appear last.
"""

from __future__ import annotations

from ..config import CREW_NAMES, Config, Palette
from ..layout import Registry
from ..writer import SheetWriter, date_check

NAME = "Route Planner"
LAST_COL = 10
STOPS = 14


def _stop(field: str, line: int) -> str:
    """Field from the nth job on the chosen crew's chosen day."""
    return (f'IFERROR(INDEX([[Job & Work Orders.{field}]],'
            f'MATCH({line},[[Job & Work Orders.route_match]],0)),"")')


def _stop_num(field: str, line: int) -> str:
    return (f'IFERROR(INDEX([[Job & Work Orders.{field}]],'
            f'MATCH({line},[[Job & Work Orders.route_match]],0))*1,"")')


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary_light)

    s.banner("Route Planner",
             "Pick a day and a crew. The stops, the gate codes and "
             "the times fill themselves in, ready to print.",
             LAST_COL)
    s.set_col(0, 0, 5)
    s.set_col(1, 1, 13)
    s.set_col(2, 2, 24)
    s.set_col(3, 3, 30)
    s.set_col(4, 4, 22)
    s.set_col(5, 5, 9)
    s.set_col(6, 6, 9)
    s.set_col(7, 7, 11)
    s.set_col(8, 8, 16)
    s.set_col(9, LAST_COL, 26)

    row = 4
    row = s.note(
        row,
        "This page organises stops onto a printable sheet. It is not "
        "satellite navigation and it does not work out the shortest "
        "route - you decide the order by setting start times on the "
        "Job & Work Orders tab, and this prints what you decided.",
        LAST_COL, height=34)
    row += 1

    # ------------------------------------------------------- the picker --
    row = s.section(row, "Choose the day", LAST_COL)
    row = s.field(row, "Date", cfg.today, style="date",
                  name="RouteDate", help_col=4,
                  help_text="Type any date. The stops below change "
                            "immediately.",
                  validate=date_check())
    row = s.field(row, "Crew", CREW_NAMES[0] if cfg.include_sample_data else None, name="RouteCrew",
                  help_col=4,
                  validate={"validate": "list",
                            "source": "=CrewNameList",
                            "input_message": "Which crew's day is "
                                             "this?"},
                  help_text="Each crew gets its own sheet. Print one "
                            "per truck.")
    row += 1

    # ---------------------------------------------------- the day's shape --
    row = s.section(row, "The day at a glance", LAST_COL)
    s.kpi(row, 0, "Stops",
          '=COUNTIFS(JobDateNum,RouteDate,JobCrew,RouteCrew,'
          'JobIsOpen,1)', "int", note="Jobs booked, still open")
    s.kpi(row, 2, "Work hours",
          '=SUMIFS(JobHoursEst,JobDateNum,RouteDate,JobCrew,'
          'RouteCrew,JobIsOpen,1)', "number1",
          note="Crew hours on site, estimated")
    s.kpi(row, 4, "Driving",
          '=ROUND(SUMIFS(JobDateNum,JobDateNum,RouteDate,JobCrew,'
          'RouteCrew,JobIsOpen,1)*0+COUNTIFS(JobDateNum,RouteDate,'
          'JobCrew,RouteCrew,JobIsOpen,1)*DriveMinutes/60,1)',
          "number1", note="Rough, at the default hop on Settings")
    s.kpi(row, 6, "Worth",
          '=SUMIFS(JobCharge,JobDateNum,RouteDate,JobCrew,RouteCrew,'
          'JobIsOpen,1)', "money", note="Value of the round")
    row = s.kpi(row, 8, "Per crew hour",
                '=IFERROR(SUMIFS(JobCharge,JobDateNum,RouteDate,'
                'JobCrew,RouteCrew,JobIsOpen,1)/'
                'SUMIFS(JobHoursEst,JobDateNum,RouteDate,JobCrew,'
                'RouteCrew,JobIsOpen,1),"")', "money", span=2,
                note="Against your charge-out rate")
    row += 1

    # ------------------------------------------------------- print head --
    row += 1
    s.merge(row, 0, 5, None, fmts.chrome("print_title"))
    s.formula(row, 0, '=BusinessName&" - crew work order"',
              fmts.chrome("print_title"))
    s.merge(row, 6, LAST_COL, None, fmts.chrome("print_sub"))
    s.formula(row, 6,
              '=TEXT(RouteDate,"dddd d mmmm yyyy")&"   "&RouteCrew',
              fmts.chrome("print_sub"))
    row += 1
    s.merge(row, 0, LAST_COL, None, fmts.chrome("note"))
    s.formula(
        row, 0,
        '="Jobs: "&COUNTIFS(JobDateNum,RouteDate,JobCrew,RouteCrew,'
        'JobIsOpen,1)&"    Estimated hours: "&'
        'TEXT(SUMIFS(JobHoursEst,JobDateNum,RouteDate,JobCrew,'
        'RouteCrew,JobIsOpen,1),"0.0")&'
        '"    Office: "&BusinessPhone',
        fmts.chrome("note"))
    row += 2

    # ------------------------------------------------------- the stops --
    s.table_head(row, 0,
                 ["#", "Start", "Customer", "Address", "Service",
                  "Mins", "Crew", "Charge", "Access / code",
                  "Notes and hazards"],
                 widths=[5, 13, 24, 30, 22, 9, 9, 11, 16, 26])
    head = row
    for n in range(1, STOPS + 1):
        line = head + n
        s.write(line, 0, n, fmts.chrome("line_number"))
        s.formula(line, 1,
                  '=IFERROR(IF(INDEX([[Job & Work Orders.start_time]],'
                  f'MATCH({n},[[Job & Work Orders.route_match]],0))="",'
                  '"",INDEX([[Job & Work Orders.start_time]],'
                  f'MATCH({n},[[Job & Work Orders.route_match]],0))),'
                  '"")', fmts.calc("time"))
        s.formula(line, 2, "=" + _stop("customer_name", n),
                  fmts.calc("text"))
        s.formula(line, 3, "=" + _stop("address", n),
                  fmts.calc("wrap"))
        s.formula(line, 4, "=" + _stop("service", n),
                  fmts.calc("text"))
        s.formula(line, 5,
                  '=IFERROR(ROUND(INDEX('
                  '[[Job & Work Orders.hours_est]],'
                  f'MATCH({n},[[Job & Work Orders.route_match]],0))*60,'
                  '0),"")', fmts.calc("int"))
        s.formula(line, 6, "=" + _stop_num("crew_used", n),
                  fmts.calc("int"))
        s.formula(line, 7, "=" + _stop_num("charge", n),
                  fmts.calc("money"))
        s.formula(line, 8,
                  '=IFERROR(INDEX([[Property Database.gate_code]],'
                  'MATCH(INDEX([[Job & Work Orders.property]],'
                  f'MATCH({n},[[Job & Work Orders.route_match]],0)),'
                  '[[Property Database.id]],0))&"","")',
                  fmts.calc("text"))
        s.formula(line, 9,
                  '=IFERROR(IF(INDEX('
                  '[[Property Database.dog]],'
                  'MATCH(INDEX([[Job & Work Orders.property]],'
                  f'MATCH({n},[[Job & Work Orders.route_match]],0)),'
                  '[[Property Database.id]],0))="Yes","DOG ON SITE. ",'
                  '"")&INDEX([[Property Database.pets_note]],'
                  'MATCH(INDEX([[Job & Work Orders.property]],'
                  f'MATCH({n},[[Job & Work Orders.route_match]],0)),'
                  '[[Property Database.id]],0))&"","")',
                  fmts.calc("wrap"))
        s.row_height(line, 26)
    s.cf(f"J{head + 2}:J{head + 1 + STOPS}",
         {"type": "text", "criteria": "containing", "value": "DOG",
          "format": fmts.cf("bad")})
    row = head + STOPS + 1

    # ------------------------------------------------------- the totals --
    s.write(row, 0, None, fmts.chrome("total_label"))
    s.merge(row, 0, 4, "Day total", fmts.chrome("total_label"))
    s.formula(row, 5,
              '=ROUND(SUMIFS(JobHoursEst,JobDateNum,RouteDate,JobCrew,'
              'RouteCrew,JobIsOpen,1)*60,0)',
              fmts.chrome("total_value"))
    s.write(row, 6, None, fmts.chrome("total_value"))
    s.formula(row, 7,
              '=SUMIFS(JobCharge,JobDateNum,RouteDate,JobCrew,'
              'RouteCrew,JobIsOpen,1)', fmts.chrome("total_value"))
    s.merge(row, 8, LAST_COL, None, fmts.chrome("total_value"))
    row += 2

    # ------------------------------------------- what the crew writes on --
    row = s.section(row, "For the crew to fill in", LAST_COL)
    row = s.note(
        row,
        "Print this page and the crew writes the real times and "
        "anything that went wrong in these boxes. Those numbers go "
        "back into the Timesheets and the job rows that evening, "
        "and that is what makes the profit figures true rather than "
        "hopeful.",
        LAST_COL, height=34)
    row += 1
    s.table_head(row, 0,
                 ["#", "Arrived", "Left", "Actual mins", "Done?",
                  "Problems on site", "Extra work done", "Materials "
                  "used", "Photo taken", "Signature"],
                 widths=[5, 13, 13, 12, 9, 26, 22, 18, 12, 20])
    head = row
    for n in range(1, STOPS + 1):
        line = head + n
        s.write(line, 0, n, fmts.chrome("line_number"))
        for column in range(1, LAST_COL + 1):
            s.write(line, column, None, fmts.chrome("form_line"))
        s.row_height(line, 24)
    row = head + STOPS + 2

    # --------------------------------------------------- the checklist --
    row = s.section(row, "Before you leave each property", LAST_COL)
    row = s.bullets(row, [
        "Gates shut and latched - the single most expensive thing a "
        "crew forgets.",
        "Clippings off the paths, the drive and the road.",
        "Beds and borders edged where the job includes them.",
        "Nothing left behind: strimmer line, fuel cans, hand tools, "
        "the blower.",
        "Any damage photographed and reported the same day, not the "
        "next week.",
        "Customer spoken to if they are in, and told what was done.",
        "Actual time written on this sheet before you drive off.",
    ], LAST_COL)
    row += 1

    row = s.note(
        row,
        "Stops are sorted by start time for the chosen date and crew; "
        "ties follow row order and blank times come last. To change "
        "the order, change the start times on "
        "the Job & Work Orders tab. Stops beyond fourteen in a day "
        "are not printed - if you are regularly over fourteen, split "
        "the round between two crews.",
        LAST_COL, height=34)
    row += 2

    row = _printable_quote(s, fmts, cfg, row)
    row = _printable_invoice(s, fmts, cfg, row)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s


# ---------------------------------------------------------------------------
# the two documents a customer actually sees
# ---------------------------------------------------------------------------
def _pull(sheet: str, field: str, key: str, picker: str,
          numeric: bool = False) -> str:
    """One field off the record the picker names."""
    tail = "*1" if numeric else '&""'
    return (f'=IF({picker}="","",IFERROR(INDEX([[{sheet}.{field}]],'
            f'MATCH({picker},[[{sheet}.{key}]],0)){tail},'
            f'{0 if numeric else chr(34) * 2}))')


def _doc_line(s: SheetWriter, fmts, row: int, label: str,
              formula: str, style: str = "text") -> int:
    """`Label | value` inside a printed document."""
    s.merge(row, 1, 2, label, fmts.chrome("form_label"))
    s.merge(row, 3, 6, None, fmts.calc(style))
    s.formula(row, 3, formula, fmts.calc(style))
    return row + 1


def _money_line(s: SheetWriter, fmts, row: int, label: str,
                formula: str, strong: bool = False) -> int:
    """A right-aligned money line on a document."""
    s.merge(row, 4, 6, label,
            fmts.chrome("total_label" if strong else "label_right"))
    s.formula(row, 7, formula,
              fmts.chrome("total_value") if strong
              else fmts.calc("money"))
    return row + 1


def _printable_quote(s: SheetWriter, fmts, cfg: Config, row: int) -> int:
    """A quote on one page, built from the row you name."""
    quote = "Quote Calculator"
    row = s.section(row, "Printable quote - pick one and print it",
                    LAST_COL)
    row = s.field(
        row, "Quote to print",
        "QTE-0001" if cfg.include_sample_data else None,
        name="PrintQuote", help_col=4,
        validate={"validate": "list", "source": "=QuoteIDList",
                  "input_message": "Pick the quote you want on "
                                   "paper."},
        help_text="Every figure below comes from that row of the "
                  "Quote Calculator.")
    row += 1

    s.merge(row, 0, 5, None, fmts.chrome("print_title"))
    s.formula(row, 0, '=BusinessName&" - quote"',
              fmts.chrome("print_title"))
    s.merge(row, 6, LAST_COL, None, fmts.chrome("print_sub"))
    s.formula(row, 6, '="Quote "&PrintQuote&"   "&'
                      'TEXT(TodayDate,"d mmmm yyyy")',
              fmts.chrome("print_sub"))
    row += 1
    s.merge(row, 0, LAST_COL, None, fmts.chrome("note"))
    s.formula(row, 0,
              '=BusinessAddress&", "&BusinessCity&"    "&'
              'BusinessPhone&"    "&BusinessEmail&'
              'IF(BusinessLicence="","","    Licence "&'
              'BusinessLicence)', fmts.chrome("note"))
    row += 2

    row = _doc_line(s, fmts, row, "Quote for",
                    _pull(quote, "customer_name", "id", "PrintQuote"))
    row = _doc_line(s, fmts, row, "Property",
                    _pull(quote, "address", "id", "PrintQuote"))
    row = _doc_line(s, fmts, row, "Work quoted",
                    _pull(quote, "service", "id", "PrintQuote"))
    row = _doc_line(s, fmts, row, "What is included",
                    _pull(quote, "description", "id", "PrintQuote"),
                    style="wrap")
    s.row_height(row - 1, 30)
    row = _doc_line(s, fmts, row, "How often",
                    _pull(quote, "frequency", "id", "PrintQuote"))
    row = _doc_line(
        row=row, s=s, fmts=fmts, label="Time on site",
        formula='=IF(PrintQuote="","",IFERROR(TEXT(INDEX('
                '[[Quote Calculator.site_hours]],MATCH(PrintQuote,'
                '[[Quote Calculator.id]],0)),"0.0")&" hours with "&'
                'INDEX([[Quote Calculator.crew_used]],MATCH('
                'PrintQuote,[[Quote Calculator.id]],0))&" on site",'
                '""))')
    row += 1

    row = _money_line(s, fmts, row, "Price for the visit",
                      _pull(quote, "price_used", "id", "PrintQuote",
                            numeric=True))
    row = _money_line(s, fmts, row, "Discount",
                      _pull(quote, "discount", "id", "PrintQuote",
                            numeric=True))
    s.merge(row, 4, 6, None, fmts.chrome("label_right"))
    s.formula(row, 4, '=IF(TaxOnServices="Yes",TaxName&" at "&'
                      'TEXT(TaxRate,"0.0%"),TaxName)',
              fmts.chrome("label_right"))
    s.formula(row, 7, _pull(quote, "tax", "id", "PrintQuote",
                            numeric=True), fmts.calc("money"))
    row += 1
    row = _money_line(s, fmts, row, "Total",
                      _pull(quote, "total", "id", "PrintQuote",
                            numeric=True), strong=True)
    row = _money_line(
        s, fmts, row, "A year of these visits",
        _pull(quote, "annual_value", "id", "PrintQuote", numeric=True))
    row += 1

    s.merge(row, 0, LAST_COL, None, fmts.chrome("note"))
    s.formula(row, 0,
              '="This quote stands until "&IF(PrintQuote="","",'
              'IFERROR(TEXT(INDEX([[Quote Calculator.valid_until]],'
              'MATCH(PrintQuote,[[Quote Calculator.id]],0)),'
              '"d mmmm yyyy"),""))&". Prices assume reasonable '
              'access and normal growth; anything we find that '
              'changes the work, we will tell you before we do it."',
              fmts.chrome("note"))
    s.row_height(row, 28)
    row += 2
    return row


def _printable_invoice(s: SheetWriter, fmts, cfg: Config,
                       row: int) -> int:
    """An invoice on one page, built from the row you name."""
    inv = "Invoice & Payments"
    row = s.section(row, "Printable invoice - pick one and print it",
                    LAST_COL)
    row = s.note(
        row,
        "This is the document the Invoice & Payments tab refers to. "
        "Pick an invoice, print this block - File, Print, Print "
        "Selection after highlighting it - and record what the "
        "customer pays back on that tab. The workbook cannot send "
        "an email or take a card payment.",
        LAST_COL, height=34)
    row = s.field(
        row, "Invoice to print",
        "INV-00001" if cfg.include_sample_data else None,
        name="PrintInvoice", help_col=4,
        validate={"validate": "list", "source": "=InvoiceIDList",
                  "input_message": "Pick the invoice you want on "
                                   "paper."},
        help_text="Marked on the invoice row as the print line.")
    row += 1

    s.merge(row, 0, 5, None, fmts.chrome("print_title"))
    s.formula(row, 0, '=BusinessName&" - invoice"',
              fmts.chrome("print_title"))
    s.merge(row, 6, LAST_COL, None, fmts.chrome("print_sub"))
    s.formula(row, 6,
              '="Invoice "&IF(PrintInvoice="","",IFERROR(IF(INDEX('
              '[[Invoice & Payments.invoice_number]],MATCH('
              'PrintInvoice,[[Invoice & Payments.id]],0))="",'
              'PrintInvoice,INDEX([[Invoice & Payments.'
              'invoice_number]],MATCH(PrintInvoice,'
              '[[Invoice & Payments.id]],0))),PrintInvoice))',
              fmts.chrome("print_sub"))
    row += 1
    s.merge(row, 0, LAST_COL, None, fmts.chrome("note"))
    s.formula(row, 0,
              '=BusinessAddress&", "&BusinessCity&"    "&'
              'BusinessPhone&"    "&BusinessEmail',
              fmts.chrome("note"))
    row += 2

    row = _doc_line(s, fmts, row, "Bill to",
                    _pull(inv, "customer_name", "id", "PrintInvoice"))
    row = _doc_line(
        s, fmts, row, "Work done",
        _pull(inv, "description", "id", "PrintInvoice"), style="wrap")
    s.row_height(row - 1, 30)
    row = _doc_line(
        s, fmts, row, "Period covered",
        _pull(inv, "period", "id", "PrintInvoice"))
    row = _doc_line(
        s, fmts, row, "Invoice date",
        '=IF(PrintInvoice="","",IFERROR(TEXT(INDEX('
        '[[Invoice & Payments.date]],MATCH(PrintInvoice,'
        '[[Invoice & Payments.id]],0)),"d mmmm yyyy"),""))')
    row = _doc_line(
        s, fmts, row, "Payment due",
        '=IF(PrintInvoice="","",IFERROR(TEXT(INDEX('
        '[[Invoice & Payments.due_date]],MATCH(PrintInvoice,'
        '[[Invoice & Payments.id]],0)),"d mmmm yyyy")&"   ("&'
        'INDEX([[Invoice & Payments.terms]],MATCH(PrintInvoice,'
        '[[Invoice & Payments.id]],0))&")",""))')
    row += 1

    row = _money_line(s, fmts, row, "Net",
                      _pull(inv, "net", "id", "PrintInvoice",
                            numeric=True))
    row = _money_line(s, fmts, row, "Discount",
                      _pull(inv, "discount", "id", "PrintInvoice",
                            numeric=True))
    s.merge(row, 4, 6, None, fmts.chrome("label_right"))
    s.formula(row, 4, '=IF(TaxOnServices="Yes",TaxName&" at "&'
                      'TEXT(TaxRate,"0.0%"),TaxName)',
              fmts.chrome("label_right"))
    s.formula(row, 7, _pull(inv, "tax", "id", "PrintInvoice",
                            numeric=True), fmts.calc("money"))
    row += 1
    row = _money_line(s, fmts, row, "Total",
                      _pull(inv, "total", "id", "PrintInvoice",
                            numeric=True), strong=True)
    row = _money_line(s, fmts, row, "Already paid",
                      _pull(inv, "paid", "id", "PrintInvoice",
                            numeric=True))
    row = _money_line(s, fmts, row, "Now due",
                      _pull(inv, "outstanding", "id", "PrintInvoice",
                            numeric=True), strong=True)
    row += 1

    s.merge(row, 0, LAST_COL, None, fmts.chrome("note"))
    s.formula(row, 0,
              '="Please pay "&CurrencySign&TEXT(IF(PrintInvoice="",'
              '0,IFERROR(INDEX([[Invoice & Payments.outstanding]],'
              'MATCH(PrintInvoice,[[Invoice & Payments.id]],0)),0)),'
              '"#,##0.00")&" to "&BusinessName&" by the due date '
              'above. Questions about this invoice: "&BusinessPhone&'
              '". Thank you for your custom."',
              fmts.chrome("note"))
    s.row_height(row, 28)
    row += 2
    return row
