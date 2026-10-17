"""The `Help` tab - FAQ, workflow rules and troubleshooting."""

from __future__ import annotations

from ..writer import NAV_LINKS, SheetWriter

NAME = "Help"
LAST_COL = 7

FAQ = [
    ("What is locked and what is open?",
     "Cream cells are yours: type, clear, replace. Grey cells are formulas "
     "and are protected so they cannot be overwritten by accident. Every "
     "sheet is protected with the password 'premium'."),
    ("How do I add a new content pillar?",
     "Add the pillar name on the Content Pillars tab, then add the same "
     "word to the Pillars column on the Lists tab. The drop down picks it "
     "up immediately - drop downs read the names."),
    ("Why do some columns look grey and read-only?",
     "They are calculated: IDs, weekdays, engagement rates, countdowns. "
     "If a grey column shows nothing, its input columns are still empty."),
    ("How do I plan a whole month at once?",
     "Filter the Content Calendar by month (the Publish Date column), fill "
     "the rows, then check the Month View tab for the shape of the month. "
     "The Dashboard queue shows what is still missing captions or assets."),
    ("Can I use this in Google Sheets or Numbers?",
     "Yes - upload the file. Formulas are deliberately old-school so they "
     "survive the trip. Some formatting shifts are normal; the numbers "
     "keep working."),
    ("Something shows #REF! or #NAME?. What now?",
     "It usually means a defined name was deleted. Undo, or re-enter the "
     "name under Formulas > Name Manager. The names are listed below."),
    ("How do the print tabs work?",
     "Print Brief turns one post into a one-page brief. Print Week shows "
     "the current week as a tidy schedule. Both are set to fit one page "
     "wide - just press print."),
    ("Can I track more than one brand?",
     "The workbook is built for one brand. If you run two, duplicate the "
     "file and rename the brand on the Settings tab of each copy."),
]

NAMES_DOC = [
    ("Report Date", "The date the workbook treats as 'today' - drives "
                    "countdowns and overdue flags (on the hidden Calc tab)."),
    ("Setting_Brand, Setting_Currency", "Business details from the "
                                        "Settings tab."),
    ("ContentIDs, CaptionIDs, AssetIDs", "Live lists used by drop downs "
                                         "and lookups."),
    ("StatusList, PlatformList, PillarList...", "Every drop down source, "
                                                "defined on the Lists tab."),
]


def build(book, fmts, cfg, reg) -> SheetWriter:
    sheet = SheetWriter(book, fmts, cfg, reg, NAME, tab_color="#B0B0A8")
    f = sheet.f
    sheet.hide_gridlines()
    sheet.banner("Help & FAQ", "Everything you need to run the planner - "
                               "and what to do when something looks odd.",
                 LAST_COL)
    sheet.set_col(0, 0, 3)
    sheet.set_col(1, 2, 18)
    sheet.set_col(3, LAST_COL, 14)

    row = 4
    row = sheet.section(row, "Frequently asked questions", LAST_COL)
    for question, answer in FAQ:
        sheet.merge(row, 0, 2, question, f.chrome("label_bold"))
        sheet.merge(row, 3, LAST_COL, answer, f.chrome("note"))
        sheet.row_height(row, 30)
        row += 1

    row += 1
    row = sheet.section(row, "Rules that keep the numbers honest", LAST_COL)
    rules = [
        "One row per post on the Content Calendar. Duplication there "
        "duplicates every number downstream.",
        "Content IDs are calculated - never type over them. Link other "
        "tabs to a post through its Content ID.",
        "Status drives the dashboards. 'Posted' is the only status that "
        "counts as published.",
        "Log performance within a week of posting - the numbers are "
        "hardest to recover after that.",
        "Permissions before posting. If the Compliance tab says Pending, "
        "it does not ship.",
    ]
    for rule in rules:
        sheet.merge(row, 0, LAST_COL, f"•  {rule}", f.chrome("label"))
        row += 1

    row += 1
    row = sheet.section(row, "Named ranges you should know", LAST_COL)
    for name, meaning in NAMES_DOC:
        sheet.merge(row, 0, 2, name, f.chrome("label_bold"))
        sheet.merge(row, 3, LAST_COL, meaning, f.chrome("note"))
        sheet.row_height(row, 26)
        row += 1

    row += 1
    row = sheet.section(row, "Keyboard habits that speed everything up",
                        LAST_COL)
    shortcuts = [
        "Ctrl + Down / Up jumps to the edge of a block of rows.",
        "Alt + Down opens a drop down in the selected cell.",
        "Ctrl + Shift + L toggles the filter arrows on the header row.",
        "Ctrl + Home takes you back to the top-left of the sheet.",
    ]
    for item in shortcuts:
        sheet.merge(row, 0, LAST_COL, f"•  {item}", f.chrome("label"))
        row += 1

    row += 1
    sheet.merge(row, 0, LAST_COL,
                "Still stuck? Email the author - " + cfg.author +
                " - and quote the tab name and what you were trying to do.",
                f.chrome("note_box"))
    sheet.row_height(row, 26)
    row += 2

    for label, target in NAV_LINKS[:4]:
        sheet.merge(row, 0, 2, "", f.chrome("nav"))
        sheet.ws.write_url(row, 0, f"internal:'{target}'!A1",
                           f.chrome("nav"), f"> {label}")
        row += 1

    sheet.finish(freeze_row=4, print_area=f"A1:{chr(65 + LAST_COL)}{row}")
    return sheet
