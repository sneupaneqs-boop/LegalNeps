# Graph Report - LegalNeps  (2026-09-30)

## Corpus Check
- 193 files · ~425,332 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: .jsonl 11, .css 5, (none) 4)

## Summary
- 2902 nodes · 6784 edges · 135 communities (116 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 279 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `724a256b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- match
- test_calculators_tools.py
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
- scrape_lawcommission.py
- Project Strategy and Prompts
- TypeScript Configuration
- test_s10_ai_and_save.py
- test_regulators_ingest.py
- test_calculators.py
- _date
- test_drafting.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- bs
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- analyze_query
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
- _bad_input
- chat
- cite
- limitation.py
- ocr_regulators.py
- forms_common.py
- test_s13_ai_gateway.py
- generation.py
- documents.py
- useLang
- ui.tsx
- playbooks.py
- ingest_regulators.py
- post
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- labour_rights.py
- scrape_regulators.py
- test_ocr_clean.py
- main.py
- test_documents_audit.py
- search/page.tsx
- ics.ts
- doc_slug
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
- S5 — Supabase auth + DB (2026-09-26)
- checklists.py
- Per-playbook findings
- report.py
- docx_out.py
- send_compliance_reminders.py
- i18n.ts
- render.py
- extract_doc_meta
- Query
- json
- nepali.py
- contract_fixtures.py
- test_chat_route_anonymous_caller_stays_on_free_tier
- S13 — AI gateway v2 (2026-09-29)
- smoke.spec.ts
- Env
- scripts
- ocr_clean.py
- tax_tds
- test_eval_sets.py
- playbook_matcher.py
- devDependencies
- dependencies
- pytest
- preeti.ts
- audit_document
- complete
- test_s12_compliance_radar.py
- ingest_scraped.py
- draft_update
- Handler
- page_verdict
- matter_file_create
- calendar
- is_table_noise
- _bad

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
- `V-batch 1 — trust engine, full UI, Document AI (2026-09-29)` --references--> `search()`  [INFERRED]
  docs/PROGRESS.md → backend/app/generation.py
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `V-batch 2b — OCR of the scanned regulator PDFs + NIA/MoLESS (2026-09-30)` --references--> `nia_rows()`  [INFERRED]
  docs/PROGRESS.md → backend/scripts/scrape_regulators.py
- `S8 — Calculators (2026-09-27)` --references--> `check()`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/limitation.py
- `S2 — Legal data engine v2 (2026-09-26)` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (135 total, 19 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.09
Nodes (44): AiFillRequest, AiFillResponse, Amendment, Analysis, Bilingual, ChatRequest, ChatResponse, CourtFeeAppealResponse (+36 more)

### Community 1 - "api.ts"
Cohesion: 0.06
Nodes (37): Amendment, AppealFeeResult, BsDate, callJson(), CallOpts, ChatResponse, checkLimitation(), CompanyProfileInput (+29 more)

### Community 2 - "match"
Cohesion: 0.08
Nodes (34): canon(), Entry, expand(), _lookup(), loose(), match(), _parse(), Romanised-Nepali / English -> formal statute-Nepali legal lexicon. The corpus… (+26 more)

### Community 3 - "test_calculators_tools.py"
Cohesion: 0.07
Nodes (61): Problems (empty when fine) with one source., verify_source(), income_tax(), Annual income tax on `taxable_income` (NPR) for a resident individual or couple…, api(), fixture, parametrize, requires_corpus (+53 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.07
Nodes (47): _is_fiscal_query(), _is_regulator_query(), mark_stale_precedents(), _match_playbook(), A precedent decided before the statute now governing the topic was enacted…, The curated action plan for this situation, when the keyword matcher is…, search(), _reset_cache_for_tests() (+39 more)

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
Cohesion: 0.18
Nodes (31): available(), company_profile_get(), draft_get(), draft_list(), _http(), llm_usage_list(), llm_usage_record(), matter_create() (+23 more)

### Community 10 - "get_index"
Cohesion: 0.10
Nodes (33): parse_json(), get_index(), detect_language(), DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl…, Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the…, Return a list of problems ([] = every cited provision found and confirmed). (+25 more)

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
Cohesion: 0.08
Nodes (22): _entry_status(), Index, _index_text(), _prior(), ndarray, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]. (+14 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "tools.py"
Cohesion: 0.13
Nodes (29): _catalog(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_age(), date_age_markers(), date_difference(), interest_rules() (+21 more)

### Community 17 - "text_norm.py"
Cohesion: 0.16
Nodes (20): focus(), The part of a passage that matters for this question: the heading line plus the…, fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised…, Index term for one folded token ('' = drop it)., _stem_en() (+12 more)

### Community 18 - "scrape_lawcommission.py"
Cohesion: 0.09
Nodes (19): build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats(), Crawler, push(), _extractable_text_fraction() (+11 more)

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
Nodes (9): _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip(), test_status_is_never_guessed() (+1 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.08
Nodes (40): appeal_fee(), court_fee(), estimate(), estimate_appeal(), The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its…, gratuity() (+32 more)

### Community 24 - "_date"
Cohesion: 0.18
Nodes (21): bs_to_ad(), add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule() (+13 more)

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

### Community 29 - "bs"
Cohesion: 0.07
Nodes (52): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference() (+44 more)

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "analyze_query"
Cohesion: 0.06
Nodes (51): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), _is_devanagari(), quick_intent(), Obvious non-legal messages, recognised without any LLM., Script check on the message itself. NOT the language hint: the hint is "ne" for… (+43 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "chat.py"
Cohesion: 0.08
Nodes (52): corpus_stats(), create_draft(), create_matter(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note() (+44 more)

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

### Community 60 - "_bad_input"
Cohesion: 0.21
Nodes (14): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+6 more)

### Community 61 - "chat"
Cohesion: 0.14
Nodes (20): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+12 more)

### Community 62 - "cite"
Cohesion: 0.09
Nodes (30): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, flat_fee(), flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%… (+22 more)

### Community 63 - "limitation.py"
Cohesion: 0.07
Nodes (51): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+43 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (40): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+32 more)

### Community 66 - "test_s13_ai_gateway.py"
Cohesion: 0.08
Nodes (22): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+14 more)

### Community 67 - "generation.py"
Cohesion: 0.09
Nodes (26): _answer_cache_key(), answer_question(), _bs_year(), _cache_key(), _extractive(), _history_text(), _LRU, _passage() (+18 more)

### Community 68 - "documents.py"
Cohesion: 0.14
Nodes (20): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+12 more)

### Community 69 - "useLang"
Cohesion: 0.15
Nodes (28): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), ProfileForm() (+20 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (31): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+23 more)

### Community 71 - "playbooks.py"
Cohesion: 0.15
Nodes (23): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), _load_yaml_files(), ValueError, Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Every playbook with every provision resolved - raises UnresolvedProvision on… (+15 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): _text_key(), assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest() (+24 more)

### Community 73 - "post"
Cohesion: 0.22
Nodes (9): create_matter_note(), draft_document(), Response, UploadFile, The drafted document as DOCX (default) or PDF (`format: "pdf"`)., save_research(), upload_matter_file(), test_audit_log_failure_does_not_raise() (+1 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.09
Nodes (21): 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500), 3.4 Legal/business prerequisites (founder to-do, confirm with your advocate), 3. Who pays, and for what, 4.1 Must-have for commercial launch, 4.2 Growth (post-launch) (+13 more)

### Community 75 - "labour_rights.py"
Cohesion: 0.14
Nodes (22): check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), _money(), _non_negative(), notice_tiers() (+14 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.05
Nodes (68): _ad_date(), authority(), bs_key(), _clean(), Client, cmd_stats(), download(), existing_corpus_titles() (+60 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "main.py"
Cohesion: 0.12
Nodes (18): asyncio, _GZipExceptStreams, health(), lifespan(), get, Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies() (+10 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (36): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+28 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.36
Nodes (9): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+1 more)

### Community 81 - "ics.ts"
Cohesion: 0.26
Nodes (10): RFC-5545, addToCalendar(), buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay() (+2 more)

### Community 82 - "doc_slug"
Cohesion: 0.10
Nodes (9): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), idx(), fixture, test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default() (+1 more)

### Community 83 - "test_s14_security.py"
Cohesion: 0.10
Nodes (15): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+7 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.14
Nodes (21): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+13 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (122): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+114 more)

### Community 87 - "audit.py"
Cohesion: 0.11
Nodes (24): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+16 more)

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
Nodes (29): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+21 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (31): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+23 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "retrieval.py"
Cohesion: 0.12
Nodes (18): array, _current_bs_year(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, Corrects status/type the source metadata gets wrong for law that isn't…, Backwards-compatible single-query search., retrieve(), _temporal_status(), main() (+10 more)

### Community 95 - "@playwright/test"
Cohesion: 0.22
Nodes (4): Json, PAIRS, ref_node_fs, @playwright/test

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (44): frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload() (+36 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.14
Nodes (18): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+10 more)

### Community 99 - "checklists.py"
Cohesion: 0.13
Nodes (23): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+15 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (32): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+24 more)

### Community 101 - "report.py"
Cohesion: 0.21
Nodes (11): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), Document (+3 more)

### Community 102 - "docx_out.py"
Cohesion: 0.11
Nodes (36): _add_font_table_fallback(), build_docx(), _get_or_add(), _insert_ordered(), _local(), _page_setup(), _paragraph(), Resolved layout blocks -> a real .docx (python-docx). Page and type set-up… (+28 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.18
Nodes (14): all_company_profiles(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent(), reminder_record_sent() (+6 more)

### Community 104 - "i18n.ts"
Cohesion: 0.11
Nodes (17): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+9 more)

### Community 105 - "render.py"
Cohesion: 0.10
Nodes (37): PageBreak, Questionnaire field + document block shapes shared by every drafting template…, Table, TemplateSpec, strip_inline(), build_pdf(), _build_context(), _effective_language() (+29 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.11
Nodes (27): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, parametrize (+19 more)

### Community 107 - "Query"
Cohesion: 0.21
Nodes (18): date_add(), interest_simple(), labour_festival_allowance(), labour_fund_contributions(), labour_hours_check(), labour_leave_accrual(), labour_leave_encashment(), labour_overtime() (+10 more)

### Community 108 - "json"
Cohesion: 0.06
Nodes (35): argparse, _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, E5Small, _first_hit(), load_questions(), main(), ndarray (+27 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "test_chat_route_anonymous_caller_stays_on_free_tier"
Cohesion: 0.40
Nodes (4): The core S13 wiring bug surface: a paid-plan user's /api/chat call must route…, test_chat_route_anonymous_caller_stays_on_free_tier(), test_chat_route_selects_tier_from_plan(), fake_answer_question()

### Community 112 - "S13 — AI gateway v2 (2026-09-29)"
Cohesion: 0.22
Nodes (10): looks_like_injection(), free(), parametrize, test_looks_like_injection_does_not_flag_ordinary_legal_questions(), test_looks_like_injection_flags_common_patterns(), S13 — AI gateway v2 (2026-09-29), 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical) (+2 more)

### Community 113 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 114 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.15
Nodes (19): clean_document(), clean_page(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), _latin_dominant(), normalise_digits() (+11 more)

### Community 117 - "tax_tds"
Cohesion: 0.48
Nodes (7): court_fee_flat(), limitation_deadline(), pattern, Deadline for any catalog entry with a fixed period. `trigger_date` is when the…, tax_tds(), max_length, min_length

### Community 118 - "test_eval_sets.py"
Cohesion: 0.18
Nodes (4): _lines(), _norm(), V1: the real-world and held-out eval sets, the `--set` flag of…, test_heldout_is_disjoint_and_marked_do_not_tune()

### Community 119 - "playbook_matcher.py"
Cohesion: 0.09
Nodes (32): _expansion_precise(), _playbook_id_for(), The glossary's word-for-word expansion is trustworthy: it found something, and…, A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, expand_hits(), _index(), _key(), _norm_en() (+24 more)

### Community 120 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 121 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 122 - "pytest"
Cohesion: 0.17
Nodes (6): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources(), pytest

### Community 123 - "preeti.ts"
Cohesion: 0.17
Nodes (9): CHARS, I_MATRA_RE, JOIN_RULES, MATRA_AFTER_HALANT_RE, MATRA_BEFORE_HALANT_RE, NASAL_BEFORE_MATRA_RE, REPH_RE, SEQUENCES (+1 more)

### Community 124 - "audit_document"
Cohesion: 0.12
Nodes (22): ai_fill_field(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, audit_document(), _error(), HTTPException, UploadFile, Bounded chunked read (see routes/chat.py:upload_matter_file): an oversized…, Signed-in only. Metered against the caller's plan-based daily quota exactly… (+14 more)

### Community 125 - "complete"
Cohesion: 0.15
Nodes (18): _compat_enabled(), complete(), One completion within `budget_s` seconds across all providers, or…, Yield answer text incrementally. A provider/model is only abandoned before it…, stream(), gateway(), fixture, test_content_as_list_of_parts_and_reasoning_hint() (+10 more)

### Community 126 - "test_s12_compliance_radar.py"
Cohesion: 0.10
Nodes (8): compliance_client(), FakeComplianceStore, fixture, S12: Compliance Radar lite - company profile, obligations, upcoming-due…, test_applies_to_gates_on_profile_fields(), test_next_due_annual_obligation(), test_next_due_is_always_in_the_future_and_recurs_monthly(), test_reminder_job_dedups_via_reminders_sent()

### Community 127 - "ingest_scraped.py"
Cohesion: 0.17
Nodes (20): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+12 more)

### Community 128 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

### Community 130 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 131 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 133 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

### Community 134 - "_bad"
Cohesion: 0.67
Nodes (3): _bad(), Exception, HTTPException

## Knowledge Gaps
- **296 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+291 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1019 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `analyze_query`, `generation.py`, `ui.tsx`, `get_index`, `Index`, `chat`?**
  _High betweenness centrality (0.246) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `match`, `generation.py`, `checklists.py`, `test_v1_trust_engine.py`, `chat.py`, `playbooks.py`, `S5 — Supabase auth + DB (2026-09-26)`, `render.py`, `json`, `main.py`, `Index`, `test_documents_audit.py`, `test_eval_sets.py`, `chat`, `retrieval.py`, `limitation.py`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _296 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08585858585858586 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06258890469416785 - nodes in this community are weakly interconnected._