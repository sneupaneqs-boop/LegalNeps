"""Download the official PDFs that carry prescribed forms (schedules) and dump
their extracted text under sources/formats/ (gitignored).

    python backend/scripts/fetch_formats.py [substring ...]

Polite: one request per second, cached (a PDF already on disk is not
re-fetched). Text extraction reuses scripts/extract_laws.extract_pdf, which
does the Devanagari glyph recovery for Law Commission PDFs.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "sources" / "formats"
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "backend" / "scripts"))

# Acts/rules whose schedules the drafting templates transcribe.
LAWS = [
    "मुलुकी देवानी कार्यविधि नियमावली, २०७५",
    "मुलुकी देवानी कार्यविधि संहिता, २०७४",
    "मुलुकी फौजदारी कार्यविधि नियमावली, २०७५",
    "मुलुकी फौजदारी कार्यविधि संहिता, २०७४",
    "सर्वोच्च अदालत नियमावली, २०७४",
    "उच्च अदालत नियमावली, २०७३",
    "जिल्ला अदालत नियमावली, २०७५",
    "सूचनाको हक सम्बन्धी नियमावली, २०६५",
    "उपभोक्ता संरक्षण नियमावली, २०७६",
    "मेलमिलाप सम्बन्धी नियमावली, २०७०",
    "श्रम नियमावली, २०७५",
    "जन्म, मृत्यु तथा अन्य व्यक्तिगत घटना (दर्ता गर्ने)नियमावली, २०३४",
    "लेख्य प्रमाणक नियमावली, २०४१",
    "वैदेशिक रोजगार नियमावली, २०६४",
    "घरेलु हिंसा (कसूर र सजाय) नियमावली, २०६७",
    "विवाह दर्ता नियमावली, २०२८",
    "मालपोत नियमावली, २०३६",
    "कसूरको अनुसन्धान सम्बन्धी नियमावली, २०७५",
    "कानूनी सहायता सम्बन्धी नियमावली, २०५५",
    "नेपाल नागरिकता ऐन, २०६३",
    "श्रम अदालत नियमावली, २०८०",
]


def slug(title: str) -> str:
    return hashlib.sha1(title.encode()).hexdigest()[:10]


def main() -> None:
    from app.retrieval import get_index

    only = sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    urls: dict[str, str] = {}
    for e in get_index().iter_entries():
        t = e.get("doc_title_ne")
        u = (e.get("url") or "").split("#")[0]
        if t in LAWS and u.startswith("http"):
            urls.setdefault(t, u)
    index_path = OUT / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    for title in LAWS:
        if only and not any(o in title for o in only):
            continue
        url = urls.get(title)
        if not url:
            print("no url in corpus:", title)
            continue
        pdf = OUT / f"{slug(title)}.pdf"
        txt = OUT / f"{slug(title)}.txt"
        if not pdf.exists():
            time.sleep(1.0)
            r = subprocess.run(["curl", "-sSL", "--fail", "-o", str(pdf), url], capture_output=True, text=True)
            if r.returncode:
                print("download failed:", title, r.stderr.strip())
                continue
        if not txt.exists():
            from extract_laws import extract_pdf

            data = extract_pdf(str(pdf))
            txt.write_text(
                "\n".join(f"<<<PAGE {i}>>>\n{p}" for i, p in enumerate(data["pages"], 1)), encoding="utf-8"
            )
        index[title] = {"url": url, "pdf": pdf.name, "txt": txt.name}
        print("ok", title, txt.stat().st_size)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
