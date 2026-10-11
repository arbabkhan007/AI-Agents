"""The four print-ready tabs: invoice, pet care sheet, visit report, forms.

Each one is driven by a single drop down at the top (which sits outside the
print area), so the user picks a record and presses print.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from ..config import Config, Palette
from ..layout import Registry, quote_sheet
from ..sample_data import get as sample
from ..writer import SheetWriter

INVOICE_SHEET = "Print Invoice"
CARE_SHEET = "Print Pet Care"
VISIT_SHEET = "Print Visit"
FORMS_SHEET = "Print Forms"

LAST_COL = 7          # column H - a comfortable portrait page


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def _pick(sheet: SheetWriter, fmts, label: str, list_name: str,
          define_as: str, hint: str, default: str = "") -> str:
    """Drop down selector on row 1. Returns the absolute cell reference."""
    ws = sheet.ws
    sheet.merge(0, 0, 1, label, fmts.chrome("label_bold"))
    fmt = fmts.input("text", bold=True, font_size=11)
    ws.merge_range(0, 2, 0, 3, default, fmt)
    ws.data_validation(0, 2, 0, 3, {
        "validate": "list", "source": f"={list_name}",
        "input_title": "Choose a record",
        "input_message": hint[:255]})
    sheet.merge(0, 4, LAST_COL, hint, fmts.chrome("note"))
    sheet.row_height(0, 22)
    sheet.book.define_name(
        define_as, f"={quote_sheet(sheet.name)}!$C$1")
    return define_as


def _row(sheet, fmts, row: int, label: str, formula: Optional[str] = None,
         style: str = "text", label_cols: Tuple[int, int] = (0, 1),
         value_cols: Tuple[int, int] = (2, 3), value: str = "",
         bold: bool = False):
    """`Label: value` line used all over the print sheets."""
    sheet.merge(row, label_cols[0], label_cols[1], label,
                fmts.chrome("label_bold" if bold else "label"))
    fmt = fmts.calc(style) if formula else fmts.chrome("label")
    if formula:
        if value_cols[1] > value_cols[0]:
            sheet.ws.merge_range(row, value_cols[0], row, value_cols[1], "",
                                 fmt)
        sheet.ws.write_formula(row, value_cols[0],
                               sheet.reg.render(formula), fmt)
    else:
        sheet.merge(row, value_cols[0], value_cols[1], value, fmt)
    return row + 1


def _first_invoice(cfg: Config) -> str:
    if not cfg.include_sample_data:
        return ""
    return f"{cfg.invoice_prefix}{cfg.invoice_start_number:04d}"


def _first_pet(cfg: Config) -> str:
    pets = sample(cfg).pets if cfg.include_sample_data else []
    if not pets:
        return ""
    return f"{pets[0]['name']} ({pets[0]['owner']})"


def _first_visit(cfg: Config) -> str:
    return "VS-0001" if cfg.include_sample_data else ""


def _index(sheet: str, field: str, key: str, key_field: str,
           fallback: str = '""') -> str:
    """INDEX/MATCH against a register, written in template syntax."""
    return (f'IFERROR(INDEX([[{sheet}.{field}]],'
            f'MATCH({key},[[{sheet}.{key_field}]],0)),{fallback})')


# ---------------------------------------------------------------------------
# 1. Print Invoice
# ---------------------------------------------------------------------------

def build_invoice(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, INVOICE_SHEET,
                    tab_color=Palette.primary_soft, landscape=False)
    ws = s.ws
    s.set_col(0, 0, 14)
    s.set_col(1, 1, 16)
    s.set_col(2, 2, 14)
    s.set_col(3, 3, 12)
    s.set_col(4, 4, 8)
    s.set_col(5, 5, 10)
    s.set_col(6, 6, 12)
    s.set_col(7, 7, 14)

    _pick(s, fmts, "Invoice to print", "InvoiceNos", "PrintInvoiceNo",
          "Pick an invoice number - everything below fills in "
          "automatically. This row does not print.",
          default=_first_invoice(cfg))

    def inv(field: str, fallback: str = '""') -> str:
        return _index("Invoices", field, "PrintInvoiceNo", "invoice_no",
                      fallback)

    client = inv("client")
    booking = inv("booking")

    def cli(field: str) -> str:
        return _index("Clients", field, f"({client})", "name")

    def bkg(field: str) -> str:
        return _index("Bookings", field, f"({booking})", "id")

    row = 2
    s.merge(row, 0, 3, "", fmts.chrome("print_title"))
    ws.write_formula(row, 0, "=Biz_Name", fmts.chrome("print_title"))
    s.merge(row, 5, LAST_COL, "INVOICE",
            fmts.chrome("print_title", align="right",
                        font_color=Palette.accent, font_size=22))
    s.row_height(row, 30)

    left = row + 1
    for formula in ('=Biz_Address', '=Biz_City&" "&Biz_State&" "&Biz_Post',
                    '=Biz_Phone', '=Biz_Email',
                    '=IF(Biz_TaxID="","",TaxName&" no: "&Biz_TaxID)'):
        s.merge(left, 0, 3, "", fmts.chrome("print_sub"))
        ws.write_formula(left, 0, formula, fmts.chrome("print_sub"))
        left += 1

    right = row + 1
    meta = [("Invoice no.", f"={inv('invoice_no')}", "text"),
            ("Invoice date", f"={inv('date')}", "date"),
            ("Due date", f"={inv('due')}", "date"),
            ("Status", f"={inv('pay_status')}", "text"),
            ("Amount due", f"={inv('balance',0)}", "money")]
    for label, formula, style in meta:
        s.merge(right, 4, 5, label, fmts.chrome("label_bold"))
        fmt = fmts.calc(style, align="right")
        ws.merge_range(right, 6, right, LAST_COL, "", fmt)
        ws.write_formula(right, 6, reg.render(formula), fmt)
        right += 1

    row = max(left, right) + 1

    s.merge(row, 0, 3, "BILL TO", fmts.chrome("subsection"))
    s.merge(row, 4, LAST_COL, "SERVICE", fmts.chrome("subsection"))
    row += 1
    block = row
    for formula in (f"={client}", f"={cli('address')}",
                    f'={cli("city")}&" "&{cli("postcode")}',
                    f"={cli('phone')}", f"={cli('email')}"):
        s.merge(block, 0, 3, "", fmts.calc("text"))
        ws.write_formula(block, 0, reg.render(formula), fmts.calc("text"))
        block += 1

    right = row
    service_meta = [
        ("Booking ref", f"={booking}", "text"),
        ("Service", f"={bkg('service')}", "text"),
        ("Pet", f"={bkg('pet')}", "text"),
        ("Service date", f"={bkg('date')}", "date"),
        ("Carer", f"={bkg('staff')}", "text"),
    ]
    for label, formula, style in service_meta:
        s.merge(right, 4, 5, label, fmts.chrome("label_bold"))
        fmt = fmts.calc(style, align="right")
        ws.merge_range(right, 6, right, LAST_COL, "", fmt)
        ws.write_formula(right, 6, reg.render(formula), fmt)
        right += 1
    row = max(block, right) + 1

    # ------------------------------------------------------- line items
    s.merge(row, 0, 3, "Description", fmts.chrome("header_left"))
    s.write(row, 4, "Qty", fmts.chrome("header"))
    s.write(row, 5, "Rate", fmts.chrome("header"))
    s.merge(row, 6, LAST_COL, "Amount", fmts.chrome("header"))
    s.row_height(row, 20)
    row += 1

    s.merge(row, 0, 3, "", fmts.calc("wrap"))
    ws.write_formula(
        row, 0,
        reg.render(f'=IF({inv("description")}="",'
                   f'{bkg("service")},{inv("description")})'),
        fmts.calc("wrap"))
    ws.write_formula(row, 4, reg.render(f'=IF({inv("qty",0)}=0,1,'
                                        f'{inv("qty",0)})'),
                     fmts.calc("number"))
    ws.write_formula(row, 5, reg.render(f'=IF({inv("rate",0)}=0,'
                                        f'{inv("line_total",0)},'
                                        f'{inv("rate",0)})'),
                     fmts.calc("money"))
    ws.merge_range(row, 6, row, LAST_COL, "", fmts.calc("money"))
    ws.write_formula(row, 6, reg.render(f'={inv("line_total",0)}'),
                     fmts.calc("money"))
    row += 1

    s.merge(row, 0, LAST_COL, "Visits covered by this invoice",
            fmts.chrome("note"))
    row += 1
    for n in range(1, 9):
        key = f'({booking})&"|"&{n}'
        vis = (lambda field, key=key:
               f'IFERROR(INDEX([[Visit Log.{field}]],'
               f'MATCH({key},[[Visit Log.line_key]],0)),"")')
        s.merge(row, 0, 3, "", fmts.calc("text"))
        ws.write_formula(
            row, 0,
            reg.render(f'=IF({vis("date")}="","","Visit on "'
                       f'&TEXT({vis("date")},"{cfg.date_format}")'
                       f'&" - "&{vis("service")}'
                       f'&IF({vis("staff")}=""," "," with "&{vis("staff")}))'),
            fmts.calc("text"))
        ws.write_formula(
            row, 4,
            reg.render(f'=IF({vis("duration")}="","",'
                       f'{vis("duration")}&" min")'),
            fmts.calc("text", align="right"))
        s.merge(row, 5, LAST_COL, "", fmts.calc("text"))
        row += 1

    row += 1
    totals = [
        ("Subtotal", f'={inv("subtotal",0)}', "money"),
        ("Additional fees", f'={inv("fees",0)}', "money"),
        ("Discount", f'=-{inv("discount",0)}', "money"),
        ("Tax", f'={inv("tax",0)}', "money"),
        ("TOTAL", f'={inv("total",0)}', "money"),
        ("Deposit / paid", f'=-{inv("paid",0)}', "money"),
    ]
    for label, formula, style in totals:
        s.merge(row, 4, 5, label, fmts.chrome("label_bold"))
        fmt = fmts.calc(style, align="right")
        ws.merge_range(row, 6, row, LAST_COL, "", fmt)
        ws.write_formula(row, 6, reg.render(formula), fmt)
        row += 1
    s.merge(row, 4, 5, "BALANCE DUE", fmts.chrome("total_label"))
    fmt = fmts.chrome("total_value", num_format=s.num_format("money"),
                      font_size=12)
    ws.merge_range(row, 6, row, LAST_COL, "", fmt)
    ws.write_formula(row, 6, reg.render(f'={inv("balance",0)}'), fmt)
    s.row_height(row, 22)
    row += 2

    s.merge(row, 0, LAST_COL, "HOW TO PAY", fmts.chrome("subsection"))
    row += 1
    row = _row(s, fmts, row, "Bank details", "=Biz_Bank",
               value_cols=(2, LAST_COL))
    row = _row(s, fmts, row, "Payment terms",
               '="Payment is due within "&PaymentTermsDays&" days '
               'of the invoice date."', value_cols=(2, LAST_COL))
    row = _row(s, fmts, row, "Late payment",
               '=IF(LateFeePct=0,"",TEXT(LateFeePct,"0%")&'
               '" late fee may be applied to overdue balances.")',
               value_cols=(2, LAST_COL))
    row = _row(s, fmts, row, "Notes", f'={inv("notes")}',
               value_cols=(2, LAST_COL))
    row += 1
    s.merge(row, 0, LAST_COL, "", fmts.chrome("note_box"))
    ws.write_formula(
        row, 0,
        '="Thank you for trusting "&Biz_Name&" with your pets. '
        'Questions about this invoice? Call "&Biz_Phone&" or email "'
        '&Biz_Email&"."', fmts.chrome("note_box"))
    s.row_height(row, 26)

    ws.print_area(2, 0, row, LAST_COL)
    ws.fit_to_pages(1, 1)
    ws.center_horizontally()
    ws.hide_gridlines(2)
    s.protect()
    return s


# ---------------------------------------------------------------------------
# 2. Print Pet Care sheet
# ---------------------------------------------------------------------------

def build_care_sheet(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, CARE_SHEET,
                    tab_color=Palette.primary_soft, landscape=False)
    ws = s.ws
    s.set_col(0, 0, 18)
    s.set_col(1, 1, 16)
    s.set_col(2, 2, 14)
    s.set_col(3, 3, 12)
    s.set_col(4, 4, 14)
    s.set_col(5, 5, 12)
    s.set_col(6, 6, 12)
    s.set_col(7, 7, 14)

    _pick(s, fmts, "Pet to print", "PetLabels", "PrintPetLabel",
          "Pick a pet reference - the care sheet fills itself in. "
          "This row does not print.", default=_first_pet(cfg))

    def pet(field: str, fallback: str = '""') -> str:
        return _index("Pets", field, "PrintPetLabel", "label", fallback)

    owner = pet("owner")

    def cli(field: str) -> str:
        return _index("Clients", field, f"({owner})", "name")

    row = 2
    s.merge(row, 0, LAST_COL, "", fmts.chrome("print_title"))
    ws.write_formula(
        row, 0,
        reg.render(f'="Pet Care Sheet - "&{pet("name")}'),
        fmts.chrome("print_title"))
    s.row_height(row, 28)
    row += 1
    s.merge(row, 0, LAST_COL, "", fmts.chrome("print_sub"))
    ws.write_formula(
        row, 0,
        '="Prepared by "&Biz_Name&" - "&Biz_Phone&" - printed "'
        '&TEXT(TODAY(),"' + cfg.date_format + '")',
        fmts.chrome("print_sub"))
    row += 2

    def block(start: int, title: str, fields: Sequence[Tuple[str, str, str]],
              columns: int = 2) -> int:
        s.merge(start, 0, LAST_COL, title, fmts.chrome("subsection"))
        start += 1
        half = (len(fields) + columns - 1) // columns
        for i, (label, formula, style) in enumerate(fields):
            col_block = i // half if columns > 1 else 0
            r = start + (i % half)
            base = 0 if col_block == 0 else 4
            s.merge(r, base, base + 1, label, fmts.chrome("label_bold"))
            fmt = fmts.calc(style)
            end = base + 3 if base == 0 else LAST_COL
            ws.merge_range(r, base + 2, r, end, "", fmt)
            ws.write_formula(r, base + 2, reg.render(formula), fmt)
        return start + half + 1

    row = block(row, "PET DETAILS", [
        ("Pet name", f'={pet("name")}', "text"),
        ("Type / breed", f'={pet("type")}&" - "&{pet("breed")}', "text"),
        ("Age", f'=IF({pet("age")}="","",{pet("age")}&" years")', "text"),
        ("Gender", f'={pet("gender")}', "text"),
        ("Weight", f'=IF({pet("weight")}="","",{pet("weight")}&" kg")',
         "text"),
        ("Colour & markings", f'={pet("colour")}', "text"),
        ("Microchip", f'={pet("microchip")}', "text"),
        ("Temperament", f'={pet("temperament")}', "text"),
    ])

    row = block(row, "OWNER & EMERGENCY CONTACTS", [
        ("Owner", f'={owner}', "text"),
        ("Phone", f'={cli("phone")}', "text"),
        ("Email", f'={cli("email")}', "text"),
        ("Address", f'={cli("address")}&" "&{cli("city")}', "text"),
        ("Emergency contact", f'={cli("emergency_name")}', "text"),
        ("Emergency phone", f'={cli("emergency_phone")}', "text"),
        ("Home access", f'={cli("key_status")}', "text"),
        ("Access notes", f'={cli("access_notes")}', "text"),
    ])

    row = block(row, "VET & MEDICAL", [
        ("Veterinarian", f'={pet("vet_name")}', "text"),
        ("Vet phone", f'={pet("vet_phone")}', "text"),
        ("Emergency clinic", f'={pet("emerg_clinic")}', "text"),
        ("Clinic phone", f'={pet("emerg_phone")}', "text"),
        ("Vaccination status", f'={pet("vacc_status")}', "text"),
        ("Vaccination expires", f'={pet("vacc_expiry")}', "date"),
        ("Insurance", f'={pet("insurer")}&" "&{pet("policy")}', "text"),
        ("Vet spend authority", f'={cli("vet_limit")}', "money"),
    ])

    row = block(row, "HEALTH, ALLERGIES & MEDICATION", [
        ("Allergies", f'={pet("allergies")}', "text"),
        ("Medical conditions", f'={pet("medical")}', "text"),
        ("Medication", f'={pet("medication")}', "text"),
        ("Dosage", f'={pet("dosage")}', "text"),
        ("Medication times", f'={pet("med_schedule")}', "text"),
        ("Emergency vet consent", f'={cli("vet_consent")}', "text"),
    ])

    row = block(row, "DAILY ROUTINE", [
        ("Food", f'={pet("food")}', "text"),
        ("Portion", f'={pet("portion")}', "text"),
        ("Feeding times", f'={pet("feed_schedule")}', "text"),
        ("Feeding notes", f'={pet("feeding")}', "text"),
        ("Walking & exercise", f'={pet("walking")}', "text"),
        ("Potty / litter", f'={pet("potty")}', "text"),
        ("Grooming", f'={pet("grooming")}', "text"),
        ("Favourites", f'={pet("favourites")}', "text"),
    ])

    s.merge(row, 0, LAST_COL, "SAFETY & HANDLING", fmts.chrome("subsection"))
    row += 1
    for label, formula in (("Risk flag", f'={pet("risk")}'),
                           ("Behaviour issues", f'={pet("behaviour")}'),
                           ("Handling instructions", f'={pet("handling")}'),
                           ("Safety warnings", f'={pet("warnings")}')):
        s.merge(row, 0, 1, label, fmts.chrome("label_bold"))
        fmt = fmts.calc("wrap")
        ws.merge_range(row, 2, row, LAST_COL, "", fmt)
        ws.write_formula(row, 2, reg.render(formula), fmt)
        s.row_height(row, 20)
        row += 1
    row += 1

    s.merge(row, 0, LAST_COL, "RECENT VISITS", fmts.chrome("subsection"))
    row += 1
    s.merge(row, 0, 1, "Date", fmts.chrome("header_left"))
    s.merge(row, 2, 3, "Service", fmts.chrome("header"))
    s.merge(row, 4, 5, "Carer", fmts.chrome("header"))
    s.merge(row, 6, LAST_COL, "Notes", fmts.chrome("header"))
    row += 1
    count = 'COUNTIF([[Visit Log.pet]],PrintPetLabel)'
    for i in range(6):
        key = f'PrintPetLabel&"|"&({count}-{i})'
        vis = (lambda field, key=key:
               f'IFERROR(INDEX([[Visit Log.{field}]],'
               f'MATCH({key},[[Visit Log.pet_key]],0)),"")')
        for label_cols, field, style in (((0, 1), "date", "date"),
                                         ((2, 3), "service", "text"),
                                         ((4, 5), "staff", "text"),
                                         ((6, LAST_COL), "notes", "text")):
            fmt = fmts.calc(style)
            ws.merge_range(row, label_cols[0], row, label_cols[1], "", fmt)
            ws.write_formula(row, label_cols[0],
                             reg.render(f'={vis(field)}'), fmt)
        row += 1
    row += 1

    s.merge(row, 0, LAST_COL,
            "Sitter notes (write on the printed sheet):",
            fmts.chrome("label_bold"))
    row += 1
    for _ in range(4):
        s.merge(row, 0, LAST_COL, "", fmts.chrome("form_line"))
        s.row_height(row, 18)
        row += 1

    ws.print_area(2, 0, row, LAST_COL)
    ws.fit_to_pages(1, 0)
    ws.hide_gridlines(2)
    s.protect()
    return s


# ---------------------------------------------------------------------------
# 3. Print Visit report
# ---------------------------------------------------------------------------

def build_visit_report(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, VISIT_SHEET,
                    tab_color=Palette.primary_soft, landscape=False)
    ws = s.ws
    s.set_col(0, 0, 18)
    s.set_col(1, 1, 14)
    s.set_col(2, 2, 14)
    s.set_col(3, 3, 12)
    s.set_col(4, 4, 14)
    s.set_col(5, 5, 12)
    s.set_col(6, 6, 12)
    s.set_col(7, 7, 14)

    _pick(s, fmts, "Visit to print", "VisitIDs", "PrintVisitID",
          "Pick a visit ID from the Visit Log. This row does not print.",
          default=_first_visit(cfg))

    def vis(field: str, fallback: str = '""') -> str:
        return _index("Visit Log", field, "PrintVisitID", "id", fallback)

    row = 2
    s.merge(row, 0, LAST_COL, "", fmts.chrome("print_title"))
    ws.write_formula(row, 0, '="Visit Report"', fmts.chrome("print_title"))
    s.row_height(row, 28)
    row += 1
    s.merge(row, 0, LAST_COL, "", fmts.chrome("print_sub"))
    ws.write_formula(
        row, 0,
        '="Prepared by "&Biz_Name&" - "&Biz_Phone&" - "&Biz_Email',
        fmts.chrome("print_sub"))
    row += 2

    pairs: List[Tuple[str, str, str, str, str, str]] = [
        ("Visit ID", f'={vis("id")}', "text",
         "Date", f'={vis("date")}', "date"),
        ("Client", f'={vis("client")}', "text",
         "Pet", f'={vis("pet")}', "text"),
        ("Service", f'={vis("service")}', "text",
         "Carer", f'={vis("staff")}', "text"),
        ("Scheduled", f'={vis("sched_start")}', "time",
         "Status", f'={vis("status")}', "text"),
        ("Arrived", f'={vis("arrive")}', "time",
         "Departed", f'={vis("depart")}', "time"),
        ("Minutes on site", f'={vis("duration")}', "int",
         "Punctuality", f'={vis("punctual")}', "text"),
    ]
    s.merge(row, 0, LAST_COL, "VISIT DETAILS", fmts.chrome("subsection"))
    row += 1
    for l1, f1, s1, l2, f2, s2 in pairs:
        for base, label, formula, style in ((0, l1, f1, s1),
                                            (4, l2, f2, s2)):
            s.merge(row, base, base + 1, label, fmts.chrome("label_bold"))
            fmt = fmts.calc(style)
            end = base + 3 if base == 0 else LAST_COL
            ws.merge_range(row, base + 2, row, end, "", fmt)
            ws.write_formula(row, base + 2, reg.render(formula), fmt)
        row += 1
    row += 1

    s.merge(row, 0, LAST_COL, "CARE GIVEN", fmts.chrome("subsection"))
    row += 1
    care = [("Fed", "fed", "text"), ("Fresh water", "water", "text"),
            ("Medication given", "meds", "text"),
            ("Potty / litter", "potty", "text"),
            ("Walk minutes", "walk_mins", "int"),
            ("Distance walked", "walk_distance", "number1"),
            ("Exercise & play", "play", "text"),
            ("Grooming", "grooming", "text")]
    half = (len(care) + 1) // 2
    for i, (label, field, style) in enumerate(care):
        base = 0 if i < half else 4
        r = row + (i % half)
        s.merge(r, base, base + 1, label, fmts.chrome("label_bold"))
        fmt = fmts.calc(style)
        end = base + 3 if base == 0 else LAST_COL
        ws.merge_range(r, base + 2, r, end, "", fmt)
        ws.write_formula(r, base + 2, reg.render(f'={vis(field)}'), fmt)
    row += half + 1

    s.merge(row, 0, LAST_COL, "HOW YOUR PET WAS", fmts.chrome("subsection"))
    row += 1
    for label, field in (("Mood & behaviour", "mood"),
                         ("Appetite", "appetite"),
                         ("Health observations", "health"),
                         ("Visit notes", "notes"),
                         ("Photos / report link", "photos")):
        s.merge(row, 0, 1, label, fmts.chrome("label_bold"))
        fmt = fmts.calc("wrap")
        ws.merge_range(row, 2, row, LAST_COL, "", fmt)
        ws.write_formula(row, 2, reg.render(f'={vis(field)}'), fmt)
        s.row_height(row, 22)
        row += 1
    row += 1

    s.merge(row, 0, 1, "Incident reported", fmts.chrome("label_bold"))
    fmt = fmts.calc("text")
    ws.merge_range(row, 2, row, LAST_COL, "", fmt)
    ws.write_formula(
        row, 2,
        reg.render(f'=IF({vis("incident")}="Yes","Yes - reference "'
                   f'&{vis("incident_ref")},"No")'), fmt)
    row += 2

    s.merge(row, 0, LAST_COL, "", fmts.chrome("note_box"))
    ws.write_formula(
        row, 0,
        '="Thank you for choosing "&Biz_Name&". Any questions about this '
        'visit? Call "&Biz_Phone&"."', fmts.chrome("note_box"))
    s.row_height(row, 24)
    row += 2
    s.merge(row, 0, 2, "Carer signature", fmts.chrome("label_bold"))
    s.merge(row, 3, LAST_COL, "", fmts.chrome("form_line"))

    ws.print_area(2, 0, row, LAST_COL)
    ws.fit_to_pages(1, 1)
    ws.hide_gridlines(2)
    s.protect()
    return s


# ---------------------------------------------------------------------------
# 4. Print Forms - blank paperwork
# ---------------------------------------------------------------------------

#: (title, intro, [field labels], (grid header, grid rows))
FORMS: List[Tuple[str, str, List[str], Optional[Tuple[List[str], int]]]] = [
    ("New Client Registration",
     "Please complete and return before your first booking.",
     ["Client name", "Phone", "Email", "Street address", "City / suburb",
      "Post code", "Emergency contact name", "Emergency contact phone",
      "Preferred contact method", "How did you hear about us?",
      "Home access (key / lockbox / code)", "Alarm instructions",
      "Anyone else with access to the property",
      "Special instructions"],
     None),
    ("Pet Profile & Care Instructions",
     "One form per pet. Attach a photo if you can.",
     ["Pet name", "Type / breed", "Date of birth", "Gender", "Weight",
      "Colour & markings", "Microchip number", "Temperament",
      "Food & portion", "Feeding times", "Medication & dosage",
      "Medication times", "Walking / exercise routine",
      "Potty / litter routine", "Allergies", "Medical conditions",
      "Veterinarian & phone", "Emergency clinic & phone",
      "Pet insurance & policy", "Favourite toys, treats & games",
      "Behaviour warnings", "Handling instructions"],
     None),
    ("Service Agreement & Veterinary Consent",
     "This authorises emergency treatment and confirms the agreed terms.",
     ["Client name", "Pet(s) covered", "Services agreed",
      "Start date", "Rates agreed", "Payment terms",
      "Cancellation policy understood (initial)",
      "Maximum veterinary spend authorised",
      "Preferred veterinary practice",
      "Permission to transport pet by vehicle (yes / no)",
      "Permission to use photos on social media (yes / no)",
      "Client signature", "Date", "Business representative", "Date"],
     None),
    ("Key Handover Receipt",
     "Complete both halves - one for you, one for the client.",
     ["Client name", "Address", "Key tag / reference",
      "Number of keys received", "Date received", "Received by",
      "Client signature", "Date returned", "Returned by",
      "Client signature on return"],
     None),
    ("Incident / Accident Report",
     "Complete on the day. Keep the original with your records.",
     ["Incident reference", "Date & time", "Location", "Pet(s) involved",
      "Client", "Staff present", "Incident type", "Severity",
      "What happened", "Immediate action taken",
      "Veterinary treatment required (yes / no)",
      "Vet / clinic attended", "Cost incurred", "Owner informed (time)",
      "Follow up required", "Prevention / lessons learned",
      "Completed by", "Signature & date"],
     None),
    ("Daily Visit Checklist",
     "Leave this with the client or keep for your records.",
     ["Client", "Pet(s)", "Week commencing", "Carer"],
     (["Date", "In", "Out", "Fed", "Water", "Meds", "Walk", "Potty",
       "Notes"], 14)),
    ("Staff Timesheet",
     "One sheet per person per week.",
     ["Team member", "Week commencing", "Pay rate", "Approved by"],
     (["Date", "Client / job", "Start", "Finish", "Break",
       "Hours", "Distance", "Notes"], 14)),
    ("Mileage Log",
     "Keep this in the vehicle and copy it into the Mileage tab weekly.",
     ["Driver", "Vehicle", "Registration", "Month"],
     (["Date", "From", "To", "Purpose", "Start odo", "End odo",
       "Distance", "Business?"], 16)),
    ("Client Feedback Form",
     "We would love to know how we did.",
     ["Client name", "Date of service", "Carer",
      "Rating out of 5 (circle): 1  2  3  4  5",
      "What went well?", "What could we do better?",
      "Would you recommend us? (yes / no)",
      "May we use your comments as a review? (yes / no)",
      "Signature"],
     None),
    ("Meet & Greet Checklist",
     "Run through this at the first visit.",
     ["Date & time", "Client", "Pet(s)", "Carer"],
     (["Checked", "Item", "Notes", "", "", "", "", ""], 14)),
]

MEET_ITEMS = [
    "Introductions - pet comfortable with the carer",
    "Keys / access tested (door, gate, alarm, lockbox)",
    "Feeding routine and food storage shown",
    "Medication, dosage and storage confirmed",
    "Lead, harness, carrier and towels located",
    "Walking route, pick-up bags and rules agreed",
    "Potty / litter routine and cleaning supplies shown",
    "Emergency contacts and vet details confirmed",
    "Vaccination records sighted",
    "House rules (furniture, rooms, visitors) agreed",
    "Waste, bins and recycling day explained",
    "Preferred updates: photos, messages, frequency",
    "Service agreement signed and consent given",
    "Booking schedule, rates and payment confirmed",
]


def build_forms(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, FORMS_SHEET,
                    tab_color=Palette.primary_soft, landscape=False)
    ws = s.ws
    s.set_col(0, 0, 26)
    s.set_col(1, 7, 11)

    s.merge(0, 0, LAST_COL,
            "Blank forms - print the page you need. Each form starts on a "
            "new page. These are for printing, so nothing here links to "
            "the rest of the workbook.",
            fmts.chrome("note_box"))
    s.row_height(0, 26)

    breaks: List[int] = []
    row = 2
    for title, intro, fields, grid in FORMS:
        if row > 2:
            breaks.append(row)
        s.merge(row, 0, LAST_COL, "", fmts.chrome("print_title"))
        ws.write_formula(row, 0, f'=Biz_Name&" - {title}"',
                         fmts.chrome("print_title"))
        s.row_height(row, 26)
        row += 1
        s.merge(row, 0, LAST_COL, intro, fmts.chrome("print_sub"))
        row += 2

        for label in fields:
            s.merge(row, 0, 1, label, fmts.chrome("form_label"))
            s.merge(row, 2, LAST_COL, "", fmts.chrome("form_line"))
            s.row_height(row, 20)
            row += 1

        if grid:
            headers, lines = grid
            row += 1
            for i, head in enumerate(headers[:LAST_COL + 1]):
                s.write(row, i, head,
                        fmts.chrome("header_left" if i == 0
                                    else "header"))
            s.row_height(row, 18)
            row += 1
            seed = MEET_ITEMS if title.startswith("Meet") else []
            for line in range(lines):
                for i in range(len(headers[:LAST_COL + 1])):
                    if seed and i == 1 and line < len(seed):
                        s.merge(row, 1, LAST_COL, seed[line],
                                fmts.chrome("form_box"))
                        break
                    s.write(row, i, None, fmts.chrome("form_box"))
                s.row_height(row, 18)
                row += 1

        row += 1
        s.merge(row, 0, LAST_COL,
                "", fmts.chrome("print_sub"))
        ws.write_formula(
            row, 0,
            '=Biz_Name&"  |  "&Biz_Phone&"  |  "&Biz_Email',
            fmts.chrome("print_sub"))
        row += 3

    try:
        ws.set_h_pagebreaks(breaks)
    except Exception:          # pragma: no cover - older API guard
        pass

    ws.print_area(2, 0, row, LAST_COL)
    ws.fit_to_pages(1, 0)
    ws.hide_gridlines(2)
    s.protect()
    return s
