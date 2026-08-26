"""Sheets D — Extras & Memories group."""
import helpers as H

MISC = "9B72CF"

EMERGENCY = [
    "Local police", "Local ambulance / emergency", "Nearest hospital (name)",
    "Nearest hospital (address)", "Nearest pharmacy / clinic",
    "My country's embassy", "Embassy address", "Embassy 24/7 line",
    "Consulate (if different)", "Travel insurance hotline",
    "Insurance policy #", "Airline / travel agency 24-7 line",
    "Hotel front desk", "Tour operator / guide",
    "Roadside / rental-car assistance", "Family contact #1",
    "Family contact #2", "Neighbor / house sitter",
    "Work / manager contact", "Family doctor at home",
]


def build_emergency(wb):
    ws = H.new_sheet(wb, "Emergency Contacts", MISC, "🚨 EMERGENCY CONTACTS",
                     "Print this page — save it offline before you fly", 4)
    H.table(ws, 4, [
        {"h": "Contact", "w": 30, "k": "in", "a": "left"},
        {"h": "Phone / Number", "w": 24, "k": "in", "a": "center"},
        {"h": "Address / Extra Info", "w": 34, "k": "in", "a": "left"},
        {"h": "Notes", "w": 28, "k": "in", "a": "left"},
    ], 20)
    for i, c in enumerate(EMERGENCY):
        H.input_cell(ws, f"A{5+i}", c, font=H.F_LABEL, halign="left", indent=1)
    ws.merge_cells("A26:D26")
    H.put(ws, "A26", "📞 Universal numbers: 112 (EU & much of the world) • 911 (US / Canada) "
                     "• 999 (UK) • 000 (Australia) • 110 (Japan) • 110 / 119 (China).",
          font=H.F_NOTE, halign="left", indent=1)
    H.finish(ws, freeze="A5")


def build_journal(wb):
    ws = H.new_sheet(wb, "Travel Journal", MISC, "📓 TRAVEL JOURNAL & MEMORIES",
                     "One line a day — the highlights you'll want to remember", 10)
    H.table(ws, 4, [
        {"h": "Date", "w": 13, "k": "in", "f": H.DATEF, "a": "center"},
        {"h": "Place", "w": 18, "k": "in", "a": "left"},
        {"h": "Highlight of the Day", "w": 34, "k": "in", "a": "left"},
        {"h": "Favorite Moment", "w": 34, "k": "in", "a": "left"},
        {"h": "Rating", "w": 9, "k": "in", "a": "center"},
        {"h": "Photo to Print?", "w": 12, "k": "in", "a": "center"},
        {"h": "Notes / Memories", "w": 32, "k": "in", "a": "left"},
    ], 30)
    H.dv_num(ws, "E5:E34")
    H.dv(ws, "F5:F34", "Yes,No")
    H.summary_box(ws, 4, 9, "📊 MEMORIES", [
        ("Average Rating", '=IFERROR(ROUND(AVERAGE(E5:E34),1),"—")', H.DEC1),
        ("Photos to Print", '=COUNTIF(F5:F34,"Yes")', H.INTF),
    ], width=17)
    H.finish(ws, freeze="A5")


def build_rating(wb):
    ws = H.new_sheet(wb, "Ratings & Reviews", MISC, "⭐ RATINGS & REVIEWS",
                     "Rate hotels, restaurants, activities — 1 (meh) to 5 (magical)", 10)
    H.table(ws, 4, [
        {"h": "Type", "w": 15, "k": "in", "a": "center"},
        {"h": "Name", "w": 26, "k": "in", "a": "left"},
        {"h": "City", "w": 16, "k": "in", "a": "left"},
        {"h": "Rating (1-5)", "w": 11, "k": "in", "a": "center"},
        {"h": "Value for Money", "w": 13, "k": "in", "a": "center"},
        {"h": "Would Recommend?", "w": 14, "k": "in", "a": "center"},
        {"h": "Comments", "w": 38, "k": "in", "a": "left"},
    ], 30)
    H.dv(ws, "A5:A34", "Hotel,Restaurant,Activity,Tour,Transport,Shop,Other")
    H.dv_num(ws, "D5:D34")
    H.dv_num(ws, "E5:E34")
    H.dv(ws, "F5:F34", "Yes,No,Maybe")
    H.summary_box(ws, 4, 9, "📊 SUMMARY", [
        ("Average Rating", '=IFERROR(ROUND(AVERAGE(D5:D34),1),"—")', H.DEC1),
        ("Would Recommend", '=COUNTIF(F5:F34,"Yes")', H.INTF),
    ], width=17)
    H.finish(ws, freeze="A5")


def build_souvenir(wb):
    ws = H.new_sheet(wb, "Souvenir List", MISC, "🎁 SOUVENIR & GIFT LIST",
                     "Who's getting what — budget vs actual, ticked off as you buy", 8)
    H.table(ws, 4, [
        {"h": "Item", "w": 26, "k": "in", "a": "left"},
        {"h": "For", "w": 16, "k": "in", "a": "left"},
        {"h": "Where to Buy", "w": 24, "k": "in", "a": "left"},
        {"h": "Budget", "w": 12, "k": "in", "f": H.MONEY},
        {"h": "Actual", "w": 12, "k": "in", "f": H.MONEY},
        {"h": "Bought?", "w": 10, "k": "in", "a": "center"},
        {"h": "Wrapped?", "w": 10, "k": "in", "a": "center"},
        {"h": "Notes", "w": 26, "k": "in", "a": "left"},
    ], 20)
    H.dv(ws, "F5:F24", "✓,✗")
    H.dv(ws, "G5:G24", "✓,✗")
    for col in "ABCDEFGH":
        H.put(ws, f"{col}25", fillc=H.NAVY, border=True)
    H.put(ws, "A25", "TOTAL", font=H.F_TOTAL, fillc=H.NAVY, halign="left",
          indent=1, border=True)
    H.calc_cell(ws, "D25", "=SUM(D5:D24)", fmt=H.MONEY, font=H.F_TOTAL, fillc=H.NAVY)
    H.calc_cell(ws, "E25", "=SUM(E5:E24)", fmt=H.MONEY, font=H.F_TOTAL, fillc=H.NAVY)
    H.calc_cell(ws, "F25", '=COUNTIF(F5:F24,"✓")&" bought"', font=H.F_TOTAL,
                fillc=H.NAVY)
    H.finish(ws, freeze="A5")


def build_wifi(wb):
    ws = H.new_sheet(wb, "Wi-Fi & Passwords", MISC, "📶 WI-FI & PASSWORDS LOG",
                     "Every network from hotel to café — no more asking twice", 4)
    H.table(ws, 4, [
        {"h": "Location", "w": 24, "k": "in", "a": "left"},
        {"h": "Network Name (SSID)", "w": 26, "k": "in", "a": "left"},
        {"h": "Password", "w": 26, "k": "in", "a": "center"},
        {"h": "Notes", "w": 34, "k": "in", "a": "left"},
    ], 20)
    ws.merge_cells("A26:D26")
    H.put(ws, "A26", "🔒 Avoid banking on public Wi-Fi — use a VPN or your phone's hotspot.",
          font=H.F_NOTE, halign="left", indent=1)
    H.finish(ws, freeze="A5")


def build(wb):
    build_emergency(wb)
    build_journal(wb)
    build_rating(wb)
    build_souvenir(wb)
    build_wifi(wb)
