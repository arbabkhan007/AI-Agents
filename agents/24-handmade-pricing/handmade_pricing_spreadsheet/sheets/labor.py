"""The Labor tab - every hour that goes into the shop.

Two kinds of row live here and the tab tells them apart on its own:

* a row with a product against it is **production time** - it belongs to that
  product's cost, and the Products tab already counts it through the craft
  tabs or the minutes typed there;
* a row with no product is **shop time** - photography, listing copy, packing,
  fair setup. That is overhead, and `overhead_share` totals it so the monthly
  overhead figure on Settings can be checked against what was really spent.

`loaded_cost` is the honest number: the rate you pay plus the payroll burden
from Settings. `rate_check` flags anything under the minimum wage, including
your own rate if you have been underpaying yourself.
"""

from __future__ import annotations

from typing import Any, List

from ..config import Config, Palette
from ..layout import SheetSpec
from .common import (calc_col, date_col, fetch, id_col, int_col, list_col,
                     money_col, num_col, product_col, row_ref, samples,
                     spec_defaults, text_col, time_col, wrap_col, yesno_col)

P = Palette

NAME = "Labor"

SUBTITLE = ("Time spent making and time spent running the shop, what it cost "
            "and where it belongs.")

HELP = ("Type the date, who worked, the task and the hours. Add a product and "
        "the time counts as production; leave it blank and the time counts as "
        "shop overhead. The rate defaults to nothing - type it, or the "
        "workbook will assume the row is free.")


def spec(cfg: Config) -> SheetSpec:
    data = samples(cfg, NAME)

    lid = row_ref("id")
    has_id = f'{lid}=""'
    hours = f"N({row_ref('hours')})"
    rate = f"N({row_ref('rate')})"
    cost = f"{hours}*{rate}"
    product = row_ref("product")

    cols: List[Any] = [
        id_col("PrefixLabor", trigger="employee", width=11.0,
               note="Numbers itself once a name is typed."),
        date_col("date", "Date", 13.0),
        time_col("start_time", "Start", 10.0, note="Optional - for the record."),
        time_col("end_time", "Finish", 10.0, note="Optional - for the record."),
        text_col("employee", "Who", 20.0,
                 note="You, a maker you pay, a contractor, a helper."),
        list_col("employment_type", "Type", "EmploymentTypeList", 13.0),
        list_col("task", "Task", "TaskList", 20.0),
        product_col(note="Leave blank for shop time that is not one product."),
        calc_col("product_name", "Product",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "name", product)})', 26.0, "text"),
        calc_col("craft", "Craft",
                 f'IF({product}="","",'
                 f'{fetch("Products", "id", "craft", product)})', 13.0, "text"),
        num_col("hours", "Hours", 9.0, note="Decimal hours: 1.5 = 90 minutes."),
        calc_col("minutes", "Minutes", f'IF({has_id},"",{hours}*60)', 10.0,
                 "number1"),
        money_col("rate", "Rate an hour", 11.0,
                  note="What this person is paid, before on-costs."),
        calc_col("cost", "Cost", f'IF({has_id},"",{cost})', 12.0, "money"),
        calc_col("burden", "Payroll on-costs",
                 f'IF({has_id},"",{cost}*PayrollBurden)', 12.0, "money",
                 note="Tax, insurance and holiday pay at the rate on Settings."),
        calc_col("loaded_cost", "True cost",
                 f'IF({has_id},"",{cost}*(1+PayrollBurden))', 12.0, "money"),
        calc_col("rate_check", "Rate check",
                 f'IF({has_id},"",IF({rate}=0,"NO RATE TYPED",'
                 f'IF({rate}<MinimumWage,"BELOW MIN WAGE","OK")))',
                 16.0, "status",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "BELOW", "fmt": "bold_bad"},
                     {"type": "text", "criteria": "containing",
                      "value": "NO RATE", "fmt": "warn"},
                     {"type": "text", "criteria": "containing",
                      "value": "OK", "fmt": "good"}]),
        text_col("batch", "Batch", 12.0,
                 note="Optional - the Batches tab ID if this was one batch."),
        calc_col("is_production", "Production?",
                 f'IF({has_id},"",IF({product}="","No","Yes"))', 11.0, "flag",
                 cf=[{"type": "text", "criteria": "containing",
                      "value": "Yes", "fmt": "good"},
                     {"type": "text", "criteria": "containing",
                      "value": "No", "fmt": "info"}]),
        calc_col("overhead_share", "Shop time cost",
                 f'IF({has_id},"",IF({product}="",N({row_ref("loaded_cost")}),0))',
                 12.0, "money",
                 note="Adds up to the real overhead of running the shop."),
        calc_col("month", "Month",
                 f'IF({row_ref("date")}="","",TEXT(N({row_ref("date")}),"yyyy-mm"))',
                 10.0, "text"),
        wrap_col("notes", "Notes", 30.0),
    ]

    return SheetSpec(columns=cols, samples=data, freeze_cols=2,
                     **spec_defaults(NAME, NAME, SUBTITLE, cfg, HELP,
                                     tab_color=P.accent))
