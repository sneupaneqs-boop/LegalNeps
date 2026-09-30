# Graph Report - LegalNeps  (2026-09-30)

## Corpus Check
- 215 files · ~526,578 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .jsonl 11, (none) 6, .css 5)

## Summary
- 3460 nodes · 8184 edges · 163 communities (142 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 332 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `16d516fe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- claim_checks.py
- api.ts
- match
- cite
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
- tools.py
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
- generation.py
- documents.py
- useLang
- LangContext.tsx
- playbooks.py
- ingest_regulators.py
- schemas.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- newest_per_series
- test_ocr_clean.py
- get
- test_documents_audit.py
- search/page.tsx
- smoke.spec.ts
- test_retrieval.py
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
- test_drafting.py
- parse_answer
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- verifier.py
- Per-playbook findings
- IncrementalDoc
- docx_out.py
- run
- i18n.ts
- render.py
- extract_doc_meta
- verifier_calibration.py
- scrape_lawcommission.py
- nepali.py
- contract_fixtures.py
- test_v3_structured.py
- Store
- test_v32_claim_checks.py
- test_s12_compliance_radar.py
- scripts
- ocr_clean.py
- test_eval_sets.py
- test_v31_streaming.py
- playbook_matcher.py
- scrape_lawcommission_gap
- scrape_regulators.py
- test_s11_matters.py
- AuditPage
- test_s13_ai_gateway.py
- Env
- load_dense
- app/__init__.py
- sys
- embedding_benchmark.py
- report.py
- authority
- calendar
- _View
- was_cut_off
- draft_update
- compliance/page.tsx
- Client
- build
- page_verdict
- quantize
- FakeDense
- mark_stale_precedents
- Run the API in Docker (no cloud payment needed)
- StreamVerifier
- filter_gaps
- ics.ts
- is_table_noise
- ingest_pdfs.py
- Done
- guess_language
- situation_guards.py
- _SSE
- entailment_filter
- .search
- alignment_ok
- devDependencies
- giwms_listing
- calls
- number_role_conflict
- _LRU
- chunks
- test_paid_tier_streams_and_reports_usage_and_runs_entailment_last

## God Nodes (most connected - your core abstractions)
1. `get()` - 61 edges
2. `get_index()` - 54 edges
3. `available()` - 47 edges
4. `useLang()` - 43 edges
5. `_http()` - 42 edges
6. `useTools()` - 41 edges
7. `S()` - 40 edges
8. `cite()` - 34 edges
9. `_date()` - 34 edges
10. `analyze_query()` - 33 edges

## Surprising Connections (you probably didn't know these)
- `V-batch 1 — trust engine, full UI, Document AI (2026-09-29)` --references--> `search()`  [INFERRED]
  docs/PROGRESS.md → backend/app/generation.py
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `V-batch 2b — OCR of the scanned regulator PDFs + NIA/MoLESS (2026-09-30)` --references--> `nia_rows()`  [INFERRED]
  docs/PROGRESS.md → backend/scripts/scrape_regulators.py
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `V3.2 — Claim checks from the live review, entailment v2, token diet (2026-09-30, offline; live re-measure pending)` --references--> `proviso_dropped()`  [INFERRED]
  docs/PROGRESS.md → backend/app/claim_checks.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (163 total, 21 thin omitted)

### Community 0 - "claim_checks.py"
Cohesion: 0.07
Nodes (45): CheckContext, _clean(), dangling_additive(), document_requirement(), _fmt(), _folded(), forum_classes(), forum_not_in_sources() (+37 more)

### Community 1 - "api.ts"
Cohesion: 0.06
Nodes (47): remove(), remove(), adToBs(), Amendment, ApiError, AppealFeeResult, BsDate, bsToAd() (+39 more)

### Community 2 - "match"
Cohesion: 0.08
Nodes (36): canon(), Entry, expand(), laws(), _lookup(), loose(), match(), _parse() (+28 more)

### Community 3 - "cite"
Cohesion: 0.07
Nodes (43): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, max_lawful_rate(), Interest on private loans under the Muluki Civil Code, 2074, chapter 15 (लेनदेन…, check_hours(), festival_allowance(), fund_contributions(), leave_accrual() (+35 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.09
Nodes (36): _is_regulator_query(), _pipeline_fingerprint(), _reset_cache_for_tests(), _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status(), _haystack_numbers(), _is_legal_claim() (+28 more)

### Community 5 - "llm.py"
Cohesion: 0.07
Nodes (57): _anthropic_complete(), _call_limit(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini() (+49 more)

### Community 6 - "test_dense.py"
Cohesion: 0.15
Nodes (18): hybrid(), attach(), idx(), fixture, Dense retrieval: vector store (digest mismatch, missing file, id alignment),…, Attach a fake dense, restore afterwards., test_agreement_beats_either_signal_alone(), test_bills_never_surface_by_default_even_if_dense_top() (+10 more)

### Community 7 - "test_api.py"
Cohesion: 0.08
Nodes (13): focus(), normalize_citations(), The part of a passage that matters for this question: the heading line plus the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, client(), fixture (+5 more)

### Community 8 - "extract_laws.py"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.17
Nodes (32): available(), company_profile_get(), draft_get(), draft_list(), _http(), llm_usage_list(), llm_usage_record(), matter_create() (+24 more)

### Community 10 - "search"
Cohesion: 0.11
Nodes (20): _is_fiscal_query(), _match_playbook(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, The curated action plan for this situation, when the keyword matcher is…, search(), (system, user prompt, max_tokens, sources sent, sources retrieved, lang) as the…, request_parts() (+12 more)

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
Cohesion: 0.11
Nodes (11): Index, Load the query encoder + corpus vectors if available (best-effort, never…, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., test_stream_endpoint_forwards_replace() (+3 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "tools.py"
Cohesion: 0.08
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "tokenize"
Cohesion: 0.16
Nodes (19): law_topic_terms(), Stemmed section titles of the retrieved STATUTES ("बेइज्जती गर्न नहुने",…, fold(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term() (+11 more)

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
Cohesion: 0.14
Nodes (14): fill(), Expand `hint` into fuller prose for `field_id` of `template_id`, in `language`,…, requires_corpus, S10: LLM-assisted free-text fill for drafting templates, plus saving a draft…, test_ai_fill_endpoint_bad_field(), test_ai_fill_endpoint_requires_auth_and_is_metered(), test_ai_fill_expands_hint_via_llm(), test_ai_fill_includes_other_answers_as_context() (+6 more)

### Community 22 - "test_regulators_ingest.py"
Cohesion: 0.16
Nodes (10): _text_key(), _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip() (+2 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.06
Nodes (52): appeal_fee(), court_fee(), estimate(), estimate_appeal(), flat_fee(), flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2)). (+44 more)

### Community 24 - "retrieval.py"
Cohesion: 0.08
Nodes (36): array, clear_query_cache(), passage_text(), Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, Load everything and run one query through it (used by…, Document title + section heading + body, Nepali first, English title/heading…, warm_up(), get_index() (+28 more)

### Community 25 - "audit.py"
Cohesion: 0.10
Nodes (25): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+17 more)

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
Cohesion: 0.07
Nodes (45): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message can be searched well WITHOUT an LLM rewriting it.…, The one rule for "answer this question without the query-rewrite call" - shared… (+37 more)

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

### Community 60 - "Progress"
Cohesion: 0.20
Nodes (11): parametrize, test_enacted_date_matches_known_acts(), Pin the headline numbers so an edit to the YAML can't drift from the law., test_numeric_rules_match_the_statute_numbers(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit) (+3 more)

### Community 61 - "chat"
Cohesion: 0.15
Nodes (19): chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage(), _log_request() (+11 more)

### Community 62 - "checklists.py"
Cohesion: 0.14
Nodes (22): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+14 more)

### Community 63 - "limitation.py"
Cohesion: 0.07
Nodes (49): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+41 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "chat.py"
Cohesion: 0.09
Nodes (43): corpus_stats(), ai_fill_field(), create_draft(), create_matter(), create_matter_note(), create_matter_task(), delete_draft(), delete_matter() (+35 more)

### Community 67 - "generation.py"
Cohesion: 0.07
Nodes (47): _answer_cache_key(), answer_max_tokens(), answer_question(), answer_system(), _cache_key(), check_context(), _extractive(), _generate_verified() (+39 more)

### Community 68 - "documents.py"
Cohesion: 0.07
Nodes (37): asyncio, AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut (+29 more)

### Community 69 - "useLang"
Cohesion: 0.09
Nodes (58): Account(), AccountPage(), Compliance(), CompliancePage(), ProfileForm(), submit(), FilesTab(), download() (+50 more)

### Community 70 - "LangContext.tsx"
Cohesion: 0.11
Nodes (28): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+20 more)

### Community 71 - "playbooks.py"
Cohesion: 0.13
Nodes (24): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), ValueError, Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Every playbook with every provision resolved - raises UnresolvedProvision on…, A playbook cites a law_title_ne/section that isn't in the corpus. (+16 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (31): assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest(), english_title() (+23 more)

### Community 73 - "schemas.py"
Cohesion: 0.08
Nodes (47): AiFillRequest, AiFillResponse, Amendment, Analysis, Bilingual, ChatRequest, ChatResponse, CompanyProfileIn (+39 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.08
Nodes (25): 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500) (+17 more)

### Community 75 - "glossary.py"
Cohesion: 0.26
Nodes (11): _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes… (+3 more)

### Community 76 - "newest_per_series"
Cohesion: 0.20
Nodes (11): _ad_date(), newest_per_series(), _nrb_listing_pages(), pub_sort_key(), Title with amendment parentheticals, digits and punctuation removed, so 'X ऐन,…, Comparable (year, month, day) for an AD ('July 22, 2025', '2025-07-22') or BS…, Keep the newest document of each title series (dated docs win; ties keep the…, Yield (href, title, date_str) over a paginated NRB category listing. (+3 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "get"
Cohesion: 0.10
Nodes (30): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+22 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (37): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+29 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "smoke.spec.ts"
Cohesion: 0.14
Nodes (6): Json, API, API_WAIT, PAGES, ref_node_fs, @playwright/test

### Community 82 - "test_retrieval.py"
Cohesion: 0.11
Nodes (6): idx(), fixture, test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours()

### Community 83 - "test_s14_security.py"
Cohesion: 0.08
Nodes (22): audit_log(), draft_delete(), matter_delete(), matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, Best-effort record of an irreversible user action (a delete, so far - see…, safe_filename() (+14 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (122): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+114 more)

### Community 87 - "run_eval.py"
Cohesion: 0.10
Nodes (31): parse_json(), parse_verdicts(), One verdict (yes/no/partial) per item from {"v":["y",...]} or the older…, aggregate(), main(), Passages, post(), Collect answers from a running API for human / LLM review of the V3 generate-… (+23 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.17
Nodes (17): frontend_app_audit_audit, FindingRow(), fmtValue(), humanize(), L, AuditResult, Bi, ChecklistCheck (+9 more)

### Community 89 - "segment.py"
Cohesion: 0.12
Nodes (24): _coerce(), Coerce a model-returned value to the fact's declared type, or None., Model JSON -> {fact: {"value": typed value | None, "clause_id": str | None}}.…, validate_extraction(), _ascii(), Clause, clause_by_id(), _clause_start() (+16 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "dsl.py"
Cohesion: 0.12
Nodes (32): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+24 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (31): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+23 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "test_drafting.py"
Cohesion: 0.13
Nodes (13): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_list_templates_matches_registry() (+5 more)

### Community 95 - "parse_answer"
Cohesion: 0.29
Nodes (8): _norm_doc(), _norm_sentence(), parse_answer(), (doc, complete). complete=False when the object was cut off or broken and only…, test_complete_json_parses_and_fenced_json_too(), test_cut_off_flag_alone_marks_a_parseable_answer_truncated(), test_truncated_json_keeps_every_complete_sentence_and_drops_the_partial_one(), test_truncation_between_blocks_and_inside_a_heading()

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.09
Nodes (41): frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload() (+33 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.15
Nodes (17): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+9 more)

### Community 99 - "verifier.py"
Cohesion: 0.08
Nodes (45): Remove a leading "But/And/तर/र" that joined the sentence to one that was…, strip_leading_conjunction(), check_sentence(), check_structured_sentence(), _cite_conflicts(), _cite_list(), _clean_doc_sentence(), _guidance_ok() (+37 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (32): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+24 more)

### Community 101 - "IncrementalDoc"
Cohesion: 0.20
Nodes (5): _Frame, IncrementalDoc, Truly incremental reader of the growing answer JSON: feed() consumes only the…, test_incremental_parser_never_rescans_consumed_text(), V3.1 — Progressive streaming with per-sentence verification (2026-09-30, offline; live latency pending)

### Community 102 - "docx_out.py"
Cohesion: 0.19
Nodes (21): _add_font_table_fallback(), build_docx(), _get_or_add(), _insert_ordered(), _local(), _page_setup(), _paragraph(), Resolved layout blocks -> a real .docx (python-docx). Page and type set-up… (+13 more)

### Community 103 - "run"
Cohesion: 0.21
Nodes (12): all_company_profiles(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent(), reminder_record_sent() (+4 more)

### Community 104 - "i18n.ts"
Cohesion: 0.11
Nodes (19): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+11 more)

### Community 105 - "render.py"
Cohesion: 0.08
Nodes (46): TemplateSpec, Inline emphasis inside a paragraph: **bold** and __underline__ (e.g. the bold…, [(segment, bold, underline), ...]; markers toggle the style and are dropped., split_inline(), strip_inline(), build_html(), build_pdf(), _inline() (+38 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.20
Nodes (15): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, requires_corpus (+7 more)

### Community 107 - "verifier_calibration.py"
Cohesion: 0.20
Nodes (12): argparse, corpus_source(), load_passages(), prf(), Calibrate the deterministic checks of the V3 verifier on the 119 human-labelled…, summarise(), _init(), main() (+4 more)

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.10
Nodes (24): build_parser(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text., Truncate to a byte budget without splitting a multi-byte character (Devanagari… (+16 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "test_v3_structured.py"
Cohesion: 0.15
Nodes (33): check(), parametrize, V3: generate-then-verify. The model's JSON answer is checked sentence by…, _run(), S(), test_altered_quote_is_removed(), test_bad_citation_number_is_removed(), test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook() (+25 more)

### Community 112 - "Store"
Cohesion: 0.24
Nodes (6): cmd_stats(), main(), sources/regulators/<authority>/{files/,manifest.jsonl}, Rewrite the manifest keeping only the latest record per URL., run_authority(), Store

### Community 113 - "test_v32_claim_checks.py"
Cohesion: 0.07
Nodes (56): guidance_term_set(), make_views(), ctx_of(), _ctx_reason(), _doc_with(), judge(), labelled(), parametrize (+48 more)

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
Cohesion: 0.13
Nodes (34): fake_stream(), gen(), parametrize, V3.1: progressive streaming with per-sentence verification. The provider stream…, Simulated provider at 40 ms per ~3-char token: time to first verified text vs…, What the frontend ends up showing: deltas append, `replace` swaps., run_events(), _sentences_of() (+26 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.14
Nodes (22): _playbook_id_for(), A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _query_tokens() (+14 more)

### Community 120 - "scrape_lawcommission_gap"
Cohesion: 0.27
Nodes (10): existing_corpus_titles(), in_corpus(), Spelling/digit-insensitive identity of a law title (years are part of the…, title_key -> doc_title_ne for every law document in the pre-existing corpus…, True when a law of this title (same year, near-identical spelling:…, Compare the Law Commission's current-acts index (alphabetical index page: ~350…, scrape_lawcommission_gap(), fresh() (+2 more)

### Community 121 - "scrape_regulators.py"
Cohesion: 0.20
Nodes (14): download(), fiscal_year_bs(), giwms_files(), _is_doc_url(), _links(), _now(), Scrapes primary regulatory texts (acts, regulations, directives, circulars)…, Download doc['url'] into the store (skipped when already present) and record… (+6 more)

### Community 122 - "test_s11_matters.py"
Cohesion: 0.18
Nodes (5): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 123 - "AuditPage"
Cohesion: 0.21
Nodes (11): AuditPage(), describe(), handleDownload(), runAudit(), fmtBytes(), auditDocument(), DocumentsApiError, downloadAuditReport() (+3 more)

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.05
Nodes (49): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+41 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "load_dense"
Cohesion: 0.09
Nodes (22): Dense, _download(), enabled(), Encoder, load_dense(), model_ready(), prepare_model(), ndarray (+14 more)

### Community 127 - "app/__init__.py"
Cohesion: 0.10
Nodes (19): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, entail_payload(), _objects_from(), V3: generate-then-verify answers. The model returns ONE JSON object (blocks of…, Complete {...} objects of the array whose items start at `pos`; whether the…, Every complete block, and every complete sentence of the block that was cut off., (compact JSON for the entailment call, [(block, sentence) per item]). One item… (+11 more)

### Community 128 - "sys"
Cohesion: 0.14
Nodes (18): Builds backend/app/data/glossary.json: English and romanised-Nepali words…, ask_json(), load_corpus(), load_ingested(), load_manifest(), main(), Step 2 of the scrape pipeline: turns documents downloaded by…, save_corpus() (+10 more)

### Community 129 - "embedding_benchmark.py"
Cohesion: 0.23
Nodes (8): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), statistics

### Community 130 - "report.py"
Cohesion: 0.21
Nodes (11): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), Document (+3 more)

### Community 131 - "authority"
Cohesion: 0.18
Nodes (11): authority(), _clean(), giwms_table(), nia_rows(), Rows of a GIWMS table listing: | # | title | published | pdf link | ... |, (title, ISO date, pdf url) rows of one NIA /law/ page. Only the main table is…, Nepal Insurance Authority (nia.gov.np; formerly Beema Samiti). Its HTTPS…, Nepal Gazette (rajpatra.dop.gov.np). Not reachable from the build sandbox; the… (+3 more)

### Community 133 - "_View"
Cohesion: 0.10
Nodes (28): clause_context(), Layout, _locate(), quote_section(), Section/rule numbers a sentence names as ITS provision (not sub-section /…, A passage split (a) at section headings ("२३. विवरण सच्याउने :") and (b) at…, The heading number the quote sits under, when the passage holds several…, The sentence names a section/rule that is another heading of the same passage… (+20 more)

### Community 134 - "was_cut_off"
Cohesion: 0.40
Nodes (5): last_finish_reason(), Finish reason of this thread's last complete()/paid_complete(), if the provider…, was_cut_off(), test_stream_json_retries_without_response_format_and_reports_finish(), test_llm_cut_off_detection()

### Community 135 - "draft_update"
Cohesion: 0.32
Nodes (8): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured(), S10 — Drafting + AI fill + save (2026-09-28)

### Community 136 - "compliance/page.tsx"
Cohesion: 0.22
Nodes (11): daysLabel(), ENTITY_TYPES, Obligations(), addToCalendar(), WINDOWS, CompanyProfile, EntityType, getCompanyProfile() (+3 more)

### Community 137 - "Client"
Cohesion: 0.15
Nodes (13): Client, _first_reachable(), _giwms_site(), Fetch a page/file if robots allows. Returns response (any status < 500) or None., Fetch a page; `patient` re-tries a few times after a pause, for listing pages…, Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher., Discover legal-text categories from a GIWMS site's home page and crawl them., One rate-limited request with retry on 5xx/network errors. Returns the… (+5 more)

### Community 138 - "build"
Cohesion: 0.13
Nodes (18): build(), _log_fallback(), Markdown in the shape the UI already shows: bold headings, bullets, inline [n]., Why an answer fell back to the extractive provisions: structure counts only (no…, The model's raw reply -> {"answer": markdown | None, "verification": report,…, _recount(), render(), verified_rule_count() (+10 more)

### Community 139 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 140 - "quantize"
Cohesion: 0.36
Nodes (8): quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., test_quantize_roundtrip_keeps_cosine(), test_store_digest_mismatch_reuses_surviving_ids(), test_store_exact_match(), test_store_same_ids_other_digest_is_used_but_flagged(), _vectors(), _write()

### Community 142 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), Pattern, A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale()

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 144 - "StreamVerifier"
Cohesion: 0.20
Nodes (9): clean_ocr_text(), dedupe_marks(), OCR glitches the model copied from a scanned source into its own sentence: a…, [5][5] -> [5]; order kept., _line(), Verify each sentence the moment it is complete and produce the markdown pieces…, New model text in; the text now safe to show (possibly ""), out., StreamVerifier (+1 more)

### Community 145 - "filter_gaps"
Cohesion: 0.24
Nodes (11): _dev_share(), filter_gaps(), gap_in_language(), (kept gaps, [(dropped gap, reason)]). Cited passages are tested first, then…, _clean_side_text(), _passage_text(), Gaps and follow-up questions carry no legal claim: keep them short and number-…, _gap_case() (+3 more)

### Community 146 - "ics.ts"
Cohesion: 0.29
Nodes (9): RFC-5545, buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay(), stamp() (+1 more)

### Community 147 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

### Community 148 - "ingest_pdfs.py"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 149 - "Done"
Cohesion: 0.16
Nodes (14): _entry_status(), _index_text(), _prior(), Authority of the source x usefulness of this particular passage., Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S4 — Search + law browser UI (2026-09-26) (+6 more)

### Community 150 - "guess_language"
Cohesion: 0.22
Nodes (9): _is_devanagari(), Script check on the message itself. NOT the language hint: the hint is "ne" for…, _is_english(), Latin-script and not romanised Nepali ("mero ghardhani le bhada badhayo")., guess_language(), Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised…, The hint is 'ne' for romanised Nepali, so it can never be used as a 'the index…, test_root_cause_language_hint_calls_romanised_nepali_ne() (+1 more)

### Community 151 - "situation_guards.py"
Cohesion: 0.25
Nodes (8): Guard, Pattern, _r(), V3.2: a small DATA table of wrong-law guards - (what the user's question says…, The id of the guard that forbids citing `source` for this question, else None., _section_no(), violation(), _guard_hit()

### Community 152 - "_SSE"
Cohesion: 0.24
Nodes (4): BaseHTTPRequestHandler, _SSE, pipeline(), fixture

### Community 153 - "entailment_filter"
Cohesion: 0.22
Nodes (7): entailment_filter(), ONE cheap call over every cited sentence: drop those whose quote does NOT…, test_build_runs_entailment_only_when_given_and_recounts(), test_entailment_fails_open(), boom(), test_entailment_removes_no_and_keeps_yes_and_partial(), test_run_provider_failure_gives_the_extractive_answer()

### Community 154 - ".search"
Cohesion: 0.33
Nodes (4): ndarray, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, Adds each eligible query's dense (cosine) ranking to `fused` in place, by…, _title_tokens()

### Community 155 - "alignment_ok"
Cohesion: 0.40
Nodes (6): alignment_ok(), _lev(), near_variant(), Same word up to a character slip (matra/spelling/OCR): edit distance 1, or 2…, Every token of the quote is in the passage window, or is a near variant of the…, test_fused_or_split_words_are_line_break_noise_not_substitution()

### Community 156 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 157 - "giwms_listing"
Cohesion: 0.40
Nodes (5): bs_key(), giwms_listing(), १३ असोज, २०८३' or '2083-06-13' -> (2083, 6, 13) for ordering; None if…, Iterate a GIWMS category listing (?page=N). Only the main list is read (not the…, scrape_ocr()

### Community 158 - "calls"
Cohesion: 0.40
Nodes (4): calls(), llm_on(), fixture, Replace llm.complete with a recorder that returns LLM_REPLY.

### Community 159 - "number_role_conflict"
Cohesion: 0.50
Nodes (4): number_role_conflict(), A reason code when a number of the sentence is bound to a unit/head noun the…, test_number_role_property_same_pair_passes_other_value_same_unit_fails(), test_number_with_unit_swapped_is_refused_and_unbound_numbers_are_not_judged()

### Community 161 - "chunks"
Cohesion: 0.67
Nodes (3): chunks(), Word-boundary chunks of ~`size` chars (newlines kept) for simulated streaming., test_chunks_are_small_lossless_and_never_split_a_citation()

## Knowledge Gaps
- **303 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+298 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1176 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `analyze_query`, `generation.py`, `LangContext.tsx`, `Done`, `retrieval.py`, `chat`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `LangContext.tsx` to `S5 — Supabase auth + DB (2026-09-26)`, `useLang`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `get_index()` connect `retrieval.py` to `embedding_benchmark.py`, `match`, `cite`, `test_v1_trust_engine.py`, `search`, `Index`, `analyze_query`, `chat`, `checklists.py`, `limitation.py`, `chat.py`, `generation.py`, `documents.py`, `playbooks.py`, `get`, `test_documents_audit.py`, `run_eval.py`, `S5 — Supabase auth + DB (2026-09-26)`, `verifier_calibration.py`, `test_eval_sets.py`, `app/__init__.py`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _303 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `claim_checks.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07358156028368794 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06462585034013606 - nodes in this community are weakly interconnected._