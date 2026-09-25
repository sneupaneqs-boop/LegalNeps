"""
One-off ingestion script: reads real Nepali legal PDFs (constitution, legal
maxims, finance acts) via Gemini's native PDF reading (which renders pages
visually, sidestepping the legacy-font encoding that corrupts naive text
extraction from these documents), and produces clean bilingual corpus
entries appended to backend/app/data/corpus.json.

Run manually: python3 scripts/ingest_pdfs.py
Requires GEMINI_API_KEY in the environment.
"""
import json
import os
import sys
import time

from google import genai

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3.1-flash-lite"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS_PATH = os.path.join(ROOT, "backend", "app", "data", "corpus.json")

client = genai.Client(api_key=API_KEY)

_file_cache = {}


def upload(path: str):
    if path in _file_cache:
        return _file_cache[path]
    f = client.files.upload(file=path)
    while f.state.name == "PROCESSING":
        time.sleep(2)
        f = client.files.get(name=f.name)
    if f.state.name != "ACTIVE":
        raise RuntimeError(f"Upload failed for {path}: {f.state}")
    _file_cache[path] = f
    return f


def ask_json(file_ref, prompt: str, retries: int = 3):
    full_prompt = (
        prompt
        + "\n\nRespond with ONLY a JSON array (no markdown fences, no commentary). "
        "Each item must be a JSON object with exactly these string keys: "
        "id, topic, title_en, title_ne, text_en, text_ne, source_en, source_ne."
    )
    last_err = None
    for attempt in range(retries):
        try:
            r = client.models.generate_content(
                model=MODEL,
                contents=[file_ref, full_prompt],
                config={"temperature": 0.1, "max_output_tokens": 8192},
            )
            text = r.text.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  retry {attempt+1}/{retries} after error: {e}", file=sys.stderr)
            time.sleep(3)
    raise last_err


def load_corpus():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_corpus(entries):
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def add_entries(new_entries, category):
    corpus = load_corpus()
    existing_ids = {e["id"] for e in corpus}
    added = 0
    for e in new_entries:
        e["category"] = category
        if e["id"] in existing_ids:
            e["id"] = f"{e['id']}-{added}"
        corpus.append(e)
        existing_ids.add(e["id"])
        added += 1
    save_corpus(corpus)
    print(f"  added {added} entries (corpus now {len(corpus)} total)")


CONSTITUTION_BATCHES = [
    (
        "preamble-part1",
        "This PDF is the Nepali original text of the Constitution of Nepal "
        "(from lawcommission.gov.np). Its embedded text layer may be garbled "
        "due to a legacy font - read the PDF VISUALLY and transcribe correctly. "
        "Extract the Preamble and Articles 1 through 15 (Part 1: Preliminary). "
        "For each Article, produce one JSON object where id is like "
        "'constitution-art-1', topic is 'Constitution - State' and title/text "
        "are the article heading/full text in Nepali (title_ne/text_ne, correct "
        "Devanagari Unicode) and an accurate English translation (title_en/text_en). "
        "source_en should be 'Constitution of Nepal, Article <N>' and source_ne "
        "the Nepali equivalent 'नेपालको संविधान, धारा <N>'. Treat the Preamble as "
        "id 'constitution-preamble'.",
    ),
    (
        "citizenship-part2",
        "Same PDF, same instructions as before (visual reading, correct Devanagari "
        "Unicode). Extract all Articles in Part 2 (Citizenship), producing one JSON "
        "object per Article the same way, topic 'Constitution - Citizenship', "
        "id like 'constitution-art-<N>'.",
    ),
    (
        "rights-1",
        "Same PDF, same instructions. Part 3 is Fundamental Rights. Extract "
        "Articles 16 through 30 (one JSON object per Article), topic "
        "'Constitution - Fundamental Rights', id like 'constitution-art-<N>'.",
    ),
    (
        "rights-2",
        "Same PDF, same instructions. Part 3 Fundamental Rights continued. "
        "Extract Articles 31 through 46 (one JSON object per Article), topic "
        "'Constitution - Fundamental Rights', id like 'constitution-art-<N>'.",
    ),
    (
        "duties-directive",
        "Same PDF, same instructions. Extract: (a) Article 48 (Fundamental "
        "Duties, if present near Part 3's end or wherever duties are listed), "
        "and (b) 5 of the most practically important Articles from Part 4 "
        "(Directive Principles, Policies and Obligations of the State) that "
        "relate to justice, social security, or legal protection of citizens. "
        "topic 'Constitution - Duties and Directive Principles', id like "
        "'constitution-art-<N>'.",
    ),
    (
        "judiciary",
        "Same PDF, same instructions. Find the Part on the Judiciary "
        "(Supreme Court, courts, judicial system) - extract the 6 most "
        "important Articles about court jurisdiction, the right to "
        "constitutional remedy, and access to justice. topic "
        "'Constitution - Judiciary', id like 'constitution-art-<N>'.",
    ),
]


