"""
Budget - planned versus actual food spend, month by month.

The grocery column is read from the Grocery Spending tab, the waste column
from the Food Waste tab, and the planned columns come from Settings.  The
summary at the top shows the year to date position for the planning year.
"""

from __future__ import annotations

try:
    from ..config import Config, Palette
    from ..layout import Col, Registry, SheetSpec
    from ..writer import Writer
except ImportError:                        # pragma: no cover
    from config import Config, Palette
    from layout import Col, Registry, SheetSpec
    from writer import Writer


def build(writer: Writer, registry: Registry, cfg: Config, ws) -> SheetSpec:
    lists = registry.rng
    gs_month = lists("Grocery Spending", "month")
    gs_total = lists("Grocery Spending", "line_total")
    fw_month = lists("Food Waste", "month")
    fw_cost = lists("Food Waste", "cost")

    columns = [
        Col("month", "Month", 12, "text", group="when",
            note="Type it as 'Jan 2026' to match the other tabs."),
        Col("planned_groceries", "Planned groceries", 13, "calc",
            group="groceries",
            formula='=IF({month}{r}="","",Weekly_Budget*52/12)'),
        Col("actual_groceries", "Actual groceries", 13, "calc",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + gs_total + ',' + gs_month + ','
                    '{month}{r}))'),
        Col("variance", "Variance", 11, "calc",
            formula='=IF({month}{r}="","",'
                    '{planned_groceries}{r}-{actual_groceries}{r})'),
        Col("planned_eating_out", "Planned eating out", 13, "calc",
            group="eating out",
            formula='=IF({month}{r}="","",Eating_Out_Budget)'),
        Col("actual_eating_out", "Actual eating out", 13, "money",
            validate={"type": "decimal", "between": 0, "and": 100000}),
        Col("eating_out_variance", "Variance", 11, "calc",
            formula='=IF({month}{r}="","",'
                    '{planned_eating_out}{r}-'
                    'IF({actual_eating_out}{r}="",0,'
                    '{actual_eating_out}{r}))'),
        Col("waste_cost", "Waste cost", 11, "calc", group="waste",
            formula='=IF({month}{r}="","",'
                    'SUMIFS(' + fw_cost + ',' + fw_month + ','
                    '{month}{r}))'),
        Col("total_planned", "Total planned", 12, "calc",
            group="totals",
            formula='=IF({month}{r}="","",'
                    '{planned_groceries}{r}+{planned_eating_out}{r})'),
        Col("total_actual", "Total actual", 12, "calc",
            formula='=IF({month}{r}="","",'
                    '{actual_groceries}{r}+'
                    'IF({actual_eating_out}{r}="",0,'
                    '{actual_eating_out}{r})+{waste_cost}{r})'),
        Col("total_variance", "Total variance", 12, "calc",
            formula='=IF({month}{r}="","",'
                    '{total_planned}{r}-{total_actual}{r})'),
        Col("rank", "Spend rank", 10, "calc", group="rankings",
            formula='=IF({total_actual}{r}="","",'
                    'COUNTIFS({total_actual_first}:{total_actual_last},'
                    '">"&{total_actual}{r})+1)'),
        Col("status", "Status", 14, "calc",
            formula='=IF({month}{r}="","",'
                    'IF({total_variance}{r}="","",'
                    'IF({total_variance}{r}<0,"Over budget",'
                    'IF({total_variance}{r}<Monthly_Budget*0.1,'
                    '"Close","Under budget"))))'),
        Col("running_total", "Running total", 12, "calc",
            formula='=IF({total_actual}{r}="","",'
                    'SUM({total_actual_first}:{total_actual}{r}))'),
        Col("notes", "Notes", 30, "text_wrap"),
    ]

    spec = SheetSpec(
        name="Budget",
        title="Budget",
        subtitle="Planned versus actual food spend, month by month",
        columns=columns,
        rows=cfg.row_count("Budget"),
        header_row=16,
        tab_color=Palette.accent,
        freeze_cols=1,
    )
    registry.add(spec)
    return spec


