"""A worked example: fourteen months of a two-crew lawn care firm.

Thornhill Grounds Care runs two trucks, eleven people on the books
through the season, forty-odd regular customers and a round that
stretches from tidy suburban front lawns to a retail park and a
church. The year in this file is deliberately not a tidy one, because
a sample company where everything reconciles teaches you nothing
about what the alert columns are for.

In this example you will find: a customer who has not been visited in
four months and is still marked Active; two invoices badly overdue,
one of them at a hundred and four days; a contract whose renewal date
has already gone past; a ride-on mower thirty engine hours beyond its
service interval and a hedge trimmer that has been out of service for
a fortnight; a bag of fertiliser that has run out completely; a
fortnight of completed visits that were never invoiced; a quote sent
eighteen days ago that nobody has chased; a one-off clearance job
that took eleven and a half hours against a four hour estimate and
lost money; a complaint about clippings left on a drive with the
revisit already booked; and a spray licence that expires in five
weeks.

Every row here is checked twice before it ships. The keys must all be
*input* columns on their register - a value written into a formula
column is silently dropped and takes the formula with it - and every
value that feeds a drop-down must exist in that drop-down's list.
``tools/check_landscaping_sample.py`` does both checks, and recomputes
the stock and odometer narratives in plain Python.

Dates are relative to ``cfg.today``, so the example stays current
whenever the workbook is built.
"""

from __future__ import annotations

import datetime as _dt
import random as _random
from typing import Any, Callable, Dict, List, Tuple

from .config import SERVICE_CATALOGUE, Config

Rows = List[Dict[str, Any]]

SEED = 20260401


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _day(cfg: Config, offset: int) -> _dt.date:
    """A date `offset` days from the build date."""
    return cfg.today + _dt.timedelta(days=offset)


def _cus(n: int) -> str:
    return f"CUS-{n:04d}"


def _prp(n: int) -> str:
    return f"PRP-{n:04d}"


def _job(n: int) -> str:
    return f"JOB-{n:05d}"


def _inv(n: int) -> str:
    return f"INV-{n:05d}"


def _con(n: int) -> str:
    return f"CON-{n:04d}"


def _emp(n: int) -> str:
    return f"EMP-{n:03d}"


def _eqp(n: int) -> str:
    return f"EQP-{n:03d}"


def _mat(n: int) -> str:
    return f"MAT-{n:04d}"


def _qte(n: int) -> str:
    return f"QTE-{n:04d}"


def _time(hour: int, minute: int = 0) -> _dt.time:
    return _dt.time(hour, minute)


def _money(value: float) -> float:
    return round(value + 0.0, 2)


def _weekday_on_or_after(start: _dt.date, weekday: int) -> _dt.date:
    """The first `weekday` (Mon=0) on or after `start`."""
    return start + _dt.timedelta(days=(weekday - start.weekday()) % 7)


# ---------------------------------------------------------------------------
# the customers, and the properties they own
# ---------------------------------------------------------------------------

#: name, contact, type, town, lead source, terms, status, rating
CUSTOMERS: List[Tuple[str, str, str, str, str, str, str, int]] = [
    ("Eleanor Whitlock", "Eleanor Whitlock", "Residential - premium",
     "Granton", "Word of mouth", "Net 14", "Active", 5),
    ("Marcus and Jean Hale", "Jean Hale", "Residential", "Granton",
     "Van signage", "Due on completion", "Active", 5),
    ("Fallow Street Dental", "Priya Raman", "Commercial", "Granton",
     "Google search", "Net 30", "Active", 4),
    ("Oakridge HOA", "Dennis Pryor", "HOA / strata", "Oakridge",
     "Property manager", "Net 30", "Active", 4),
    ("The Birches Care Home", "Sandra Okafor", "Commercial", "Granton",
     "Existing customer referral", "Net 30", "Active", 5),
    ("Tom Bellamy", "Tom Bellamy", "Residential", "Ashbourne",
     "Nextdoor", "Due on completion", "Active", 4),
    ("Hartley Retail Park", "Gavin Doyle", "Retail park", "Granton",
     "Google Business profile", "Net 45", "Active", 3),
    ("St Columba's Church", "Rev. Martin Cole", "Church", "Oakridge",
     "Word of mouth", "Net 30", "Active", 5),
    ("Nadia Fairbrother", "Nadia Fairbrother", "Residential",
     "Granton", "Facebook", "Due on completion", "Active", 5),
    ("Brookside Lettings", "Katie Vance", "Property management",
     "Ashbourne", "Property manager", "Net 30", "Active", 3),
    ("Gerald Ashworth", "Gerald Ashworth", "Residential - premium",
     "Oakridge", "Repeat customer", "Net 14", "Active", 5),
    ("Milltown Veterinary", "Dr Owen Shaw", "Commercial", "Ashbourne",
     "Google search", "Net 14", "Active", 4),
    ("Harriet Nkemelu", "Harriet Nkemelu", "Residential", "Granton",
     "Leaflet drop", "Due on completion", "Active", 4),
    ("Wendover Primary School", "Alice Treadwell",
     "School or college", "Granton", "Word of mouth", "Net 30",
     "Active", 4),
    ("Peter and Rose Quill", "Rose Quill", "Residential", "Ashbourne",
     "Yard sign", "Due on completion", "Active", 5),
    ("Carlton Industrial Units", "Ray Meacham", "Commercial",
     "Granton", "Door knock", "Net 45", "Active", 2),
    ("Joan Pemberton", "Joan Pemberton", "Residential", "Oakridge",
     "Word of mouth", "Due on completion", "Occasional", 5),
    ("Dalewood Mews Residents", "Chris Udall", "HOA / strata",
     "Granton", "Existing customer referral", "Net 30", "Active", 4),
    ("Sam Ridgeway", "Sam Ridgeway", "Residential", "Ashbourne",
     "Instagram", "Due on completion", "Active", 4),
    ("Fernhill Guest House", "Moira Tate", "Commercial", "Oakridge",
     "Checkatrade or similar", "Net 14", "Active", 4),
    ("Duncan Pryce", "Duncan Pryce", "Residential", "Granton",
     "Van signage", "Due on completion", "Active", 3),
    ("The Granary Offices", "Yusuf Baig", "Commercial", "Granton",
     "Google search", "Net 30", "Active", 4),
    ("Lily Marchetti", "Lily Marchetti", "Residential", "Ashbourne",
     "Nextdoor", "Due on completion", "Active", 5),
    ("Northfield Allotments", "Eddie Rourke", "Municipal",
     "Oakridge", "Word of mouth", "Net 30", "Seasonal", 4),
    ("Pauline Duggan", "Pauline Duggan", "Residential", "Granton",
     "Leaflet drop", "Due on completion", "Active", 4),
    ("Harbour View Flats", "Nicola Dent", "Property management",
     "Ashbourne", "Property manager", "Net 30", "Active", 3),
    ("Ian Merriweather", "Ian Merriweather", "Residential",
     "Oakridge", "Repeat customer", "Due on completion", "Active", 5),
    ("Castle Hill Nursery", "Bea Lonsdale", "Commercial", "Granton",
     "Existing customer referral", "Net 14", "Active", 4),
    ("Rachel Osei", "Rachel Osei", "Residential", "Granton",
     "Facebook", "Due on completion", "Active", 5),
    ("Bramley Court Flats", "Kev Ashton", "HOA / strata",
     "Ashbourne", "Property manager", "Net 30", "Active", 3),
    ("Martin Slade", "Martin Slade", "Residential", "Oakridge",
     "Google search", "Due on completion", "Dormant", 3),
    ("Westgate Dental Group", "Hanna Lindqvist", "Commercial",
     "Granton", "Word of mouth", "Net 30", "Active", 4),
    ("Colin Ferraby", "Colin Ferraby", "Residential", "Ashbourne",
     "Yard sign", "Due on completion", "Occasional", 4),
    ("Thorpe & Sons Builders", "Danny Thorpe",
     "Construction contract", "Granton", "Word of mouth", "Net 30",
     "Active", 3),
    ("Esme Carrick", "Esme Carrick", "Residential - premium",
     "Oakridge", "Existing customer referral", "Net 14", "Active", 5),
    ("Lavender Lodge", "Trish Monroe", "Commercial", "Granton",
     "Checkatrade or similar", "Net 14", "Active", 5),
    ("Greg Stanmore", "Greg Stanmore", "Residential", "Granton",
     "Door knock", "Due on completion", "Lead", 3),
    ("Riverbank Business Centre", "Lara Finch", "Commercial",
     "Ashbourne", "Google Business profile", "Net 45", "Active", 3),
    ("Maureen Ollerenshaw", "Maureen Ollerenshaw", "Residential",
     "Oakridge", "Word of mouth", "Due on completion", "Active", 5),
    ("Kestrel Park Residents", "Simon Pike", "HOA / strata",
     "Granton", "Property manager", "Net 30", "Active", 4),
    ("Aled Gwynne", "Aled Gwynne", "Residential", "Ashbourne",
     "Instagram", "Due on completion", "Lost", 2),
    ("Benford Self Storage", "Carl Benford", "Commercial", "Granton",
     "Van signage", "Net 30", "Active", 3),
]

STREETS = [
    "Fallow Road", "Mill Lane", "Oakridge Drive", "Hartley Way",
    "Church Walk", "Brook Street", "Carlton Rise", "Dalewood Mews",
    "Fernhill Road", "Granary Yard", "Kestrel Park", "Northfield Lane",
    "Harbour View", "Bramley Court", "Westgate Street", "Lavender Hill",
    "Riverbank Close", "Castle Hill", "Ashbourne Road", "Quarry Lane",
]

