"""`Seasonal Planner` - the year, four blocks at a time.

Lawn care is the same twelve months over and over, and almost
everything that goes wrong is something that should have been booked
six weeks earlier. This page is the list: what to sell, what to
service and what to order, season by season, with the numbers from
your own records sitting next to each block so you can see what that
season has actually been worth.

The two checklists at the bottom are the ones crews are most often
missing: a maintenance visit checklist, and a property inspection to
run before quoting a site you have never seen.
"""

from __future__ import annotations

from ..config import Config, Palette
from ..layout import Registry
from ..writer import SheetWriter

NAME = "Seasonal Planner"
LAST_COL = 10
TASK_ROWS = 7

#: season -> (months, what to sell, what to prepare)
SEASON_PLAN = [
    ("Spring", "March to May", 3, 5, [
        ("Spring clean-ups", "The biggest selling window of the year. "
                             "Quote these in February, not April."),
        ("First cuts and edging", "Set the round order now and it "
                                  "holds for the whole season."),
        ("Fertiliser and pre-emergent", "Timing beats product. Book "
                                        "it by soil temperature, not "
                                        "by the calendar."),
        ("Mulch and bed refresh", "High margin, and it sells itself "
                                  "once the first warm weekend "
                                  "arrives."),
        ("Aeration and overseeding", "Cool season grass only. Ask "
                                     "before you quote it."),
        ("Irrigation start-up", "Check every head before you turn "
                                "the water on, not after."),
        ("Contract renewals", "Agree this season's price before the "
                              "first cut, never halfway through."),
    ]),
    ("Summer", "June to August", 6, 8, [
        ("Weekly and fortnightly cutting", "The core of the round. "
                                           "Protect it."),
        ("Hedge trimming", "Check for nesting birds first - in many "
                           "places that is the law, not a courtesy."),
        ("Weed control", "Licensed work in most places. Check who on "
                         "the crew can legally do it."),
        ("Irrigation checks", "A dry August is when customers notice "
                              "a head that has not worked since "
                              "May."),
        ("Watering advice", "Free, takes two minutes, and saves the "
                            "lawn you will be blamed for."),
        ("Holiday cover", "Book crew holidays around the round, and "
                          "tell customers before they notice."),
        ("Mid-season equipment service", "The one everybody skips. "
                                         "It is also the one that "
                                         "stops August breakdowns."),
    ]),
    ("Autumn / Fall", "September to November", 9, 11, [
        ("Leaf clearance", "Sell it as a series, not a single "
                           "visit. Three visits beats one argument."),
        ("Autumn feed", "Sets up next spring. Easy to sell to "
                        "anybody who liked their lawn this year."),
        ("Final cuts", "Agree the last cut date in writing so the "
                       "invoice is never a surprise."),
        ("Gutter and drain clearing", "Easy add-on while you are "
                                      "already there with a ladder."),
        ("Irrigation winterising", "Miss it and you will be quoted "
                                   "for the burst pipe."),
        ("Snow contracts", "Sign these in October. Nobody signs a "
                           "snow contract during a blizzard at a "
                           "sensible price."),
        ("Next year's pricing", "Review every contract against this "
                                "year's actual hours."),
    ]),
    ("Winter", "December to February", 12, 2, [
        ("Snow and ice clearing", "If you offer it, agree the "
                                  "trigger depth and the rate "
                                  "before the first fall."),
        ("Pruning and dormant work", "Trees and shrubs are easier to "
                                     "read with no leaves on them."),
        ("Hardscaping and fencing", "Fills the quiet weeks and keeps "
                                    "the crew together."),
        ("Full equipment service", "Every machine, in the workshop, "
                                   "before March. Blades, belts, "
                                   "filters, plugs."),
        ("Book next season", "Ring every customer. The round you "
                             "confirm in January is the round you "
                             "have in April."),
        ("Marketing and quotes", "Spring enquiries start in "
                                 "February. Be ready in January."),
        ("Accounts and insurance", "Renewals, licences, tax. Do it "
                                   "now; you will not have time in "
                                   "May."),
    ]),
]

