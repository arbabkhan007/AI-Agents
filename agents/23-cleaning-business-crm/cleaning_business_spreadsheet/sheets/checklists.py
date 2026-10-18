"""Checklists - the master task list by service type."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Checklists")
    samples = sd.CHECKLISTS if cfg.include_sample_data else []

    columns = [
        Col("id", "ID", 10, "text",
            formula='IF({service}{r}="","",'
                    '"CK-"&TEXT(ROW()-4,"0000"))'),
        Col("service", "Service", 22, "text",
            validate={"type": "list", "source": "=Services_Names",
                      "ignore_blank": True},
            note="Which service this task belongs to."),
        Col("room_area", "Room / Area", 15, "text",
            validate={"type": "list", "source": [
                "Whole property", "Kitchen", "Bathrooms", "Bedrooms",
                "Living areas", "Hall & stairs", "Windows", "Floors",
                "Office area", "Communal areas", "Exterior", "Other"]}),
        Col("step_no", "Step", 7, "int"),
        Col("item", "Task", 34, "text"),
        Col("required", "Required", 10, "center",
            validate={"type": "list", "source": ["Yes", "No", ""]}),
        Col("est_min", "Est. Min", 9, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 0, "maximum": 480}),
        Col("kit", "Kit / Chemicals", 18, "text"),
        Col("standard", "Standard", 22, "text",
            note="What 'done properly' looks like."),
    ]

    return SheetSpec(
        name="Checklists",
        title="Service Checklists",
        subtitle="The master list of what each service includes. Print a "
                 "job sheet and the crew knows exactly what is expected.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
