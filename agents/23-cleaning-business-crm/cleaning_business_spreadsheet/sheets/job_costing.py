"""Job Costing - what each job really cost you."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Job Costing")
    samples = sd.JOB_COSTING if cfg.include_sample_data else []

    columns = [
        Col("id", "ID", 11, "text",
            formula='IF({job_ref}{r}="","",'
                    '"JC-"&TEXT(ROW()-4,"0000"))'),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True},
            note="One costing sheet per job number."),
        Col("date", "Date", 13, "date_locked",
            formula='IF({job_ref}{r}="","",IFERROR(INDEX([[Jobs.date]],'
                    'MATCH({job_ref}{r},[[Jobs.job_number]],0)),""))'),
        Col("client", "Client", 22, "text_locked",
            formula='IF({job_ref}{r}="","",IFERROR(INDEX([[Jobs.client]],'
                    'MATCH({job_ref}{r},[[Jobs.job_number]],0)),""))'),
        Col("revenue", "Revenue", 13, "money_locked",
            formula='IF({job_ref}{r}="","",IFERROR(INDEX([[Jobs.price]],'
                    'MATCH({job_ref}{r},[[Jobs.job_number]],0)),0))'),
        Col("labour", "Labour Cost", 13, "money_locked",
            formula='IF({job_ref}{r}="","",IFERROR('
                    'INDEX([[Jobs.labour_cost]],'
                    'MATCH({job_ref}{r},[[Jobs.job_number]],0)),0))',
            note="Pulled from the Jobs tab (hours x cleaners x loaded "
                 "hourly cost)."),
        Col("supplies", "Supplies Cost", 13, "money_locked",
            formula='IF({job_ref}{r}="","",'
                    'SUMIFS([[Supply Usage.total_cost]],'
                    '[[Supply Usage.job_ref]],{job_ref}{r}))'),
        Col("mileage", "Mileage Cost", 13, "money_locked",
            formula='IF({job_ref}{r}="","",'
                    'SUMIFS([[Mileage.claim]],[[Mileage.job_ref]],'
                    '{job_ref}{r}))'),
        Col("other", "Other Costs", 12, "money",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 1000000},
            note="Anything else - parking, specialist hire, replacement "
                 "of broken items."),
        Col("total_cost", "Total Cost", 13, "money_locked",
            formula='IF({job_ref}{r}="","",'
                    '{labour}{r}+{supplies}{r}+{mileage}{r}+{other}{r})'),
        Col("profit", "Profit", 13, "money_locked",
            formula='IF({job_ref}{r}="","",{revenue}{r}-{total_cost}{r})'),
        Col("margin", "Margin %", 11, "pct_locked",
            formula='IF(OR({job_ref}{r}="",{revenue}{r}=0),"",'
                    '{profit}{r}/{revenue}{r})'),
        Col("flag", "Flag", 14, "text_locked",
            formula='IF({job_ref}{r}="","",IF({revenue}{r}=0,"No revenue",'
                    f'IF({{margin}}{{r}}<{cfg.margin_floor},'
                    '"LOW MARGIN","OK")))',
            note="Jobs under the margin floor need a pricing review."),
    ]

    spec = SheetSpec(
        name="Job Costing",
        title="Job Costing",
        subtitle="The true cost of every job - labour, supplies, travel "
                 "and extras - and the profit it made.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
    spec.col("flag").cf = [
        {"type": "text", "criteria": "containing", "value": "LOW MARGIN",
         "style": "bad"},
        {"type": "text", "criteria": "containing", "value": "No revenue",
         "style": "warning"},
        {"type": "text", "criteria": "containing", "value": "OK",
         "style": "good"},
    ]
    return spec
