"""Sheets A — Home + Pre-Trip Planning group."""
import helpers as H

PRE = H.TEAL

NAV = [
    ("Pre-Trip Planning", "Destination Overview", "Trip basics — who, where, when and why"),
    ("Pre-Trip Planning", "Budget Tracker", "Estimated vs actual costs per category"),
    ("Pre-Trip Planning", "Savings Goal", "Progress bar + savings log to hit your target"),
    ("Pre-Trip Planning", "Research & Ideas", "Must-see spots, links and inspiration"),
    ("Pre-Trip Planning", "Visa & Documents", "Checklist so nothing expires or is forgotten"),
    ("Pre-Trip Planning", "Booking Log", "Every confirmation number in one place"),
    ("Packing & Prep", "Packing Checklist", "Categorized list with pack-progress %"),
    ("Packing & Prep", "Weather Tracker", "Forecast + outfit planning per day"),
    ("Packing & Prep", "Carry-On vs Checked", "What goes in which bag"),
    ("Packing & Prep", "Pre-Trip To-Do", "Bank alerts, pet sitter, mail hold…"),
    ("Itinerary & Daily", "Daily Itinerary", "Day-by-day plan with times & costs"),
    ("Itinerary & Daily", "Hourly Schedule", "7-day morning / afternoon / evening grid"),
    ("Itinerary & Daily", "Route Planner", "Order your stops + sketch a map"),
    ("Itinerary & Daily", "Transportation Log", "Flights, trains & taxis with confirmations"),
    ("Itinerary & Daily", "Accommodation", "Up to 3 stays — Wi-Fi passwords included"),
    ("Expense Tracking", "Expense Log", "150-row daily spend log, auto-converted"),
    ("Expense Tracking", "Currency Converter", "Rate table + quick converter"),
    ("Expense Tracking", "Tipping Guide", "What to tip in 12+ countries"),
    ("Expense Tracking", "Trip Cost Summary", "Every total on one dashboard"),
    ("Food & Activities", "Restaurant Wishlist", "Wish list with reservations & ratings"),
    ("Food & Activities", "Activity Planner", "Excursions — idea → booked → done"),
    ("Food & Activities", "Local Phrases", "16 essentials to learn"),
    ("Food & Activities", "Etiquette Notes", "Do's and don'ts by topic"),
    ("Extras & Memories", "Emergency Contacts", "Embassy, hospital, insurance, family"),
    ("Extras & Memories", "Travel Journal", "Daily highlights & favorite moments"),
    ("Extras & Memories", "Ratings & Reviews", "Rate everything 1–5"),
    ("Extras & Memories", "Souvenir List", "Gift budget vs actual spending"),
    ("Extras & Memories", "Wi-Fi & Passwords", "Every network + password, saved"),
]


