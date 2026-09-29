# Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform

Written 2026-09-29, after S1–S14. Supersedes `docs/STRATEGY.md` from here on (keep that file for
history — its S1–S14 are done; its S15 is folded into V21–V22 below). Inputs: a live audit of
production (this doc, §1), the two research reports the founder commissioned
(`Nepal_Legal_Tech_Strategy.md`, `Kanooni_Sathi_AI_Audit_Roadmap.docx`), and `docs/PROGRESS.md`.

**One-line thesis:** don't build "ChatGPT for Nepali law". Build the system that turns a Nepali
legal problem into *verified law → evidence → an action plan → the document you need to send*,
and never states a legal claim it can't point to.

---

## 1. Audit: where the product actually is (measured 2026-09-29)

### 1.1 What exists
| Layer | State |
|---|---|
| Corpus | 57,787 chunks: 854 law documents (20,118 act, 16,437 rule, 559 constitution chunks), 10,554 Supreme Court precedent chunks, **14 directive chunks**. Status: 36,273 `in_force`, 356 `bill`, **10,604 `unknown`**. Custom Nepali BM25 index, 124,818-term vocab. |
| Retrieval | BM25 only in production. Eval: hit@8 **0.760**, MRR **0.616** on 150 questions (no held-out set). Hybrid BM25 + local e5-small **won the eval (hit@8 0.808, +5pts)** in S4 but was never shipped. |
| AI | Free multi-provider chain (Gemini/Groq/OpenRouter/Cohere) for everyone. S13 added paid tiers (Haiku 4.5 chat, Sonnet 5.5 drafting) with a cost ledger — **unreachable**, since nothing can set a user's plan off `free`. |
| Backend features | 41 API routes: chat + stream, search, law browser, 25 playbooks + matcher, 4 calculator families + BS↔AD, 10 drafting templates + AI-fill + versioned drafts, matters (notes/tasks/files), compliance radar (6 cited obligations), saved research, quotas, llm-usage, audit log. 257 backend tests. |
| **Frontend** | **Uses 9 of the 41 routes.** Pages: home/chat, search, law browser, static action plans, saved research, sign-in. **No UI at all for** drafting, AI-fill, matters, calculators, compliance radar, account/plan/usage, playbook routing. |
| Infra | Vercel (Next 15, React 19) + Render **free** + Supabase **free**. |

### 1.2 What's broken or risky (found live, not theoretical)
1. **Answers misapply and invent law.** Two real production queries:
   - *"घरबेटीले deposit फिर्ता दिएन"*: 3 of the top 5 sources were irrelevant (Financial Procedure Rules, Income Tax Act ×2, Finance Act 2082). The answer told the *tenant* to give 35 days' notice — that's the Civil Code's notice rule for ending a tenancy, not a deposit-recovery rule. It wrote "धारा" (article) for "दफा" (section). The answer was cut off mid-heading. A **correct, curated playbook for exactly this question already exists** (`deposit_not_returned`) and chat never consulted it.
   - *"Employer hasn't paid salary for 4 months"*: cited the Insolvency Act and Income Tax Act as sources, presented a **BS 2027 (1970) precedent under a repealed wage law** as the current 35-day limitation rule, and told the user to file "a criminal complaint for wage theft" with no source at all.
   These are exactly the failure modes both research reports warn about — and they're live today.
2. **Source status is never shown.** Every chat source returns `status: null` even though the corpus has status for 64% of chunks. Users can't tell current law from repealed law.
3. **45-second cold start.** After the free Render instance sleeps, the first request rebuilds the BM25 index in memory (`/api/stats` took 45.5s). The first visitor after any quiet period thinks the site is broken.
4. **Most of the product is invisible.** ~75% of built capability has no UI, so the research reports (which audited the public site) concluded matters, drafting and calculators don't exist. Users conclude the same.
5. **No backups.** Supabase free tier has no automated backups or PITR, and free projects **pause after ~7 days of inactivity**. Every user's matters, drafts and research has no recovery path.
6. **No way to pay.** No pricing page, checkout, invoices or plan management. Paid-tier code is dead code.
7. Open S14 items: starlette CVEs (need a FastAPI major bump), a postcss advisory inside Next's own tree, leaked-password protection off.

