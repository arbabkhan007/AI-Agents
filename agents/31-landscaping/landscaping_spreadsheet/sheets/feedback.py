"""19. Customer Feedback - what they said, and what you did about it.

Complaints are not the enemy; unrecorded complaints are. A row here
with a date, a cause and a resolution is a business learning
something. The same complaint arriving three times from three
customers, with nobody noticing, is a business about to lose them.

Scores feed back to the customer record and to the crew scorecard, so
one piece of feedback lands everywhere it is relevant.
"""

from __future__ import annotations

from ..config import Palette, Config
from ..layout import Col, SheetSpec
from ..sample_data import get as sample
from ..writer import date_check, list_from
from .common import (alert_cf, alert_chain, amount, customer_col,
                     date_num_col, id_col, lookup_customer, month_col,
                     pick, rating_cf, score_validation,
                     status_cf, yesno, zero)

NAME = "Customer Feedback"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="Customer Feedback",
        subtitle="Compliments, complaints and scores - with the cause, "
                 "the fix and how long it took.",
        tab_color=Palette.primary_mid,
        rows=cfg.row_count("feedback"),
        samples=sample("feedback", cfg),
        freeze_cols=3,
        help_text=(
            "Log everything, good and bad. Put the Job ID on it when "
            "it is about a particular visit, and the score feeds both "
            "the customer's record and the crew scorecard. Then fill "
            "in what you did about it - that column is the one that "
            "turns a complaint into a repeat customer."),
        extra_notes=[
            "A score of 1 to 5. Anything at or below 3 counts as a "
            "problem and is chased on the dashboard until it is "
            "resolved.",
            "Recording the cause honestly - rushed, wrong day, "
            "machine broke, price surprise - is how three "
            "complaints turn into one fix.",
            "Ask for a review only after a resolved complaint or a "
            "compliment. The 'Review asked' column stops you asking "
            "the same person twice.",
        ],
        columns=[
            id_col("date", '"FBK-"', digits=4, header="Line"),
            Col("date", "Date", 11, "date",
                validate=date_check(),
                note="Start here - the day they told you."),
            customer_col(),
            Col("customer_name", "Customer", 20, "text",
                formula=lookup_customer("name")),
            Col("job", "Job ID", 11, "id",
                validate=pick("JobIDList",
                              "Pick the visit this is about."),
                note="If it is about one visit. Blank if it is general."),
            Col("property", "Property ID", 11, "id",
                validate=pick("PropertyList",
                              "Where it happened."),
                note="Where it happened, if it matters."),
            Col("crew", "Crew", 12, "text",
                validate=list_from("CrewNameList"),
                note="Which crew the feedback is about. Feeds their "
                     "quality score."),
            Col("source", "How it came in", 16, "text",
                validate=list_from("FeedbackSourceList")),
            Col("type", "Type", 16, "text",
                validate=list_from("FeedbackTypeList"),
                cf=status_cf()),
            Col("score", "Score", 8, "rating",
                validate=score_validation(5),
                cf=rating_cf(),
                note="1 to 5. Three or below is treated as a problem."),
            Col("comment", "What they said", 38, "wrap",
                note="Their words, not your summary of them. They are "
                     "more useful later."),
            Col("cause", "Cause", 20, "text",
                validate=pick("FeedbackCauseList",
                              "Why did it happen? Be honest - this is "
                              "for you, not for them."),
                note="The pattern in this column is worth more than "
                     "any individual complaint."),
            Col("action", "What you did", 34, "wrap",
                note="The fix. 'Recut the front, apologised, no "
                     "charge' is a complete answer."),
            Col("cost", "Cost to fix", 11, "money",
                validate=amount(0, 1000000,
                                "What putting it right cost you - a "
                                "free visit, a refund, replacement "
                                "plants."),
                note="Worth knowing. Poor work is rarely free."),
            Col("status", "Status", 14, "text",
                validate=list_from("FeedbackStatusList"),
                cf=status_cf()),
            Col("resolved_date", "Resolved on", 12, "date",
                validate=date_check()),
            Col("owner", "Handled by", 16, "text"),
            Col("review_asked", "Review asked", 11, "flag",
                validate=yesno("Have you asked this customer for a "
                               "public review?"),
                note="Ask after a compliment or a resolved complaint, "
                     "never after an unresolved one."),
            Col("review_left", "Review left", 10, "flag",
                validate=yesno()),
            Col("follow_up", "Follow up on", 12, "date",
                validate=date_check(),
                note="Put a date here and it will be chased."),
            Col("notes", "Notes", 24, "wrap"),

            # ---- the worked out bits ---------------------------------
            Col("is_problem", "Problem", 8, "int",
                formula=zero("date",
                             'IF(({type}{r}="Complaint")+'
                             '({type}{r}="Quality issue")+'
                             '({type}{r}="Damage claim")+'
                             '(AND({score}{r}>0,{score}{r}<=3))>0,'
                             '1,0)'),
                hidden=True,
                note="A complaint, a quality issue, a damage claim or "
                     "a score of three or less."),
            Col("is_open", "Open", 6, "int",
                formula=zero("date",
                             'IF(({status}{r}="Resolved")+'
                             '({status}{r}="Closed")>0,0,1)'),
                hidden=True),
            Col("days_open", "Days open", 10, "int",
                formula=zero("date",
                             'IF({is_open}{r}=0,'
                             'IF({resolved_date}{r}="",0,'
                             '{resolved_date}{r}-{date}{r}),'
                             'TodayDate-{date}{r})'),
                cf=[{"type": "cell", "criteria": ">=", "value": 14,
                     "fmt": "bad"},
                    {"type": "cell", "criteria": ">=", "value": 7,
                     "fmt": "warn"}],
                note="How long it took, or how long it has been "
                     "sitting there."),
            Col("is_promoter", "Promoter", 8, "int",
                formula=zero("date",
                             'IF({score}{r}>=4,1,0)'),
                hidden=True),
            date_num_col("date", "date_num"),
            month_col("date"),

            Col("alert", "What needs doing", 44, "wrap",
                formula=alert_chain("date", [
                    ('AND({is_problem}{r}=1,{is_open}{r}=1,'
                     '{days_open}{r}>=7)',
                     "Urgent - an unresolved complaint over a week old"),
                    ('AND({is_problem}{r}=1,{is_open}{r}=1)',
                     "Action - complaint open, deal with it today"),
                    ('AND({is_open}{r}=1,{follow_up}{r}<>"",'
                     '{follow_up}{r}<=TodayDate)',
                     "Follow up - the follow-up date has arrived"),
                    ('AND({is_problem}{r}=1,{cause}{r}="")',
                     "Add - no cause recorded, so nothing can be "
                     "learned from it"),
                    ('AND({is_problem}{r}=1,{action}{r}="")',
                     "Add - nothing recorded about what you did"),
                    ('AND({is_promoter}{r}=1,'
                     '{review_asked}{r}<>"Yes")',
                     "Action - a happy customer who has not been "
                     "asked for a review"),
                    ('AND({review_asked}{r}="Yes",'
                     '{review_left}{r}<>"Yes",'
                     'TodayDate-{date}{r}>=FeedbackChaseDays)',
                     "Follow up - review asked for but never left"),
                    ('{is_open}{r}=1', "Due - still open"),
                ]),
                cf=alert_cf()),
        ],
    )
