"""13 Records & Milestones - automatic PRs, cardio records, plate maths.

The register on the left is the non-scale-victories log (input).  The
block on the right mirrors the exercise library and pulls each
movement's heaviest lift, best estimated 1RM, the date it happened and
the PR count straight out of the log with SUMPRODUCT(MAX(...)) and
COUNTIFS - no array formulas, no macros.  Below it: the plate
calculator lifters screenshot, cardio records and consistency marks.
"""

from __future__ import annotations

from ..config import BAR_KG, BAR_LB, PLATES_KG, PLATES_LB, Config
from ..layout import Col, SheetSpec, col_letter, quote_sheet
from ..writer import SheetWriter, date_check, list_from
from .. import sample_data

NAME = "13 Records & Milestones"
LIB = "6 Exercise Library"
LOG = "5 Workout Log"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="13  Records & Milestones",
        subtitle="Personal records detect themselves; the wins that never "
                 "show on a scale get written down here.",
        tab_color="#E4572E",
        rows=cfg.row_count("Non-Scale Victories"),
        freeze_cols=2,
        help_text="Left: your non-scale victories - clothes, energy, "
                  "lifts, sleep, mood - with a reward note. Right: the "
                  "automatic record book and the plate calculator.",
        columns=[
            Col("id", "ID", 8, "id",
                formula='="N-"&TEXT(ROW()-{first}+1,"000")'),
            Col("date", "Date", 12, "date", validate=date_check()),
            Col("category", "Category", 13, "text",
                validate=list_from("ListNSV")),
            Col("victory", "The win", 40, "wrap",
                note="The trouser size, the stairwell, the rep that "
                     "moved, the night you slept."),
            Col("reward", "Reward note", 26, "wrap",
                note="What you promised yourself for getting here."),
        ],
        samples=sample_data.nsv_rows(cfg)
        if cfg.include_sample_data else [],
    )


