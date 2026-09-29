"""Brings the original letter/contract templates up to standard Nepali
court/office layout without rewriting their text: titles centred and
underlined, the date right-aligned, body paragraphs justified, and the
underscore signature lines replaced by a proper signature block with
left/right thumbprint boxes and witness lines.
"""
from __future__ import annotations

import dataclasses

from .dsl import doc
from .fields import Paragraph, TemplateSpec

_STANDARD_NOTE = {
    "en": "Standard format (not prescribed by a schedule): laid out to ordinary Nepali letter / contract conventions. "
          "Have a lawyer review any document before you sign or file it.",
    "ne": "मानक ढाँचा (अनुसूचीमा तोकिएको होइन): नेपालमा प्रचलित पत्र/सम्झौताको सामान्य ढाँचामा तयार गरिएको। "
          "हस्ताक्षर वा दाखिला गर्नु अघि कानून व्यवसायीसँग परामर्श गर्नुहोस्।",
}

_CATEGORY = {
    "legal_notice_salary": "notices",
    "legal_notice_deposit": "notices",
    "reply_notice": "notices",
    "rental_agreement": "deeds",
    "power_of_attorney": "deeds",
    "affidavit": "deeds",
    "employment_contract": "deeds",
    "nda": "deeds",
    "sale_agreement": "deeds",
}

_KEYWORDS = {
    "legal_notice_salary": ("unpaid salary", "wages", "तलब", "employer", "notice", "श्रम"),
    "legal_notice_deposit": ("deposit", "rent", "landlord", "धरौटी", "घरबहाल", "घरबेटी", "notice"),
    "reply_notice": ("reply", "response", "notice", "जवाफ", "सूचना"),
    "rental_agreement": ("rent", "lease", "tenancy", "landlord", "tenant", "घरबहाल", "बहाल", "घरधनी", "सम्झौता"),
    "power_of_attorney": ("power of attorney", "अख्तियारनामा", "agent", "representative", "प्रतिनिधि", "POA"),
    "affidavit": ("affidavit", "सपथपत्र", "स्वघोषणा", "sworn statement", "declaration"),
    "employment_contract": ("employment", "job", "contract", "रोजगार", "श्रम", "salary", "appointment letter"),
    "nda": ("nda", "confidentiality", "non-disclosure", "गोप्यता", "secret"),
    "sale_agreement": ("sale", "buy", "agreement", "बिक्री", "सम्झौता", "goods"),
}

_W_LINES = {
    "ne": ("@l,+ साक्षीहरू :\n@l १.|नाम, ठेगाना : ………………………………          सही : ………………\n"
           "@l २.|नाम, ठेगाना : ………………………………          सही : ………………\n"),
    "en": ("@l,+ Witnesses:\n@l 1.|Name, address: ………………………………          Signature: ………………\n"
           "@l 2.|Name, address: ………………………………          Signature: ………………\n"),
}


