# Session prompts — V2 (commercial build)

Use with `docs/STRATEGY_V2.md`. One session = one milestone (V1…V22). Start a fresh Claude Code
session (or `/clear`) for each one, paste the **master prompt**, and append the session's add-on
from the table below if it has one.

## Master prompt (paste at the start of every session)

```
You are building Kanooni Sathi into a commercial, evidence-grounded Nepali legal intelligence
platform: it turns a legal problem into verified law -> evidence -> an action plan -> the
document the user needs. Repo: this one. Live: kanooni-sathi.vercel.app (frontend, Next 15),
kanooni-sathi-api.onrender.com (FastAPI), Supabase project "LegalNeps" (agzvhessbwwhectuizko).

1. Orient. Read docs/PROGRESS.md "Next session", then only that session's row and the sections
   of docs/STRATEGY_V2.md it depends on. Use `graphify query "<question>"` before reading source
   files (see CLAUDE.md). Do exactly one V-session.

2. Plan in at most 10 bullets: files to touch, tests to add, and how you will PROVE the
   session's "Done when" - with a measurement or a live check, not an assertion.

3. Non-negotiable product rules:
   - Never invent a law, section, case number, deadline, fee or procedure. Every legal claim
     comes from a passage retrieved from our corpus; if it isn't there, say so.
   - Numbers in a legal claim (days, rupees, %, section numbers) must appear in the cited passage.
   - Never present a repealed provision or a bill as current law. Show status on every citation.
   - AI for language; deterministic code for math, dates (BS<->AD) and legal rules.
   - Model output that drives UI or logic is structured JSON, validated before use.
   - Every model call goes through backend/app/llm.py. Free users -> free chain; paid -> Haiku
     4.5; deep research, contract audit and drafting for paid users -> Sonnet 5.5. Use prompt
     caching on paid calls.
   - "Legal information, not legal advice" everywhere a user reads an answer.
   - No confidence percentages. Show evidence coverage (supported vs not-verified claims).

4. Engineering rules:
   - Every new user-data table ships with RLS, and you verify isolation LIVE with two users
     (SET LOCAL ROLE authenticated + request.jwt.claims inside a rolled-back transaction).
   - Plan/billing fields are writable only by the service role - never by the client.
   - The backend uses the service-role key, so every query also filters by user_id in Python.
   - Tests for every new backend function (monkeypatched supa/llm, same pattern as
     backend/tests/test_s11_matters.py). Keep the whole suite green: `cd backend && python3 -m
     pytest -q`.
   - Touching retrieval or text_norm? Run backend/eval/run_eval.py before and after, on both the
     main and the held-out set, and write both numbers down.
   - Frontend: `npm run build` must pass, then actually load the pages you changed (next start +
     curl, or Playwright once V21 adds it). Say plainly what you could not click through.
   - Preserve existing behavior; refactor incrementally. Don't widen the session's scope - put
     ideas in PROGRESS "Later".

5. Finish (all of it, every session):
   - Prove each "Done when" item, with numbers.
   - Update docs/PROGRESS.md: a new "### Vn - <name> (<date>)" entry under Done (what was built,
     what was verified live vs only in tests, honest gaps), and rewrite "Next session" to the
     next V-session plus any "Still outstanding from Vn" items.
   - Run `graphify update .`, commit with a clear message, push to the working branch.
   - Wait for the Render deploy to show "live" and confirm new routes in /openapi.json. Vercel
     only builds a PREVIEW on push: check it's READY, load it, then promote it to production
     (Vercel create_deployment with that deploymentId and target "production") and confirm
     kanooni-sathi.vercel.app serves the change.
   - Report: what shipped, what's live, measured results, what's still open.

6. Stop and ask me (don't work around it) when something needs money, an account I own
   (Khalti, domain, Supabase/Render plan), a secret you don't have, or a legal judgment.
```

## Session add-ons (append to the master prompt)

| Session | Add-on |
|---|---|
| **V1** | `Start by re-running these two live queries against production and saving the full responses as eval cases: "घरबेटीले deposit फिर्ता दिएन, के गर्ने?" and "My employer has not paid my salary for 4 months. What can I do?" (STRATEGY_V2 §1.2.1 lists what's wrong with each). Build the 50-question held-out set from questions NOT already in backend/eval/questions.jsonl, mixing English, Devanagari and Romanized Nepali across tenancy, labour, family, land, company, tax, criminal, consumer, cyber, banking.` |
| **V2** | `Before writing to Supabase, compute the storage size (chunks x dims x bytes) and confirm it fits the plan's DB limit. Measure warm and cold search latency on the live Render instance after deploy, not just locally.` |
| **V3** | `Design the answer JSON schema first and show it to me in the plan. The verifier must be deterministic code (no LLM judging its own claims). Include tests with deliberately wrong answers: a fabricated section, a wrong number of days, a citation to a passage that wasn't retrieved.` |
| **V4** | `Build the adversarial set: 20 questions whose most likely retrieved authority is a repealed act, a bill, or a pre-2074 precedent under an old law. Report the before/after count of repealed-as-current answers.` |
| **V6** | `Read the claude-api skill before writing any Anthropic code. Use Sonnet 5.5 with tool use and a hard cap on tool calls and tokens per request, and log real token usage to llm_usage.` |
| **V7, V8, V9, V10, V11** | `Read the frontend-design skill first. Mobile-first (most users are on phones), Nepali and English on every screen, fast on a 3G connection. Load every page you touched and describe what you saw.` |
| **V12, V13** | `Uploaded documents are private user data: RLS + storage path isolation + explicit upload consent. Contract-audit checklists live in YAML like the playbooks; every rule cites a verified section id and passes the citation test. Mark any rule you could not verify as UNVERIFIED instead of guessing.` |
| **V15** | `Ask me for the Khalti merchant keys by env var NAME only; never print values. Verify webhook signatures server-side. A plan upgrade must be impossible without a verified payment or an admin action - prove it with a test that tries.` |
| **V16** | `Legal pages are drafts for my advocate to review - label them that way in the PR description.` |
| **V17, V18** | `Scrape politely (rate limit, identify the bot, respect robots.txt). Every ingested item stores source URL, issuing authority, publication date and fetched-at.` |
| **V21** | `Produce docs/LAUNCH_REPORT.md with STRATEGY_V2 §7's metrics table filled with measured numbers. Also do the FastAPI/starlette upgrade left open in S14.` |

## Model guidance
| Situation | Use |
|---|---|
| Normal coding, UI, tests | Sonnet (default) |
| Designing V3 (verifier), V6 (agent), V13 (audit engine), V15 (payments) | Opus to plan, Sonnet to implement |
| Bulk YAML (checklists, glossary, eval questions), running tests | Haiku subagents |
| Context above ~60% | `/compact keep: milestone, files changed, failing tests, metrics` |
