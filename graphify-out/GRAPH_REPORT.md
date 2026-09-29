# Graph Report - LegalNeps  (2026-09-29)

## Corpus Check
- 102 files · ~141,515 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 2, .example 2, .gz 2)

## Summary
- 1293 nodes · 2642 edges · 89 communities (71 shown, 18 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4b515f8e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- scrape_nkp.py
- test_calculators.py
- test_drafting.py
- llm.py
- playbooks.py
- test_api.py
- PDF Text Extraction
- supa.py
- run_eval.py
- Graphify Tool Documentation
- package.json
- extract_doc_meta
- Index
- devanagari_glyphs.py
- test_s12_compliance_radar.py
- tokenize
- Web Crawler Implementation
- Project Strategy and Prompts
- TypeScript Configuration
- test_s10_ai_and_save.py
- retrieval.py
- resolve_provision
- compliance.py
- render.py
- Corpus Manifest Data
- Civil Law Playbooks
- Graph Export Documentation
- dates.py
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- test_hot_path.py
- Personal Loan Playbooks
- Sexual Harassment Playbooks
- _require_matter
- Folder Watching Documentation
- Git Hook Documentation
- Incremental Update Documentation
- Theft Complaint Playbooks
- Traffic Compensation Playbooks
- Dependency and CI Workflows
- GitHub Integration Documentation
- Media Transcription Documentation
- Root Claude Documentation
- Local Claude Documentation
- Extraction Specification
- Next.js Configuration
- next-env.d.ts
- Cheque Bounce Playbook
- Citizenship Playbook
- Consumer Complaint Playbook
- Domestic Violence Playbook
- FIR Registration Playbook
- Employment Fraud Playbook
- Land Dispute Playbook
- RTI Request Playbook
- FakeMattersStore
- get
- chat
- scrape_lawcommission.py
- limitation.py
- chat.py
- ai_fill.py
- test_s13_ai_gateway.py
- generation.py
- main.py
- app/page.tsx
- AuthWidget
- os
- ai_fill_field
- post
- build_corpus.py
- embedding_benchmark.py
- _LRU
- ingest_scraped.py
- test_s11_matters.py
- next
- search/page.tsx
- ingest_pdfs.py
- test_s14_security.py
- _FakeResponse
- react
- Done
- Progress
- saved/page.tsx
- [slug]/page.tsx

## God Nodes (most connected - your core abstractions)
1. `available()` - 47 edges
2. `_http()` - 42 edges
3. `get_index()` - 27 edges
4. `complete()` - 24 edges
5. `run()` - 23 edges
6. `analyze_query()` - 22 edges
7. `FakeMattersStore` - 21 edges
8. `tokenize()` - 20 edges
9. `resolve_provision()` - 19 edges
10. `Index` - 19 edges

## Surprising Connections (you probably didn't know these)
- `S8 — Calculators (2026-09-27)` --references--> `check()`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/limitation.py
- `Known issues` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `S2 — Legal data engine v2 (2026-09-26)` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `S4 — Search + law browser UI (2026-09-26)` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `Known issues` --references--> `classify_status()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (89 total, 18 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.14
Nodes (26): upcoming_obligations(), Amendment, Analysis, Bilingual, CourtFeeEstimateResponse, DraftingField, DraftingTemplateDetail, DraftingTemplateSummary (+18 more)

### Community 1 - "api.ts"
Cohesion: 0.13
Nodes (18): ActionPlanPage(), Bi(), ProvisionCard(), LawSectionPage(), Amendment, Bilingual, ChatResponse, getLawSection() (+10 more)

### Community 2 - "scrape_nkp.py"
Cohesion: 0.17
Nodes (13): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+5 more)

### Community 3 - "test_calculators.py"
Cohesion: 0.12
Nodes (25): appeal_fee(), court_fee(), estimate(), estimate_appeal(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its… (+17 more)

### Community 4 - "test_drafting.py"
Cohesion: 0.19
Nodes (13): render_docx(), parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne() (+5 more)

### Community 5 - "llm.py"
Cohesion: 0.07
Nodes (52): _anthropic_complete(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini(), _gemini_cfg() (+44 more)

### Community 6 - "playbooks.py"
Cohesion: 0.07
Nodes (36): _keyword_hit_fraction(), _keyword_weight(), Match, _playbook_keywords(), _query_tokens(), Non-LLM query -> playbook routing (S7). Scores each playbook's `keywords` list…, Longer, more specific phrases count for more than a bare one-word keyword, so a…, 1.0 for an exact phrase hit, else the fraction of the keyword's own words that… (+28 more)

### Community 7 - "test_api.py"
Cohesion: 0.05
Nodes (19): focus(), normalize_citations(), The part of a passage that matters for this question: the heading line plus the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, client(), fixture (+11 more)

### Community 8 - "PDF Text Extraction"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.06
Nodes (78): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, all_company_profiles(), audit_log(), available(), cache_get(), cache_put(), check_and_increment_quota() (+70 more)

### Community 10 - "run_eval.py"
Cohesion: 0.28
Nodes (18): analyze_query(), search(), available(), parse_json(), get_index(), detect_language(), cmd_e2e(), cmd_retrieval() (+10 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.08
Nodes (23): dependencies, next, react, react-dom, @supabase/supabase-js, devDependencies, @types/node, @types/react (+15 more)

### Community 13 - "extract_doc_meta"
Cohesion: 0.16
Nodes (19): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, parametrize (+11 more)

### Community 14 - "Index"
Cohesion: 0.12
Nodes (11): Index, _index_text(), _prior(), ndarray, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., Authority of the source x usefulness of this particular passage. (+3 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "test_s12_compliance_radar.py"
Cohesion: 0.12
Nodes (5): compliance_client(), FakeComplianceStore, fixture, S12: Compliance Radar lite - company profile, obligations, upcoming-due…, test_reminder_job_dedups_via_reminders_sent()

### Community 17 - "tokenize"
Cohesion: 0.18
Nodes (18): fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term() (+10 more)

### Community 18 - "Web Crawler Implementation"
Cohesion: 0.18
Nodes (4): Crawler, push(), Icon-only PDF links (common on the category tables) carry no anchor text; fall…, Listing pages (category tables, index pages, pagination) link directly to every…

### Community 19 - "Project Strategy and Prompts"
Cohesion: 0.11
Nodes (17): Add-ons for specific sessions (append to the kickoff), Session prompts, Universal kickoff prompt (paste this at the start of every session), When to switch models yourself, 1. What already exists, 2. Changes to the original roadmap, 3. Target architecture, 4. Session plan (1 session = 1 milestone = 1 PR) (+9 more)

### Community 20 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "test_s10_ai_and_save.py"
Cohesion: 0.13
Nodes (14): fill(), Expand `hint` into fuller prose for `field_id` of `template_id`, in `language`,…, requires_corpus, S10: LLM-assisted free-text fill for drafting templates, plus saving a draft…, test_ai_fill_endpoint_bad_field(), test_ai_fill_endpoint_requires_auth_and_is_metered(), test_ai_fill_expands_hint_via_llm(), test_ai_fill_includes_other_answers_as_context() (+6 more)

### Community 22 - "retrieval.py"
Cohesion: 0.13
Nodes (17): array, _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, size(), corpus_source(), BM25 search over the government-sourced corpus (laws + precedents). The corpus… (+9 more)

### Community 23 - "resolve_provision"
Cohesion: 0.15
Nodes (17): gratuity(), notice(), notice_period_days(), Labour Act, 2074 (श्रम ऐन, २०७४) calculators (S8): gratuity, termination…, दफा ५३: उपदान accrues at 8.33% of basic monthly pay for every month worked,…, दफा १४४(१): minimum notice before ending an employment relationship (either…, दफा १४४: the notice period owed, and the pay-in-lieu (दफा १४४(२)/(३)) if the…, दफा १४५(७): one month's basic pay per completed year of service as a lump-sum… (+9 more)

### Community 24 - "compliance.py"
Cohesion: 0.18
Nodes (20): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+12 more)

### Community 25 - "render.py"
Cohesion: 0.17
Nodes (16): _build_context(), get_template(), get_template_detail(), list_templates(), MissingField, ValueError, Questionnaire answers -> rendered DOCX (S9). Each template's paragraphs are…, [(text, bold, align), ...] for every non-empty paragraph of `template_id`… (+8 more)

### Community 26 - "Corpus Manifest Data"
Cohesion: 0.20
Nodes (9): built_at, counts, curated, law_chunks, law_documents, precedents, total, digest (+1 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Documentation"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "dates.py"
Cohesion: 0.16
Nodes (14): ad_to_bs(), bs_to_ad(), date, ValueError, BS <-> AD date conversion (S8). Nepal's Bikram Sambat calendar has variable…, Outside the BS calendar table this build ships with., UnsupportedDate, test_ad_to_bs_rejects_out_of_range() (+6 more)

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "test_hot_path.py"
Cohesion: 0.12
Nodes (23): analyze_needs_llm(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message is a legal question we can search well without an…, Whether analyze_query() will reach a provider for this message - kept in sync…, Weighted query set: the LLM's Nepali legal phrasings carry most weight;… (+15 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "_require_matter"
Cohesion: 0.13
Nodes (19): create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task(), delete_research(), download_matter_file() (+11 more)

### Community 37 - "Folder Watching Documentation"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 38 - "Git Hook Documentation"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 39 - "Incremental Update Documentation"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 40 - "Theft Complaint Playbooks"
Cohesion: 0.67
Nodes (3): Theft Complaint Playbook, Muluki Aparadh Sanhita, 2074 Section 242, Muluki Faujdari Karyavidhi Sanhita, 2074 Section 4 (1)

### Community 41 - "Traffic Compensation Playbooks"
Cohesion: 0.67
Nodes (3): Traffic Accident Compensation Playbook, Sawari tatha Yatayat Wyawastha Ain, 2049 Section 152, Sawari tatha Yatayat Wyawastha Ain, 2049 Section 163

### Community 42 - "Dependency and CI Workflows"
Cohesion: 0.67
Nodes (3): Backend Dependencies, Script Dependencies, CI Workflow

### Community 60 - "get"
Cohesion: 0.10
Nodes (28): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+20 more)

### Community 61 - "chat"
Cohesion: 0.14
Nodes (20): chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_request(), Request (+12 more)

### Community 62 - "scrape_lawcommission.py"
Cohesion: 0.15
Nodes (16): build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text. (+8 more)

### Community 63 - "limitation.py"
Cohesion: 0.25
Nodes (6): LimitationRule, ValueError, Limitation-period (हदम्याद) checker (S8). मुलुकी देवानी कार्यविधि संहिता दफा ४९…, UnknownClaimType, calendar, dataclasses

### Community 64 - "chat.py"
Cohesion: 0.13
Nodes (23): corpus_stats(), get_company_profile(), law_doc(), list_llm_usage(), match_playbooks(), put_company_profile(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, Cost-per-query visibility (STRATEGY's S13 "done when" bar): every paid-tier… (+15 more)

### Community 65 - "ai_fill.py"
Cohesion: 0.22
Nodes (12): _build(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, UnknownField, Field, Paragraph (+4 more)

### Community 66 - "test_s13_ai_gateway.py"
Cohesion: 0.06
Nodes (34): fill_paid(), S13: same expansion, billed to a specific paid-tier model…, paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, looks_like_injection(), daily_quota_for(), S13: plan-based tier routing and token-cost accounting. STRATEGY.md §2's…, `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).… (+26 more)

