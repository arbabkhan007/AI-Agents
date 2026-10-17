"""Register: Campaigns, with a live ROI helper block."""

from __future__ import annotations

from .. import sample_data
from ..layout import SheetSpec, rows_to_last
from ..writer import date_check, number_check

NAME = "Campaigns"
ROWS = 30
LAST_COL = 17         # R

COLUMNS = [
    dict(header="Campaign ID", key="id", width=11,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",\"CMP-\"&TEXT({r}-{first}+1,\"000\"))"),
    dict(header="Campaign Name", key="name", width=24,
         note="The name used in the Content Calendar drop down."),
    dict(header="Start Date", key="start", width=12, style="date",
         validate=date_check()),
    dict(header="End Date", key="end", width=12, style="date",
         validate=date_check()),
    dict(header="Goal", key="goal", width=11,
         validate={"validate": "list", "source": "=GoalList"}),
    dict(header="Target Audience", key="audience", width=20,
         style="wrap", note="Persona names work well here."),
    dict(header="Offer / Hook", key="offer", width=22, style="wrap"),
    dict(header="Primary Platforms", key="platforms", width=22,
         style="wrap"),
    dict(header="Budget", key="budget", width=12, style="money",
         validate=number_check(0, 1000000)),
    dict(header="Actual Spend", key="spent", width=12, style="money",
         is_formula=True,
         formula="=SUMIFS([[Budget.actual]],[[Budget.campaign]],$B{r})",
         note="Pulled live from the Budget tab."),
    dict(header="Status", key="status", width=11,
         validate={"validate": "list", "source": "=CampaignStatusList"}),
    dict(header="Owner", key="owner", width=14,
         validate={"validate": "list", "source": "=TeamNames"}),
    dict(header="Assets Ready", key="assets", width=10, style="int",
         is_formula=True,
         formula="=COUNTIFS([[Assets.campaign]],$B{r},"
                 "[[Assets.status]],\"In Use\")+COUNTIFS("
                 "[[Assets.campaign]],$B{r},[[Assets.status]],\"Ready\")",
         note="Ready or in-use assets tagged to this campaign."),
    dict(header="Content Pieces", key="pieces", width=11, style="int",
         is_formula=True,
         formula="=COUNTIF([[Content Calendar.campaign]],$B{r})",
         note="Calendar rows tagged to this campaign."),
    dict(header="Notes", key="notes", width=30, style="wrap"),
    dict(header="Spend Helper", key="rank_key", width=9, hidden=True,
         is_formula=True,
         formula="=IF($B{r}=\"\",\"\",COUNT($I$first:$I{r})+{r}*0.000001)"),
    dict(header="Progress", key="progress", width=12, style="percent",
         is_formula=True,
         formula="=IF($K{r}=\"Complete\",1,IF($C{r}=\"\",0,IF($D{r}=\"\",0,"
                 "IF($K{r}=\"Planning\",0,MIN(1,MAX(0,(Report_Date"
                 "-$C{r})/MAX(1,$D{r}-$C{r})))))))",
         note="Time progress through the campaign window."),
    dict(header="Budget Health", key="health", width=13,
         is_formula=True,
         formula="=IF($I{r}=0,IF($J{r}=0,\"No budget\",\"Overspend\"),"
                 "IF($J{r}=$I{r},\"On plan\",IF($J{r}<$I{r},\"Under\","
                 "\"Overspend\")))",
         note="Compares actual spend with the budget."),
]


def spec(cfg) -> SheetSpec:
    samples = sample_data.campaigns() if cfg.include_sample_data else []
    rows = cfg.row_count(NAME) or ROWS
    return SheetSpec(
        name=NAME, title="Campaigns",
        subtitle="The big pushes behind the daily posts. Budget columns "
                 "fill themselves from the Budget tab.",
        columns=COLUMNS, rows=rows, samples=samples,
        first_data_row=6, last_data_row=rows_to_last(6, rows),
        help_text="Campaign Name is the value used in the Content Calendar, "
                  "so name it exactly as you want to see it there.",
        tab_color="#C98F5B", freeze_cols=2)


def decorate(sheet, fmts, cfg, reg=None) -> None:
    spec_obj = sheet.reg[NAME]
    first, last = spec_obj.first_data_row, spec_obj.last_data_row
    row = last + 2
    row = sheet.section(row, "Campaign ROI helper - live", LAST_COL)
    headers = ["Campaign", "Budget", "Actual spend", "Health"]
    spans = [(0, 3), (4, 5), (6, 7), (8, 10)]
    for (c0, c1), head in zip(spans, headers):
        sheet.merge(row, c0, c1, head, fmts.chrome("header"))
    row += 1
    n = max(len(spec_obj.samples), 6)
    for offset in range(n):
        rank = offset + 1
        fmt_label = fmts.cell("text", "calc")
        fmt_money = fmts.cell("money", "calc")
        fmt_text = fmts.cell("text", "calc")
        name_formula = (
            "=IFERROR(INDEX($B${first}:$B${last},"
            "MATCH(SMALL($P${first}:$P${last},{n}),"
            "$P${first}:$P${last},0)),\"\")"
        ).format(first=first, last=last, n=rank)
        sheet.merge(row, 0, 3, "", fmt_label)
        sheet.ws.write_formula(row, 0, sheet.reg.render(name_formula),
                               fmt_label)
        for (c0, c1), letter, fmt in (((4, 5), "I", fmt_money),
                                      ((6, 7), "J", fmt_money),
                                      ((8, 10), "R", fmt_text)):
            sheet.merge(row, c0, c1, "", fmt)
            formula = (f"=IF($A{row + 1}=\"\",\"\",INDEX(${letter}${first}:"
                       f"${letter}${last},MATCH($A{row + 1},$B${first}:"
                       f"$B${last},0)))")
            sheet.ws.write_formula(row, c0, sheet.reg.render(formula), fmt)
        row += 1
