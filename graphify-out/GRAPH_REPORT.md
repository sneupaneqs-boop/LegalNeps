# Graph Report - LegalNeps  (2026-09-30)

## Corpus Check
- 206 files · ~454,299 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .jsonl 11, (none) 6, .css 5)

## Summary
- 3266 nodes · 7688 edges · 155 communities (132 shown, 23 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 317 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1a92fd1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- list_llm_usage
- api.ts
- match
- labour_rights.py
- test_v1_trust_engine.py
- llm.py
- test_dense.py
- test_api.py
- extract_laws.py
- supa.py
- search
- Graphify Tool Documentation
- package.json
- build_corpus.py
- Index
- devanagari_glyphs.py
- get
- retrieval.py
- Crawler
- Project Strategy and Prompts
- TypeScript Configuration
- test_s10_ai_and_save.py
- test_regulators_ingest.py
- test_calculators.py
- get_index
- audit.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- cite
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
- checklists.py
- limitation.py
- ocr_regulators.py
- forms_common.py
- complete
- generation.py
- documents.py
- useLang
- ui.tsx
- playbooks.py
- ingest_regulators.py
- chat.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- scrape_regulators.py
- test_ocr_clean.py
- _bad_input
- test_documents_audit.py
- search/page.tsx
- ics.ts
- doc_slug
- test_s14_security.py
- ChatMessage.tsx
- test_drafting_formats.py
- calculators.tsx
- run_eval.py
- audit/page.tsx
- segment.py
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
- IncrementalDoc
- docx_out.py
- send_compliance_reminders.py
- i18n.ts
- render.py
- extract_doc_meta
- test_translit.py
- scrape_lawcommission.py
- nepali.py
- contract_fixtures.py
- test_v3_structured.py
- Store
- verifier.py
- test_s12_compliance_radar.py
- scripts
- ocr_clean.py
- test_eval_sets.py
- test_v31_streaming.py
- playbook_matcher.py
- scrape_lawcommission_gap
- load_dense
- pytest
- answer_review.py
- test_s13_ai_gateway.py
- Env
- Dense
- config.py
- ingest_scraped.py
- embedding_benchmark.py
- report.py
- authority
- calendar
- _View
- stream_json
- draft_update
- matter_file_create
- Client
- _generate_verified
- page_verdict
- quantize
- FakeDense
- mark_stale_precedents
- Run the API in Docker (no cloud payment needed)
- _targets
- tidy_answer
- _playbook_id_for
- is_table_noise
- pipeline
- scrape_nia
- _gemini_complete
- Handler
- _SSE
- flat_fee
- match_playbooks

## God Nodes (most connected - your core abstractions)
1. `get()` - 61 edges
2. `get_index()` - 52 edges
3. `available()` - 47 edges
4. `useLang()` - 43 edges
5. `_http()` - 42 edges
6. `useTools()` - 41 edges
7. `S()` - 40 edges
8. `cite()` - 34 edges
9. `_date()` - 34 edges
10. `analyze_query()` - 32 edges

## Surprising Connections (you probably didn't know these)
- `V-batch 1 — trust engine, full UI, Document AI (2026-09-29)` --references--> `search()`  [INFERRED]
  docs/PROGRESS.md → backend/app/generation.py
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `V2 — Hybrid retrieval, dense half (2026-09-30)` --references--> `passage_text()`  [INFERRED]
  docs/PROGRESS.md → backend/app/dense.py
- `Known issues` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (155 total, 23 thin omitted)

### Community 1 - "api.ts"
Cohesion: 0.05
Nodes (65): ActionPlanPage(), Bi(), ProvisionCard(), formatSize(), add(), remove(), OverviewTab(), handleDelete() (+57 more)

### Community 2 - "match"
Cohesion: 0.15
Nodes (19): canon(), Entry, _lookup(), loose(), match(), _parse(), Romanised-Nepali / English -> formal statute-Nepali legal lexicon. The corpus…, Spelling-tolerant form of a roman word: sh->s, w/v->b, z->j, ph/f->p,… (+11 more)

### Community 3 - "labour_rights.py"
Cohesion: 0.12
Nodes (25): check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), leave_entitlements(), row(), _money() (+17 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.10
Nodes (32): _is_regulator_query(), _pipeline_fingerprint(), _reset_cache_for_tests(), _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status(), _haystack_numbers(), Returns (answer with unsupported legal claims marked, report). (+24 more)

### Community 5 - "llm.py"
Cohesion: 0.21
Nodes (19): _anthropic_complete(), _call_limit(), _client_http(), _groq_complete(), LLMUnavailable, _openai_call(), _openai_headers(), _openai_payload() (+11 more)

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

### Community 10 - "search"
Cohesion: 0.15
Nodes (16): _is_fiscal_query(), _match_playbook(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, The curated action plan for this situation, when the keyword matcher is…, search(), search() boosts titles from analysis['laws'] plus the lexicon's laws., test_build_queries_boosts_the_llm_named_law() (+8 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.10
Nodes (19): dependencies, next, react, react-dom, @supabase/supabase-js, devDependencies, @playwright/test, @types/node (+11 more)

### Community 13 - "build_corpus.py"
Cohesion: 0.22
Nodes (13): curated_entries(), _doc_type(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -… (+5 more)

### Community 14 - "Index"
Cohesion: 0.11
Nodes (11): Index, Load the query encoder + corpus vectors if available (best-effort, never…, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., test_stream_endpoint_forwards_replace() (+3 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "get"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "retrieval.py"
Cohesion: 0.09
Nodes (32): array, _is_english(), ndarray, BM25 search over the government-sourced corpus (laws + precedents). The corpus…, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, Adds each eligible query's dense (cosine) ranking to `fused` in place, by…, Latin-script and not romanised Nepali ("mero ghardhani le bhada badhayo")., Backwards-compatible single-query search. (+24 more)

### Community 18 - "Crawler"
Cohesion: 0.17
Nodes (5): classify(), Crawler, push(), Icon-only PDF links (common on the category tables) carry no anchor text; fall…, Listing pages (category tables, index pages, pagination) link directly to every…

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
Nodes (50): appeal_fee(), court_fee(), estimate(), estimate_appeal(), flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%… (+42 more)

### Community 24 - "get_index"
Cohesion: 0.07
Nodes (47): argparse, clear_query_cache(), passage_text(), Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, Load everything and run one query through it (used by…, Document title + section heading + body, Nepali first, English title/heading…, warm_up(), corpus_source() (+39 more)

### Community 25 - "audit.py"
Cohesion: 0.11
Nodes (24): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+16 more)

### Community 26 - "counts"
Cohesion: 0.12
Nodes (15): built_at, counts, curated, law_chunks, law_documents, ocr_chunks, ocr_documents, precedents (+7 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Documentation"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "cite"
Cohesion: 0.07
Nodes (55): age_on(), markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days() (+47 more)

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
Nodes (36): analyze_needs_llm(), confidence(), _is_devanagari(), Script check on the message itself. NOT the language hint: the hint is "ne" for…, How sure we are this message can be searched well WITHOUT an LLM rewriting it.…, The one rule for "answer this question without the query-rewrite call" - shared…, Whether analyze_query() will reach a provider for this message., _skip_llm() (+28 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "test_calculators_tools.py"
Cohesion: 0.06
Nodes (76): income_tax(), Annual income tax on `taxable_income` (NPR) for a resident individual or couple…, api(), bs(), _corpus_hadmyad_sections(), fixture, parametrize, requires_corpus (+68 more)

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
Cohesion: 0.12
Nodes (17): parametrize, test_enacted_date_matches_known_acts(), rule(), Done, Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus) (+9 more)

### Community 61 - "chat"
Cohesion: 0.15
Nodes (18): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+10 more)

### Community 62 - "checklists.py"
Cohesion: 0.14
Nodes (22): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+14 more)

### Community 63 - "limitation.py"
Cohesion: 0.09
Nodes (40): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+32 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "complete"
Cohesion: 0.16
Nodes (17): complete(), One completion within `budget_s` seconds across all providers, or…, Yield answer text incrementally. A provider/model is only abandoned before it…, stream(), gateway(), fixture, test_content_as_list_of_parts_and_reasoning_hint(), test_direct_providers_rotate_keys_and_skip_unconfigured() (+9 more)

### Community 67 - "generation.py"
Cohesion: 0.09
Nodes (29): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), focus(), _guidance_terms_text(), _history_text(), _LRU (+21 more)

### Community 68 - "documents.py"
Cohesion: 0.06
Nodes (44): asyncio, AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut (+36 more)

### Community 69 - "useLang"
Cohesion: 0.13
Nodes (40): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), ProfileForm() (+32 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (32): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+24 more)

### Community 71 - "playbooks.py"
Cohesion: 0.15
Nodes (23): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), _load_yaml_files(), ValueError, Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Every playbook with every provision resolved - raises UnresolvedProvision on… (+15 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (31): assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest(), english_title() (+23 more)

### Community 73 - "chat.py"
Cohesion: 0.05
Nodes (96): corpus_stats(), create_draft(), create_matter(), create_matter_note(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file() (+88 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.08
Nodes (25): 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500) (+17 more)

### Community 75 - "glossary.py"
Cohesion: 0.26
Nodes (11): _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes… (+3 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.12
Nodes (24): _ad_date(), bs_key(), fiscal_year_bs(), giwms_listing(), newest_per_series(), _now(), _nrb_listing_pages(), pub_sort_key() (+16 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.16
Nodes (17): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), draft_document() (+9 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (37): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+29 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "ics.ts"
Cohesion: 0.10
Nodes (15): RFC-5545, Json, API, API_WAIT, PAGES, buildIcs(), compact(), escapeText() (+7 more)

### Community 82 - "doc_slug"
Cohesion: 0.10
Nodes (9): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), idx(), fixture, test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default() (+1 more)

### Community 83 - "test_s14_security.py"
Cohesion: 0.10
Nodes (16): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+8 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.08
Nodes (48): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+40 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.05
Nodes (130): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+122 more)

### Community 87 - "run_eval.py"
Cohesion: 0.11
Nodes (35): analyze_query(), build_queries(), quick_intent(), Obvious non-legal messages, recognised without any LLM., Weighted query set. Sources, best first: the LLM's Nepali legal phrasings; the…, available(), parse_json(), detect_language() (+27 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.10
Nodes (28): apply_checklist(), _clause_label(), _coerce(), _quote(), Coerce a model-returned value to the fact's declared type, or None., Model JSON -> {fact: {"value": typed value | None, "clause_id": str | None}}.…, A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,… (+20 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "dsl.py"
Cohesion: 0.14
Nodes (29): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+21 more)

### Community 92 - "rules.py"
Cohesion: 0.11
Nodes (26): Any, applies(), evaluate(), fields_in(), _leaf(), _num(), _present(), ValueError (+18 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "normalise_text"
Cohesion: 0.19
Nodes (13): normalise_text(), parse_period_phrase(), Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari…, (value, unit) of the number+unit at the start of a phrase like 'छ महिनाभित्र'…, Problems (empty when fine) with one entry's citation and stated period: the…, section_text(), verify_entry() (+5 more)

### Community 95 - "structured.py"
Cohesion: 0.07
Nodes (32): build(), chunks(), _clean_side_text(), entailment_filter(), _line(), _norm_doc(), _norm_sentence(), _objects_from() (+24 more)

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (47): addToCalendar(), frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp() (+39 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.14
Nodes (18): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+10 more)

### Community 99 - "verifier_calibration.py"
Cohesion: 0.16
Nodes (25): check_structured_sentence(), _cite_list(), lexical_support(), looks_rule_like(), _numbers_in(), Numbers/quantities the sentence asserts. Section references and (1)-style…, A sentence that states or implies law, whatever kind the model gave it., (share of the sentence's content words the quote supports, hits, words… (+17 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (33): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+25 more)

### Community 101 - "IncrementalDoc"
Cohesion: 0.15
Nodes (11): _Frame, IncrementalDoc, Truly incremental reader of the growing answer JSON: feed() consumes only the…, parametrize, _sentences_of(), split_random(), test_incremental_parser_cut_off_mid_sentence_and_prose_prefix(), test_incremental_parser_devanagari_and_escaped_quotes() (+3 more)

### Community 102 - "docx_out.py"
Cohesion: 0.10
Nodes (37): _add_font_table_fallback(), build_docx(), _get_or_add(), _insert_ordered(), _local(), _page_setup(), _paragraph(), Resolved layout blocks -> a real .docx (python-docx). Page and type set-up… (+29 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.18
Nodes (14): all_company_profiles(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent(), reminder_record_sent() (+6 more)

### Community 104 - "i18n.ts"
Cohesion: 0.13
Nodes (12): ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage(), getLawDoc(), getLawSection(), listPlaybooks() (+4 more)

### Community 105 - "render.py"
Cohesion: 0.11
Nodes (32): TemplateSpec, strip_inline(), _build_context(), _effective_language(), get_template(), get_template_detail(), _items(), list_templates() (+24 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.13
Nodes (22): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+14 more)

### Community 107 - "test_translit.py"
Cohesion: 0.15
Nodes (14): expand(), Devanagari statute terms for the roman/English words in `text` (deduplicated,…, index(), fixture, parametrize, V2: the romanised-Nepali -> statute-Nepali lexicon (app/translit.py). The…, The validation that keeps the lexicon honest: after the same tokenisation the…, test_chh_ch_variants_tolerated_but_theft_is_not_daughter() (+6 more)

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.11
Nodes (23): build_parser(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text., Truncate to a byte budget without splitting a multi-byte character (Devanagari… (+15 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "test_v3_structured.py"
Cohesion: 0.10
Nodes (41): check(), parametrize, V3: generate-then-verify. The model's JSON answer is checked sentence by…, _run(), S(), test_altered_quote_is_removed(), test_answer_review_rows_and_aggregate(), test_bad_citation_number_is_removed() (+33 more)

### Community 112 - "Store"
Cohesion: 0.17
Nodes (11): cmd_stats(), download(), giwms_files(), _is_doc_url(), main(), sources/regulators/<authority>/{files/,manifest.jsonl}, Rewrite the manifest keeping only the latest record per URL., Download doc['url'] into the store (skipped when already present) and record… (+3 more)

### Community 113 - "verifier.py"
Cohesion: 0.12
Nodes (22): _bridge(), check_sentence(), _clean_doc_sentence(), _expand_multiplier(), _guidance_ok(), guidance_term_set(), _in_terms(), _is_legal_claim() (+14 more)

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

### Community 118 - "test_v31_streaming.py"
Cohesion: 0.15
Nodes (29): fake_stream(), gen(), V3.1: progressive streaming with per-sentence verification. The provider stream…, Simulated provider at 40 ms per ~3-char token: time to first verified text vs…, What the frontend ends up showing: deltas append, `replace` swaps., run_events(), test_cache_hit_still_has_no_streaming_events(), test_cut_off_stream_shows_only_complete_sentences() (+21 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.20
Nodes (16): _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _query_tokens(), Non-LLM query -> playbook routing (S7). Scores each playbook's `keywords` list…, match(), but also returns the winning score. (+8 more)

### Community 120 - "scrape_lawcommission_gap"
Cohesion: 0.19
Nodes (14): _clean(), existing_corpus_titles(), giwms_table(), in_corpus(), Rows of a GIWMS table listing: | # | title | published | pdf link | ... |, Spelling/digit-insensitive identity of a law title (years are part of the…, title_key -> doc_title_ne for every law document in the pre-existing corpus…, True when a law of this title (same year, near-identical spelling:… (+6 more)

### Community 121 - "load_dense"
Cohesion: 0.18
Nodes (13): _download(), enabled(), load_dense(), model_ready(), prepare_model(), Path, Vectors for `ids` (the loaded corpus's passage ids, in row order), or None when…, Best-effort: a Dense for this corpus, or None (BM25-only). Never raises. (+5 more)

### Community 122 - "pytest"
Cohesion: 0.17
Nodes (6): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources(), pytest

### Community 123 - "answer_review.py"
Cohesion: 0.26
Nodes (9): aggregate(), main(), Passages, post(), Collect answers from a running API for human / LLM review of the V3 generate-…, Numbers in a rendered cited sentence that appear in none of its quotes (the '0…, Full text of cited sources: local corpus by id, else the API's section…, review_row() (+1 more)

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.05
Nodes (44): fill_paid(), S13: same expansion, billed to a specific paid-tier model…, paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, looks_like_injection(), ai_fill_field(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, S13: writes one llm_usage row per real (non-cached, non-free-tier) generation,… (+36 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "Dense"
Cohesion: 0.16
Nodes (8): Dense, Encoder, ndarray, L2-normalised float32 embeddings, shape (len(texts), DIM). Batches are length-…, int8 vectors aligned to an Index's row order. `have[i]` is False for rows with…, (n_passages, n_queries) cosine similarities; -1 where a passage has no vector., Query encoder + vector store for one Index., VectorStore

### Community 127 - "config.py"
Cohesion: 0.40
Nodes (3): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, dotenv

### Community 128 - "ingest_scraped.py"
Cohesion: 0.17
Nodes (20): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+12 more)

### Community 129 - "embedding_benchmark.py"
Cohesion: 0.23
Nodes (8): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), statistics

### Community 130 - "report.py"
Cohesion: 0.19
Nodes (12): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), Document (+4 more)

### Community 131 - "authority"
Cohesion: 0.20
Nodes (10): authority(), _giwms_site(), _links(), Discover legal-text categories from a GIWMS site's home page and crawl them., Ministry of Labour, Employment and Social Security: the bare host moless.gov.np…, Public Procurement Monitoring Office: PPA/PPR texts, directives and criteria., Nepal Gazette (rajpatra.dop.gov.np). Not reachable from the build sandbox; the…, scrape_gazette() (+2 more)

### Community 133 - "_View"
Cohesion: 0.21
Nodes (11): _fuzzy_span(), make_views(), _qtokens(), quote_in_source(), Quote tokens: NFC, PUA glyphs and punctuation/danda gone, digits ASCII,…, One source prepared for span matching., >=90% of the quote's tokens found in one contiguous run of the source (OCR'd…, None if the quote is a verbatim span of the source, else a reason code. (+3 more)

### Community 134 - "stream_json"
Cohesion: 0.18
Nodes (11): _compat_enabled(), last_finish_reason(), paid_stream(), Yield the raw text of a JSON answer as the provider writes it (free-tier chain:…, Streaming twin of paid_complete (same single Anthropic model, no fallback).…, Finish reason of this thread's last complete()/paid_complete(), if the provider…, stream_json(), was_cut_off() (+3 more)

### Community 135 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

### Community 136 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 137 - "Client"
Cohesion: 0.27
Nodes (5): Client, Fetch a page/file if robots allows. Returns response (any status < 500) or None., Fetch a page; `patient` re-tries a few times after a pause, for listing pages…, Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher., One rate-limited request with retry on 5xx/network errors. Returns the…

### Community 138 - "_generate_verified"
Cohesion: 0.21
Nodes (13): _generate_verified(), add_usage(), paid_call(), repair(), (structured.build() result | None if no model answered, usage). Never raises.…, Markdown in the shape the UI already shows: bold headings, bullets, inline [n]., render(), (verified doc, report). Failing sentences are dropped; blocks left with nothing… (+5 more)

### Community 139 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 140 - "quantize"
Cohesion: 0.31
Nodes (9): quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., save_vectors(), test_quantize_roundtrip_keeps_cosine(), test_store_digest_mismatch_reuses_surviving_ids(), test_store_exact_match(), test_store_same_ids_other_digest_is_used_but_flagged(), _vectors() (+1 more)

### Community 141 - "FakeDense"
Cohesion: 0.25
Nodes (5): FakeDense, attach(), idx(), fixture, Stands in for dense.Dense: `wanted` maps query text -> {passage id: cosine};…

### Community 142 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), Pattern, A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale()

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 144 - "_targets"
Cohesion: 0.36
Nodes (8): _cool_target(), _model_key(), _openai_complete(), (base_url, api_key, model_id sent to the API, cooldown key)., Expand a "provider/model" chain into concrete endpoint+key+model calls:…, _Target, _targets(), tuple

### Community 145 - "tidy_answer"
Cohesion: 0.50
Nodes (4): Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer(), test_dhara_becomes_dafa_for_statutes_only(), test_trailing_empty_heading_is_removed()

### Community 146 - "_playbook_id_for"
Cohesion: 0.29
Nodes (7): _playbook_id_for(), A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, laws(), Exact corpus titles of the statutes the matched strong entries point to., The half-match on "boss" must neither skip the LLM nor pin the Workplace Sexual…, test_the_wrong_playbook_is_not_a_confident_match(), test_laws_are_reported_for_strong_matches_only()

### Community 147 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

### Community 149 - "scrape_nia"
Cohesion: 0.29
Nodes (7): _first_reachable(), nia_rows(), The first base URL whose home page answers (a site can serve one scheme/host…, (title, ISO date, pdf url) rows of one NIA /law/ page. Only the main table is…, Nepal Insurance Authority (nia.gov.np; formerly Beema Samiti). Its HTTPS…, scrape_nia(), V-batch 2b — OCR of the scanned regulator PDFs + NIA/MoLESS (2026-09-30)

### Community 150 - "_gemini_complete"
Cohesion: 0.53
Nodes (6): _cool(), _gemini(), _gemini_cfg(), _gemini_complete(), _gemini_stream(), _ready()

### Community 153 - "flat_fee"
Cohesion: 0.67
Nodes (3): flat_fee(), The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., test_flat_fee_rejects_an_unknown_case_type()

## Knowledge Gaps
- **301 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+296 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1124 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `generation.py`, `ui.tsx`, `run_eval.py`, `get_index`, `Done`, `chat`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `embedding_benchmark.py`, `S5 — Supabase auth + DB (2026-09-26)`, `generation.py`, `documents.py`, `test_v1_trust_engine.py`, `playbooks.py`, `chat.py`, `search`, `test_translit.py`, `Index`, `test_documents_audit.py`, `retrieval.py`, `test_eval_sets.py`, `run_eval.py`, `normalise_text`, `chat`, `checklists.py`, `limitation.py`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _301 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.05004389815627744 - nodes in this community are weakly interconnected._
- **Should `labour_rights.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11692307692307692 - nodes in this community are weakly interconnected._