MAINTENANCE_CHECKLIST = [
    "Walk the property before starting - look for toys, hoses, pet "
    "mess, stones and anything that will become a projectile.",
    "Check the mowing height is right for the season and the grass "
    "type. Scalping in July is how you lose a customer.",
    "Blades sharp and clean. A blunt blade tears the grass and the "
    "lawn goes brown three days later, long after you have left.",
    "Mow in a different direction from last visit where you can - it "
    "stops ruts and keeps the grass standing up.",
    "Edge and strim everything the job includes, every visit. Missed "
    "edges are the most common complaint in this trade.",
    "Blow all hard surfaces clear: paths, drive, patio, and the road "
    "outside.",
    "Clippings dealt with the way the customer agreed - left, bagged "
    "or taken away.",
    "Beds and borders checked for weeds if the job includes them.",
    "Gates closed and latched. Every single time.",
    "Tools counted back onto the trailer before you drive off.",
    "Damage, hazards and anything odd photographed and reported the "
    "same day.",
    "Actual time written down before the next job starts.",
]

INSPECTION_CHECKLIST = [
    "Measure the lawn properly - pace it or use a map tool. Guessing "
    "the area is guessing the price.",
    "Note the slope and the surface. Steep, wet or rough ground can "
    "add half as much again to the time.",
    "Check access: gate width, steps, locked gates, who holds a key, "
    "whether the ride-on can get in at all.",
    "Count the obstacles - trees, beds, play equipment, washing "
    "poles. Every one is a turn and a slow-down.",
    "Look for hazards: ponds, septic lids, irrigation heads, "
    "retaining walls, a bad step, overhead cables.",
    "Ask about dogs, and whether they are out during the day.",
    "Find out where the truck and trailer will park, and whether "
    "there is a time limit.",
    "Check for water and power on site if the work needs them.",
    "Agree what happens to the clippings before you quote, not "
    "after.",
    "Ask what they were unhappy about with the last company. It is "
    "the most useful question you will ask all day.",
    "Photograph the site - before photos are worth money later.",
    "Write the drive time and mileage from your yard onto the "
    "property record.",
]


