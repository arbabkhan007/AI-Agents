"""👥 Participants - the guest list with RSVP, teams and status."""

from .. import config as C
from ..book import r, ci
from . import common as K

KEY = "participants"
LAST_COL = "J"

COLUMNS = [
    ("n", "#", "idx", None),
    ("name", "Participant", "text", None),
    ("team", "Team / dept", "center", None),
    ("household", "Household / couple", "center", None),
    ("rsvp", "RSVP", "center", None),
    ("diet", "Dietary needs", "center", None),
    ("lastyear", "Gave to last year", "center", None),
    ("status", "Gift status", "center", None),
    ("wishes", "Wishes", "calc_num", None),
    ("notes", "Notes", "wrap", None),
]


def build(bk):
    th = bk.th
    m = bk.demo
    K.sheet_head(bk, KEY, LAST_COL,
                 "\U0001F465  Participants",
                 "Everyone in the draw - RSVP, household and team feed the "
                 "exclusion rules automatically.")
    K.table_frame(bk, KEY, COLUMNS, height=20)
    if m:
        for i, p in enumerate(m.people):
            row = C.ROW_FIRST + i
            K.write_row(bk, KEY, COLUMNS, row,
                        {"n": i + 1, "name": p["name"], "team": p["team"],
                         "household": p["household"], "rsvp": p["rsvp"],
                         "diet": p["diet"], "lastyear": p["lastyear"],
                         "status": p["status"], "notes": p["notes"] or ""},
                        {"wishes": sum(1 for w in m.wishes
                                       if w[0] == p["name"])})
    for i in range(len(m.people) if m else 0, C.CAP[KEY]):
        K.write_row(bk, KEY, COLUMNS, C.ROW_FIRST + i,
                    {"n": i + 1, "name": "", "team": "", "household": "",
                     "rsvp": "", "diet": "", "lastyear": "", "status": "",
                     "wishes": "", "notes": ""})
    # wishes count formula per row
    wrng = bk.rng("wishlists", "who") if bk.has("wishlists") else None
    for i in range(C.CAP[KEY]):
        row = C.ROW_FIRST + i
        if wrng:
            bk.ws(KEY).write_formula(
                r(row), ci(bk.col(KEY, "wishes")),
                '=IF($B%d="","",COUNTIF(%s,$B%d))' % (row, wrng, row),
                bk.S.f(**bk.S.base(font_size=10.5, font_color=th.primary,
                                   bg_color=th.alt, align="center",
                                   valign="vcenter", border=1,
                                   border_color=th.border,
                                   num_format="#,##0")),
                sum(1 for w in (m.wishes if m else [])
                    if w[0] == (m.people[i]["name"] if i < len(m.people)
                                else "")) or "")
            bk.stats["formulas"] += 1

    K.list_dv(bk, KEY, "team", "teams")
    K.list_dv(bk, KEY, "diet", "diets")
    K.fixed_dv(bk, KEY, "rsvp", "RSVP")
    K.fixed_dv(bk, KEY, "status", "Statuses")
    K.status_cf(bk, KEY, "status", {
        C.ST_NOT: (th.bad_soft, th.bad),
        C.ST_BOUGHT: (th.warn_soft, th.warn),
        C.ST_WRAPPED: (th.info_soft, th.info),
        C.ST_DONE: (th.ok_soft, th.ok)})
    K.status_cf(bk, KEY, "rsvp", {
        "Yes": (th.ok_soft, th.ok),
        "No": (th.bad_soft, th.bad),
        "Maybe": (th.warn_soft, th.warn)})

    names = "$B$%d:$B$%d" % (C.ROW_FIRST, C.last_row(KEY))
    st = "$H$%d:$H$%d" % (C.ROW_FIRST, C.last_row(KEY))
    rv = "$E$%d:$E$%d" % (C.ROW_FIRST, C.last_row(KEY))
    chips = [
        ('="\U0001F465 In the draw: "&COUNTA(%s)' % names, "primary",
         "In the draw: %d" % (m.agg["participants"] if m else 0), 3),
        ('="\u2705 RSVP yes: "&COUNTIF(%s,"Yes")' % rv, "ok",
         "RSVP yes: %d" % (m.agg["rsvp_yes"] if m else 0), 3),
        ('="\u23F3 Awaiting: "&COUNTIF(%s,"Maybe")+COUNTIF(%s,"No")'
         % (rv, rv), "warn",
         "Awaiting: %d" % (sum(1 for p in m.people
                                if p["rsvp"] in ("Maybe", "No"))
                           if m else 0), 3),
        ('="\U0001F381 Ready (wrapped+done): "&COUNTIF(%s,"%s")+COUNTIF(%s,'
         '"%s")' % (st, C.ST_WRAPPED, st, C.ST_DONE), "gold",
         "Ready: %d" % (m.agg["wrapped"] if m else 0), 3),
    ]
    K.chips(bk, KEY, chips, LAST_COL)
    K.footer_nav(bk, KEY, C.last_row(KEY) + 2, LAST_COL)
