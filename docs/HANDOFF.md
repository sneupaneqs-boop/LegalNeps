# Kanooni Sathi — Hand-off for the next Claude session

Written 2026-10-02 at the end of a very long session. Read this file first, then `docs/PROGRESS.md`
(newest entries are at the top of "## Done") and `docs/STRATEGY_V2.md` (the plan). Everything below
is what was actually built and measured; numbers are quoted from review files that are committed in
`backend/eval/reports/` or recorded in `docs/PROGRESS.md`. Where something was not verified, it says so.

---------------------------------------------------------------------------------------------------

## 0. TL;DR

* **What it is:** a bilingual (Nepali/English) legal-information web app for Nepal. Chat answers
  questions from a corpus of ~73,667 passages of official Nepali law, plus drafting (44 court/office
  templates), calculators/limitation periods (229), contract audit, matters workspace, compliance reminders.
* **Stack:** FastAPI backend on Render (free tier) · Next.js 15 / React 19 frontend on Vercel ·
  Supabase (Postgres, Auth, Storage, RLS). Search = custom Nepali BM25 + int8 e5-small dense vectors, fused.
* **State:** everything is deployed and working end-to-end EXCEPT sign-in (needs a dashboard setting only the
  founder can change, §9). Backend tests: **1,844 passing**. Production branch: `claude/dreamy-hawking-4y5lgf`.
* **The unsolved problem is answer accuracy.** Every shown quote is real and word-for-word (0 invented
  numbers/sections in every review), but a large share of sentences cite a real provision that does NOT govern
  the user's situation ("wrong-law"). Last live review (fresh 30 questions, set C): **25% bad sentences
  (6/24, 95% CI 12–45%)**, only **1/30** answers fully correct and useful, **6 of 7 refusals wrong**. Target was
  <5%. Rules + free LLMs have plateaued (§7, §8). Recommended route: advocate-reviewed answer bank for the
  ~150 most common situations + a stronger judge model for paid users (§10).
* **Do NOT market answers as "verified correct".** The UI evidence box now says quotes match the law word for
  word and that applicability is NOT checked. Keep that.
* **Money/ops constraint:** founder is in Nepal and cannot pay foreign providers (no Render paid plan, no
  cards). Everything must run on free tiers. The Claude account behind the sub-agents hit its monthly spend
  limit at the end of this session (no more agent runs until it resets / is raised).

---------------------------------------------------------------------------------------------------

## 1. Product, user, constraints

* Founder (email in session context) runs this as a startup in Nepal. Pricing plan: Pro Rs 1,499/mo, Business
  Rs 3,999/mo (see `docs/STRATEGY_V2.md`). No revenue yet.
* **User preferences (follow them):** no generic advice; don't repeat the question back; don't hedge with
  "it depends" — give a recommendation and say why; never answer "I cannot do that"; use the cheaper model
  (Sonnet) for normal work and sub-agents, Opus only when really necessary; keep it simple (user is not a
  native English speaker).
* **Honesty rule (important):** report numbers as measured, say plainly when a target is missed. This session's
  worst failure mode was celebrating tuned-set numbers; the fresh-set reviews corrected that every time.
* Git: develop on `claude/dreamy-hawking-4y5lgf`, commit with a clear message, push with `git push -u origin
  <branch>`; commit footer lines are given by the harness reminders (Co-Authored-By / Claude-Session). Do not open
  PRs unless asked. After any code change run `graphify update .` (CLAUDE.md rule) — it regenerates
  `graphify-out/`; on merge conflicts in `graphify-out/` take "ours".

---------------------------------------------------------------------------------------------------

## 2. Deployment & infrastructure (where things run)

