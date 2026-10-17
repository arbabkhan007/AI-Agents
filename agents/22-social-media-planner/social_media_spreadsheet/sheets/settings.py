"""The `Settings` tab: control panel for the whole workbook."""

from __future__ import annotations

from ..layout import SheetSpec
from ..writer import SheetWriter, date_check, number_check
from .. import sample_data

NAME = "Settings"
LAST_COL = 8


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#B0B0A8")
    f = sheet.f
    sheet.banner(
        "Workbook Settings",
        "Tell the workbook about your business once, and it flows through "
        "the dashboards and printables. Cream cells are yours to edit.",
        LAST_COL)
    sheet.hide_gridlines()

    sheet.set_col(0, 0, 2)
    sheet.set_col(1, 1, 22)
    sheet.set_col(2, 2, 2)
    sheet.set_col(3, 4, 16)
    sheet.set_col(5, LAST_COL, 12)

    row = 4
    row = sheet.section(row, "Business details", LAST_COL)
    row = sheet.field(row, "Business / brand name", cfg.brand.name,
                      name="Setting_Brand", help_text="Shown on printables.")
    row = sheet.field(row, "Brand tagline", "Slow-made ceramics for slow mornings",
                      value_end=5,
                      help_text="One line that feels like you.")
    row = sheet.field(row, "Industry", "Handmade ceramics",
                      name="Setting_Industry",
                      help_text="Used in the report narrative.")
    row = sheet.field(row, "Website", "wildflower.studio",
                      value_end=5, name="Setting_Website")
    row = sheet.field(row, "Primary social platform", "Instagram",
                      name="Setting_PrimaryPlatform",
                      validate={"validate": "list", "source": "=PlatformList"})
    row = sheet.field(row, "Default post timezone", "America/New_York",
                      value_end=5, help_text="Local time of your audience.")
    row = sheet.field(row, "Week starts on", cfg.week_start,
                      name="Setting_WeekStart",
                      validate={"validate": "list", "source": "=WeekdayList"})

    row += 1
    row = sheet.section(row, "Currency & numbers", LAST_COL)
    row = sheet.field(row, "Currency", cfg.currency_symbol, name="Setting_Currency",
                      help_text="Controls the symbols in money columns.")
    row = sheet.field(row, "Currency code", cfg.currency_code,
                      name="Setting_CurrencyCode")
    row = sheet.field(row, "Monthly ad budget", 600.0, style="money",
                      name="Setting_AdBudget",
                      validate=number_check(0, 1000000),
                      help_text="Reference figure for the Budget tab.")
    row = sheet.field(row, "Average order value", 48.0, style="money",
                      name="Setting_AvgOrderValue",
                      validate=number_check(0, 1000000),
                      help_text="Used by Performance to estimate revenue.")
    row = sheet.field(row, "Fiscal year starts", "January",
                      name="Setting_FiscalStart",
                      validate={"validate": "list",
                                "source": "=MonthList"})

    row += 1
    row = sheet.section(row, "Defaults for new rows", LAST_COL)
    row = sheet.field(row, "Default content status", "Idea",
                      name="Setting_DefaultStatus",
                      validate={"validate": "list", "source": "=StatusList"})
    row = sheet.field(row, "Default content owner", "Jordan Avery",
                      name="Setting_DefaultOwner",
                      validate={"validate": "list", "source": "=TeamNames"})
    row = sheet.field(row, "Default reporting period", "Monthly",
                      name="Setting_ReportingPeriod",
                      validate={"validate": "list",
                                "source": ["Weekly", "Monthly", "Quarterly",
                                           "Yearly"]})
    row = sheet.field(row, "Planning year", cfg.today.year,
                      style="int", name="Setting_Year",
                      validate=number_check(2020, 2100, decimal=False),
                      help_text="Drives the Month View and the week headers.")
    row = sheet.field(row, "Planning month", "Mar", name="Setting_Month",
                      validate={"validate": "list", "source": "=MonthList"})

    row += 1
    row = sheet.section(row, "Tags & hygiene", LAST_COL)
    row = sheet.field(row, "Default UTM source", "instagram",
                      name="Setting_UtmSource",
                      validate={"validate": "list", "source": "=UtmSourceList"})
    row = sheet.field(row, "Default UTM medium", "social",
                      name="Setting_UtmMedium")
    row = sheet.field(row, "Tracking vanity link", "wildflower.studio/spring",
                      value_end=5, name="Setting_VanityLink")

    row += 1
    row = sheet.section(row, "Team & brand voice (quick ref)", LAST_COL)
    rows = sample_data.settings_rows() if cfg.include_sample_data else []
    if rows:
        row = sheet.table_head(row, 0, ["Setting", "Value", "How it is used"],
                               [18, 24, 40])
        for entry in rows:
            sheet.write(row, 0, entry["setting"], f.cell("text", "plain"))
            sheet.write(row, 1, entry["value"], f.cell("text", "plain"))
            sheet.merge(row, 2, LAST_COL, entry["help"],
                        f.chrome("note"))
            row += 1
    else:
        row = sheet.note(row, "Quick reference to your brand voice words, "
                              "posting cadence, approval rules and who owns "
                              "what. A blank copy lives on the Team and "
                              "Brand Voice tabs.", LAST_COL)

    row += 1
    row = sheet.note(
        row, "Header settings are locked formula cells. The cream fields "
             "above are open - type straight over them. Changing the lists "
             "on the Lists tab updates the drop downs everywhere.",
        LAST_COL, height=30)
    sheet.finish(freeze_row=4, print_area=f"A1:{chr(65 + LAST_COL)}{row}")
    return sheet
