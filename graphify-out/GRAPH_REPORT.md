# Graph Report - LegalNeps  (2026-09-29)

## Corpus Check
- 178 files · ~317,014 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: .jsonl 7, .css 5, (none) 4)

## Summary
- 2675 nodes · 6351 edges · 133 communities (114 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 262 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `70aef83b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- scrape_nkp.py
- test_calculators_tools.py
- test_v1_trust_engine.py
- llm.py
- playbook_matcher.py
- test_api.py
- extract_laws.py
- supa.py
- get_index
- Graphify Tool Documentation
- package.json
- build_corpus.py
- Index
- devanagari_glyphs.py
- tools.py
- text_norm.py
- Crawler
- Project Strategy and Prompts
- TypeScript Configuration
- test_s10_ai_and_save.py
- test_regulators_ingest.py
- test_calculators.py
- test_s12_compliance_radar.py
- test_drafting.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- _date
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- test_hot_path.py
- Personal Loan Playbooks
- Sexual Harassment Playbooks
- chat.py
- Folder Watching Documentation
- Git Hook Documentation
- Incremental Update Documentation
- Theft Complaint Playbooks
- Traffic Compensation Playbooks
- Dependency and CI Workflows
- GitHub Integration Documentation
- Media Transcription Documentation
- CLAUDE.md
- Local Claude Documentation
- Extraction Specification
- next.config.js
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
- cite
- limitation.py
- list_llm_usage
- forms_common.py
- test_s13_ai_gateway.py
- generation.py
- app/__init__.py
- useLang
- ui.tsx
- playbooks.py
- ingest_regulators.py
- post
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- ai_fill.py
- scrape_regulators.py
- json
- Progress
- test_documents_audit.py
- search/page.tsx
- ics.ts
- test_retrieval.py
- test_s14_security.py
- ChatMessage.tsx
- test_drafting_formats.py
- calculators.tsx
- audit.py
- audit/page.tsx
- segment.py
- extract.py
- dsl.py
- rules.py
- Session prompts — V2 (commercial build)
- retrieval.py
- @playwright/test
- run_audit
- [templateId]/page.tsx
- Done
- checklists.py
- Per-playbook findings
- sources.py
- docx_out.py
- send_compliance_reminders.py
- i18n.ts
- render.py
- extract_doc_meta
- matter_file_create
- scrape_lawcommission.py
- nepali.py
- contract_fixtures.py
- test_chat_route_anonymous_caller_stays_on_free_tier
- looks_like_injection
- smoke.spec.ts
- Env
- scripts
- models.py
- embedding_benchmark.py
- test_playbook_matcher.py
- glossary.py
- devDependencies
- dependencies
- MatterOut
- preeti.ts
- draft_update
- complete
- verifier.py
- ingest_pdfs.py
- review_fee
- check_ip_rate_limit
- _LRU
- match_playbooks
- calendar

## God Nodes (most connected - your core abstractions)
1. `available()` - 47 edges
2. `_http()` - 42 edges
3. `useTools()` - 41 edges
4. `useLang()` - 41 edges
5. `get_index()` - 39 edges
6. `cite()` - 34 edges
7. `_date()` - 34 edges
8. `ToolsPage()` - 32 edges
9. `errorText()` - 32 edges
10. `callJson()` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `S8 — Calculators (2026-09-27)` --references--> `check()`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/limitation.py
- `Known issues` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `S2 — Legal data engine v2 (2026-09-26)` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (133 total, 19 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.10
Nodes (34): ai_fill_field(), law_doc(), law_section(), list_playbooks(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, upcoming_obligations(), AiFillRequest, AiFillResponse (+26 more)

### Community 1 - "api.ts"
Cohesion: 0.05
Nodes (66): formatSize(), add(), remove(), Tab, TasksTab(), add(), patch(), remove() (+58 more)

### Community 2 - "scrape_nkp.py"
Cohesion: 0.16
Nodes (14): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+6 more)

### Community 3 - "test_calculators_tools.py"
Cohesion: 0.07
Nodes (60): bs_month_length(), Number of days in a BS month (29-32; varies by year)., Interest on a private loan from `start` to `end`, with the lawful cap applied.…, simple_interest(), income_tax(), Income tax for resident individuals / couples and tax deducted at source (TDS),…, Tax to deduct at source on a payment of `amount` (NPR). For a contract the Rs…, (from, to, rate%) - the last bracket is open-ended; the surcharge splits the… (+52 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.10
Nodes (35): _is_fiscal_query(), _is_regulator_query(), mark_stale_precedents(), _match_playbook(), A precedent decided before the statute now governing the topic was enacted…, The curated action plan for this situation, when the keyword matcher is…, search(), Returns (answer with unsupported legal claims marked, report). (+27 more)

### Community 5 - "llm.py"
Cohesion: 0.14
Nodes (31): _anthropic_complete(), _client_http(), _cool(), _cool_target(), _gemini(), _gemini_cfg(), _gemini_complete(), _gemini_stream() (+23 more)

### Community 6 - "playbook_matcher.py"
Cohesion: 0.23
Nodes (12): _keyword_hit_fraction(), _keyword_weight(), Match, _playbook_keywords(), _query_tokens(), Non-LLM query -> playbook routing (S7). Scores each playbook's `keywords` list…, Longer, more specific phrases count for more than a bare one-word keyword, so a…, 1.0 for an exact phrase hit, else the fraction of the keyword's own words that… (+4 more)

### Community 7 - "test_api.py"
Cohesion: 0.09
Nodes (10): focus(), normalize_citations(), The part of a passage that matters for this question: the heading line plus the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, client(), fixture, test_focus_keeps_heading_and_the_matching_clause(), test_research_save_list_delete_roundtrip() (+2 more)

### Community 8 - "extract_laws.py"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.18
Nodes (31): available(), company_profile_get(), draft_get(), draft_list(), _http(), llm_usage_list(), llm_usage_record(), matter_create() (+23 more)

### Community 10 - "get_index"
Cohesion: 0.23
Nodes (20): analyze_query(), build_queries(), Weighted query set: the LLM's Nepali legal phrasings carry most weight;…, available(), parse_json(), get_index(), detect_language(), cmd_e2e() (+12 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.22
Nodes (8): name, private, version, react-dom, @types/node, @types/react, @types/react-dom, typescript

### Community 13 - "build_corpus.py"
Cohesion: 0.20
Nodes (14): curated_entries(), _doc_type(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -… (+6 more)

### Community 14 - "Index"
Cohesion: 0.12
Nodes (12): Index, ndarray, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., _title_tokens() (+4 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "tools.py"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "text_norm.py"
Cohesion: 0.20
Nodes (17): fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term() (+9 more)

### Community 18 - "Crawler"
Cohesion: 0.18
Nodes (4): Crawler, push(), Icon-only PDF links (common on the category tables) carry no anchor text; fall…, Listing pages (category tables, index pages, pagination) link directly to every…

### Community 19 - "Project Strategy and Prompts"
Cohesion: 0.11
Nodes (17): Add-ons for specific sessions (append to the kickoff), Session prompts, Universal kickoff prompt (paste this at the start of every session), When to switch models yourself, 1. What already exists, 2. Changes to the original roadmap, 3. Target architecture, 4. Session plan (1 session = 1 milestone = 1 PR) (+9 more)

### Community 20 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "test_s10_ai_and_save.py"
Cohesion: 0.14
Nodes (14): fill(), Expand `hint` into fuller prose for `field_id` of `template_id`, in `language`,…, requires_corpus, S10: LLM-assisted free-text fill for drafting templates, plus saving a draft…, test_ai_fill_endpoint_bad_field(), test_ai_fill_endpoint_requires_auth_and_is_metered(), test_ai_fill_expands_hint_via_llm(), test_ai_fill_includes_other_answers_as_context() (+6 more)

### Community 22 - "test_regulators_ingest.py"
Cohesion: 0.16
Nodes (10): _text_key(), _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip() (+2 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.06
Nodes (51): appeal_fee(), court_fee(), estimate(), estimate_appeal(), flat_fee(), flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2)). (+43 more)

### Community 24 - "test_s12_compliance_radar.py"
Cohesion: 0.07
Nodes (25): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+17 more)

### Community 25 - "test_drafting.py"
Cohesion: 0.13
Nodes (13): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_list_templates_matches_registry() (+5 more)

### Community 26 - "counts"
Cohesion: 0.17
Nodes (11): built_at, counts, curated, law_chunks, law_documents, precedents, regulator_chunks, regulator_documents (+3 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Documentation"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "_date"
Cohesion: 0.12
Nodes (36): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference() (+28 more)

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
Cohesion: 0.18
Nodes (12): confidence(), How sure we are this message is a legal question we can search well without an…, _explode(), llm_available(), fixture, S3: LLM-free hot path - confidence-gated skip of analyze_query()'s LLM call,…, test_confidence_high_for_nepali_and_glossary_matched_english(), test_confidence_low_for_english_with_no_glossary_hits() (+4 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "chat.py"
Cohesion: 0.14
Nodes (28): corpus_stats(), create_matter_note(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task() (+20 more)

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

### Community 59 - "FakeMattersStore"
Cohesion: 0.08
Nodes (8): FakeMattersStore, matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, In-memory stand-in for supa.py's matters/notes/tasks/files functions, keyed by…, test_user_b_cannot_see_user_a_matter_or_its_subresources(), pytest

### Community 60 - "get"
Cohesion: 0.11
Nodes (26): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+18 more)

### Community 61 - "chat"
Cohesion: 0.15
Nodes (19): chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage(), _log_request() (+11 more)

### Community 62 - "cite"
Cohesion: 0.08
Nodes (39): check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), leave_entitlements(), row(), _money() (+31 more)

### Community 63 - "limitation.py"
Cohesion: 0.09
Nodes (39): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+31 more)

### Community 64 - "list_llm_usage"
Cohesion: 0.67
Nodes (3): list_llm_usage(), Cost-per-query visibility (STRATEGY's S13 "done when" bar): every paid-tier…, LlmUsageOut

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "test_s13_ai_gateway.py"
Cohesion: 0.07
Nodes (31): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, S13: writes one llm_usage row per real (non-cached, non-free-tier) generation,…, _record_llm_usage_sync(), audit_document(), UploadFile, Bounded chunked read (see routes/chat.py:upload_matter_file): an oversized…, Signed-in only. Metered against the caller's plan-based daily quota exactly… (+23 more)

### Community 67 - "generation.py"
Cohesion: 0.09
Nodes (31): analyze_needs_llm(), _answer_cache_key(), answer_question(), _bs_year(), _cache_key(), _extractive(), _history_text(), _passage() (+23 more)

### Community 68 - "app/__init__.py"
Cohesion: 0.11
Nodes (21): asyncio, _GZipExceptStreams, health(), lifespan(), get, Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies() (+13 more)

### Community 69 - "useLang"
Cohesion: 0.12
Nodes (42): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), ProfileForm() (+34 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (31): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+23 more)

### Community 71 - "playbooks.py"
Cohesion: 0.16
Nodes (22): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), _load_yaml_files(), ValueError, Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Every playbook with every provision resolved - raises UnresolvedProvision on… (+14 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.10
Nodes (30): assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest(), english_title() (+22 more)

### Community 73 - "post"
Cohesion: 0.17
Nodes (12): create_draft(), create_matter(), draft_document(), Response, The drafted document as DOCX (default) or PDF (`format: "pdf"`)., save_research(), DraftRequest, MatterIn (+4 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.07
Nodes (26): free(), 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices) (+18 more)

### Community 75 - "ai_fill.py"
Cohesion: 0.16
Nodes (14): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+6 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.05
Nodes (64): _ad_date(), authority(), bs_key(), _clean(), Client, cmd_stats(), download(), existing_corpus_titles() (+56 more)

### Community 77 - "json"
Cohesion: 0.12
Nodes (23): argparse, main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, ask_json(), load_corpus(), load_ingested(), load_manifest(), main() (+15 more)

### Community 78 - "Progress"
Cohesion: 0.22
Nodes (10): Pin the headline numbers so an edit to the YAML can't drift from the law., test_numeric_rules_match_the_statute_numbers(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus), Next session (+2 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (35): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+27 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "ics.ts"
Cohesion: 0.29
Nodes (9): RFC-5545, buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay(), stamp() (+1 more)

### Community 82 - "test_retrieval.py"
Cohesion: 0.11
Nodes (7): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours()

### Community 83 - "test_s14_security.py"
Cohesion: 0.10
Nodes (15): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+7 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.07
Nodes (115): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+107 more)

### Community 87 - "audit.py"
Cohesion: 0.11
Nodes (24): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+16 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.12
Nodes (23): _coerce(), Coerce a model-returned value to the fact's declared type, or None., Model JSON -> {fact: {"value": typed value | None, "clause_id": str | None}}.…, validate_extraction(), _ascii(), Clause, clause_by_id(), _clause_start() (+15 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "dsl.py"
Cohesion: 0.12
Nodes (31): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+23 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (32): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+24 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "retrieval.py"
Cohesion: 0.12
Nodes (16): array, corpus_source(), _current_bs_year(), _index_text(), _prior(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, Corrects status/type the source metadata gets wrong for law that isn't…, Backwards-compatible single-query search. (+8 more)

### Community 95 - "@playwright/test"
Cohesion: 0.22
Nodes (4): Json, PAIRS, ref_node_fs, @playwright/test

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (46): addToCalendar(), frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp() (+38 more)

### Community 98 - "Done"
Cohesion: 0.16
Nodes (17): _require_user(), cache_get(), cache_put(), check_and_increment_quota(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+9 more)

### Community 99 - "checklists.py"
Cohesion: 0.12
Nodes (24): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+16 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (33): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+25 more)

### Community 101 - "sources.py"
Cohesion: 0.08
Nodes (28): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, max_lawful_rate(), Interest on private loans under the Muluki Civil Code, 2074, chapter 15 (लेनदेन…, normalise_text(), parse_period_phrase(), Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari… (+20 more)

### Community 102 - "docx_out.py"
Cohesion: 0.09
Nodes (36): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), _add_font_table_fallback() (+28 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.18
Nodes (14): all_company_profiles(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent(), reminder_record_sent() (+6 more)

### Community 104 - "i18n.ts"
Cohesion: 0.11
Nodes (16): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+8 more)

### Community 105 - "render.py"
Cohesion: 0.09
Nodes (45): build_docx(), PageBreak, TemplateSpec, strip_inline(), build_html(), build_pdf(), _inline(), _para_html() (+37 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.15
Nodes (20): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+12 more)

### Community 107 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.13
Nodes (19): main(), Download the official PDFs that carry prescribed forms (schedules) and dump…, slug(), build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats() (+11 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "test_chat_route_anonymous_caller_stays_on_free_tier"
Cohesion: 0.40
Nodes (4): The core S13 wiring bug surface: a paid-plan user's /api/chat call must route…, test_chat_route_anonymous_caller_stays_on_free_tier(), test_chat_route_selects_tier_from_plan(), fake_answer_question()

### Community 112 - "looks_like_injection"
Cohesion: 0.67
Nodes (4): looks_like_injection(), parametrize, test_looks_like_injection_does_not_flag_ordinary_legal_questions(), test_looks_like_injection_flags_common_patterns()

### Community 113 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 114 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "models.py"
Cohesion: 0.15
Nodes (18): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+10 more)

### Community 117 - "embedding_benchmark.py"
Cohesion: 0.23
Nodes (8): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), statistics

### Community 119 - "glossary.py"
Cohesion: 0.31
Nodes (9): expand(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, Nepali statute terms for the English/romanised phrases in `text`, longest…, size(), S7 — +17 playbooks + matcher (2026-09-26) (+1 more)

### Community 120 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 121 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 122 - "MatterOut"
Cohesion: 0.20
Nodes (10): list_matters(), put_company_profile(), update_draft(), update_matter(), CompanyProfileIn, CompanyProfileOut, MatterOut, MatterUpdateIn (+2 more)

### Community 123 - "preeti.ts"
Cohesion: 0.17
Nodes (9): CHARS, I_MATRA_RE, JOIN_RULES, MATRA_AFTER_HALANT_RE, MATRA_BEFORE_HALANT_RE, NASAL_BEFORE_MATRA_RE, REPH_RE, SEQUENCES (+1 more)

### Community 124 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

### Community 125 - "complete"
Cohesion: 0.12
Nodes (20): _compat_enabled(), complete(), One completion within `budget_s` seconds across all providers, or…, Yield answer text incrementally. A provider/model is only abandoned before it…, stream(), gateway(), Handler, fixture (+12 more)

### Community 126 - "verifier.py"
Cohesion: 0.36
Nodes (9): check_sentence(), _haystack_numbers(), _is_legal_claim(), _norm_num(), _quantities(), Deterministic citation verifier for generated answers. The model writes the…, None if the claim is supported, else a short reason code., _sections() (+1 more)

### Community 127 - "ingest_pdfs.py"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 128 - "review_fee"
Cohesion: 0.29
Nodes (7): s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%…, review_fee(), settlement_fee(), test_court_fee_extensions_reject_non_positive_values(), test_review_fee_is_ten_percent_of_the_plaint_fee(), test_settlement_fee()

### Community 129 - "check_ip_rate_limit"
Cohesion: 0.47
Nodes (5): check_ip_rate_limit(), True if this IP is still under its hourly budget (and records the hit)., test_ip_rate_limit_blocks_after_the_hourly_budget(), test_ip_rate_limit_is_per_ip(), test_ip_rate_limit_window_expires()

### Community 131 - "match_playbooks"
Cohesion: 0.67
Nodes (3): match_playbooks(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, PlaybookMatchResponse

## Knowledge Gaps
- **291 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+286 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 907 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `Done` to `check_ip_rate_limit`, `get_index`, `generation.py`, `ui.tsx`?**
  _High betweenness centrality (0.253) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `audit/page.tsx`, `Done`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `schemas.py`, `Done`, `generation.py`, `checklists.py`, `test_v1_trust_engine.py`, `sources.py`, `app/__init__.py`, `playbooks.py`, `chat.py`, `scrape_lawcommission.py`, `json`, `Index`, `test_documents_audit.py`, `embedding_benchmark.py`, `test_calculators.py`, `chat`, `retrieval.py`, `limitation.py`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _291 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10252100840336134 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.05487269534679543 - nodes in this community are weakly interconnected._
- **Should `test_calculators_tools.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06944444444444445 - nodes in this community are weakly interconnected._