#: customer index (1 based), nickname, property type, lawn sq ft,
#: terrain, access, miles, drive minutes, obstacles, status
PROPERTIES: List[Tuple[int, str, str, int, str, str, float, int,
                       int, str]] = [
    (1, "The Old Rectory", "Large grounds", 9400, "Gentle slope",
     "Locked gate - code", 4.2, 14, 18, "Active"),
    (2, "Home", "Front and back lawn", 1850, "Flat", "Side gate",
     2.1, 8, 6, "Active"),
    (3, "Surgery frontage", "Commercial frontage", 1200, "Flat",
     "Open access", 1.4, 6, 3, "Active"),
    (4, "Oakridge - the green", "Communal gardens", 14500, "Flat",
     "Open access", 6.8, 19, 22, "Active"),
    (4, "Oakridge - entrance beds", "Communal gardens", 2600, "Flat",
     "Open access", 6.8, 19, 9, "Active"),
    (5, "The Birches", "Large grounds", 7600, "Gentle slope",
     "Barrier or fob", 3.1, 11, 14, "Active"),
    (6, "Home", "Back lawn only", 900, "Flat", "Side gate", 5.4, 16,
     4, "Active"),
    (7, "Hartley Retail Park", "Car park verges", 11200, "Flat",
     "Restricted hours", 2.8, 10, 26, "Active"),
    (8, "Churchyard", "Large grounds", 8800, "Uneven",
     "Open access", 7.1, 21, 31, "Active"),
    (9, "Home", "Front and back lawn", 2200, "Flat",
     "Customer must be home", 1.9, 7, 7, "Active"),
    (10, "14 Brook Street", "Front and back lawn", 1400, "Flat",
     "Key safe", 5.9, 17, 5, "Active"),
    (10, "27 Quarry Lane", "Front lawn only", 650, "Gentle slope",
     "Open access", 6.2, 18, 2, "Active"),
    (11, "Ashworth House", "Large grounds", 6900, "Terraced",
     "Locked gate - key held", 7.4, 22, 19, "Active"),
    (12, "Practice grounds", "Commercial frontage", 1800, "Flat",
     "Open access", 5.1, 15, 6, "Active"),
    (13, "Home", "Front and back lawn", 1650, "Flat", "Side gate",
     2.4, 9, 8, "Active"),
    (14, "School field", "Sports pitch", 26000, "Flat",
     "Restricted hours", 3.3, 12, 4, "Active"),
    (14, "School frontage", "Commercial frontage", 2400, "Flat",
     "Restricted hours", 3.3, 12, 11, "Active"),
    (15, "Home", "Front and back lawn", 2050, "Gentle slope",
     "Side gate", 6.1, 18, 9, "Active"),
    (16, "Carlton Units 1-6", "Commercial frontage", 4200, "Flat",
     "Open access", 2.2, 9, 13, "Active"),
    (17, "Home", "Front lawn only", 780, "Flat", "Open access", 7.8,
     23, 3, "One-off only"),
    (18, "Dalewood Mews", "Communal gardens", 5600, "Flat",
     "Barrier or fob", 1.7, 7, 17, "Active"),
    (19, "Home", "Back lawn only", 1100, "Obstacle heavy",
     "Dog on site", 5.6, 17, 12, "Active"),
    (20, "Fernhill Guest House", "Large grounds", 5200,
     "Gentle slope", "Open access", 8.2, 24, 15, "Active"),
    (21, "Home", "Front and back lawn", 1500, "Flat", "Side gate",
     2.6, 9, 6, "Active"),
    (22, "The Granary", "Commercial frontage", 2900, "Flat",
     "Restricted hours", 1.2, 6, 8, "Active"),
    (23, "Home", "Front and back lawn", 1750, "Wet or boggy",
     "Side gate", 6.4, 19, 7, "Active"),
    (24, "Northfield plots", "Allotment or plot", 9800, "Uneven",
     "Locked gate - code", 7.6, 22, 28, "Seasonal only"),
    (25, "Home", "Front lawn only", 820, "Flat", "Open access", 2.9,
     10, 3, "Active"),
    (26, "Harbour View Flats", "Communal gardens", 4400, "Flat",
     "Key safe", 6.7, 20, 14, "Active"),
    (27, "Merriweather Cottage", "Front and back lawn", 2600,
     "Heavily shaded", "Side gate", 7.2, 21, 16, "Active"),
    (28, "Nursery yard and verges", "Commercial frontage", 3600,
     "Flat", "Open access", 2.3, 9, 10, "Active"),
    (29, "Home", "Front and back lawn", 1900, "Flat",
     "Locked gate - code", 1.6, 7, 6, "Active"),
    (30, "Bramley Court", "Communal gardens", 3800, "Gentle slope",
     "Barrier or fob", 6.9, 20, 12, "Active"),
    (31, "Home", "Front and back lawn", 1600, "Flat", "Side gate",
     7.9, 23, 7, "On hold"),
    (32, "Westgate frontage", "Commercial frontage", 1500, "Flat",
     "Open access", 1.8, 8, 5, "Active"),
    (33, "Home", "Back lawn only", 1250, "Steep slope", "Side gate",
     6.3, 19, 9, "Active"),
    (34, "Riverside plot 4", "New build plot", 5400, "Uneven",
     "Open access", 3.7, 13, 2, "Active"),
    (35, "Carrick House", "Large grounds", 8200, "Terraced",
     "Locked gate - key held", 7.7, 23, 24, "Active"),
    (36, "Lavender Lodge", "Large grounds", 4900, "Gentle slope",
     "Open access", 2.7, 10, 18, "Active"),
    (38, "Riverbank Centre", "Car park verges", 6800, "Flat",
     "Restricted hours", 5.8, 17, 20, "Active"),
    (39, "Home", "Front and back lawn", 2100, "Flat", "Side gate",
     7.3, 21, 8, "Active"),
    (40, "Kestrel Park green", "Communal gardens", 7200, "Flat",
     "Open access", 2.5, 9, 16, "Active"),
    (40, "Kestrel Park play area", "Communal gardens", 2800, "Flat",
     "Open access", 2.5, 9, 11, "Active"),
    (41, "Home", "Front and back lawn", 1450, "Flat", "Side gate",
     6.6, 20, 6, "Lost"),
    (42, "Benford yard", "Commercial frontage", 2200, "Flat",
     "Barrier or fob", 2.0, 8, 4, "Active"),
    (1, "The Paddock", "Large grounds", 12800, "Uneven",
     "Locked gate - code", 4.2, 14, 9, "Seasonal only"),
    (5, "The Birches - rear garden", "Communal gardens", 3100,
     "Flat", "Barrier or fob", 3.1, 11, 13, "Active"),
    (7, "Hartley - service yard", "Commercial frontage", 1900,
     "Flat", "Restricted hours", 2.8, 10, 5, "Active"),
    (11, "Ashworth - orchard", "Large grounds", 5800, "Uneven",
     "Locked gate - key held", 7.4, 22, 34, "Seasonal only"),
    (13, "Mother's house", "Front lawn only", 700, "Flat",
     "Open access", 2.8, 10, 2, "Active"),
    (18, "Dalewood - rear path", "Communal gardens", 1600, "Flat",
     "Barrier or fob", 1.7, 7, 6, "Active"),
    (22, "Granary - roof terrace", "Roof terrace", 400, "Flat",
     "Customer must be home", 1.2, 6, 8, "Active"),
    (28, "Nursery - display beds", "Communal gardens", 1800, "Flat",
     "Open access", 2.3, 9, 14, "Active"),
    (34, "Riverside plot 7", "New build plot", 4800, "Uneven",
     "Open access", 3.7, 13, 1, "Active"),
    (36, "Lavender Lodge - car park", "Car park verges", 2400,
     "Flat", "Open access", 2.7, 10, 7, "Active"),
    (40, "Kestrel Park verges", "Car park verges", 3300, "Flat",
     "Open access", 2.5, 9, 9, "Active"),
    (4, "Oakridge - play field", "Sports pitch", 18500, "Flat",
     "Open access", 6.8, 19, 3, "Active"),
    (14, "School beds and borders", "Communal gardens", 1200,
     "Flat", "Restricted hours", 3.3, 12, 22, "Active"),
]

#: the crew, in ID order
CREW: List[Tuple[str, str, str, str, str, float, float]] = [
    ("Marcus Thornhill", "Owner / operator", "Crew A", "Owner",
     "Active", 0.00, 0.00),
    ("Dermot Hayes", "Crew leader", "Crew A", "Full time", "Active",
     24.00, 33.60),
    ("Kyle Brennan", "Groundsperson", "Crew A", "Full time",
     "Active", 18.50, 25.90),
    ("Sofia Rinaldi", "Crew leader", "Crew B", "Full time", "Active",
     23.50, 32.90),
    ("Owen Mbeki", "Machine operator", "Crew B", "Full time",
     "Active", 20.00, 28.00),
    ("Jade Falconer", "Horticulturist", "Crew B", "Part time",
     "Active", 21.00, 29.40),
    ("Liam Teague", "Spray technician", "Crew A", "Full time",
     "Active", 22.00, 30.80),
    ("Nina Prosser", "Apprentice", "Crew B", "Full time", "Active",
     13.50, 18.90),
    ("Rob Cartwright", "Groundsperson", "Solo", "Seasonal",
     "Seasonal layoff", 18.00, 25.20),
    ("Priya Nandra", "Office / admin", "Unassigned", "Part time",
     "Active", 19.00, 26.60),
    ("Charlie Oyelaran", "Seasonal casual", "Crew A", "Casual",
     "Left", 16.00, 22.40),
]