def decorate(sheet: SheetWriter, fmts, cfg: Config, reg) -> None:
    spec_ = reg[NAME]
    lib = reg[LIB]
    log = reg[LOG]
    ql = quote_sheet(LOG)
    qe = quote_sheet(LIB)

    ex = f"{ql}!${log.letter('exercise')}${log.first_data_row}:" \
         f"${log.letter('exercise')}${log.last_data_row}"
    kg = f"{ql}!${log.letter('kg')}${log.first_data_row}:" \
         f"${log.letter('kg')}${log.last_data_row}"
    e1 = f"{ql}!${log.letter('e1rm')}${log.first_data_row}:" \
         f"${log.letter('e1rm')}${log.last_data_row}"
    vol = f"{ql}!${log.letter('vol')}${log.first_data_row}:" \
          f"${log.letter('vol')}${log.last_data_row}"
    dt = f"{ql}!${log.letter('date')}${log.first_data_row}:" \
         f"${log.letter('date')}${log.last_data_row}"
    pr = f"{ql}!${log.letter('pr')}${log.first_data_row}:" \
         f"${log.letter('pr')}${log.last_data_row}"
    rownum = f"ROW({ql}!${log.letter('exercise')}${log.first_data_row}:" \
             f"${log.letter('exercise')}${log.last_data_row})"

    col0 = 7  # H
    top = 3
    sheet.merge(top, col0, col0 + 5,
                "AUTOMATIC RECORD BOOK - reads the workout log",
                sheet.f.chrome("section"))
    heads = ["Exercise", "Heaviest", "Best e1RM", "Date of best",
             "Best set volume", "PRs"]
    for i, text in enumerate(heads):
        sheet.write(top + 1, col0 + i, text, sheet.f.chrome("header"))
    for i, width in enumerate([28, 10, 11, 13, 13, 7]):
        sheet.set_col(col0 + i, col0 + i, width)
    row = top + 2
    n_lib = lib.rows
    for offset in range(n_lib):
        lib_row = lib.first_data_row + offset
        name_ref = f"{qe}!${lib.letter('name')}${lib_row}"
        cond = f"({ex}=$H{row + 1})"
        best_e1 = f"SUMPRODUCT(MAX({cond}*{e1}))"
        best_kg = f"SUMPRODUCT(MAX({cond}*{kg}))"
        best_vol = f"SUMPRODUCT(MAX({cond}*{vol}))"
        best_row = f"SUMPRODUCT(MAX({cond}*({e1}={best_e1})*{rownum}))"
        sheet.formula(row, col0, f'=IF({name_ref}="","",{name_ref})',
                      sheet.f.calc("text"))
        sheet.formula(row, col0 + 1,
                      f'=IF($H{row + 1}="","",IF({best_kg}=0,"",IF('
                      f'Units="Imperial",{best_kg}/KgPerLb,{best_kg})))',
                      sheet.f.calc("number1"))
        sheet.formula(row, col0 + 2,
                      f'=IF($H{row + 1}="","",IF({best_e1}=0,"",IF('
                      f'Units="Imperial",{best_e1}/KgPerLb,{best_e1})))',
                      sheet.f.calc("number1"))
        sheet.formula(row, col0 + 3,
                      f'=IF(OR($H{row + 1}="",{best_e1}=0),"",INDEX({dt},'
                      f'{best_row}-{log.first_data_row}+1))',
                      sheet.f.calc("date"))
        sheet.formula(row, col0 + 4,
                      f'=IF(OR($H{row + 1}="",{best_vol}=0),"",IF('
                      f'Units="Imperial",{best_vol}/KgPerLb,{best_vol}))',
                      sheet.f.calc("number1"))
        sheet.formula(row, col0 + 5,
                      f'=IF($H{row + 1}="","",COUNTIFS({ex},$H{row + 1},'
                      f'{pr},"PR"))',
                      sheet.f.calc("int"))
        row += 1

    # ---- plate calculator -------------------------------------------------
    row += 2
    row = sheet.section(row, "PLATE CALCULATOR", col0 + 5, first_col=col0)
    row = sheet.field(row, "Bar load (your unit)", 100.0, style="number1",
                      label_col=col0, value_col=col0 + 1,
                      help_text="Total bar weight including the bar. The "
                                "calculator splits it per side.")
    target = f"${col_letter(col0 + 1)}${row}"
    row = sheet.field(row, "Bar alone",
                      formula='IF(Units="Imperial",%s,%s)'
                              % (BAR_LB, BAR_KG),
                      style="number1", label_col=col0,
                      value_col=col0 + 1,
                      help_text="20 kg / 45 lb, edit if your bar differs.")
    bar = f"${col_letter(col0 + 1)}${row}"
    row += 1
    # per-side remainder chain over the plate denominations
    row = sheet.table_head(row, col0,
                           ["Plate", "Per side", "Running remainder"],
                           widths=None)
    rem = f"MAX(0,({target}-{bar})/2)"
    plate_rows = []
    for plate in (PLATES_LB if not cfg.metric else PLATES_KG):
        sheet.write(row, col0, plate, sheet.f.input("number1"))
        sheet.formula(row, col0 + 1,
                      f'=IF({target}="","",INT(({rem})/{plate}))',
                      sheet.f.calc("int"))
        sheet.formula(row, col0 + 2,
                      f'=IF({target}="","",({rem})-INT(({rem})/{plate})*'
                      f'{plate})',
                      sheet.f.calc("number1"))
        plate_rows.append((plate, row))
        rem = f"${col_letter(col0 + 2)}${row + 1}"
        row += 1
    sheet.merge(row, col0, col0 + 5,
                "Load per side:", sheet.f.chrome("label_bold"))
    row += 1
    sheet.merge(row, col0, col0 + 5,
                "=" + " & ".join(
                    [f'IF(${col_letter(col0 + 1)}${r}=0,"",IF('
                     f'${col_letter(col0 + 1)}${r}=0,""," ")&TEXT('
                     f'${col_letter(col0 + 1)}${r},"0")&" x "&TEXT('
                     f'{p},"0.##")&"  ")' for p, r in plate_rows]),
                sheet.f.chrome("label"))
    row += 2

    # ---- cardio records and consistency -----------------------------------
    ca = reg["7 Cardio & Activity"]
    qc = quote_sheet(ca.name)
    c_km = f"{qc}!${ca.letter('km')}${ca.first_data_row}:" \
           f"${ca.letter('km')}${ca.last_data_row}"
    c_pace = f"{qc}!${ca.letter('pace')}${ca.first_data_row}:" \
             f"${ca.letter('pace')}${ca.last_data_row}"
    c_dur = f"{qc}!${ca.letter('dur')}${ca.first_data_row}:" \
            f"${ca.letter('dur')}${ca.last_data_row}"
    row = sheet.section(row, "CARDIO RECORDS & CONSISTENCY", col0 + 5,
                        first_col=col0)
    lines = [
        ("Longest distance",
         f'=IF(SUMPRODUCT(MAX({c_km}))=0,"",IF(Units="Imperial",'
         f'SUMPRODUCT(MAX({c_km}))/KmPerMi,SUMPRODUCT(MAX({c_km}))))',
         "number1"),
        ("Fastest pace (min/km)",
         f'=IF(SUMPRODUCT(MAX(({c_pace}>0)*{c_pace}))=0,"",'
         f'SUMPRODUCT(MIN(({c_pace}>0)*{c_pace}+(1-({c_pace}>0))*9999)))',
         "number1"),
        ("Longest single session (min)",
         f'=IF(SUMPRODUCT(MAX({c_dur}))=0,"",SUMPRODUCT(MAX({c_dur})))',
         "number1"),
        ("Sessions in the last 30 days",
         f'=COUNTIFS({dt},">="&TODAY()-29,{dt},"<="&TODAY())', "int"),
        ("Training minutes, last 7 days",
         f'=SUMIFS({ql}!${log.letter("dur")}${log.first_data_row}:'
         f'${log.letter("dur")}${log.last_data_row},{dt},">="&TODAY()-6,'
         f'{dt},"<="&TODAY())', "int"),
        ("Weeks with at least one logged session",
         f'=SUMPRODUCT(({ql}!${log.letter("wstart")}${log.first_data_row}:'
         f'${log.letter("wstart")}${log.last_data_row}<>"")/COUNTIFS('
         f'{ql}!${log.letter("wstart")}${log.first_data_row}:'
         f'${log.letter("wstart")}${log.last_data_row},'
         f'{ql}!${log.letter("wstart")}${log.first_data_row}:'
         f'${log.letter("wstart")}${log.last_data_row}))',
         "int"),
    ]
    for label, formula, style in lines:
        sheet.merge(row, col0, col0 + 3, label,
                    sheet.f.chrome("label_bold"))
        sheet.formula(row, col0 + 4, formula, sheet.f.calc(style))
        row += 1
    sheet.note(row + 1, "Records recalculate the moment a better row "
                        "exists in the log. Nothing on this tab is typed "
                        "except the victories and the bar load.",
               col0 + 5, first_col=col0, height=26)
    sheet.finish(freeze_row=4, freeze_col=2,
                 print_area=f"$A$1:${col_letter(col0 + 5)}$"
                            f"{spec_.last_data_row}")
