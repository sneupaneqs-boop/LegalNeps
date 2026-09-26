# Kanooni Sathi: rules for Claude

Bilingual (EN/NE) Nepal legal app. Grounded **only** in official sources (Law Commission, NKP).
Plan: `docs/STRATEGY.md`. Current state and next session: `docs/PROGRESS.md`. Read PROGRESS first. Read STRATEGY only for the section you need.

## Layout
- `backend/app/`: FastAPI. `retrieval.py` (BM25 + SQLite passage store), `generation.py` (understand → search → answer), `llm.py` (provider chains, time budgets), `text_norm.py` (Nepali folding), `glossary.py`, `config.py`
- `backend/scripts/`: scrapers, PDF extraction, corpus builders · `backend/eval/`: retrieval/e2e eval · `backend/tests/`: pytest
- `frontend/`: Next.js 14 app router, no UI library
- `backend/app/data/corpus/*.jsonl.gz`: built corpus. **Never read it directly.** Inspect it with a short Python one-liner that prints counts or one record.

## Commands
- Tests: `cd backend && python3 -m pytest -q 2>&1 | tail -15` (script tests need `pip install -r requirements-scripts.txt`)
- Retrieval eval: `cd backend && python3 eval/run_eval.py retrieval` (no LLM, ~1 min)
- Frontend: `cd frontend && npm run build`

## Non-negotiables
1. Never invent law. Every legal statement in an answer, playbook, calculator or template cites a provision that exists in the corpus. Add a test that proves it.
2. Deterministic before AI: rules → cache → retrieval → free LLM chain → Claude. Any new LLM call needs a reason in the PR description and must be metered.
3. Don't regress the eval. Run the retrieval eval before and after any change to search or text_norm. Paste both numbers in the PR.
4. Keep existing behaviour: streaming, time budgets, extractive fallback when no LLM responds.
5. Secrets only in env vars. RLS on every Supabase table.

## How to work (token budget)
- One session = one milestone from PROGRESS. Don't add features outside it; log ideas in PROGRESS "Later".
- Locate before reading: use Grep/Glob, then read only the line ranges you need. Delegate broad searches to the `scout` subagent (Haiku).
- Run tests and evals through the `runner` subagent (Haiku), or pipe to `tail`. Don't paste full logs.
- Use the `architect` subagent (Opus) only for: schema/data-model design, auth/RLS design, security review, or a bug that survived 2 fix attempts. Give it a tight brief with file paths.
- Drafting bulk content (playbooks, templates, translations): Haiku drafts, you verify citations against the corpus.
- Match surrounding code style. Keep comments sparse.
- End of session: update `docs/PROGRESS.md` (done, metrics, next), commit, push, and open a PR if asked.