#: equipment: name, category, make, model, cost, life, status,
#: condition, crew, engine hours now, hours since service
EQUIPMENT: List[Tuple[str, str, str, str, float, int, str, str, str,
                      float, float]] = [
    ("Ride-on 48in", "Ride-on mower", "Hustler", "Raptor XD 48",
     6400.00, 7, "Needs service", "Good", "Crew A", 612.0, 130.0),
    ("Ride-on 54in", "Ride-on mower", "Toro", "TimeCutter 54",
     7200.00, 7, "In service", "Good", "Crew B", 438.0, 42.0),
    ("Walk-behind 36in", "Walk-behind mower", "Exmark",
     "Turf Tracer", 4100.00, 8, "In service", "Fair", "Crew A",
     910.0, 61.0),
    ("Push mower - small lawns", "Push mower", "Honda", "HRX217",
     720.00, 6, "In service", "Good", "Crew B", 260.0, 18.0),
    ("Trimmer 1", "String trimmer", "Stihl", "FS 91 R", 380.00, 5,
     "In service", "Good", "Crew A", 540.0, 22.0),
    ("Trimmer 2", "String trimmer", "Stihl", "FS 91 R", 380.00, 5,
     "In service", "Worn", "Crew B", 705.0, 51.0),
    ("Trimmer 3 - spare", "String trimmer", "Echo", "SRM-2620",
     340.00, 5, "Spare", "Fair", "Unassigned", 190.0, 14.0),
    ("Hedge trimmer - long reach", "Hedge trimmer", "Stihl",
     "HL 94 K", 620.00, 6, "Out of service", "Broken", "Crew B",
     295.0, 73.0),
    ("Hedge trimmer - handheld", "Hedge trimmer", "Stihl",
     "HS 82 R", 450.00, 6, "In service", "Good", "Crew A", 210.0,
     31.0),
    ("Blower - backpack 1", "Leaf blower", "Stihl", "BR 600",
     520.00, 6, "In service", "Good", "Crew A", 480.0, 27.0),
    ("Blower - backpack 2", "Leaf blower", "Stihl", "BR 600",
     520.00, 6, "In service", "Fair", "Crew B", 505.0, 44.0),
    ("Blower - handheld", "Leaf blower", "Echo", "PB-2520", 180.00,
     5, "In service", "Fair", "Solo", 165.0, 12.0),
    ("Chainsaw 16in", "Chainsaw", "Husqvarna", "445", 420.00, 7,
     "In service", "Good", "Crew A", 88.0, 9.0),
    ("Chainsaw - pole saw", "Chainsaw", "Stihl", "HT 103", 680.00,
     7, "In service", "Good", "Crew B", 62.0, 6.0),
    ("Edger", "Edger", "Echo", "PE-2620", 330.00, 6, "In service",
     "Good", "Crew A", 140.0, 11.0),
    ("Aerator - tow behind", "Aerator", "Agri-Fab", "45-0299",
     450.00, 10, "In service", "Fair", "Unassigned", 95.0, 20.0),
    ("Scarifier", "Scarifier", "Billy Goat", "PR550", 2600.00, 8,
     "In service", "Good", "Unassigned", 120.0, 16.0),
    ("Sprayer - backpack", "Sprayer", "Solo", "425", 140.00, 5,
     "In service", "Good", "Crew A", 0.0, 0.0),
    ("Sprayer - tow tank", "Sprayer", "Fimco", "ATV 25", 390.00, 8,
     "In service", "Fair", "Crew A", 0.0, 0.0),
    ("Pressure washer", "Pressure washer", "Karcher", "HD 5/11",
     780.00, 7, "In repair", "Needs attention", "Unassigned", 210.0,
     38.0),
    ("Spreader - walk behind", "Spreader", "Lesco", "80 lb",
     520.00, 10, "In service", "Good", "Crew A", 0.0, 0.0),
    ("Trailer - 12ft", "Trailer", "Ifor Williams", "GD105",
     3200.00, 15, "In service", "Good", "Crew A", 0.0, 0.0),
    ("Trailer - tipping", "Trailer", "Ifor Williams", "TT2012",
     4900.00, 15, "In service", "Good", "Crew B", 0.0, 0.0),
    ("Hand tool set - Crew A", "Hand tools", "Mixed", "-", 680.00,
     5, "In service", "Fair", "Crew A", 0.0, 0.0),
    ("Hand tool set - Crew B", "Hand tools", "Mixed", "-", 680.00,
     5, "In service", "Worn", "Crew B", 0.0, 0.0),
    ("PPE set and signage", "Safety equipment", "Mixed", "-",
     940.00, 4, "In service", "Good", "Unassigned", 0.0, 0.0),
]

#: materials: name, category, unit, supplier, cost, charge, opening,
#: reorder at, reorder qty, status, hazardous
MATERIALS: List[Tuple[str, str, str, str, float, float, float,
                      float, float, str, str]] = [
    ("Spring feed 20-5-10", "Fertiliser", "Bag",
     "Granton Turf Supplies", 28.50, 42.00, 40, 10, 30, "Active",
     "No"),
    ("Autumn feed 6-5-18", "Fertiliser", "Bag",
     "Granton Turf Supplies", 31.00, 46.00, 24, 8, 24, "Active",
     "No"),
    ("Summer feed 24-0-8", "Fertiliser", "Bag",
     "Granton Turf Supplies", 29.50, 44.00, 18, 8, 24, "Seasonal",
     "No"),
    ("Selective weed killer", "Weed control", "Litre",
     "AgriDirect", 34.00, 52.00, 12, 4, 10, "Active", "Yes"),
    ("Pre-emergent granular", "Weed control", "Bag", "AgriDirect",
     38.00, 58.00, 9, 4, 12, "Seasonal", "Yes"),
    ("Moss control - iron sulphate", "Weed control", "Kilogram",
     "AgriDirect", 6.80, 11.00, 25, 10, 25, "Active", "Yes"),
    ("Grass seed - hard wearing", "Grass seed", "Kilogram",
     "Granton Turf Supplies", 9.40, 15.50, 45, 15, 40, "Active",
     "No"),
    ("Grass seed - shade mix", "Grass seed", "Kilogram",
     "Granton Turf Supplies", 11.20, 18.00, 14, 6, 20, "Active",
     "No"),
    ("Turf - standard", "Turf", "Square metre", "Rolling Acres Turf",
     4.20, 7.50, 0, 0, 100, "Special order", "No"),
    ("Bark mulch", "Mulch", "Cubic yard", "Ashbourne Aggregates",
     34.00, 58.00, 6, 3, 12, "Active", "No"),
    ("Composted mulch", "Mulch", "Cubic yard",
     "Ashbourne Aggregates", 29.00, 52.00, 4, 3, 12, "Active", "No"),
    ("Topsoil - screened", "Topsoil", "Cubic yard",
     "Ashbourne Aggregates", 26.00, 46.00, 3, 2, 10, "Active", "No"),
    ("Compost - peat free", "Compost", "Bag", "Castle Hill Nursery",
     6.50, 11.00, 30, 12, 40, "Active", "No"),
    ("Sharp sand", "Sand", "Cubic yard", "Ashbourne Aggregates",
     31.00, 54.00, 2, 2, 8, "Active", "No"),
    ("Decorative gravel", "Gravel", "Cubic yard",
     "Ashbourne Aggregates", 42.00, 72.00, 1, 1, 6, "Active", "No"),
    ("Bedding plants - mixed tray", "Bedding", "Tray",
     "Castle Hill Nursery", 7.80, 14.00, 0, 6, 24, "Seasonal", "No"),
    ("Shrubs - 3 litre", "Plants", "Each", "Castle Hill Nursery",
     9.60, 18.00, 8, 5, 20, "Active", "No"),
    ("Lawn edging - steel", "Edging", "Roll",
     "Granton Turf Supplies", 22.00, 38.00, 3, 2, 8, "Active", "No"),
    ("Weed membrane", "Membrane", "Roll", "Granton Turf Supplies",
     18.50, 32.00, 5, 2, 8, "Active", "No"),
    ("Two stroke oil", "Oil and lubricant", "Bottle",
     "Meadow Lane Motors", 9.20, 0.00, 14, 6, 18, "Active", "No"),
    ("Chain oil", "Oil and lubricant", "Litre",
     "Meadow Lane Motors", 7.40, 0.00, 10, 4, 12, "Active", "No"),
    ("Trimmer line 2.4mm", "Consumables", "Roll",
     "Meadow Lane Motors", 24.00, 0.00, 7, 3, 10, "Active", "No"),
    ("Mower blades - 48in set", "Consumables", "Each",
     "Meadow Lane Motors", 48.00, 0.00, 4, 2, 6, "Active", "No"),
    ("Green waste sacks", "Consumables", "Each",
     "Granton Turf Supplies", 1.10, 0.00, 180, 60, 200, "Active",
     "No"),
    ("Marker paint", "Consumables", "Bottle", "AgriDirect", 8.40,
     0.00, 6, 3, 12, "Active", "No"),
    ("Ice melt - rock salt", "Consumables", "Sack",
     "Ashbourne Aggregates", 7.60, 13.00, 20, 10, 40, "Seasonal",
     "No"),
]


# ---------------------------------------------------------------------------
# the registers that are simply lists
# ---------------------------------------------------------------------------

def _customers(cfg: Config) -> Rows:
    rows: Rows = []
    rng = _random.Random(SEED + 1)
    for index, (name, contact, kind, town, source, terms, status,
                rating) in enumerate(CUSTOMERS, start=1):
        residential = kind.startswith("Residential")
        first = _day(cfg, -rng.randint(120, 1500))
        notes = ""
        if status == "Dormant":
            notes = ("Stopped the round in the summer - said they "
                     "would be in touch and never were. Worth a "
                     "call before spring.")
        elif status == "Lead":
            notes = ("Quoted for the first cut, waiting to hear. "
                     "Chase it.")
        elif status == "Lost":
            notes = ("Went to a cheaper outfit in the spring. Left "
                     "owing nothing, so no hard feelings.")
        elif kind == "Retail park":
            notes = ("Pays late every single time. Build it into "
                     "the price, not into your temper.")
        rows.append({
            "name": name,
            "contact": contact,
            "phone": f"555 0{100 + index:03d} {rng.randint(10, 99)}",
            "email": (contact.split()[-1].lower().replace("'", "")
                      + "@example.com"),
            "address": f"{rng.randint(1, 180)} "
                       f"{STREETS[index % len(STREETS)]}",
            "town": town,
            "postcode": f"440{rng.randint(10, 89)}",
            "type": kind,
            "source": source,
            "first_job": first,
            "terms": terms,
            "method": ("Direct debit" if residential and index % 3 == 0
                       else "Bank transfer" if not residential
                       else rng.choice(["Bank transfer", "Card",
                                        "Standing order"])),
            "status": status,
            "rating": rating,
            "po_required": "Yes" if kind in (
                "Commercial", "Municipal", "School or college",
                "Retail park", "Property management") else "No",
            "tax_exempt": "Yes" if kind == "Church" else "No",
            "marketing_ok": "No" if index % 7 == 0 else "Yes",
            "notes": notes,
        })
    return rows