### 1.3 Verdict
The foundations (corpus, deterministic calculators, curated playbooks and templates, matters, tiering, security) are real and ahead of what the public sees. **The product loses on the two things users actually judge: whether the answer is right, and whether they can find the features.** Fix trust first, surface what exists second, then build the signature feature (Document AI), then charge money.

---

## 2. What to take from the research reports — and what to reject

| Recommendation | Verdict | Why |
|---|---|---|
| Evidence-grounded answers + claim-level citation verifier + "evidence coverage" instead of fake confidence % | **Adopt, P0** | Directly fixes §1.2.1. Highest-value item in both reports. |
| In-force / repealed / amended status on every citation | **Adopt, P0** | Data exists for 64% of chunks; it's just not surfaced (§1.2.2). |
| Hybrid lexical + semantic retrieval | **Adopt, P0** | Already proven +5pts hit@8 on our eval. Ship it with precomputed vectors in pgvector. |
| Colloquial Nepali → formal legal term expansion | **Adopt** | 20k-line glossary exists; extend with colloquial/Romanized mappings from real failed queries. |
| Missing-facts detector, query decomposition | **Adopt** | Playbooks already have `fact_questions`; decomposition belongs in the Pro deep-research agent. |
| Action Plans 2.0, Matter Workspace, drafting, calculators, BS↔AD | **Adopt — mostly already built** | Backend exists. The work is UI + wiring, not new engines. |
| Document AI / contract audit as signature feature | **Adopt, P1** | Clearest paid use case for lawyers, CAs and SMEs. Build checklist-driven, not free-form. |
| Law Watch / update feed | **Adopt, P1** | Turns a lookup tool into a subscription people keep. |
| Preeti ↔ Unicode converter, bilingual dictionary | **Adopt as quick wins** | Deterministic, cheap, a genuine Nepal pain point; dictionary data already exists. |
| "What was the law on date X" for **all** acts | **Adopt narrowly** | Real moat, but historical versions need amendment-act parsing and manual verification. Do the top 30 most-queried acts only, verified. Never promise full retroactive reconstruction. |
| **Self-hosted open-weight LLM (Qwen via Ollama/llama.cpp), "zero third-party API"** | **Reject for now** | A GPU that runs a 14B–32B model at usable speed costs roughly $250–700/month; today's API spend is near $0 on free tiers and ~Rs 1.5 per paid answer. Open 14B models are markedly weaker at Devanagari legal reasoning than Claude/Gemini. It also adds GPU ops to a solo founder. Keep the *principle* — every model call already goes through one interface (`llm.py`), so swapping later is a config change. **Revisit when** the monthly API bill passes ~$400 or an enterprise buyer requires on-prem. Handle privacy through provider zero-retention terms, consent and data minimization instead. |
| Local reranker (bge-reranker-v2-m3, 568M params) | **Defer** | Doesn't fit a 512MB instance. Re-test after hybrid ships and the instance is upgraded. |
| Local embeddings | **Adopt** | e5-small (118MB) already benchmarked; precompute corpus vectors offline. |
| Browser WebGPU models | **Reject** | Device support is patchy in the target market; no legal answer should depend on it. |
| "45 features in two weeks" | **Reject** | Not credible. This plan is 22 sessions to a real commercial launch. |

---

## 3. Who pays, and for what

**Beachhead: CAs, accountants and SME owners, then lawyers.** They have recurring statutory deadlines (recurring engagement), contracts to check, labour and tax questions, and budget. Vidhica's traction in the CA segment validates it. Compliance Radar, calculators, labour playbooks and contract templates are already built for this user. Lawyers are the second segment (research, memos, drafting, matters). Citizens are the free acquisition funnel, and the **854 act pages + ~36k section pages are an SEO asset** nobody in the market is exploiting.

