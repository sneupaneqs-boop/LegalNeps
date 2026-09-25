# Kanooni Sathi (कानूनी साथी) — Legal Friend

A bilingual (English / Nepali) AI assistant that helps people understand Nepali
law — starting with civil law — in plain, empathetic language. Inspired by
[Niti](https://github.com/Yunika-Bajracharya/Niti-Legal-Semantic-Search), but
built as retrieval + LLM reasoning (RAG) instead of raw extractive search, so
it can actually understand a person's situation ("my landlord won't return my
deposit") and not just keyword-match legal text.

## How it works

1. **Retrieval** (`backend/app/retrieval.py`) — the user's message is matched
   against a bilingual corpus of law provisions and precedents
   (`backend/app/data/corpus.json`) using TF-IDF similarity, in whichever
   language (English or Nepali) the message was written in.
2. **Generation** (`backend/app/generation.py`) — the top matching passages
   are handed to an LLM (tries Gemini via `GEMINI_API_KEY`, then Groq via
   `GROQ_API_KEY`, then Claude via `ANTHROPIC_API_KEY` — whichever is
   configured) along with a system prompt that instructs it to: understand
   the person's real underlying concern, answer only from the retrieved
   passages (no invented citations), explain things in plain non-legalese
   language, reply in the same language as the question, and always add a
   disclaimer that this isn't a substitute for a licensed advocate.
3. If no LLM key is configured, the backend still works — it falls back to
   showing the raw matched passages directly (extractive mode), so the app
   degrades gracefully instead of breaking.

## About the legal corpus

`backend/app/data/corpus.json` mixes two kinds of entries:

- **Real, sourced entries** (`constitution-*`, `maxim-*`, and the finance/Act
  entries) — extracted from the actual PDFs in `sources/` (Nepal's
  Constitution, a Law Commission legal-maxims volume, and several finance
  Acts, all originally in Nepali with a legacy, non-Unicode font that made
  naive text extraction come out garbled). `backend/scripts/ingest_pdfs.py`
  re-extracts these correctly by having Gemini read the PDF pages visually
  (bypassing the broken font layer) and translate each provision into the
  other language in the same pass. Re-run it (`GEMINI_API_KEY=... python3
  backend/scripts/ingest_pdfs.py [constitution|maxims|acts|all]`) if you add
  more source PDFs to `sources/`.
- **Illustrative demo entries** (`civil-*`, `precedent-*`) — paraphrased
  summaries of civil-law topics (marriage, contracts, tort, etc.) written
  from general knowledge before real source documents were available, kept
  because they cover topics the uploaded PDFs don't. Precedent entries are
  explicitly marked "illustrative summary — verify exact case citation."
  Worth replacing with real Supreme Court (NKP) text over time.

### Corpus format

Each entry in `corpus.json`:

```json
{
  "id": "unique-id",
  "category": "law | precedent",
  "topic": "short topic label",
  "title_en": "...", "title_ne": "...",
  "text_en": "...", "text_ne": "...",
  "source_en": "citation string", "source_ne": "citation string (Nepali)"
}
```

To scale this up to the full Civil Code and NKP case law, the next steps
would be: ingest official PDFs (once the environment's network policy allows
those domains, or by uploading the PDFs directly), chunk them by
section/paragraph, and swap the TF-IDF retriever for a multilingual
embedding model (e.g. `intfloat/multilingual-e5-base`) + a vector index
(FAISS) once the corpus is too large for TF-IDF to work well.

### Bulk-scraping lawcommission.gov.np

`backend/scripts/scrape_lawcommission.py` + `backend/scripts/ingest_scraped.py`
are a two-step pipeline to pull in *every* law/rule/regulation the Law
Commission publishes, not just the handful of seed PDFs above:

```bash
# 1. crawl + download every ऐन/नियमावली/etc. PDF (resumable, polite, rate-limited)
python3 backend/scripts/scrape_lawcommission.py crawl
python3 backend/scripts/scrape_lawcommission.py stats

# 2. (optional) OCR any scanned PDFs that have no text layer at all
#    apt install ocrmypdf tesseract-ocr-nep tesseract-ocr-eng
python3 backend/scripts/scrape_lawcommission.py ocr

# 3. turn the downloaded PDFs into corpus.json entries (visual Gemini read,
#    same technique as ingest_pdfs.py, so it copes with the legacy font)
GEMINI_API_KEY=... python3 backend/scripts/ingest_scraped.py
```

Both scripts are resumable/idempotent: re-running `crawl` skips URLs already
in `sources/lawcommission/manifest.jsonl`, and re-running `ingest_scraped.py`
skips documents already recorded in `sources/lawcommission/ingested.json`.
Downloaded PDFs live under `sources/lawcommission/<category>/` and are
gitignored (large binary dump) — only the resulting `corpus.json` entries get
committed.

**Precedents/case law**: lawcommission.gov.np publishes legislation, not
Supreme Court judgments — those are published separately as NKP (Nepal
Kanoon Patrika) by the Supreme Court (supremecourt.gov.np). Pass
`--extra-domain supremecourt.gov.np --seed https://supremecourt.gov.np/...`
to the crawler to pull those in too once you've confirmed the site's actual
listing URLs.

**Network note**: this sandboxed session's egress proxy blocks
`lawcommission.gov.np` outright (policy denial, confirmed via both `curl`
and `WebFetch`), so the crawl could be written but not run from here. Run it
from an environment with unrestricted internet access (your own machine, or
a Claude Code on the web environment configured to allow that host).

## Running it locally

### Backend (FastAPI)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add GEMINI_API_KEY (or GROQ_API_KEY / ANTHROPIC_API_KEY)
uvicorn app.main:app --reload --port 8000
```

Without any LLM key set, `/api/chat` still works in extractive fallback
mode — useful for testing retrieval without API cost.

### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # points at the backend URL
npm run dev
```

Open http://localhost:3000. Use the language toggle in the top-right to
switch the whole UI (and the assistant's replies) between English and
Nepali.

## API

`POST /api/chat`

```json
{ "message": "my landlord won't return my rent deposit", "language": "auto" }
```

`language` is `"en"`, `"ne"`, or `"auto"` (detects Devanagari script).

Response:

```json
{
  "answer": "...",
  "language": "en",
  "sources": [{ "id": "...", "title": "...", "citation": "...", "snippet": "...", "score": 0.4 }],
  "llm_used": true
}
```

## Project structure

```
backend/
  app/
    main.py            FastAPI app + CORS
    routes/chat.py      POST /api/chat
    retrieval.py         TF-IDF retrieval over the bilingual corpus
    generation.py        Gemini/Groq/Claude prompt + extractive fallback
    data/corpus.json     the legal corpus (see caveat above)
  scripts/ingest_pdfs.py re-extracts sources/*.pdf into corpus.json via Gemini
sources/                 original source PDFs (Constitution, legal maxims, Acts)
frontend/
  app/page.tsx           chat UI, language toggle
  components/ChatMessage.tsx
  lib/api.ts             backend client
  lib/i18n.ts             English/Nepali UI strings
```

## Disclaimer

This app provides general legal information for educational purposes. It is
not a substitute for advice from a licensed Nepali advocate, and the demo
corpus has not been independently verified against official sources.