def build_home(wb):
    ws = H.new_sheet(wb, "Home", H.NAVY,
                     "✈️ TRAVEL PLANNER — VERSION 2",
                     "by Novality store  ✦  plan • pack • spend smart • enjoy", 4)
    for L, w in (("A", 18), ("B", 24), ("C", 46), ("D", 14)):
        ws.column_dimensions[L].width = w

    D = "'Destination Overview'"
    B = "'Budget Tracker'"
    H.section(ws, 4, 4, "🧳 TRIP SNAPSHOT")
    snap = [
        (5, "A", "Trip Name", f'=IF({D}!B5="","—",{D}!B5)', None,
             "C", "Destination", f'=IF({D}!B8="","—",{D}!B9&", "&{D}!B8)', None),
        (6, "A", "Departure", f'=IF({D}!B11="","—",{D}!B11)', H.DATEF,
             "C", "Return", f'=IF({D}!B12="","—",{D}!B12)', H.DATEF),
        (7, "A", "Trip Length", f'=IF({D}!B14="","—",{D}!B14&" days")', None,
             "C", "Travelers", f'=IF({D}!B13="","—",{D}!B13&" traveler(s)")', None),
        (8, "A", "Budget (Est.)", f"={B}!B15", H.MONEY,
             "C", "Spent (Actual)", f"={B}!C15", H.MONEY),
    ]
    for r, lc, ll, f1, fm, rc, rl, f2, fm2 in snap:
        H.put(ws, f"{lc}{r}", ll, font=H.F_LABEL, fillc=H.CREAM,
              halign="left", indent=1, border=True)
        H.calc_cell(ws, f"{chr(ord(lc)+1)}{r}", f1, fmt=fm)
        H.put(ws, f"{rc}{r}", rl, font=H.F_LABEL, fillc=H.CREAM,
              halign="left", indent=1, border=True)
        H.calc_cell(ws, f"D{r}", f2, fmt=fm2)

    H.section(ws, 10, 4, "🧭 QUICK NAVIGATION — 28 PLANNING SHEETS")
    r = 11
    for i, (grp, name, desc) in enumerate(NAV):
        z = H.CREAM if i % 2 == 0 else None
        H.put(ws, f"A{r}", grp, font=H.F_NOTE, fillc=z, halign="left",
              indent=1, border=True)
        H.put(ws, f"B{r}", name, font=H.F_LABEL, fillc=z, halign="left",
              indent=1, border=True)
        H.put(ws, f"C{r}", desc, font=H.F_BODY, fillc=z, halign="left",
              indent=1, border=True)
        H.calc_cell(ws, f"D{r}", f'=HYPERLINK("#\'{name}\'!A1","Open →")',
                    font=H.F_LINK)
        r += 1
    ws.row_dimensions[10].height = 20

    H.section(ws, 40, 4, "📌 HOW TO USE")
    tips = [
        "✔  Yellow cells are yours to fill in — type, pick dates, or choose from the dropdown arrows.",
        "✔  Blue-gray cells calculate automatically and are locked, so the formulas can never break.",
        "✔  Status columns have dropdowns — tap ✓ when something is done, packed or visited.",
        "✔  Start on 'Destination Overview', set your 'Budget Tracker', then plan the fun stuff!",
    ]
    for i, t in enumerate(tips):
        H.box(ws, 41 + i, 1, 41 + i, 4, fillc=H.CREAM)
        H.put(ws, f"A{41+i}", t, font=H.F_BODY, halign="left", indent=1)
        ws.row_dimensions[41 + i].height = 18

    ws.merge_cells("A46:D46")
    H.put(ws, "A46", "Travel Planner v2.0  •  made with ❤ by Novality store  •  happy travels!",
          font=H.F_NOTE, halign="center")
    H.finish(ws, landscape=False)


def build_destination(wb):
    ws = H.new_sheet(wb, "Destination Overview", PRE, "🌍 DESTINATION OVERVIEW",
                     "The who / where / when of your trip — it feeds the Home snapshot", 3)
    H.table(ws, 4, [
        {"h": "Field", "w": 24, "k": "lock"},
        {"h": "Your Details", "w": 34, "k": "in"},
        {"h": "Notes / Extra Info", "w": 46, "k": "in", "a": "left"},
    ], 14)

    rows = [
        (5,  "Trip Name", None, None, "e.g. “Cherry Blossom Japan 2027”"),
        (6,  "Traveler Name(s)", None, None, "Everyone on the booking"),
        (7,  "Home City / Base", None, None, None),
        (8,  "Destination Country", None, None, None),
        (9,  "Destination City / Cities", None, None, "One base or a multi-stop route"),
        (10, "Trip Purpose", None, None, None),
        (11, "Departure Date", H.DATEF, None, None),
        (12, "Return Date", H.DATEF, None, None),
        (13, "Number of Travelers", H.INTF, None, None),
        (14, None, None, None, "Calculated from your dates"),
        (15, None, None, None, "Updates automatically each day"),
        (16, "Home Emergency Contact", None, None, "Name + phone"),
        (17, "Home Address", None, None, None),
        (18, "Trip Notes / Why We're Going", None, None, "Free text"),
    ]
    for r, label, fmt, _x, note in rows:
        if label:
            H.put(ws, f"A{r}", label, font=H.F_LABEL, fillc=H.CREAM,
                  halign="left", indent=1, border=True)
            H.input_cell(ws, f"B{r}", fmt=fmt)
        H.input_cell(ws, f"C{r}", value=note, font=H.F_NOTE, halign="left", wrap=True)

    H.dv(ws, "B10", "Leisure / Beach,City Break,Adventure / Outdoors,Business,Family Trip,"
                    "Honeymoon / Romance,Backpacking,Visiting Friends & Family,Festival / Event,Other")
    H.calc_cell(ws, "B14", '=IF(COUNT(B11:B12)<2,"",B12-B11+1)', fmt=H.INTF)
    H.calc_cell(ws, "B15", '=IF(B11="","—",B11-TODAY())', fmt=H.INTF)
    H.put(ws, "A14", "Trip Length (Days)", font=H.F_LABEL, fillc=H.CREAM,
          halign="left", indent=1, border=True)
    H.put(ws, "A15", "Days Until Departure", font=H.F_LABEL, fillc=H.CREAM,
          halign="left", indent=1, border=True)
    ws.row_dimensions[18].height = 26
    H.finish(ws, landscape=False, freeze="A5")


