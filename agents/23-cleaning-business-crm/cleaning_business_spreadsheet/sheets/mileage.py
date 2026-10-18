"""The Mileage register - travel between jobs."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Mileage")
    samples = sd.MILEAGE if cfg.include_sample_data else []
    dist = cfg.distance_unit
    rate = cfg.travel_rate

    columns = [
        Col("id", "Trip ID", 11, "text",
            formula='IF({distance}{r}="","",'
                    '"ML-"&TEXT(ROW()-4,"0000"))'),
        Col("date", "Date", 13, "date",
            validate={"type": "date", "criteria": "between",
                      "minimum": "DATE(2020,1,1)",
                      "maximum": "DATE(2100,1,1)"}),
        Col("employee", "Employee", 18, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True}),
        Col("client", "Client", 20, "text",
            validate={"type": "list", "source": "=Clients_Names",
                      "ignore_blank": True}),
        Col("purpose", "Purpose", 22, "text",
            note="Job travel, supply run, estimate visit..."),
        Col("start_odometer", f"Start ({dist})", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 1000000}),
        Col("end_odometer", f"End ({dist})", 11, "decimal",
            validate={"type": "decimal", "criteria": "between",
                      "minimum": 0, "maximum": 1000000}),
        Col("distance", f"Distance ({dist})", 11, "decimal_locked",
            formula='IF(OR({start_odometer}{r}="",{end_odometer}{r}=""),'
                    '"",MAX(0,{end_odometer}{r}-{start_odometer}{r}))'),
        Col("rate", "Rate / Unit", 11, "money_locked",
            formula=f'IF({{distance}}{{r}}="","",{rate})',
            note=f"{cfg.currency_symbol}{rate:.2f} per {dist} - change "
                 "the reimbursement rate on the Settings tab and "
                 "rebuild."),
        Col("claim", "Claim", 12, "money_locked",
            formula='IF({distance}{r}="","",'
                    'ROUND({distance}{r}*{rate}{r},2))',
            note="Flows into the job's total cost."),
        Col("notes", "Notes", 22, "text"),
    ]

    return SheetSpec(
        name="Mileage",
        title="Mileage Log",
        subtitle="Every business trip, reimbursed at your mileage rate "
                 "and charged to the job where it belongs.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