def render(ws, spec: SheetSpec, writer: Writer, cfg: Config) -> None:
    f, p = writer.fmt, Palette
    writer.grid_off(ws)
    ws.set_column(0, 0, 14)
    ws.set_column(1, 2, 14)
    ws.set_column(3, 3, 12)
    ws.set_column(4, 5, 14)
    ws.set_column(6, 6, 12)
    ws.set_column(7, 7, 12)
    ws.set_column(8, 10, 13)
    ws.set_column(11, 11, 11)
    ws.set_column(12, 12, 14)
    ws.set_column(13, 13, 13)
    ws.set_column(14, 14, 30)

    ws.set_row(0, 30)
    ws.merge_range(0, 0, 0, 10, "BUDGET", f["title"])
    ws.set_row(1, 18)
    ws.merge_range(1, 0, 1, 10,
                   "Planned versus actual food spend, month by month",
                   f["subtitle"])
    ws.set_row(2, 20)
    ws.merge_range(2, 0, 2, 10,
                   "  |  Dashboard   |   Settings   |   Grocery Spending   "
                   "|   Food Waste   |   Reports", f["nav"])

    reg = writer.registry
    month_rng = reg.rng("Budget", "month")
    actual_rng = reg.rng("Budget", "actual_groceries")
    total_rng = reg.rng("Budget", "total_actual")
    waste_rng = reg.rng("Budget", "waste_cost")

    ws.set_row(4, 22)
    ws.merge_range(4, 0, 4, 10, "  YEAR TO DATE", f["section"])
    ws.write(5, 0, "Planning year", f["label"])
    ws.write_formula(5, 1, "=Plan_Year", f["calc_number"])

    tiles = [
        ("Grocery spend YTD", f'=SUMIFS({actual_rng},{month_rng},"<>")',
         "kpi_value_money", 3),
        ("Total food spend YTD", f'=SUM({total_rng})', "kpi_value_money", 5),
        ("Waste cost YTD", f'=SUM({waste_rng})', "kpi_value_money", 7),
        ("Monthly budget", "=Monthly_Budget", "kpi_value_money", 9),
    ]
    for label, formula, style, col in tiles:
        ws.write(7, col, label, f["kpi_label"])
        ws.write_formula(8, col, formula, f[style])
    ws.set_row(8, 30)

    ws.write(10, 0, "Average month", f["label"])
    ws.write_formula(10, 1, f'=IFERROR(AVERAGE({total_rng}),0)',
                     f["total_money"])
    ws.write(10, 2, "Months over budget", f["label"])
    ws.write_formula(10, 3,
                     '=COUNTIFS(' + reg.rng("Budget", "status")
                     + ',"Over budget")', f["calc_number"])
    ws.write(10, 4, "Months under", f["label"])
    ws.write_formula(10, 5,
                     '=COUNTIFS(' + reg.rng("Budget", "status")
                     + ',"Under budget")', f["calc_number"])
    ws.write(10, 6, "Waste as % of spend", f["label"])
    ws.write_formula(10, 7,
                     f'=IFERROR(SUM({waste_rng})/SUM({actual_rng}),0)',
                     f["calc_percent"])
    ws.write(10, 8, "Target", f["label"])
    ws.write_formula(10, 9, "=Waste_Reduction_Target", f["calc_percent"])

    writer.write_note(ws, 12, 0,
                      "Add one row per month. The planned columns come from "
                      "Settings, the actual grocery and waste columns come "
                      "from the Grocery Spending and Food Waste tabs, and "
                      "you type in what you spent eating out.", width=10)

    writer.register(ws, spec)
    writer.widths(ws, spec)
    writer.freeze(ws, spec)
    ws.set_tab_color(Palette.accent)
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.repeat_rows(0, spec.header_row - 1)
    ws.print_area(0, 0, spec.last_data_row - 1, spec.last_col_index)