def build(book, fmts, cfg: Config, reg: Registry) -> SheetWriter:
    s = SheetWriter(book, fmts, cfg, reg, NAME,
                    tab_color=Palette.primary_light)

    s.banner("Seasonal Planner",
             "What to sell, service and order in each season - with "
             "what that season has actually earned you.",
             LAST_COL)
    s.set_col(0, 0, 4)
    s.set_col(1, 1, 30)
    s.set_col(2, 2, 52)
    s.set_col(3, 3, 13)
    s.set_col(4, 4, 13)
    s.set_col(5, LAST_COL, 14)

    row = 4
    row = s.note(
        row,
        "Everything here is a prompt, not a rule. Grass types, "
        "climates and local regulations differ enormously - what "
        "follows is the shape of a temperate season, and you should "
        "edit the tasks to match the ground you actually work on. "
        "The figures on the right are your own, from your own job "
        "records.",
        LAST_COL, height=44)
    row += 1

    # --------------------------------------------------- where we are --
    row = s.section(row, "Right now", LAST_COL)
    s.kpi(row, 0, "Season",
          '=IF(MONTH(TodayDate)<=2,"Winter",'
          'IF(MONTH(TodayDate)<=5,"Spring",'
          'IF(MONTH(TodayDate)<=8,"Summer",'
          'IF(MONTH(TodayDate)<=11,"Autumn / Fall","Winter"))))',
          "text", note="Worked out from today's date")
    s.kpi(row, 2, "In season?",
          '=IF(AND(MONTH(TodayDate)>=SeasonStart,'
          'MONTH(TodayDate)<=SeasonEnd),"Yes - main season",'
          '"No - out of season")', "text",
          note="Against the months on Settings")
    s.kpi(row, 4, "Jobs this month",
          '=COUNTIFS(JobMonth,ThisMonthKey,JobIsDone,1)', "int",
          note="Completed so far")
    s.kpi(row, 6, "Revenue this month",
          '=SUMIFS(JobCharge,JobMonth,ThisMonthKey,JobIsDone,1)',
          "money")
    row = s.kpi(row, 8, "Contracts live",
                "=SUM(ConIsLive)", "int", span=2,
                note="Standing agreements in force")
    row += 1

    # ----------------------------------------------- the four seasons --
    for name, months, first_month, last_month in [
            (p[0], p[1], p[2], p[3]) for p in SEASON_PLAN]:
        plan = dict((p[0], p[4]) for p in SEASON_PLAN)[name]
        row = s.section(row, f"{name}  -  {months}", LAST_COL)

        # the season's own numbers, from the job register
        if first_month <= last_month:
            in_season = (f'(MONTH(JobDateNum)>={first_month})*'
                         f'(MONTH(JobDateNum)<={last_month})')
        else:                      # winter wraps the year end
            in_season = (f'((MONTH(JobDateNum)>={first_month})+'
                         f'(MONTH(JobDateNum)<={last_month}))')
        s.merge(row, 1, 2, "What this season has earned you, all "
                           "years", fmts.chrome("label_bold"))
        s.formula(row, 3,
                  f'=SUMPRODUCT({in_season}*JobIsDone*JobCharge)',
                  fmts.calc("money"))
        s.formula(row, 4,
                  f'=SUMPRODUCT({in_season}*JobIsDone)',
                  fmts.calc("int"))
        s.merge(row, 5, LAST_COL, None, fmts.chrome("note"))
        s.write(row, 5, "Revenue and completed visits in these "
                        "months, from your own records",
                fmts.chrome("note"))
        row += 1

        s.table_head(row, 1, ["Task", "Why it matters", "Start by",
                              "Done?", "Who", "Notes"],
                     widths=[30, 52, 13, 13, 14, 20])
        head = row
        for index, (task, why) in enumerate(plan[:TASK_ROWS]):
            line = head + 1 + index
            s.write(line, 1, task, fmts.chrome("label_bold"))
            s.write(line, 2, why, fmts.chrome("note"))
            s.write(line, 3, None, fmts.input("date"))
            s.write(line, 4, None, fmts.input("flag"))
            s.write(line, 5, None, fmts.input("text"))
            s.merge(line, 6, LAST_COL, None, fmts.input("text"))
            s.ws.data_validation(
                line, 4, line, 4,
                {"validate": "list", "source": ["Yes", "No"]})
            s.row_height(line, 26)
        row = head + len(plan[:TASK_ROWS]) + 2

    # -------------------------------------------- maintenance checklist --
    row = s.section(row, "Lawn maintenance checklist - every visit",
                    LAST_COL)
    row = s.note(
        row,
        "Print this and put it in the truck. Most complaints in this "
        "trade are not about the quality of the cut - they are about "
        "an open gate, a missed edge or clippings on the drive.",
        LAST_COL, height=30)
    row += 1
    s.table_head(row, 1, ["Check", "Done"], widths=[70, 10])
    head = row
    for index, item in enumerate(MAINTENANCE_CHECKLIST):
        line = head + 1 + index
        s.merge(line, 1, 5, item, fmts.chrome("day_item"))
        s.write(line, 6, None, fmts.chrome("form_box"))
        s.row_height(line, 24)
    row = head + len(MAINTENANCE_CHECKLIST) + 2

    # --------------------------------------------- inspection checklist --
    row = s.section(row, "Property inspection checklist - before you "
                         "quote", LAST_COL)
    row = s.note(
        row,
        "Twelve things to establish on a site you have never worked. "
        "Every one of them is a number or a fact that belongs on the "
        "Property Database, and every one of them changes the price.",
        LAST_COL, height=30)
    row += 1
    s.table_head(row, 1, ["Check", "Noted"], widths=[70, 10])
    head = row
    for index, item in enumerate(INSPECTION_CHECKLIST):
        line = head + 1 + index
        s.merge(line, 1, 5, item, fmts.chrome("day_item"))
        s.write(line, 6, None, fmts.chrome("form_box"))
        s.row_height(line, 24)
    row = head + len(INSPECTION_CHECKLIST) + 2

    # ------------------------------------------------ seasonal reminders --
    row = s.section(row, "Reminders that pay for themselves", LAST_COL)
    row = s.bullets(row, [
        "Renew contracts before the season starts, never during it. "
        "A price agreed in February is a conversation; the same "
        "price raised in June is an argument.",
        "Service every machine in the quiet months. A mower that "
        "fails in July costs a week of the best weather of the "
        "year.",
        "Order bulk materials out of season. Mulch and fertiliser "
        "are cheapest when nobody wants them.",
        "Ring dormant customers at the start of spring. The "
        "Customer CRM tab marks them for you after the number of "
        "days you set on Settings.",
        "Check licence and insurance expiry dates in the winter. The "
        "Crew Database warns you sixty days out.",
        "Take before and after photos through the season. In "
        "February they are the only marketing material you will "
        "have.",
    ], LAST_COL)
    row += 1

    row = s.note(
        row,
        "Local regulation beats anything written here. Pesticide "
        "and fertiliser application, hedge cutting during nesting "
        "season, green waste disposal and water use are all "
        "controlled differently from one place to the next, and some "
        "of them carry real penalties. Check what applies where you "
        "work before you sell it.",
        LAST_COL, height=48)

    s.finish(freeze_row=4, gridlines=False, fit_width=True)
    s.protect()
    return s
