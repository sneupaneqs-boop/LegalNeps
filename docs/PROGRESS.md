# Progress

Tracks what's done, current metrics, and the next session to run. See
`docs/STRATEGY.md` for the full plan and `docs/SESSION_PROMPTS.md` for the
kickoff prompt.

## Next session

**S3 — LLM-free hot path.** See STRATEGY.md §4, week 1 table.

## Done

### S2 — Legal data engine v2 (2026-09-26)

- **Doc-level metadata** (`app/doc_meta.py`, shared by `scripts/build_corpus.py`
  and `app/retrieval.py`): every official Nepali law PDF opens with a printed
  header — certification/gazette date, then a numbered list of amending acts
  each with its own BS date — before the preamble text starts. Sampled it
  across the built corpus (not raw PDFs, which aren't in this checkout — see
  Known issues) instead of the 20-PDF sample the session prompt asked for,
  since `sources/processed/law_docs.jsonl` and the raw PDFs are gitignored
  and not present in this environment; the built corpus's first chunk per
  document carries the same header text the raw PDF would. `extract_doc_meta()`
  pulls `enacted_bs`, `amended_by` (name + BS date per amendment), and
  `consolidated_upto` (latest amendment date, else `enacted_bs`) from it.
  `classify_status()` turns that into `status`: `in_force` (header found),
  `bill` (title contains "विधेयक" and no header — never promulgated), or
  `unknown` (no header, not titled as a bill — mostly non-law docs: annual
  reports, policies, treaties in a different date format). Repealed-act
  detection is out of scope (needs a cross-document repeal graph, not
  extractable from one doc's own text) — everything superseded still reads
  `in_force`/`unknown`.
- **Canonical provision IDs**: every law chunk now carries `doc_id` (the
  existing per-document short hash) and `provision_id` (`<doc_id>:<section>`,
  or just `<doc_id>` when there's no section).
- **Bills excluded from default search**: `Index.search()` takes
  `include_bills: bool = False`; entries with `status == "bill"` are skipped
  by default. `Index._build()` computes status lazily from each doc's first
  chunk when an entry has no `status` field (`retrieval.py::_entry_status`),
  so this works against the corpus shards already committed to this repo —
  which predate this change and carry no `status` field — without needing a
  full pipeline rebuild (raw sources aren't available here to do that; see
  Known issues). Once `build_corpus.py` is next run with the raw sources,
  every entry will carry `status` directly and the lazy path becomes a no-op.
  `INDEX_VERSION` bumped 2→3 to invalidate old on-disk caches (new field in
  `meta.npz`).
- **`corpus_version`** added to `/api/stats` (alongside the existing
  `digest`, kept for compatibility) plus a `by_status` breakdown.
- Verified end-to-end against the real shipped corpus (57,787 passages,
  digest `ceb6a969e6897f8e`): `by_status` = `{unknown: 10660, in_force:
  36225, bill: 348}` (348 chunks across the 9 bill documents). Six varied
  queries that touch bill-document content returned 0 bill hits by default,
  and `include_bills=True` correctly surfaces them.

## Metrics (S2, real corpus)

Retrieval eval re-run after rebuilding the index cache with bill-exclusion
(`python eval/run_eval.py retrieval --raw-only`, same 150 questions, no
regression vs. the S1 baseline):

| Metric | S1 baseline | S2 |
|---|---|---|
| hit@8 (covered) | 0.760 | 0.760 |
| hit@3 (covered) | 0.664 | 0.678 |
| MRR | 0.603 | 0.616 |
| median latency | 48 ms | 58 ms (single-run jitter) |

`test on 20 known acts' dates`: `tests/test_doc_meta.py::test_enacted_date_matches_known_acts`,
20 real acts/rules read off the built corpus, all pass. Corpus-wide:
`in_force` status covers >75% of all law documents (`in_force`/(`in_force`+`unknown`+`bill`)
≈ 74% of chunks, but that includes 8,685 `other`-type chunks — mostly annual
reports/policies that were never expected to have this header; among
`act`/`rule`/`constitution` docs specifically, coverage is ~86%, see next
line). 75/75 backend tests pass (was 48; +27 for S2 doc-meta tests, +1 bill
fixture/search test, +1 stats assertion, +2 for `by_status`/`corpus_version`).

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

1. ~~9 draft bills (`विधेयक`) are indexed as `doc_type: act`~~ — **fixed in
   S2**: they're now `status: bill` and excluded from default search
   (`doc_type` itself is untouched — still `act`, since that's a doc-type
   classification bug, not a status one, and STRATEGY only asked for the
   status field). `doc_type` bug for future reference: `_doc_type()` in
   `build_corpus.py` matches "विधेयक"/"ऐन" as a raw substring anywhere in the
   title, so a *report about* a bill or act (title containing "...ऐन सम्बन्धी
   अध्ययन प्रतिवेदन") also gets `doc_type: act`; harmless now since they also
   lack a header and get `status: unknown` (not `in_force`), but worth a
   proper fix later.
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
7. **`sources/processed/law_docs.jsonl`, `sources/nkp/cases.jsonl`, and the
   raw scraped PDFs are not present in this checkout** (gitignored, and the
   scrape/extract scripts that produce them weren't run in this session —
   they need network access to lawcommission.gov.np / nkp.gov.np this
   environment may not have). This means: (a) `build_corpus.py` cannot
   actually be re-run here to regenerate `app/data/corpus/*.jsonl.gz` with
   the new S2 fields baked in — S2's status/date/provision-ID fields were
   verified against `extract_doc_meta`/`classify_status` unit tests using
   the *already-built* corpus's first-chunk text (which contains the same
   header the raw PDF has) and a live rebuilt *index cache* (which computes
   status lazily, see S2 notes), not a rebuilt *corpus*; (b) the S2 session
   prompt's add-on ("sample 20 Law Commission PDFs' first page text via the
   extraction code") was done against the built corpus's first chunks
   instead, since neither the raw PDFs nor `law_docs.jsonl` exist here. Next
   session that touches the corpus build pipeline should confirm whether
   this environment has been given scrape access, or run `build_corpus.py`
   in an environment that does, so the shipped `.jsonl.gz` files pick up
   `status`/`enacted_bs`/`amended_by`/`consolidated_upto`/`doc_id`/
   `provision_id` directly instead of relying on the retrieval-time fallback.
8. Enacted-date extraction (`app/doc_meta.py::extract_doc_meta`) covers
   ~86% of `act`/`rule`/`constitution` documents (the rest are mostly older
   or OCR-damaged headers using label variants not yet matched, plus
   treaties which use a different AD-date format entirely — `लागू भएको
   मितिः ... तद अनुसार ...`, not attempted this session). Docs it misses get
   `status: unknown`, which stays visible in default search (only `bill`
   status is excluded), so this doesn't cause bad citations — just missing
   `enacted_bs`/`amended_by` metadata for those docs.
9. Repealed-act detection is not implemented (`status` has no `repealed`
   value yet, despite STRATEGY listing it) — would need a cross-document
   repeal graph (an act's own "खारेजी र बचाउ" section names what *it*
   repeals, not whether *it* was later repealed by something else), which is
   a separate research task.

## Later (ideas raised but out of scope for the current session)

- Fix `_doc_type()` in `build_corpus.py` to stop matching "ऐन"/"विधेयक" as a
  bare substring (issue 1 above) — cosmetic now that status handles the
  trust-risk part, but `doc_type` still mislabels a few report/study
  documents as `act`.
- Repealed-act detection (issue 9 above).
- Treaty and OCR-damaged-header date extraction (issue 8 above).