### Community 67 - "generation.py"
Cohesion: 0.18
Nodes (17): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), _history_text(), _passage(), _prompt(), Question understanding -> retrieval -> grounded answer. 1. analyze_query: a… (+9 more)

### Community 68 - "main.py"
Cohesion: 0.12
Nodes (16): asyncio, _GZipExceptStreams, health(), lifespan(), get, Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies() (+8 more)

### Community 69 - "app/page.tsx"
Cohesion: 0.29
Nodes (12): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), ChatMessage(), Message, saveResearch(), sendChatMessage() (+4 more)

### Community 70 - "AuthWidget"
Cohesion: 0.30
Nodes (12): AuthWidget(), handleSendCode(), handleVerify(), authAvailable(), getSession(), onAuthChange(), sendOtp(), signOut() (+4 more)

### Community 71 - "os"
Cohesion: 0.22
Nodes (10): argparse, main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, main(), OCR for documents extract_laws.py flagged `needs_ocr` (scanned PDFs, or text…, render(), transcribe(), os (+2 more)

### Community 72 - "ai_fill_field"
Cohesion: 0.28
Nodes (9): ai_fill_field(), _log_llm_usage(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, S13: writes one llm_usage row per real (non-cached, non-free-tier) generation,…, _record_llm_usage_sync(), AiFillRequest, AiFillResponse, estimate_cost_usd() (+1 more)

### Community 73 - "post"
Cohesion: 0.15
Nodes (13): create_draft(), create_matter(), create_matter_note(), draft_document(), save_research(), DraftRequest, MatterIn, MatterNoteIn (+5 more)

### Community 74 - "build_corpus.py"
Cohesion: 0.24
Nodes (11): _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -…, Earlier hand-verified constitution-art-N entries carry English translations;…, First substantial Devanagari line of the document (its printed title). (+3 more)

### Community 75 - "embedding_benchmark.py"
Cohesion: 0.23
Nodes (8): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), statistics

### Community 77 - "ingest_scraped.py"
Cohesion: 0.27
Nodes (11): ask_json(), load_corpus(), load_ingested(), load_manifest(), main(), Step 2 of the scrape pipeline: turns documents downloaded by…, save_corpus(), save_ingested() (+3 more)

### Community 78 - "test_s11_matters.py"
Cohesion: 0.18
Nodes (5): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 79 - "next"
Cohesion: 0.20
Nodes (6): ActionPlansPage(), AREA_LABEL, frontend_app_globals, metadata, listPlaybooks(), next

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "ingest_pdfs.py"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 82 - "test_s14_security.py"
Cohesion: 0.20
Nodes (6): api_client(), fixture, S14: security + reliability. Covers what's unit-testable from this sandbox…, test_matter_file_upload_over_cap_is_rejected_without_buffering_whole_body(), io, pytest

### Community 83 - "_FakeResponse"
Cohesion: 0.22
Nodes (4): _FakeHttp, _FakeResponse, test_draft_delete_writes_an_audit_log_entry(), test_matter_delete_writes_an_audit_log_entry()

### Community 84 - "react"
Cohesion: 0.24
Nodes (5): DEV_DIGITS, inline(), renderAnswer(), toAscii(), react

### Community 85 - "Done"
Cohesion: 0.32
Nodes (7): _entry_status(), One section's full entry plus neighbouring sections, for /law/[doc]/[section]., curated_entries(), Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S4 — Search + law browser UI (2026-09-26)

### Community 86 - "Progress"
Cohesion: 0.40
Nodes (6): _doc_type(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Next session, Progress

### Community 87 - "saved/page.tsx"
Cohesion: 0.53
Nodes (5): SavedPage(), handleDelete(), deleteSavedResearch(), listSavedResearch(), SavedResearch

### Community 88 - "[slug]/page.tsx"
Cohesion: 0.67
Nodes (3): DOC_TYPE_LABEL, LawDocPage(), getLawDoc()

## Knowledge Gaps
- **154 isolated node(s):** `LimitationRule`, `built_at`, `curated`, `law_chunks`, `precedents` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 472 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `supa.py` to `generation.py`, `AuthWidget`, `run_eval.py`, `Done`, `chat`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `AuthWidget` to `api.ts`, `app/page.tsx`, `supa.py`, `next`, `search/page.tsx`, `saved/page.tsx`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `get_index()` connect `run_eval.py` to `chat.py`, `generation.py`, `main.py`, `playbooks.py`, `supa.py`, `embedding_benchmark.py`, `Index`, `retrieval.py`, `resolve_provision`, `get`, `chat`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LimitationRule`, `built_at`, `curated` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1396011396011396 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._