| Thing | Value |
|---|---|
| Frontend (prod alias) | https://kanooni-sathi.vercel.app (Vercel project `kanooni-sathi`, id `prj_o0efSCNwdWR5ed4FJV6Eq1tY1ADc`, team slug `mocklyy`) |
| Backend API | https://kanooni-sathi-api.onrender.com (Render service `srv-dat9vhrtqb8s73ac7lf0`, workspace `tea-d7rf24ugvqtc73bf39ig`, region Oregon, **free plan: 512 MB RAM, 0.1 CPU, sleeps after 15 min idle, first request after sleep ≈ 30–60 s**) |
| Supabase | project id `agzvhessbwwhectuizko` (free tier: 500 MB DB — using ~13 MB; 1 GB storage — using 0; **no automated backups on free tier**) |
| Auto-deploy branch | both Render and Vercel build from `claude/dreamy-hawking-4y5lgf` on every push |
| Vercel production | pushes create PREVIEW deployments; promote one to production with the Vercel MCP `create_deployment` (`requestBody: {name:"kanooni-sathi", deploymentId:"<preview id>", target:"production"}`) |
| Render build command | `cd backend && pip install -r requirements.txt && python scripts/prebuild_index.py` (founder set this; it builds the search index, downloads + prunes the e5-small ONNX model, builds the heading cache, at build time) |
| Python on Render | pinned **3.11.9** via root `.python-version`. Render IGNORES `backend/runtime.txt`. Render defaulted to 3.14 once and numpy had no wheel → BM25 silently returned zero hits for a day. Never remove `.python-version`. |
| Memory | live RSS ≈ 390 MB of 512 MB with dense search loaded. `DENSE=0` env var is the kill switch (≈ 200 MB, keyword-only). |
| Docker (untested here) | `backend/Dockerfile`, `docker-compose.yml`, guide `docs/SELF_HOSTING.md`: run the API on the founder's own computer + Tailscale Funnel/Cloudflare tunnel; Docker daemon was not available in the sandbox so the image was never built here. |

Tools in the Claude session that manage these: Render MCP (`list_deploys`, `list_logs`, `update_environment_variables`
— pass `workspaceId`), Vercel MCP (`list_deployments`, `get_deployment`, `create_deployment`), Supabase MCP
(`execute_sql`, `query_logs`, `apply_migration`). Updating a Render env var triggers a redeploy.

Env vars (backend; names come from `backend/app/config.py`, example in `backend/.env.example`):
LLM keys: `GROQ_API_KEYS`/`GROQ_API_KEY`, `GEMINI_API_KEYS`/`GEMINI_API_KEY`, `OPENROUTER_API_KEYS`,
`CEREBRAS_API_KEYS`, `MISTRAL_API_KEYS`, `COHERE_API_KEYS`, `ANTHROPIC_API_KEY` (paid tiers). Supabase:
`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`. CORS: `CORS_ORIGINS`, `CORS_ORIGIN_REGEX`. Email: `RESEND_API_KEY`.
Quotas: `DAILY_QUOTA_FREE/INDIVIDUAL/PROFESSIONAL/FIRM`, `IP_RATE_LIMIT_PER_HOUR`.
Feature switches (all documented in code comments): `DENSE`, `RETRIEVAL_MODE`, `ENTAILMENT_CHECK` (**default 0 — see §7**),
`STREAM_VERIFIED`, `STREAM_MIN_RULES`, `FIT_GATE`, `FIT_MIN_ONTOPIC`, `FIT_ABSTAIN_STRICT`, `FIT_FORM_FILTER`,
`FIT_USE_DENSE`, `GUARDS_V27`, `CONDITION_CHECKS`, `SECTION_ROUTES`, `TRAILING_PROVISO_CHECK`, `DEBUG_ANSWERS`
(logs the start of raw model replies when an answer falls back — set to 1 only briefly for diagnosis, it logs
user-influenced text; currently 0 on Render). Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, anon key
(the CSP in `frontend/next.config.js` is built from these at BUILD time; changing the API URL needs a rebuild).

Currently only **Groq** (2 keys, same org → one shared rate-limit pool) and **Gemini** (2 keys) are configured as
free LLM providers. That is the main reliability limit (§7).

---------------------------------------------------------------------------------------------------

## 3. Repo map (where to find things)

