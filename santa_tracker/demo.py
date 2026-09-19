"""Fictional demo party: the Novality Store holiday party, December 2026.

Feeds cached values into every formula cell of the EXAMPLE workbooks so the
file opens looking alive (and so calc_check can prove the caches match what
the formulas compute).
"""

import datetime


def today():
    # build-date aware, so the dashboard's "days to go" cache is correct the
    # day the EXAMPLE file is generated (Excel recalculates it on open)
    return datetime.date.today()


# ---------------------------------------------------------------------------
# cast
# ---------------------------------------------------------------------------
PEOPLE = [
    # name, team, household, rsvp, diet, last year gave to, status, notes
    ("Ava Novak", "Studio", "Novak home", "Yes", "", "Jack Byrne",
     "Complete", "Hosting helper - arrives early"),
    ("Ben Carter", "Shop", "", "Yes", "Vegetarian", "Ava Novak",
     "Gift Purchased", "Owes Kia a bet from 2025"),
    ("Chloe Diaz", "Online", "", "Yes", "Vegan", "Grace Liu",
     "Wrapped", ""),
    ("Dan Novak", "Studio", "Novak home", "Yes", "", "Elena Petrov",
     "Gift Purchased", "Ava's husband - couple rule applies"),
    ("Elena Petrov", "Shop", "", "Maybe", "Gluten-free", "Farid Khan",
     "Not Started", "Waiting on shift rota"),
    ("Farid Khan", "Shop", "", "Yes", "Halal", "Chloe Diaz",
     "Wrapped", ""),
    ("Grace Liu", "Online", "Flat 4B", "Yes", "", "Hugo Silva",
     "Complete", "Flat 4B - couple rule applies too"),
    ("Hugo Silva", "Online", "Flat 4B", "Yes", "", "Grace Liu",
     "Gift Purchased", ""),
    ("Isla Moore", "Studio", "", "No", "", "Leo Fontaine",
     "Not Started", "Away in December - sad face"),
    ("Jack Byrne", "Shop", "", "Yes", "Nut allergy", "Ava Novak",
     "Gift Purchased", "Espresso-machine feud with Leo"),
    ("Kia Osei", "Online", "", "Yes", "", "Ben Carter",
     "Wrapped", ""),
    ("Leo Fontaine", "Studio", "", "Yes", "Vegetarian", "Isla Moore",
     "Gift Purchased", ""),
]

CUSTOM_PAIRS = [
    ("Jack Byrne", "Leo Fontaine", "Espresso-machine feud of 2025"),
    ("Kia Osei", "Ben Carter", "Last year's regrettable candle"),
]

RULES = {"couple": "On", "team": "Off", "lastyear": "On"}

SPENT = [32.50, 24.00, 28.75, 31.20, 18.00, 26.40, 33.10, 42.00,
         0.00, 29.95, 27.30, 25.60]
RECEIPTS = ["\u2713", "", "\u2713", "", "", "\u2713", "", "\u2713", "",
            "\u2713", "", "\u2713"]
REFS = ["NV-88121", "", "AMZ-4071", "", "", "ETS-2210", "", "NV-88203",
        "", "AMZ-4188", "", "ETS-2355"]

WISHES = [
    ("Ava Novak", "Chunky knit throw blanket", "Must-love",
     "https://example.com/throw", "\u2713", "Any colour but grey"),
    ("Ava Novak", "Ceramic mug tree", "Nice to have", "", "", ""),
    ("Ben Carter", "Single-origin coffee beans 1kg", "Must-love",
     "https://example.com/beans", "\u2713", "No dark roasts"),
    ("Chloe Diaz", "Vegan candle trio", "Nice to have", "", "", ""),
    ("Chloe Diaz", "Linen tea towel set", "Just an idea", "", "", ""),
    ("Dan Novak", "Whisky tasting set", "Must-love",
     "https://example.com/whisky", "", "Peated, please"),
    ("Elena Petrov", "Gluten-free chocolate box", "Must-love", "", "", ""),
    ("Farid Khan", "Desk plant (low light)", "Nice to have", "", "\u2713", ""),
    ("Grace Liu", "Silk scrunchie set", "Just an idea", "", "", ""),
    ("Grace Liu", "Matcha ceremony kit", "Must-love",
     "https://example.com/matcha", "", ""),
    ("Hugo Silva", "Vinyl: jazz classics", "Nice to have", "", "", ""),
    ("Jack Byrne", "Espresso tamp mat", "Must-love", "", "", "Obvious reasons"),
    ("Kia Osei", "Botanical print A4", "Nice to have", "", "\u2713", ""),
    ("Leo Fontaine", "Sourdough starter kit", "Just an idea", "", "", ""),
    ("Leo Fontaine", "Wooden bread lame", "Nice to have", "", "", ""),
    ("Isla Moore", "Travel journal", "Nice to have", "", "", ""),
]

