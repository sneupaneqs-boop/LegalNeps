"""Shared builders for the prescribed-format templates: party blocks,
signature blocks, the schedule-heading toggle, and the `official()` /
`standard()` constructors that stamp `source`, `kind` and `category`."""
from __future__ import annotations

import json
import pathlib

from .dsl import F, SELECT, doc
from .fields import Field, TemplateSpec

_URLS = json.loads((pathlib.Path(__file__).parent / "law_urls.json").read_text(encoding="utf-8"))

# law short names -> corpus doc_title_ne (must match the corpus / law_urls.json)
CDPC = "मुलुकी देवानी कार्यविधि संहिता, २०७४"          # civil procedure code
CDPR = "मुलुकी देवानी कार्यविधि नियमावली, २०७५"        # civil procedure rules
CRPC = "मुलुकी फौजदारी कार्यविधि संहिता, २०७४"         # criminal procedure code
SC_RULES = "सर्वोच्च अदालत नियमावली, २०७४"
HC_RULES = "उच्च अदालत नियमावली, २०७३"
DC_RULES = "जिल्ला अदालत नियमावली, २०७५"
RTI_RULES = "सूचनाको हक सम्बन्धी नियमावली, २०६५"
CONSUMER_RULES = "उपभोक्ता संरक्षण नियमावली, २०७६"
MEDIATION_RULES = "मेलमिलाप सम्बन्धी नियमावली, २०७०"
LABOUR_RULES = "श्रम नियमावली, २०७५"
PERSONAL_EVENTS_RULES = "जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने)नियमावली, २०३४"
MARRIAGE_RULES = "विवाह दर्ता नियमावली, २०२८"
NOTARY_RULES = "लेख्य प्रमाणक नियमावली, २०४१"
FEA_RULES = "वैदेशिक रोजगार नियमावली, २०६४"
DV_RULES = "घरेलु हिंसा (कसूर र सजाय) नियमावली, २०६७"
MALPOT_RULES = "मालपोत नियमावली, २०३६"


def law_url(law: str, page: int | None = None) -> str:
    base = _URLS[law]
    return f"{base}#page={page}" if page else base


def source(law: str, schedule: str, relates_to: str, page: int, form_title: str, law_en: str = "") -> dict:
    return {
        "law_title_ne": law,
        "law_title_en": law_en,
        "schedule": schedule,
        "relates_to": relates_to,
        "form_title": form_title,
        "url": law_url(law, page),
        "page": page,
    }


SCHEDULE_TOGGLE = Field(
    "schedule_heading",
    {"en": "Print the schedule heading lines", "ne": "अनुसूचीको शीर्षक (अनुसूची नं., सँग सम्बन्धित नियम/दफा) छाप्ने"},
    "select", False,
    {"en": "The official schedule starts with lines such as \"अनुसूची–१ (दफा ९५ सँग सम्बन्धित)\". Keep them "
           "for an exact copy of the prescribed form; choose No for a clean filing copy.",
     "ne": "आधिकारिक अनुसूची \"अनुसूची–१ (दफा ९५ सँग सम्बन्धित)\" जस्ता पङ्क्तिबाट सुरु हुन्छ। हुबहु नमुना चाहिए "
           "छाप्ने; सफा दाखिला प्रति चाहिए नछाप्ने रोज्नुहोस्।"},
    "yes",
    [{"value": "yes", "label": {"en": "Yes - print them", "ne": "छाप्ने"}},
     {"value": "no", "label": {"en": "No - omit them", "ne": "नछाप्ने"}}],
)


def schedule_heading(schedule: str, relates_to: str, form_title: str) -> list:
    """The three heading lines every schedule carries, switchable by the
    `schedule_heading` field."""
    guard_open, guard_close = "{% if schedule_heading != 'no' %}", "{% endif %}"
    return doc(
        f"@c {guard_open}{schedule}{guard_close}\n"
        f"@c {guard_open}({relates_to} सँग सम्बन्धित){guard_close}\n"
        f"@cbu {guard_open}{form_title}{guard_close}"
    )


