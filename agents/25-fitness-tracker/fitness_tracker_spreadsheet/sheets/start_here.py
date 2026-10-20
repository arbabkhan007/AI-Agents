"""1 Start Here - welcome, quick start, colour key, demo data, licence.

Carries the full health disclaimer, the privacy note, the licence and
the documented one-pass way to remove the example data.
"""

from __future__ import annotations

from ..config import DISCLAIMER, Config, Palette
from ..writer import SheetWriter
from . import common as C

NAME = "1 Start Here"

QUICK_START = [
    "1.  Skim 16 Settings & Lists - units, week start, targets and the "
    "lists are all there, and all editable.",
    "2.  Fill in 2 Profile & Goals: sex, age, height, starting weight, "
    "goal weight, and up to six goals of any kind.",
    "3.  Plan the week on 4 Workout Planner - pick a start date, the "
    "phases arrive pre-filled, change anything.",
    "4.  Log as you go: 5 Workout Log, 7 Cardio & Activity, 8 Weight "
    "Tracker, 10 Habit Tracker, 11 Meals & Macros, 12 Water & Sleep.",
    "5.  Read 3 Dashboard daily and 14 Weekly & Monthly Review once a "
    "week. Print 15 Reports & Charts when the month closes.",
]

FAQ = [
    ("Will it work in my Excel?",
     "Excel 2010 or later on Windows or Mac, Excel on the web, Google "
     "Sheets, LibreOffice Calc and Apple Numbers all open it. No macros, "
     "no add-ins, no subscription."),
    ("Does it work in Google Sheets?",
     "Yes. Make your own copy (File > Make a copy), then use it as "
     "normal. Charts and drop downs survive; sparklines show in Excel "
     "and are ignored politely elsewhere."),
    ("What is the password for?",
     "Sheets are protected so formula cells cannot be overwritten by "
     "accident. The password is 'premium', printed on 16 Settings & "
     "Lists. Unprotect via Review > Unprotect Sheet."),
    ("How do I delete the example data?",
     "One pass: on each register (tabs 5, 7, 8, 9, 11, 12, 13) select "
     "the cream cells from row 5 to the last example row and press "
     "Delete. The blank copy in your download is already empty."),
    ("Can I add my own exercises and foods?",
     "Yes - type them on 6 Exercise Library and in the calorie database "
     "on 11 Meals & Macros. Drop downs grow the moment you do."),
    ("Will switching kg to lb break my history?",
     "No. Every row carries a unit stamp; leave it blank and the row "
     "uses the workbook unit. Switch units and every display, chart and "
     "target converts; stamped rows keep their meaning."),
    ("Are the calorie and body-fat numbers reliable?",
     "They are estimates computed from what you type, clearly labelled "
     "as estimates, and every target is yours to overwrite. Nothing "
     "here is medical advice."),
    ("Where does my data live?",
     "In your file, on your machine or your own Drive. Nothing is sent "
     "anywhere; there is no account and no connection."),
    ("What if a drop down looks empty?",
     "The list it reads is on 16 Settings & Lists - check the block is "
     "not filtered or cleared. Unprotect, retype, re-protect."),
    ("Can I use it with clients?",
     "One file per client is fine under the personal-use licence. "
     "Reselling or redistributing the template itself is not."),
]


def build(book, fmts, cfg: Config, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME,
                        tab_color=Palette.primary, landscape=False)
    last_col = 9
    sheet.banner("1  Start Here",
                 f"{cfg.product_name} - v{cfg.version} by {cfg.author}",
                 last_col, nav=False)
    sheet.nav_strip(2, last_col)
    row = 4
    row = sheet.section(row, "WELCOME", last_col)
    row = sheet.note(row,
                     "This is a complete tracking system that does the "
                     "arithmetic for you: sixteen tabs, one colour code, "
                     "every total live. It plans, logs, calculates and "
                     "prints - and it never phones home.", last_col,
                     height=40)
    row = sheet.section(row, "FIVE-STEP QUICK START", last_col)
    row = sheet.bullets(row, QUICK_START, last_col, height=26)
    row += 1
    row = sheet.section(row, "THE COLOUR CODE", last_col)
    sheet.merge(row, 0, 1, "cream", sheet.f.chrome("legend_input"))
    sheet.merge(row, 2, last_col, "type here - every input cell in "
                                       "the workbook",
                sheet.f.chrome("label"))
    row += 1
    sheet.merge(row, 0, 1, "grey", sheet.f.chrome("legend_calc"))
    sheet.merge(row, 2, last_col, "calculated - locked so it stays "
                                       "true",
                sheet.f.chrome("label"))
    row += 2
    row = sheet.section(row, "WHERE YOUR DATA LIVES", last_col)
    row = sheet.note(row,
                     "This file is yours. It lives on your machine or in "
                     "your own cloud folder; nothing is sent anywhere, "
                     "there is no account, no login and no connection. "
                     "In Google Sheets: File > Make a copy, then work in "
                     "your copy.", last_col, height=40)
    row = sheet.section(row, "DEMO DATA - AND HOW TO REMOVE IT", last_col)
    row = sheet.note(row,
                     "The filled copy ships with eleven weeks of example "
                     "training so you can see every formula working: "
                     "workout log, cardio, weigh-ins, measurements, "
                     "meals, water, sleep, habits and a month of ticks. "
                     "Remove it in one pass - on tabs 5, 7, 8, 9, 11, 12 "
                     "and 13 select the cream cells from row 5 down to "
                     "the last example row and press Delete - or open "
                     "the completely blank workbook that ships beside "
                     "this one.", last_col, height=56)
    row = sheet.section(row, "HEALTH & FITNESS DISCLAIMER", last_col)
    row = sheet.note(row, DISCLAIMER, last_col, height=88)
    row = sheet.section(row, "LICENCE", last_col)
    row = sheet.note(row,
                     "Personal-use licence: one buyer, unlimited personal "
                     "use, including tracking clients you coach one file "
                     "at a time. Not for resale, redistribution, or "
                     "inclusion in another product. Keep the credit row "
                     "on printed pages or do not - your prints, your "
                     "fridge.", last_col, height=40)
    row = sheet.section(row, "QUESTIONS BUYERS ACTUALLY ASK", last_col)
    for question, answer in FAQ:
        sheet.merge(row, 0, last_col, question,
                    sheet.f.chrome("label_bold"))
        row += 1
        sheet.merge(row, 0, last_col, answer, sheet.f.chrome("note"))
        sheet.row_height(row, 26)
        row += 1
    row += 1
    C.footer(sheet, cfg, last_col, row)
    sheet.finish(freeze_row=3, gridlines=False)
    return sheet