WE_GIFTS = [
    ("Giant pickle plushie", 12.00),
    ("Disco-ball bauble set", 15.50),
    ("Mystery sealed box", 20.00),
    ("Heated mug coaster", 18.25),
    ("Llama Christmas jumper", 22.00),
    ("Singing fish plaque", 14.75),
    ("Fancy hot chocolate tin", 16.40),
    ("Desktop zen garden", 19.90),
    ("Reindeer antler headband", 11.30),
    ("Marble cheese board", 24.50),
]

# round-1 turns then round-2 catch-up turns for the stolen-from players
HISTORY = [
    (1, "Pick", 4, ""),
    (2, "Pick", 7, ""),
    (3, "Steal", 4, None),     # from order 1
    (4, "Pick", 2, ""),
    (5, "Steal", 4, None),     # from order 3 -> gift 4 locks (2 steals)
    (6, "Pick", 9, ""),
    (7, "Steal", 9, None),     # from order 6
    (8, "Pick", 1, ""),
    (9, "Steal", 1, None),     # from order 8
    (10, "Pick", 6, ""),
    (1, "Pick", 3, ""),        # round 2: Ava replaces her stolen gift
    (2, "Pass", 7, ""),
    (3, "Pick", 5, ""),        # Chloe replaces hers
    (4, "Pass", 2, ""),
]


def _offset_for(people, pairs, rules):
    n = len(people)
    for off in range(1, n):
        ok = True
        for i in range(n):
            rec = people[(i + off) % n][0]
            g = people[i]
            if rec == g[0]:
                ok = False
            if rules["couple"] == "On" and g[2] and \
                    people[(i + off) % n][2] == g[2]:
                ok = False
            if rules["lastyear"] == "On" and rec == g[6 - 1]:
                ok = False
            if (g[0], rec) in pairs:
                ok = False
        if ok:
            return off
    return 1


def _rank(keys):
    """1-based rank, largest first (matches Excel RANK default)."""
    order = sorted(range(len(keys)), key=lambda i: -keys[i])
    out = [0] * len(keys)
    for pos, i in enumerate(order):
        out[i] = pos + 1
    return out


