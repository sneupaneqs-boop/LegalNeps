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
   are handed to Claude (Anthropic API) along with a system prompt that
   instructs it to: understand the person's real underlying concern, answer
   only from the retrieved passages (no invented citations), explain things
   in plain non-legalese language, reply in the same language as the question,
   and always add a disclaimer that this isn't a substitute for a licensed
   advocate.
3. If no `ANTHROPIC_API_KEY` is configured, the backend still works — it
   falls back to showing the raw matched passages directly (extractive mode),
   so the app degrades gracefully instead of breaking.

## ⚠️ About the legal corpus (read this)

This environment's network access could not reach the Nepal Law Commission
(`lawcommission.gov.np`) or Supreme Court (`nkp.gov.np`) sites to pull the
verbatim official text. `backend/app/data/corpus.json` currently contains a
**curated demo corpus**: paraphrased summaries of well-known National Civil
Code, 2074 (2017) provisions and a few landmark Supreme Court precedents,
written from general knowledge for testing purposes only. Every entry is
labeled with a citation, and precedent entries are explicitly marked
"illustrative summary — verify exact case citation."

**Before using this for anything real:** replace `corpus.json` with actual
text sourced from the official Nepal Law Commission and Supreme Court (NKP)
publications. The retrieval/generation pipeline works with any corpus in the
same shape — see the schema at the top of this README's "Corpus format"
section below.

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

## Running it locally

### Backend (FastAPI)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

Without `ANTHROPIC_API_KEY` set, `/api/chat` still works in extractive
fallback mode — useful for testing retrieval without API cost.

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
    generation.py        Claude prompt + extractive fallback
    data/corpus.json     the legal corpus (see caveat above)
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
