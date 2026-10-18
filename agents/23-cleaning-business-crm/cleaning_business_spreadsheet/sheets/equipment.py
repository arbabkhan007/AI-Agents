"""The Equipment register."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Equipment")
    samples = sd.EQUIPMENT if cfg.include_sample_data else []
    interval = cfg.maintenance_days

    columns = [
        Col("id", "Asset ID", 11, "text",
            formula='IF({name}{r}="","",'
                    '"EQ-"&TEXT(ROW()-4,"000"))'),
        Col("name", "Equipment", 24, "text"),
        Col("category", "Category", 14, "center",
            validate={"type": "list", "source": [
                "Vacuum", "Floor machine", "Pressure washer", "Steamer",
                "Vehicle", "Tool", "Safety", "Other"]}),
        Col("serial", "Serial #", 14, "text"),
        Col("purchase_date", "Bought", 13, "date"),
        Col("purchase_cost", "Cost", 12, "money"),
        Col("condition", "Condition", 12, "center",
            validate={"type": "list", "source": [
                "Excellent", "Good", "Fair", "Poor", "Retired"]}),
        Col("status", "Status", 13, "center",
            validate={"type": "list", "source": [
                "In service", "In for repair", "Retired", "Missing"]}),
        Col("last_service", "Last Service", 13, "date"),
        Col("next_service", "Next Service", 13, "date_locked",
            formula='IF({last_service}{r}="","",{last_service}{r}+' +
                    str(interval) + ')',
            note=f"Last service plus {interval} days."),
        Col("assigned_to", "Assigned To", 16, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("location", "Location", 14, "text"),
        Col("notes", "Notes", 22, "text"),
        Col("service_due", "Service Due?", 12, "text_locked",
            formula='IF({name}{r}="","",IF({next_service}{r}="","-",'
                    f'IF(TODAY()>{{next_service}}{{r}}-{cfg.reminder_days},'
                    '"DUE SOON","OK")))'),
    ]

    spec = SheetSpec(
        name="Equipment",
        title="Equipment & Maintenance",
        subtitle="Every machine and vehicle, its condition, and when it "
                 "is next due a service.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.accent,
    )
    spec.col("service_due").cf = [
        {"type": "text", "criteria": "containing", "value": "DUE SOON",
         "style": "warning"},
        {"type": "text", "criteria": "containing", "value": "OK",
         "style": "good"},
    ]
    spec.col("status").cf = [
        {"type": "text", "criteria": "containing", "value": "Retired",
         "style": "bad"},
        {"type": "text", "criteria": "containing", "value": "In for repair",
         "style": "warning"},
    ]
    return spec
