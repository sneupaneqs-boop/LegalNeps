# Progress log

Claude: read this at the start of every session. Update it at the end.

## Next session
**S1: Baseline + CI** (see STRATEGY §4)

## Baseline metrics
| Metric | S1 baseline | Latest |
|---|---|---|
| Retrieval hit@8 (150 q) | - | - |
| MRR | - | - |
| % legal questions with ≥1 LLM call | 100% (analyze + answer on every legal question) | - |
| App tests | 36 pass | - |

## Done
- **S0 (audit, 26 Sep 2026):** strategy v2 written; fixed pydantic pin (fresh installs were failing); added CLAUDE.md, model-routing subagents, and a token-saving permission deny list.

## Sessions
- [ ] S1 Baseline + CI
- [ ] S2 Legal data engine v2 (status/dates/amendments, bills out)
- [ ] S3 LLM-free hot path
- [ ] S4 Search + law browser UI, embedding benchmark
- [ ] S5 Supabase auth + DB + persistent cache + quotas
- [ ] S6 Action Plan engine + 8 playbooks
- [ ] S7 +17 playbooks + matcher
- [ ] S8 Calculators
- [ ] S9 Drafting engine + 6 templates
- [ ] S10 AI fill + 4 templates + versions  ← 2-week free beta cut-off
- [ ] S11 Matter workspace lite
- [ ] S12 Compliance Radar lite
- [ ] S13 AI gateway v2 (tiers, cost, quotas)
- [ ] S14 Security + reliability
- [ ] S15 QA + launch

## Known issues
- 9 bills (विधेयक) tagged as `act`; no status/date/amendment metadata (S2)
- 8,685 `other` chunks in default search (S2)
- No rate limiting on /api/chat (S5)
- Answer cache is in-memory only and ignores corpus version (S5)

## Later (don't build now)
- Contract review, doc vault OCR, change monitor, precedent↔section links, Khalti billing, teams