def build_budget(wb):
    ws = H.new_sheet(wb, "Budget Tracker", PRE, "💰 BUDGET TRACKER",
                     "Estimated vs actual for every category — variance updates itself", 10)
    last = H.table(ws, 4, [
        {"h": "Category", "w": 24, "k": "in", "a": "left"},
        {"h": "Estimated Cost", "w": 14, "k": "in", "f": H.MONEY},
        {"h": "Actual Cost", "w": 14, "k": "in", "f": H.MONEY},
        {"h": "Difference", "w": 14, "k": "calc", "f": H.MONEY},
        {"h": "% of Est. Used", "w": 12, "k": "calc", "f": H.PCT},
        {"h": "Status", "w": 24, "k": "calc", "a": "center"},
        {"h": "Notes", "w": 32, "k": "in", "a": "left"},
    ], 10)
    cats = ["✈️ Flights", "🏨 Accommodation", "🍽️ Food & Dining",
            "🚕 Local Transport", "🎟️ Activities & Tours", "🛍️ Shopping",
            "🛡️ Travel Insurance", "📋 Visas & Fees", "🎁 Souvenirs",
            "✨ Miscellaneous"]
    for i, cat in enumerate(cats):
        r = 5 + i
        H.input_cell(ws, f"A{r}", cat, halign="left", indent=1)
        H.calc_cell(ws, f"D{r}", f'=IF(COUNT(B{r}:C{r})=0,"",B{r}-C{r})', fmt=H.MONEY)
        H.calc_cell(ws, f"E{r}", f'=IF(OR(B{r}="",B{r}=0),"",C{r}/B{r})', fmt=H.PCT)
        H.calc_cell(ws, f"F{r}", f'=IF(COUNT(B{r}:C{r})=0,"",IF(C{r}>B{r},"⚠ Over budget","✓ On track"))')
    # TOTAL row (15)
    for col in "ABCDEFG":
        H.put(ws, f"{col}15", fillc=H.NAVY, border=True)
    H.put(ws, "A15", "TOTAL", font=H.F_TOTAL, fillc=H.NAVY, halign="left",
          indent=1, border=True)
    for col, f, fmt in (("B", "=SUM(B5:B14)", H.MONEY), ("C", "=SUM(C5:C14)", H.MONEY),
                        ("D", "=B15-C15", H.MONEY), ("E", '=IF(B15=0,"",C15/B15)', H.PCT)):
        H.calc_cell(ws, f"{col}15", f, fmt=fmt, font=H.F_TOTAL, fillc=H.NAVY)
    H.calc_cell(ws, "F15", '=IF(COUNT(B5:C14)=0,"",IF(C15>B15,"⚠ Over by "&TEXT(C15-B15,"#,##0.00"),'
                           '"✓ Under by "&TEXT(B15-C15,"#,##0.00")))',
                font=H.F_TOTAL, fillc=H.NAVY)
    H.databar(ws, "E5:E14")
    H.summary_box(ws, 4, 9, "📊 SUMMARY", [
        ("Total Estimated", "=B15", H.MONEY),
        ("Total Actual", "=C15", H.MONEY),
        ("Remaining Budget", "=B15-C15", H.MONEY),
        ("% of Budget Used", '=IF(B15=0,"",C15/B15)', H.PCT),
    ])
    ws.auto_filter.ref = "A4:G14"
    H.finish(ws, freeze="A5", title_rows="4:4")


