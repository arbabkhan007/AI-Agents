"""Job Tasks - the checklist items behind each job."""

from __future__ import annotations

from ..config import Config, Palette
from ..formats import FormatBook
from ..layout import Col, SheetSpec


def build_register(cfg: Config, fmts: FormatBook) -> SheetSpec:
    from .. import sample_data as sd

    rows = cfg.row_count("Job Tasks")
    samples = sd.JOB_TASKS if cfg.include_sample_data else []

    columns = [
        Col("id", "Task ID", 11, "text",
            formula='IF({job_ref}{r}="","",'
                    '"TK-"&TEXT(ROW()-4,"0000"))'),
        Col("job_ref", "Job #", 13, "text",
            validate={"type": "list", "source": "=Jobs_Numbers",
                      "ignore_blank": True}),
        Col("step_no", "Step", 7, "int"),
        Col("room_area", "Room / Area", 15, "text",
            validate={"type": "list", "source": [
                "Whole property", "Kitchen", "Bathrooms", "Bedrooms",
                "Living areas", "Hall & stairs", "Windows", "Floors",
                "Office area", "Communal areas", "Exterior", "Other"]}),
        Col("task", "Task", 30, "text",
            note="What has to happen, e.g. 'Oven inside and out'."),
        Col("assigned_to", "Assigned To", 16, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("est_min", "Est. Min", 9, "int",
            validate={"type": "whole", "criteria": "between",
                      "minimum": 0, "maximum": 480}),
        Col("done", "Done", 8, "center",
            validate={"type": "list", "source": ["Yes", "No", ""]},
            note="Tick with Yes - the Jobs tab shows x/y progress."),
        Col("done_by", "Done By", 15, "text",
            validate={"type": "list", "source": "=Employees_Names",
                      "ignore_blank": True}),
        Col("done_at", "Completed At", 13, "date"),
        Col("notes", "Notes", 26, "text"),
        Col("match_key", "Match Key", 12, "text_locked",
            formula='IF({job_ref}{r}="","",'
                    '{job_ref}{r}&"-"&{step_no}{r})',
            hidden=True,
            note="Helper for the printable job sheet. Leave hidden."),
    ]

    spec = SheetSpec(
        name="Job Tasks",
        title="Job Tasks & Checklists",
        subtitle="Break every job into steps. Tick them off as they are "
                 "done - the Jobs tab and the dashboard read the ticks.",
        columns=columns,
        rows=rows,
        samples=samples,
        tab_color=Palette.primary,
    )
    spec.col("done").cf = [
        {"type": "text", "criteria": "containing", "value": "Yes",
         "style": "good"},
    ]
    return spec
