# Kanooni Sathi: Build Strategy (v2)

Replaces *Nepal Legal App: 2-Week Commercial Roadmap*. That document had the
right product thesis. It did not account for what this repo already contains,
and its session order would have broken the build. This version is based on an
audit of the code (26 Sep 2026).

**Bottom line:** plan for **15 build sessions over 3 weeks** to reach a paid
beta, then **6 hardening sessions (week 4)**. You can't do the original
14-day, 14-subsystem plan in 14 sessions. Days 8–11 each need 2 sessions, and
auth was scheduled on Day 13, after features that depend on it. If you only
have 2 weeks, stop after S10 and run a free public beta (research + action
plans + drafting, no accounts).

---

## 1. What already exists

| Area | State | Verdict |
|---|---|---|
| Corpus | 57,787 passages: 803 law docs (act 20k chunks, rule 16k, constitution 559, treaty 940, order 480), 10,554 Supreme Court precedents (NKP). Official sources only, with URLs. | **Strong. Keep it.** This is further along than the old roadmap's "Day 2". |
| Extraction | Legacy-font conversion (Preeti/Kantipur/PCS), glyph-outline decoding for broken Kalimati, Gemini-vision OCR only for failures | **Strong.** Hard to copy. |
| Search | BM25 on custom Nepali normalisation (ब/व, halant, vowel-length folding, postposition stripping), RRF fusion, authority priors, SQLite passage store, <1 ms/query | **Keep.** Don't replace it with Postgres full-text search: Postgres has no Nepali stemmer, and this code handles Nepali better. |
| Answering | Understand (LLM) → retrieve → grounded, cited, streamed answer. Hard time budgets. Extractive fallback when no LLM is available. | Good, but **2 LLM calls on every legal question**. That is the opposite of "API-free by default". |
| LLM layer | Multi-provider free-tier chains (Groq/Gemini/Mistral/Cohere/OpenRouter/Cerebras) with key rotation and cooldowns; Anthropic and Groq SDKs as last resort | Good for free usage. Nothing is metered, tiered by plan, or costed. |
| Cache | In-memory LRU (answers 512, analyses 2048) | Lost on every restart or deploy. The key doesn't include the corpus version. |
| Frontend | Next.js 14 single chat page, streaming, clickable citations, EN/NE | Fine for chat. No search, law-browsing, or provision pages. |
| Users / DB / auth | **None** | Blocks every paid feature. |
| Tests / eval | 36 app tests pass. 150 hand-written eval questions plus a synthetic and e2e harness. | Good. No CI runs them. |

### Bugs and risks found in the audit
1. **Fresh installs failed.** `pydantic==2.10.3` conflicts with `google-genai==2.25.0` (needs ≥2.12.5). *Fixed in this commit.* Any redeploy on Render would have failed.
2. **Bills are indexed as Acts.** 9 `विधेयक` (draft bills) are tagged `doc_type: act`, so the app can cite a law that was never passed. No doc has a status, enactment date, or amendment list. This is the biggest trust risk.
3. **8,685 chunks are `other`** (annual reports and similar). They're down-weighted but still in the default search.
4. **20 MB corpus and 23 MB of PDFs are committed to git.** That's acceptable for now, but reading them wastes a session's tokens (now blocked in `.claude/settings.json`).
5. Script tests (`test_extract`, `test_nkp_parser`, `test_glyph_order`) need `requirements-scripts.txt`. CI must install both.
6. No rate limiting on `/api/chat`. One person with a loop can use up every free-tier key.

---

## 2. Changes to the original roadmap