def build_savings(wb):
    ws = H.new_sheet(wb, "Savings Goal", PRE, "🎯 SAVINGS GOAL TRACKER",
                     "Watch the bar fill as you save — log every deposit below", 4)
    for L, w in (("A", 20), ("B", 16), ("C", 30), ("D", 16)):
        ws.column_dimensions[L].width = w
    H.section(ws, 4, 4, "🎯 GOAL OVERVIEW")
    H.put(ws, "A5", "Savings Target", font=H.F_LABEL, fillc=H.CREAM,
          halign="left", indent=1, border=True)
    H.input_cell(ws, "B5", fmt=H.MONEY)
    H.put(ws, "C5", "Tip: match it to your Budget Tracker total",
          font=H.F_NOTE, halign="left", indent=1)
    for r, label, f, fmt in (
        (6, "Saved So Far", "=SUM(B12:B31)", H.MONEY),
        (7, "Still Needed", '=IF(B5="","",MAX(0,B5-B6))', H.MONEY),
        (8, "Progress", '=IF(OR(B5="",B5=0),"",MIN(1,B6/B5))', H.PCT),
    ):
        H.put(ws, f"A{r}", label, font=H.F_LABEL, fillc=H.CREAM,
              halign="left", indent=1, border=True)
        H.calc_cell(ws, f"B{r}", f, fmt=fmt)
    H.box(ws, 9, 1, 9, 4)
    H.put(ws, "A9", '=IF(OR(B5="",B5=0),"",REPT("█",MIN(20,ROUND(B6/B5*20,0)))'
                    '&REPT("░",20-MIN(20,ROUND(B6/B5*20,0))))',
          font=H.Font(bold=True, size=16, color=H.TEAL), halign="center")
    ws.row_dimensions[9].height = 26

    H.section(ws, 10, 4, "🧾 SAVINGS LOG — every deposit gets you closer")
    H.table(ws, 11, [
        {"h": "Date", "w": 14, "k": "in", "f": H.DATEF, "a": "center"},
        {"h": "Amount Saved", "w": 16, "k": "in", "f": H.MONEY},
        {"h": "Source / Note", "w": 30, "k": "in", "a": "left"},
        {"h": "Running Total", "w": 16, "k": "calc", "f": H.MONEY},
    ], 20, zebra=False)
    for r in range(12, 32):
        H.calc_cell(ws, f"D{r}", f'=IF(B{r}="","",SUM($B$12:B{r}))', fmt=H.MONEY)
    H.put(ws, "A33", "Tip: log each payday transfer — the jar fills itself.",
          font=H.F_NOTE, halign="left", indent=1)
    H.finish(ws, landscape=False, freeze="A12")


def build_research(wb):
    ws = H.new_sheet(wb, "Research & Ideas", PRE, "🔎 RESEARCH & INSPIRATION",
                     "Collect the dream list now — sort it into the itinerary later", 11)
    H.table(ws, 4, [
        {"h": "#", "w": 5, "k": "lock", "a": "center"},
        {"h": "Place / Attraction", "w": 26, "k": "in", "a": "left"},
        {"h": "City / Area", "w": 18, "k": "in", "a": "left"},
        {"h": "Why It's a Must / Notes", "w": 42, "k": "in", "a": "left"},
        {"h": "Priority", "w": 12, "k": "in", "a": "center"},
        {"h": "Visited?", "w": 11, "k": "in", "a": "center"},
    ], 12)
    for i in range(12):
        H.put(ws, f"A{5+i}", i + 1, font=H.F_NOTE, halign="center", border=True)
    H.dv(ws, "E5:E16", "High,Medium,Low")
    H.dv(ws, "F5:F16", "✓,✗")

    H.table(ws, 4, [
        {"h": "Link Title", "w": 26, "k": "in", "a": "left"},
        {"h": "URL", "w": 36, "k": "in", "a": "left"},
        {"h": "Category", "w": 16, "k": "in", "a": "left"},
        {"h": "Notes", "w": 42, "k": "in", "a": "left"},
    ], 10, start_col=8)
    ws.column_dimensions["G"].width = 3
    H.dv(ws, "J5:J14", "Blog,Video,Booking Site,Map,Review,Tour,Food,Other")
    H.summary_box(ws, 17, 8, "📍 PROGRESS", [
        ("Places visited", '=COUNTIF(F5:F16,"✓")&" of "&COUNTA(B5:B16)', None),
    ], width=18, vwidth=12, set_width=False)

    H.section(ws, 19, 11, "💡 NOTES & INSPIRATION")
    H.box(ws, 20, 1, 26, 11, fillc=H.INPUT, unlocked=True)
    ws["A20"].alignment = H.Alignment(horizontal="left", vertical="top",
                                      wrap_text=True, indent=1)
    ws.row_dimensions[20].height = 24
    H.finish(ws, freeze="A5")


