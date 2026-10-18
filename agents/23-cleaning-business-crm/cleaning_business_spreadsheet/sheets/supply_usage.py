"""Supply Usage - what each job used."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Supply Usage")
    samples = sd.SUPPLY_USAGE if cfg.include_sample_data else []

    columns = [
        Col("id", "Usage ID", 11, "text",
            formula='IF({supply}{r}="","",'
                    '"SU-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True}),
        Col("supply", "Supply", 24, "text",
            validate={"type": "list", "source": "=Supplies_Names",
                      "ignore_blank": True}),
        Col("qty", "Qty Used", 10, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 100000}),
        Col("unit_cost", "Unit Cost", 11, "money_locked",
            formula='IF({supply}{r}="","",'
                    'IFERROR(INDEX([[Supplies.cost_per_unit]],'
                    'MATCH({supply}{r},[[Supplies.name]],0)),0))'),
        Col("total_cost", "Total Cost", 12, "money_locked",
            formula='IF({supply}{r}="","",'
                    'ROUND({qty}{r}*{unit_cost}{r},2))',
            note="Flows into the job's total cost and the supplies "
                 "expense category."),
        Col("employee", "Logged By", 16, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("notes", "Notes", 22, "text"),
    ]

    return SheetSpec(
        name="Supply Usage",
        title="Supply Usage",
        subtitle="Every bottle, box and roll that leaves the store room, "
                 "tagged with the job it was used on.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