| Original | Change | Why |
|---|---|---|
| Day 2: build Legal Data Engine from scratch | **Extend** the existing pipeline with doc-level metadata: `doc_id`, `status` (in_force / bill / repealed / unknown), `enacted_bs`, `amended_by[]`, `consolidated_upto`, canonical provision IDs | ~80% of the pipeline already exists. Law Commission PDFs print amendment lists and dates in the header, so regex can extract them without an LLM. |
| Day 3: Postgres FTS + pgvector for search | Keep BM25 in-process. Add embeddings **only if the eval shows a gain**, as a hybrid. | Render free tier has 512 MB RAM and bge-m3 needs ~2 GB. Measure first: multilingual-e5-small ONNX int8 (~120 MB) vs a hosted embedding API for queries. |
| Day 12: AI gateway | Split. **S3** removes the LLM from the hot path (biggest cost win, done early). **S13** adds per-plan tiering and cost tracking. | Cost control is the business model, so it can't wait until Day 12. |
| Day 13: Auth + security | **Auth + DB in S5.** Security review in S14. | Saved research, vault, matters, quotas and payments all need users. |
| Days 8–9: Document Vault + Contract Intelligence | **Moved to week 4.** Beta gets file upload inside matters only. | Highest effort and most crowded category (Vidhica, Lexana). It doesn't differentiate you. |
| Day 7: full Compliance Radar | **Lite in S12:** company profile → seeded obligations → BS-date calendar → email reminders. Change monitoring in week 4. | A proper radar needs a verified obligations dataset. Seed a small correct one. |
| Groq → Claude escalation | Free chain (existing) for free users; **Claude Haiku 4.5** for paid structured tasks; **Claude Sonnet 5** only for paid drafting and contract review. Metered. | Margins stay predictable. Never sell unlimited AI. |
| (absent) | **Lawyer review of playbooks and templates** | Your moat is correctness. Pay a licensed Nepali advocate to review the 25 action plans and 10 templates before launch. It's the best money you'll spend. |

---

## 3. Target architecture

```
query
  │
  ├─ rules: greeting/thanks/off-topic regex, calculator/date intents ─────────► deterministic reply (0 API)
  ├─ playbook matcher (keywords + glossary [+ embeddings]) ─ confident ──────► Action Plan (0 API)
  ├─ glossary expansion ─ confident? ── no ──► fast LLM analyze (free chain)
  │                           yes
  ▼
BM25 (+hybrid if it wins eval) → top passages (in_force only by default)
  │
  ├─ Postgres answer cache hit (key: corpus_version|lang|normalized_query|source_ids) ─► 0 API
  ▼
answer tier:  free user → free chain   ·   paid → Haiku 4.5   ·   drafting/contract (paid) → Sonnet 5
  ▼
cited answer + "next action" (playbook / template / save to matter)
```

**Data split:** the legal corpus stays as built files (versioned by `manifest.digest` = `corpus_version`). **Supabase Postgres** holds user data: users, plans, usage, answer_cache, saved_research, matters, drafts, tasks, feedback, company_profiles, obligations. Enable RLS on every table from day one. Supabase free tier covers auth, storage and Postgres.

**Payments:** in beta, take manual eSewa/Khalti QR payments and upgrade plans by hand. Add the Khalti API in week 4. Don't build billing before anyone has paid.

---

## 4. Session plan (1 session = 1 milestone = 1 PR)

Model key for building this: **S** = Sonnet (default), **O** = Opus for the planning step only, **H** = Haiku subagents for search, tests and bulk text.

### Week 1: foundation and trust
| # | Milestone | Done when | Model |
|---|---|---|---|
| S1 | **Baseline + CI.** GitHub Actions: pytest (app + scripts deps) and `next build`. Structured request log: `llm_calls`, `tier`, `latency_ms`, `cache_hit`. Record baseline eval (hit@8, MRR, % queries with an LLM call) in `docs/PROGRESS.md`. | CI green; baseline numbers written down | S + H |
| S2 | **Legal data engine v2.** Doc metadata extraction (status, enacted_bs, amended_by, consolidated_upto). Bills and `other` excluded from default search. Canonical provision IDs `<doc_slug>:<section>`. `corpus_version` exposed in `/api/stats`. | 0 bills in default results; test on 20 known acts' dates; eval does not regress | **O** plans schema → S |
| S3 | **LLM-free hot path.** Confidence score from glossary expansion; skip the analyze call when confident; intent regex expanded. | ≥70% of eval questions answered with no analyze call, hit@8 within 2 pts of baseline | S |
| S4 | **Search + law browser UI.** `/search` with filters (law/precedent, doc type, in-force), `/law/[doc]` and `/law/[doc]/[section]` pages with official PDF link. Embedding benchmark (e5-small vs API) on the 150-question eval; ship hybrid only if it wins. | Pages work on mobile; benchmark table in PROGRESS | S + H |
| S5 | **Supabase auth + DB.** Email OTP and Google login. Tables + RLS. Persistent answer cache keyed by corpus_version. Per-user daily quota and IP rate limit. | Logged-in user saves a research item; cache survives restart; rate limit test | **O** plans RLS → S |