def build_visa(wb):
    ws = H.new_sheet(wb, "Visa & Documents", PRE, "🛂 VISA & DOCUMENT CHECKLIST",
                     "Passport, visa, insurance, copies — nothing left behind", 8)
    H.table(ws, 4, [
        {"h": "Document", "w": 32, "k": "in", "a": "left"},
        {"h": "Required?", "w": 12, "k": "in", "a": "center"},
        {"h": "Status", "w": 14, "k": "in", "a": "center"},
        {"h": "Deadline", "w": 14, "k": "in", "f": H.DATEF, "a": "center"},
        {"h": "Notes", "w": 36, "k": "in", "a": "left"},
    ], 14)
    docs = [
        "Passport (valid 6+ months after return)",
        "Visa / eTA / travel authorization",
        "Travel insurance policy",
        "Vaccination certificates (if required)",
        "Prescription meds + doctor's note",
        "Driver's license / IDP",
        "National ID card",
        "Credit & debit cards (no foreign fees?)",
        "Cash in local currency",
        "Boarding passes / e-tickets",
        "Hotel & tour confirmations",
        "Copies of documents (cloud + paper)",
        "Passport photos (spare)",
        "Health / vaccination records",
    ]
    for i, d in enumerate(docs):
        H.input_cell(ws, f"A{5+i}", d, font=H.F_LABEL, halign="left", indent=1)
    H.dv(ws, "B5:B18", "Yes,No,N/A")
    H.dv(ws, "C5:C18", "Not Started,In Progress,Ready,N/A")
    H.summary_box(ws, 4, 7, "📊 PROGRESS", [
        ("Ready", '=COUNTIF(C5:C18,"Ready")', H.INTF),
        ("Still To Do", '=COUNTIF(B5:B18,"Yes")-COUNTIFS(B5:B18,"Yes",C5:C18,"Ready")', H.INTF),
        ("% Ready", '=IFERROR(MIN(1,COUNTIFS(B5:B18,"Yes",C5:C18,"Ready")/COUNTIF(B5:B18,"Yes")),"")', H.PCT),
    ], width=14)
    H.databar(ws, "H7")
    H.put(ws, "A20", "Rule of thumb: many countries want a passport valid 6+ months beyond your return date.",
          font=H.F_NOTE, halign="left", indent=1)
    H.finish(ws, freeze="A5")


def build_booking(wb):
    ws = H.new_sheet(wb, "Booking Log", PRE, "🎟️ BOOKING CONFIRMATION LOG",
                     "One row per booking — never scroll emails at a check-in desk again", 12)
    H.table(ws, 4, [
        {"h": "Type", "w": 14, "k": "in", "a": "center"},
        {"h": "Provider", "w": 20, "k": "in", "a": "left"},
        {"h": "Confirmation #", "w": 22, "k": "in", "a": "center"},
        {"h": "Booked On", "w": 14, "k": "in", "f": H.DATEF, "a": "center"},
        {"h": "Starts", "w": 14, "k": "in", "f": H.DATEF, "a": "center"},
        {"h": "Ends", "w": 14, "k": "in", "f": H.DATEF, "a": "center"},
        {"h": "Cost", "w": 13, "k": "in", "f": H.MONEY},
        {"h": "Paid?", "w": 10, "k": "in", "a": "center"},
        {"h": "Notes", "w": 30, "k": "in", "a": "left"},
    ], 14)
    H.dv(ws, "A5:A18", "Flight,Hotel,Car Rental,Tour / Activity,Train,Bus,Cruise,Ferry,"
                       "Restaurant,Transfer,Other")
    H.dv(ws, "H5:H18", "Yes,No,Deposit")
    H.summary_box(ws, 4, 11, "📊 SUMMARY", [
        ("Total Booked Cost", "=SUM(G5:G18)", H.MONEY),
        ("Confirmations Logged", '=COUNTIF(C5:C18,"?*")', H.INTF),
        ("Still Unpaid", '=COUNTIF(H5:H18,"No")', H.INTF),
    ], width=20)
    H.finish(ws, freeze="A5")