def official(
    *, id: str, title_en: str, title_ne: str, desc_en: str, desc_ne: str, category: str,
    law: str, schedule: str, relates_to: str, page: int, form_title: str,
    fields: list, body: str, provisions: list | None = None, keywords: tuple = (), law_en: str = "",
    heading: bool = True, font_size: float = 12.0, body_en: str | None = None,
) -> TemplateSpec:
    """A template transcribed from a statutory schedule. Prescribed forms
    exist only in Nepali; `body_en` optionally adds an unofficial English
    rendering (used where a template pre-dates this and was bilingual)."""
    blocks = (schedule_heading(schedule, relates_to, form_title) if heading else []) + doc(body)
    if body_en:
        blocks = blocks + doc(body_en, "en")
    flds = ([SCHEDULE_TOGGLE] if heading else []) + list(fields)
    return TemplateSpec(
        id=id,
        title={"en": title_en, "ne": title_ne},
        description={"en": desc_en, "ne": desc_ne},
        fields=flds,
        paragraphs=blocks,
        provisions=provisions or [],
        category=category,
        kind="official",
        source=source(law, schedule, relates_to, page, form_title, law_en),
        languages=("en", "ne") if body_en else ("ne",),
        font_size=font_size,
        keywords=keywords,
    )


def standard(
    *, id: str, title_en: str, title_ne: str, desc_en: str, desc_ne: str, category: str,
    fields: list, body: str, provisions: list | None = None, keywords: tuple = (),
    basis_law: str | None = None, basis_note: dict | None = None, font_size: float = 12.0,
    body_en: str | None = None,
) -> TemplateSpec:
    """A template with no prescribing schedule: laid out to standard Nepali
    court / office letter conventions and labelled as such."""
    src = None
    if basis_law or basis_note:
        src = {"law_title_ne": basis_law or "", "note": basis_note or {}}
    return TemplateSpec(
        id=id,
        title={"en": title_en, "ne": title_ne},
        description={"en": desc_en, "ne": desc_ne},
        fields=list(fields),
        paragraphs=doc(body) + (doc(body_en, "en") if body_en else []),
        provisions=provisions or [],
        category=category,
        kind="standard",
        source=src,
        languages=("en", "ne") if body_en else ("ne",),
        font_size=font_size,
        keywords=keywords,
    )


# ------------------------------------------------------------- shared fields

REG_NO = F("reg_no", "Registration no. (court fills)", "दर्ता नं. (अदालतले भर्ने)")
REG_DATE = F("reg_date", "Registration date (court fills)", "दर्ता मिति (अदालतले भर्ने)", "date")
DATE = F("doc_date", "Date of the document", "लिखत मिति", "date",
         help_en="Picked as A.D., printed in B.S. (इति सम्वत् ... साल ... महिना ... गते ... रोज ... शुभम्)",
         help_ne="ए.डी. मा चयन गर्नुहोस्; बि.सं. मा छापिन्छ (इति सम्वत् ... साल ... महिना ... गते ... रोज ... शुभम्)")
CASE_TITLE = F("case_title", "Case (मुद्दा)", "मुद्दा", required=True,
               help_en="Nature of the case, e.g. अंश, बकसपत्र बदर, ऋण असुली", help_ne="जस्तै: अंश, बकसपत्र बदर, ऋण असुली")
LAWYERS = F("lawyers", "Lawyers appointed (one per line: name | licence no.)",
            "नियुक्त कानून व्यवसायी (एक पङ्क्तिमा: नाम | प्रमाणपत्र नं.)", "textarea")
FEES = F("fees", "Fees paid with this filing (one per line: item | amount NPR)",
         "यसैसाथ बुझाएको दस्तुर (एक पङ्क्तिमा: विवरण | रु.)", "textarea")
EVIDENCE = F("evidence", "Evidence attached (one per line)", "संलग्न प्रमाण (एक पङ्क्तिमा एउटा)", "textarea")
WITNESSES = F("witnesses", "Witnesses (one per line: full name, age, address)",
              "साक्षी (एक पङ्क्तिमा: पूरा नाम, उमेर, ठेगाना)", "textarea")

