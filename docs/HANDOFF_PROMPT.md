# Paste this into a new Claude session (self-contained kickoff prompt)

> You are continuing work on **Kanooni Sathi**, a bilingual (Nepali/English) legal-information web app for Nepal
> (FastAPI backend on Render free tier, Next.js 15 frontend on Vercel, Supabase). GitHub repo:
> `sneupaneqs-boop/LegalNeps`. **All the work is on the branch `claude/dreamy-hawking-4y5lgf`** — if your checkout is on
> any other branch (for example `claude/ecstatic-hopper-3yaiot`) it is an old copy with none of the work. Run
> `git fetch origin && git checkout claude/dreamy-hawking-4y5lgf && git pull`.
>
> **Read, in this order:** (1) `docs/HANDOFF.md` (full hand-off: state, deployment IDs, repo map, how the chat pipeline works,
> what works, what failed, what to ignore, unfinished work, next steps); (2) the newest entries at the top of "## Done" in
> `docs/PROGRESS.md` ("V3 outcome and next steps (2026-10-01)", "V2.7 live review (… fresh set C)", "V2.7"); (3)
> `docs/STRATEGY_V2.md` only if you need the long-term plan. Ignore `docs/STRATEGY.md` and `docs/SESSION_PROMPTS.md` (old).
>
> **The situation in 8 lines:**
> 1. Everything is deployed and working except sign-in (needs a Supabase dashboard setting only the founder can change: Site URL
>    `https://kanooni-sathi.vercel.app` + redirect URL `https://kanooni-sathi.vercel.app/**`).
> 2. Backend tests: 1,844 passing (`cd backend && python -m pytest -q`).
> 3. Corpus: 73,667 passages of Nepali law; search = BM25 + e5-small dense, fused. Chat pipeline: LLM query rewrite → hybrid search →
>    playbook pins → topical-fit gate → structured JSON answer → deterministic per-sentence verification → fallback/abstain.
> 4. Every quote shown is real and verbatim (0 invented numbers/sections in all reviews), BUT many sentences cite a real provision that does
>    not govern the user's situation ("wrong-law"). Latest live review on 30 fresh questions: 25% bad sentences (6/24), only 1/30 answers fully
>    correct and useful, 6 of 7 refusals ("no provision found") were wrong. Target was <5%: NOT met.
> 5. Rules + free LLMs have plateaued. Best next route: an advocate-reviewed answer bank for the ~150 most common situations, finishing the
>    unmerged V2.8 branch (`worktree-agent-acf49f3c1aba0dcc1`: title-level retrieval, abstain-gate fix, truthful caveat, regime guards), and a
>    stronger judge model for paying users only.
> 6. Never claim accuracy from tuned sets. All existing question sets are burned; write a NEW fresh set before the next live review.
> 7. Constraints: founder is in Nepal, cannot pay foreign providers → free tiers only (Render free 512 MB; free LLM keys Groq/Gemini that
>    rate-limit). Use Sonnet sub-agents in git worktrees for normal work (tell them to commit early); Opus only if necessary.
> 8. Style: be specific, give a recommendation (no "it depends"), report numbers as measured, say plainly when a target is missed.
>
> Before doing anything: confirm you are on the right branch, run the tests, read the files above, then tell me in 10 lines what you
> understood and what you propose to do first.
