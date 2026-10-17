"""Register: AB Tests."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check

NAME = "AB Tests"
ROWS = 40

COLUMNS = [
    dict(header="Test ID", key="id", width=11,
         validate={"validate": "list",
                   "source": ["AB-001", "AB-002", "AB-003", "AB-004",
                              "AB-005", "AB-006", "AB-007", "AB-008"]},
         note="Your own numbering, e.g. AB-001."),
    dict(header="Test Name", key="name", width=22,
         note="What you are testing, in plain words."),
    dict(header="Metric", key="metric", width=12,
         validate={"validate": "list",
                   "source": ["Reach", "Watch time", "Clicks", "Saves",
                              "Sales", "Signups", "Comments"]},
         note="The ONE number that decides it."),
    dict(header="Hypothesis", key="hypothesis", width=32, style="wrap",
         note="What you believe, stated before the test."),
    dict(header="Variant A", key="variant_a", width=24, style="wrap"),
    dict(header="Variant B", key="variant_b", width=24, style="wrap"),
    dict(header="Audience", key="audience", width=12,
         validate={"validate": "list",
                   "source": ["Cold", "Warm", "Mixed"]}),
    dict(header="Start Date", key="start", width=12, style="date",
         validate=date_check()),
    dict(header="Status", key="status", width=13,
         validate={"validate": "list",
                   "source": ["Draft", "Running", "Winner Found",
                              "Cancelled"]}),
    dict(header="Result", key="result", width=10,
         validate={"validate": "list", "source": ["A", "B", "Tie"]},
         note="Which variant won, if any."),
    dict(header="Winner Check", key="winner", width=12,
         is_formula=True,
         formula="=IF($I{r}=\"\",\"\",IF(AND($I{r}=\"Winner Found\","
                 "$J{r}=\"\"),\"Add result\",\"Complete\"))",
         note="Nudges you to record the outcome."),
    dict(header="Notes", key="notes", width=28, style="wrap",
         note="What you will do differently because of this test."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.ab_tests() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="AB Tests",
        subtitle="Opinions are cheap. Test the hook, the CTA, the time - "
                 "then write down what won and act on it.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="One metric per test. If you cannot name the metric, it "
                  "is not a test yet.",
        tab_color="#2E7D8F", freeze_cols=1)
