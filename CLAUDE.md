## READ FIRST (new session)

**Start with `docs/HANDOFF.md`** — the full hand-off: what this project is, what is deployed and where, what works, what
failed, what to ignore, what is unfinished. All work lives on branch `claude/dreamy-hawking-4y5lgf` (if you are on another
branch you are looking at an OLD checkout: `git fetch origin && git checkout claude/dreamy-hawking-4y5lgf`).

## Plan

The build plan is `docs/STRATEGY_V2.md` (sessions V1–V22); the kickoff prompt and per-session
add-ons are in `docs/SESSION_PROMPTS_V2.md`; current state and the next session are in
`docs/PROGRESS.md`. `docs/STRATEGY.md` (S1–S15) is history.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