### Week 2: the differentiator (Law → Facts → Action)
| # | Milestone | Done when | Model |
|---|---|---|---|
| S6 | **Action Plan engine.** YAML playbook schema: issue, fact questions, provisions (canonical IDs), evidence checklist, forum/office, limitation period (cited), next steps, template link. Engine + UI + first 8 playbooks (unpaid salary, deposit not returned, domestic violence, divorce, cheque bounce, inheritance/अंश, consumer complaint, cyber harassment). | **Test fails if any cited provision ID isn't in the corpus**; 8 playbooks render | S |
| S7 | **+17 playbooks + matcher.** Query → playbook routing without an LLM (keywords + glossary). | 25 playbooks; matcher precision ≥90% on 60 labelled queries | S, H drafts playbooks |
| S8 | **Calculators.** BS↔AD dates, limitation-period checker, court fee, labour gratuity/notice/severance (Labour Act 2074). Each result shows its section. | Table-driven tests per calculator | S |
| S9 | **Drafting engine.** Questionnaire → template (Jinja) → DOCX/PDF, bilingual. First 6: legal notice (salary), legal notice (deposit), rental agreement, अख्तियारनामा, affidavit, consumer complaint. | Generated DOCX opens; snapshot tests | S |
| S10 | **Drafting + AI fill + save.** LLM only for free-text sections (tiered). +4 templates (employment contract, NDA, sale agreement, reply notice). Version history. Saved to user. | 10 templates; AI fill is metered | S |

**Stop here for a 2-week free beta.**

### Week 3: professional features and launch
| # | Milestone | Done when | Model |
|---|---|---|---|
| S11 | **Matter workspace lite.** Matter = client, facts, saved research, action plans, drafts, notes, tasks, uploaded files (Supabase storage, private). | CRUD + RLS tests: user B can't see A's matter | S |
| S12 | **Compliance Radar lite.** Company profile → obligations from a small, cited, verified seed (IRD/VAT/TDS, OCR annual, SSF, labour) → BS calendar → email reminders (Resend free tier). | Each obligation has a source; reminder job runs | S |
| S13 | **AI gateway v2.** Plan-based tier routing (free chain / Haiku 4.5 / Sonnet 5), `llm_usage` table with token cost, quota enforcement, prompt versions, prompt-injection guard for user-supplied text. | Cost per query visible; quota blocks correctly | S |
| S14 | **Security + reliability.** `/security-review`, RLS audit, audit log, error boundaries, backups, secret handling, dependency audit. | No high findings open | **O** reviews → S fixes |
| S15 | **QA + launch.** Full eval + 40 adversarial questions (bills, repealed law, out-of-scope, injection). Playwright smoke tests. Landing + pricing page with manual payment flow. Deploy checklist. | Metrics in §6 met or documented | S + H |

### Week 4: hardening (after beta feedback)
H1 contract review v1 (clause checklist + rule flags, Sonnet for paid) · H2 document vault OCR/search · H3 legal-change monitor (weekly Law Commission crawl diff → affected provisions → notify saved matters and compliance profiles) · H4 precedent ↔ section linking · H5 Khalti API billing + team seats · H6 load test + restore drill.

---

## 5. Pricing to test
| Plan | Price | Includes |
|---|---|---|
| Free | Rs 0 | Search, law browser, action plans, calculators, 5 AI answers/day, 2 drafts/month |
| Individual | Rs 499/mo | 40 AI answers/day, unlimited drafts, saved research |
| Professional | Rs 1,299/mo | Haiku-tier answers, AI draft fill, matters, compliance radar, 200 AI/day |
| Firm | Rs 3,999/mo (5 seats) | Shared matters, Sonnet drafting allowance, admin |

The deterministic features cost nothing to serve, so the free plan can be generous with them. Meter AI.

## 6. Beta success metrics (measured in S15)
- **API-free rate ≥ 70%** of requests (no LLM call at all)
- **Citation validity 100%:** every `[n]` maps to a returned source; every playbook ID resolves
- **Bills/repealed cited as current: 0** on the adversarial set
- Retrieval hit@8 ≥ baseline (S1)
- p50 latency: search < 300 ms, cached answer < 500 ms, first streamed token < 4 s
- Calculator tests 100% pass

## 7. Do not build in weeks 1–3
Native mobile app, e-signature, lawyer marketplace, voice, community features, autonomous agents, bulk corpus expansion, court cause-list scraping, automated billing.