### 3.1 Plans (recommended)
| Plan | Price | For | Includes |
|---|---|---|---|
| **Free (Citizen)** | Rs 0 | Public | Search, law browser, action plans, tools, dictionary, **5 AI answers/day** (free model chain), 1 lite document check/month |
| **Pro** | **Rs 1,499/mo** or Rs 14,990/yr | Lawyers, CAs, consultants | Verified answers on Haiku 4.5 (50/day), Deep Research on Sonnet 5.5 (5/day), contract audit (30/mo), unlimited drafting + exports, matters, compliance radar (1 company), Law Watch (10 follows) |
| **Business** | **Rs 3,999/mo** | SMEs, small firms (3 seats) | Everything in Pro shared across 3 seats, compliance radar for 5 companies, 100 audits/mo, shared matters |
| **Student** | Rs 299/mo | Verified students | Search, 20 answers/day, case briefs, study mode later |
| **Firm / Enterprise** | from Rs 12,000/mo | Firms, banks, corporates | Seats, admin, audit log export, custom Law Watch feeds, SLA |

**Set `DAILY_QUOTA_FREE` to 5** when paid plans launch (resolves the S13 flag; 50/day free leaves no reason to upgrade).

### 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices)
| Action | Model | Tokens (in/out) | Cost |
|---|---|---|---|
| Verified answer | Haiku 4.5 ($1/$5 per M) | ~6k / 0.9k | ≈ $0.011 ≈ **Rs 1.5** |
| Deep research (≈6 tool calls) | Sonnet 5.5 ($2/$10 per M) | ~40k / 3k | ≈ $0.11 ≈ **Rs 15** |
| Contract audit | Sonnet 5.5 | ~15k / 4k | ≈ $0.07 ≈ **Rs 10** |

A typical Pro month (150 answers + 20 deep research + 10 audits) costs ≈ Rs 625 → **~58% gross margin at Rs 1,499**, higher with prompt caching. Daily caps protect the tail.

### 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500)
| Item | Cost | Why it's not optional |
|---|---|---|
| Render Starter → Standard | $7 → $25/mo | Kills the 45s cold start; Standard (2GB) also fits hybrid vectors + a reranker later |
| Supabase Pro | $25/mo | Daily backups, no auto-pause. **Without it a week of no traffic pauses production.** |
| Anthropic API | usage, cap at $50/mo at launch | Paid tiers |
| Domain (e.g. kanoonisathi.com) | ~$12/yr | Needed to send email via Resend and for trust |
| Resend, Sentry, analytics | free tiers | Email, error tracking, product analytics |

Break-even ≈ **7–8 Pro subscribers**.