def _properties(cfg: Config) -> Rows:
    rows: Rows = []
    rng = _random.Random(SEED + 2)
    for index, (customer, nickname, kind, lawn, terrain, access,
                miles, drive, obstacles, status) in enumerate(
                    PROPERTIES, start=1):
        dog = "Yes" if access == "Dog on site" or index % 9 == 0 \
            else "No"
        gate = ""
        if access in ("Locked gate - code", "Barrier or fob"):
            gate = f"{rng.randint(1000, 9989)}"
        elif access == "Key safe":
            gate = f"Key safe {rng.randint(1000, 9989)}"
        rows.append({
            "customer": _cus(customer),
            "nickname": nickname,
            "address": f"{rng.randint(1, 140)} "
                       f"{STREETS[index % len(STREETS)]}",
            "town": CUSTOMERS[customer - 1][3],
            "postcode": f"440{rng.randint(10, 89)}",
            "type": kind,
            "lawn_area": lawn,
            "beds_area": int(lawn * rng.uniform(0.04, 0.22)),
            "hedge_length": rng.choice([0, 0, 40, 65, 90, 130, 180]),
            "terrain": terrain,
            "access": access,
            "gate_code": gate,
            "dog": dog,
            "pets_note": ("Large dog, usually out in the back "
                          "garden. Ring before opening the gate."
                          if dog == "Yes" else
                          "Irrigation heads along the front edge - "
                          "keep the ride-on off the verge."
                          if index % 11 == 0 else ""),
            "parking": rng.choice(["On the drive", "On the road",
                                   "Service yard", "Visitor bay",
                                   "Verge - no restrictions"]),
            "water": "Yes" if index % 3 else "No",
            "power": "Yes" if index % 4 else "No",
            "disposal": rng.choice(["Take away", "Take away",
                                    "Leave bagged", "Compost heap",
                                    "Mulch in place"]),
            "miles": miles,
            "drive_minutes": drive,
            "obstacles": obstacles,
            "status": status,
            "start_date": _day(cfg, -rng.randint(90, 1400)),
            "photo_before": "",
            "photo_after": "",
            "map_link": "",
            "notes": ("Verges are council land up to the kerb - do "
                      "not cut past the marker."
                      if kind == "Car park verges" else
                      "Septic lid in the back lawn, two paces from "
                      "the shed. Mark it in spring."
                      if index % 13 == 0 else ""),
        })
    return rows


def _services(cfg: Config) -> Rows:
    """The catalogue, priced for a two-person crew."""
    rows: Rows = []
    labour = cfg.labour_rate + cfg.overhead_per_hour
    for name, category, unit, minutes, blurb in SERVICE_CATALOGUE:
        hours = minutes / 60.0
        crew_size = 2 if minutes >= 45 else 1
        materials = {
            "Fertiliser application": 14.00,
            "Weed control - selective": 11.50,
            "Overseeding": 22.00,
            "Turf laying": 48.00,
            "Mulch install": 62.00,
            "Planting - bedding": 34.00,
            "Topdressing": 18.00,
        }.get(name, 0.0)
        rate = round(
            (hours * labour * crew_size + materials * 1.35)
            / max(0.05, 1 - cfg.target_margin), 2)
        rate = round(max(rate, cfg.minimum_visit * 0.6), 2)
        season = "All year"
        lower = name.lower()
        if "leaf" in lower or "autumn" in lower:
            season = "Autumn / Fall"
        elif "spring" in lower or "aeration" in lower:
            season = "Spring"
        elif "snow" in lower or "ice" in lower or "prun" in lower:
            season = "Winter"
        elif "irrigation" in lower or "hedge" in lower:
            season = "Summer"
        frequency = "Weekly" if category == "Mowing" else (
            "Twice a year" if category in ("Pruning", "Renovation")
            else "One-off" if category == "Install" else "Monthly")
        licence = "Yes" if category == "Treatment" else "No"
        rows.append({
            "name": name,
            "category": category,
            "description": blurb,
            "unit": unit,
            "rate": rate,
            "minutes": minutes,
            "crew_size": crew_size,
            "materials_cost": materials,
            "equipment": {
                "Mowing": "Walk-behind mower",
                "Pruning": "Hedge trimmer",
                "Treatment": "Sprayer",
                "Renovation": "Scarifier",
                "Install": "Hand tools",
                "Seasonal": "Leaf blower",
                "Maintenance": "Hand tools",
            }.get(category, "Hand tools"),
            "min_charge": cfg.minimum_visit,
            "season": season,
            "frequency": frequency,
            "taxable": "Yes",
            "skill": ("Spray technician" if category == "Treatment"
                      else "Arborist" if "tree" in lower
                      else "Horticulturist" if category == "Install"
                      else "Groundsperson"),
            "licence_needed": licence,
            "status": "Seasonal" if season != "All year" else "Active",
            "notes": "",
        })
    return rows


def _crew(cfg: Config) -> Rows:
    rows: Rows = []
    for index, (name, role, crew, employment, status, pay,
                cost) in enumerate(CREW, start=1):
        spray = "Yes" if role in ("Spray technician",
                                  "Owner / operator") else "No"
        licence = ""
        licence_expiry = None
        if spray == "Yes":
            licence = "PA1 + PA6 spray certificate"
            # the licence that is about to catch somebody out
            licence_expiry = _day(cfg, 35 if role == "Spray technician"
                                  else 400)
        elif role in ("Driver", "Crew leader", "Machine operator"):
            licence = "Full driving licence - trailer entitlement"
            licence_expiry = _day(cfg, 300 + index * 40)
        rows.append({
            "name": name,
            "role": role,
            "crew": crew,
            "employment": employment,
            "phone": f"555 02{index:02d} {40 + index}",
            "email": name.split()[0].lower() + "@thornhillgrounds.example",
            "emergency": f"{name.split()[-1]} family - 555 03{index:02d}",
            "start_date": _day(cfg, -(300 + index * 170)),
            "end_date": _day(cfg, -45) if status == "Left" else None,
            "status": status,
            "pay_rate": pay,
            "cost_rate": cost,
            "overtime_rate": cfg.overtime_multiplier,
            "licence": licence,
            "licence_expiry": licence_expiry,
            "insurance_expiry": _day(cfg, 120 + index * 7),
            "can_spray": spray,
            "can_drive": "Yes" if role not in ("Apprentice",
                                               "Office / admin")
            else "No",
            "equipment_ok": ("Ride-on, walk-behind, trimmer, blower, "
                             "hedge trimmer"
                             if role in ("Crew leader",
                                         "Machine operator",
                                         "Owner / operator")
                             else "Walk-behind, trimmer, blower"),
            "notes": ("Spray certificate expires in five weeks - "
                      "book the refresher now or the treatment work "
                      "stops." if role == "Spray technician" else
                      "Back for the spring - keep the number."
                      if status == "Seasonal layoff" else ""),
        })
    return rows


def _equipment(cfg: Config) -> Rows:
    rows: Rows = []
    rng = _random.Random(SEED + 3)
    for index, (name, category, make, model, price, life, status,
                condition, crew, hours_now,
                since_service) in enumerate(EQUIPMENT, start=1):
        bought = _day(cfg, -rng.randint(200, 2100))
        last_service_days = {
            "Needs service": 190,
            "Out of service": 240,
            "In repair": 150,
        }.get(status, rng.randint(20, 160))
        rows.append({
            "name": name,
            "category": category,
            "make": make,
            "model": model,
            "serial": f"{make[:3].upper()}-{rng.randint(10000, 99999)}",
            "purchase_date": bought,
            "purchase_price": price,
            "life_years": life,
            "warranty_end": bought + _dt.timedelta(days=365 * 2),
            "status": status,
            "condition": condition,
            "assigned": crew,
            "location": "Fallow Yard" if category != "Trailer"
                        else "Fallow Yard - back row",
            "hours_now": hours_now,
            "last_service": _day(cfg, -last_service_days),
            "last_service_hours": round(max(0.0,
                                            hours_now - since_service), 1),
            "service_hours": 100 if hours_now else 0,
            "service_months": 12,
            "replace_flag": "Yes" if condition in ("Worn", "Broken")
                            else "No",
            "insured": "Yes" if price >= 400 else "No",
            "notes": ("Thirty hours past its service interval. Book "
                      "it in before it books itself in."
                      if status == "Needs service" else
                      "Gearbox gone. Quote to repair is more than "
                      "half a new one - decide before the hedges "
                      "need doing." if status == "Out of service"
                      else ""),
        })
    return rows


def _materials(cfg: Config) -> Rows:
    rows: Rows = []
    for index, (name, category, unit, supplier, cost, charge,
                opening, reorder_at, reorder_qty, status,
                hazardous) in enumerate(MATERIALS, start=1):
        rows.append({
            "name": name,
            "category": category,
            "unit": unit,
            "supplier": supplier,
            "supplier_code": f"{supplier.split()[0][:3].upper()}"
                             f"-{index:03d}",
            "cost_unit": cost,
            "charge_unit": charge,
            "opening": opening,
            "reorder_at": reorder_at,
            "reorder_qty": reorder_qty,
            "location": "Yard store" if not hazardous == "Yes"
                        else "Locked chemical cabinet",
            "status": status,
            "hazardous": hazardous,
            "expiry": _day(cfg, 300 + index * 9)
                      if category in ("Fertiliser", "Weed control",
                                      "Pesticide", "Grass seed")
                      else None,
            "notes": ("Kept under lock and key, and only the two "
                      "certificated sprayers touch it."
                      if hazardous == "Yes" else ""),
        })
    return rows


# ---------------------------------------------------------------------------
# the world - contracts, jobs, invoices and everything that hangs off them
#
# These registers have to agree with each other, so they are built once,
# together, and then handed out register by register.
# ---------------------------------------------------------------------------

