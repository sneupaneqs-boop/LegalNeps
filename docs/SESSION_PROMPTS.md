# Session prompts

Start every session in Claude Code on the web (or the CLI) from this repo. Run `/clear` between sessions. The model defaults to Sonnet via `.claude/settings.json`.

## Universal kickoff prompt (paste this at the start of every session)

```
Read docs/PROGRESS.md and do the session listed under "Next session".
Read only the section of docs/STRATEGY.md for that session.

Workflow:
1. Plan in at most 10 bullets: files to touch, tests to add, how you'll prove "Done when". If the
   session is marked O in STRATEGY, get the design from the `architect` subagent first
   (tight brief, file paths only), then implement it yourself.
2. Use `scout` for broad searches and `runner` for tests/eval/build. Read only the line ranges
   you need.
3. Implement in small steps. Run the relevant tests after each step.
4. If you touch search or text_norm, run the retrieval eval before and after.
5. Finish: every "Done when" item is met and proven, tests pass, docs/PROGRESS.md is updated
   (done, metrics, next session, new known issues), then commit and push to my branch.
Don't build anything outside this session's milestone. Put ideas in PROGRESS "Later".
If something is blocked, stop and tell me what you need instead of working around it.
```

## Add-ons for specific sessions (append to the kickoff)

- **S2:** `Before coding, sample 20 Law Commission PDFs' first page text (via the extraction code, not raw files) to confirm the header patterns for dates and amendment lists.`
- **S5:** `I have a Supabase project. Ask me for SUPABASE_URL / anon key / service key names only. Never print values.`
- **S6/S7:** `Use the drafter subagent for playbook YAML. Then verify every provision ID with the citation test yourself. Flag anything the drafter marked UNVERIFIED.`
- **S14:** `Run /security-review on the diff since S5, and send the findings to the architect subagent for triage.`
- **S15:** `Produce docs/LAUNCH_REPORT.md with the §6 metrics table.`

## When to switch models yourself
| Situation | Do |
|---|---|
| Normal coding, tests, UI, bug fixes | Stay on Sonnet (default) |
| S2 / S5 / S14 design, or stuck after 2 attempts | Let it call `architect`, or type `/model opusplan` (Opus plans, Sonnet executes), then `/model sonnet` |
| Pure search, running tests, bulk YAML/translation | Haiku subagents (automatic via `scout` / `runner` / `drafter`) |
| Context above ~60% | `/compact keep: milestone, files changed, failing tests, metrics` |
