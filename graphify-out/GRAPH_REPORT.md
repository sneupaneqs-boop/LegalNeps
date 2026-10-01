# Graph Report - LegalNeps  (2026-10-01)

## Corpus Check
- 227 files · ~640,790 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 34 file(s) not represented in the graph (top: .jsonl 14, (none) 6, .css 5)

## Summary
- 3698 nodes · 8812 edges · 168 communities (140 shown, 28 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 352 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cf25f368`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- claim_checks.py
- api.ts
- translit.py
- cite
- test_v1_trust_engine.py
- llm.py
- test_dense.py
- test_api.py
- extract_laws.py
- supa.py
- test_v25_routing.py
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
- audit.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- _date
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- analyze_query
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
- Progress
- chat
- checklists.py
- limitation.py
- ocr_regulators.py
- forms_common.py
- chat.py
- _run
- documents.py
- matters/[id]/page.tsx
- ui.tsx
- playbooks.py
- ingest_regulators.py
- schemas.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- time
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
- get_index
- audit/page.tsx
- segment.py
- extract.py
- dsl.py
- rules.py
- Session prompts — V2 (commercial build)
- test_drafting.py
- complete
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- _View
- Per-playbook findings
- IncrementalDoc
- docx_out.py
- argparse
- i18n.ts
- render.py
- extract_doc_meta
- verifier.py
- scrape_nkp.py
- nepali.py
- contract_fixtures.py
- test_v3_structured.py
- topical_fit_calibration.py
- test_v32_claim_checks.py
- test_s12_compliance_radar.py
- scripts
- ocr_clean.py
- main.py
- test_v31_streaming.py
- playbook_matcher.py
- answer_review.py
- scrape_lawcommission.py
- test_s11_matters.py
- test_eval_sets.py
- test_s13_ai_gateway.py
- Env
- dense.py
- parse_answer
- ingest_scraped.py
- Done
- test_v33_topical_fit.py
- measure_resources.py
- calendar
- Playbook audit - the 25 curated action plans
- topical_fit.py
- safe_filename
- filter_gaps
- scrape_regulators.py
- build
- page_verdict
- ingest_pdfs.py
- generation.py
- stream_json
- Run the API in Docker (no cloud payment needed)
- fit_reply.py
- _targets
- useLang
- is_table_noise
- .section
- _gemini_complete
- devDependencies
- situation_guards.py
- _SSE
- entailment_filter
- .search
- alignment_ok
- calls
- pipeline
- Handler
- chunks
- _LRU
- _heading
- .attach_dense
- draft_update
- ._doc_index
- idx
- test_answer_review_rows_and_aggregate
- test_paid_tier_runs_entailment_on_the_paid_model

## God Nodes (most connected - your core abstractions)
1. `get_index()` - 71 edges
2. `get()` - 61 edges
3. `available()` - 47 edges
4. `tokenize()` - 47 edges
5. `useLang()` - 43 edges
6. `_http()` - 42 edges
7. `useTools()` - 41 edges
8. `S()` - 40 edges
9. `run()` - 39 edges
10. `analyze_query()` - 36 edges

## Surprising Connections (you probably didn't know these)
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `V-batch 2b — OCR of the scanned regulator PDFs + NIA/MoLESS (2026-09-30)` --references--> `nia_rows()`  [INFERRED]
  docs/PROGRESS.md → backend/scripts/scrape_regulators.py
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `V3.2 — Claim checks from the live review, entailment v2, token diet (2026-09-30, offline; live re-measure pending)` --references--> `proviso_dropped()`  [INFERRED]
  docs/PROGRESS.md → backend/app/claim_checks.py
- `V3.2 — Claim checks from the live review, entailment v2, token diet (2026-09-30, offline; live re-measure pending)` --references--> `uncited_forum_claim()`  [INFERRED]
  docs/PROGRESS.md → backend/app/claim_checks.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (168 total, 28 thin omitted)

### Community 0 - "claim_checks.py"
Cohesion: 0.05
Nodes (63): _clean(), dangling_additive(), _dev_share(), document_requirement(), _fmt(), _folded(), forum_classes(), forum_not_in_sources() (+55 more)

### Community 1 - "api.ts"
Cohesion: 0.07
Nodes (44): adToBs(), Amendment, AppealFeeResult, BsDate, bsToAd(), calcGratuity(), calcNotice(), calcSeverance() (+36 more)

### Community 2 - "translit.py"
Cohesion: 0.06
Nodes (46): canon(), Entry, expand(), expand_ne(), _key_in(), laws_ne(), _lookup(), loose() (+38 more)

### Community 3 - "cite"
Cohesion: 0.07
Nodes (43): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, max_lawful_rate(), Interest on private loans under the Muluki Civil Code, 2074, chapter 15 (लेनदेन…, check_hours(), festival_allowance(), fund_contributions(), leave_accrual() (+35 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.07
Nodes (43): _bs_year(), _is_regulator_query(), mark_stale_precedents(), _pipeline_fingerprint(), Pattern, A precedent decided before the statute now governing the topic was enacted…, Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer() (+35 more)

### Community 5 - "llm.py"
Cohesion: 0.19
Nodes (21): _anthropic_complete(), _call_limit(), _client_http(), _groq_complete(), LLMUnavailable, _openai_call(), _openai_headers(), _openai_payload() (+13 more)

### Community 6 - "test_dense.py"
Cohesion: 0.10
Nodes (28): quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., FakeDense, hybrid(), attach(), idx(), fixture, Dense retrieval: vector store (digest mismatch, missing file, id alignment),… (+20 more)

### Community 7 - "test_api.py"
Cohesion: 0.09
Nodes (10): focus(), normalize_citations(), The part of a passage that matters for this question: the heading line plus the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, client(), fixture, test_focus_keeps_heading_and_the_matching_clause(), test_research_save_list_delete_roundtrip() (+2 more)

### Community 8 - "extract_laws.py"
Cohesion: 0.07
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), find_sections(), _font_bytes(), _font_family() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.12
Nodes (46): all_company_profiles(), available(), company_profile_get(), company_profile_upsert(), draft_get(), draft_list(), _http(), llm_usage_list() (+38 more)

### Community 10 - "test_v25_routing.py"
Cohesion: 0.07
Nodes (50): _is_bank_query(), _match_playbook(), _nrb_directive_hits(), _playbook_id_for(), _playbook_pick(), playbook_support(), `text` with known Devanagari spelling slips corrected (unchanged when nothing…, A retail-banking question (see _BANK_ACTOR/_BANK_SERVICE): NRB directives are… (+42 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.14
Nodes (13): dependencies, next, react, react-dom, @supabase/supabase-js, name, private, version (+5 more)

### Community 13 - "build_corpus.py"
Cohesion: 0.18
Nodes (15): curated_entries(), _doc_type(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -… (+7 more)

### Community 14 - "Index"
Cohesion: 0.14
Nodes (9): Index, Path, 1-based id of the specialist regime a passage belongs to (0 = general law)., Per-passage heading weights and specialist-regime ids (best-effort, never…, All passages (loads everything - for scripts/evals, not requests)., _regime_of(), test_stream_endpoint_forwards_replace(), test_stream_endpoint_forwards_the_status_event() (+1 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "get"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "tokenize"
Cohesion: 0.16
Nodes (19): law_topic_terms(), Stemmed section titles of the retrieved STATUTES ("बेइज्जती गर्न नहुने",…, fold(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term() (+11 more)

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
Cohesion: 0.11
Nodes (20): _build(), fill(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, Expand `hint` into fuller prose for `field_id` of `template_id`, in `language`,…, UnknownField (+12 more)

### Community 22 - "test_regulators_ingest.py"
Cohesion: 0.16
Nodes (10): _text_key(), _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip() (+2 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.06
Nodes (57): appeal_fee(), court_fee(), estimate(), estimate_appeal(), flat_fee(), flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2)). (+49 more)

### Community 24 - "retrieval.py"
Cohesion: 0.07
Nodes (35): array, _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, _inactive_regimes(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, Regime ids whose cue words the (lower-cased) query text does not contain., Backwards-compatible single-query search., retrieve() (+27 more)

### Community 25 - "audit.py"
Cohesion: 0.09
Nodes (30): AuditError, classify_contract(), _coerce(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines() (+22 more)

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
Cohesion: 0.11
Nodes (41): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference() (+33 more)

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
Nodes (58): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), _expansion_precise(), _is_devanagari(), quick_intent(), Obvious non-legal messages, recognised without any LLM. (+50 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "test_calculators_tools.py"
Cohesion: 0.06
Nodes (78): income_tax(), Annual income tax on `taxable_income` (NPR) for a resident individual or couple…, api(), bs(), _corpus_hadmyad_sections(), fixture, parametrize, requires_corpus (+70 more)

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

### Community 60 - "Progress"
Cohesion: 0.33
Nodes (6): Live deployment (2026-09-28/29 audit), Metrics (baseline, S1), Metrics (S2, real corpus), Next session, Progress, S1 — Baseline + CI (2026-09-26)

### Community 61 - "chat"
Cohesion: 0.11
Nodes (24): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+16 more)

### Community 62 - "checklists.py"
Cohesion: 0.13
Nodes (24): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+16 more)

### Community 63 - "limitation.py"
Cohesion: 0.08
Nodes (44): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+36 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "chat.py"
Cohesion: 0.07
Nodes (54): corpus_stats(), create_draft(), create_matter(), create_matter_note(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file() (+46 more)

### Community 67 - "_run"
Cohesion: 0.18
Nodes (10): _run(), test_entailment_fails_open(), boom(), test_free_tier_entailment_is_off_by_default_and_env_flag_enables_it_as_one_extra_call(), test_nepali_gets_a_larger_token_budget(), test_run_provider_failure_gives_the_extractive_answer(), test_run_streams_status_then_verified_deltas_then_done(), test_run_truncated_json_is_salvaged_not_cut_mid_sentence() (+2 more)

### Community 68 - "documents.py"
Cohesion: 0.11
Nodes (27): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+19 more)

### Community 69 - "matters/[id]/page.tsx"
Cohesion: 0.12
Nodes (36): FilesTab(), download(), handleFile(), remove(), formatSize(), MatterBackLink(), MatterDetail(), MatterDetailPage() (+28 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (31): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+23 more)

### Community 71 - "playbooks.py"
Cohesion: 0.13
Nodes (25): all_playbooks_resolved(), _get_playbook_cached(), list_playbooks(), _load_yaml_files(), lookup_entry(), _norm(), ValueError, Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited… (+17 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest(), english_title() (+24 more)

### Community 73 - "schemas.py"
Cohesion: 0.08
Nodes (43): ai_fill_field(), law_doc(), law_section(), list_draft_versions(), list_llm_usage(), match_playbooks(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, Expands a free-text field's short hint via the LLM. Signed-in only, metered… (+35 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.09
Nodes (21): 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500), 3.4 Legal/business prerequisites (founder to-do, confirm with your advocate), 3. Who pays, and for what, 4.1 Must-have for commercial launch, 4.2 Growth (post-launch) (+13 more)

### Community 75 - "glossary.py"
Cohesion: 0.43
Nodes (7): expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, (matched phrase words, its Nepali terms) for each glossary phrase in `text`,…, size()

### Community 76 - "time"
Cohesion: 0.10
Nodes (20): passage_text(), Document title + section heading + body, Nepali first, English title/heading…, build_pool(), embed_pool(), _fetch(), Which small multilingual encoder should the dense half use? (default +…, _init(), main() (+12 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.15
Nodes (18): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), draft_document() (+10 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.07
Nodes (42): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, clause_by_id(), _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of… (+34 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "preeti.ts"
Cohesion: 0.06
Nodes (25): RFC-5545, Json, API, API_WAIT, PAGES, buildIcs(), compact(), escapeText() (+17 more)

### Community 82 - "doc_slug"
Cohesion: 0.11
Nodes (7): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours()

### Community 83 - "test_s14_security.py"
Cohesion: 0.09
Nodes (18): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+10 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.07
Nodes (114): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+106 more)

### Community 87 - "get_index"
Cohesion: 0.07
Nodes (43): answer_question(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, parse_json(), get_index(), DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl… (+35 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.16
Nodes (16): _ascii(), Clause, _clause_start(), _normalise_id(), _paragraph_fallback(), prompt_view(), Split contract text into numbered clauses so findings can cite "Clause 7".…, Accept whatever the model echoes back: "Clause 7", "clause 7.", "7.", "दफा ७",… (+8 more)

### Community 90 - "extract.py"
Cohesion: 0.13
Nodes (23): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+15 more)

### Community 91 - "dsl.py"
Cohesion: 0.12
Nodes (32): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+24 more)

### Community 92 - "rules.py"
Cohesion: 0.10
Nodes (29): Any, apply_checklist(), _clause_label(), Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate(), fields_in(), _leaf() (+21 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "test_drafting.py"
Cohesion: 0.13
Nodes (13): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_list_templates_matches_registry() (+5 more)

### Community 95 - "complete"
Cohesion: 0.16
Nodes (17): complete(), One completion within `budget_s` seconds across all providers, or…, Yield answer text incrementally. A provider/model is only abandoned before it…, stream(), gateway(), fixture, test_content_as_list_of_parts_and_reasoning_hint(), test_direct_providers_rotate_keys_and_skip_unconfigured() (+9 more)

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (46): frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload() (+38 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.15
Nodes (17): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+9 more)

### Community 99 - "_View"
Cohesion: 0.12
Nodes (20): clause_context(), Section/rule numbers a sentence names as ITS provision (not sub-section /…, The sentence names a section/rule that is another heading of the same passage…, (tokens of the clause up to the end of the quote, tokens of the clause after…, section_mismatch(), top_section_refs(), Polisher, _qtokens() (+12 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.08
Nodes (25): bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared, defamation - Someone defamed me (+17 more)

### Community 101 - "IncrementalDoc"
Cohesion: 0.15
Nodes (11): _Frame, IncrementalDoc, Truly incremental reader of the growing answer JSON: feed() consumes only the…, parametrize, _sentences_of(), split_random(), test_incremental_parser_cut_off_mid_sentence_and_prose_prefix(), test_incremental_parser_devanagari_and_escaped_quotes() (+3 more)

### Community 102 - "docx_out.py"
Cohesion: 0.07
Nodes (49): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), _add_font_table_fallback() (+41 more)

### Community 103 - "argparse"
Cohesion: 0.16
Nodes (12): argparse, E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize() (+4 more)

### Community 104 - "i18n.ts"
Cohesion: 0.11
Nodes (16): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+8 more)

### Community 105 - "render.py"
Cohesion: 0.13
Nodes (30): TemplateSpec, strip_inline(), build_pdf(), _build_context(), _effective_language(), get_template(), get_template_detail(), _items() (+22 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.12
Nodes (25): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+17 more)

### Community 107 - "verifier.py"
Cohesion: 0.09
Nodes (43): _bridge(), check_sentence(), check_structured_sentence(), _cite_conflicts(), _cite_list(), _expand_multiplier(), _guidance_ok(), _in_terms() (+35 more)

### Community 108 - "scrape_nkp.py"
Cohesion: 0.17
Nodes (13): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+5 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "test_v3_structured.py"
Cohesion: 0.15
Nodes (31): check(), parametrize, V3: generate-then-verify. The model's JSON answer is checked sentence by…, S(), test_altered_quote_is_removed(), test_bad_citation_number_is_removed(), test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook(), test_english_sentence_with_english_translation_quote() (+23 more)

### Community 112 - "topical_fit_calibration.py"
Cohesion: 0.18
Nodes (20): auc(), choose_threshold(), evaluate(), _fam_source(), fit_variant(), fit_weights(), loao_cv_logloss(), main() (+12 more)

### Community 113 - "test_v32_claim_checks.py"
Cohesion: 0.06
Nodes (64): clean_ocr_text(), dedupe_marks(), OCR glitches the model copied from a scanned source into its own sentence: a…, [5][5] -> [5]; order kept., _line(), guidance_term_set(), ctx_of(), _ctx_reason() (+56 more)

### Community 114 - "test_s12_compliance_radar.py"
Cohesion: 0.07
Nodes (25): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+17 more)

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.16
Nodes (18): clean_document(), clean_page(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), _latin_dominant(), normalise_digits() (+10 more)

### Community 117 - "main.py"
Cohesion: 0.13
Nodes (16): asyncio, _GZipExceptStreams, health(), lifespan(), Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies(), root() (+8 more)

### Community 118 - "test_v31_streaming.py"
Cohesion: 0.14
Nodes (30): fake_stream(), gen(), V3.1: progressive streaming with per-sentence verification. The provider stream…, Simulated provider at 40 ms per ~3-char token: time to first verified text vs…, What the frontend ends up showing: deltas append, `replace` swaps., run_events(), test_cache_hit_still_has_no_streaming_events(), test_cut_off_stream_shows_only_complete_sentences() (+22 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.12
Nodes (24): _keyword_hit_fraction(), _keyword_weight(), Match, _playbook_keywords(), _playbook_vetoes(), _positions(), Pattern, _query_tokens() (+16 more)

### Community 120 - "answer_review.py"
Cohesion: 0.17
Nodes (12): corpus_source(), aggregate(), main(), Passages, post(), Collect answers from a running API for human / LLM review of the V3 generate-…, Numbers in a rendered cited sentence that appear in none of its quotes (the '0…, Full text of cited sources: local corpus by id, else the API's section… (+4 more)

### Community 121 - "scrape_lawcommission.py"
Cohesion: 0.20
Nodes (13): build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text. (+5 more)

### Community 122 - "test_s11_matters.py"
Cohesion: 0.18
Nodes (5): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 123 - "test_eval_sets.py"
Cohesion: 0.18
Nodes (4): _lines(), _norm(), V1: the real-world and held-out eval sets, the `--set` flag of…, test_heldout_is_disjoint_and_marked_do_not_tune()

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.05
Nodes (44): fill_paid(), S13: same expansion, billed to a specific paid-tier model…, paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, looks_like_injection(), daily_quota_for(), estimate_cost_usd(), model_for_tier() (+36 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "dense.py"
Cohesion: 0.10
Nodes (23): Dense, _download(), enabled(), Encoder, load_dense(), model_ready(), prepare_model(), ndarray (+15 more)

### Community 127 - "parse_answer"
Cohesion: 0.29
Nodes (8): _norm_doc(), _norm_sentence(), parse_answer(), (doc, complete). complete=False when the object was cut off or broken and only…, test_complete_json_parses_and_fenced_json_too(), test_cut_off_flag_alone_marks_a_parseable_answer_truncated(), test_truncated_json_keeps_every_complete_sentence_and_drops_the_partial_one(), test_truncation_between_blocks_and_inside_a_heading()

### Community 128 - "ingest_scraped.py"
Cohesion: 0.27
Nodes (11): ask_json(), load_corpus(), load_ingested(), load_manifest(), main(), Step 2 of the scrape pipeline: turns documents downloaded by…, save_corpus(), save_ingested() (+3 more)

### Community 129 - "Done"
Cohesion: 0.11
Nodes (20): search(), search() boosts titles from analysis['laws'] plus the lexicon's laws., test_build_queries_boosts_the_llm_named_law(), requires_corpus, test_deposit_question_pins_civil_code_and_drops_tax_acts(), test_every_search_result_has_a_status(), test_playbook_excluded_provision_never_reaches_the_evidence(), test_procurement_insurance_labour_regulator_passages_stay_in_their_field() (+12 more)

### Community 130 - "test_v33_topical_fit.py"
Cohesion: 0.10
Nodes (33): has_figure(), orphan_opener(), Remove a leading "But/And/तर/र" that joined the sentence to one that was…, anaphor" when the sentence opens with a demonstrative / connective that points…, Some kept sentence states a number bound to a unit (days, years, %, rupees...)., strip_leading_conjunction(), _clean_doc_sentence(), make_views() (+25 more)

### Community 131 - "measure_resources.py"
Cohesion: 0.21
Nodes (11): clear_query_cache(), Load everything and run one query through it (used by…, warm_up(), main(), Warm/cold memory and search latency of the production retrieval path. python3…, rss_mb(), warm(), resource (+3 more)

### Community 133 - "Playbook audit - the 25 curated action plans"
Cohesion: 0.17
Nodes (11): All NEEDS-ADVOCATE-REVIEW items (64), Existing playbooks changed in V2.5, How to read the per-playbook sections, Method and limits of this audit, New playbooks (all NEEDS-ADVOCATE-REVIEW), Playbook audit - the 25 curated action plans, Result in one paragraph, Summary table (+3 more)

### Community 134 - "topical_fit.py"
Cohesion: 0.07
Nodes (36): _cterms(), Family, _head_string(), heading_of(), _in(), _is_precedent(), judge(), load_model() (+28 more)

### Community 135 - "safe_filename"
Cohesion: 0.50
Nodes (4): A display-safe file name: no directory parts, no "..", no control or path…, safe_filename(), parametrize, test_safe_filename()

### Community 136 - "filter_gaps"
Cohesion: 0.27
Nodes (10): filter_gaps(), gap_in_language(), (kept gaps, [(dropped gap, reason)]). Cited passages are tested first, then…, _clean_side_text(), _passage_text(), Gaps and follow-up questions carry no legal claim: keep them short and number-…, _gap_case(), test_honest_gaps_of_the_same_review_are_kept() (+2 more)

### Community 137 - "scrape_regulators.py"
Cohesion: 0.05
Nodes (68): _ad_date(), authority(), bs_key(), _clean(), Client, cmd_stats(), download(), existing_corpus_titles() (+60 more)

### Community 138 - "build"
Cohesion: 0.11
Nodes (17): asks_quantity(), build(), _log_fallback(), Markdown in the shape the UI already shows: bold headings, bullets, inline [n]., Why an answer fell back to the extractive provisions: structure counts only (no…, The model's raw reply -> {"answer": markdown | None, "verification": report,…, _recount(), render() (+9 more)

### Community 139 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 140 - "ingest_pdfs.py"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 141 - "generation.py"
Cohesion: 0.06
Nodes (51): CheckContext, What the checks may know about the request. All optional: with none of it the…, _answer_cache_key(), answer_max_tokens(), answer_system(), apply_topical_gate(), _cache_key(), check_context() (+43 more)

### Community 142 - "stream_json"
Cohesion: 0.25
Nodes (8): _compat_enabled(), last_finish_reason(), Yield the raw text of a JSON answer as the provider writes it (free-tier chain:…, Finish reason of this thread's last complete()/paid_complete(), if the provider…, stream_json(), was_cut_off(), test_stream_json_retries_without_response_format_and_reports_finish(), test_llm_cut_off_detection()

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 144 - "fit_reply.py"
Cohesion: 0.20
Nodes (14): abstain_answer(), _cite(), _excerpt(), extractive_answer(), gate_ran(), on_topic_laws(), V3.3: what the user sees when the topical-fit gate leaves too little to answer…, The corpus files a long section under its FIRST sub-section ("दफा 10 (1)")… (+6 more)

### Community 145 - "_targets"
Cohesion: 0.36
Nodes (8): _cool_target(), _model_key(), _openai_complete(), (base_url, api_key, model_id sent to the API, cooldown key)., Expand a "provider/model" chain into concrete endpoint+key+model calls:…, _Target, _targets(), tuple

### Community 146 - "useLang"
Cohesion: 0.14
Nodes (29): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), addToCalendar() (+21 more)

### Community 147 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

### Community 148 - ".section"
Cohesion: 0.29
Nodes (4): Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., V2.6 additions (2026-10-01): three new playbooks and changes to existing ones

### Community 149 - "_gemini_complete"
Cohesion: 0.53
Nodes (6): _cool(), _gemini(), _gemini_cfg(), _gemini_complete(), _gemini_stream(), _ready()

### Community 150 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 151 - "situation_guards.py"
Cohesion: 0.25
Nodes (8): Guard, Pattern, _r(), V3.2: a small DATA table of wrong-law guards - (what the user's question says…, The id of the guard that forbids citing `source` for this question, else None., _section_no(), violation(), _guard_hit()

### Community 153 - "entailment_filter"
Cohesion: 0.22
Nodes (8): entail_payload(), entailment_filter(), parse_verdicts(), (compact JSON for the entailment call, [(block, sentence) per item]). One item…, One verdict (yes/no/partial) per item from {"v":["y",...]} or the older…, ONE cheap call over every cited sentence: drop those whose quote does NOT…, main(), test_entailment_reads_both_formats_and_fails_open()

### Community 154 - ".search"
Cohesion: 0.31
Nodes (5): ndarray, Multiplies the fused scores (in place) by (a) a demotion for passages from a…, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, Adds each eligible query's dense (cosine) ranking to `fused` in place, by…, _title_tokens()

### Community 155 - "alignment_ok"
Cohesion: 0.29
Nodes (8): alignment_ok(), _lev(), near_variant(), Same word up to a character slip (matra/spelling/OCR): edit distance 1, or 2…, Every token of the quote is in the passage window, or is a near variant of the…, _fuzzy_span(), >=90% of the quote's tokens found in one contiguous run of the source; every…, test_fused_or_split_words_are_line_break_noise_not_substitution()

### Community 156 - "calls"
Cohesion: 0.40
Nodes (4): calls(), llm_on(), fixture, Replace llm.complete with a recorder that returns LLM_REPLY.

### Community 159 - "chunks"
Cohesion: 0.67
Nodes (3): chunks(), Word-boundary chunks of ~`size` chars (newlines kept) for simulated streaming., test_chunks_are_small_lossless_and_never_split_a_citation()

### Community 163 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

## Knowledge Gaps
- **306 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+301 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1244 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `Done`, `analyze_query`, `ui.tsx`, `generation.py`, `get_index`, `chat`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `Done`, `translit.py`, `cite`, `measure_resources.py`, `test_v1_trust_engine.py`, `topical_fit.py`, `test_v25_routing.py`, `generation.py`, `Index`, `fit_reply.py`, `test_calculators.py`, `retrieval.py`, `entailment_filter`, `analyze_query`, `chat`, `checklists.py`, `limitation.py`, `chat.py`, `playbooks.py`, `schemas.py`, `time`, `test_documents_audit.py`, `S5 — Supabase auth + DB (2026-09-26)`, `argparse`, `topical_fit_calibration.py`, `main.py`, `answer_review.py`, `test_eval_sets.py`, `dense.py`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _306 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `claim_checks.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04960491659350307 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06767676767676768 - nodes in this community are weakly interconnected._