RELATIONS = ["छोरा", "छोरी", "पति", "पत्नी"]


def party_fields(prefix: str, en_role: str, ne_role: str, required: bool = True) -> list:
    return [
        F(f"{prefix}_name", f"{en_role}: full name", f"{ne_role}को पूरा नाम", required=required),
        F(f"{prefix}_father", f"{en_role}: father's / grandfather's (or spouse's) name",
          f"{ne_role}का बाबु/बाजे (वा पति/पत्नी) को नाम"),
        SELECT(f"{prefix}_rel", f"{en_role}: relation", f"{ne_role}: नाता", RELATIONS),
        F(f"{prefix}_addr", f"{en_role}: address (district, municipality/ward, tole)",
          f"{ne_role}को ठेगाना (जिल्ला, गा.पा./न.पा., वडा नं., टोल)"),
        F(f"{prefix}_age", f"{en_role}: age (years)", f"{ne_role}को उमेर (वर्ष)", "number"),
    ]


def party_line(prefix: str, role_ne: str) -> str:
    """The prescribed party line "… को छोरा/छोरी/पति/पत्नी … बस्ने वर्ष … को … बादी"."""
    return (
        f"{{{{ {prefix}_father|blank }}}} को {{{{ {prefix}_rel|default('छोरा/छोरी/पति/पत्नी', true) }}}} "
        f"{{{{ {prefix}_addr|blank(8) }}}} बस्ने वर्ष {{{{ {prefix}_age|nd|blank(3) }}}} को "
        f"{{{{ {prefix}_name|blank(8) }}}} **{role_ne}**"
    )


def more_parties_field(id: str, en_role: str, ne_role: str) -> Field:
    return F(id, f"Additional {en_role}s (one per line)",
             f"थप {ne_role} (एक पङ्क्तिमा एक जना)", "textarea",
             help_en="Write each in the same form: father's name को छोरा/पति ..., address बस्ने वर्ष .. को full name",
             help_ne="प्रत्येक जनाको विवरण यसै ढाँचामा लेख्नुहोस्: बाबुको नाम को छोरा/पति ..., ठेगाना बस्ने वर्ष .. को पूरा नाम")


def court_field(help_ne: str = "जस्तै: काठमाडौं जिल्ला अदालत") -> Field:
    return F("court", "Court / office (full name)", "अदालत/कार्यालयको पूरा नाम",
             help_en="e.g. Kathmandu District Court (in Nepali)", help_ne=help_ne)


def court_line(verb: str = "दायर गरेको") -> str:
    """'… अदालत/कार्यालयमा दायर गरेको' - the prescribed wording when blank, the
    natural filled reading when a court is named."""
    return ("{{ court|blank(12) }}{% if not court %} अदालत/कार्यालय{% endif %}मा " + verb)


def numbered_items(field: str, label_min: int = 3, indent: float = 1.0) -> str:
    """(क) (ख) (ग) lines repeated per line of a textarea answer."""
    return f"@l,>{indent},each={field}:{label_min} ({{{{ ka }}}})|{{{{ item }}}}"


FEE_ITEMS = (
    "@l,>1,each=fees:3 ({{ ka }})|{% set _p = (item.split('|') + ['', ''])[:2] %}"
    "{{ _p[0]|trim|blank(8) }} बापत रु {{ _p[1]|trim|nd|blank(6) }}"
)


def pair_items(field: str, label_min: int, first: str, second: str, indent: float = 1.0, gap: int = 6) -> str:
    """(क) <first> ... <second> ... lines from textarea rows written "a | b"."""
    sp = "\u00a0" * gap
    return (
        f"@l,>{indent},each={field}:{label_min} ({{{{ ka }}}})|{first} "
        "{% set _p = (item.split('|') + ['', ''])[:2] %}{{ _p[0]|trim|blank(6) }}" + sp + f"{second} "
        "{{ _p[1]|trim|blank(6) }}"
    )


__all__ = [n for n in dir() if not n.startswith("_")]
