# Progress

Tracks what's done, current metrics, and the next session to run. See
`docs/STRATEGY.md` for the full plan and `docs/SESSION_PROMPTS.md` for the
kickoff prompt.

## Live deployment (2026-09-28/29 audit)

Until this audit, the public site (`kanooni-sathi.vercel.app`) had never
actually served any of S1-S10 - both the Vercel production alias and the
Render backend were wired to a separate, earlier branch
(`claude/ecstatic-hopper-3yaiot`, a smaller chat-only app), and every deploy
from this branch (`claude/dreamy-hawking-4y5lgf`) had only ever landed as a
Vercel *preview*, never promoted. Fixed this session:

- **Backend**: new Render service `kanooni-sathi-api`
  (https://kanooni-sathi-api.onrender.com), tracking this branch, auto-deploy
  on push. The old `kanooni-sathi-backend` service (still on the broken
  branch) is unused now but was left running rather than deleted.
- **Frontend**: `NEXT_PUBLIC_API_URL` on Vercel points at the new backend;
  a fresh production deploy was pushed live at `kanooni-sathi.vercel.app`.
- **Supabase**: `NEXT_PUBLIC_SUPABASE_URL`/`NEXT_PUBLIC_SUPABASE_ANON_KEY`
  added to Vercel (S5 had never set these, so sign-in silently did nothing
  in production). `SUPABASE_SERVICE_ROLE_KEY` (new `sb_secret_...` format)
  and `SUPABASE_URL` added to the Render backend, so saved research, drafts,
  version history, and the daily quota now actually persist.
- **LLM keys**: Gemini, Groq, OpenRouter, and Cohere API keys added to the
  Render backend (`GEMINI_API_KEY(S)`, `GROQ_API_KEY(S)`,
  `OPENROUTER_API_KEY(S)`, `COHERE_API_KEY`) - chat now answers with a real
  generative summary (`llm_used: true`) instead of the extractive fallback.
- Verified end-to-end against the live production URL: home, search, law
  browser (doc + section pages), all 25 playbooks, LLM-backed chat with
  correct citations, all 4 calculators, DOCX drafting generation, CORS from
  the production origin. All green.
- Not done (infra-only, not blocking): the GitHub repo's default branch is
  still `claude/ecstatic-hopper-3yaiot` (cosmetic - doesn't affect what's
  deployed); the old Render service could be deleted whenever wanted.

## Next session

**S12 — Compliance Radar lite.** See STRATEGY.md §4, week 3 table: company
profile → obligations from a small, cited, verified seed (IRD/VAT/TDS, OCR
annual, SSF, labour) → BS calendar → email reminders (Resend free tier).
Done when: each obligation has a source; reminder job runs.

**Still outstanding from S11** (not blocking, just don't forget it): (a) no
frontend UI yet for the matter workspace (list/detail/notes/tasks/files),
same backend-only scope as S7-S10 - `POST/GET/PUT/DELETE /api/matters...`
all work and are tested, but nobody's built the page. (b) `saved_research`
and `drafts` got a nullable `matter_id` column this session so they *can*
be linked to a matter, but no API endpoint sets it yet - `POST
/api/research` and the drafting save endpoints still don't accept a
`matter_id` param. (c) File uploads are capped at 20MB in the route
handler (`app/routes/chat.py`); nothing enforces a total-storage quota per
user or per matter yet.

**Still outstanding from S10** (not blocking, just don't forget it): (a)
nobody has actually signed up on the live LegalNeps Supabase project yet
(`select id from auth.users` returns empty), so `drafts`/`draft_versions`
have only been verified structurally (schema applied, FK/RLS confirmed via
`get_advisors` and a deliberate FK-violation probe) - a real signed-in
save→list→version-history round trip is still unverified end-to-end, same
gap S5 already flagged for `saved_research`. (b) AI fill is metered by
reusing the existing per-user daily answer quota (`increment_usage` RPC) -
STRATEGY's own dedicated `llm_usage` token-cost ledger is S13's job
("AI gateway v2"), not this session's; don't mistake the shared-quota
approach here for that later table already existing. (c) No frontend UI
yet for AI-fill or the drafts list/version-history view, same backend-only
scope as S7-S9.

**Still outstanding from S9** (not blocking, just don't forget it): (a) PDF
export isn't built - STRATEGY says "DOCX/PDF" but S9's own "done when" bar
only requires the DOCX to open, so PDF was left out rather than faked; a
DOCX->PDF path (e.g. via a headless LibreOffice conversion) is real work for
whichever session needs it. (b) No frontend UI page for the questionnaire ->
draft flow yet, same reasoning as S7/S8's backend-only scope. (c) The
`affidavit` template intentionally ships with zero cited provisions - it's
a generic sworn-statement format, not itself created under one dedicated
statute in the corpus (confirmed by `idx.search()` turning up nothing for
"सपथपत्र" as a section heading) - don't read this as a missed citation.

**Still outstanding from S8** (not blocking, just don't forget it): the 4
calculators are backend-only (`GET /api/calculators/...`) - no frontend UI
page yet. STRATEGY's S8 "done when" bar (table-driven tests per calculator)
didn't require one, same reasoning as S7's matcher. Left for whichever
session next touches frontend pages.

**Still outstanding from S5** (not this session's job, just don't forget
it): give the user the exact steps to (a) set `SUPABASE_SERVICE_ROLE_KEY` on
the backend deploy and `NEXT_PUBLIC_SUPABASE_URL`/`NEXT_PUBLIC_SUPABASE_ANON_KEY`
on the frontend deploy, and (b) do one real signed-in test of save-research
end to end, since S5 could only verify the pieces individually.

**Still outstanding from S7** (not blocking, just don't forget it): the
matcher is built and exposed at `GET /api/playbooks/match?q=...` but is not
yet wired into the frontend chat flow or `generation.py`'s LLM pipeline —
STRATEGY's architecture diagram shows a confident match short-circuiting
straight to an Action Plan with zero API calls, which the frontend doesn't
do yet. Left for whichever session next touches the chat UI/pipeline, since
S7's own "done when" bar (25 playbooks, ≥90% precision) doesn't require it.

## Done

### S11 — Matter workspace lite (2026-09-29)

A real user (`s.neupaneqs@gmail.com`) signed in on the live site between
S10 and this session - confirmed via `select * from public.profiles`,
which now has 1 row. That closes S10's "nobody has signed up yet" gap on
its own; the S10-era `drafts`/`saved_research` structural-only caveat can
be retired once that user actually saves something.

- **Schema**: `matters` (client_name, facts, status) plus `matter_notes`,
  `matter_tasks`, and `matter_files` (metadata only; bytes live in a new
  private Supabase Storage bucket `matter-files` under
  `{user_id}/{matter_id}/{filename}`, with `storage.objects` RLS policies
  scoping access to that path prefix). `saved_research` and `drafts` each
  got a nullable `matter_id` FK so they *can* be linked to a matter later
  (see "Next session" - no endpoint sets it yet). Applied as two real
  migrations to the live LegalNeps Supabase project, same as S10.
- **Real RLS proof, not just structural**: this is the first session able
  to actually test isolation end-to-end, because a service-role secret key
  now exists to drive it. Created two throwaway Supabase auth users via the
  Admin API, signed in as each to get real per-user JWTs, and hit
  PostgREST directly with the anon key (i.e. exactly how RLS is meant to be
  exercised, not through the backend's own service-role bypass): user A
  creates a matter, user B's SELECT/UPDATE/DELETE against it all correctly
  return empty/0-rows. **This caught a real gap**: `matter_notes`' insert
  policy only checked `auth.uid() = user_id` on the note's own row, not
  that the referenced `matter_id` actually belonged to that user - so user
  B could attach a note to user A's `matter_id` (B still couldn't read
  A's real data through this, since every read stays scoped to `user_id =
  B`, but it's cross-tenant row injection at the DB level). Fixed with a
  second migration adding an `exists (select 1 from matters where id =
  matter_id and user_id = auth.uid())` check to the insert policies on
  `matter_notes`, `matter_tasks`, and `matter_files`; re-ran the same live
  probe and confirmed B now gets a 403. Test users and their data were
  deleted afterward (`auth.users` back to the 1 real signup,
  `matters`/`matter_notes` back to 0 rows).
- **App-layer ownership check**: the backend talks to Supabase with the
  service-role key, which bypasses RLS entirely - so DB-level RLS alone
  doesn't protect the backend's own API surface. Every note/task/file route
  in `app/routes/chat.py` calls a `_require_matter()` dependency first,
  which 404s (not 403, so a stranger's matter ID and a nonexistent one look
  identical) before touching anything scoped to a `matter_id` that isn't
  the caller's.
- **File upload**: `POST /api/matters/{id}/files` accepts a real multipart
  upload (added `python-multipart` to requirements.txt, without which
  FastAPI silently can't parse form data), streams the bytes to the private
  Storage bucket via `supa.matter_file_create()`, then records metadata.
  20MB size cap in the route handler. Download is a signed, time-limited
  URL (`matter_file_signed_url()`, 5 min default) rather than the backend
  proxying file bytes itself.
- **API**: full CRUD on `/api/matters`, `/api/matters/{id}/notes`,
  `/api/matters/{id}/tasks`, `/api/matters/{id}/files` - all
  `_require_user`-gated. No frontend UI yet (see "Next session").
- **Tests**: `tests/test_s11_matters.py` - fail-open-without-Supabase
  checks, a full CRUD round trip per resource type (including a real
  multipart file upload against the test client), and the API-layer
  ownership proof (every sub-resource route 404s for user B on user A's
  matter). Full backend suite: **214 passed** (was 207).
- **graphify**: re-ran `graphify update .` (code) and `graphify label .`
  (community naming) after this session's changes - the committed graph
  now covers the matters/notes/tasks/files code too (1136 nodes, 2290
  edges, 69 communities).

### S10 — Drafting + AI fill + save (2026-09-28)

- **+4 templates**, bringing the total to 10: employment contract, NDA,
  sale agreement, and a reply-to-a-legal-notice letter. Same
  research-before-writing discipline as every session since S6 - new
  citations found with `idx.search()` and read in full with `idx.section()`
  before being coded: श्रम ऐन दफा ११/१३ (an employment contract is legally
  required and must state pay/benefits/terms; the up-to-6-month probation
  rule) for the employment contract; मुलुकी देवानी संहिता दफा ५०४/५३७
  (general contract formation and breach-compensation) for the NDA, since
  Nepali law has no NDA-specific statute; दफा ४१४/४१६ (right to transfer
  owned property; ownership passes to the transferee) for the sale
  agreement. `reply_notice` ships with no citation by design, same
  reasoning as S9's `affidavit` - it's a response letter, not itself
  created under a dedicated statute.
- **AI fill** (`app/drafting/ai_fill.py`, new): expands a user's short
  free-text hint (e.g. "our client list and pricing" for an NDA's
  confidentiality-scope field) into 2-4 sentences of proper document
  prose, in the target language. Deliberately scoped to `textarea` fields
  only - a name or a date is exactly the kind of thing a user just types,
  and routing it through an LLM would add latency and hallucination risk
  for zero benefit. The system prompt explicitly forbids inventing names,
  dates, amounts, or statute citations not present in the hint - citations
  in a generated document only ever come from the template's own
  corpus-verified paragraphs, never from this free-text fill. Tiered per
  STRATEGY's requirement: calls `llm.complete(..., fast=True)`, the cheap/
  low-latency tier S3 already built, not the stronger answer tier.
- **Metering**: `POST /api/drafting/templates/{id}/ai-fill` requires a
  signed-in user and calls the same `supa.check_and_increment_quota()`
  (the `increment_usage` Postgres RPC) that `/api/chat` already uses - one
  shared per-user daily budget across chat answers and AI-fill calls. This
  satisfies S10's "AI fill is metered" bar without building the dedicated
  token-cost `llm_usage` ledger STRATEGY reserves for S13's "AI gateway
  v2" - see "Next session" for why that distinction matters.
- **Save + version history**: new `drafts` and `draft_versions` tables,
  applied as a real migration to the live LegalNeps Supabase project
  (`agzvhessbwwhectuizko`) via the Supabase MCP tools available this
  session - the first session in this build able to touch that project
  directly rather than only writing code against it. Both tables FK to
  `auth.users(id)` and have RLS enabled with the same `auth.uid() =
  user_id` policy shape S5 used for `saved_research` (confirmed by reading
  `saved_research`'s own constraint definition and matching it, not just
  assuming the convention). `get_advisors` after applying showed no new
  security findings (the one pre-existing `answer_cache` RLS-without-policy
  finding is S5's, untouched here). A deliberate insert with a
  nonexistent `user_id` was used to confirm the FK actually rejects bad
  data, since no real user has signed up in the project yet to test with
  (see "Next session"). `supa.py` gets `draft_create/update/list/get/
  delete/versions_list`: every save writes both the draft's current state
  and an immutable version snapshot, so `draft_update` always appends
  rather than overwrites history.
- **API**: `POST /api/drafting/templates/{id}/ai-fill`, `POST/GET/PUT/
  DELETE /api/drafting/drafts[/{id}]`, `GET
  /api/drafting/drafts/{id}/versions` - all `_require_user`-gated.
- **Tests**: `tests/test_drafting.py`'s template set grew from 6 to 10 (40
  cases, was 28). New `tests/test_s10_ai_and_save.py`: `ai_fill` unit tests
  with `llm.complete` monkeypatched (no real LLM key in this build
  environment, same limitation noted since S3), the metering/auth-gating
  behavior at the API layer (a second AI-fill call gets 429 once a faked
  quota check denies it), and the full drafts CRUD + version-history round
  trip against a monkeypatched `supa` store (same pattern
  `tests/test_api.py` already uses for `saved_research`, since Supabase
  isn't configured as this backend process's own env in this build
  environment). Full backend suite: **207 passed** (was 184). Frontend
  `npm run build` re-verified clean (no frontend changes this session).

### S9 — Drafting engine (2026-09-28)

New `app/drafting/` package: questionnaire answers → rendered DOCX,
bilingual, for the first 6 templates STRATEGY names - legal notice (unpaid
salary), legal notice (deposit not returned), rental agreement, अख्तियारनामा
(power of attorney), affidavit, and a consumer complaint letter.

- **Architecture**: each template (`registry.py`) is a list of paragraphs,
  each holding a Jinja source string per language (`{"en": "...", "ne":
  "..."}`) rather than a hand-authored `.docx` file with embedded Jinja tags
  (the `docxtpl` approach) - that would mean constructing binary `.docx`
  template files with no GUI in this environment, which is fragile to author
  and review. `render.py` fills in the questionnaire's answers plus
  always-available context (today's date in BS, via S8's `ad_to_bs()` - a
  direct reuse of last session's work) and lays the rendered paragraphs out
  as a real `.docx` with `python-docx`. A missing required answer raises
  `MissingField` before any rendering happens, not a confusing Jinja
  traceback.
- **Citations**: every statute reference embedded in a template's Nepali
  text was found with `idx.search()` and read in full with `idx.section()`
  against the real corpus first, same discipline as S6/S7/S8. New
  citations this session: श्रम ऐन दफा ३५ (wage-payment interval, for the
  salary notice - found after दफा ६३ turned out to be about labour-supplier
  licence cancellation, not general wage payment, and was discarded), मुलुकी
  देवानी संहिता दफा ४९५/५०० (general obligation/compensation duty, reused
  for the deposit notice since Nepali law has no deposit-specific statute -
  same finding S7 already made for the `deposit_not_returned` playbook),
  मुलुकी देवानी संहिता दफा ३८६/३८९/४०२ (the rental-agreement chapter - दफा
  ३८६(१) turned out to list the exact mandatory clauses a written tenancy
  agreement must contain, which the template's clause-by-clause structure
  follows directly), and मुलुकी देवानी संहिता दफा ५९१/५९२ (agency/
  representative appointment, the actual legal basis for अख्तियारनामा).
  Each template's `provisions` list is re-resolved against the corpus via
  `playbooks.resolve_provision()` (same as S8's calculators), tested
  separately from the DOCX content itself. The `affidavit` template ships
  with no citation by design - see "Next session" above.
- **API**: `GET /api/drafting/templates`, `GET
  /api/drafting/templates/{id}` (fields + resolved provisions, for a
  frontend questionnaire to render), and `POST
  /api/drafting/templates/{id}/draft` (returns the generated `.docx` as a
  binary response with the right content type and a `Content-Disposition`
  filename).
- **Tests**: `tests/test_drafting.py`, table-driven per STRATEGY's "done
  when" bar - every template's generated DOCX is opened with `python-docx`
  and checked for non-empty content, in both languages (12 cases), plus
  content-substitution checks (answers and citations actually appear in the
  rendered text), a Jinja `{% if %}` conditional-field test (अख्तियारनामा's
  optional `valid_until`), missing-field/unknown-template/bad-language error
  cases, and an API test. Full backend suite: **184 passed** (was 156).
  Frontend `npm run build` re-verified clean (no frontend changes this
  session).

### S8 — Calculators (2026-09-27)

Four calculators (`app/calculators/`), each returning the specific corpus
provision it's based on (re-resolved live against the corpus via a new
public `playbooks.resolve_provision()`, same `UnresolvedProvision` guarantee
as a playbook), plus a `GET /api/calculators/...` endpoint each:

- **BS↔AD dates** (`dates.py`): thin wrapper over the `nepali_datetime`
  package rather than a hand-rolled BS calendar table - Nepal's BS month
  lengths follow an official almanac, not a fixed rule, so reimplementing
  that table by hand is exactly the kind of thing that's quietly wrong in
  an edge case nobody tests. `bs_to_ad`/`ad_to_bs`, range ~1975–2100 B.S.
  (~1918–2044 A.D.), `UnsupportedDate` outside that range.
- **Limitation-period checker** (`limitation.py`): मुलुकी देवानी कार्यविधि
  संहिता दफा ४९ says there's no single general limitation period - each
  claim type's own governing law sets its own. So this is a cited lookup
  table, not one formula, reusing the exact citations S6/S7 already
  verified for the matching playbooks: contract civil claim (मुलुकी देवानी
  संहिता दफा ५२०, 2 years), partition disagreement (दफा २३५, 3 months),
  labour dispute complaint (श्रम ऐन दफा १६२, 6 months), foreign employment
  complaint (वैदेशिक रोजगार ऐन दफा ६०, 1 year), cheque dishonour complaint
  (बैङ्किङ्ग कसूर तथा सजाय ऐन दफा १७, 1 year). `check()` returns deadline,
  days remaining, and whether the claim is already time-barred.
- **Court fee calculator** (`court_fee.py`): मुलुकी देवानी कार्यविधि संहिता
  दफा ६९'s marginal-bracket schedule on claim value (बिगो) - flat Rs 500 for
  the first Rs 25,000, then 5%/3.5%/2%/1.5%/1% on each further bracket,
  computed the same way as an income-tax schedule (each bracket's rate
  applies only to the slice of value inside it - verified by hand against
  the statute's own worked figures for Rs 50,000/100,000 before trusting
  the code). Separately: दफा ९७'s flat Rs 200 फिराद दस्तुर (always charged,
  not part of the दफा ६९ schedule) and दफा ७३'s 15% appeal surcharge.
- **Labour Act calculators** (`labour.py`, श्रम ऐन २०७४): gratuity/उपदान
  (दफा ५३: 8.33% of basic monthly pay per month of service), termination
  notice period + pay-in-lieu (दफा १४४: 1/7/30 days depending on whether
  service was ≤4 weeks / 4 weeks–1 year / >1 year), and retrenchment
  severance (दफा १४५(७): one month's basic pay per completed year of
  service, pro-rated below 1 year - both cases reduce to one formula,
  `basic_monthly_pay * years_of_service`).
- **Research method**: same as S6/S7 - every new citation (दफा ४९/६८/६९/
  ७०/७३/९७ of देवानी कार्यविधि संहिता; दफा ५२/५३/१४४/१४५(२) of श्रम ऐन) was
  found with `idx.search()` and read in full with `idx.section()` against
  the real corpus before being coded against, not written from memory. The
  देवानी कार्यविधि संहिता दफा ६९ bracket schedule text itself was used to
  hand-verify three of the seven test cases (Rs 50,000/100,000 claim
  values) before the parametrized test table was written.
- **Tests**: `tests/test_calculators.py`, table-driven per STRATEGY's "done
  when" bar - 48 cases across all 4 calculators (BS↔AD round-trips against
  independently-verified pairs, limitation deadlines/time-barred flags,
  court-fee brackets against hand-derived figures, labour formulas), plus
  an API-level test hitting the real corpus. Full backend suite: **156
  passed** (was 107). Frontend `npm run build` re-verified clean (no
  frontend changes this session - see "Next session" above for the UI gap
  this leaves).

### S7 — +17 playbooks + matcher (2026-09-26)

- **17 new playbooks** (`app/data/playbooks/*.yaml`), bringing the total to
  25: wrongful_termination, workplace_sexual_harassment, bonus_not_paid,
  foreign_employment_fraud, tenant_eviction_without_notice,
  land_boundary_dispute, unpaid_personal_loan,
  traffic_accident_compensation, defamation, theft_complaint,
  physical_assault, child_custody, maintenance_alimony,
  child_marriage_protection, citizenship_by_descent,
  right_to_information_request, fir_not_registered. Same research-before-
  writing discipline as S6: every provision was found with `idx.search()`
  and confirmed with `idx.section(doc_slug(title), section)` against the
  real 57,787-passage corpus before being cited, not written from training-
  data memory. Two near-miss citations were caught and corrected this way
  before being finalized: `tenant_eviction_without_notice`'s मुलुकी देवानी
  संहिता दफा 404 note was originally too generic (rewrote it to state the
  actual narrow ground the law allows: a tenant vanishing 3+ months without
  paying rent — not "landlord wants tenant out"), and
  `land_boundary_dispute` initially considered भूमि सम्बन्धी ऐन दफा 14क until
  reading its full text showed it's about landholding-ceiling violations,
  not boundaries — dropped in favour of जग्गा (नाप जाँच) ऐन दफा 5/8.
- **Matcher** (`app/playbook_matcher.py`, new): routes a free-text query to
  a playbook id without any LLM call. Each of the 25 playbooks got a hand-
  written `keywords` list (Nepali + English + romanised trigger phrases,
  inserted into every YAML right after `area:`). Scoring is plain token/
  substring overlap — a keyword contributes its word-count as weight, scaled
  by what fraction of the keyword's own words showed up in the query (so a
  multi-word phrase can match partially instead of all-or-nothing), and an
  English/romanised query is first widened through S3's `glossary.expand()`
  so it can still hit a playbook's Nepali-only keywords. `match()` returns a
  playbook id only when the top score clears an absolute floor *and* beats
  the runner-up by a margin — ambiguous or off-topic queries return `None`
  rather than a wrong guess.
- **Precision measured, not assumed**: `tests/test_playbook_matcher.py`
  ships a 65-query labelled set (62 positive across all 25 playbooks, mixing
  Nepali/English/romanised phrasing, 3 clearly-unrelated negatives),
  written independently of keyword-tuning. Actual result:
  **95.16% precision** (59/62) against STRATEGY's ≥90% bar, plus 100% on
  rejecting the 3 unrelated queries and an empty-query guard.
- **API**: new `GET /api/playbooks/match?q=...` endpoint
  (`app/routes/chat.py`) returns `{"playbook_id": "..."|null}`, exercised in
  `tests/test_playbooks.py`'s existing real-corpus API test alongside the
  pre-existing `/api/playbooks` endpoints. Not yet wired into the frontend
  or into `generation.py`'s LLM pipeline as a short-circuit — see "Next
  session" above.
- **Verification**: `tests/test_playbooks.py`'s `EXPECTED_IDS` and citation-
  integrity assertions extended from 8 to all 25 playbooks —
  `test_every_cited_provision_resolves_in_the_real_corpus` passed with 0
  `UnresolvedProvision` errors on the first run across all 25×~2-3
  provisions each. Full backend suite: **107 passed** (was 103 before this
  session; +4 matcher tests, existing API test extended). Frontend
  `npm run build` re-run clean (no frontend changes this session, so this
  just confirms no regression).
- **Bug caught mid-session, not shipped**: the first attempt at inserting
  `keywords` into the 25 YAML files via a Python script silently did
  nothing — the script's `pathlib.Path(".").glob("*.yaml")` was run from
  `backend/` instead of `backend/app/data/playbooks/`, so the glob matched
  zero files and the script exited with no output and no error. Caught via
  `grep -c "^keywords:" app/data/playbooks/*.yaml` returning 0 despite the
  script appearing to succeed — fixed by pointing the glob at the correct
  directory and re-running; verified with the same grep plus a
  `yaml.safe_load` pass over all 25 files afterward.

### S6 — Action Plan engine (2026-09-26)

**Deviated from the session prompt's suggested workflow on purpose**: it
says to use a "drafter" subagent for the YAML then verify citations myself.
No such subagent is configured in this environment, and more importantly —
having watched an LLM invent plausible-looking but wrong Nepali statute
citations before (that's exactly why the verify-yourself step exists) — I
judged it safer to do the citation research against the live corpus myself
*before* writing a word of YAML, rather than draft first and debug wrong
citations after. So every provision in every playbook below was looked up
with `idx.search()`/`idx.section()` against the real corpus first,
cross-checked by reading the actual section text, and only then written
into YAML - not generated from training-data memory of Nepali law.

- **Engine** (`app/playbooks.py`, new): loads YAML from
  `app/data/playbooks/*.yaml` and resolves every cited provision
  (`law_title_ne` + `section`) against the live corpus via S4's
  `doc_slug()`/`Index.section()` - reusing that machinery means a playbook's
  citations link straight into the law browser (`/law/[slug]/[section]`)
  and show the corpus's own live citation text/URL/status, not a copy that
  can drift out of sync. `UnresolvedProvision` is raised, not silently
  swallowed, when a citation doesn't resolve - the citation-integrity test
  depends on that being a hard failure.
- **8 playbooks** (`unpaid_salary`, `deposit_not_returned`,
  `domestic_violence`, `divorce`, `cheque_bounce`, `inheritance_share`,
  `consumer_complaint`, `cyber_harassment`): each has fact questions,
  cited provisions with plain-language notes, an evidence checklist, forum/
  office, a limitation-period note (cited where the corpus has an explicit
  हदम्याद clause for that chapter - e.g. मुलुकी देवानी संहिता दफा 235 for
  अंश, दफा १६२ श्रम ऐन for labour complaints, दफा 14 घरेलु हिंसा ऐन), and
  numbered next steps. `template_link: null` (S9 will add real drafting
  templates). All bilingual (en/ne).
- **Citation-integrity test** (`tests/test_playbooks.py`,
  `test_every_cited_provision_resolves_in_the_real_corpus`): every single
  provision in every playbook resolved on the first run - no citation had
  to be fixed after the fact, which I take as the payoff of researching
  before writing rather than after.
- **API**: `GET /api/playbooks` (summary list), `GET /api/playbooks/{id}`
  (full, resolved). **Frontend**: `/action-plans` (list, area badges) and
  `/action-plans/[id]` (fact questions, clickable law citations, evidence,
  forum, limitation, numbered next steps) - verified in a real browser
  (Playwright, mobile viewport) against the live backend, and confirmed a
  citation link (`/law/{slug}/162`, श्रम ऐन दफा १६२) actually lands on the
  correct real section, not just that it doesn't 404.

**Found and fixed two more real bugs while building** (both pre-existing,
surfaced by this session's work rather than caused by it):
1. **Test-isolation leak** in `tests/test_retrieval.py` and
   `tests/test_api.py`: both set `retrieval.CACHE_DIR = tmp_path` as a
   *direct* assignment instead of `monkeypatch.setattr(...)`, so it was
   never reverted after those tests ran. Any later test that touched the
   *real* corpus's `get_index()` (this session's `test_playbooks.py` was
   the first) would find `CACHE_DIR` still pointed at an already-deleted
   pytest tmp dir, miss the on-disk cache, and silently rebuild the whole
   57,787-passage index from scratch - caught because that one test took
   17.85s instead of the <1s it should. Fixed both to properly restore the
   original value.
2. **`Index.section()` never backfilled `status`** the way `Index.doc()`
   already does (S4 gap): a pre-S2 corpus row has no stored `status` field,
   and `doc()` correctly falls back to the computed status array, but
   `section()` just spread the raw row - so `/api/law/{slug}/{section}`
   (and now playbook provisions, which call `section()` internally) was
   silently returning `status: null` for effectively the entire corpus
   instead of `"in_force"`. Found by eyeballing resolved playbook output
   before trusting it, not by a failing assertion - worth noting as a
   reminder to look at real output, not just green tests. Fixed the same
   way `doc()` already does it.

103/103 backend tests pass (was 97 after S5; +6 for `test_playbooks.py`).
Frontend `next build` succeeds; `/action-plans` and `/action-plans/[id]`
compile and were verified live.

### S5 — Supabase auth + DB (2026-09-26)

A Supabase MCP connection became available mid-session, which changed the
plan: instead of asking the user to click through the dashboard, found their
already-created empty **"LegalNeps"** project (org `sneupaneqs-boop's Org`,
region `ap-southeast-1`, project ref `agzvhessbwwhectuizko`) via
`list_projects` and built directly against it through the MCP tools -
migrations applied and verified live, not just written and assumed correct.
The account also has 3 older, unrelated projects (`Sudin`, `MOCKLYY`,
`BarXcut`) - not touched.

**Schema** (4 migrations, all applied and confirmed via `list_tables`/
`get_advisors`):
- `profiles` (id, email, plan default 'free') - auto-created by an
  `on_auth_user_created` trigger (`handle_new_user()`) whenever Supabase
  Auth creates a new `auth.users` row.
- `usage_daily` (user_id, day, request_count) - per-user daily quota.
- `answer_cache` (cache_key, corpus_version, language, question, answer
  jsonb, hit_count) - replaces the in-memory-only LRU cache (known issue #5:
  lost on restart, not keyed by corpus_version). RLS enabled with **zero**
  policies for anon/authenticated (backend-only, via service_role, which
  bypasses RLS in Supabase) - the advisor's "RLS enabled, no policy" lint on
  this table is expected, not a gap.
- `saved_research` (id, user_id, question, answer jsonb, language,
  created_at) - a logged-in user's saved answers; RLS: select/insert/delete
  own rows only.
- `increment_usage(user_id, daily_limit)` RPC: atomic check-and-increment
  (`INSERT ... ON CONFLICT DO UPDATE ... RETURNING`) so two concurrent
  requests from the same user can't both read "under quota" and both
  proceed - a plain read-then-write from the backend would have this race.
  Execute revoked from anon/authenticated (service_role only).
- Security advisor flagged `handle_new_user()` as callable directly via
  `/rest/v1/rpc/handle_new_user` by anon/authenticated - fixed by revoking
  EXECUTE from those roles (the trigger itself still fires regardless, since
  trigger invocation isn't gated by the invoking role's grants in Postgres).
  Advisor re-run clean after (only the expected `answer_cache` INFO
  remains).

**Backend** (`app/supa.py`, new): talks to Supabase's REST/Auth API directly
over `httpx` (already a dependency) rather than the `supabase-py` SDK, to
avoid another heavy dependency tree after S1's pydantic lesson. `get_user()`
validates a frontend access token via a round trip to Supabase's own
`/auth/v1/user` (simpler and safer than reimplementing local JWT
verification / key rotation). `check_and_increment_quota()` calls the RPC;
fails open (never blocks) if Supabase is unreachable. `cache_get()`/
`cache_put()` back the persistent answer cache, gated on `corpus_version`
matching. `check_ip_rate_limit()` is a pure in-memory per-process sliding
window (documented limitation: not shared across multiple backend
instances - fine for a single free-tier instance, wrong for a
horizontally-scaled deploy).
- `generation.py`: added a corpus_version-prefixed `_answer_cache_key()`,
  kept separate from the plain `_cache_key()` used by `analyze_query()`'s
  cache (analysis output doesn't depend on corpus content - coupling it to
  `get_index()` was a real bug I introduced and caught via a test that
  suddenly took 16s instead of instant, see "Found while building" below).
  `run()` now checks the Supabase cache (L2) behind the existing in-memory
  LRU (L1) for first-turn messages, and writes through to both on a fresh
  LLM answer.
- `routes/chat.py`: `/api/chat` and `/api/chat/stream` now enforce the IP
  rate limit (429) for every caller and the per-user daily quota (429) for
  authenticated ones. New `POST/GET /api/research` and
  `DELETE /api/research/{id}`, all requiring a valid bearer token
  (`_require_user` dependency, 401 otherwise).
- `config.py`: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
  `DAILY_QUOTA_FREE` (default 50/day), `IP_RATE_LIMIT_PER_HOUR` (default
  30/hour) - all env-configurable.

**Found while building** (both fixed): (1) `_cache_key()` originally called
`get_index()` directly, which forced a full ~17s corpus index build the
first time *any* cache key was computed - including from
`tests/test_hot_path.py`, which has no retrieval fixture and doesn't need
one. Caught because that specific test suddenly took 16.73s instead of
instant; split into `_cache_key()` (no corpus dependency, used by
`analyze_query()`) and `_answer_cache_key()` (corpus-version-prefixed, used
only by the answer cache). (2) `check_ip_rate_limit()` and
`check_and_increment_quota()` originally used
`config.IP_RATE_LIMIT_PER_HOUR`/`config.DAILY_QUOTA_FREE` as Python default
*parameter* values - evaluated once at import time, so a
`monkeypatch.setattr(config, ...)` in a test (or any runtime config change)
silently had no effect. A test written to prove the 429 behavior caught
this immediately (asserted 429, got 200). Fixed by reading `config.*` inside
the function body instead.

**Frontend**: `lib/supabase.ts` (client + `signInWithOtp`/`verifyOtp`/
`signOut`), `lib/useAuth.ts` (session hook), `components/AuthWidget.tsx`
(email → 6-digit code sign-in popover, dropped into the header on all three
pages). A "Save" button appears under any chat answer; disabled with a
"sign in to save" tooltip when logged out. New `/saved` page lists and
deletes saved research. Google sign-in **deferred at the user's choice**
(needs a separate Google Cloud Console OAuth setup) - email OTP only for
now; adding Google later doesn't touch the schema or this code.

**Verified live against the real Supabase project** (via the MCP SQL tools,
which only need project access, not the service_role key): the
`on_auth_user_created` trigger fires and creates a `profiles` row
(`plan: free`) when a test `auth.users` row is inserted; `increment_usage`
correctly allows the first N calls and blocks the (N+1)th
(`allowed: false`) while counting accurately; deleting the test user
cascades to delete their `profiles` row (`on delete cascade` works); the
REST API paths/params `app/supa.py` uses were checked directly against the
live project with `curl` and the (non-secret) anon key - `/auth/v1/user`
with a garbage token returns 403 (handled as "no user" by `get_user()`),
`/rest/v1/answer_cache` with the right query-string shape returns `200 []`
(RLS blocking anon, not a URL/param bug). All test data cleaned up
afterward (verified 0 rows in every table again).

**NOT verified**: the actual authenticated round trip through
`app/supa.py`'s own code, running as a live backend process with
`SUPABASE_SERVICE_ROLE_KEY` set. That key is a real secret I deliberately
never fetched or asked for (Supabase's anon/publishable keys are meant to
be public; service_role is not) - the user needs to set it directly as an
env var in their deployment, never pasted into this chat. Until that
happens and someone does one real signed-in save/list/delete through the
actual running app, treat the backend↔Supabase write path as "individually
verified, not end-to-end verified."

**Env vars the user needs to set** (names only were requested; the two
non-secret values are given directly since Supabase publishable/anon keys
are meant to ship in client code):
- Backend deploy (e.g. Render): `SUPABASE_URL=https://agzvhessbwwhectuizko.supabase.co`,
  `SUPABASE_SERVICE_ROLE_KEY=<from Project Settings → API → service_role, kept secret>`
- Frontend deploy (e.g. Vercel): `NEXT_PUBLIC_SUPABASE_URL=https://agzvhessbwwhectuizko.supabase.co`,
  `NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFnenZoZXNzYnd3aGVjdHVpemtvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA0Mjc5ODAsImV4cCI6MjEwNjAwMzk4MH0.9kEUTIfY5ugnjxc8xpCmddbc9ElztCDl9kJDhQnbb_U`

S5's own "done when" (STRATEGY.md): "a logged-in user saves a research item"
- built and individually verified, not yet end-to-end tested (needs the
service_role key, see above). "cache survives restart" - the Supabase-backed
L2 cache does this by construction (it's a Postgres table), but again not
yet exercised by a live request. "rate limit test" - `tests/test_supa.py`
and `tests/test_api.py` cover this directly (IP window, per-IP isolation,
window expiry, 429 propagation through `/api/chat`).

97/97 backend tests pass (was 89; +8 for supa.py + auth/quota/rate-limit
routes). Frontend `next build` succeeds; new `/saved` route and `AuthWidget`
compile cleanly.

### S4 — Search + law browser UI (2026-09-26)

- **Backend**: `retrieval.py` gained a doc-browser layer on top of the
  existing BM25 index — `doc_slug(title)` (stable hash-based id, works for
  every entry whether or not it has S2's `doc_id`, since curated entries
  never do), `Index.doc(slug)` (doc metadata + ordered section list) and
  `Index.section(slug, section)` (one section + prev/next), both built from
  parallel arrays already in memory (no extra storage). `doc()` backfills
  `enacted_bs`/`amended_by` via `extract_doc_meta()` for pre-S2 corpus rows
  the same way `_entry_status()` already backfills `status`, so the browser
  shows real dates without a corpus rebuild. `search()` gained `doc_type`
  and `status` filters (`status` takes precedence over the default
  bill-exclusion, so `status=bill` explicitly asks for them back).
  `INDEX_VERSION` 3→4. New routes: `GET /api/law/{slug}`,
  `GET /api/law/{slug}/{section}`; `/api/search` gained `doc_type`/`status`
  query params; `Source` gained `slug`/`section`/`status` so search results
  can link straight into the browser.
- **Frontend**: `/search` (query + category/doc-type/in-force filters,
  result cards linking into the browser or the official source for
  precedents), `/law/[slug]` (doc metadata, status pill, enactment date,
  amendment list, official PDF link, section list), `/law/[slug]/[section]`
  (full bilingual text, citation, prev/next nav). A bill's status pill and
  red warning banner ("This is a draft bill...") show automatically wherever
  `status !== "in_force"` — the S2/S3.1 trust-risk work now has a UI, not
  just an API-level filter. Nav links added between chat/search/law pages.
- **Verified in a real browser**, not just `next build`: started both dev
  servers, drove `/search` with Playwright (mobile 390×844 viewport),
  confirmed filters render and a real query returns result cards with
  correct badges/citations, confirmed `/law/[slug]` and `/law/[slug]/[section]`
  render real corpus content (dates, amendments, section nav) via
  server-rendered HTML fetched directly from the running backend, and
  confirmed the bill-warning banner actually renders for the curated bill
  entry from S3.1. Screenshots reviewed, not just captured.
- 89/89 backend tests pass (was 82; +7 for the law-browser retrieval methods
  and API endpoints, +1 for the new search filters). Frontend `next build`
  succeeds; new routes `/search`, `/law/[slug]`, `/law/[slug]/[section]`
  compile as expected (static/dynamic split shown in the build output).

**Embedding benchmark** (`eval/embedding_benchmark.py`, new): STRATEGY says
ship a hybrid retriever only if it wins on the 150-question eval, so this
measures it instead of assuming it either way. Downloaded
`Xenova/multilingual-e5-small` (ONNX int8, 118MB — matches the ~120MB
estimate) and re-ranked BM25's own top-50 candidates per question with
cosine similarity, fused at a few weights. No hosted-embedding API key is
available in this environment, so only the local e5-small arm was
benchmarked (STRATEGY's other arm — "a hosted embedding API for queries" —
is untested here).

| Mode | hit@8 | hit@3 | MRR |
|---|---|---|---|
| BM25 only (this session's baseline) | 0.760 | 0.678 | 0.616 |
| hybrid, alpha=0.3 | 0.801 | 0.719 | 0.634 |
| **hybrid, alpha=0.5** | **0.808** | **0.726** | **0.636** |
| hybrid, alpha=0.7 | 0.795 | 0.678 | 0.589 |
| e5-small only (alpha=1) | 0.733 | 0.534 | 0.451 |

**Hybrid wins clearly** (alpha 0.3–0.5: +4–5pt hit@8, +2pt MRR over BM25
alone; e5 alone is worse than BM25 alone on every metric — this corpus's
custom Nepali BM25 tokenisation is doing real work a generic multilingual
embedding doesn't replace, it only complements it). **Not shipped this
session** despite winning the quality test, for two reasons found while
benchmarking, both about *how* to ship it rather than *whether*:

1. **Latency**: embedding 50 BM25 candidates per request took ~730ms on
   CPU (query embedding itself is ~3ms - it's re-embedding the candidate
   passages on every request that's expensive). STRATEGY's own target is
   p50 search < 300ms. As benchmarked (embed-candidates-at-request-time),
   hybrid search would blow that budget by 2x+. The fix is precomputing and
   storing embeddings for the corpus once (offline), leaving only the ~3ms
   query embedding at request time - real engineering (storage format,
   memory budget alongside the existing BM25 index, a rebuild step in
   `build_corpus.py`), not a config flag.
2. **Memory**: the ONNX model itself is 118MB, close to STRATEGY's own
   flagged Render free-tier ceiling (512MB total, alongside the BM25 index,
   FastAPI, everything else) - worth a real memory-budget check before
   committing, not just "it downloaded fine here."

Also a methodology caveat worth flagging rather than hiding: alpha was
swept on the same 150-question set used everywhere else in this project's
evals (there's no held-out set) — a real production decision should
re-validate on different questions before trusting alpha=0.5 specifically,
even though the *direction* of the result (hybrid > BM25 > nothing, e5
alone < BM25 alone) is unambiguous enough across three alpha values to act
on. Recommended as a follow-up session's task, not squeezed into S4:
precompute corpus embeddings, measure real request latency and memory
end-to-end, re-validate alpha on a fresh question set, then ship.

### S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check)

Before starting S4, checked whether the S2 corpus/pipeline work was actually
complete end-to-end rather than assuming it — found a real gap and fixed it.

- **Confirmed**: `sources/processed/law_docs.jsonl`, `sources/nkp/cases.jsonl`,
  and the raw scraped Law Commission/NKP PDFs are genuinely not present in
  this checkout (as known issue #7 already said) - only 7 standalone PDFs
  live directly in `sources/` (constitution, legal maxims, 5 finance
  bills/acts from BS 2082-2083), meant for one-off ingestion via
  `scripts/ingest_pdfs.py` (needs `GEMINI_API_KEY`, not run this session).
  Of those 5: 2 (`राष्ट्र ऋण उठाउने विधेयक, २०८३` and `वैकल्पिक विकास वित्त
  परिचालन ऐन, २०८२`) were already ingested into `backend/app/data/corpus.json`
  in an earlier session; the other 3 (`आर्थिक विधेयक, २०८३`, `विनियोजन ऐन
  २०८३`, `विशेष सेवा ऐन जगाउने ऐन`) have never been ingested - just sitting
  as raw PDFs, not in the corpus at all. Not fixed this session (needs a key
  this environment doesn't have); noted in Known issues.
- **Bug found and fixed**: the already-ingested `राष्ट्र ऋण उठाउने विधेयक,
  २०८३` curated entry - a literal draft bill for national debt, never
  passed - had **no `status` field and no `doc_title_ne`**, and my S2
  fallback (`retrieval.py::_entry_status`) only checked `doc_title_ne` for
  curated entries, so it silently fell through to `in_force` and was fully
  citable by default (curated entries also get a 1.08x authority-prior
  boost, so this bill would rank *better* than average, not worse). Verified
  end-to-end: before the fix, it appeared in default search; after, it's
  excluded (still reachable with `include_bills=True`) and `by_status.bill`
  in `/api/stats` went from 348 to 356 chunks.
- **Root cause of the miss, for real**: even `e.get("doc_title_ne") or
  e.get("title_ne") or e.get("source_ne")` isn't enough - this entry's
  `title_ne` ("राष्ट्र ऋण उठाउन सक्ने") doesn't say "विधेयक" at all; only its
  `source_ne` ("राष्ट्र ऋण उठाउने विधेयक, २०८३") does. An `or`-chain stops at
  the first non-empty field, so it never reached `source_ne`. Fixed in both
  `retrieval.py::_entry_status` and `build_corpus.py::curated_entries()` to
  check all three fields, not just the first non-empty one - caught by a
  fixture shaped exactly like the real entry
  (`tests/fixtures.py::national-debt-raising-bill-2083-section-2`) plus a
  regression test that failed against my first attempted fix before I found
  the `or`-chain bug.
- 82/82 tests pass (was 81; +1 curated-bill regression test). Retrieval eval
  unchanged (hit@8 0.760, MRR 0.616 - identical to S2/S3, as expected since
  this only touches bill-status classification, not ranking).

### S3 — LLM-free hot path (2026-09-26)

- **Expanded intent regex** (`app/generation.py::quick_intent`): added
  `SMALLTALK_RE` ("who are you", "what can you do", "तिमी को हौ", ...) and a
  deliberately narrow `OFF_TOPIC_HINT_RE` (weather/jokes/songs/movies) —
  narrow on purpose, since a false positive here sends a real legal question
  a canned refusal, which is worse than just asking the LLM. Both return
  before any LLM call, same as the existing greeting/thanks regexes.
- **Confidence-gated skip of the analyze LLM call**
  (`generation.confidence()` + `CONFIDENCE_THRESHOLD = 0.6`): a Nepali-script
  message is confident by default (statutes are all Nepali, so the raw
  message already searches directly); an English/romanised message is
  confident when `glossary.expand()` recognises its vocabulary. When
  confident **and there's no conversation history**, `analyze_query()`
  returns immediately with a locally-built analysis (no LLM call) instead of
  calling the LLM to rewrite the query — `build_queries()` already applies
  the same glossary expansion regardless of whether `analyze_query` called
  the LLM, so retrieval quality for the skipped case is identical to the
  existing LLM-unavailable ("raw") path, not degraded. Follow-up messages
  (history present) always go through the LLM, since resolving "what about
  daughters?" into a standalone question needs it.
- `generation.analyze_needs_llm()` factors the same short-circuit logic out
  of `analyze_query()` so `run()`'s `llm_calls` counter (from S1) stays
  accurate without duplicating the decision.
- `tests/test_hot_path.py` (new): confirms `llm.complete` is genuinely never
  invoked for a confident, no-history message (monkeypatches it to raise if
  called), confirms it *is* still called for a low-confidence message and
  for any follow-up, and covers the new regexes.

**Done-when, measured against the real 150-question eval set**
(`config.GEMINI_API_KEY` set to a dummy value so `llm.available()` is `True`,
matching how the check runs in production — the same trick S1's structural
`llm_calls` reasoning used, since this environment has no real provider
keys):

| Metric | Target | Result |
|---|---|---|
| % of eval questions that skip the analyze call | ≥70% | **88%** (132/150) |
| hit@8 vs. S1 baseline | within 2 pts | **0 pts** (identical by construction — the skipped path builds queries exactly like the existing raw-mode path) |

81/81 backend tests pass (was 75; +6 for S3).

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
4. ~~No rate limiting on `/api/chat`~~ — **fixed in S5**: IP-hourly limit on
   every request, per-user daily quota on authenticated ones
   (`app/supa.py::check_ip_rate_limit`/`check_and_increment_quota`).
   Individually verified (see S5 notes); not yet exercised by a live request
   against the real deployment (needs `SUPABASE_SERVICE_ROLE_KEY` set).
5. ~~In-memory LRU caches ... lost on every restart, not keyed by
   corpus_version~~ — **fixed in S5**: `_analysis_cache` stays in-memory
   (its output doesn't depend on corpus content, no need to persist it), but
   `_answer_cache` now has a Supabase-backed L2 behind it, keyed by
   `corpus_version`, surviving restarts. Same caveat as #4: not yet
   exercised live.
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
10. 3 of the 7 standalone PDFs in `sources/` (`आर्थिक विधेयक, २०८३`,
    `विनियोजन ऐन २०८३`, `विशेष सेवा ऐन जगाउने ऐन`) have never been ingested —
    they aren't in the corpus in any form, so questions about them get no
    answer at all (not a wrong-answer risk, just a coverage gap). Needs
    `scripts/ingest_pdfs.py` run with `GEMINI_API_KEY` set, which this
    environment doesn't have.

## Later (ideas raised but out of scope for the current session)

- Fix `_doc_type()` in `build_corpus.py` to stop matching "ऐन"/"विधेयक" as a
  bare substring (issue 1 above) — cosmetic now that status handles the
  trust-risk part, but `doc_type` still mislabels a few report/study
  documents as `act`.
- Repealed-act detection (issue 9 above).
- Treaty and OCR-damaged-header date extraction (issue 8 above).
- Run `scripts/ingest_pdfs.py` for the 3 un-ingested finance PDFs once a
  Gemini key is available (issue 10 above).
