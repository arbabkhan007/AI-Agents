"""Timesheets - hours worked, what they cost."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Timesheets")
    samples = sd.TIMESHEETS if cfg.include_sample_data else []

    columns = [
        Col("id", "Entry ID", 11, "text",
            formula='IF({employee}{r}="","",'
                    '"TS-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("employee", "Employee", 20, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True},
            note="Leave blank for non-job time (training, travel)."),
        Col("start", "Start", 9, "time"),
        Col("end", "End", 9, "time"),
        Col("break_min", "Break (min)", 10, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 0, "maximum": 240}),
        Col("hours", "Hours", 9, "decimal_locked",
            formula='IF(OR({start}{r}="",{end}{r}=""),"",'
                    'ROUND(({end}{r}-{start}{r})*24-{break_min}{r}/60,2))',
            note="Calculated from start, end and break."),
        Col("pay_rate", "Pay Rate", 11, "money_locked",
            formula='IF({employee}{r}="","",'
                    'IFERROR(INDEX([[Employees.hourly_pay]],'
                    'MATCH({employee}{r},[[Employees.name]],0)),""))'),
        Col("pay", "Pay", 12, "money_locked",
            formula='IF(OR({employee}{r}="",{hours}{r}=""),"",'
                    'ROUND({hours}{r}*{pay_rate}{r},2))'),
        Col("overtime", "Overtime Hrs", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 16},
            note="Hours paid at the overtime multiplier."),
        Col("overtime_pay", "OT Pay", 11, "money_locked",
            formula='IF({overtime}{r}="","",'
                    'ROUND({overtime}{r}*{pay_rate}{r}*' +
                    str(cfg.overtime_multiplier) + ',2))'),
        Col("approved", "Approved", 10, "center",
            validate={"type": "list", "source": ["Yes", "No", ""]}),
        Col("notes", "Notes", 22, "text"),
    ]

    return SheetSpec(
        name="Timesheets",
        title="Timesheets",
        subtitle="Hours in, pay out. Wages cost flows to Job Costing and "
                 "the Financial Plan through these rows.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