class Demo(object):
    def __init__(self):
        self.people = [dict(zip(
            ("name", "team", "household", "rsvp", "diet", "lastyear",
             "status", "notes"), p)) for p in PEOPLE]
        self.pairs = [(a, b) for a, b, _ in CUSTOM_PAIRS]
        self.pair_reason = {(a, b): r for a, b, r in CUSTOM_PAIRS}
        self.rules = dict(RULES)
        n = len(self.people)
        self.offset = _offset_for(PEOPLE, self.pairs, RULES)
        self.assign = [self.people[(i + self.offset) % n]["name"]
                       for i in range(n)]
        self.spent = list(SPENT)
        self.receipts = list(RECEIPTS)
        self.refs = list(REFS)
        self.wishes = WISHES
        self.settings = {
            "party": "Novality Store Holiday Party",
            "message": "19 Dec - bring a wrapped gift and a stealing face!",
            "currency": "$",
            "year": 2026,
            "date": datetime.date(2026, 12, 19),
            "location": "Novality Loft, 12 Market Street",
            "host": "The Novality Team",
            "bmin": 20.0, "bmax": 35.0, "steals": 2, "start": 1,
            # the workbook's draw shift is MOD(seed-1, N-1); seed = offset+1
            # makes the live formula reproduce this demo's assignment
            "seed": self.offset + 1,
            "weseed": 7,
            "status": "Final \u2014 locked \U0001F512",
        }
        self._build_we()
        self._agg()

    # ------------------------------------------------------------------
    def _build_we(self):
        s = self.settings["weseed"]
        players = [p["name"] for p in self.people if p["rsvp"] != "No"][:10]
        n = len(players)
        k1 = [((s * 7919 * (i + 2) + i * 104729) % 999983) * 100 + i
              for i in range(n)]
        k2 = [((s * 6967 * (i + 5) + i * 1299709) % 999983) * 100 + i
              for i in range(n)]
        # exposed so the sheet builder can cache the hidden helper columns
        self.we_k1 = k1
        self.we_k2 = k2
        seats = _rank(k1)              # seat order per player row
        nums = _rank(k2)               # gift number per player row
        self.we = []
        for i, pl in enumerate(players):
            self.we.append({
                "player": pl, "seat": seats[i], "giftnum": nums[i],
                "desc": WE_GIFTS[i][0], "value": WE_GIFTS[i][1],
            })
        by_seat = {w["seat"]: w for w in self.we}
        by_num = {w["giftnum"]: w for w in self.we}
        self.history = []
        holder = {}
        steals = {}
        for turn, (seat, action, gnum, _) in enumerate(HISTORY, 1):
            pl = by_seat[seat]["player"]
            frm = ""
            if action == "Steal":
                frm = holder.get(gnum, "")
                holder[gnum] = pl
                steals[gnum] = steals.get(gnum, 0) + 1
            elif action == "Pick":
                holder[gnum] = pl
            self.history.append((turn, pl, action, gnum, frm))
        self.holder = holder
        self.steals = steals
        self.last_action = {}
        for turn, pl, action, gnum, frm in self.history:
            self.last_action[gnum] = action
        for w in self.we:
            g = w["giftnum"]
            w["steals"] = steals.get(g, 0)
            w["holder"] = holder.get(g, "")
            w["last"] = self.last_action.get(g, "")
            complete = len(set(holder.values())) == len(self.we)
            if w["steals"] >= self.settings["steals"] or complete:
                w["status"] = "\U0001F512 Final"
            elif g not in holder:
                w["status"] = "\U0001F381 Available"
            elif w["last"] == "Steal":
                w["status"] = "\U0001F504 Stolen"
            else:
                w["status"] = "\U0001F932 Held"
            frm = ""
            for turn, pl, action, gn, f in reversed(self.history):
                if gn == g and action == "Steal":
                    frm = f
                    break
            w["stolenfrom"] = frm if w["status"] == "\U0001F504 Stolen" else ""
            w["final"] = ""
        self.we_players = players
        self.we_by_seat = by_seat
        self.by_num = by_num

    # ------------------------------------------------------------------
    def money(self, value, decimals=2):
        cur = self.settings["currency"]
        if decimals:
            return "%s%.*f" % (cur, decimals, value)
        return "%s%d" % (cur, value)

    def _agg(self):
        n = len(self.people)
        st = [p["status"] for p in self.people]
        bought = sum(1 for s in st if s in ("Gift Purchased", "Wrapped",
                                            "Complete"))
        wrapped = sum(1 for s in st if s in ("Wrapped", "Complete"))
        done = sum(1 for s in st if s == "Complete")
        spent = sum(self.spent)
        rules = sum(1 for v in self.rules.values() if v == "On") + \
            len(self.pairs)
        in_play = sum(1 for w in self.we if w["status"] in
                      ("\U0001F932 Held", "\U0001F504 Stolen"))
        locked = sum(1 for w in self.we if w["status"] == "\U0001F512 Final")
        comp = (bought + wrapped + done) / (3.0 * n)
        self.agg = {
            "participants": n,
            "rsvp_yes": sum(1 for p in self.people if p["rsvp"] == "Yes"),
            "rsvp_pending": sum(1 for p in self.people
                                if p["rsvp"] == "Maybe"),
            "assigned": n,
            "purchased": bought,
            "wrapped": wrapped,
            "complete": done,
            "total_budget": n * self.settings["bmax"],
            "spent": spent,
            "avg_gift": spent / bought,
            "rules_count": rules,
            "we_players": len(self.we),
            "gifts_in_play": in_play,
            "locked_gifts": locked,
            "completion": comp,
            "turns_done": len(self.history),
            "current_turn": (self.settings["start"] - 1 +
                             len(self.history)) % len(self.we) + 1,
            "violations": 0,
            "over_budget": sum(1 for x in self.spent
                               if x > self.settings["bmax"]),
            "diets": sum(1 for p in self.people if p["diet"]),
        }