def _sig_blocks(spec_id: str) -> tuple[str, str] | None:
    """(ne, en) DSL for the closing signature block of a template."""
    date_ne = "@r,+ मितिः {{ today_bs }} (अंग्रेजी मितिः {{ today_ad }})\n"
    date_en = "@r,+ Date: {{ today_bs }} B.S. ({{ today_ad }} A.D.)\n"
    if spec_id == "power_of_attorney":
        ne = ("@l,+ अख्तियार दिनेको दस्तखत : ……………………          नाम : {{ principal_name }}\n"
              "@thumbs label=अख्तियार दिनेको ल्याप्चे सहीछाप\n"
              "@l,+ अख्तियार लिने प्रतिनिधिको मञ्जुरी दस्तखत : ……………………          नाम : {{ agent_name }}\n"
              + _W_LINES["ne"] + date_ne)
        en = ("@l,+ Principal's signature: ……………………          Name: {{ principal_name }}\n"
              "@thumbs label=Principal's thumbprints\n"
              "@l,+ Representative's acceptance signature: ……………………          Name: {{ agent_name }}\n"
              + _W_LINES["en"] + date_en)
        return ne, en
    if spec_id == "affidavit":
        ne = ("@l,+ बयान गर्नेको दस्तखत : ……………………          नाम : {{ declarant_name }}\n"
              "@thumbs label=बयान गर्नेको ल्याप्चे सहीछाप\n"
              "@l,+ बयान गर्नेले मेरो सामु सही गरेको प्रमाणित गर्ने अधिकारी : ……………………  (दस्तखत, नाम, पद, छाप)\n" + date_ne)
        en = ("@l,+ Declarant's signature: ……………………          Name: {{ declarant_name }}\n"
              "@thumbs label=Declarant's thumbprints\n"
              "@l,+ Attested by the officer before whom this was signed: ……………………  (signature, name, post, seal)\n" + date_en)
        return ne, en
    if spec_id == "rental_agreement":
        ne = ("@l,+ घरधनीको दस्तखत : ……………………          नाम : {{ landlord_name }}\n"
              "@thumbs label=घरधनीको ल्याप्चे सहीछाप\n"
              "@l,+ बहालवालाको दस्तखत : ……………………          नाम : {{ tenant_name }}\n"
              "@thumbs label=बहालवालाको ल्याप्चे सहीछाप\n"
              "@l,+ साक्षीहरू :\n@l १.|घरधनी तर्फबाट, नाम, ठेगाना : ……………………          सही : ………………\n"
              "@l २.|घरधनी तर्फबाट, नाम, ठेगाना : ……………………          सही : ………………\n"
              "@l ३.|बहालवाला तर्फबाट, नाम, ठेगाना : ……………………          सही : ………………\n"
              "@l ४.|बहालवाला तर्फबाट, नाम, ठेगाना : ……………………          सही : ………………\n" + date_ne)
        en = ("@l,+ Landlord's signature: ……………………          Name: {{ landlord_name }}\n"
              "@thumbs label=Landlord's thumbprints\n"
              "@l,+ Tenant's signature: ……………………          Name: {{ tenant_name }}\n"
              "@thumbs label=Tenant's thumbprints\n"
              "@l,+ Witnesses:\n@l 1.|Landlord's side, name, address: ……………………          Signature: ………………\n"
              "@l 2.|Landlord's side, name, address: ……………………          Signature: ………………\n"
              "@l 3.|Tenant's side, name, address: ……………………          Signature: ………………\n"
              "@l 4.|Tenant's side, name, address: ……………………          Signature: ………………\n" + date_en)
        return ne, en
    if spec_id == "employment_contract":
        ne = ("@l,+ रोजगारदाताको तर्फबाट दस्तखत : ……………………          नाम : {{ employer_name }}\n"
              "@l,+ कर्मचारीको दस्तखत : ……………………          नाम : {{ employee_name }}\n"
              "@thumbs label=कर्मचारीको ल्याप्चे सहीछाप\n" + _W_LINES["ne"] + date_ne)
        en = ("@l,+ Signed for the employer: ……………………          Name: {{ employer_name }}\n"
              "@l,+ Employee's signature: ……………………          Name: {{ employee_name }}\n"
              "@thumbs label=Employee's thumbprints\n" + _W_LINES["en"] + date_en)
        return ne, en
    if spec_id == "nda":
        ne = ("@l,+ पहिलो पक्षको दस्तखत : ……………………          नाम : {{ party_a_name }}\n"
              "@l,+ दोस्रो पक्षको दस्तखत : ……………………          नाम : {{ party_b_name }}\n"
              "@thumbs label=दोस्रो पक्षको ल्याप्चे सहीछाप\n" + _W_LINES["ne"] + date_ne)
        en = ("@l,+ First party's signature: ……………………          Name: {{ party_a_name }}\n"
              "@l,+ Second party's signature: ……………………          Name: {{ party_b_name }}\n"
              "@thumbs label=Second party's thumbprints\n" + _W_LINES["en"] + date_en)
        return ne, en
    if spec_id == "sale_agreement":
        ne = ("@l,+ बेच्नेको दस्तखत : ……………………          नाम : {{ seller_name }}\n"
              "@thumbs label=बेच्नेको ल्याप्चे सहीछाप\n"
              "@l,+ किन्नेको दस्तखत : ……………………          नाम : {{ buyer_name }}\n"
              "@thumbs label=किन्नेको ल्याप्चे सहीछाप\n" + _W_LINES["ne"] + date_ne)
        en = ("@l,+ Seller's signature: ……………………          Name: {{ seller_name }}\n"
              "@thumbs label=Seller's thumbprints\n"
              "@l,+ Buyer's signature: ……………………          Name: {{ buyer_name }}\n"
              "@thumbs label=Buyer's thumbprints\n" + _W_LINES["en"] + date_en)
        return ne, en
    return None


def _has_sig_line(p: Paragraph) -> bool:
    return any("____" in (t or "") for t in p.text.values())


def _polish_paragraph(p: Paragraph) -> Paragraph:
    ne = p.text.get("ne") or ""
    en = p.text.get("en") or ""
    first = ne or en
    kw: dict = {}
    if p.bold and p.align == "center":
        kw["underline"] = True
    if first.lstrip().startswith(("Date:", "मितिः")):
        kw["align"] = "right"
    elif any(k in first for k in ("Sincerely,", "भवदीय,")):
        kw["align"] = "right"
    elif p.align == "left" and not p.bold and len(first) > 90:
        kw["align"] = "justify"
    return dataclasses.replace(p, **kw) if kw else p


def polish(spec: TemplateSpec) -> TemplateSpec:
    blocks = []
    sig = _sig_blocks(spec.id)
    for b in spec.paragraphs:
        if isinstance(b, Paragraph):
            if sig and _has_sig_line(b):
                blocks.extend(doc(sig[0], "ne") + doc(sig[1], "en"))
                continue
            b = _polish_paragraph(b)
        blocks.append(b)
    law = spec.provisions[0]["law_title_ne"] if spec.provisions else ""
    return dataclasses.replace(
        spec,
        paragraphs=blocks,
        category=_CATEGORY.get(spec.id, spec.category),
        kind="standard",
        source={"law_title_ne": law, "note": _STANDARD_NOTE},
        keywords=_KEYWORDS.get(spec.id, ()),
    )
