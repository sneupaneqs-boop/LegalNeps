# Graph Report - LegalNeps  (2026-09-30)

## Corpus Check
- 205 files · ~449,423 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .jsonl 11, (none) 6, .css 5)

## Summary
- 3190 nodes · 7477 edges · 149 communities (129 shown, 20 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `305b50af`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- match
- parametrize
- test_v1_trust_engine.py
- llm.py
- test_dense.py
- test_api.py
- extract_laws.py
- supa.py
- get_index
- Graphify Tool Documentation
- package.json
- build_corpus.py
- Index
- devanagari_glyphs.py
- get
- tokenize
- Crawler
- Project Strategy and Prompts
- TypeScript Configuration
- test_s10_ai_and_save.py
- test_regulators_ingest.py
- test_calculators.py
- retrieval.py
- test_drafting.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- _date
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- app/__init__.py
- Personal Loan Playbooks
- Sexual Harassment Playbooks
- test_calculators_tools.py
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
- Done
- chat
- cite
- limitation.py
- ocr_regulators.py
- forms_common.py
- ai_fill.py
- generation.py
- documents.py
- useLang
- ui.tsx
- checklists.py
- ingest_regulators.py
- chat.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- scrape_regulators.py
- test_ocr_clean.py
- _bad_input
- test_documents_audit.py
- search/page.tsx
- preeti.ts
- doc_slug
- test_s14_security.py
- ChatMessage.tsx
- test_drafting_formats.py
- calculators.tsx
- run_eval.py
- audit/page.tsx
- audit.py
- extract.py
- dsl.py
- rules.py
- Session prompts — V2 (commercial build)
- normalise_text
- structured.py
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- verifier_calibration.py
- Per-playbook findings
- models.py
- re
- send_compliance_reminders.py
- LangContext.tsx
- render.py
- extract_doc_meta
- audit_document
- scrape_nkp.py
- nepali.py
- contract_fixtures.py
- S
- scrape_lawcommission.py
- verifier.py
- test_s12_compliance_radar.py
- scripts
- ocr_clean.py
- test_eval_sets.py
- test_v3_structured.py
- playbook_matcher.py
- devDependencies
- load_dense
- pytest
- compliance/page.tsx
- test_s13_ai_gateway.py
- Env
- Dense
- config.py
- json
- Progress
- report.py
- entailment_filter
- calendar
- _View
- _generate_verified
- draft_update
- matter_file_create
- test_chat_route_anonymous_caller_stays_on_free_tier
- verify_structured
- page_verdict
- quantize
- FakeDense
- mark_stale_precedents
- Run the API in Docker (no cloud payment needed)
- Encoder
- tidy_answer
- DraftingTemplateSummary
- is_table_noise
- pipeline

## God Nodes (most connected - your core abstractions)
1. `get()` - 61 edges
2. `get_index()` - 52 edges
3. `available()` - 47 edges
4. `useLang()` - 43 edges
5. `_http()` - 42 edges
6. `useTools()` - 41 edges
7. `cite()` - 34 edges
8. `_date()` - 34 edges
9. `analyze_query()` - 32 edges
10. `ToolsPage()` - 32 edges

## Surprising Connections (you probably didn't know these)
- `V-batch 1 — trust engine, full UI, Document AI (2026-09-29)` --references--> `search()`  [INFERRED]
  docs/PROGRESS.md → backend/app/generation.py
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `S2 — Legal data engine v2 (2026-09-26)` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `S4 — Search + law browser UI (2026-09-26)` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (149 total, 20 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.08
Nodes (40): ai_fill_field(), get_playbook(), list_draft_versions(), list_llm_usage(), match_playbooks(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, Expands a free-text field's short hint via the LLM. Signed-in only, metered…, Cost-per-query visibility (STRATEGY's S13 "done when" bar): every paid-tier… (+32 more)

### Community 1 - "api.ts"
Cohesion: 0.05
Nodes (43): patch(), Amendment, AppealFeeResult, BsDate, callJson(), CallOpts, ChatResponse, checkLimitation() (+35 more)

### Community 2 - "match"
Cohesion: 0.08
Nodes (36): canon(), Entry, expand(), laws(), _lookup(), loose(), match(), _parse() (+28 more)

### Community 3 - "parametrize"
Cohesion: 0.07
Nodes (39): bs_month_length(), Number of days in a BS month (29-32; varies by year)., check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), _money() (+31 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.10
Nodes (31): _is_regulator_query(), _pipeline_fingerprint(), _reset_cache_for_tests(), _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status(), Returns (answer with unsupported legal claims marked, report)., verify() (+23 more)

### Community 5 - "llm.py"
Cohesion: 0.08
Nodes (52): _anthropic_complete(), _call_limit(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini() (+44 more)

### Community 6 - "test_dense.py"
Cohesion: 0.18
Nodes (15): hybrid(), Dense retrieval: vector store (digest mismatch, missing file, id alignment),…, Attach a fake dense, restore afterwards., test_agreement_beats_either_signal_alone(), test_bills_never_surface_by_default_even_if_dense_top(), test_category_filter_after_fusion(), test_dense_finds_what_bm25_cannot(), test_dense_weight_shifts_the_order() (+7 more)

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
Cohesion: 0.09
Nodes (35): clear_query_cache(), Load everything and run one query through it (used by…, warm_up(), _match_playbook(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, The curated action plan for this situation, when the keyword matcher is…, search() (+27 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.14
Nodes (13): dependencies, next, react, react-dom, @supabase/supabase-js, name, private, version (+5 more)

### Community 13 - "build_corpus.py"
Cohesion: 0.22
Nodes (13): curated_entries(), _doc_type(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -… (+5 more)

### Community 14 - "Index"
Cohesion: 0.10
Nodes (14): Index, ndarray, Load the query encoder + corpus vectors if available (best-effort, never…, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]. (+6 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "get"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "tokenize"
Cohesion: 0.19
Nodes (17): fold(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term(), tokenize(), _bridge() (+9 more)

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
Nodes (42): appeal_fee(), court_fee(), estimate(), estimate_appeal(), The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its…, gratuity() (+34 more)

### Community 24 - "retrieval.py"
Cohesion: 0.08
Nodes (28): argparse, array, passage_text(), Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, Document title + section heading + body, Nepali first, English title/heading…, save_vectors(), corpus_source(), BM25 search over the government-sourced corpus (laws + precedents). The corpus… (+20 more)

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
Cohesion: 0.10
Nodes (44): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference() (+36 more)

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "app/__init__.py"
Cohesion: 0.06
Nodes (45): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message can be searched well WITHOUT an LLM rewriting it.…, The one rule for "answer this question without the query-rewrite call" - shared… (+37 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "test_calculators_tools.py"
Cohesion: 0.08
Nodes (50): flat_fee(), The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., Problems (empty when fine) with one source., verify_source(), income_tax(), Annual income tax on `taxable_income` (NPR) for a resident individual or couple…, api(), bs() (+42 more)

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

### Community 60 - "Done"
Cohesion: 0.18
Nodes (13): _entry_status(), _index_text(), _prior(), Authority of the source x usefulness of this particular passage., Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S4 — Search + law browser UI (2026-09-26) (+5 more)

### Community 61 - "chat"
Cohesion: 0.12
Nodes (22): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+14 more)

### Community 62 - "cite"
Cohesion: 0.08
Nodes (34): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%…, review_fee(), settlement_fee() (+26 more)

### Community 63 - "limitation.py"
Cohesion: 0.09
Nodes (38): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+30 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (40): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+32 more)

### Community 66 - "ai_fill.py"
Cohesion: 0.10
Nodes (23): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+15 more)

### Community 67 - "generation.py"
Cohesion: 0.09
Nodes (31): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), focus(), _history_text(), _is_devanagari(), _is_fiscal_query() (+23 more)

### Community 68 - "documents.py"
Cohesion: 0.11
Nodes (19): asyncio, _GZipExceptStreams, health(), lifespan(), Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies(), root() (+11 more)

### Community 69 - "useLang"
Cohesion: 0.10
Nodes (51): Compliance(), CompliancePage(), ProfileForm(), submit(), DraftPage(), handleDelete(), FilesTab(), download() (+43 more)

### Community 70 - "ui.tsx"
Cohesion: 0.15
Nodes (24): Account(), AccountPage(), AuthWidget(), handleSendCode(), handleVerify(), isActive(), NAV, Shell() (+16 more)

### Community 71 - "checklists.py"
Cohesion: 0.06
Nodes (49): keyword_scores(), _keyword_table(), Keyword hits per contract type: each keyword counts up to 5 times in the body,…, assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist() (+41 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): _text_key(), assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest() (+24 more)

### Community 73 - "chat.py"
Cohesion: 0.08
Nodes (53): corpus_stats(), create_draft(), create_matter(), create_matter_note(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file() (+45 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.08
Nodes (25): 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500) (+17 more)

### Community 75 - "glossary.py"
Cohesion: 0.26
Nodes (11): _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes… (+3 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.05
Nodes (69): _ad_date(), authority(), bs_key(), _clean(), Client, cmd_stats(), download(), existing_corpus_titles() (+61 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.14
Nodes (19): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), draft_document() (+11 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (37): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+29 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.36
Nodes (9): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+1 more)

### Community 81 - "preeti.ts"
Cohesion: 0.06
Nodes (25): RFC-5545, Json, API, API_WAIT, PAGES, buildIcs(), compact(), escapeText() (+17 more)

### Community 82 - "doc_slug"
Cohesion: 0.10
Nodes (9): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), idx(), fixture, test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default() (+1 more)

### Community 83 - "test_s14_security.py"
Cohesion: 0.10
Nodes (16): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+8 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.14
Nodes (21): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+13 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (122): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+114 more)

### Community 87 - "run_eval.py"
Cohesion: 0.11
Nodes (28): parse_json(), aggregate(), main(), Passages, post(), Collect answers from a running API for human / LLM review of the V3 generate-…, Full text of cited sources: local corpus by id, else the API's section…, review_row() (+20 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "audit.py"
Cohesion: 0.07
Nodes (48): apply_checklist(), AuditError, classify_contract(), _clause_label(), _coerce(), _confident(), ContractTypeUnknown, extract_facts() (+40 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "dsl.py"
Cohesion: 0.11
Nodes (32): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+24 more)

### Community 92 - "rules.py"
Cohesion: 0.11
Nodes (26): Any, applies(), evaluate(), fields_in(), _leaf(), _num(), _present(), ValueError (+18 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "normalise_text"
Cohesion: 0.15
Nodes (15): normalise_text(), parse_period_phrase(), Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari…, (value, unit) of the number+unit at the start of a phrase like 'छ महिनाभित्र'…, Problems (empty when fine) with one entry's citation and stated period: the…, section_text(), verify_entry() (+7 more)

### Community 95 - "structured.py"
Cohesion: 0.10
Nodes (26): build(), chunks(), _clean_side_text(), _norm_doc(), _norm_sentence(), _objects_from(), parse_answer(), V3: generate-then-verify answers. The model returns ONE JSON object (blocks of… (+18 more)

### Community 96 - "run_audit"
Cohesion: 0.11
Nodes (21): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), summarize(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no… (+13 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.11
Nodes (35): frontend_app_draft_draft, Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload(), handleSave(), missingFields() (+27 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.14
Nodes (18): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+10 more)

### Community 99 - "verifier_calibration.py"
Cohesion: 0.15
Nodes (27): check_structured_sentence(), _cite_list(), lexical_support(), looks_rule_like(), _numbers_in(), Numbers/quantities the sentence asserts. Section references and (1)-style…, A sentence that states or implies law, whatever kind the model gave it., (share of the sentence's content words the quote supports, hits, words… (+19 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (32): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+24 more)

### Community 101 - "models.py"
Cohesion: 0.26
Nodes (12): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+4 more)

### Community 102 - "re"
Cohesion: 0.10
Nodes (39): _add_font_table_fallback(), build_docx(), _get_or_add(), _insert_ordered(), _local(), _page_setup(), _paragraph(), Resolved layout blocks -> a real .docx (python-docx). Page and type set-up… (+31 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.18
Nodes (14): all_company_profiles(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent(), reminder_record_sent() (+6 more)

### Community 104 - "LangContext.tsx"
Cohesion: 0.07
Nodes (30): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, frontend_app_globals, DOC_TYPE_LABEL, LawDocPage() (+22 more)

### Community 105 - "render.py"
Cohesion: 0.12
Nodes (31): PageBreak, TemplateSpec, strip_inline(), build_pdf(), _build_context(), _effective_language(), get_template(), get_template_detail() (+23 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.17
Nodes (18): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, parametrize (+10 more)

### Community 107 - "audit_document"
Cohesion: 0.20
Nodes (11): audit_document(), audit_report(), _error(), HTTPException, post, Response, UploadFile, Render an audit (the JSON returned by /documents/audit) as a DOCX report.… (+3 more)

### Community 108 - "scrape_nkp.py"
Cohesion: 0.17
Nodes (13): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+5 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "S"
Cohesion: 0.16
Nodes (23): check(), parametrize, S(), test_altered_quote_is_removed(), test_bad_citation_number_is_removed(), test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook(), test_english_sentence_with_english_translation_quote(), test_english_sentence_with_nepali_quote_is_bridged_through_the_glossary() (+15 more)

### Community 112 - "scrape_lawcommission.py"
Cohesion: 0.13
Nodes (19): main(), Download the official PDFs that carry prescribed forms (schedules) and dump…, slug(), build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats() (+11 more)

### Community 113 - "verifier.py"
Cohesion: 0.16
Nodes (18): check_sentence(), _clean_doc_sentence(), _expand_multiplier(), _guidance_ok(), _haystack_numbers(), _in_terms(), _is_legal_claim(), _ne_variants() (+10 more)

### Community 114 - "test_s12_compliance_radar.py"
Cohesion: 0.07
Nodes (25): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+17 more)

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.16
Nodes (18): clean_document(), clean_page(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), _latin_dominant(), normalise_digits() (+10 more)

### Community 117 - "test_eval_sets.py"
Cohesion: 0.09
Nodes (14): DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl…, Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the…, Return a list of problems ([] = every cited provision found and confirmed)., verify_case(), _lines(), _norm() (+6 more)

### Community 118 - "test_v3_structured.py"
Cohesion: 0.17
Nodes (13): V3: generate-then-verify. The model's JSON answer is checked sentence by…, _run(), test_answer_review_rows_and_aggregate(), test_free_tier_skips_entailment_by_default_and_env_flag_enables_it(), test_nepali_gets_a_larger_token_budget(), test_old_prose_cache_entry_is_not_served(), test_paid_tier_runs_entailment_on_the_paid_model(), test_run_falls_back_to_the_provisions_when_too_little_survives() (+5 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.15
Nodes (21): _playbook_id_for(), A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _query_tokens() (+13 more)

### Community 120 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 121 - "load_dense"
Cohesion: 0.18
Nodes (13): _download(), enabled(), load_dense(), model_ready(), prepare_model(), Path, Vectors for `ids` (the loaded corpus's passage ids, in row order), or None when…, Best-effort: a Dense for this corpus, or None (BM25-only). Never raises. (+5 more)

### Community 122 - "pytest"
Cohesion: 0.17
Nodes (6): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources(), pytest

### Community 123 - "compliance/page.tsx"
Cohesion: 0.22
Nodes (11): daysLabel(), ENTITY_TYPES, Obligations(), addToCalendar(), WINDOWS, CompanyProfile, EntityType, getCompanyProfile() (+3 more)

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.09
Nodes (22): S13: writes one llm_usage row per real (non-cached, non-free-tier) generation,…, _record_llm_usage_sync(), daily_quota_for(), estimate_cost_usd(), model_for_tier(), S13: plan-based tier routing and token-cost accounting. STRATEGY.md §2's…, `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).…, select_tier() (+14 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "Dense"
Cohesion: 0.23
Nodes (6): Dense, ndarray, int8 vectors aligned to an Index's row order. `have[i]` is False for rows with…, (n_passages, n_queries) cosine similarities; -1 where a passage has no vector., Query encoder + vector store for one Index., VectorStore

### Community 127 - "config.py"
Cohesion: 0.40
Nodes (3): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, dotenv

### Community 128 - "json"
Cohesion: 0.10
Nodes (31): main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus() (+23 more)

### Community 129 - "Progress"
Cohesion: 0.25
Nodes (8): Pin the headline numbers so an edit to the YAML can't drift from the law., test_numeric_rules_match_the_statute_numbers(), rule(), Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus), Next session, Progress

### Community 130 - "report.py"
Cohesion: 0.21
Nodes (11): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), Document (+3 more)

### Community 131 - "entailment_filter"
Cohesion: 0.22
Nodes (9): entailment_filter(), One cheap call over every cited sentence: drop those whose quote does NOT…, doc_of(), test_build_runs_entailment_only_when_given_and_recounts(), test_entailment_fails_open(), boom(), test_entailment_removes_no_and_keeps_yes_and_partial(), test_fewer_than_two_verified_rules_falls_back() (+1 more)

### Community 133 - "_View"
Cohesion: 0.24
Nodes (10): _fuzzy_span(), _qtokens(), quote_in_source(), Quote tokens: NFC, PUA glyphs and punctuation/danda gone, digits ASCII,…, One source prepared for span matching., >=90% of the quote's tokens found in one contiguous run of the source (OCR'd…, None if the quote is a verbatim span of the source, else a reason code., _View (+2 more)

### Community 134 - "_generate_verified"
Cohesion: 0.28
Nodes (9): _generate_verified(), add_usage(), paid_call(), repair(), _guidance_terms_text(), Every step/forum/evidence line of the plan in both languages: the only place an…, (structured.build() result | None if no model answered, usage). Never raises., was_cut_off() (+1 more)

### Community 135 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

### Community 136 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 137 - "test_chat_route_anonymous_caller_stays_on_free_tier"
Cohesion: 0.40
Nodes (4): The core S13 wiring bug surface: a paid-plan user's /api/chat call must route…, test_chat_route_anonymous_caller_stays_on_free_tier(), test_chat_route_selects_tier_from_plan(), fake_answer_question()

### Community 138 - "verify_structured"
Cohesion: 0.28
Nodes (9): _line(), Markdown in the shape the UI already shows: bold headings, bullets, inline [n]., render(), (verified doc, report). Failing sentences are dropped; blocks left with nothing…, verify_structured(), test_failing_sentences_are_removed_and_report_keeps_the_legacy_shape(), test_heading_left_without_sentences_is_dropped(), test_render_makes_the_markdown_the_ui_already_shows() (+1 more)

### Community 139 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 140 - "quantize"
Cohesion: 0.36
Nodes (8): quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., test_quantize_roundtrip_keeps_cosine(), test_store_digest_mismatch_reuses_surviving_ids(), test_store_exact_match(), test_store_same_ids_other_digest_is_used_but_flagged(), _vectors(), _write()

### Community 141 - "FakeDense"
Cohesion: 0.25
Nodes (5): FakeDense, attach(), idx(), fixture, Stands in for dense.Dense: `wanted` maps query text -> {passage id: cosine};…

### Community 142 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), Pattern, A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale()

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 145 - "tidy_answer"
Cohesion: 0.50
Nodes (4): Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer(), test_dhara_becomes_dafa_for_statutes_only(), test_trailing_empty_heading_is_removed()

### Community 146 - "DraftingTemplateSummary"
Cohesion: 0.50
Nodes (4): get_drafting_template(), list_drafting_templates(), DraftingTemplateDetail, DraftingTemplateSummary

### Community 147 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

## Knowledge Gaps
- **301 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+296 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1102 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `app/__init__.py`, `generation.py`, `ui.tsx`, `get_index`, `Done`, `chat`?**
  _High betweenness centrality (0.255) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `json`, `match`, `generation.py`, `documents.py`, `test_v1_trust_engine.py`, `S5 — Supabase auth + DB (2026-09-26)`, `checklists.py`, `chat.py`, `Index`, `test_documents_audit.py`, `scrape_lawcommission.py`, `test_eval_sets.py`, `run_eval.py`, `test_calculators.py`, `retrieval.py`, `chat`, `normalise_text`, `limitation.py`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _301 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08414634146341464 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.05496828752642706 - nodes in this community are weakly interconnected._