#: contract: property index (1 based), service, frequency, price,
#: weekday, status
CONTRACT_PLAN: List[Tuple[int, str, str, float, int, str]] = [
    (1, "Lawn mowing - large grounds", "Fortnightly", 128.00, 0,
     "Active"),
    (2, "Lawn mowing - standard", "Weekly", 42.00, 0, "Active"),
    (3, "Lawn mowing - standard", "Fortnightly", 38.00, 1, "Active"),
    (4, "Lawn mowing - large grounds", "Weekly", 215.00, 1, "Active"),
    (6, "Lawn mowing - large grounds", "Weekly", 165.00, 1, "Active"),
    (7, "Lawn mowing - standard", "Fortnightly", 34.00, 2, "Active"),
    (8, "Lawn mowing - large grounds", "Weekly", 180.00, 2, "Active"),
    (9, "Lawn mowing - large grounds", "Fortnightly", 142.00, 2,
     "Active"),
    (10, "Lawn mowing - standard", "Weekly", 46.00, 3, "Active"),
    (11, "Lawn mowing - standard", "Fortnightly", 36.00, 3, "Active"),
    (13, "Lawn mowing - large grounds", "Fortnightly", 118.00, 3,
     "Due renewal"),
    (14, "Lawn mowing - standard", "Fortnightly", 40.00, 4, "Active"),
    (15, "Lawn mowing - standard", "Weekly", 44.00, 4, "Active"),
    (16, "Lawn mowing - large grounds", "Weekly", 260.00, 4,
     "Active"),
    (18, "Lawn mowing - standard", "Weekly", 48.00, 0, "Active"),
    (19, "Lawn mowing - large grounds", "Fortnightly", 95.00, 0,
     "Active"),
    (21, "Lawn mowing - large grounds", "Weekly", 110.00, 1,
     "Active"),
    (22, "Lawn mowing - standard", "Fortnightly", 39.00, 1, "Active"),
    (23, "Lawn mowing - large grounds", "Fortnightly", 86.00, 2,
     "Active"),
    (25, "Lawn mowing - standard", "Fortnightly", 37.00, 2, "Active"),
    (26, "Lawn mowing - standard", "Weekly", 52.00, 3, "Active"),
    (27, "Lawn mowing - large grounds", "Fortnightly", 92.00, 3,
     "Active"),
    (29, "Lawn mowing - standard", "Weekly", 54.00, 4, "Active"),
    (30, "Lawn mowing - large grounds", "Fortnightly", 88.00, 4,
     "Active"),
    (32, "Lawn mowing - standard", "Fortnightly", 41.00, 0, "Active"),
    (33, "Lawn mowing - standard", "Weekly", 43.00, 0, "Active"),
    (35, "Lawn mowing - large grounds", "Fortnightly", 150.00, 1,
     "Active"),
    (36, "Lawn mowing - large grounds", "Weekly", 125.00, 1,
     "Active"),
    (38, "Lawn mowing - large grounds", "Fortnightly", 132.00, 2,
     "Active"),
    (39, "Lawn mowing - standard", "Weekly", 45.00, 2, "Active"),
    (40, "Lawn mowing - large grounds", "Weekly", 148.00, 3,
     "Active"),
    (42, "Lawn mowing - standard", "Fortnightly", 56.00, 3, "Active"),
    (47, "Lawn mowing - large grounds", "Fortnightly", 72.00, 4,
     "Active"),
    (48, "Lawn mowing - standard", "Fortnightly", 58.00, 4, "Active"),
    (53, "Hedge trimming", "Twice a year", 240.00, 0,
     "Seasonal break"),
    (55, "Lawn mowing - large grounds", "Weekly", 138.00, 0,
     "Active"),
    (57, "Lawn mowing - large grounds", "Fortnightly", 175.00, 1,
     "Paused"),
    (58, "Blow down and tidy", "Monthly", 95.00, 2, "Active"),
]

#: extra, non contract work that shows up through the year
ONE_OFF_SERVICES = [
    ("Hedge trimming", 1.0), ("Leaf clearance", 1.0),
    ("Fall cleanup", 1.0), ("Mulch install", 1.0),
    ("Aeration", 1.0), ("Overseeding", 1.0),
    ("Fertiliser application", 1.0), ("Weed control - selective", 1.0),
    ("Pressure washing", 1.0), ("Gutter clearing", 1.0),
    ("Shrub and bush pruning", 1.0), ("Turf laying", 1.0),
    ("Planting - bedding", 1.0), ("Spring cleanup", 1.0),
]


def _units(unit: str, area: float) -> float:
    """Chargeable units, exactly as the Job sheet works them out."""
    if unit == "Per 1,000 sq ft":
        return max(1.0, area) / 1000.0
    if unit == "Per 100 sq ft":
        return max(1.0, area) / 100.0
    if unit == "Per sq ft":
        return max(1.0, area)
    return 1.0


def _estimate(service: str, prop_index: int) -> float:
    """Catalogue hours for a service at a property."""
    for name, _category, unit, minutes, _blurb in SERVICE_CATALOGUE:
        if name == service:
            area = float(PROPERTIES[prop_index - 1][3])
            return max(0.4, minutes * _units(unit, area) / 60.0)
    raise KeyError(service)


_WORLD_CACHE: Dict[Any, Dict[str, Rows]] = {}


def _build_world(cfg: Config) -> Dict[str, Rows]:
    rng = _random.Random(SEED)
    today = cfg.today

    contracts: Rows = []
    jobs: Rows = []
    quotes: Rows = []
    invoices: Rows = []
    timesheets: Rows = []
    vehicles: Rows = []
    expenses: Rows = []
    feedback: Rows = []
    schedule: Rows = []

    active_crew = [index for index, row in enumerate(CREW, start=1)
                   if row[4] in ("Active", "On holiday", "Off sick")]
    crew_a = [index for index in active_crew
              if CREW[index - 1][2] == "Crew A"]
    crew_b = [index for index in active_crew
              if CREW[index - 1][2] == "Crew B"]

    # ------------------------------------------------- the contracts --
    for number, (prop, service, frequency, price, weekday,
                 status) in enumerate(CONTRACT_PLAN, start=1):
        customer = PROPERTIES[prop - 1][0]
        started = _day(cfg, -rng.randint(200, 1300))
        renewal = (_day(cfg, -12) if status == "Due renewal"
                   else _day(cfg, rng.randint(30, 300)))
        contracts.append({
            "customer": _cus(customer),
            "property": _prp(prop),
            "service": service,
            "frequency": frequency,
            "day_pref": ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday"][weekday],
            "start_date": started,
            "end_date": None,
            "season_only": "Yes" if PROPERTIES[prop - 1][9] ==
                           "Seasonal only" else "No",
            "visit_price": price,
            "billing": CUSTOMERS[customer - 1][5],
            "po_number": (f"PO-{rng.randint(4000, 9999)}"
                          if CUSTOMERS[customer - 1][2] in
                          ("Commercial", "Retail park",
                           "School or college", "Municipal",
                           "Property management") else ""),
            "status": status,
            "renewal_date": renewal,
            "price_review": _day(cfg, -rng.randint(120, 400)),
            "notes": ("Renewal date has already gone past. Agree "
                      "this season's price before the first cut, "
                      "not halfway through it."
                      if status == "Due renewal" else
                      "Paused while the building work is on. They "
                      "will want it back in the spring."
                      if status == "Paused" else ""),
        })

    # ------------------------------------------------------- the jobs --
    # Visits are generated backwards from today so that the newest
    # work - the part a buyer looks at first - is the most detailed.
    horizon_back = 180
    horizon_forward = 12
    for number, (prop, service, frequency, price, weekday,
                 status) in enumerate(CONTRACT_PLAN, start=1):
        if status in ("Paused", "Seasonal break"):
            continue
        gap = {"Weekly": 7, "Fortnightly": 14, "Monthly": 28,
               "Twice a year": 182}[frequency]
        customer = PROPERTIES[prop - 1][0]
        crew = "Crew A" if weekday in (0, 2, 4) else "Crew B"
        first = _weekday_on_or_after(_day(cfg, -horizon_back), weekday)
        day = first
        while day <= _day(cfg, horizon_forward):
            # out of season: the round stops between December and March
            if day.month in (12, 1, 2):
                day += _dt.timedelta(days=gap)
                continue
            ahead = (day - today).days
            if ahead > 0:
                job_status = "Scheduled"
            elif ahead == 0:
                job_status = "Dispatched"
            else:
                job_status = "Completed"
            weather = "Dry"
            hours = None
            if ahead < 0 and rng.random() < 0.045:
                job_status = rng.choice(["Rained off", "Skipped",
                                         "Needs revisit"])
                weather = "Heavy rain" if job_status == "Rained off" \
                    else "Dry"
            est = _estimate(service, prop)
            if job_status == "Completed":
                hours = round(est * rng.uniform(0.82, 1.22), 1)
            jobs.append({
                "date": day,
                "customer": _cus(customer),
                "property": _prp(prop),
                "service": service,
                "crew": crew,
                "status": job_status,
                "priority": "3 - Normal",
                "contract": _con(number),
                "quote": "",
                "start_time": _time(7 + (number % 5), (number % 4) * 15),
                "crew_size": 2,
                "hours_typed": hours,
                "weather": weather,
                "completed_by": (CREW[(crew_a if crew == "Crew A"
                                       else crew_b)[0] - 1][0]
                                 if job_status == "Completed" else ""),
                "checklist_done": "Yes" if job_status == "Completed"
                                  else "No",
                "photo_before": "",
                "photo_after": "",
                "issues": "",
                "notes": "",
                "price_quoted": None,
                "extras": None,
                "invoice": "",
                "_prop": prop,
                "_est": est,
            })
            day += _dt.timedelta(days=gap)

    # one-off work, scattered through the year
    for index in range(70):
        prop = rng.choice([p for p in range(1, len(PROPERTIES) + 1)
                           if PROPERTIES[p - 1][9] in
                           ("Active", "Seasonal only", "One-off only")])
        service, _weight = rng.choice(ONE_OFF_SERVICES)
        day = _day(cfg, -rng.randint(1, horizon_back))
        if day.month in (12, 1, 2) and "Leaf" not in service:
            day += _dt.timedelta(days=90)
        if day > _day(cfg, horizon_forward):
            day = _day(cfg, -rng.randint(1, 60))
        customer = PROPERTIES[prop - 1][0]
        est = _estimate(service, prop)
        ahead = (day - today).days
        job_status = "Completed" if ahead < 0 else "Scheduled"
        hours = round(est * rng.uniform(0.85, 1.3), 1) \
            if job_status == "Completed" else None
        price = round(max(cfg.minimum_visit,
                          est * cfg.charge_rate * rng.uniform(0.9,
                                                              1.15)), 2)
        jobs.append({
            "date": day,
            "customer": _cus(customer),
            "property": _prp(prop),
            "service": service,
            "crew": rng.choice(["Crew A", "Crew B"]),
            "status": job_status,
            "priority": rng.choice(["2 - High", "3 - Normal",
                                    "3 - Normal", "4 - Low"]),
            "contract": "",
            "quote": "",
            "start_time": _time(rng.choice([8, 9, 10, 13]), 0),
            "crew_size": 2,
            "hours_typed": hours,
            "weather": "Dry",
            "completed_by": (CREW[1][0] if job_status == "Completed"
                             else ""),
            "checklist_done": "Yes" if job_status == "Completed"
                              else "No",
            "photo_before": "", "photo_after": "", "issues": "",
            "notes": "",
            "price_quoted": price,
            "extras": None,
            "invoice": "",
            "_prop": prop,
            "_est": est,
        })

    jobs.sort(key=lambda row: (row["date"], row["property"]))
    return {
        "contracts": contracts,
        "jobs": jobs,
        "quotes": quotes,
        "invoices": invoices,
        "timesheets": timesheets,
        "vehicles": vehicles,
        "expenses": expenses,
        "feedback": feedback,
        "schedule": schedule,
        "_rng": rng,
        "_crew_a": crew_a,
        "_crew_b": crew_b,
    }