```
CLAUDE.md                     project rules (graphify + pointers to the plan)
docs/PROGRESS.md              chronological log; newest at top of "## Done"; "Next session" near the top
docs/STRATEGY_V2.md           the current plan (milestones V1–V22). STRATEGY.md = old S1–S15 plan (history)
docs/SESSION_PROMPTS_V2.md    kickoff prompt + per-session add-ons for the V2 plan
docs/PLAYBOOK_AUDIT.md        every curated playbook + NEEDS-ADVOCATE-REVIEW items (64 + ~25 newer rows)
docs/SELF_HOSTING.md          Docker-on-own-computer guide (untested)
backend/app/main.py           FastAPI app, security headers, size limit, routers
backend/app/routes/           chat.py (chat/stream, search, law browser, playbooks, drafting, calculators, matters, research, tools…), documents.py, tools.py
backend/app/generation.py     THE chat pipeline (analysis → query building → search → playbook pin → gates → LLM → verify → stream)
backend/app/retrieval.py      BM25 index (SQLite + npz cache), status/temporal logic, hybrid fusion with dense, heading signal
backend/app/dense.py          e5-small int8 ONNX query encoder + vectors (app/data/dense/vectors.npz, 26 MB, committed)
backend/app/structured.py     structured-answer prompt (JSON), tolerant/incremental parsing, render, entailment (off), build()
backend/app/verifier.py       deterministic verification: old verify() (prose) + verify_structured / verify_sentence
backend/app/claim_checks.py   number-role binding, fuzzy quote rules, orphan connectives, duplicates, precedent gates, uncited-forum rule
backend/app/condition_checks.py  dropped-condition checks (time limits, leading cross-refs, alternative branches…)
backend/app/situation_guards.py  actor/population/regime guards as DATA (bank vs private creditor, school vs college, public vs private company…)
backend/app/topical_fit.py    V3.3 topical-fit gate (specialist-regime table does the real work) + data/topical_fit.json
backend/app/fit_reply.py      abstain reply, topical extractive fallback, display ordering
backend/app/section_routes.py + data/section_routes.yaml   14 hand-verified keyword→section routes
backend/app/translit.py       romanised/English/Devanagari concept lexicon (≈116 + ≈25 + Devanagari rows), vocab-validated
backend/app/glossary.py + data/glossary.json   English/romanised → Nepali legal term expansion
backend/app/playbook_matcher.py, playbooks.py, data/playbooks/*.yaml   37 curated action plans ("playbooks")
backend/app/drafting/         44 templates (22 official schedule forms + 22 standard), DOCX + PDF renderers, fonts
backend/app/calculators/      limitation, labour, court fee, interest, tax, BS dates; data/limitation_periods.yaml (229 entries)
backend/app/documents/        contract-audit (Document AI) + data/contract_checklists/
backend/app/compliance.py     compliance radar (obligations by company profile)
backend/app/llm.py, tiers.py  provider chain (free), paid tiers (Haiku 4.5 chat / Sonnet 5.5 drafting), cost ledger, budgets
backend/app/supa.py           Supabase REST client, answer cache (key must not contain NUL), safe_filename, audit log
backend/app/data/corpus/      part-000..003.jsonl.gz + manifest.json (73,667 passages; part-002 regulators; part-003 OCR'd)
backend/app/data/index_cache/ built index (gitignored); dense_model/ downloaded at build (gitignored)
backend/scripts/              prebuild_index.py, build_dense.py (regen vectors after corpus change, ~27 min), scrape_*.py, ingest_*.py, ocr_*.py
backend/eval/                 run_eval.py (retrieval sets), answer_review.py (live answers → review JSON), question sets, reports/
backend/tests/                1,844 tests (pytest)
frontend/app/                 Next.js routes: / (chat), search, law/[slug]/[section], draft, matters, saved, tools, compliance, audit, account, action-plans
frontend/components/ChatMessage.tsx + chat-extras.css   answer UI (plan card, fact chips, Evidence box, source cards)
frontend/lib/                 api.ts (stream client), drafting.ts, documents.ts, i18n*.ts, supabase.ts, preeti.ts
sources/                      scraped raw sources (mostly gitignored); sources/regulators/*/manifest.jsonl, ingest_report.json
graphify-out/                 generated knowledge graph (do not edit by hand)
```

---------------------------------------------------------------------------------------------------

## 4. Corpus and search (what's in the data)

