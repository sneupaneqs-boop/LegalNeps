# Graph Report - LegalNeps  (2026-09-30)

## Corpus Check
- 193 files · ~425,769 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: .jsonl 11, .css 5, (none) 4)

## Summary
- 2911 nodes · 6807 edges · 135 communities (118 shown, 17 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 280 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fcb55c57`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- match
- parametrize
- test_v1_trust_engine.py
- llm.py
- matters/[id]/page.tsx
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
- scrape_lawcommission.py
- test_drafting.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- _date
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- test_query_understanding.py
- Personal Loan Playbooks
- Sexual Harassment Playbooks
- get
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
- test_calculators_tools.py
- chat
- cite
- limitation.py
- ocr_regulators.py
- forms_common.py
- ai_fill.py
- generation.py
- app/__init__.py
- useLang
- ui.tsx
- playbooks.py
- ingest_regulators.py
- chat.py
- Env
- retrieval.py
- scrape_regulators.py
- test_ocr_clean.py
- _bad_input
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
- normalise_text
- @playwright/test
- run_audit
- [templateId]/page.tsx
- Done
- checklists.py
- Per-playbook findings
- models.py
- docx_out.py
- send_compliance_reminders.py
- i18n.ts
- render.py
- extract_doc_meta
- audit_document
- scrape_nkp.py
- nepali.py
- contract_fixtures.py
- cache_put
- post
- smoke.spec.ts
- embedding_benchmark.py
- scripts
- ocr_clean.py
- test_eval_sets.py
- DocResolver
- playbook_matcher.py
- devDependencies
- dependencies
- test_s11_matters.py
- preeti.ts
- test_s13_ai_gateway.py
- complete
- test_s12_compliance_radar.py
- json
- ingest_pdfs.py
- Progress
- page_verdict
- S6 — Action Plan engine (2026-09-26)
- calendar
- doc_slug
- is_table_noise

## God Nodes (most connected - your core abstractions)
1. `available()` - 47 edges
2. `get_index()` - 44 edges
3. `useLang()` - 43 edges
4. `_http()` - 42 edges
5. `useTools()` - 41 edges
6. `cite()` - 34 edges
7. `_date()` - 34 edges
8. `analyze_query()` - 32 edges
9. `ToolsPage()` - 32 edges
10. `errorText()` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `Known issues` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `Known issues` --references--> `classify_status()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `S13 — AI gateway v2 (2026-09-29)` --references--> `fill_paid()`  [INFERRED]
  docs/PROGRESS.md → backend/app/drafting/ai_fill.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (135 total, 17 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.11
Nodes (32): ai_fill_field(), list_playbooks(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, upcoming_obligations(), AiFillRequest, AiFillResponse, Amendment, Analysis (+24 more)

### Community 1 - "api.ts"
Cohesion: 0.07
Nodes (34): ActionPlanPage(), Bi(), ProvisionCard(), Amendment, AppealFeeResult, Bilingual, BsDate, CallOpts (+26 more)

### Community 2 - "match"
Cohesion: 0.08
Nodes (36): canon(), Entry, expand(), laws(), _lookup(), loose(), match(), _parse() (+28 more)

### Community 3 - "parametrize"
Cohesion: 0.07
Nodes (39): bs_month_length(), Number of days in a BS month (29-32; varies by year)., check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), _money() (+31 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.07
Nodes (49): _is_regulator_query(), _match_playbook(), The curated action plan for this situation, when the keyword matcher is…, _reset_cache_for_tests(), check_sentence(), _expand_multiplier(), _haystack_numbers(), _is_legal_claim() (+41 more)

### Community 5 - "llm.py"
Cohesion: 0.14
Nodes (31): _anthropic_complete(), _client_http(), _cool(), _cool_target(), _gemini(), _gemini_cfg(), _gemini_complete(), _gemini_stream() (+23 more)

### Community 6 - "matters/[id]/page.tsx"
Cohesion: 0.12
Nodes (36): FilesTab(), download(), handleFile(), remove(), formatSize(), MatterBackLink(), MatterDetail(), MatterDetailPage() (+28 more)

### Community 7 - "test_api.py"
Cohesion: 0.10
Nodes (7): normalize_citations(), Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, client(), fixture, test_research_save_list_delete_roundtrip(), test_text_citations_are_mapped_to_numbered_sources(), fastapi_testclient

### Community 8 - "extract_laws.py"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.16
Nodes (36): available(), draft_create(), draft_get(), draft_list(), draft_update(), _draft_version_insert(), draft_versions_list(), _http() (+28 more)

### Community 10 - "get_index"
Cohesion: 0.11
Nodes (32): analyze_query(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, search(), available(), parse_json(), get_index(), cmd_e2e() (+24 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.22
Nodes (8): name, private, version, react-dom, @types/node, @types/react, @types/react-dom, typescript

### Community 13 - "build_corpus.py"
Cohesion: 0.22
Nodes (13): curated_entries(), _doc_type(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -… (+5 more)

### Community 14 - "Index"
Cohesion: 0.18
Nodes (7): Index, _index_text(), _prior(), All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Authority of the source x usefulness of this particular passage., Connection

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "tools.py"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "text_norm.py"
Cohesion: 0.11
Nodes (27): focus(), _is_devanagari(), Script check on the message itself. NOT the language hint: the hint is "ne" for…, The part of a passage that matters for this question: the heading line plus the…, ndarray, _title_tokens(), detect_language(), fold() (+19 more)

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
Cohesion: 0.15
Nodes (10): _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip(), test_status_is_never_guessed() (+2 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.08
Nodes (42): appeal_fee(), court_fee(), estimate(), estimate_appeal(), The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its…, bs_to_ad() (+34 more)

### Community 24 - "scrape_lawcommission.py"
Cohesion: 0.13
Nodes (19): main(), Download the official PDFs that carry prescribed forms (schedules) and dump…, slug(), build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats() (+11 more)

### Community 25 - "test_drafting.py"
Cohesion: 0.13
Nodes (13): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_list_templates_matches_registry() (+5 more)

### Community 26 - "counts"
Cohesion: 0.12
Nodes (15): built_at, counts, curated, law_chunks, law_documents, ocr_chunks, ocr_documents, precedents (+7 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Documentation"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "_date"
Cohesion: 0.07
Nodes (49): ad_to_bs(), add_bs_months(), add_days(), bs_difference(), bs_to_iso(), BsDiff, check_ad_supported(), ValueError (+41 more)

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "test_query_understanding.py"
Cohesion: 0.06
Nodes (42): analyze_needs_llm(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message can be searched well WITHOUT an LLM rewriting it.…, The one rule for "answer this question without the query-rewrite call" - shared…, Whether analyze_query() will reach a provider for this message. (+34 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "get"
Cohesion: 0.11
Nodes (20): get_company_profile(), get_draft(), get_drafting_template(), get_playbook(), law_doc(), law_section(), limitation_claim_types(), list_draft_versions() (+12 more)

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
Cohesion: 0.12
Nodes (4): FakeMattersStore, matters_client(), fixture, In-memory stand-in for supa.py's matters/notes/tasks/files functions, keyed by…

### Community 60 - "test_calculators_tools.py"
Cohesion: 0.08
Nodes (51): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, flat_fee(), The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., add_bs_years(), add_period(), Add a limitation-style period. days -> calendar days, months -> BS months,…, `date` plus N BS years (12 BS months each), clipped like add_bs_months. (+43 more)

### Community 61 - "chat"
Cohesion: 0.13
Nodes (21): chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage(), _log_request() (+13 more)

### Community 62 - "cite"
Cohesion: 0.07
Nodes (37): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%…, review_fee(), settlement_fee() (+29 more)

### Community 63 - "limitation.py"
Cohesion: 0.09
Nodes (42): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+34 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "ai_fill.py"
Cohesion: 0.23
Nodes (10): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+2 more)

### Community 67 - "generation.py"
Cohesion: 0.09
Nodes (30): _answer_cache_key(), answer_question(), _bs_year(), _cache_key(), _extractive(), _history_text(), _is_fiscal_query(), _LRU (+22 more)

### Community 68 - "app/__init__.py"
Cohesion: 0.09
Nodes (23): asyncio, _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, _GZipExceptStreams, health(), lifespan(), get, Request (+15 more)

### Community 69 - "useLang"
Cohesion: 0.12
Nodes (32): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), addToCalendar() (+24 more)

### Community 70 - "ui.tsx"
Cohesion: 0.12
Nodes (30): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+22 more)

### Community 71 - "playbooks.py"
Cohesion: 0.15
Nodes (21): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), _load_yaml_files(), Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Every playbook with every provision resolved - raises UnresolvedProvision on…, Summary list (no provision resolution - cheap, for GET /api/playbooks). (+13 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): _text_key(), assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest() (+24 more)

### Community 73 - "chat.py"
Cohesion: 0.12
Nodes (33): corpus_stats(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task(), delete_research() (+25 more)

### Community 74 - "Env"
Cohesion: 0.06
Nodes (30): client(), Env, free(), fixture, Fake Supabase surface for the route tests., 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict (+22 more)

### Community 75 - "retrieval.py"
Cohesion: 0.09
Nodes (26): array, _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en() (+18 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.05
Nodes (69): _ad_date(), authority(), bs_key(), _clean(), Client, cmd_stats(), download(), existing_corpus_titles() (+61 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.13
Nodes (20): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+12 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (36): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+28 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "ics.ts"
Cohesion: 0.29
Nodes (9): RFC-5545, buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay(), stamp() (+1 more)

### Community 82 - "test_retrieval.py"
Cohesion: 0.12
Nodes (3): idx(), fixture, test_cache_roundtrip()

### Community 83 - "test_s14_security.py"
Cohesion: 0.08
Nodes (21): audit_log(), draft_delete(), matter_delete(), matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, Best-effort record of an irreversible user action (a delete, so far - see…, safe_filename() (+13 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.14
Nodes (21): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+13 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (120): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+112 more)

### Community 87 - "audit.py"
Cohesion: 0.10
Nodes (25): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+17 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.11
Nodes (25): _coerce(), Coerce a model-returned value to the fact's declared type, or None., Model JSON -> {fact: {"value": typed value | None, "clause_id": str | None}}.…, validate_extraction(), _ascii(), Clause, clause_by_id(), _clause_start() (+17 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "dsl.py"
Cohesion: 0.12
Nodes (30): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+22 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (31): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+23 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "normalise_text"
Cohesion: 0.12
Nodes (19): normalise_text(), parse_period_phrase(), Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari…, (value, unit) of the number+unit at the start of a phrase like 'छ महिनाभित्र'…, Problems (empty when fine) with one entry's citation and stated period: the…, section_text(), verify_entry() (+11 more)

### Community 95 - "@playwright/test"
Cohesion: 0.22
Nodes (4): Json, PAIRS, ref_node_fs, @playwright/test

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.07
Nodes (51): frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload() (+43 more)

### Community 98 - "Done"
Cohesion: 0.13
Nodes (20): _require_user(), cache_get(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Validate a Supabase access token (from the frontend's Authorization header) and…, True if this IP is still under its hourly budget (and records the hit). (+12 more)

### Community 99 - "checklists.py"
Cohesion: 0.15
Nodes (21): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+13 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (31): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+23 more)

### Community 101 - "models.py"
Cohesion: 0.15
Nodes (18): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+10 more)

### Community 102 - "docx_out.py"
Cohesion: 0.07
Nodes (49): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), _add_font_table_fallback() (+41 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.17
Nodes (15): all_company_profiles(), company_profile_get(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent() (+7 more)

### Community 104 - "i18n.ts"
Cohesion: 0.13
Nodes (12): ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage(), getLawDoc(), getLawSection(), listPlaybooks() (+4 more)

### Community 105 - "render.py"
Cohesion: 0.11
Nodes (35): PageBreak, TemplateSpec, strip_inline(), build_pdf(), _build_context(), _effective_language(), get_template(), get_template_detail() (+27 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.16
Nodes (19): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+11 more)

### Community 107 - "audit_document"
Cohesion: 0.17
Nodes (15): audit_document(), _error(), HTTPException, UploadFile, Bounded chunked read (see routes/chat.py:upload_matter_file): an oversized…, Signed-in only. Metered against the caller's plan-based daily quota exactly…, _read_capped(), daily_quota_for() (+7 more)

### Community 108 - "scrape_nkp.py"
Cohesion: 0.16
Nodes (14): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+6 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "cache_put"
Cohesion: 0.40
Nodes (5): cache_put(), jsonb_safe(), Postgres jsonb rejects the NUL character (\\u0000), which some scanned law…, saved_research_create(), test_answer_cache_strips_nul_characters_postgres_jsonb_rejects()

### Community 112 - "post"
Cohesion: 0.15
Nodes (13): create_draft(), create_matter(), create_matter_note(), draft_document(), Response, The drafted document as DOCX (default) or PDF (`format: "pdf"`)., save_research(), DraftRequest (+5 more)

### Community 113 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 114 - "embedding_benchmark.py"
Cohesion: 0.21
Nodes (9): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), numpy (+1 more)

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.15
Nodes (19): clean_document(), clean_page(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), _latin_dominant(), normalise_digits() (+11 more)

### Community 117 - "test_eval_sets.py"
Cohesion: 0.18
Nodes (4): _lines(), _norm(), V1: the real-world and held-out eval sets, the `--set` flag of…, test_heldout_is_disjoint_and_marked_do_not_tune()

### Community 118 - "DocResolver"
Cohesion: 0.19
Nodes (10): DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl…, Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the…, Return a list of problems ([] = every cited provision found and confirmed)., verify_case(), parametrize, requires_corpus (+2 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.18
Nodes (18): _playbook_id_for(), A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _query_tokens() (+10 more)

### Community 120 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 121 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 122 - "test_s11_matters.py"
Cohesion: 0.22
Nodes (3): S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 123 - "preeti.ts"
Cohesion: 0.17
Nodes (9): CHARS, I_MATRA_RE, JOIN_RULES, MATRA_AFTER_HALANT_RE, MATRA_BEFORE_HALANT_RE, NASAL_BEFORE_MATRA_RE, REPH_RE, SEQUENCES (+1 more)

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.07
Nodes (25): paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, looks_like_injection(), `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).…, select_tier(), _FakeAnthropicClient, _FakeMessage, _FakeTextBlock (+17 more)

### Community 125 - "complete"
Cohesion: 0.12
Nodes (20): _compat_enabled(), complete(), One completion within `budget_s` seconds across all providers, or…, Yield answer text incrementally. A provider/model is only abandoned before it…, stream(), gateway(), Handler, fixture (+12 more)

### Community 126 - "test_s12_compliance_radar.py"
Cohesion: 0.10
Nodes (8): compliance_client(), FakeComplianceStore, fixture, S12: Compliance Radar lite - company profile, obligations, upcoming-due…, test_applies_to_gates_on_profile_fields(), test_next_due_annual_obligation(), test_next_due_is_always_in_the_future_and_recurs_monthly(), test_reminder_job_dedups_via_reminders_sent()

### Community 127 - "json"
Cohesion: 0.12
Nodes (22): argparse, main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, ask_json(), load_corpus(), load_ingested(), load_manifest(), main() (+14 more)

### Community 128 - "ingest_pdfs.py"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 129 - "Progress"
Cohesion: 0.22
Nodes (10): parametrize, test_enacted_date_matches_known_acts(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (baseline, S1), Metrics (S2, real corpus) (+2 more)

### Community 130 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 131 - "S6 — Action Plan engine (2026-09-26)"
Cohesion: 0.32
Nodes (4): Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., S6 — Action Plan engine (2026-09-26)

### Community 133 - "doc_slug"
Cohesion: 0.33
Nodes (6): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours()

### Community 134 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

## Knowledge Gaps
- **296 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+291 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1019 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `Done` to `get_index`, `generation.py`, `ui.tsx`, `cache_put`?**
  _High betweenness centrality (0.247) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `Done`?**
  _High betweenness centrality (0.182) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `match`, `S6 — Action Plan engine (2026-09-26)`, `test_v1_trust_engine.py`, `Index`, `scrape_lawcommission.py`, `get`, `chat`, `limitation.py`, `generation.py`, `app/__init__.py`, `playbooks.py`, `chat.py`, `retrieval.py`, `test_documents_audit.py`, `normalise_text`, `Done`, `checklists.py`, `render.py`, `embedding_benchmark.py`, `test_eval_sets.py`, `DocResolver`, `json`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _296 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10984848484848485 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06507936507936508 - nodes in this community are weakly interconnected._