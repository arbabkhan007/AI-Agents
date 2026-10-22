"""16 Client Loyalty - points, tiers and referral rewards."""

from __future__ import annotations

from ..config import Config
from ..layout import Col, SheetSpec
from ..writer import cf_text, list_from
from .. import sample_data

NAME = "16 Client Loyalty"


def spec(cfg: Config) -> SheetSpec:
    return SheetSpec(
        name=NAME,
        title="16  Client Loyalty",
        subtitle="Visit-based points, tiers, reward eligibility and "
                 "referral rewards - all read from the CRM.",
        tab_color="#B98A2F",
        rows=cfg.row_count(NAME),
        freeze_cols=2,
        help_text="Pick a client and everything else fills in: visits and "
                  "referrals from the CRM, points from the rate on "
                  "Settings, tier and reward from the thresholds.",
        columns=[
            Col("client", "Client", 22, "text",
                validate=list_from("ClientNames")),
            Col("visits", "Visits", 8, "int",
                formula='IF({client}{r}="","",IFERROR(INDEX(ClientVisits,'
                        'MATCH({client}{r},ClientNames,0)),""))'),
            Col("points", "Points", 8, "int",
                formula='IF({visits}{r}="","",{visits}{r}*PointsPerVisit)'),
            Col("tier", "Tier", 9, "status",
                formula='IF({points}{r}="","",IF({points}{r}>='
                        'RewardThreshold*2,"Gold",IF({points}{r}>='
                        'RewardThreshold,"Silver","Bronze")))',
                cf=[cf_text("Gold", "good"), cf_text("Silver", "info")]),
            Col("reward_due", "Reward due", 10, "flag",
                formula='IF({points}{r}="","",IF({points}{r}>='
                        'RewardThreshold,"Yes","No"))',
                cf=[cf_text("Yes", "good")]),
            Col("referrals", "Referrals", 9, "int",
                formula='IF({client}{r}="","",IFERROR(INDEX('
                        'ClientReferrals,MATCH({client}{r},ClientNames,0)),'
                        '""))'),
            Col("ref_reward", "Referral credit", 11, "money",
                formula='IF({referrals}{r}="","",ROUND(N({referrals}{r})*'
                        'ReferralReward,2))'),
            Col("notes", "Rewards given & notes", 30, "wrap"),
        ],
        samples=sample_data.loyalty_rows(cfg)
        if cfg.include_sample_data else [],
        extra_notes=[
            "Points per visit, the reward threshold and the referral "
            "credit are all Settings - change the scheme without touching "
            "a formula.",
        ],
    )