### 3.4 Legal/business prerequisites (founder to-do, confirm with your advocate)
- Register the company (OCR) and get PAN/VAT (IRD) — required for Khalti/eSewa merchant accounts and VAT invoices.
- Position everything as **legal information, not legal advice**. Legal practice is reserved for licensed advocates under the Nepal Bar Council Act, 2050; the product must say so and route high-stakes matters to an advocate.
- Individual Privacy Act, 2075: explicit consent for document uploads, purpose limitation, user data export and deletion.
- Pay a licensed advocate to review the 25 playbooks, 10 templates, 6 compliance obligations and the contract-audit checklists before launch (carried over from STRATEGY v1 — still the best money you'll spend).

---

## 4. Product: the feature set

Status key: **E** = exists in backend, needs UI/wiring · **N** = new build.

### 4.1 Must-have for commercial launch
**A. Trust engine (the "very smart" part people actually notice)**
1. **Verified answers (N)** — structured JSON answer (issue, facts used, facts missing, applicable law, precedents, analysis, steps, deadlines, evidence to collect, citations), then a deterministic verifier:
   - every legal sentence must cite a retrieved passage;
   - every number in a claim (days, rupees, percentages, section numbers) must appear in the cited passage;
   - every cited section must be in the retrieved set;
   - failing claims are removed or visibly marked "not verified".
   UI shows an **Evidence check** block ("9 claims supported · 2 primary sources · 1 precedent · 1 claim not verified"). No confidence percentages.
2. **Status on every citation (E-data, N-UI)** — in force / amended / repealed / bill / unverified badges. Fix the `status: null` bug. Resolve the 10,604 `unknown` chunks. Hard rule: a repealed provision is never presented as current law.
3. **Precedent staleness flag (N)** — link precedents to the statutes they interpret; flag "decided under a repealed/older law".
4. **Hybrid retrieval (N)** — precomputed e5-small vectors in Supabase pgvector, fused with BM25 at alpha≈0.5, plus a **domain filter** (don't surface income-tax acts for a tenancy question). Re-validate on a new held-out set.
5. **Playbook-first chat (E)** — a confident match puts the Action Plan card at the top of the answer, asks the playbook's `fact_questions` as tappable chips, and conditions the answer on the facts.
6. **Deep Research mode — Pro (N)** — Sonnet 5.5 tool-use agent (`search_law`, `open_section`, `open_precedent`, `run_calculator`) that decomposes the question into issues, retrieves per issue, synthesizes, then runs the same verifier. Shows a research trail (sources consulted, not chain-of-thought). Exports a research memo (DOCX/PDF).
7. **Colloquial Nepali expansion (E-data, N)** — extend the glossary with Romanized/colloquial mappings mined from real failed queries ("घरबेटी deposit", "salary आएन", "जग्गाको सिमाना").

**B. Surface what exists**
8. **App shell + repositioned homepage (N)** — "Ask a question. Find the law. Verify it. Know what to do next." Navigation: Ask · Search · Action Plans · Draft · Matters · Tools · Compliance. Citizen / Professional mode toggle.
9. **Drafting Studio (E)** — 10 templates, guided questionnaire, AI-fill, DOCX + PDF download, saved drafts with version history.
10. **Matters workspace (E)** — list + detail (overview, research, drafts, documents, notes, tasks, timeline); "Save to matter" from any answer or draft (wires the unused `matter_id` columns).
11. **Tools (E + N)** — limitation, court fee, gratuity/notice/severance, BS↔AD, **Preeti↔Unicode converter (N)**, **bilingual legal dictionary (N, from glossary)**.
12. **Compliance Radar (E)** — company profile, upcoming deadlines calendar, .ics export, working email reminders (Resend + secured cron trigger).
13. **Account (N)** — plan, usage against quota, cost history (Pro), data export/delete.

**C. Document AI — signature feature**
14. **Upload + understand (N)** — PDF/DOCX (image OCR later), Devanagari normalization, Preeti detection/conversion, clause segmentation; ask questions of the document grounded in both the document and the corpus.
15. **Contract Audit v1 (N)** — five contract types (employment, rent/lease, NDA, service agreement, sale/loan). Each has a curated, cited checklist in YAML, like the playbooks. The LLM *extracts* clause facts; deterministic rules *judge* them. Output: findings table (✓ present · ⚠ ambiguous · ⚠ possible conflict · ℹ related authority) with section citations and suggested redrafts; exportable report.
16. **Notice/letter from a matter (E + N)** — drafts pre-filled from matter facts and audit findings.

**D. Commercial plumbing**
17. **Pricing + checkout (N)** — pricing page; Khalti web checkout (API) with manual eSewa QR as fallback; verified webhook → set `profiles.plan` via service role only; plan expiry; VAT invoice PDF.
18. **Admin console (N)** — users, plans, usage, LLM cost per user, manual upgrade/downgrade, refunds, flagged-injection review.
19. **Onboarding + email (N)** — welcome, quota warnings, renewal reminders, compliance reminders.
20. **Legal pages + consent (N)** — Terms, Privacy (Privacy Act 2075), "information not advice" disclaimer, upload consent, cookie notice.
21. **SEO (N)** — sitemap for every act and section page, structured data, OG images, fast static law pages.

**E. Reliability**
22. No cold start (paid instance, index persisted/loaded fast) · Supabase Pro backups · Sentry · uptime check · eval gate in CI · Playwright E2E.

### 4.2 Growth (post-launch)
Law Watch + update feed (follow an act/section/regulator, weekly crawl diff, email) · corpus expansion for the business segment (IRD circulars, NRB directives — currently only 14 chunks — OCR notices, SEBON) · case brief generator (precomputed for top-cited judgments) · similar cases · cites/cited-by graph · amendment timeline + "law on date X" for the top 30 acts · evidence matrix + chronology from matter documents · contract version comparison · team seats · advocate referral directory (revenue share) · installable PWA.

### 4.3 Later
Student mode (briefs, quizzes, flashcards) · counterargument simulator · knowledge-graph visualization · OCR at scale for scanned judgments · self-hosted model (only on the §2 trigger) · WhatsApp/Viber bot · voice.

---

## 5. Architecture decisions

```
query ─► intent + domain classify (rules first, fast LLM if unsure)
        ├─ greeting / calc / date intent ───────────────────────────► deterministic reply (0 API)
        ├─ confident playbook match ─► Action Plan card + fact chips ─► (answer conditioned on facts)
        ▼
  colloquial→formal expansion (glossary) ─► hybrid retrieval (BM25 in-process + pgvector e5)
        ─► domain filter + status filter (in_force by default) ─► evidence bundle (≤8 passages)
        ─► answer cache (corpus_version | lang | query | source ids) ─ hit ─► 0 API
        ▼
  tier:  free → free chain · Pro/Business → Haiku 4.5 · Deep Research / audit / drafting → Sonnet 5.5
        ▼
  structured JSON ─► deterministic verifier (citations, numbers, status, sections) ─► render + evidence block
```

Rules that don't change:
- **AI for language, code for math and dates, primary sources for law.**
- Every model call goes through `llm.py` (one interface; swappable).
- Citations can only come from the retrieved set. Numbers must appear in their cited passage.
- Plan changes happen **only** via the service role (payment webhook or admin), never from the client (see the S14 RLS fix).
- Every new user-data table ships with RLS and a live two-user isolation test (see S11).
- Prompt caching on every paid call's system prompt.

---

## 6. Session plan (1 session = 1 milestone = 1 commit/PR)

### Phase A — Trust engine
| # | Milestone | Done when |
|---|---|---|
| V1 | **Answer-quality triage.** Fix `status: null` on chat sources; add a domain filter to retrieval; turn the two §1.2.1 failures plus 28 more real-world queries into eval cases; create a **50-question held-out set**; record baselines (hit@8, MRR, unsupported-claim rate by manual review of 30 answers). | Both §1.2.1 queries return only on-domain sources with status shown; baselines written to PROGRESS |
| V2 | **Ship hybrid retrieval.** Precompute e5-small vectors for all chunks → pgvector; fuse with BM25; re-validate alpha on the held-out set. | hit@8 ≥ 0.80 on held-out; search p50 < 300ms warm |
| V3 | **Structured answer + citation verifier.** JSON schema, deterministic checks (§4.1.1), unsupported claims removed or flagged, Evidence-check block in UI; answer never truncates mid-section. | Unsupported-claim rate < 5% on a 30-answer manual review; 0 uncited numbers |
| V4 | **Temporal safety.** Resolve `unknown` statuses; precedent→statute links + staleness flag; status badges; verifier rejects repealed-as-current. | 0 repealed-as-current on a 20-question adversarial set |
| V5 | **Playbook-first chat + fact chips.** | The deposit and salary queries open the right Action Plan first |
| V6 | **Deep Research (Pro).** Sonnet 5.5 tool-use agent + trail + memo export. | 10 multi-issue questions each produce a verified memo with ≥90% supported claims |

### Phase B — Surface the product
| V7 | App shell, homepage repositioning, Citizen/Pro toggle, account page | Every feature reachable in ≤2 clicks; Lighthouse ≥ 90 |
| V8 | Drafting Studio UI + PDF export | Draft → AI-fill → DOCX/PDF → saved version, end to end in the browser |
| V9 | Matters UI + "Save to matter" everywhere | Research, a draft and a file saved into one matter and viewable together |
| V10 | Tools page + Preeti↔Unicode + dictionary | All calculators usable in the UI; converter passes a 50-string test set |
| V11 | Compliance Radar UI + working reminders (Resend + secured cron) + .ics | A real reminder email received end to end |

### Phase C — Document AI
| V12 | Upload + extraction + clause segmentation + document Q&A | Q&A over 5 sample contracts answers with clause references |
| V13 | Contract Audit v1 (5 checklists, cited, rules-judged) + report export | Finds seeded defects in 10 test contracts with ≥90% recall |
| V14 | Notice/letter from matter + audit findings; evidence matrix + chronology | A deposit-recovery notice generated from a matter with its uploaded lease |

### Phase D — Commercial
| V15 | Pricing page, Khalti checkout + eSewa QR fallback, webhook → plan, expiry, VAT invoice, admin console | A real test payment upgrades a real account; admin can downgrade it |
| V16 | Onboarding + emails, Terms/Privacy/consent, data export/delete, SEO sitemap + structured data, analytics | Law pages indexed in Search Console; delete-my-data works |

### Phase E — Retention + moat
| V17 | Law Watch + update feed (weekly Law Commission/Gazette crawl diff, follow, email) | A seeded "amendment" triggers an alert to a follower |
| V18 | Business corpus: IRD circulars, NRB directives, OCR notices with status + dates | ≥500 new directive/circular chunks; eval unchanged or better |
| V19 | Case briefs (precomputed for top-cited), similar cases, cites/cited-by | 50 briefs spot-checked by the founder; similar-case hit rate measured |
| V20 | Amendment timeline + "law on date X" for top 30 acts (verified) | 20 historical-date questions answered with the right version |

### Phase F — Launch
| V21 | Full eval (150 + 50 held-out + 40 adversarial), Playwright E2E on every flow, load test, mobile/PWA, accessibility; FastAPI/starlette upgrade | All §7 metrics met or documented |
| V22 | Advocate sign-off, deploy checklist, status page, pricing live, launch | Paying users can sign up, pay, and use every Pro feature |

Order is deliberate: **V1–V5 before anything else** — selling a product that invents law is worse than selling nothing.

---

## 7. Launch metrics (measured in V21)
| Metric | Target |
|---|---|
| Retrieval hit@8 (held-out) | ≥ 0.85 |
| Citation validity (every [n] maps to a returned source) | 100% |
| Numbers in claims present in cited passage | 100% |
| Unsupported-claim rate (manual review, 50 answers) | < 5% |
| Repealed/bill cited as current (adversarial set) | 0 |
| API-free request rate | ≥ 60% |
| Search p50 / first streamed token p50 / cold start | < 300ms / < 4s / none > 5s |
| Contract audit recall on seeded defects | ≥ 90% |
| Calculator + converter tests | 100% pass |

## 8. Decisions only the founder can make (block specific sessions)
1. **Spend ~$75/mo** (Render Standard, Supabase Pro, API cap, domain) — blocks V2 (memory) and V11 (email domain); backups are urgent regardless.
2. **Company registration + PAN/VAT + Khalti merchant account** — blocks V15.
3. **Advocate review budget** — blocks V22.
4. **Pricing** — §3.1 is the recommendation; confirm or change before V15.
