"""
Builds backend/app/data/glossary.json: English and romanised-Nepali words
people actually type -> the formal Nepali terms statutes use. The app uses
it to expand queries locally, so English/romanised questions still reach
the right Nepali provisions when no LLM call is possible (no key, quota,
outage), and to strengthen LLM-rewritten queries.

    GEMINI_API_KEY=... python3 backend/scripts/build_glossary.py

Resumable: areas already in the file are skipped. Paced for free-tier RPM.
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "backend", "app", "data", "glossary.json")
sys.path.insert(0, os.path.join(ROOT, "backend"))

AREAS = [
    "landlord-tenant and house rent", "marriage, divorce and matrimonial property", "child custody, adoption, guardianship",
    "inheritance, partition (अंश), wills, ancestral property", "contracts, sale, agency, guarantees",
    "loans, debt recovery, mortgage, interest", "land ownership, land registration, tenancy of farmland (mohi), land ceiling",
    "neighbour disputes, easements, encroachment, boundaries", "torts, compensation, negligence, damages",
    "criminal law general: murder, hurt, assault, theft, robbery, cheating, fraud", "sexual offences, rape, harassment, child sexual abuse",
    "domestic violence and gender-based violence", "defamation, insult, privacy, cyber crime, online harassment, hacking",
    "criminal procedure: arrest, bail, FIR/first information report, police custody, investigation, trial",
    "civil procedure: filing a suit, court fees, limitation period, appeal, execution of judgment",
    "constitutional rights, writs, fundamental rights, equality, discrimination, citizenship",
    "labour and employment: wages, dismissal, leave, gratuity, provident fund, trade unions, child labour",
    "consumer protection, product quality, price, complaints", "company, business registration, partnership, insolvency",
    "tax: income tax, VAT, customs, excise", "banking, cheques, negotiable instruments, microfinance, cooperatives",
    "corruption, bribery, money laundering", "human trafficking, foreign employment, migration",
    "narcotics, arms, public order", "traffic, vehicles, driving licence, road accidents",
    "local government, ward office, municipality, judicial committee, mediation", "right to information, public service, government employees",
    "children's rights, juvenile justice, education", "health, medical negligence, abortion, disability, senior citizens",
    "environment, forest, water, wildlife", "intellectual property, copyright, trademark, patent",
    "elections, parliament, president, federal/provincial government, judiciary structure",
]

SYSTEM = """You are an expert in Nepali law and legal Nepali. For the given legal area, list \
40-70 entries mapping the words people type to the exact formal terms used in Nepal's statutes \
(Muluki Civil Code 2074, Muluki Criminal Code 2074, Constitution of Nepal, and special Acts). \
Each entry: {"en": [English lay words and legal terms, lowercase, 1-4 words each], \
"roman": [romanised Nepali spellings people type, lowercase, e.g. "gharbeti", "dharauti", "sambandha bichhed"], \
"ne": [the formal Nepali statute terms, most important first, plus common colloquial Devanagari forms]}. \
Be precise: e.g. rape -> "जबरजस्ती करणी", landlord -> "घरधनी", tenant -> "बहालवाला", \
deposit -> "धरौटी", limitation period -> "हदम्याद", partition share -> "अंश", \
bail -> "धरौटी", "जमानत", plaint -> "फिराद", cheating -> "ठगी". Return JSON {"entries": [...]}."""


def main():
    from app import llm

    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"areas": {}}
    for area in AREAS:
        if area in data["areas"]:
            continue
        for attempt in range(4):
            try:
                raw = llm.complete(SYSTEM, f"Legal area: {area}", json_mode=True, max_tokens=6000, temperature=0.2)
                entries = llm.parse_json(raw)["entries"]
                clean = []
                for e in entries:
                    ne = [x.strip() for x in e.get("ne", []) if isinstance(x, str) and x.strip()]
                    en = [x.strip().lower() for x in e.get("en", []) if isinstance(x, str) and x.strip()]
                    ro = [x.strip().lower() for x in e.get("roman", []) if isinstance(x, str) and x.strip()]
                    if ne and (en or ro):
                        clean.append({"en": en, "roman": ro, "ne": ne})
                data["areas"][area] = clean
                with open(OUT, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=0)
                print(f"[glossary] {area}: {len(clean)} entries", file=sys.stderr)
                break
            except Exception as e:  # noqa: BLE001
                print(f"[glossary] {area} attempt {attempt + 1} failed: {str(e)[:150]}", file=sys.stderr)
                time.sleep(30)
        time.sleep(13)  # stay under free-tier requests-per-minute


if __name__ == "__main__":
    main()
