# Progress

Tracks what's done, current metrics, and the next session to run. See
`docs/STRATEGY.md` for the full plan and `docs/SESSION_PROMPTS.md` for the
kickoff prompt.

## Next session

**S3 — LLM-free hot path.** See STRATEGY.md §4, week 1 table.

## Done

### S1 — Baseline + CI (2026-09-26)

- **Fixed the fresh-install blocker.** `backend/requirements.txt` pinned
  `pydantic==2.10.3`, which conflicts with `google-genai==2.25.0` (needs
  `pydantic>=2.12.5`) — confirmed with a clean-venv install
  (`ResolutionImpossible`). Changed to `pydantic>=2.12.5`; a clean install of
  `requirements-scripts.txt` (app + scripts deps together) now succeeds and
  resolves pydantic 2.13.5.
- **CI**: `.github/workflows/ci.yml` — two jobs, `backend` (installs
  `requirements-scripts.txt`, runs `pytest`) and `frontend` (`npm ci`,
  `npm run build`), on push to `main` and on every PR.
- **Structured request log**: every `/api/chat` and `/api/chat/stream`
  request logs one JSON line (`kanooni.request` logger) with `llm_calls`
  (count of pipeline-stage LLM calls — analyze + answer, not per-provider
  retries), `tier` (always `"free"` until S13 adds paid tiers), `latency_ms`,
  `cache_hit`, `llm_used`, `language`. Implementation: `generation.py::run()`
  counts the two pipeline stages itself and puts `llm_calls` in the `"done"`
  event, threaded through `answer_question()`; `routes/chat.py::_log_request`
  reads it from the result. (First attempt used a `contextvars.ContextVar` in
  `llm.py`, reset per request — verified broken for the streaming endpoint:
  Starlette's `iterate_in_threadpool` copies context fresh on every `next()`
  call across the thread pool, so mutations made mid-stream don't survive to
  the next chunk. A plain counter local to the `run()` generator frame does
  survive suspension/resumption regardless of thread, so that's what's used.)
- **Baseline eval recorded** (see Metrics below).

## Metrics (baseline, S1)

Recorded 2026-09-26 against corpus `manifest.digest = ceb6a969e6897f8e`
(57,787 passages). No LLM provider keys are configured in this environment,
so retrieval was measured in **raw-query mode only** (no query-understanding
rewrite) — this is the floor the LLM-assisted mode builds on, not the
production number reported to users.

Retrieval (`python eval/run_eval.py retrieval --raw-only`, 150 hand-written
questions, top_k=8):

| Metric | Value |
|---|---|
| hit@8 (covered) | 0.760 |
| hit@3 (covered) | 0.664 |
| MRR | 0.603 |
| median latency | 48 ms |
| with_precedent | 0.973 |
| coverage gaps (expected law entirely absent from corpus) | 3 (राष्ट्रिय निकुञ्ज तथा वन्यजन्तु संरक्षण, लागु औषध, स्थानीय सरकार सञ्चालन) |

35/150 questions missed in raw mode (see `eval/reports/retrieval-*.json` —
gitignored, regenerate locally). This is the number S3 needs to raise via the
query-understanding path (`app/generation.analyze_query` → LLM query
rewrite), which is not exercised here without keys.

**% of requests that make an LLM call:** not measured live (no keys), but
structural per `app/generation.py::run`: a "legal"-intent message always
makes exactly 2 calls (`analyze_query` then the answer `stream`/`complete`);
`greeting`/`thanks`/`off_topic`/`unclear` (recognised by `quick_intent()` or
the analysis classification) make 0 or 1. There is currently no path that
answers a legal question with 0 LLM calls — that's S3's target (glossary-only
confident match skips `analyze_query`; playbook matcher in S6/S7 skips both).

Tests: 48 passed (`backend/tests`, includes `test_extract`, `test_nkp_parser`,
`test_glyph_order` now that CI installs `requirements-scripts.txt`).
Frontend: `next build` succeeds.

## Known issues

1. 9 draft bills (`विधेयक`) are indexed as `doc_type: act` — the app can cite
   a law that was never passed. No doc has a status, enactment date, or
   amendment list. **Biggest trust risk — S2.**
2. 8,685 chunks are `doc_type: other` (annual reports etc.), down-weighted
   but still in the default search.
3. 20 MB corpus + 23 MB of source PDFs are committed to git (acceptable for
   now; avoid reading them directly in-session — go through the extraction
   code instead).
4. No rate limiting on `/api/chat` — one caller in a loop can exhaust every
   free-tier key.
5. In-memory LRU caches (`_analysis_cache`, `_answer_cache` in
   `generation.py`) are lost on every restart/deploy and aren't keyed by
   `corpus_version` — S5 replaces this with the persistent Supabase cache.
6. No LLM provider keys are configured in this build environment, so the
   query-understanding retrieval mode, the answer-generation path, and the
   "% queries with an LLM call" metric could not be measured live this
   session — only the structural facts above. Re-run
   `python eval/run_eval.py retrieval` (without `--raw-only`) once keys are
   available to get real llm-mode numbers.

## Later (ideas raised but out of scope for the current session)

- (none yet)