def _finish_world(world: Dict[str, Any], cfg: Config) -> None:
    """Everything that can only be done once the job IDs are settled."""
    rng: _random.Random = world["_rng"]
    jobs: Rows = world["jobs"]
    today = cfg.today

    # ------------------------------------------- today's round, for the
    # route planner to have something to print
    for offset, (prop, service, crew, hour) in enumerate([
            (2, "Lawn mowing - standard", "Crew A", 8),
            (3, "Lawn mowing - standard", "Crew A", 9),
            (22, "Lawn mowing - standard", "Crew A", 11),
            (29, "Lawn mowing - standard", "Crew A", 13),
            (19, "Leaf clearance", "Crew A", 15),
            (4, "Lawn mowing - large grounds", "Crew B", 8),
            (8, "Leaf clearance", "Crew B", 11),
            (36, "Lawn mowing - large grounds", "Crew B", 14)]):
        customer = PROPERTIES[prop - 1][0]
        est = _estimate(service, prop)
        jobs.append({
            "date": today,
            "customer": _cus(customer),
            "property": _prp(prop),
            "service": service,
            "crew": crew,
            "status": "Dispatched" if hour <= 11 else "Scheduled",
            "priority": "3 - Normal" if offset % 4 else "2 - High",
            "contract": "", "quote": "",
            "start_time": _time(hour, 0),
            "crew_size": 2,
            "hours_typed": None,
            "weather": "Dry",
            "completed_by": "",
            "checklist_done": "No",
            "photo_before": "", "photo_after": "", "issues": "",
            "notes": "On today's round.",
            "price_quoted": None if service.startswith("Lawn mowing")
                            else round(est * cfg.charge_rate, 2),
            "extras": None,
            "invoice": "",
            "_prop": prop,
            "_est": est,
        })

    jobs.sort(key=lambda row: (row["date"], row["start_time"],
                               row["property"]))

    # ----------------------------------------------- the stories ------
    completed = [index for index, row in enumerate(jobs, start=1)
                 if row["status"] == "Completed"]

    # the clearance job that ran away with itself
    for index in reversed(completed):
        if jobs[index - 1]["service"] == "Fall cleanup":
            jobs[index - 1]["hours_typed"] = 11.5
            jobs[index - 1]["issues"] = (
                "Twice the green waste we were shown on the site "
                "visit, and no vehicle access to the back.")
            jobs[index - 1]["notes"] = (
                "Quoted four hours, took eleven and a half. The "
                "estimate was made from a photograph. Walk the site "
                "next time.")
            break

    # a visit that went wrong and was put right
    complaint_job = completed[-18] if len(completed) > 20 else completed[-1]
    jobs[complaint_job - 1]["issues"] = (
        "Clippings left on the drive and the side gate left open.")
    jobs[complaint_job - 1]["checklist_done"] = "No"

    # ------------------------------------------------- the invoices ----
    invoices: Rows = world["invoices"]
    unbilled_from = today - _dt.timedelta(days=12)
    by_customer_month: Dict[Tuple[str, str], List[int]] = {}
    one_offs: List[int] = []
    for index in completed:
        row = jobs[index - 1]
        if row["date"] >= unbilled_from:
            continue                       # deliberately not billed yet
        if row["contract"]:
            key = (row["customer"], row["date"].strftime("%Y-%m"))
            by_customer_month.setdefault(key, []).append(index)
        else:
            one_offs.append(index)

    def _charge(index: int) -> float:
        row = jobs[index - 1]
        if row["price_quoted"]:
            return float(row["price_quoted"])
        contract = row["contract"]
        if contract:
            number = int(contract.split("-")[1])
            return float(CONTRACT_PLAN[number - 1][3])
        return 0.0

    def _add_invoice(customer: str, job_id: str, contract: str,
                     date: _dt.date, subtotal: float, description: str,
                     period: str) -> int:
        number = len(invoices) + 1
        terms = CUSTOMERS[int(customer.split("-")[1]) - 1][5]
        term_days = {"Due on completion": 0, "Net 7": 7, "Net 14": 14,
                     "Net 30": 30, "Net 45": 45, "Net 60": 60,
                     "Monthly in advance": 0,
                     "Monthly in arrears": 30}[terms]
        due = date + _dt.timedelta(days=term_days)
        age = (today - due).days
        paid = subtotal
        paid_date = date + _dt.timedelta(
            days=max(1, term_days - rng.randint(0, 4)))
        status = "Paid"
        reminders = 0
        last_chase = None
        if age < 0:
            paid, paid_date, status = 0.0, None, "Sent"
        elif rng.random() < 0.12:
            paid, paid_date = 0.0, None
            status = "Overdue"
            reminders = 1 if age < 30 else 2
            last_chase = today - _dt.timedelta(days=rng.randint(3, 12))
        invoices.append({
            "invoice_number": f"TGC-{2000 + number}",
            "date": date,
            "customer": customer,
            "job": job_id,
            "contract": contract,
            "description": description,
            "period": period,
            "po_number": "",
            "subtotal": _money(subtotal),
            "discount": None,
            "paid": _money(paid) if paid else None,
            "paid_date": paid_date,
            "method": "Bank transfer" if status != "Paid"
                      else rng.choice(["Bank transfer", "Card",
                                       "Direct debit", "Cheque"]),
            "terms": terms,
            "status": status,
            "sent": "Yes",
            "reminders": reminders or None,
            "last_chase": last_chase,
            "notes": "",
        })
        return number

    for (customer, month), indexes in sorted(
            by_customer_month.items(),
            key=lambda item: (item[0][1], item[0][0])):
        subtotal = sum(_charge(index) for index in indexes)
        if subtotal <= 0:
            continue
        last = max(indexes)
        date = jobs[last - 1]["date"] + _dt.timedelta(days=1)
        if date > today:
            continue
        number = _add_invoice(
            customer, "", jobs[last - 1]["contract"], date, subtotal,
            f"Grounds maintenance - {len(indexes)} visit"
            f"{'s' if len(indexes) > 1 else ''}", month)
        for index in indexes:
            jobs[index - 1]["invoice"] = _inv(number)

    for index in one_offs:
        row = jobs[index - 1]
        subtotal = _charge(index)
        if subtotal <= 0:
            continue
        number = _add_invoice(
            row["customer"], _job(index), "",
            row["date"] + _dt.timedelta(days=1), subtotal,
            row["service"], row["date"].strftime("%Y-%m"))
        jobs[index - 1]["invoice"] = _inv(number)

    # the two that have gone badly late
    owed = [number for number, row in enumerate(invoices, start=1)
            if row["status"] in ("Sent", "Overdue")]
    if len(owed) >= 2:
        worst = invoices[owed[0] - 1]
        worst["date"] = today - _dt.timedelta(days=134)
        worst["terms"] = "Net 30"
        worst["paid"] = None
        worst["paid_date"] = None
        worst["status"] = "Overdue"
        worst["reminders"] = 4
        worst["last_chase"] = today - _dt.timedelta(days=9)
        worst["notes"] = ("Four reminders and two phone calls. "
                          "Decide: letter before action, or write it "
                          "off and stop working for them.")
        second = invoices[owed[1] - 1]
        second["date"] = today - _dt.timedelta(days=98)
        second["terms"] = "Net 30"
        second["paid"] = None
        second["paid_date"] = None
        second["status"] = "Overdue"
        second["reminders"] = 2
        second["last_chase"] = today - _dt.timedelta(days=21)
        second["notes"] = "Says the invoice went to the wrong email."

    # one part paid, because it happens
    part = next((row for row in invoices
                 if row["status"] == "Paid" and row["subtotal"] > 300),
                None)
    if part is not None:
        part["paid"] = _money(part["subtotal"] * 0.5)
        part["status"] = "Part paid"
        part["notes"] = "Paid half on the day, half promised Friday."

    # ------------------------------------------------ the timesheets --
    timesheets: Rows = world["timesheets"]
    crew_a: List[int] = world["_crew_a"]
    crew_b: List[int] = world["_crew_b"]
    recent_from = today - _dt.timedelta(days=42)
    for index in completed:
        row = jobs[index - 1]
        if row["date"] < recent_from:
            continue                  # older work carries typed hours
        hours = row["hours_typed"] or row["_est"]
        team = crew_a if row["crew"] == "Crew A" else crew_b
        start = row["start_time"]
        for person in team[:2]:
            begin = _dt.datetime.combine(row["date"], start)
            end = begin + _dt.timedelta(hours=hours) \
                + _dt.timedelta(minutes=30)
            timesheets.append({
                "date": row["date"],
                "employee": _emp(person),
                "job": _job(index),
                "task": "Leaf clearance"
                        if "Leaf" in row["service"]
                        else "Hedge and shrub work"
                        if "Hedge" in row["service"]
                        else "Clean-up and hauling"
                        if "clearance" in row["service"].lower()
                        else "Mowing",
                "start_time": start,
                "end_time": end.time().replace(second=0,
                                               microsecond=0),
                "break_mins": 30,
                "hours_typed": None,
                "mileage": None,
                "approved": "Yes",
                "notes": "",
            })
        # the hours stop being an estimate once they are written down
        row["hours_typed"] = None

    # Older weeks are recorded the way most firms actually record
    # them - one line per person per week - so that the monthly
    # labour cost is still true even though the detail has gone.
    week = _weekday_on_or_after(today - _dt.timedelta(days=182), 0)
    while week < recent_from:
        end_of_week = week + _dt.timedelta(days=6)
        for crew_name, team in (("Crew A", crew_a), ("Crew B", crew_b)):
            worked = sum(
                (row["hours_typed"] or row["_est"])
                for row in jobs
                if row["crew"] == crew_name
                and row["status"] == "Completed"
                and week <= row["date"] <= end_of_week)
            if worked <= 0:
                continue
            for person in team[:2]:
                hours = round(worked + rng.uniform(2.0, 5.5), 1)
                timesheets.append({
                    "date": week,
                    "employee": _emp(person),
                    "job": "",
                    "task": "Mowing",
                    "start_time": None,
                    "end_time": None,
                    "break_mins": None,
                    "hours_typed": hours,
                    "mileage": round(rng.uniform(60, 190), 1),
                    "approved": "Yes",
                    "notes": "Week total - before we started "
                             "recording hours job by job.",
                })
        week += _dt.timedelta(days=7)

    # the unbillable hours that eat a landscaping week
    day = recent_from
    while day <= today:
        if day.weekday() < 5:
            for person, task, hours in [
                    (crew_a[0], "Driving", 1.2),
                    (crew_b[0], "Loading and unloading", 0.8)]:
                timesheets.append({
                    "date": day,
                    "employee": _emp(person),
                    "job": "",
                    "task": task,
                    "start_time": _time(7, 0),
                    "end_time": _time(8, 0),
                    "break_mins": None,
                    "hours_typed": hours,
                    "mileage": 24.0 if task == "Driving" else None,
                    "approved": "Yes",
                    "notes": "",
                })
        day += _dt.timedelta(days=7)
    for offset, (person, task, hours, note) in enumerate([
            (1, "Quoting and site visits", 3.5,
             "Four site visits, two quotes out of them."),
            (10, "Admin and invoicing", 6.0, "Month end invoicing."),
            (7, "Equipment maintenance", 4.0,
             "Blades, filters and plugs on both ride-ons."),
            (10, "Admin and invoicing", 5.5, "Chasing the old debt."),
            (1, "Training", 7.0, "Spray refresher day."),
            (3, "Yard and workshop", 3.0, "Yard tidy and trailer "
                                          "lights."),
    ]):
        timesheets.append({
            "date": today - _dt.timedelta(days=4 + offset * 6),
            "employee": _emp(person),
            "job": "",
            "task": task,
            "start_time": _time(8, 0),
            "end_time": _time(8 + int(hours), 30),
            "break_mins": 30,
            "hours_typed": hours,
            "mileage": None,
            "approved": "Yes",
            "notes": note,
        })

    # -------------------------------------------------- the schedule --
    schedule: Rows = world["schedule"]
    day = today - _dt.timedelta(days=28)
    while day <= today + _dt.timedelta(days=7):
        if day.weekday() < 5:
            for person in crew_a + crew_b:
                working = "Yes"
                reason = ""
                status = CREW[person - 1][4]
                if status == "On holiday":
                    working, reason = "No", "Holiday"
                elif rng.random() < 0.05:
                    working = "No"
                    reason = rng.choice(["Holiday", "Sick",
                                         "Training", "Rained off"])
                schedule.append({
                    "date": day,
                    "employee": _emp(person),
                    "crew": CREW[person - 1][2],
                    "working": working,
                    "reason": reason,
                    "start_time": _time(7, 30) if working == "Yes"
                                  else None,
                    "end_time": _time(16, 30) if working == "Yes"
                                else None,
                    "break_mins": 30 if working == "Yes" else None,
                    "notes": "",
                })
        day += _dt.timedelta(days=1)

    # -------------------------------------------------- the expenses --
    expenses: Rows = world["expenses"]
    stock: Dict[int, float] = {index: float(row[6])
                               for index, row in enumerate(MATERIALS,
                                                           start=1)}
    purchases: List[Tuple[_dt.date, int, float]] = []
    for index, row in enumerate(MATERIALS, start=1):
        if row[9] == "Discontinued":
            continue
        for buy in range(rng.randint(1, 3)):
            purchases.append((
                today - _dt.timedelta(days=rng.randint(14, 220)),
                index, float(row[8])))
    purchases.sort()
    bought_by_date: Dict[int, List[Tuple[_dt.date, float]]] = {}
    for date, index, quantity in purchases:
        bought_by_date.setdefault(index, []).append((date, quantity))
    for date, index, quantity in purchases:
        material = MATERIALS[index - 1]
        amount = _money(quantity * material[4])
        stock[index] += quantity
        expenses.append({
            "date": date,
            "supplier": material[3],
            "description": f"{material[0]} x {quantity:g}",
            "category": "Materials",
            "amount": amount,
            "tax_amount": None,
            "job": "",
            "material": _mat(index),
            "movement": "Purchase",
            "quantity": quantity,
            "equipment": "",
            "vehicle": "",
            "payment_method": "Account",
            "reference": f"INV{rng.randint(10000, 99999)}",
            "tax_category": "Cost of sale",
            "recurring": "No",
            "billable": "No",
            "receipt_link": "",
            "notes": "",
        })

    # material used on jobs - never more than has been bought
    used_so_far: Dict[int, float] = {}
    usage_services = {
        "Fertiliser application": (1, 2.0),
        "Weed control - selective": (4, 0.6),
        "Overseeding": (7, 3.0),
        "Mulch install": (10, 2.0),
        "Turf laying": (9, 20.0),
        "Planting - bedding": (16, 3.0),
        "Spring cleanup": (24, 6.0),
        "Leaf clearance": (24, 4.0),
        "Fall cleanup": (24, 8.0),
    }
    for index in completed:
        row = jobs[index - 1]
        plan = usage_services.get(row["service"])
        if plan is None:
            continue
        material_index, quantity = plan
        # only stock that had actually been delivered by that date
        available = float(MATERIALS[material_index - 1][6])
        available += sum(
            qty for when, qty in bought_by_date.get(material_index, [])
            if when <= row["date"])
        available -= used_so_far.get(material_index, 0.0)
        if available < quantity:
            continue                       # cannot use what you never bought
        used_so_far[material_index] = \
            used_so_far.get(material_index, 0.0) + quantity
        stock[material_index] -= quantity
        material = MATERIALS[material_index - 1]
        expenses.append({
            "date": row["date"],
            "supplier": material[3],
            "description": f"{material[0]} used at "
                           f"{PROPERTIES[row['_prop'] - 1][1]}",
            "category": "Materials",
            "amount": _money(quantity * material[4]),
            "tax_amount": None,
            "job": _job(index),
            "material": _mat(material_index),
            "movement": "Usage",
            "quantity": quantity,
            "equipment": "",
            "vehicle": "",
            "payment_method": "Account",
            "reference": "",
            "tax_category": "Cost of sale",
            "recurring": "No",
            "billable": "No",
            "receipt_link": "",
            "notes": "",
        })

    # one bag spoiled, because that happens too
    if stock.get(13, 0) >= 4:
        stock[13] -= 4
        expenses.append({
            "date": today - _dt.timedelta(days=26),
            "supplier": MATERIALS[12][3],
            "description": "Compost - split sacks, spoiled in the "
                           "rain",
            "category": "Materials",
            "amount": _money(4 * MATERIALS[12][4]),
            "tax_amount": None,
            "job": "",
            "material": _mat(13),
            "movement": "Wastage",
            "quantity": 4.0,
            "equipment": "", "vehicle": "",
            "payment_method": "Account",
            "reference": "",
            "tax_category": "Cost of sale",
            "recurring": "No", "billable": "No", "receipt_link": "",
            "notes": "Left on the trailer overnight. Cover them.",
        })

    # green waste, overheads and the rest of the running costs
    day = today - _dt.timedelta(days=240)
    while day <= today:
        if day.weekday() == 4:
            expenses.append({
                "date": day,
                "supplier": "Granton Civic Amenity",
                "description": "Green waste - tipping charges",
                "category": "Green waste disposal",
                "amount": _money(rng.uniform(38, 96)),
                "tax_amount": None, "job": "", "material": "",
                "movement": "", "quantity": None, "equipment": "",
                "vehicle": "", "payment_method": "Card",
                "reference": f"TIP{rng.randint(1000, 9999)}",
                "tax_category": "Cost of sale", "recurring": "No",
                "billable": "No", "receipt_link": "", "notes": "",
            })
        if day.day == 1:
            for supplier, description, category, amount, tax in [
                    ("Fallow Yard Lettings", "Yard and store rent",
                     "Yard or storage rent", 480.00,
                     "Operating expense"),
                    ("Hartwell Insurance",
                     "Public liability and tools cover",
                     "Business insurance", 196.00,
                     "Operating expense"),
                    ("Meridian Telecom", "Phones and data", "Phone",
                     74.00, "Operating expense"),
                    ("Groundskeeper Software", "Scheduling software",
                     "Website and software", 39.00,
                     "Operating expense")]:
                expenses.append({
                    "date": day, "supplier": supplier,
                    "description": description, "category": category,
                    "amount": amount, "tax_amount": None, "job": "",
                    "material": "", "movement": "", "quantity": None,
                    "equipment": "", "vehicle": "",
                    "payment_method": "Direct debit",
                    "reference": "", "tax_category": tax,
                    "recurring": "Yes", "billable": "No",
                    "receipt_link": "", "notes": "",
                })
        day += _dt.timedelta(days=1)

    for offset, (supplier, description, category, amount, equipment,
                 tax) in enumerate([
            ("Meadow Lane Motors", "Ride-on 48in - annual service",
             "Equipment repair", 268.00, 1, "Operating expense"),
            ("Meadow Lane Motors",
             "Hedge trimmer - gearbox strip and quote",
             "Equipment repair", 95.00, 8, "Operating expense"),
            ("Granton Hire Centre", "Stump grinder - one day",
             "Equipment hire", 128.00, 0, "Cost of sale"),
            ("Workwear Direct", "Boots, gloves and hi-vis",
             "Workwear and PPE", 243.00, 0, "Operating expense"),
            ("Ohio Pesticide Board", "Spray licence renewal",
             "Licences and certification", 165.00, 0,
             "Operating expense"),
            ("Granton Printers", "Leaflets - spring drop",
             "Advertising", 310.00, 0, "Operating expense"),
            ("Bright & Co Accountants", "Year end accounts",
             "Accounting and legal", 640.00, 0, "Operating expense"),
            ("Meadow Lane Motors", "Blades, belts and filters",
             "Equipment repair", 188.00, 3, "Operating expense"),
    ]):
        expenses.append({
            "date": today - _dt.timedelta(days=16 + offset * 21),
            "supplier": supplier,
            "description": description,
            "category": category,
            "amount": amount,
            "tax_amount": None, "job": "", "material": "",
            "movement": "", "quantity": None,
            "equipment": _eqp(equipment) if equipment else "",
            "vehicle": "", "payment_method": "Card",
            "reference": f"R{rng.randint(10000, 99999)}",
            "tax_category": tax, "recurring": "No", "billable": "No",
            "receipt_link": "", "notes": "",
        })
    expenses.sort(key=lambda entry: entry["date"])

    # -------------------------------------------- the vehicle ledger --
    vehicles: Rows = world["vehicles"]
    odometer = {"Truck 1": 68400, "Truck 2": 41250, "Van": 93100}
    day = today - _dt.timedelta(days=240)
    while day <= today:
        if day.weekday() in (0, 3):
            for name in ("Truck 1", "Truck 2"):
                miles = rng.randint(150, 320)
                odometer[name] += miles
                gallons = round(miles / rng.uniform(11.5, 14.5), 1)
                vehicles.append({
                    "date": day,
                    "vehicle": name,
                    "type": "Fuel",
                    "odometer": odometer[name],
                    "gallons": gallons,
                    "amount": _money(gallons * cfg.fuel_price *
                                     rng.uniform(0.96, 1.06)),
                    "full_tank": "Yes",
                    "driver": CREW[(1 if name == "Truck 1"
                                    else 3)][0],
                    "supplier": rng.choice(["Granton Fuel Stop",
                                            "Highway Services",
                                            "Ashbourne Garage"]),
                    "reference": f"F{rng.randint(10000, 99999)}",
                    "job": "", "notes": "",
                })
        day += _dt.timedelta(days=1)
    for offset, (name, kind, amount, note) in enumerate([
            ("Truck 1", "Service", 420.00, "Annual service and MOT."),
            ("Truck 2", "Tyres", 648.00, "Two rear tyres."),
            ("Van", "Insurance", 1180.00, "Fleet policy renewal."),
            ("Truck 1", "Repair", 236.00, "Trailer lights and wiring."),
            ("Trailer 1", "Service", 95.00, "Bearings and brakes."),
            ("Truck 2", "Road tax / licence", 310.00, ""),
    ]):
        vehicles.append({
            "date": today - _dt.timedelta(days=22 + offset * 27),
            "vehicle": name,
            "type": kind,
            # no odometer on a workshop invoice - the mileage
            # history is the fill-up history, and a stray reading
            # dated in the middle of it only muddies the figures
            "odometer": None,
            "gallons": None,
            "amount": amount,
            "full_tank": "No",
            "driver": CREW[0][0],
            "supplier": "Meadow Lane Motors",
            "reference": f"S{rng.randint(1000, 9999)}",
            "job": "", "notes": note,
        })
    vehicles.sort(key=lambda entry: (entry["date"], entry["vehicle"]))

    # -------------------------------------------------- the feedback --
    feedback: Rows = world["feedback"]
    sources = ["Asked on site", "Email", "Google review",
               "Text message", "Phone call", "Unprompted"]
    for offset in range(54):
        index = completed[-(offset * 3 + 2)] if len(completed) > 170 \
            else completed[-(offset % len(completed)) - 1]
        row = jobs[index - 1]
        good = rng.random() < 0.82
        score = rng.choice([9, 10, 10, 9, 8]) if good \
            else rng.choice([3, 4, 5, 6])
        feedback.append({
            "date": row["date"] + _dt.timedelta(days=1),
            "customer": row["customer"],
            "job": _job(index),
            "property": row["property"],
            "crew": row["crew"],
            "source": rng.choice(sources),
            "type": "Compliment" if good else
                    rng.choice(["Complaint", "Quality issue"]),
            "score": score,
            "comment": rng.choice([
                "Lawn looks the best it has in years.",
                "Always on time and always tidy.",
                "Very happy - thank you.",
                "Nice job on the edges this week.",
            ]) if good else rng.choice([
                "Edges were missed along the path.",
                "Clippings left on the patio.",
                "Crew arrived much later than usual.",
            ]),
            "cause": "Nothing - it went well" if good else
                     rng.choice(["Missed an area",
                                 "Clippings left behind",
                                 "Late arrival", "Rushed the job"]),
            "action": "" if good else "Revisit booked, no charge.",
            "cost": None if good else _money(rng.uniform(25, 70)),
            "status": "Resolved" if good else
                      rng.choice(["Resolved", "Revisit booked",
                                  "Being fixed"]),
            "resolved_date": row["date"] + _dt.timedelta(days=2)
                             if good else None,
            "owner": CREW[0][0],
            "review_asked": "Yes" if good else "No",
            "review_left": "Yes" if good and rng.random() < 0.4
                           else "No",
            "follow_up": None,
            "notes": "",
        })
    # the complaint that matches the job marked up earlier
    row = jobs[complaint_job - 1]
    feedback.append({
        "date": row["date"] + _dt.timedelta(days=1),
        "customer": row["customer"],
        "job": _job(complaint_job),
        "property": row["property"],
        "crew": row["crew"],
        "source": "Complaint",
        "type": "Complaint",
        "score": 3,
        "comment": "Clippings all over the drive and the side gate "
                   "left open. The dog got out.",
        "cause": "Gate or access problem",
        "action": "Rang the same afternoon, went back and blew the "
                  "drive down, no charge. Gate check added to the "
                  "crew sheet.",
        "cost": 48.00,
        "status": "Revisit booked",
        "resolved_date": None,
        "owner": CREW[0][0],
        "review_asked": "No",
        "review_left": "No",
        "follow_up": today + _dt.timedelta(days=5),
        "notes": "New crew member's first week on that round.",
    })
    feedback.sort(key=lambda entry: entry["date"])

    # ---------------------------------------------------- the quotes --
    quotes: Rows = world["quotes"]
    for offset in range(58):
        prop = rng.randint(1, len(PROPERTIES))
        service, _weight = rng.choice(ONE_OFF_SERVICES)
        customer = PROPERTIES[prop - 1][0]
        date = today - _dt.timedelta(days=rng.randint(2, 300))
        est = _estimate(service, prop)
        price = round(max(cfg.minimum_visit,
                          est * cfg.charge_rate * rng.uniform(0.95,
                                                              1.2)), 2)
        age = (today - date).days
        if age < 6:
            status = "Sent"
        elif age < 40:
            status = rng.choice(["Accepted", "Accepted", "Declined",
                                 "Followed up"])
        else:
            status = rng.choice(["Accepted", "Declined", "Expired",
                                 "Accepted"])
        quotes.append({
            "date": date,
            "customer": _cus(customer),
            "property": _prp(prop),
            "service": service,
            "frequency": "One-off",
            "crew_size": 2,
            "materials_cost": _money(est * rng.uniform(4, 18)),
            "equipment_cost": None,
            "disposal_cost": _money(rng.choice([0, 0, 35, 60])),
            "target_margin": cfg.target_margin,
            "discount": None,
            "quoted_price": price,
            "status": status,
            "sent_date": date,
            "decision_date": date + _dt.timedelta(
                days=rng.randint(2, 14)) if status in
                ("Accepted", "Declined") else None,
            "job": "", "contract": "",
            "lost_reason": rng.choice([
                "Went with a cheaper quote",
                "Decided to do it themselves",
                "Never came back to us",
                "Timing did not suit",
            ]) if status == "Declined" else "",
            "notes": "",
        })
    # the one that has been sitting there too long
    quotes.append({
        "date": today - _dt.timedelta(days=18),
        "customer": _cus(4),
        "property": _prp(4),
        "service": "Mulch install",
        "frequency": "One-off",
        "crew_size": 2,
        "materials_cost": 620.00,
        "equipment_cost": 85.00,
        "disposal_cost": None,
        "target_margin": cfg.target_margin,
        "discount": None,
        "quoted_price": 1840.00,
        "status": "Sent",
        "sent_date": today - _dt.timedelta(days=18),
        "decision_date": None,
        "job": "", "contract": "",
        "lost_reason": "",
        "notes": "Eighteen days and no answer. One phone call is "
                 "worth more than three emails.",
    })
    quotes.sort(key=lambda entry: entry["date"])