* **Corpus:** 73,667 passages: constitution 356, acts 21.8k, rules 19.3k, directives 11.1k, treaties 940, orders 480,
  precedents 10.5k (Supreme Court), "other" 9.1k (reports, dictionaries). Law-document count ≈ 982.
  Shards: part-000/001 (Law Commission + NKP precedents), part-002 (regulators: NRB, IRD, SEBON, Company Registrar,
  Law-Commission gap acts; 14,002 chunks), part-003 (1,878 passages, 1,404 OCR'd with Tesseract nep+eng + NIA/MoLESS).
  Passages carry `status` (in_force / bill / lapsed / ordinance / unknown); bills and lapsed ordinances are excluded
  from search; `INDEX_VERSION = 5` + corpus digest key the caches.
* **Not ingested / known gaps:** Nepal Gazette (rajpatra) unreachable from the sandbox; one unreadable NIA scan;
  English-only NRB AML/CFT directives skipped by policy (OCR text cached, re-ingest with `--profile full`); some
  statutes simply absent (e.g. a deposit-refund rule for tenancy; Civil Code has no will chapter in the corpus).
  Nepal Citizenship Rules not in corpus (so no citizenship-application draft).
* **Search = BM25 (custom Nepali tokenizer/stemmer in `text_norm.py`) + e5-small dense, RRF-fused.** Weighted queries:
  LLM-rewritten Nepali phrasings (weight 1.0), lexicon expansion, glossary, raw message. Filters after fusion: category,
  status, per-doc cap (3), dedupe by text hash. Extras: regulator/authority topic filters (NRB/SEBON/OCR/PPMO/NIA/MoLESS
  passages only for banking/securities/company/procurement/insurance/labour questions; IRD only for tax questions),
  fiscal-domain filter, stale-precedent flagging, heading-coverage boost (cache `<digest>-v5.aux1.npz`, 4 MB, built from
  SQLite on first call and at prebuild), section routes, playbook pins.
* **Playbooks** (`data/playbooks/*.yaml`, 37): curated situation → provisions + forum + steps. A confident match pins
  its provisions at the top; they can `exclude_provisions` and use `entry_title_contains` pins. Matching: exact
  phrase hits add up, partial hits count once; relevance gate drops an unconfirmed plan; `not_keywords` vetoes.
  All 37 are flagged for advocate review in `docs/PLAYBOOK_AUDIT.md` — none was reviewed by a lawyer.
* **Regenerating after a corpus change:** `cd backend && python scripts/build_corpus.py` (deletes shards! re-run
  `ingest_regulators.py`/`ocr_regulators.py ingest` after), then `python scripts/build_dense.py` (~27 min, resumable) and
  commit `app/data/dense/vectors.npz`; digest mismatch → vectors reused by id, missing ones BM25-only (logged).

---------------------------------------------------------------------------------------------------

## 5. The chat pipeline step by step (`backend/app/generation.py` → `run()`)

1. Cache lookup (in-memory + Supabase `answer_cache`). Key = `PIPELINE_VERSION|corpus digest|lang|normalised message`.
   `PIPELINE_VERSION` (now `p12-<fingerprint>`) auto-includes a hash of the prompts, lexicon, verifier, structured,
   topical-fit files and all playbooks, so stale cached answers retire themselves. (Past bug: key contained `\x00`, which
   Postgres rejects → no answer was ever cached; also stale answers survived pipeline changes.)
2. `analyze_query`: for any non-Devanagari message the LLM (fast tier) rewrites to formal Nepali search phrases +
   names laws; clear Devanagari questions skip the LLM; follow-ups always go through it. Deterministic fallback = romanised
   lexicon (`translit.py`). Intent shortcuts (greeting etc.).
3. `build_queries` → `search()` (hybrid) → playbook match (`_match_playbook`/`_playbook_id_for`, relevance gate) → pinned
   provisions + routed sections → precedents (flag stale).
4. **V3.3 topical-fit gate** (`apply_topical_gate`): marks off-topic passages (specialist regimes the question doesn't
   mention, forms/schedules, etc.); abstain if < `FIT_MIN_ONTOPIC` on-topic statutes and nothing pinned.
5. Structured generation: ONE JSON object (blocks → sentences with `kind` and `cites:[{n, quote}]`, plus `gaps`,
   `follow_up_questions`). Free chain via `llm.py` (streamed JSON, tolerant parser); paid tiers via Anthropic.
6. **Verify each sentence deterministically** (`verifier.py`, `claim_checks.py`, `condition_checks.py`,
   `situation_guards.py`): quote must be verbatim in the cited passage (OCR-fuzzy only for `ocr:true` chunks); every
   number/unit/section must be in the quote (Nepali/English number words 1–100, lakh/crore handled); lexical overlap; status
   (repealed/lapsed/bill/stale); precedent rules; uncited forum/procedure claims; dropped conditions/provisos; regime/actor
   guards; duplicates/orphan connectives. Failing sentences are REMOVED, empty headings dropped.
7. Fewer than 2 verified rule/deadline/penalty sentences → fallback: topical extractive list (or abstain reply).
   Streaming: sentences are verified as they complete and released after `STREAM_MIN_RULES` verified; end-of-stream `build()`
   is authoritative → `replace` event if the final text differs. Events: `meta → status? → delta* → replace? → delta* → done`.
8. Frontend (`ChatMessage.tsx`): plan card, fact chips, source cards with status badges, Evidence box (quotes match word for
   word; applicability NOT checked), "checking sources…" state.

Parser lesson: free models sometimes emit JSON whose keys turn into loose strings after the first block; the lenient parser
used to keep only the empathy line (24/30 answers fell back). `structured._loose_blocks` now recovers intact sentence objects.

---------------------------------------------------------------------------------------------------

## 6. What works (verified)

* **Deployment & infra:** frontend + backend + Supabase live; all routes 200; CSP/security headers; storage keys server-generated
  (filename traversal fixed); private endpoints 401 without token; `Cache-Control: no-store` on private paths.
* **Search/retrieval (raw path, no LLM rewrite; hit@8 = right law in top 8):** default 150-question tuning set 0.760 →
  **0.952**; realworld-30 0.70 → 1.0; held-out-50 0.76 → **0.82** (section hit@8 0.58, hit@3 0.34). Live held-out through the
  real LLM-rewrite path (measured once, 2026-09-30, before V2.5): hit@8 **0.84**, hit@3 0.76. Search p50 ≈ 90 ms warm.
* **Zero invented numbers/sections** in every claim-by-claim review (V3, V3.2, V3.3, V2.7); 0 uncited numbers in any rendered answer.
* **Quote/number/section/status verification** is solid and deterministic (hundreds of tests).
* **Drafting:** 44 templates, DOCX + PDF (Kalimati/Noto Sans Devanagari), all 176 renders (44×ne/en×docx/pdf) returned 200;
  22 are official schedule forms from the law (source law + schedule printed in the UI), 22 labelled "standard format".
* **Tools:** 229 limitation periods (each period phrase asserted against the section text by tests; 17 flagged
  `needs_review`), labour (overtime/leave/gratuity/notice/festival), interest cap, tax slabs/TDS, court fee, BS date maths
  (months counted as BS months per Civil Procedure Code s.62); invalid input → 4xx not 500.
* **Contract audit (Document AI):** endpoints/UI exist, 401 without token; never tested with a real LLM or a real login.
* **Answer cache** now actually writes to Supabase; **security** items from S14.
* **Good live answers exist** (stolen-phone FIR refusal, RTI timelines, lease termination notice, dowry harassment,
  cheque-bounce deadlines, Foreign Employment refund) — see `backend/eval/reports/answer-review-*-labels-*.json` for verbatim bests.

---------------------------------------------------------------------------------------------------

## 7. What did NOT work / lessons learned (read before trying again)

**Accuracy (the big one)**
* Claim-level history (reviewer = a Sonnet agent labelling every shown sentence supported/unsupported/wrong-law/
  hallucinated against the cited passage; single reviewer, wide CIs):
  V1 prose answers 40.3% (48/119) → V3 structured 15.6% (12/77 — but the checks were then tuned on exactly those 12, so
  that number is not generalisable) → V3.2 fresh set A 44.3% (31/70) → V3.3+V2.6 fresh set B 32.7% (16/49) → V2.7 fresh
  set C **25.0% (6/24)**. Differences between B and C are inside the noise. "Correct and useful" (usefulness 2, zero bad
  sentences) was 2/30 (B) and 1/30 (C).
* **Wrong-law is the dominant failure (≈ 70–77% of bad sentences):** a real, verbatim, verified quote from a provision that
  does not govern the user's facts (school-transfer Act for a college student, apartment-sale Act for a land sale,
  guarantor rule for a borrower, public-company shareholder rule for a private company…). No deterministic check can
  see it in general; each guard row fixes one family and the next fresh set finds new ones.
