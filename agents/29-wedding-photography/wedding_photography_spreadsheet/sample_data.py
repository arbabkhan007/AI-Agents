"""A worked example: one studio, fifteen weddings, every tab populated.

The studio is Rowan & Fern Photography and the year it is having is
not a flattering one.  There is a wedding from three months ago still
sitting in editing past the promised turnaround, a couple who never
paid their balance, a date that has been promised to two couples at
once, and an elopement that was priced on instinct and works out at
less per hour than a supermarket shift.  A sample studio where
everything runs smoothly teaches nobody anything; this one teaches you
what each alert column is actually for.

Every row here is checked twice before it ships.  The keys must all be
*input* columns on their register - a value written into a formula
column is silently dropped and takes the formula with it - and every
value that feeds a drop-down must exist in that drop-down's list.
``tools/check_wedding_sample.py`` does both checks.

Dates are all relative to ``cfg.today``, so the example stays current
no matter when the workbook is built.  Weddings land on Saturdays
because real ones mostly do.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any, Callable, Dict, List

from .config import SHOT_LIST, TIMELINE_EVENTS, Config

Rows = List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _day(cfg: Config, offset: int) -> _dt.date:
    """A date `offset` days from the build date."""
    return cfg.today + _dt.timedelta(days=offset)


def _time(hour: int, minute: int = 0) -> _dt.time:
    return _dt.time(hour % 24, minute)


def _clt(n: int) -> str:
    return f"CLT-{n:04d}"


def _wed(n: int) -> str:
    return f"WED-{n:04d}"


def _phg(n: int) -> str:
    return f"PHG-{n:03d}"


def _mkt(n: int) -> str:
    return f"MKT-{n:04d}"


# The fifteen weddings, in the row order they appear in the register.
# (offset from today, couple, venue, venue type, city, guests, package)
# Offsets are all congruent to 6 mod 7, which is a Saturday when the
# build date is a Sunday, and close enough to one otherwise.
WEDDINGS = [
    (-400, "Nadia & Priya Raman-Okafor", "The Old Mill Barn", "Barn",
     "Hood River", 95, "Classic Wedding"),
    (-302, "Hollis & Jun Tanaka-Reed", "Cascade Vineyard Estate",
     "Vineyard", "Dundee", 130, "Premium Wedding"),
    (-190, "Imogen & Bram Castellanos", "St Agnes Church",
     "Church", "Portland", 150, "Premium Wedding"),
    (-92, "Saoirse & Eliot Vance", "Willow Creek Country House",
     "Country house", "Newberg", 110, "Classic Wedding"),
    (-64, "Margit & Tobias Lindqvist", "The Beaumont Hotel",
     "Hotel", "Portland", 80, "Classic Wedding"),
    (-29, "Delphine & Oscar Mbeki", "Rosegate Gardens",
     "Garden", "Lake Oswego", 70, "Essential Wedding"),
    (-1, "Yusra & Kaleem Haddad", "The Granary at Fir Point",
     "Barn", "Sherwood", 165, "Luxury Wedding"),
    (6, "Tessa & Rowan Whitfield", "Marchmont House",
     "Country house", "Salem", 100, "Classic Wedding"),
    (20, "Camille & Esme Fontaine", "Harbour Light Hotel",
     "Hotel", "Astoria", 120, "Premium Wedding"),
    (55, "Juno & Felix Arbuthnot", "Crater Rim Overlook",
     "Other", "Bend", 8, "Essential Wedding"),
    (118, "Beatrix & Idris Oyelaran", "The Winter Orangery",
     "Garden", "Portland", 90, "Classic Wedding"),
    (181, "Anneliese & Caspar von Hoff", "Thornbury Castle",
     "Castle", "Victoria", 180, "Luxury Wedding"),
    (181, "Marnie & Gus Pendleton", "Fernbrook Marquee",
     "Marquee", "Hillsboro", 140, "Premium Wedding"),
    (251, "Océane & Théo Belanger", "Villa Dorado",
     "Other", "Oaxaca", 60, "Luxury Wedding"),
    (342, "Sunniva & Abel Mackintosh", "The Assembly Rooms",
     "Other", "Portland", 115, "Classic Wedding"),
]

# Which booking is in which state.  Index is 1-based, matching WED-nnnn.
_DONE = (1, 2, 3)              # delivered, paid, reviewed
_EDITING_LATE = (4,)           # past the promised turnaround
_DELIVERED_WAITING = (5,)      # delivered, no review yet
_EDITING_OK = (6,)             # inside the turnaround, balance unpaid
_JUST_SHOT = (7,)              # cards backed up, nothing else
_PAST = _DONE + _EDITING_LATE + _DELIVERED_WAITING + _EDITING_OK \
    + _JUST_SHOT


def _booking_status(index: int) -> str:
    if index in _DONE:
        return "Complete"
    if index in _EDITING_LATE or index in _EDITING_OK:
        return "In editing"
    if index in _DELIVERED_WAITING:
        return "Delivered"
    if index in _JUST_SHOT:
        return "Wedding done"
    if index in (13, 15):
        return "Pencilled in"
    return "Confirmed"


# ---------------------------------------------------------------------------
# 1. Client CRM
# ---------------------------------------------------------------------------

_CLIENT_EXTRA = [
    # style, photo_style, delivery_pref, source, referred_by, priority
    ("Rustic", "Light and airy", "Gallery + album", "Instagram", "",
     "Normal"),
    ("Fine art", "Film emulation", "Everything", "Venue recommendation",
     "Cascade Vineyard Estate", "Normal"),
    ("Traditional cultural", "True to colour", "Gallery + prints",
     "Referral", "Nadia Raman-Okafor", "Normal"),
    ("Documentary", "True to colour", "Gallery + USB", "Website", "",
     "Normal"),
    ("Modern", "Dark and moody", "Online gallery only", "Google search",
     "", "Normal"),
    ("Boho", "Light and airy", "Gallery + USB", "Pinterest", "", "Low"),
    ("Editorial", "Dark and moody", "Everything", "Wedding fair", "",
     "High"),
    ("Classic", "True to colour", "Gallery + album", "Referral",
     "Hollis Tanaka-Reed", "High"),
    ("Documentary", "Light and airy", "Gallery + album", "Instagram",
     "", "Normal"),
    ("Elopement", "Film emulation", "Online gallery only", "TikTok", "",
     "Low"),
    ("Vintage", "Light and airy", "Gallery + prints",
     "Venue recommendation", "The Winter Orangery", "Normal"),
    ("Fine art", "Light and airy", "Everything", "Wedding directory",
     "", "High"),
    ("Rustic", "True to colour", "Gallery + USB", "Instagram", "",
     "Normal"),
    ("Destination", "Film emulation", "Everything", "Past client",
     "Imogen Castellanos", "High"),
    ("Modern", "Mixed - photographer's choice", "Gallery + album",
     "Word of mouth", "", "Normal"),
]

_CLIENT_STATUS = {
    1: "Complete", 2: "Complete", 3: "Complete", 4: "Wedding done",
    5: "Delivered", 6: "Wedding done", 7: "Wedding done",
}

_CLIENT_NOTES = {
    4: "Chasing me for the gallery. I am three weeks past my own "
       "promise and I have no good answer.",
    6: "Lovely couple, still owe the balance. Third reminder went "
       "out and I have not phoned yet.",
    8: "Questionnaire still not back and the wedding is next "
       "Saturday. Ring them, do not email again.",
    10: "Priced this on the phone in two minutes. See Profit "
        "Analysis before quoting the next elopement.",
    13: "Pencilled only. Same date as Anneliese & Caspar - whoever "
        "signs first gets it and I need to tell the other today.",
}


def clients(cfg: Config) -> Rows:
    rows: Rows = []
    for index, (offset, couple, venue, _vtype, city, _guests, _pkg) \
            in enumerate(WEDDINGS, start=1):
        first, second = couple.split(" & ")
        style, photo, delivery, source, referred, priority = \
            _CLIENT_EXTRA[index - 1]
        surname = second.split(" ")[-1]
        handle = first.split(" ")[0].lower()
        rows.append({
            "name": f"{first} {surname}" if " " not in first
                    else first,
            "partner": second,
            "email": f"{handle}.{surname.lower().replace(' ', '')}"
                     f"@example.com",
            "phone": f"+1 503 555 {1000 + index * 37:04d}",
            "country": "Mexico" if city == "Oaxaca"
                       else ("Canada" if city == "Victoria"
                             else "United States"),
            "status": _CLIENT_STATUS.get(index, "Booked"),
            "priority": priority,
            "wedding_date": _day(cfg, offset),
            "venue": venue,
            "venue_city": city,
            "source": source,
            "referred_by": referred,
            "first_contact": _day(cfg, offset - 330),
            "style": style,
            "photo_style": photo,
            "delivery_pref": delivery,
            "notes": _CLIENT_NOTES.get(index, ""),
            "marketing_ok": "No" if index in (3, 12) else "Yes",
        })

    # three live enquiries with no booking behind them yet
    rows += [
        {"name": "Wren Alcott", "partner": "Mateo Alcott",
         "email": "wren.alcott@example.com",
         "phone": "+1 503 555 6612", "country": "United States",
         "status": "Enquiry", "priority": "High",
         "wedding_date": _day(cfg, 236), "venue": "Still looking",
         "venue_city": "Portland", "source": "Instagram",
         "referred_by": "", "first_contact": _day(cfg, -11),
         "style": "Documentary", "photo_style": "Light and airy",
         "delivery_pref": "Gallery + album",
         "notes": "Consultation booked. Budget is real, date is a "
                  "Friday, I have it free.",
         "marketing_ok": "Yes"},
        {"name": "Fenella Brightwater", "partner": "Alice Nkemdirim",
         "email": "fenella.b@example.com",
         "phone": "+1 503 555 7741", "country": "United States",
         "status": "Enquiry", "priority": "Normal",
         "wedding_date": _day(cfg, 181), "venue": "Fernbrook Marquee",
         "venue_city": "Hillsboro", "source": "Venue recommendation",
         "referred_by": "Fernbrook Marquee", "first_contact":
         _day(cfg, -4),
         "style": "Boho", "photo_style": "Light and airy",
         "delivery_pref": "Online gallery only",
         "notes": "Third enquiry for that same Saturday. The date is "
                  "worth more than the package - price it that way.",
         "marketing_ok": "Yes"},
        {"name": "Isolde Marchetti", "partner": "Rafe Marchetti",
         "email": "isolde.m@example.com",
         "phone": "+1 503 555 8890", "country": "United States",
         "status": "Enquiry", "priority": "Low",
         "wedding_date": _day(cfg, 475), "venue": "Undecided",
         "venue_city": "Eugene", "source": "Google search",
         "referred_by": "", "first_contact": _day(cfg, -2),
         "style": "Classic", "photo_style": "True to colour",
         "delivery_pref": "Gallery + USB",
         "notes": "Eighteen months out and price-shopping. Worth one "
                  "good reply, not three.",
         "marketing_ok": "Yes"},
    ]
    return rows


# ---------------------------------------------------------------------------
# 2. Lead Tracker
# ---------------------------------------------------------------------------

def leads(cfg: Config) -> Rows:
    rows: Rows = []

    # the enquiries that turned into the fifteen bookings
    won = [
        (1, "Instagram", _mkt(2), "", 1400, 42),
        (2, "Venue recommendation", "", "", 2600, 31),
        (3, "Referral", "", _wed(1), 2700, 18),
        (4, "Website", _mkt(5), "", 1900, 26),
        (5, "Google search", "", "", 1800, 35),
        (6, "Pinterest", _mkt(8), "", 1300, 21),
        (7, "Wedding fair", _mkt(11), "", 3800, 47),
        (8, "Referral", "", _wed(2), 2000, 14),
        (9, "Instagram", _mkt(14), "", 2600, 29),
        (10, "TikTok", _mkt(17), "", 1250, 9),
        (11, "Venue recommendation", "", "", 1950, 23),
        (12, "Wedding directory", _mkt(20), "", 3900, 52),
        (13, "Instagram", _mkt(22), "", 2550, 16),
        (14, "Past client", "", _wed(3), 4100, 38),
        (15, "Word of mouth", "", "", 1900, 27),
    ]
    for index, source, campaign, referral, budget, lag in won:
        offset, couple, venue, _vt, _city, guests, package = \
            WEDDINGS[index - 1]
        first, second = couple.split(" & ")
        enquiry = offset - 330
        rows.append({
            "name": first, "partner": second,
            "email": f"{first.split(' ')[0].lower()}"
                     f".{second.split(' ')[-1].lower()}@example.com",
            "phone": f"+1 503 555 {1000 + index * 37:04d}",
            "client": _clt(index),
            "enquiry_date": _day(cfg, enquiry),
            "source": source, "campaign": campaign,
            "referred_by": referral,
            "wedding_date": _day(cfg, offset),
            "venue": venue, "guests": guests, "package": package,
            "budget": budget, "status": "Booked", "priority": "Normal",
            "replied": _day(cfg, enquiry + 1),
            "consultation": _day(cfg, enquiry + 6),
            "proposal_sent": _day(cfg, enquiry + 7),
            "decision_date": _day(cfg, enquiry + lag),
            "lost_reason": "", "follow_up": "",
            "notes": "",
        })

    # the ones that got away, and the ones still in play
    rows += [
        {"name": "Wren Alcott", "partner": "Mateo Alcott",
         "email": "wren.alcott@example.com",
         "phone": "+1 503 555 6612", "client": _clt(16),
         "enquiry_date": _day(cfg, -11), "source": "Instagram",
         "campaign": _mkt(24), "referred_by": "",
         "wedding_date": _day(cfg, 236), "venue": "Still looking",
         "guests": 85, "package": "Premium Wedding", "budget": 2800,
         "status": "Consultation booked", "priority": "High",
         "replied": _day(cfg, -11), "consultation": _day(cfg, 3),
         "proposal_sent": "", "decision_date": "", "lost_reason": "",
         "follow_up": _day(cfg, 4),
         "notes": "Best enquiry this month. Send the Premium "
                  "comparison before the call, not after."},
        {"name": "Fenella Brightwater", "partner": "Alice Nkemdirim",
         "email": "fenella.b@example.com",
         "phone": "+1 503 555 7741", "client": _clt(17),
         "enquiry_date": _day(cfg, -4),
         "source": "Venue recommendation", "campaign": "",
         "referred_by": "", "wedding_date": _day(cfg, 181),
         "venue": "Fernbrook Marquee", "guests": 110,
         "package": "Classic Wedding", "budget": 2100,
         "status": "Proposal sent", "priority": "Normal",
         "replied": _day(cfg, -4), "consultation": _day(cfg, -2),
         "proposal_sent": _day(cfg, -1), "decision_date": "",
         "lost_reason": "", "follow_up": _day(cfg, 6),
         "notes": "Third couple wanting that Saturday."},
        {"name": "Isolde Marchetti", "partner": "Rafe Marchetti",
         "email": "isolde.m@example.com",
         "phone": "+1 503 555 8890", "client": _clt(18),
         "enquiry_date": _day(cfg, -2), "source": "Google search",
         "campaign": "", "referred_by": "",
         "wedding_date": _day(cfg, 475), "venue": "Undecided",
         "guests": 60, "package": "", "budget": 0,
         "status": "New", "priority": "Low",
         "replied": "", "consultation": "", "proposal_sent": "",
         "decision_date": "", "lost_reason": "", "follow_up": "",
         "notes": "Not replied yet. This is the row the dashboard "
                  "is shouting about."},
        {"name": "Corrine Vasquez", "partner": "Dov Perlman",
         "email": "corrine.v@example.com",
         "phone": "+1 503 555 2214", "client": "",
         "enquiry_date": _day(cfg, -23), "source": "Instagram",
         "campaign": _mkt(22), "referred_by": "",
         "wedding_date": _day(cfg, 194), "venue": "The Beaumont Hotel",
         "guests": 140, "package": "Premium Wedding", "budget": 2500,
         "status": "Lost", "priority": "Normal",
         "replied": _day(cfg, -23), "consultation": _day(cfg, -18),
         "proposal_sent": _day(cfg, -17),
         "decision_date": _day(cfg, -9),
         "lost_reason": "Went with a cheaper photographer",
         "follow_up": "",
         "notes": "Lost on price by about $400. They asked twice "
                  "whether I could 'do it for less' - I should have "
                  "offered fewer hours, not a discount."},
        {"name": "Perpetua Odili", "partner": "Sam Odili",
         "email": "p.odili@example.com",
         "phone": "+1 503 555 3390", "client": "",
         "enquiry_date": _day(cfg, -37), "source": "Wedding fair",
         "campaign": _mkt(11), "referred_by": "",
         "wedding_date": _day(cfg, 118), "venue": "The Winter Orangery",
         "guests": 90, "package": "Classic Wedding", "budget": 1800,
         "status": "Date unavailable", "priority": "Normal",
         "replied": _day(cfg, -37), "consultation": "",
         "proposal_sent": "", "decision_date": _day(cfg, -36),
         "lost_reason": "Date already booked",
         "follow_up": "",
         "notes": "Offered them an associate shooter and they said "
                  "no. Worth asking the question anyway."},
        {"name": "Halle Bergstrom", "partner": "Nils Bergstrom",
         "email": "halle.b@example.com",
         "phone": "+1 503 555 4418", "client": "",
         "enquiry_date": _day(cfg, -19), "source": "Pinterest",
         "campaign": _mkt(8), "referred_by": "",
         "wedding_date": _day(cfg, 320), "venue": "Cascade Vineyard "
                                                 "Estate",
         "guests": 70, "package": "Classic Wedding", "budget": 1600,
         "status": "Contacted", "priority": "Normal",
         "replied": _day(cfg, -19), "consultation": "",
         "proposal_sent": "", "decision_date": "", "lost_reason": "",
         "follow_up": _day(cfg, -5),
         "notes": "Follow-up date has already passed. Chase today."},
        {"name": "Ottoline Reyes", "partner": "Gabriel Reyes",
         "email": "ottoline.r@example.com",
         "phone": "+1 503 555 5502", "client": "",
         "enquiry_date": _day(cfg, -6), "source": "Referral",
         "campaign": "", "referred_by": _wed(5),
         "wedding_date": _day(cfg, 285), "venue": "Marchmont House",
         "guests": 100, "package": "Premium Wedding", "budget": 2600,
         "status": "Consultation done", "priority": "High",
         "replied": _day(cfg, -6), "consultation": _day(cfg, -1),
         "proposal_sent": "", "decision_date": "", "lost_reason": "",
         "follow_up": _day(cfg, 1),
         "notes": "Proposal promised within 48 hours. Margit sent "
                  "them - thank her either way."},
        {"name": "Davina Achebe", "partner": "Kit Achebe",
         "email": "davina.a@example.com",
         "phone": "+1 503 555 9931", "client": "",
         "enquiry_date": _day(cfg, -58), "source": "Website",
         "campaign": _mkt(5), "referred_by": "",
         "wedding_date": _day(cfg, 410), "venue": "Thornbury Castle",
         "guests": 200, "package": "Luxury Wedding", "budget": 4500,
         "status": "Proposal sent", "priority": "High",
         "replied": _day(cfg, -58), "consultation": _day(cfg, -51),
         "proposal_sent": _day(cfg, -49), "decision_date": "",
         "lost_reason": "", "follow_up": _day(cfg, -21),
         "notes": "Biggest open proposal on the board and I have let "
                  "it go cold for seven weeks."},
        {"name": "Minna Soderberg", "partner": "Ray Soderberg",
         "email": "minna.s@example.com",
         "phone": "+1 503 555 1177", "client": "",
         "enquiry_date": _day(cfg, -71), "source": "Facebook",
         "campaign": "", "referred_by": "",
         "wedding_date": _day(cfg, 160), "venue": "Rosegate Gardens",
         "guests": 45, "package": "Essential Wedding", "budget": 900,
         "status": "Not a fit", "priority": "Low",
         "replied": _day(cfg, -70), "consultation": "",
         "proposal_sent": "", "decision_date": _day(cfg, -69),
         "lost_reason": "Budget below the Essential package",
         "follow_up": "",
         "notes": "Sent them two photographers who shoot at that "
                  "level. Costs nothing, comes back eventually."},
    ]
    return rows


# ---------------------------------------------------------------------------
# 3. Wedding Bookings
# ---------------------------------------------------------------------------

_BOOKING_TEAM = {
    # index: (lead, second)
    1: (_phg(1), _phg(2)), 2: (_phg(1), _phg(2)),
    3: (_phg(1), _phg(3)), 4: (_phg(1), _phg(2)),
    5: (_phg(1), ""), 6: (_phg(1), ""),
    7: (_phg(1), _phg(2)), 8: (_phg(1), _phg(3)),
    9: (_phg(1), _phg(2)), 10: (_phg(1), ""),
    11: (_phg(1), _phg(3)), 12: (_phg(1), _phg(2)),
    13: (_phg(3), _phg(5)), 14: (_phg(1), _phg(2)),
    15: (_phg(1), ""),
}

_BOOKING_MONEY = {
    # index: (addons, travel_fee, discount)
    1: (250, 0, 0), 2: (650, 0, 100), 3: (400, 45, 0),
    4: (250, 0, 150), 5: (0, 0, 0), 6: (0, 0, 0),
    7: (900, 120, 0), 8: (250, 0, 0), 9: (650, 95, 0),
    10: (0, 210, 0), 11: (250, 0, 0), 12: (1150, 380, 0),
    13: (400, 0, 0), 14: (650, 1250, 0), 15: (0, 0, 100),
}

_MUST_HAVES = {
    7: "Grandmother Haddad with both grandsons - she is 94 and "
       "will not last the evening.\nThe nikah signing, wide and "
       "close.\nKaleem's mother's gold bangles on the dress.",
    8: "Tessa's late father's watch on Rowan's wrist.\n"
       "The dog, Biscuit, in at least one family group.",
    9: "Both brides getting ready in the same room - they wanted "
       "no first look.\nThe lighthouse at sunset, with or without "
       "us.",
    12: "The castle from the drive, before anyone arrives.\n"
        "Four generations of von Hoff women together.",
}

_FAMILY = {
    7: "Couple + both sets of parents\nCouple + Haddad grandparents\n"
       "Couple + all siblings\nBride + her four aunts\n"
       "Groom + university friends",
    8: "Couple + Whitfield parents\nCouple + Tessa's mother alone\n"
       "Couple + Biscuit\nCouple + all four grandparents",
    9: "Couple + Fontaine parents\nCouple + Camille's brothers\n"
       "Couple + both mothers",
    12: "Couple + von Hoff parents\nCouple + all grandparents\n"
        "Four generations of women\nCouple + the whole family",
}

_SENSITIVE = {
    7: "Bride's father died in March. Do not ask the family to "
       "assemble 'both parents' - the list above is exact.",
    8: "Tessa's father died two years ago. Her mother will cry at "
       "the watch shot; give her a minute first.",
    12: "Groom's parents are divorced and will not stand together. "
        "Two separate parent groups, never one.",
}

_RESTRICTIONS = {
    3: "No flash during the service. Photographer stays behind the "
       "third pew throughout.",
    7: "No photographs of women who have not consented during the "
       "bridal preparation. Ask the aunt in the green first.",
    12: "Castle permit forbids drone flight. Confirmed in writing.",
}

_TRADITIONS = {
    3: "Full Catholic mass, about 70 minutes.",
    7: "Nikah signing, then a separate baraat arrival with drums "
       "at about 15:40. Allow 25 minutes, not 10.",
    14: "Mexican lazo and arras during the ceremony.",
}

_BOOKING_NOTES = {
    4: "Gallery is three weeks past the promise. Say so plainly "
       "and give a date you can actually keep.",
    6: "Balance unpaid 29 days after the wedding. Gallery stays "
       "unlisted until it clears - that was in the contract.",
    8: "Questionnaire not back and the wedding is in six days. "
       "Phone, do not email.",
    10: "Eight guests on a clifftop. Priced like a portrait shoot, "
        "costed like a wedding. Read Profit Analysis first.",
    13: "Pencilled in on a date already promised to Anneliese & "
        "Caspar. Whoever signs first takes it.",
    15: "Pencilled. No contract sent yet - that is the only thing "
        "standing between this and a real booking.",
}


def bookings(cfg: Config) -> Rows:
    rows: Rows = []
    for index, (offset, _couple, venue, vtype, city, guests, package) \
            in enumerate(WEDDINGS, start=1):
        lead, second = _BOOKING_TEAM[index]
        addons, travel, discount = _BOOKING_MONEY[index]
        status = _booking_status(index)
        ceremony = 14 if vtype != "Church" else 13
        if index == 10:
            ceremony = 17            # clifftop elopement at sunset
        hours = {"Essential Wedding": 6, "Classic Wedding": 8,
                 "Premium Wedding": 10, "Luxury Wedding": 12}[package]
        start_hour = ceremony - 4 if hours >= 10 else ceremony - 3
        if index == 10:
            start_hour = 16
            hours = 2
        row: Dict[str, Any] = {
            "client": _clt(index),
            "wedding_date": _day(cfg, offset),
            "status": status,
            "confirmed_date": "" if status == "Pencilled in"
                              else _day(cfg, offset - 300),
            "ceremony_time": _time(ceremony),
            "reception_time": _time(ceremony + 3),
            "photo_start": _time(start_hour),
            "photo_end": _time(start_hour + hours),
            "venue": venue,
            "venue_type": vtype,
            "prep_location": f"{venue} - bridal suite"
                             if vtype in ("Hotel", "Country house",
                                          "Castle")
                             else f"Family home, {city}",
            "ceremony_location": f"{venue} - "
                                 + ("chapel" if vtype == "Church"
                                    else "ceremony lawn"),
            "reception_location": f"{venue} - main room",
            "guests": guests,
            "photographer": lead,
            "second": second,
            "package": package,
            "addons": addons,
            "travel_fee": travel,
            "discount": discount,
            "must_haves": _MUST_HAVES.get(index, ""),
            "family_list": _FAMILY.get(index, ""),
            "key_guests": "Wedding planner: Odette Hale (on the day "
                          "from 11:00)" if index in (7, 12) else "",
            "traditions": _TRADITIONS.get(index, ""),
            "restrictions": _RESTRICTIONS.get(index, ""),
            "sensitivities": _SENSITIVE.get(index, ""),
            "special_requests": "Sparkler exit at 22:30 - venue has "
                                "agreed in writing."
                                if index in (7, 9, 12) else "",
            "questionnaire_sent": "" if index in (13, 15)
                                  else _day(cfg, offset - 60),
            "questionnaire_back": "",
            "notes": _BOOKING_NOTES.get(index, ""),
        }
        if index not in (8, 13, 15) and index <= 14:
            row["questionnaire_back"] = _day(cfg, offset - 44)
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 4. Packages & Pricing
# ---------------------------------------------------------------------------

def packages(cfg: Config) -> Rows:
    rows: Rows = [
        {"name": "Essential Wedding", "tier": "Essential",
         "active": "Yes",
         "summary": "Six hours, one photographer, online gallery. "
                    "The smallest package I will still put my name "
                    "on.",
         "hours": 6, "photographers": 1, "engagement": "No",
         "images": 350, "album": "No album", "print_credit": 0,
         "travel_allowance": 40,
         "inclusions": "Six hours of coverage\nOne photographer\n"
                       "350+ edited images\nOnline gallery for "
                       "12 months\nPrint release",
         "base_price": 1200, "standard_discount": 0,
         "album_cost": 0, "editing_hours": 12, "other_cost": 40},
        {"name": "Classic Wedding", "tier": "Classic",
         "active": "Yes",
         "summary": "Eight hours, engagement shoot, 20 page album. "
                    "Two thirds of my bookings land here.",
         "hours": 8, "photographers": 1, "engagement": "Yes",
         "images": 500, "album": "20 page album", "print_credit": 100,
         "travel_allowance": 60,
         "inclusions": "Eight hours of coverage\nOne photographer\n"
                       "Engagement shoot\n500+ edited images\n"
                       "20 page album\n$100 print credit\n"
                       "Online gallery for 12 months",
         "base_price": 1800, "standard_discount": 0,
         "album_cost": 185, "editing_hours": 18, "other_cost": 55},
        {"name": "Premium Wedding", "tier": "Premium",
         "active": "Yes",
         "summary": "Ten hours, two photographers, 30 page album. "
                    "The one to push when the guest list passes 100.",
         "hours": 10, "photographers": 2, "engagement": "Yes",
         "images": 700, "album": "30 page album", "print_credit": 250,
         "travel_allowance": 80,
         "inclusions": "Ten hours of coverage\nLead + second "
                       "shooter\nEngagement shoot\n700+ edited "
                       "images\n30 page album\n$250 print credit\n"
                       "Sneak peek within 48 hours",
         "base_price": 2500, "standard_discount": 0,
         "album_cost": 265, "editing_hours": 24, "other_cost": 70},
        {"name": "Luxury Wedding", "tier": "Luxury",
         "active": "Yes",
         "summary": "Twelve hours, two photographers, 40 page album "
                    "with parent copies. Sell the album, not the "
                    "hours.",
         "hours": 12, "photographers": 2, "engagement": "Yes",
         "images": 900, "album": "40 page album + parent copies",
         "print_credit": 500, "travel_allowance": 120,
         "inclusions": "Twelve hours of coverage\nLead + second "
                       "shooter\nEngagement shoot\n900+ edited "
                       "images\n40 page album + two parent copies\n"
                       "$500 print credit\nSneak peek within 24 "
                       "hours\nUSB in a presentation box",
         "base_price": 3500, "standard_discount": 0,
         "album_cost": 540, "editing_hours": 30, "other_cost": 95},
        {"name": "Elopement Hour", "tier": "Elopement",
         "active": "Yes",
         "summary": "Two hours, one photographer, 80 images. Priced "
                    "on instinct in 2024 and never revisited - the "
                    "hourly rate on this is the worst on the sheet.",
         "hours": 2, "photographers": 1, "engagement": "No",
         "images": 80, "album": "No album", "print_credit": 0,
         "travel_allowance": 30,
         "inclusions": "Two hours of coverage\nOne photographer\n"
                       "80+ edited images\nOnline gallery for "
                       "12 months",
         "base_price": 650, "standard_discount": 0,
         "album_cost": 0, "editing_hours": 5, "other_cost": 25},
        {"name": "Classic 2024", "tier": "Custom", "active": "No",
         "summary": "Last year's Classic, kept only so old bookings "
                    "and old numbers still make sense. Do not quote "
                    "it.",
         "hours": 8, "photographers": 1, "engagement": "Yes",
         "images": 450, "album": "20 page album", "print_credit": 75,
         "travel_allowance": 50,
         "inclusions": "Eight hours of coverage\nOne photographer\n"
                       "Engagement shoot\n450+ edited images\n"
                       "20 page album",
         "base_price": 1550, "standard_discount": 0,
         "album_cost": 185, "editing_hours": 18, "other_cost": 55},
    ]
    return rows


# ---------------------------------------------------------------------------
# 5. Photographer & Staff
# ---------------------------------------------------------------------------

def staff(cfg: Config) -> Rows:
    return [
        {"name": "Marisa Calloway", "role": "Lead photographer",
         "status": "Active", "type": "Owner",
         "phone": "+1 503 555 0101",
         "email": "marisa@rowanandfern.example.com",
         "started": _day(cfg, -2920), "day_rate": 0, "hour_rate": 0,
         "edit_rate": 0, "is_owner": "Yes", "can_lead": "Yes",
         "can_second": "No", "can_edit": "Yes",
         "specialism": "Documentary coverage, family diplomacy",
         "kit": "R6 II + R6, 35mm, 50mm, 85mm, 70-200mm, two "
                "speedlights",
         "insured": "Yes", "insurance_expiry": _day(cfg, 97),
         "notes": "The whole business. Every hour she spends "
                  "editing is an hour she is not selling - that is "
                  "what Owner hourly value on Settings is for."},
        {"name": "Dev Ashworth", "role": "Second shooter",
         "status": "Active", "type": "Self-employed contractor",
         "phone": "+1 503 555 0188",
         "email": "dev.ashworth@example.com",
         "started": _day(cfg, -1460), "day_rate": 350,
         "hour_rate": 45, "edit_rate": 0, "is_owner": "No",
         "can_lead": "No", "can_second": "Yes", "can_edit": "No",
         "specialism": "Reportage, dance floor, never misses a "
                       "speech reaction",
         "kit": "Own R6 + 24-70mm, 135mm", "insured": "Yes",
         "insurance_expiry": _day(cfg, -12),
         "notes": "Insurance expired twelve days ago. He cannot "
                  "shoot the next wedding until the new "
                  "certificate is on file."},
        {"name": "Joelle Nakamura", "role": "Second shooter",
         "status": "Active", "type": "Self-employed contractor",
         "phone": "+1 503 555 0231",
         "email": "joelle.n@example.com",
         "started": _day(cfg, -980), "day_rate": 375,
         "hour_rate": 48, "edit_rate": 32, "is_owner": "No",
         "can_lead": "Yes", "can_second": "Yes", "can_edit": "Yes",
         "specialism": "Fine art, can lead if Marisa is double "
                       "booked",
         "kit": "Own Z6 III + 35mm, 85mm", "insured": "Yes",
         "insurance_expiry": _day(cfg, 211),
         "notes": "The answer to a date clash. Costs more than Dev "
                  "and is worth it."},
        {"name": "Tomas Bright", "role": "Editor",
         "status": "Active", "type": "Self-employed contractor",
         "phone": "+1 503 555 0344",
         "email": "tomas@brightedits.example.com",
         "started": _day(cfg, -610), "day_rate": 0, "hour_rate": 0,
         "edit_rate": 28, "is_owner": "No", "can_lead": "No",
         "can_second": "No", "can_edit": "Yes",
         "specialism": "Culling and colour, 48 hour turnaround",
         "kit": "Calibrated studio, remote", "insured": "No",
         "insurance_expiry": "",
         "notes": "At $28 an hour he is cheaper than Marisa's own "
                  "time by a wide margin. The backlog on "
                  "WED-0004 exists because she did not send it."},
        {"name": "Priya Raman", "role": "Assistant",
         "status": "Occasional", "type": "Unpaid helper",
         "phone": "+1 503 555 0415",
         "email": "priya.raman@example.com",
         "started": _day(cfg, -240), "day_rate": 80, "hour_rate": 12,
         "edit_rate": 0, "is_owner": "No", "can_lead": "No",
         "can_second": "Yes", "can_edit": "No",
         "specialism": "Lighting, bags, keeping Aunt Margaret busy",
         "kit": "None - uses studio spares", "insured": "No",
         "insurance_expiry": "",
         "notes": "Studying photography. Not insured, so she "
                  "assists and does not shoot."},
    ]


# ---------------------------------------------------------------------------
# 6. Contracts & Documents
# ---------------------------------------------------------------------------

def contracts(cfg: Config) -> Rows:
    rows: Rows = []
    for index, (offset, _couple, venue, vtype, _city, _g, _p) in \
            enumerate(WEDDINGS, start=1):
        sent = offset - 305
        store = f"Dropbox / Weddings / {_wed(index)}"
        if index == 15:
            # the pencilled booking with nothing sent
            rows.append({
                "booking": _wed(index), "doc_type": "Wedding contract",
                "title": "Wedding photography contract",
                "required": "Yes", "status": "Outstanding",
                "sent_date": "", "signed_date": "", "expires": "",
                "stored_at": store, "signers": "Both parties",
                "notes": "Not sent. Until this goes out the date is "
                         "not held, whatever the calendar says."})
            continue
        if index == 13:
            rows.append({
                "booking": _wed(index), "doc_type": "Wedding contract",
                "title": "Wedding photography contract",
                "required": "Yes", "status": "Sent",
                "sent_date": _day(cfg, -9), "signed_date": "",
                "expires": _day(cfg, 5), "stored_at": store,
                "signers": "Both parties",
                "notes": "Sent nine days ago. The same date is "
                         "pencilled for another couple."})
            continue
        rows.append({
            "booking": _wed(index), "doc_type": "Wedding contract",
            "title": "Wedding photography contract", "required": "Yes",
            "status": "Counter-signed", "sent_date": _day(cfg, sent),
            "signed_date": _day(cfg, sent + 4), "expires": "",
            "stored_at": store, "signers": "Both parties",
            "notes": ""})
        rows.append({
            "booking": _wed(index), "doc_type": "Booking form",
            "title": "Booking form and deposit confirmation",
            "required": "Yes", "status": "Filed",
            "sent_date": _day(cfg, sent), "signed_date":
            _day(cfg, sent + 4), "expires": "", "stored_at": store,
            "signers": "Couple", "notes": ""})
        if vtype in ("Church", "Castle", "Vineyard", "Country house"):
            late = index in (9, 12)
            rows.append({
                "booking": _wed(index), "doc_type": "Venue permit",
                "title": f"{venue} photography permit",
                "required": "Yes",
                "status": "Outstanding" if late else "Filed",
                "sent_date": "" if late else _day(cfg, offset - 70),
                "signed_date": "" if late else _day(cfg, offset - 62),
                "expires": _day(cfg, offset + 1),
                "stored_at": store, "signers": "Venue",
                "notes": "Venue will not let me past the gate "
                         "without this." if late else ""})
        if index in (7, 12, 14):
            rows.append({
                "booking": _wed(index),
                "doc_type": "Venue public liability",
                "title": f"{venue} - proof of my cover",
                "required": "Yes", "status": "Filed",
                "sent_date": _day(cfg, offset - 50),
                "signed_date": _day(cfg, offset - 50),
                "expires": _day(cfg, 97), "stored_at": store,
                "signers": "Insurer", "notes": ""})
        if index in _PAST:
            rows.append({
                "booking": _wed(index), "doc_type": "Model release",
                "title": "Permission to use images in marketing",
                "required": "No",
                "status": "Signed" if index not in (3, 6)
                          else "Not needed",
                "sent_date": _day(cfg, offset + 2)
                if index not in (3, 6) else "",
                "signed_date": _day(cfg, offset + 5)
                if index not in (3, 6) else "", "expires": "",
                "stored_at": store, "signers": "Couple",
                "notes": "Declined - nothing from this wedding goes "
                         "online." if index in (3, 6) else ""})
        if index in (8, 9, 12):
            rows.append({
                "booking": _wed(index), "doc_type": "Timeline sign-off",
                "title": "Wedding day timeline, agreed version",
                "required": "Yes",
                "status": "Sent" if index == 8 else "Signed",
                "sent_date": _day(cfg, offset - 30),
                "signed_date": "" if index == 8
                               else _day(cfg, offset - 26),
                "expires": _day(cfg, offset - 7), "stored_at": store,
                "signers": "Couple",
                "notes": "Unsigned with six days to go." if index == 8
                         else ""})
        if _BOOKING_TEAM[index][1]:
            rows.append({
                "booking": _wed(index),
                "doc_type": "Second shooter agreement",
                "title": "Second shooter terms and copyright "
                         "assignment",
                "required": "Yes",
                "status": "Signed" if index != 9 else "Outstanding",
                "sent_date": _day(cfg, offset - 40) if index != 9
                             else "",
                "signed_date": _day(cfg, offset - 38) if index != 9
                               else "", "expires": "",
                "stored_at": store, "signers": "Second shooter",
                "notes": "Dev's insurance certificate has expired "
                         "too - fix both together." if index == 9
                         else ""})
    return rows


# ---------------------------------------------------------------------------
# 7. Payments & Invoices
# ---------------------------------------------------------------------------

_PACKAGE_PRICE = {"Essential Wedding": 1200, "Classic Wedding": 1800,
                  "Premium Wedding": 2500, "Luxury Wedding": 3500}


def payments(cfg: Config) -> Rows:
    rows: Rows = []
    counter = 0
    for index, (offset, _couple, _venue, _vt, _city, _g, package) in \
            enumerate(WEDDINGS, start=1):
        if index == 15:
            continue                 # pencilled, nothing invoiced yet
        addons, travel, discount = _BOOKING_MONEY[index]
        total = _PACKAGE_PRICE[package] + addons + travel - discount
        deposit = round(total * 0.30, 2)
        second = round(total * 0.35, 2)
        final = round(total - deposit - second, 2)
        booked = offset - 300
        paid_all = index not in (6, 13)

        counter += 1
        rows.append({
            "booking": _wed(index), "stage": "Booking deposit",
            "reference": f"INV-{2000 + counter}",
            "description": "Deposit to hold the date",
            "amount": deposit, "due_date": _day(cfg, booked + 7),
            "received": deposit if index != 13 else 0,
            "received_date": _day(cfg, booked + 3) if index != 13
                             else "",
            "method": "Bank transfer" if index != 13 else "",
            "fee": 0, "reminders": 0, "last_reminder": "",
            "notes": "Date is not held until this clears."
                     if index == 13 else ""})

        counter += 1
        due_second = offset - 90
        got_second = due_second < 0 and index != 13
        rows.append({
            "booking": _wed(index), "stage": "Second instalment",
            "reference": f"INV-{2000 + counter}",
            "description": "Second instalment, 90 days before",
            "amount": second, "due_date": _day(cfg, due_second),
            "received": second if got_second else 0,
            "received_date": _day(cfg, due_second + 2)
                             if got_second else "",
            "method": "Bank transfer" if got_second else "",
            "fee": 0, "reminders": 0, "last_reminder": "",
            "notes": ""})

        counter += 1
        due_final = offset - 14
        got_final = due_final < 0 and paid_all
        rows.append({
            "booking": _wed(index), "stage": "Final payment",
            "reference": f"INV-{2000 + counter}",
            "description": "Balance, due two weeks before the day",
            "amount": final, "due_date": _day(cfg, due_final),
            "received": final if got_final else 0,
            "received_date": _day(cfg, due_final + 1)
                             if got_final else "",
            "method": "Bank transfer" if got_final else "",
            "fee": 0,
            "reminders": 3 if index == 6 else 0,
            "last_reminder": _day(cfg, -6) if index == 6 else "",
            "notes": "Forty-three days overdue. Three emails, no "
                     "phone call yet. Make the phone call."
                     if index == 6 else ""})

        if index in (3, 11):
            counter += 1
            rows.append({
                "booking": _wed(index), "stage": "Album",
                "reference": f"INV-{2000 + counter}",
                "description": "Album upgrade to 40 pages",
                "amount": 320, "due_date": _day(cfg, offset + 40),
                "received": 320 if index == 3 else 0,
                "received_date": _day(cfg, offset + 44)
                                 if index == 3 else "",
                "method": "Credit card" if index == 3 else "",
                "fee": 9.60 if index == 3 else 0,
                "reminders": 0, "last_reminder": "", "notes": ""})
        if index == 2:
            counter += 1
            rows.append({
                "booking": _wed(index), "stage": "Prints",
                "reference": f"INV-{2000 + counter}",
                "description": "Parent print sets, two of",
                "amount": 180, "due_date": _day(cfg, offset + 60),
                "received": 180, "received_date":
                _day(cfg, offset + 58), "method": "Stripe",
                "fee": 5.52, "reminders": 0, "last_reminder": "",
                "notes": "Print sales are the quietest money in "
                         "this business."})
        if index == 7:
            counter += 1
            rows.append({
                "booking": _wed(index), "stage": "Overtime",
                "reference": f"INV-{2000 + counter}",
                "description": "One extra hour on the night, agreed "
                               "at 22:10 by text",
                "amount": 250, "due_date": _day(cfg, 13),
                "received": 0, "received_date": "", "method": "",
                "fee": 0, "reminders": 0, "last_reminder": "",
                "notes": "Agreed in writing on the night. Invoice "
                         "it while they still remember saying yes."})
        if index == 4:
            counter += 1
            rows.append({
                "booking": _wed(index), "stage": "Refund",
                "reference": f"CRN-{2000 + counter}",
                "description": "Goodwill credit for the late gallery",
                "amount": -150, "due_date": _day(cfg, -5),
                "received": -150, "received_date": _day(cfg, -5),
                "method": "Bank transfer", "fee": 0, "reminders": 0,
                "last_reminder": "",
                "notes": "Cheaper than the review they would have "
                         "left. It still comes out of the margin."})
    return rows


# ---------------------------------------------------------------------------
# 8. Wedding Timeline
# ---------------------------------------------------------------------------

_TIMELINE_LOCATIONS = {
    "venue_detail": "Ceremony room", "bride_prep": "Bridal suite",
    "groom_prep": "Groom's room", "dress_details": "Bridal suite",
    "first_look": "Walled garden", "couple_portraits_1":
    "Walled garden", "guests_arrive": "Entrance",
    "ceremony": "Ceremony room", "confetti": "Front steps",
    "family_groups": "South lawn", "wedding_party": "South lawn",
    "couple_portraits_2": "Orchard", "cocktail_hour": "Terrace",
    "reception_detail": "Dining room", "entrance": "Dining room",
    "speeches": "Dining room", "cake_cutting": "Dining room",
    "first_dance": "Dance floor", "dancing": "Dance floor",
    "sparkler_exit": "Front drive",
}

_CRITICAL = {"ceremony", "family_groups", "first_dance", "speeches",
             "cake_cutting", "first_look"}


def _timeline_for(cfg: Config, index: int, keys, *, done: bool,
                  drift: Dict[str, int] = None) -> Rows:
    """One wedding's running order, drawn from the standard plan."""
    drift = drift or {}
    offset, _couple, _venue, vtype, _city, _g, _pkg = \
        WEDDINGS[index - 1]
    ceremony_hour = 13 if vtype == "Church" else 14
    lead, second = _BOOKING_TEAM[index]
    rows: Rows = []
    for key, label, minutes, duration, role in TIMELINE_EVENTS:
        if key not in keys:
            continue
        staff_id = second if role == "Second shooter" and second \
            else lead
        row: Dict[str, Any] = {
            "booking": _wed(index), "event": label, "label": "",
            "offset": minutes, "time_override": "",
            "duration": duration,
            "location": _TIMELINE_LOCATIONS.get(key, ""),
            "staff": staff_id,
            "critical": "Yes" if key in _CRITICAL else "No",
            "notes": "", "done": "Yes" if done else "No",
            "actual": "",
        }
        if done:
            total = ceremony_hour * 60 + minutes + drift.get(key, 0)
            row["actual"] = _time(total // 60, total % 60)
        rows.append(row)
    return rows


def timeline(cfg: Config) -> Rows:
    all_keys = [k for k, _l, _m, _d, _r in TIMELINE_EVENTS]
    rows: Rows = []

    # the wedding that happened yesterday, with what actually
    # happened written next to what was meant to happen
    rows += _timeline_for(
        cfg, 7, all_keys, done=True,
        drift={"bride_prep": 20, "groom_prep": 15, "first_look": 25,
               "couple_portraits_1": 30, "ceremony": 18,
               "confetti": 18, "family_groups": 22,
               "wedding_party": 35, "couple_portraits_2": 40,
               "speeches": 12, "first_dance": 5, "dancing": 5,
               "sparkler_exit": 0})
    rows[0]["notes"] = ("Baraat arrived at 15:40 with drums. Twenty "
                        "five minutes, not ten - put that in the "
                        "template for next time.")
    for row in rows:
        if row["event"] == "Family group photographs":
            row["notes"] = ("Ran 22 minutes late because nobody had "
                            "told the uncles to stay. Print the "
                            "family list next time.")

    # next Saturday: planned, nothing done
    rows += _timeline_for(cfg, 8, all_keys[:18], done=False)

    # three weeks out: two brides, no first look
    keys_9 = [k for k in all_keys
              if k not in ("first_look", "groom_prep")]
    rows += _timeline_for(cfg, 9, keys_9, done=False)

    # the elopement: four lines is the whole day
    rows += [
        {"booking": _wed(10), "event": "Venue and detail shots",
         "label": "Trailhead and rim", "offset": -45, "duration": 20,
         "time_override": "", "location": "Crater Rim Overlook",
         "staff": _phg(1), "critical": "No",
         "notes": "Forty minute walk in from the car park. That walk "
                  "is why this package loses money.",
         "done": "No", "actual": ""},
        {"booking": _wed(10), "event": "Wedding ceremony",
         "label": "Vows at the overlook", "offset": 0, "duration": 20,
         "time_override": _time(17), "location": "Crater Rim Overlook",
         "staff": _phg(1), "critical": "Yes", "notes": "",
         "done": "No", "actual": ""},
        {"booking": _wed(10), "event": "Couple portraits",
         "label": "Golden hour portraits", "offset": 25,
         "duration": 45, "time_override": "",
         "location": "Rim trail", "staff": _phg(1), "critical": "Yes",
         "notes": "Sunset is at 18:12. There is no second chance.",
         "done": "No", "actual": ""},
        {"booking": _wed(10), "event": "Confetti and congratulations",
         "label": "Champagne on the rock", "offset": 75,
         "duration": 15, "time_override": "",
         "location": "Rim trail", "staff": _phg(1), "critical": "No",
         "notes": "", "done": "No", "actual": ""},
    ]

    # the castle, six months out, skeleton only
    rows += _timeline_for(
        cfg, 12,
        ["venue_detail", "bride_prep", "ceremony", "family_groups",
         "speeches", "first_dance"], done=False)
    for row in rows[-6:]:
        row["notes"] = ("Skeleton only. Firm this up at the venue "
                        "visit in month four.")
    return rows


# ---------------------------------------------------------------------------
# 9. Shot List Manager
# ---------------------------------------------------------------------------

_SHOT_WHEN = {
    "Details": "Before the ceremony",
    "Preparation": "Getting ready",
    "Couple": "Couple portraits",
    "Family": "Family groups",
    "Ceremony": "Ceremony",
    "Reception": "Reception",
}

_GROUP_NAME = {
    "Details and venue": "Details", "Getting ready": "Preparation",
    "The couple": "Couple", "Family and groups": "Family",
    "The ceremony": "Ceremony", "The reception": "Reception",
}


def _shot_group(label: str) -> str:
    """Map a config shot group onto a Shot group drop-down value."""
    if label in _GROUP_NAME:
        return _GROUP_NAME[label]
    lowered = label.lower()
    for key, value in (("detail", "Details"), ("ready", "Preparation"),
                       ("prep", "Preparation"), ("couple", "Couple"),
                       ("portrait", "Couple"), ("family", "Family"),
                       ("group", "Family"), ("ceremony", "Ceremony"),
                       ("reception", "Reception"),
                       ("party", "Reception"),
                       ("evening", "Reception")):
        if key in lowered:
            return value
    return "Details"


def shots(cfg: Config) -> Rows:
    rows: Rows = []

    # WED-0009, three weeks out: the full standard list, nothing shot
    for _key, label, shot_names in SHOT_LIST:
        group = _shot_group(label)
        for shot in shot_names:
            rows.append({
                "booking": _wed(9), "group_name": group, "shot": shot,
                "people": "", "priority": "Normal", "must_have": "No",
                "requested_by": "Your standard list",
                "when": _SHOT_WHEN[group], "location": "",
                "notes": "", "done": "No", "taken_at": "",
                "skipped": "No", "skip_reason": "", "delivered": "No"})

    # the two things that wedding is actually about
    rows += [
        {"booking": _wed(9), "group_name": "Couple",
         "shot": "Both brides getting ready in the same room",
         "people": "Camille, Esme", "priority": "High",
         "must_have": "Yes", "requested_by": "Couple asked for it",
         "when": "Getting ready", "location": "Harbour suite",
         "notes": "They did not want a first look. This replaces it.",
         "done": "No", "taken_at": "", "skipped": "No",
         "skip_reason": "", "delivered": "No"},
        {"booking": _wed(9), "group_name": "Couple",
         "shot": "The lighthouse at sunset",
         "people": "Camille, Esme", "priority": "High",
         "must_have": "Yes", "requested_by": "Couple asked for it",
         "when": "Golden hour", "location": "Point headland",
         "notes": "Eleven minute walk. Leave the reception at 19:40.",
         "done": "No", "taken_at": "", "skipped": "No",
         "skip_reason": "", "delivered": "No"},
        {"booking": _wed(9), "group_name": "Family",
         "shot": "Couple + Fontaine parents", "people":
         "Camille, Esme, Ariane, Luc", "priority": "High",
         "must_have": "Yes", "requested_by": "Couple asked for it",
         "when": "Family groups", "location": "Terrace",
         "notes": "", "done": "No", "taken_at": "", "skipped": "No",
         "skip_reason": "", "delivered": "No"},
        {"booking": _wed(9), "group_name": "Family",
         "shot": "Couple + Camille's brothers",
         "people": "Camille, Esme, Luca, Theo", "priority": "Normal",
         "must_have": "Yes", "requested_by": "Couple asked for it",
         "when": "Family groups", "location": "Terrace", "notes": "",
         "done": "No", "taken_at": "", "skipped": "No",
         "skip_reason": "", "delivered": "No"},
        {"booking": _wed(9), "group_name": "Family",
         "shot": "Couple + both mothers",
         "people": "Camille, Esme, Ariane, Sylvie",
         "priority": "Normal", "must_have": "Yes",
         "requested_by": "Parent asked for it", "when":
         "Family groups", "location": "Terrace", "notes": "",
         "done": "No", "taken_at": "", "skipped": "No",
         "skip_reason": "", "delivered": "No"},
    ]

    # WED-0008, next Saturday: the short list that matters
    eight = [
        ("Details", "The dress hanging", "", "Normal", "No",
         "Your standard list"),
        ("Details", "Rings on the invitation suite", "", "Normal",
         "No", "Your standard list"),
        ("Preparation", "Tessa's father's watch going on Rowan's "
                        "wrist", "Rowan", "High", "Yes",
         "Couple asked for it"),
        ("Preparation", "Mother fastening the dress", "Tessa, Hilary",
         "High", "Yes", "Parent asked for it"),
        ("Ceremony", "The walk down the aisle", "", "High", "No",
         "Your standard list"),
        ("Ceremony", "The vows, both faces", "", "High", "No",
         "Your standard list"),
        ("Ceremony", "Ring exchange, close", "", "Normal", "No",
         "Your standard list"),
        ("Family", "Couple + Whitfield parents",
         "Tessa, Rowan, Gavin, Lorna", "High", "Yes",
         "Couple asked for it"),
        ("Family", "Couple + Tessa's mother alone", "Tessa, Hilary",
         "High", "Yes", "Couple asked for it"),
        ("Family", "Couple + Biscuit the dog", "Tessa, Rowan",
         "Normal", "Yes", "Couple asked for it"),
        ("Family", "Couple + all four grandparents", "", "Normal",
         "Yes", "Parent asked for it"),
        ("Couple", "Golden hour in the long meadow", "", "High", "No",
         "Your own idea"),
        ("Reception", "Room before the guests come in", "", "Normal",
         "No", "Your standard list"),
        ("Reception", "Speeches - reaction shots, not the speaker",
         "", "High", "No", "Your own idea"),
        ("Reception", "First dance, wide and close", "", "High", "No",
         "Your standard list"),
    ]
    for group, shot, people, priority, must, source in eight:
        rows.append({
            "booking": _wed(8), "group_name": group, "shot": shot,
            "people": people, "priority": priority, "must_have": must,
            "requested_by": source, "when": _SHOT_WHEN[group],
            "location": "", "notes": "", "done": "No", "taken_at": "",
            "skipped": "No", "skip_reason": "", "delivered": "No"})

    # WED-0007, shot yesterday: what got taken and what did not
    seven = [
        ("Family", "Grandmother Haddad with both grandsons",
         "Yusra, Kaleem, Nadra", "High", "Yes",
         "Couple asked for it", "Yes", _time(16, 42), "No", ""),
        ("Ceremony", "The nikah signing, wide", "", "High", "Yes",
         "Couple asked for it", "Yes", _time(14, 18), "No", ""),
        ("Ceremony", "The nikah signing, close on the pen", "",
         "High", "Yes", "Couple asked for it", "Yes",
         _time(14, 21), "No", ""),
        ("Details", "Kaleem's mother's gold bangles on the dress",
         "", "High", "Yes", "Parent asked for it", "Yes",
         _time(11, 30), "No", ""),
        ("Details", "Baraat drums arriving", "", "Normal", "No",
         "Your own idea", "Yes", _time(15, 44), "No", ""),
        ("Family", "Couple + both sets of parents", "", "High", "Yes",
         "Your standard list", "Yes", _time(16, 30), "No", ""),
        ("Family", "Couple + Haddad grandparents", "", "High", "Yes",
         "Couple asked for it", "Yes", _time(16, 36), "No", ""),
        ("Family", "Couple + all siblings", "", "Normal", "Yes",
         "Couple asked for it", "Yes", _time(16, 48), "No", ""),
        ("Family", "Bride + her four aunts", "", "Normal", "Yes",
         "Parent asked for it", "Yes", _time(16, 55), "No", ""),
        ("Family", "Groom + university friends", "", "Low", "No",
         "Couple asked for it", "No", "", "Yes",
         "Half of them were already on the dance floor and the "
         "light had gone. Offered a reshoot at the reception, "
         "they declined."),
        ("Couple", "Sparkler exit", "", "High", "No",
         "Couple asked for it", "Yes", _time(22, 31), "No", ""),
        ("Reception", "Speeches - the father of the bride's chair, "
                      "empty, with his photograph on it", "",
         "High", "Yes", "Your own idea", "Yes", _time(19, 52), "No",
         ""),
    ]
    for (group, shot, people, priority, must, source, done, taken,
         skipped, reason) in seven:
        rows.append({
            "booking": _wed(7), "group_name": group, "shot": shot,
            "people": people, "priority": priority, "must_have": must,
            "requested_by": source, "when": _SHOT_WHEN[group],
            "location": "", "notes": "", "done": done,
            "taken_at": taken, "skipped": skipped,
            "skip_reason": reason, "delivered": "No"})

    # WED-0012, the castle: the four shots booked six months early
    twelve = [
        ("Details", "The castle from the drive, before anyone "
                    "arrives", "High", "Yes", "Couple asked for it"),
        ("Family", "Four generations of von Hoff women",
         "High", "Yes", "Couple asked for it"),
        ("Family", "Couple + von Hoff parents - father's side only",
         "High", "Yes", "Couple asked for it"),
        ("Family", "Couple + von Hoff parents - mother's side only",
         "High", "Yes", "Couple asked for it"),
    ]
    for group, shot, priority, must, source in twelve:
        rows.append({
            "booking": _wed(12), "group_name": group, "shot": shot,
            "people": "", "priority": priority, "must_have": must,
            "requested_by": source, "when": _SHOT_WHEN[group],
            "location": "", "notes": "Parents are divorced and will "
                                     "not stand together."
            if "side only" in shot else "",
            "done": "No", "taken_at": "", "skipped": "No",
            "skip_reason": "", "delivered": "No"})
    return rows


# ---------------------------------------------------------------------------
# 10. Editing Workflow
# ---------------------------------------------------------------------------

def editing(cfg: Config) -> Rows:
    rows: Rows = []
    recipe = {
        # index: (editor, outsourced, steps done, shot, kept,
        #         delivered, hours, rush)
        1: (_phg(1), "No", 10, 3800, 620, 540, 19.5, "No"),
        2: (_phg(4), "Yes", 10, 5200, 880, 760, 24.0, "No"),
        3: (_phg(1), "No", 10, 4900, 820, 710, 27.5, "No"),
        4: (_phg(1), "No", 5, 4100, 690, 0, 9.0, "No"),
        5: (_phg(4), "Yes", 10, 3600, 610, 520, 16.5, "No"),
        6: (_phg(1), "No", 7, 2900, 470, 0, 8.0, "No"),
        7: (_phg(1), "No", 2, 6400, 0, 0, 1.5, "Yes"),
    }
    steps = ["step_backed_up", "step_imported", "step_culled",
             "step_selected", "step_edited", "step_colour",
             "step_retouched", "step_album_designed",
             "step_preview_sent", "step_final_uploaded"]
    notes = {
        4: "Ninety-two days since the wedding against a forty-two "
           "day promise. It stalled at 'selection complete' because "
           "I kept meaning to do it myself. Tomas charges $28 an "
           "hour. Send it.",
        6: "Deliberately parked at retouching until the balance "
           "clears. That is in the contract and the couple know.",
        7: "Cards backed up to two drives before I went to bed. "
           "That is the only step that cannot wait.",
    }
    for index, (editor, outsourced, done_steps, shot, kept,
                delivered, hours, rush) in recipe.items():
        offset = WEDDINGS[index - 1][0]
        row: Dict[str, Any] = {
            "booking": _wed(index), "editor": editor,
            "outsourced": outsourced,
            "priority": "High" if index in (4, 7) else "Normal",
            "rush": rush,
            "started": _day(cfg, offset + 2),
            "preview_sent": _day(cfg, offset + 7)
                            if done_steps >= 9 else "",
            "finished": _day(cfg, offset + 34)
                        if done_steps == 10 else "",
            "shot_count": shot, "kept": kept,
            "delivered_count": delivered, "hours": hours,
            "backup": "Yes",
            "notes": notes.get(index, ""),
        }
        for position, key in enumerate(steps, start=1):
            row[key] = "Yes" if position <= done_steps else "No"
        if index == 7:
            row["started"] = _day(cfg, 0)
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 11. Gallery & Delivery
# ---------------------------------------------------------------------------

def gallery(cfg: Config) -> Rows:
    recipe = {
        1: ("Pic-Time", "Delivered", 540, 1240, 310, 96, "Yes",
            "Yes", 310, 0),
        2: ("Pic-Time", "Delivered", 760, 2180, 540, 171, "Yes",
            "Yes", 180, 140),
        3: ("Pic-Time", "Delivered", 710, 1890, 480, 142, "No",
            "Yes", 0, 320),
        4: ("Pic-Time", "Created", 0, 0, 0, 0, "No", "No", 0, 0),
        5: ("Pic-Time", "Delivered", 520, 640, 210, 58, "Yes", "No",
            0, 0),
        6: ("Pic-Time", "Preview sent", 40, 96, 0, 11, "No", "No",
            0, 0),
        7: ("Pic-Time", "Not created", 0, 0, 0, 0, "No", "No", 0, 0),
    }
    notes = {
        3: "Expires in a few weeks. They have not downloaded the "
           "full set - warn them before it closes, then sell the "
           "extension.",
        4: "Gallery exists and is empty. The couple have the link.",
        5: "Delivered and nobody has asked for a review yet. That "
           "is money sitting on the table.",
        6: "Preview only. The full gallery goes live when the "
           "balance clears.",
        7: "Shot yesterday. Sneak peek promised within 24 hours for "
           "Luxury - that clock is running.",
    }
    rows: Rows = []
    for index, (platform, status, images, views, downloads, favs,
                usb, album, print_sales, extra) in recipe.items():
        offset = WEDDINGS[index - 1][0]
        delivered_on = _day(cfg, offset + 34) \
            if status in ("Delivered", "Archived") else ""
        rows.append({
            "booking": _wed(index), "platform": platform,
            "gallery_name": f"{WEDDINGS[index - 1][1]} - "
                            f"{WEDDINGS[index - 1][2]}",
            "link": f"https://gallery.example.com/{_wed(index).lower()}",
            "has_password": "Yes", "status": status,
            "delivered_on": delivered_on, "images": images,
            "expiry_warned": "No", "archived": "No",
            "first_viewed": _day(cfg, offset + 35)
                            if delivered_on else "",
            "views": views, "downloads": downloads,
            "favourites": favs, "usb_sent": usb,
            "album_ordered": album,
            "album_sent": _day(cfg, offset + 95)
                          if album == "Yes" and index in (1, 2)
                          else "",
            "print_sales": print_sales, "extra_sales": extra,
            "review_asked": _day(cfg, offset + 40)
                            if index in (1, 2, 3) else "",
            "notes": notes.get(index, ""),
        })
    return rows


# ---------------------------------------------------------------------------
# 12. Equipment Inventory
# ---------------------------------------------------------------------------

def equipment(cfg: Config) -> Rows:
    kit = [
        ("Canon R6 Mark II (body 1)", "Camera body", "Canon",
         "R6M2-884217", "In use", "Excellent", _phg(1), -540, 2499,
         5, "Yes", 2100, 185000, 400000, "", 2499,
         "The one that goes to every wedding."),
        ("Canon R6 (body 2)", "Camera body", "Canon", "R6-771940",
         "In use", "Good", _phg(1), -1180, 2099, 5, "Yes", 1200,
         372000, 400000, "Canon R6 Mark II (body 1)", 2499,
         "Shutter count is at 93% of rated life. Budget for the "
         "replacement now, not in the week it dies."),
        ("Canon R8 (backup body)", "Camera body", "Canon",
         "R8-110562", "Spare", "Excellent", "", -300, 1499, 5,
         "Yes", 1300, 41000, 400000, "Canon R6 (body 2)", 1499,
         "Lives in the car. Has never been needed and that is the "
         "entire point."),
        ("Sigma 35mm f1.4 Art", "Lens", "Sigma", "SG35-22914",
         "In use", "Good", _phg(1), -1460, 849, 8, "Yes", 600, 0, 0,
         "", 899, ""),
        ("Canon RF 50mm f1.2L", "Lens", "Canon", "RF50-449021",
         "In use", "Excellent", _phg(1), -720, 2299, 8, "Yes", 2000,
         0, 0, "", 2299, "The look the whole brand is built on."),
        ("Canon RF 85mm f1.2L", "Lens", "Canon", "RF85-558130",
         "In use", "Excellent", _phg(1), -400, 2699, 8, "Yes", 2400,
         0, 0, "", 2699, ""),
        ("Canon RF 70-200mm f2.8L", "Lens", "Canon",
         "RF70200-663094", "Being repaired", "Needs repair", "",
         -980, 2599, 8, "Yes", 2200, 0, 0, "", 2699,
         "Focus motor is grinding. Away for three weeks and the "
         "next wedding is in six days - hire one if it is not back "
         "by Thursday."),
        ("Canon RF 24-70mm f2.8L", "Lens", "Canon", "RF2470-229417",
         "In use", "Good", _phg(2), -1300, 2299, 8, "Yes", 1700, 0,
         0, "", 2399, "On permanent loan to Dev."),
        ("Godox V1 speedlight (1)", "Flash / speedlight", "Godox",
         "V1-330881", "In use", "Good", _phg(1), -900, 259, 4, "No",
         0, 0, 0, "", 269, ""),
        ("Godox V1 speedlight (2)", "Flash / speedlight", "Godox",
         "V1-330882", "In use", "Fair", _phg(1), -900, 259, 4, "No",
         0, 0, 0, "Godox V1 speedlight (1)", 269,
         "Hot shoe is loose. Works, but I would not trust it for a "
         "first dance."),
        ("Godox AD200 Pro", "Studio lighting", "Godox",
         "AD200-771203", "In use", "Excellent", _phg(1), -610, 349,
         5, "No", 0, 0, 0, "", 369, ""),
        ("MagMod modifier kit", "Light modifier", "MagMod",
         "MM-KIT-9921", "In use", "Good", _phg(1), -1100, 229, 6,
         "No", 0, 0, 0, "", 249, ""),
        ("Manfrotto 055 tripod", "Tripod / monopod", "Manfrotto",
         "MN055-412098", "In use", "Good", _phg(1), -1800, 219, 10,
         "No", 0, 0, 0, "", 239, ""),
        ("SanDisk 128GB CFexpress x6", "Memory card", "SanDisk",
         "SD-CFE-BATCH-7", "In use", "Good", _phg(1), -420, 1080, 3,
         "No", 0, 0, 0, "", 1140,
         "Six cards. Never reformat one until the wedding is on two "
         "drives - that rule is the business."),
        ("SanDisk 64GB SD x8", "Memory card", "SanDisk",
         "SD-SDXC-BATCH-4", "In use", "Fair", _phg(2), -1500, 440,
         3, "No", 0, 0, 0, "", 480,
         "Past their rated life. Replace before next season."),
        ("Canon LP-E6NH batteries x8", "Battery", "Canon",
         "LPE6-BATCH-11", "In use", "Fair", _phg(1), -800, 640, 3,
         "No", 0, 0, 0, "", 680,
         "Two of the eight no longer hold a full day."),
        ("ThinkTank Airport Advantage", "Camera bag", "ThinkTank",
         "TT-AA-55302", "In use", "Good", _phg(1), -1600, 329, 10,
         "No", 0, 0, 0, "", 349, ""),
        ("Samsung T7 4TB (working)", "Backup drive", "Samsung",
         "T7-990214", "In use", "Excellent", _phg(1), -300, 299, 4,
         "No", 0, 0, 0, "", 299, ""),
        ("Samsung T7 4TB (mirror)", "Backup drive", "Samsung",
         "T7-990215", "In use", "Excellent", _phg(1), -300, 299, 4,
         "No", 0, 0, 0, "Samsung T7 4TB (working)", 299,
         "The second copy. A wedding is not backed up until it is "
         "on this one too."),
        ("Synology DS223 NAS 16TB", "Backup drive", "Synology",
         "DS223-440178", "In use", "Excellent", _phg(1), -200, 749,
         6, "Yes", 700, 0, 0, "", 799,
         "Third copy, off the desk. Cheaper than losing one "
         "wedding."),
        ("Mac Studio M2 Max", "Editing computer", "Apple",
         "MS-M2-227741", "In use", "Excellent", _phg(1), -480, 2399,
         5, "Yes", 2000, 0, 0, "", 2499, ""),
        ("BenQ SW271C monitor", "Monitor", "BenQ", "BQ-SW271-88120",
         "In use", "Good", _phg(1), -1020, 1099, 7, "No", 0, 0, 0,
         "", 1149, "Calibrate it monthly or the albums come back "
                   "magenta."),
        ("Adobe Creative Cloud Photography", "Software licence",
         "Adobe", "ADBE-SUB-2026", "In use", "New", _phg(1), -365,
         239, 1, "No", 0, 0, 0, "", 239,
         "Renews annually. Sits in Expense Tracker as a recurring "
         "cost, not here."),
        ("Nikon D750 (old body)", "Camera body", "Nikon",
         "D750-118827", "Retired", "Retired", "", -3100, 1899, 5,
         "No", 0, 486000, 400000, "", 0,
         "Kept for parts and nostalgia. Written off years ago."),
    ]
    rows: Rows = []
    for (item, category, make, serial, status, condition, assigned,
         bought, price, life, insured, value, shutter, limit,
         backup_for, replace, note) in kit:
        rows.append({
            "item": item, "category": category, "make": make,
            "serial": serial, "status": status, "condition": condition,
            "assigned": assigned, "location": "Studio"
            if not assigned else "With the photographer",
            "bought": _day(cfg, bought), "price": price,
            "life_years": life, "insured": insured,
            "insured_value": value,
            "warranty_to": _day(cfg, bought + 730),
            "serviced": _day(cfg, bought + 365)
            if category == "Camera body" else "",
            "shutter": shutter, "shutter_limit": limit,
            "backup_for": backup_for, "replace_cost": replace,
            "notes": note,
        })
    return rows


# ---------------------------------------------------------------------------
# 13. Travel & Mileage
# ---------------------------------------------------------------------------

def travel(cfg: Config) -> Rows:
    base = "Studio, Portland OR"
    plan = [
        # index, purpose, miles, mode, fuel, tolls, parking, accom,
        # other, hours, receipt
        (1, "Wedding day", 62, "Car", 0, 0, 12, 0, 0, 2.5, "Yes"),
        (1, "Venue visit", 62, "Car", 0, 0, 0, 0, 0, 2.5, "No"),
        (2, "Wedding day", 31, "Car", 0, 0, 0, 0, 0, 1.2, "No"),
        (2, "Engagement shoot", 31, "Car", 0, 0, 8, 0, 0, 1.2, "Yes"),
        (3, "Wedding day", 9, "Car", 0, 0, 22, 0, 0, 0.5, "Yes"),
        (4, "Wedding day", 26, "Car", 0, 0, 0, 0, 0, 1.0, "No"),
        (4, "Album delivery", 26, "Car", 0, 0, 6, 0, 0, 1.0, "Yes"),
        (5, "Wedding day", 7, "Car", 0, 0, 30, 0, 0, 0.4, "Yes"),
        (6, "Wedding day", 14, "Car", 0, 0, 0, 0, 0, 0.6, "No"),
        (7, "Wedding day", 19, "Car", 0, 0, 15, 0, 0, 0.8, "Yes"),
        (7, "Rehearsal", 19, "Car", 0, 0, 0, 0, 0, 0.8, "No"),
        (8, "Venue visit", 48, "Car", 0, 0, 0, 0, 0, 1.9, "No"),
        (9, "Venue visit", 97, "Car", 0, 4.50, 0, 0, 0, 3.6, "Yes"),
        (10, "Venue visit", 164, "Car", 0, 0, 10, 0, 0, 5.8, "Yes"),
        (12, "Venue visit", 288, "Car", 0, 18.00, 0, 145, 42,
         9.5, "Yes"),
        (14, "Venue visit", 0, "Flight", 0, 0, 0, 0, 0, 0, "No"),
    ]
    rows: Rows = []
    for (index, purpose, miles, mode, fuel, tolls, parking, accom,
         other, hours, receipt) in plan:
        offset = WEDDINGS[index - 1][0]
        when = offset if purpose == "Wedding day" else offset - 120
        rows.append({
            "date": _day(cfg, when), "booking": _wed(index),
            "purpose": purpose,
            "from_place": base,
            "to_place": f"{WEDDINGS[index - 1][2]}, "
                        f"{WEDDINGS[index - 1][4]}",
            "mode": mode, "one_way": miles,
            "return_trip": "Yes", "scout_trips": 0,
            "fuel": fuel if fuel else "", "tolls": tolls, "parking": parking,
            "accommodation": accom, "other_cost": other,
            "charge_override": 0, "hours": hours, "receipt": receipt,
            "notes": "",
        })

    # the two that teach something
    rows[-2]["notes"] = ("Victoria and back with an overnight. The "
                         "travel fee covers the fuel and nothing "
                         "else - ten hours of my life are free.")
    rows[-1].update({
        "mode": "Flight", "one_way": 0, "return_trip": "Yes",
        "fuel": "", "other_cost": 680, "accommodation": 420,
        "hours": 14, "receipt": "Yes",
        "notes": "Oaxaca. Flights and three nights. The $1,250 "
                 "travel fee does not cover this and I agreed to "
                 "it anyway."})

    rows += [
        {"date": _day(cfg, -45), "booking": "",
         "purpose": "Training or workshop", "from_place": base,
         "to_place": "Seattle WA", "mode": "Train", "one_way": 0,
         "return_trip": "Yes", "scout_trips": 0, "fuel": "",
         "tolls": 0, "parking": 0, "accommodation": 165,
         "other_cost": 128, "charge_override": 0, "hours": 7.5,
         "receipt": "Yes",
         "notes": "Flash workshop. Not chargeable to anybody, still "
                  "the best money spent this year."},
        {"date": _day(cfg, -12), "booking": "",
         "purpose": "Networking", "from_place": base,
         "to_place": "Portland city centre", "mode": "Car",
         "one_way": 6, "return_trip": "Yes", "scout_trips": 0,
         "fuel": "", "tolls": 0, "parking": 9, "accommodation": 0,
         "other_cost": 0, "charge_override": 0, "hours": 2.5,
         "receipt": "Yes",
         "notes": "Venue coordinators' drinks. Two of my last five "
                  "bookings came from that room."},
        {"date": _day(cfg, -3), "booking": "",
         "purpose": "Equipment collection", "from_place": base,
         "to_place": "Pro Photo Supply", "mode": "Car", "one_way": 4,
         "return_trip": "Yes", "scout_trips": 0, "fuel": "",
         "tolls": 0, "parking": 0, "accommodation": 0,
         "other_cost": 0, "charge_override": 0, "hours": 0.8,
         "receipt": "No", "notes": "Dropped the 70-200 in for "
                                   "repair."},
    ]
    return rows


# ---------------------------------------------------------------------------
# 14. Marketing Calendar
# ---------------------------------------------------------------------------

def marketing(cfg: Config) -> Rows:
    plan = [
        # offset, platform, type, title, booking index, status,
        # reach, engagement, saves, clicks, enquiries, spend, hours
        (-395, "Instagram", "Sneak peek", "Nadia & Priya - first "
         "look in the barn", 1, "Published", 4200, 388, 61, 44, 2,
         0, 1.0),
        (-360, "Blog", "Full wedding gallery", "A September barn "
         "wedding at The Old Mill", 1, "Evergreen", 1850, 42, 0,
         118, 3, 0, 3.5),
        (-298, "Instagram", "Carousel", "Cascade Vineyard in "
         "autumn light", 2, "Published", 6100, 540, 94, 72, 1, 0,
         1.2),
        (-280, "Pinterest", "Portfolio update", "Vineyard wedding "
         "inspiration board", 2, "Evergreen", 22400, 310, 1180,
         264, 4, 0, 2.0),
        (-250, "Instagram", "Reel / video", "Sixty seconds of a "
         "vineyard wedding", 2, "Published", 18700, 1420, 206, 88,
         2, 40, 2.5),
        (-186, "Instagram", "Sneak peek", "St Agnes, and the light "
         "through those windows", 3, "Published", 3900, 301, 44, 31,
         0, 0, 0.8),
        (-150, "Blog", "Blog post", "How to plan family groups "
         "without losing an hour", "", "Evergreen", 2400, 61, 0,
         190, 5, 0, 4.0),
        (-120, "Instagram", "Educational post", "Why your "
         "photographer keeps asking about the sunset", "",
         "Published", 5200, 410, 128, 52, 1, 0, 1.0),
        (-96, "Instagram", "Behind the scenes", "What is actually "
         "in the bag", "", "Published", 3100, 266, 38, 19, 0, 0,
         0.6),
        (-88, "Instagram", "Sneak peek", "Willow Creek in high "
         "summer", 4, "Published", 4600, 352, 57, 40, 1, 0, 0.9),
        (-70, "Wedding directory", "Promotion", "Autumn date "
         "availability listing", "", "Archived", 980, 0, 0, 37, 2,
         149, 0.5),
        (-62, "Instagram", "Client testimonial", "What Margit said "
         "about the gallery", 5, "Published", 2800, 240, 31, 26, 1,
         0, 0.5),
        (-48, "Facebook", "Full wedding gallery", "Rosegate Gardens "
         "- a small wedding that was not small at all", 6,
         "Published", 1600, 88, 0, 22, 0, 0, 1.5),
        (-40, "Email newsletter", "Promotion", "Two 2027 Saturdays "
         "left", "", "Published", 420, 96, 0, 58, 3, 0, 1.2),
        (-30, "Instagram", "Carousel", "Five things to do the week "
         "before your wedding", "", "Published", 7400, 610, 212,
         64, 2, 0, 1.5),
        (-21, "TikTok", "Reel / video", "A day in the life of a "
         "wedding photographer", "", "Published", 31200, 2840, 410,
         96, 1, 0, 2.0),
        (-14, "Google Business", "Portfolio update", "Refreshed "
         "the profile gallery", "", "Published", 1240, 18, 0, 71,
         2, 0, 0.5),
        (-7, "Instagram", "Story", "Behind the scenes at the "
         "Haddad wedding", 7, "Published", 2100, 180, 12, 14, 0, 0,
         0.3),
        (-2, "Instagram", "Sneak peek", "Yusra & Kaleem - the "
         "nikah", 7, "Drafted", 0, 0, 0, 0, 0, 0, 0.4),
        (1, "Instagram", "Sneak peek", "Yusra & Kaleem - the "
         "sparkler exit", 7, "Scheduled", 0, 0, 0, 0, 0, 0, 0.4),
        (4, "Pinterest", "Portfolio update", "Barn weddings in "
         "Oregon", "", "Scheduled", 0, 0, 0, 0, 0, 0, 1.0),
        (9, "Blog", "Blog post", "A winter wedding at The Granary",
         7, "Idea", 0, 0, 0, 0, 0, 0, 0),
        (16, "Instagram", "Educational post", "What a wedding "
         "photographer actually does in the six weeks after your "
         "wedding", "", "Idea", 0, 0, 0, 0, 0, 0, 0),
        (23, "Email newsletter", "Promotion", "Engagement shoot "
         "slots for spring", "", "Idea", 0, 0, 0, 0, 0, 0, 0),
        (30, "Wedding fair", "Promotion", "Portland Winter Wedding "
         "Fair stand", "", "Scheduled", 0, 0, 0, 0, 0, 495, 12.0),
        (45, "Instagram", "Client testimonial", "Ask Delphine for "
         "a line about the gallery", 6, "Idea", 0, 0, 0, 0, 0, 0,
         0),
    ]
    rows: Rows = []
    for (offset, platform, ctype, title, index, status, reach,
         engagement, saves, clicks, enquiries, spend, hours) in plan:
        booking = _wed(index) if index else ""
        rows.append({
            "date": _day(cfg, offset), "platform": platform,
            "type": ctype, "title": title,
            "content": "", "booking": booking,
            "permission": "Yes" if booking else "No",
            "status": status,
            "posted_on": _day(cfg, offset)
            if status in ("Published", "Evergreen", "Archived")
            else "",
            "reach": reach, "engagement": engagement, "saves": saves,
            "clicks": clicks, "manual_enquiries": enquiries,
            "spend": spend, "hours": hours, "notes": "",
        })
    rows[3]["notes"] = ("Pinterest is slow and then it is not. This "
                        "one board has outperformed a year of "
                        "stories.")
    rows[10]["notes"] = ("$149 for two enquiries, neither of which "
                         "booked. Do not renew.")
    rows[24]["notes"] = ("$495 and twelve hours. Last year's fair "
                         "paid for itself twice over - check "
                         "Marketing Calendar before committing "
                         "again.")
    return rows


# ---------------------------------------------------------------------------
# 15. Expense Tracker
# ---------------------------------------------------------------------------

def expenses(cfg: Config) -> Rows:
    rows: Rows = []

    # recurring overheads, thirteen months of them
    recurring = [
        ("Adobe", "Software subscriptions", "Creative Cloud "
         "Photography plan", 19.99, "Monthly", "Operating expense"),
        ("Pic-Time", "Software subscriptions", "Gallery hosting",
         29.00, "Monthly", "Operating expense"),
        ("Squarespace", "Website & hosting", "Website and domain",
         23.00, "Monthly", "Operating expense"),
        ("Backblaze", "Memory & storage", "Off-site backup",
         9.00, "Monthly", "Operating expense"),
    ]
    for month in range(13, 0, -1):
        when = -month * 30 + 4
        for supplier, category, description, amount, freq, tax_cat \
                in recurring:
            rows.append({
                "date": _day(cfg, when), "supplier": supplier,
                "category": category, "description": description,
                "booking": "", "amount": amount, "tax_amount": 0,
                "method": "Credit card", "receipt": "Yes",
                "reference": "", "recurring": freq,
                "business_pct": 1.0, "tax_category": tax_cat,
                "notes": ""})

    one_offs = [
        (-420, "Hiscox", "Insurance", "Annual public liability and "
         "kit cover", 612.00, "One off", "Operating expense", "",
         "Yes", "Renews in about three months. Dev's own cover has "
         "already lapsed - that is a separate problem."),
        (-400, "Dev Ashworth", "Second shooters", "Second shooter, "
         "Raman-Okafor wedding", 350.00, "One off", "Cost of sale",
         1, "Yes", ""),
        (-396, "Loxley Colour", "Albums & prints", "20 page album, "
         "Raman-Okafor", 185.00, "One off", "Cost of sale", 1,
         "Yes", ""),
        (-392, "Shell", "Travel & mileage", "Fuel", 58.20, "One off",
         "Operating expense", "", "Yes", ""),
        (-302, "Dev Ashworth", "Second shooters", "Second shooter, "
         "Tanaka-Reed wedding", 350.00, "One off", "Cost of sale",
         2, "Yes", ""),
        (-298, "Tomas Bright", "Editing services", "24 hours "
         "editing, Tanaka-Reed", 672.00, "One off", "Cost of sale",
         2, "Yes", "Twenty-eight dollars an hour against my own "
                   "sixty-five. This is the cheapest line on the "
                   "sheet."),
        (-290, "Loxley Colour", "Albums & prints", "30 page album, "
         "Tanaka-Reed", 265.00, "One off", "Cost of sale", 2, "Yes",
         ""),
        (-250, "Meta", "Marketing & advertising", "Boosted reel",
         40.00, "One off", "Operating expense", "", "Yes", ""),
        (-190, "Joelle Nakamura", "Second shooters", "Second "
         "shooter, Castellanos wedding", 375.00, "One off",
         "Cost of sale", 3, "Yes", ""),
        (-186, "Loxley Colour", "Albums & prints", "30 page album, "
         "Castellanos", 265.00, "One off", "Cost of sale", 3, "Yes",
         ""),
        (-180, "Pro Photo Supply", "Camera equipment", "Canon RF "
         "85mm f1.2L", 2699.00, "One off", "Capital / asset", "",
         "Yes", "Capital, not an expense. It belongs on Equipment "
                "Inventory too - put it in both places."),
        (-120, "Pro Photo Supply", "Memory & storage", "Six "
         "CFexpress cards", 1080.00, "One off", "Capital / asset",
         "", "Yes", ""),
        (-96, "Dev Ashworth", "Second shooters", "Second shooter, "
         "Vance wedding", 350.00, "One off", "Cost of sale", 4,
         "Yes", ""),
        (-92, "Pro Photo Supply", "Equipment rental", "70-200mm "
         "hire while mine was in for service", 95.00, "One off",
         "Cost of sale", 4, "Yes", ""),
        (-70, "Wedding Directory Co", "Marketing & advertising",
         "Autumn listing", 149.00, "One off", "Operating expense",
         "", "Yes", "Two enquiries, no bookings. Not renewing."),
        (-64, "Tomas Bright", "Editing services", "16.5 hours "
         "editing, Lindqvist", 462.00, "One off", "Cost of sale", 5,
         "Yes", ""),
        (-60, "Loxley Colour", "Albums & prints", "20 page album, "
         "Lindqvist", 185.00, "One off", "Cost of sale", 5, "Yes",
         ""),
        (-45, "Amtrak", "Education & training", "Seattle flash "
         "workshop - travel and ticket", 293.00, "One off",
         "Operating expense", "", "Yes", ""),
        (-40, "Canon Service", "Equipment repair", "70-200mm focus "
         "motor", 340.00, "One off", "Operating expense", "", "Yes",
         "Three week turnaround and a wedding in six days."),
        (-32, "The Flower Press", "Client gifts", "Thank-you "
         "bouquets, two", 96.00, "One off", "Operating expense", "",
         "Yes", ""),
        (-29, "Priya Raman", "Assistants", "Assistant, Mbeki "
         "wedding", 80.00, "One off", "Cost of sale", 6, "Yes", ""),
        (-21, "Peak Accounting", "Accounting & legal", "Quarterly "
         "bookkeeping", 240.00, "Quarterly", "Operating expense",
         "", "Yes", ""),
        (-14, "Stripe", "Bank & card fees", "Card processing fees, "
         "last month", 31.12, "Monthly", "Operating expense", "",
         "No", "No receipt - comes off the statement. Fine for the "
               "accountant, not fine for the receipt column."),
        (-8, "Noissue", "Packaging & postage", "USB boxes and "
         "tissue, 25 sets", 148.00, "One off", "Cost of sale", "",
         "Yes", ""),
        (-2, "Dev Ashworth", "Second shooters", "Second shooter, "
         "Haddad wedding", 350.00, "One off", "Cost of sale", 7,
         "Yes", ""),
        (-1, "The Granary at Fir Point", "Meals on shoot", "Supplier "
         "meals, two", 44.00, "One off", "Operating expense", 7,
         "No", "Lost the receipt. Forty-four dollars I cannot "
               "prove."),
        (-1, "Portland Parking", "Travel & mileage", "Venue car "
         "park", 15.00, "One off", "Operating expense", 7, "Yes",
         ""),
        (-310, "Marisa Calloway", "Tax & national insurance",
         "Quarterly estimated tax", 2400.00, "Quarterly",
         "Not deductible", "", "Yes", "Not an expense. It is here "
         "so the bank balance makes sense."),
        (-120, "Marisa Calloway", "Tax & national insurance",
         "Quarterly estimated tax", 2150.00, "Quarterly",
         "Not deductible", "", "Yes", ""),
        (-250, "Studio Collective", "Studio rent", "Desk and "
         "meeting room, six months up front", 1740.00,
         "Twice a year", "Operating expense", "", "Yes", ""),
        (-61, "Studio Collective", "Studio rent", "Desk and "
         "meeting room, six months up front", 1740.00,
         "Twice a year", "Operating expense", "", "Yes", ""),
        (-200, "Marisa Calloway", "Miscellaneous", "Monthly owner "
         "drawing", 2200.00, "Monthly", "Owner drawing", "", "No",
         "Owner drawings are not a business cost. Tagging them "
         "correctly is what keeps the profit figure honest."),
        (-5, "Pro Photo Supply", "Lens purchases", "Deposit on a "
         "replacement body", 500.00, "One off", "Capital / asset",
         "", "Yes", "Body 2 is at 93% of its rated shutter life. "
                    "Equipment Inventory has been saying so for "
                    "months."),
        (-18, "Apple", "Office expenses", "Printer ink and paper",
         62.40, "One off", "Operating expense", "", "No", ""),
        (-9, "City of Portland", "Licences & permits", "Business "
         "licence renewal", 110.00, "Annual", "Operating expense",
         "", "Yes", ""),
    ]
    for (offset, supplier, category, description, amount, freq,
         tax_cat, index, receipt, note) in one_offs:
        rows.append({
            "date": _day(cfg, offset), "supplier": supplier,
            "category": category, "description": description,
            "booking": _wed(index) if index else "",
            "amount": amount, "tax_amount": 0,
            "method": "Credit card" if category in
            ("Software subscriptions", "Website & hosting")
            else "Bank transfer",
            "receipt": receipt, "reference": "",
            "recurring": freq,
            "business_pct": 0.5 if category == "Office expenses"
            else 1.0,
            "tax_category": tax_cat, "notes": note})
    return rows


# ---------------------------------------------------------------------------
# 16. Profit Analysis
# ---------------------------------------------------------------------------

def profit(cfg: Config) -> Rows:
    """One line per wedding. Everything else on that tab is a
    formula - this register is deliberately one column wide."""
    return [{"booking": _wed(index)}
            for index in range(1, len(WEDDINGS) + 1)]


# ---------------------------------------------------------------------------
# 17. Reviews & Referrals
# ---------------------------------------------------------------------------

def reviews(cfg: Config) -> Rows:
    plan = [
        (1, "Email", 0, "Received", "Google", 5,
         "They caught my grandmother laughing",
         "We have one photograph of my grandmother laughing with "
         "both her grandsons and she died in January. Marisa did "
         "not ask us to pose for it. She just saw it.",
         "Yes", "Website homepage, Google profile", "Yes", 2,
         "Yes", ""),
        (2, "In the gallery", 1, "Received", "Google", 5,
         "Worth every penny and then some",
         "We booked the Premium package and spent the whole day "
         "forgetting there was a photographer there. The album "
         "arrived three weeks early.",
         "Yes", "Instagram, Google profile", "Yes", 1, "Yes", ""),
        (3, "Email", 2, "Received", "Wedding directory", 4,
         "Beautiful photographs, slow album",
         "The photographs are everything we hoped for. The album "
         "took longer than we were told, which is the only reason "
         "this is not five stars.",
         "No", "", "Yes", 1, "Yes",
         "Four stars for a reason I control. The album was 26 days "
         "late. Fix the process, not the review."),
        (4, "Email", 2, "Chased", "Google", "", "", "", "No", "",
         "No", 0, "No",
         "Asking for a review while the gallery is three weeks "
         "late is not a good idea. Deliver first, then ask."),
        (5, "", 0, "Not requested", "", "", "", "", "No", "", "No",
         0, "No",
         "Delivered 34 days ago, review never asked for. This is "
         "the easiest thing on the whole dashboard to fix."),
        (6, "", 0, "Not requested", "", "", "", "", "No", "", "No",
         0, "No",
         "Balance unpaid. Ask for the money before asking for the "
         "review."),
        (2, "Text message", 0, "Received", "Facebook", 5,
         "Second time we have used Rowan & Fern",
         "Used Marisa for our engagement shoot and then the "
         "wedding. Same person, same care, both times.",
         "Yes", "Facebook page", "Yes", 0, "Yes",
         "A second review from the same couple on a different "
         "platform. Perfectly normal and worth asking for."),
        (1, "Thank-you card", 0, "Declined", "", "", "", "", "No",
         "", "No", 1, "Yes",
         "Did not want to write a public review and sent two "
         "couples instead. That is a better outcome."),
        (3, "Automatic reminder", 3, "No review left", "Google", "",
         "", "", "No", "", "No", 0, "No",
         "Three automatic reminders and nothing. Stop at two."),
        (5, "In person", 0, "Requested", "Google", "", "", "", "No",
         "", "No", 0, "No",
         "Asked at the album handover. Give it a fortnight before "
         "chasing."),
    ]
    rows: Rows = []
    for (index, how, reminders, status, platform, rating, headline,
         quote, can_use, used_on, responded, referrals, thanked,
         note) in plan:
        offset = WEDDINGS[index - 1][0]
        asked = _day(cfg, offset + 40) if how else ""
        received = _day(cfg, offset + 46) if status == "Received" \
            else ""
        rows.append({
            "booking": _wed(index), "asked_on": asked,
            "how_asked": how, "reminders": reminders,
            "status": status, "received_on": received,
            "platform": platform, "rating": rating,
            "headline": headline, "quote": quote,
            "can_use": can_use, "used_on": used_on,
            "responded": responded, "referrals": referrals,
            "thanked": thanked, "notes": note})
    return rows


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

#: keyed by register *module* name, which is what each register's
#: ``spec()`` passes to :func:`get`.
_BUILDERS: Dict[str, Callable[[Any], List[Dict[str, Any]]]] = {
    "clients": clients,
    "leads": leads,
    "bookings": bookings,
    "packages": packages,
    "staff": staff,
    "contracts": contracts,
    "payments": payments,
    "timeline": timeline,
    "shots": shots,
    "editing": editing,
    "gallery": gallery,
    "equipment": equipment,
    "travel": travel,
    "marketing": marketing,
    "expenses": expenses,
    "profit": profit,
    "reviews": reviews,
}


def get(name: str, cfg) -> List[Dict[str, Any]]:
    """Sample rows for a register, or [] when samples are switched off."""
    if not getattr(cfg, "include_sample_data", True):
        return []
    builder = _BUILDERS.get(name)
    return builder(cfg) if builder else []