def ingest_constitution():
    print("=== Constitution ===")
    f = upload(os.path.join(ROOT, "samidhan.pdf"))
    for name, prompt in CONSTITUTION_BATCHES:
        print(f"-- batch: {name}")
        entries = ask_json(f, prompt)
        add_entries(entries, "law")


def ingest_maxims():
    print("=== Legal Maxims ===")
    f = upload(os.path.join(ROOT, "legal Maxims.pdf"))
    prompt = (
        "This PDF is a Nepal Law Commission publication of legal maxims/principles "
        "in Nepali. Its embedded text layer may be garbled due to a legacy font - "
        "read the PDF VISUALLY. Find a representative set of 30 well-known, "
        "practically useful legal maxims from the early-to-middle chapters "
        "(covering things like natural justice, evidence, contracts, and "
        "procedure) and for each produce one JSON object: id like "
        "'maxim-1', 'maxim-2' etc, topic 'Legal Maxim', title_ne = the maxim "
        "itself in Nepali/Latin as written, title_en = the maxim transliterated "
        "or its common English name, text_ne = its meaning/explanation in "
        "Nepali, text_en = its meaning/explanation in English, source_en = "
        "'Nepal Law Commission - Legal Maxims', source_ne = "
        "'नेपाल कानून आयोग - कानूनी उखान/सिद्धान्त'."
    )
    entries = ask_json(f, prompt)
    add_entries(entries, "law")


ACT_FILES = [
    ("आर्थिक विधेयक, २०८३_mqsvmdf.pdf", "Economic Bill, 2083", "आर्थिक विधेयक, २०८३"),
    ("राष्ट्र ऋण उठाउने विधेयक, २०८३_8niazhp.pdf", "National Debt Raising Bill, 2083", "राष्ट्र ऋण उठाउने विधेयक, २०८३"),
    ("विनियोजन ऐन २०८३_kvsnh9e.pdf", "Appropriation Act, 2083", "विनियोजन ऐन २०८३"),
    ("विशेष सेवा ऐन जगाउने ऐन_56k33tm.pdf", "Special Service Act", "विशेष सेवा ऐन"),
    ("वैकल्पिक विकास वित्त परिचालन ऐन,२०८२_6ihxhtm (1).pdf", "Alternative Development Finance Mobilization Act, 2082", "वैकल्पिक विकास वित्त परिचालन ऐन, २०८२"),
]


def ingest_acts():
    print("=== Finance/Government Acts ===")
    for fname, label_en, label_ne in ACT_FILES:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            print(f"  SKIP missing: {fname}")
            continue
        print(f"-- {fname}")
        f = upload(path)
        prompt = (
            f"This PDF is the Nepali original text of the '{label_en}' "
            f"({label_ne}). Its embedded text layer may be garbled due to a "
            "legacy font - read the PDF VISUALLY. Extract: (1) the Act's "
            "overall purpose/preamble as one entry, and (2) up to 5 of its "
            "most substantively important operative sections (दफा) - skip "
            "purely numeric schedules/budget line-item tables. For each "
            "produce one JSON object: id like "
            f"'{label_en.lower().replace(' ', '-').replace(',', '')}-purpose' "
            "or '-section-<N>', topic 'Government/Finance Law', title_ne/"
            "title_en, text_ne/text_en (concise but accurate, 2-5 sentences "
            f"each), source_en = '{label_en}', source_ne = '{label_ne}'."
        )
        try:
            entries = ask_json(f, prompt)
            add_entries(entries, "law")
        except Exception as e:  # noqa: BLE001
            print(f"  FAILED: {e}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("all", "constitution"):
        ingest_constitution()
    if target in ("all", "maxims"):
        ingest_maxims()
    if target in ("all", "acts"):
        ingest_acts()
    print("Done.")