* **Free fast-tier LLM as an "entailment" judge removed 44% of sentences that had passed every deterministic check**
  and 19/30 answers fell to the plain-provisions fallback → default `ENTAILMENT_CHECK=0` (paid tiers still run it).
  A stronger judge model is the untested fix.
* **Rules tuned on the sentences they are measured on do not generalise.** V3.2 "caught 10/12 bad" and then the fresh set
  scored 44%. ALWAYS fit on one set and test on a fresh one; never claim a target from a tuned set.
* **The topical-fit fitted score is inert; dense features didn't help** (e5 cosines ≈ 0.86 for on-topic and off-topic
  alike). Only the hand-built specialist-regime table (army, judges, postal, insolvency, hire-purchase, customs, election,
  civil service, prison, instalment tax, education, widow, producer liability, brokerage, sentencing) catches wrong-law:
  15/24 held-out, 0 over-removal. It needs new rows after every live review (it is whack-a-mole).
* **Prompt timidity:** telling the free model "code deletes any sentence it can't quote; if unsure omit" made it answer with only
  an empathy line (≈ 10/30). Fixed by "state what the passages say BEFORE any gap". Prompt changes move results a lot.
* **V2.7 made the system safer but much more cautious:** modes on set C = 7 structured / 16 fallback / 7 abstain. Abstain
  precision **1/7** — in two cases (Civil Code s.122 parents' care; Compulsory Education Act s.13 transfer certificate)
  the governing section was on screen under "possibly related" while the answer said nothing was found. The fallback caveat
  "These provisions match the subject of your question" was inaccurate in 11/16 fallbacks (V2.8 was started to fix this).
* **Retrieval misses remain the root of ≈ 60% of bad outcomes:** the governing section exists in the corpus but is not retrieved
  or not used (lists per review in `answer-review-v27-labels-20261001.json`, `answer-review-v33-labels-20261001.json`). In 8 of
  21 set-C misses the section TITLE nearly paraphrases the question → a title-match channel is the highest-value general fix.
* Hand-written section routes (V2.7: 14 rows) fixed their own questions (in-sample 14/14) but did not fire on set C.
  Held-out section hit@8 did not move (0.58) after V2.6/V2.7 — treat route/lexicon gains as in-sample.
* Things tried and **not kept**: lead-doc cap 4/5/6 (cost default hit@8); dense weight 2.2/3.0; heading boost 0.5 (−1.3 pt);
  specialist prior in retrieval (OFF by default, −0.6 pt, no section gain); neighbour (±2 section) expansion (no gold section
  was adjacent); dense re-rank of top-30 (blows the +30 ms budget); "म्याद नाघे" proviso trigger (false removals);
  leading cross-reference trigger variant (couldn't separate good sentences).
* V2.6 held-out run showed a small regression (MRR −0.018, section hit@8 −3 questions) from heading boost/lexicon; V2.7 then
  restored MRR to 0.653 but section hit@8 stayed 0.58. Switches: `retrieval.SEARCH["heading_boost"]`, `translit._LEXICON_NE`.

**Reliability / latency**
* Free LLM tiers 429/503 constantly (Groq tokens-per-minute; both Groq keys share one org; Gemini quota/high demand). Live
  answers took 28–42 s and 2–5 of 30 got no model answer. Fix attempts: token diet (−27 % input, adaptive `max_tokens`),
  per-key cooldown. Real fix = more free provider keys (Cerebras/OpenRouter/Mistral) — founder action.
* Non-streamed JSON generation first made users wait for the full answer (12–30 s Nepali); progressive per-sentence verified
  streaming (V3.1) was added; its provider-compat (response_format + stream) was only partly tested against real providers.
* Hugging Face Spaces free tier needs a paid plan for Docker apps — not an option. Render Starter ($7) is still 512 MB (no
  memory help; it only stops sleeping and gives ≈ 0.5 CPU). Founder can't pay foreign providers anyway.

**Process lessons**
* Sub-agents (Sonnet) in git worktrees work well, but twice they hit API session limits mid-task, and once the monthly spend
  limit. Ask them to COMMIT EARLY; resume with `SendMessage`. Worktree branches are named `worktree-agent-<id>`.
* One agent accidentally edited files in the main checkout; always `git status` after merging.
* `docs/PROGRESS.md` conflicts on almost every merge — keep BOTH sides (a small python snippet was used each time).
* Duplicate agent hand-back messages arrive repeatedly (they restate a finished report) — verify against git before acting.
* The held-out set (`questions_heldout.jsonl`) must never be inspected or tuned on; it has been run raw ≥ 6 times already and one
  agent accidentally displayed ho01/ho02. Consider authoring a NEW held-out set before the next accuracy claim.
* Review sets A (answers30), B (answers30b), C (answers30c), sections12, sections_b, realworld, default are all BURNED as tuning
  data. Make a new set D (fresh questions, never used) for the next live measurement.

---------------------------------------------------------------------------------------------------

## 8. Evaluation tooling (how to measure)

* Retrieval (offline, raw = no LLM rewrite): `cd backend && python eval/run_eval.py retrieval --raw-only --set default|realworld|heldout|sections12|sections_b`
  (needs `DENSE_MODEL_DIR=/home/user/LegalNeps/backend/app/data/dense_model` in worktrees; reports are gitignored → `backend/eval/reports/`).
* Retrieval through the DEPLOYED pipeline (LLM rewrite included, aggregate only): `python eval/live_retrieval.py --set heldout --sleep 4`.
* Live answer review harness: `python eval/answer_review.py --set answers30c --limit 30 --out <file>.json --sleep 6` (≈ 20 min,
  free tier). It records mode (structured / extractive_fallback / none; abstain = fallback whose text starts with the
  abstain sentence), kept sentences with cited quote + full passage, removal reason counts. Then spawn a Sonnet reviewer
  agent to label every kept sentence (prompt used is in this session's history; scheme in `answer-review-v33-labels-20261001.json`).
  Headline numbers to compute: wrong-claim rate with Wilson CI, share of ALL answers safe+useful, correct+useful, abstain precision.
* Verification calibration: `eval/verifier_calibration.py`, `eval/v27_replay.py`, `eval/v27_gate_overremoval.py` replay the
  labelled sentences offline (no LLM) to measure caught/over-removed.
* Tests: `cd backend && python -m pytest -q` (1,844; ~2 min; dense tests need the model dir, else BM25-only). Frontend:
  `cd frontend && NEXT_PUBLIC_API_URL=https://kanooni-sathi-api.onrender.com NEXT_PUBLIC_SUPABASE_URL=https://agzvhessbwwhectuizko.supabase.co npm run build`
  (fails without `NEXT_PUBLIC_API_URL`). Playwright/unit tests under `frontend/tests`.
* Committed evidence files: `backend/eval/reports/answer-review-v3-*`, `…-v32-*`, `…-v33-*`, `…-v27-*` (answers + labels),
  `live-answers/live-review-20260930` (V1), `verifier-calibration-20260930.json`, `baselines-20260930.json`.

---------------------------------------------------------------------------------------------------

## 9. Things only the founder can do (blocked on a human)

1. **Fix sign-in:** Supabase dashboard → Authentication → URL Configuration: Site URL = `https://kanooni-sathi.vercel.app`; add
   Redirect URLs `https://kanooni-sathi.vercel.app/**` (and `https://*-mocklyy.vercel.app/**` for previews); then request a NEW
   email. Code side is done (`emailRedirectTo` in `frontend/lib/supabase.ts`). Nothing behind login has ever been tested with a real user
   (matters, saved drafts, AI-fill, contract audit with a real model, compliance email reminders via Resend).
2. **More free LLM keys** (Cerebras, OpenRouter, Mistral; a second Google account/project for Gemini) → add in Render →
   Environment (comma-separated). Never paste keys in chat.
3. **Advocate review** of the 37 playbooks (`docs/PLAYBOOK_AUDIT.md`), the 22 "standard format" drafts, the 17 `needs_review`
   limitation entries. This is also the route to high accuracy (§10).
4. Optional/costly: Supabase Pro (backups), Supabase leaked-password-protection toggle (free), UptimeRobot ping every 5 min to stop
   Render sleeping (but Render's 750 free hours are shared across the workspace: pause other free web services —
   `simon-says-central`, `simonsays-central`, `ICPLBOOKING`, `icpl-app`, `MOCKLY` belong to OTHER projects; do not touch them),
   Render Starter later (one Pro subscriber ≈ covers it). Also raise/await the Claude account spend limit before more agent runs.

---------------------------------------------------------------------------------------------------

## 9b. Unfinished work

* **V2.8 (cut off by the spend limit)** — branch `worktree-agent-acf49f3c1aba0dcc1` (worktree
  `.claude/worktrees/agent-acf49f3c1aba0dcc1`), 3 commits ("title channel (own vocab, verb-stem folding, doc support) + concept
  lexicon rows", "title channel as doc-supported boost + light injection; curated title text", "Labour Act termination terms in
  the dismissal lexicon row") plus UNCOMMITTED edits in config.py, generation.py, retrieval.py, topical_fit.py. NOT merged, NOT
  tested by the main session, never deployed. Its brief (in this session): title-level retrieval with Nepali stemming; stop
  abstaining when a retrieved section's title matches; make the "match the subject" caveat truthful (only for strict `direct_fit`
  passages); regime guards (shop ≠ company → Private Firm Registration Act ss.3–4; EPF Act s.12 binds public offices, private PF is
  Labour Act s.52; proviso check for "तर…" quotes); replay offline on labelled data; run held-out ONCE. Treat its code as a
  starting point: inspect `git diff`, run the full tests, check default hit@8/MRR (no regression > 1 pt), then merge.
* Governing sections that exist but were not retrieved on set C (verify with `get_index().section(doc_slug(title), section)`):
  c01 Civil Code 586–587; c02 Criminal Code 284, Civil Code 680; c03 Labour Act 139, 144, 148; c05 Civil Code 122 + Senior Citizens Act 4–5;
  c07 Civil Code 206, 219; c08 Good Governance Act 25; c09 Income Tax Act 9(2)(क), Local Govt Operation Act 57; c10 Vehicles and
  Transport Management Act 45, 160(2)(क); c11 Civil Code 279; c14 Criminal Code 253, ETA 47; c15 Civil Code 474, 476, 488; c16 Private Firm
  Registration Act 3–4; c18 Compulsory Education Act 13; c19 NRB directive 19/082 s.8; c20 Civil Code 67; c23 Civil Code 297, Land Revenue
  Act 8; c26 Privacy Act 29; c27 Companies Act 126, 136; c29 Income Tax Act 2(ज), 3. Honest "none found" cases: rent increase mid-term,
  hotel service charge, pre-divorce maintenance, remittance tax (no explicit provision).
* Other open items: OCR for remaining scans; Nepal Gazette scraper (host unreachable from sandbox); the nine default-set retrieval misses
  (valid-will procedure, hacking/cyber crime, bribery घुस, impeachment of a judge, police-custody duration, forgery, guarantee/jamani, dog
  bites, depositors' protection when a bank fails); real-query keyword gaps in playbooks; romanised phrasing beyond the lexicon;
  Preeti↔Unicode converter and dictionary exist but only minimally verified; Playwright e2e not run on the latest UI.
* V-plan milestones not started (see `docs/STRATEGY_V2.md`): V6 Deep Research (Pro), hybrid pgvector in Postgres (we used in-memory int8
  instead), V11 email domain, payments, V14+ (marketplace, mobile…). Pricing/tier gating exists in code (`tiers.py`) but billing is not wired.

---------------------------------------------------------------------------------------------------

## 10. Recommended next steps (ranked)

1. **Do not claim accuracy.** Ship as "cited provisions, quotes checked against the text". Keep the Evidence-box caveat.
2. **Advocate-reviewed answer bank** for the ~150 most common situations (family, land/property, tenancy, labour, cheque/loan, police/FIR,
   cyber, consumer, company, tax). Playbooks already hold the governing provisions for 37; extend to ~150 with advocate sign-off and answer
   those situations from curated text (correct by construction); the LLM only handles the long tail and must abstain honestly.
3. **Finish V2.8** (title-level retrieval, abstain gate, truthful caveat, regime guards) — then measure on a NEW fresh set D (+ a new
   held-out set), review claim-by-claim, report with CIs.
4. **Stronger judge for paid users only** (applicability check "does this passage govern this user's situation?" with Haiku/Sonnet), then
   measure cost vs wrong-law reduction.
5. **More free provider keys** → fewer 429s, shorter waits. Consider per-key cooldown/Retry-After parsing if not already enough.
6. After the accuracy story: login fix verification with a real account, test the signed-in features end to end, backups, billing.

---------------------------------------------------------------------------------------------------

## 11. What to IGNORE (stale, superseded or noise)

* `docs/STRATEGY.md` and `docs/SESSION_PROMPTS.md` (S1–S15 plan) — history only. The plan is `STRATEGY_V2.md`.
* Older `docs/PROGRESS.md` entries (S1–S14, "S15 is the last") — the Next-session text for S-numbers is obsolete; the V-batch entries
  and V2.x/V3.x entries are current. The "Next session" block near the top may lag; trust the newest entry.
* `backend/runtime.txt` (Render ignores it; `.python-version` rules). `graphify-out/` (generated). `backend/app/data/index_cache/`,
  `dense_model/` (build artefacts, gitignored). `sources/` raw downloads (gitignored; only manifests/reports committed).
* Eval reports from tuned runs as "evidence of accuracy": V3 review 1 (15.6%) is NOT representative; use sets A/B/C numbers.
* Review sets and `questions_sections*.jsonl` are tuning data; the heldout file is compromised by repeated use.
* The legacy prose-answer path (`verifier.verify()` flags with ⚠) still exists for the extractive path and tests; new answers use the
  structured path. `STREAM_VERIFIED=0` restores V3 (non-streamed) behaviour; `FIT_GATE=0` restores V3.2. Don't re-enable
  `ENTAILMENT_CHECK` on the free tier.
* A throwaway symlink `backend/evl -> eval` and the many `.claude/worktrees/agent-*` worktrees/branches are agent leftovers — safe to prune
  after merging anything you want (`git worktree list`). `main` branch is not used; production is the dev branch above.
* Other Render services in the same workspace (SPORTXXX / ICPLBOOKING / MOCKLY / simonsays) are unrelated projects.
* `embedding_benchmark.py` / `dense_model_compare.py` — one-off model comparisons (e5-small chosen; e5-base is only ~3 pts better and won't
  fit 512 MB; LaBSE and paraphrase-multilingual-MiniLM were worse).

---------------------------------------------------------------------------------------------------

## 12. Quick start for a new session

```bash
cd /home/user/LegalNeps && git checkout claude/dreamy-hawking-4y5lgf && git pull
cd backend && pip install -r requirements.txt && python scripts/prebuild_index.py   # builds index + downloads model
python -m pytest -q                                                                  # expect ~1844 passed
uvicorn app.main:app --port 8000                                                     # local API
curl -s localhost:8000/api/health
cd ../frontend && npm install && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```
Before touching accuracy work: read `docs/PROGRESS.md` entries "V3 outcome and next steps (2026-10-01)", "V2.7 live review (2026-10-01,
fresh set C)", "V2.7", "V3.3", "V3.2"; open `backend/eval/reports/answer-review-v27-labels-20261001.json` for the concrete wrong sentences.
Prefer Sonnet sub-agents in worktrees for building/reviewing, with explicit commit-early instructions, and merge + test + push + wait for
Render/Vercel before measuring live.