def _world(cfg: Config) -> Dict[str, Any]:
    key = (cfg.today, cfg.labour_rate, cfg.charge_rate)
    cached = _WORLD_CACHE.get(key)
    if cached is None:
        cached = _build_world(cfg)
        _finish_world(cached, cfg)
        _WORLD_CACHE[key] = cached
    return cached


def _strip(rows: Rows) -> Rows:
    """Drop the private bookkeeping keys before the rows are written."""
    return [{key: value for key, value in row.items()
             if not key.startswith("_")} for row in rows]


def _from_world(name: str) -> Callable[[Config], Rows]:
    def builder(cfg: Config) -> Rows:
        return _strip(_world(cfg)[name])
    return builder


def _profit(cfg: Config) -> Rows:
    """Fourteen months to report on, with a target against each."""
    rows: Rows = []
    year = cfg.today.year
    month = cfg.today.month
    monthly_target = cfg.target_revenue_year / 12.0
    # the season does not spread itself evenly, and nor should the target
    weights = {1: 0.25, 2: 0.3, 3: 0.8, 4: 1.35, 5: 1.5, 6: 1.35,
               7: 1.2, 8: 1.15, 9: 1.2, 10: 1.35, 11: 1.0, 12: 0.4}
    for back in range(13, -1, -1):
        index = month - back
        keyed_year = year + (index - 1) // 12
        keyed_month = (index - 1) % 12 + 1
        rows.append({
            "month": f"{keyed_year:04d}-{keyed_month:02d}",
            "target": _money(monthly_target * weights[keyed_month]),
            "notes": ("Target weighted for the season - a target of "
                      "one twelfth a month is a target you will miss "
                      "for seven months and beat for five."
                      if back == 13 else ""),
        })
    return rows


_BUILDERS: Dict[str, Callable[[Config], Rows]] = {
    "customers": _customers,
    "properties": _properties,
    "services": _services,
    "crew": _crew,
    "equipment": _equipment,
    "materials": _materials,
    "contracts": _from_world("contracts"),
    "quotes": _from_world("quotes"),
    "jobs": _from_world("jobs"),
    "schedule": _from_world("schedule"),
    "timesheets": _from_world("timesheets"),
    "vehicles": _from_world("vehicles"),
    "invoices": _from_world("invoices"),
    "expenses": _from_world("expenses"),
    "feedback": _from_world("feedback"),
    "profit": _profit,
}


def get(module: str, cfg: Config) -> Rows:
    """Sample rows for a register module, or an empty list.

    Keyed by the *module* name (``jobs``), not the sheet name, because
    a mismatch here produces an empty register and no error at all.
    """
    builder = _BUILDERS.get(module)
    if builder is None:
        return []
    return builder(cfg)
