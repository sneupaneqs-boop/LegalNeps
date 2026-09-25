# Kanooni Sathi (कानूनी साथी) — Legal Friend

A bilingual (English / Nepali) assistant that answers questions about Nepali
law in plain language, grounded **only in official government sources**:

- **Laws** — every Act, Code, Regulation, Order, policy and treaty published by
  the Nepal Law Commission (lawcommission.gov.np), split into sections (दफा /
  धारा / नियम).
- **Precedents** — Supreme Court decisions from the official Nepal Kanoon
  Patrika (nkp.gov.np): headnotes, laws applied, precedents relied on.

Every answer cites numbered sources that link to the exact PDF page or court
decision. Questions can be in English, Nepali or romanised Nepali
("gharbeti le deposit firta diyena").

## How it works

1. **Understand** — a cheap/fast LLM tier rewrites the question into formal
   Nepali legal search terms and likely statutes (statutes exist only in
   Nepali, so this is what lets English questions find them). A built-in
   glossary does the same offline, so search keeps working with no LLM.
2. **Retrieve** — BM25 over Nepali-normalised tokens (digit/vowel-length
   folding, postposition stripping), several weighted phrasings fused,
   authority priors (Constitution/Acts above reports), duplicates collapsed.
   Laws and precedents are retrieved separately. <1 ms per query.
3. **Answer** — the stronger LLM tier writes a plain-language answer using only
   the retrieved passages, citing them as [1], [2]…, streamed to the browser.
4. **Never hangs** — every LLM call has a time budget (8 s to understand, 30 s
   for the answer to start). If no model responds, the app returns the matching
   official provisions instead.

## LLM providers (tried in order)

| Provider | Env vars | Notes |
|---|---|---|
| Any OpenAI-compatible gateway, e.g. **[OmniRoute](https://github.com/diegosouzapw/OmniRoute)** | `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODELS` (default `auto`), `OPENAI_FAST_MODELS` (default `auto/fast`) | One endpoint that routes across all the providers you connect in OmniRoute, with fallback and quota tracking |
| Google Gemini | `GEMINI_API_KEY`, optional `GEMINI_MODELS` / `GEMINI_FAST_MODELS` | Walks a chain of models; the free tier allows only ~20 requests/day per full "flash" model, lite models allow more |
| Anthropic | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | |
| Groq | `GROQ_API_KEY`, `GROQ_MODEL` | |

### Using OmniRoute for more free capacity

OmniRoute is a self-hosted gateway: you connect your own API keys for
providers with free tiers (Gemini, Groq, Mistral, OpenRouter, Cerebras, …) in
its dashboard, and it routes each request to whichever has quota left.

```bash
npx omniroute            # dashboard + API on http://localhost:20128
# connect providers in the dashboard, create an API key, then:
export OPENAI_BASE_URL=http://localhost:20128/v1
export OPENAI_API_KEY=<key from the OmniRoute dashboard>
```

Only connect providers through their official API keys. OmniRoute's own
terms-risk catalog marks some providers "avoid" (they scrape consumer chat
websites or reuse subscription logins) — don't enable those for a public app.

## Running it locally

### Backend (FastAPI)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY and/or OPENAI_BASE_URL (OmniRoute) etc.
uvicorn app.main:app --port 8000
```

The first start compiles the corpus into a search index under
`app/data/index_cache/` (about a minute); later starts take under a second.

### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## API

- `POST /api/chat/stream` — `{"message": "...", "language": "auto"|"en"|"ne"}` →
  NDJSON: `{"type":"meta","sources":[...]}`, then `{"type":"delta","text":...}`…,
  then `{"type":"done","answer":...,"llm_used":bool}`.
- `POST /api/chat` — same input, one JSON response.
- `GET /api/search?q=...&category=law|precedent&k=10` — search only.
- `GET /api/stats` — corpus counts.

## Rebuilding the corpus

```bash
pip install -r backend/requirements-scripts.txt
python3 backend/scripts/scrape_lawcommission.py crawl   # resumable; honours robots.txt crawl-delay
python3 backend/scripts/scrape_nkp.py                   # Supreme Court precedents
python3 backend/scripts/extract_laws.py                 # PDF -> clean section chunks
GEMINI_API_KEY=... python3 backend/scripts/ocr_gemini.py   # scanned / broken PDFs only
GEMINI_API_KEY=... python3 backend/scripts/build_corpus.py # -> backend/app/data/corpus/*.jsonl.gz
```

Extraction needs no LLM for almost all documents: legacy fonts (Preeti,
Kantipur, PCS Nepali…) are converted per text span, and Kalimati PDFs with
broken Unicode maps (e.g. "मममि" for "मिति") are decoded from the font's own
glyph outlines. Documents whose text layer still isn't real Nepali are flagged
and transcribed with Gemini vision.

## Tests and evaluation

```bash
cd backend
python3 -m pytest -q                                # unit + API tests (no LLM calls)
python3 eval/run_eval.py retrieval                  # 150 hand-written questions (en / ne / romanised)
python3 eval/run_eval.py synth-gen && python3 eval/run_eval.py synth   # questions generated from real provisions
python3 eval/run_eval.py e2e --n 15                 # full answers graded for grounding
```

## Project structure

```
backend/app/        FastAPI app: retrieval.py (BM25 + passage store), generation.py
                    (understand -> search -> answer), llm.py (providers, tiers,
                    time budgets), glossary.py, text_norm.py
backend/app/data/   corpus shards + glossary (built by the scripts)
backend/scripts/    scrapers, PDF extraction, OCR, corpus/glossary builders
backend/eval/       evaluation questions and harness
backend/tests/      pytest suite
frontend/           Next.js chat UI (streaming, clickable citations, EN/NE)
```

## Disclaimer

General legal information for educational purposes, not a substitute for a
licensed Nepali advocate. Always check the linked official source.
