"""Age calculator for majority and consent-age questions.

Age is counted on the Bikram Sambat calendar, whole years first (a person "turns
18" on the 18th BS anniversary of the birth date). The ages themselves are read
from the law:
- 10: a person who has not completed 10 years is legally incapable; from 10 up to
  18 semi-capable (Civil Code ss. 33, 34);
- 18: adult (Civil Code s. 32); also the age below which a person is a "child"
  (Act Relating to Children, 2075, s. 2) and below which consent to sexual
  intercourse is not valid (Criminal Code s. 219(2));
- 20: minimum age to marry (Civil Code s. 70(1)(घ); Criminal Code s. 173).
"""
from __future__ import annotations

import datetime

from . import dates
from .sources import Source, cite

CIV = "मुलुकी देवानी संहिता, २०७४"
CRI = "मुलुकी अपराध संहिता, २०७४"
CHILD = "बालबालिका सम्बन्धी ऐन, २०७५"

S_INCAPABLE = Source("age_10_incapable", CIV, "33", "दश वर्ष उमेर पूरा नभएको", "under 10: legally incapable")
S_SEMI = Source("age_10_18_semi", CIV, "34", "दश वर्ष पूरा भई अठार वर्ष उमेर पूरा नगरेको व्यक्ति अर्धसक्षम मानिनेछ", "10 to under 18: semi-capable")
S_ADULT = Source("age_18_adult", CIV, "32", "अठार वर्ष उमेर पूरा भएको प्रत्येक व्यक्ति बालिग", "18 completed: adult")
S_CHILD = Source("age_18_child", CHILD, "2 (2)", "अठार वर्ष उमेर पूरा नगरेको व्यक्ति", "under 18: a child under the Children's Act")
S_CONSENT = Source("age_18_consent", CRI, "219 (1)", "अठार वर्षभन्दा कम उमेरको कुनै बालिकालाई करणी", "under 18: consent does not count (s. 219(2))")
S_MARRIAGE = Source("age_20_marriage", CIV, "70", "बीस वर्ष उमेर पूरा भएमा", "20 completed: may marry")
S_MARRIAGE_CRIME = Source("age_20_marriage_offence", CRI, "173", "बीस वर्ष नपुगी", "marriage before 20 is an offence and void")

SOURCES = [v for v in list(globals().values()) if isinstance(v, Source)]

# (years, id, English label, Nepali label, provisions)
MARKERS = [
    (10, "capacity", "Legal capacity: under 10 incapable; 10 to under 18 semi-capable", "कानूनी सक्षमता: १० वर्ष नपुगेको असक्षम; १० देखि १८ वर्षभन्दा कम अर्धसक्षम", [S_INCAPABLE, S_SEMI]),
    (18, "majority", "Adulthood (majority); below 18 a child; consent age", "बालिग (१८ वर्ष); १८ वर्षभन्दा कम बालबालिका; सहमतिको उमेर", [S_ADULT, S_CHILD, S_CONSENT]),
    (20, "marriage", "Minimum age to marry", "विवाह गर्ने न्यूनतम उमेर", [S_MARRIAGE, S_MARRIAGE_CRIME]),
]


def markers_table() -> list[dict]:
    return [
        {"years": y, "id": i, "label": {"en": en, "ne": ne}, "provisions": [cite(s) for s in srcs]}
        for y, i, en, ne, srcs in MARKERS
    ]


def age_on(birth: datetime.date, as_of: datetime.date) -> dict:
    """Age of someone born on `birth` on the date `as_of`, and when they reach each
    legal age. Raises ValueError if `as_of` is before `birth`."""
    dates.check_ad_supported(birth)
    dates.check_ad_supported(as_of)
    if as_of < birth:
        raise ValueError("the as-of date cannot be before the date of birth")
    diff = dates.bs_difference(birth, as_of)
    thresholds = []
    for years, id_, en, ne, srcs in MARKERS:
        try:
            reached_on = dates.add_bs_years(birth, years)
            reached_iso = reached_on.isoformat()
            reached_bs = dates.bs_to_iso(dates.ad_to_bs(reached_on))
            reached = reached_on <= as_of
        except dates.UnsupportedDate:
            reached_iso = reached_bs = None
            reached = False
        thresholds.append({
            "years": years,
            "id": id_,
            "label": {"en": en, "ne": ne},
            "reached": reached,
            "reached_on": reached_iso,
            "reached_on_bs": reached_bs,
            "provisions": [cite(s) for s in srcs],
        })
    return {
        "birth_date": birth.isoformat(),
        "birth_date_bs": dates.bs_to_iso(dates.ad_to_bs(birth)),
        "as_of": as_of.isoformat(),
        "as_of_bs": dates.bs_to_iso(dates.ad_to_bs(as_of)),
        "years": diff.years,
        "months": diff.months,
        "days": diff.days,
        "total_days": diff.total_days,
        "thresholds": thresholds,
        "counting_note": {
            "en": "Age is counted on the Bikram Sambat calendar: a person turns N on the N-th BS anniversary of the birth date.",
            "ne": "उमेर वि.सं. पात्रो अनुसार गनिन्छ: जन्ममितिको N औँ वि.सं. वार्षिकोत्सवमा N वर्ष पूरा हुन्छ।",
        },
    }
