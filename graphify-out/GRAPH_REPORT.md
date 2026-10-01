# Graph Report - LegalNeps  (2026-10-01)

## Corpus Check
- 226 files · ~634,541 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: .jsonl 12, (none) 6, .css 5)

## Summary
- 3659 nodes · 8711 edges · 177 communities (154 shown, 23 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 343 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5e8dded3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- claim_checks.py
- api.ts
- test_translit.py
- labour_rights.py
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
- cite
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- generation.py
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
- catalog
- ocr_regulators.py
- forms_common.py
- chat.py
- _generate_verified
- documents.py
- useLang
- ui.tsx
- limitation.py
- ingest_regulators.py
- schemas.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- re
- check
- test_ocr_clean.py
- _bad_input
- test_documents_audit.py
- search/page.tsx
- smoke.spec.ts
- test_retrieval.py
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
- ai_fill.py
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- _View
- Per-playbook findings
- IncrementalDoc
- docx_out.py
- run
- i18n.ts
- render.py
- extract_doc_meta
- verifier.py
- scrape_lawcommission.py
- nepali.py
- contract_fixtures.py
- test_v3_structured.py
- topical_fit_calibration.py
- test_v32_claim_checks.py
- _date
- scripts
- ocr_clean.py
- main.py
- test_v31_streaming.py
- playbook_matcher.py
- test_v33_topical_fit.py
- scrape_regulators.py
- pytest
- test_eval_sets.py
- test_s13_ai_gateway.py
- Env
- Dense
- parse_answer
- ingest_scraped.py
- search
- verify_sentence
- audit_document
- calendar
- Layout
- Scorer
- matter_file_create
- filter_gaps
- Client
- build
- page_verdict
- load_dense
- StreamVerifier
- mark_stale_precedents
- Run the API in Docker (no cloud payment needed)
- fit_reply.py
- make_profile
- compliance/page.tsx
- is_table_noise
- authority
- Done
- match
- situation_guards.py
- _SSE
- parse_verdicts
- .search
- alignment_ok
- newest_per_series
- pipeline
- Store
- number_role_conflict
- _LRU
- scrape_lawcommission_gap
- quantize
- draft_update
- FakeDense
- entailment_filter
- _lookup
- S13 — AI gateway v2 (2026-09-29)
- load_model
- cache_put
- giwms_listing
- test_chat_route_anonymous_caller_stays_on_free_tier
- tidy_answer
- _temporal_status
- _is_regulator_query
- _pipeline_fingerprint
- test_procurement_insurance_labour_regulator_passages_stay_in_their_field

## God Nodes (most connected - your core abstractions)
1. `get_index()` - 65 edges
2. `get()` - 61 edges
3. `available()` - 47 edges
4. `useLang()` - 43 edges
5. `_http()` - 42 edges
6. `useTools()` - 41 edges
7. `tokenize()` - 40 edges
8. `S()` - 40 edges
9. `run()` - 39 edges
10. `analyze_query()` - 36 edges

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

## Communities (177 total, 23 thin omitted)

### Community 0 - "claim_checks.py"
Cohesion: 0.07
Nodes (47): CheckContext, _clean(), dangling_additive(), document_requirement(), _fmt(), _folded(), forum_classes(), forum_not_in_sources() (+39 more)

### Community 1 - "api.ts"
Cohesion: 0.07
Nodes (45): adToBs(), Amendment, ApiError, AppealFeeResult, BsDate, bsToAd(), calcGratuity(), calcNotice() (+37 more)

### Community 2 - "test_translit.py"
Cohesion: 0.15
Nodes (14): expand(), Devanagari statute terms for the roman/English words in `text` (deduplicated,…, index(), fixture, parametrize, V2: the romanised-Nepali -> statute-Nepali lexicon (app/translit.py). The…, The validation that keeps the lexicon honest: after the same tokenisation the…, test_chh_ch_variants_tolerated_but_theft_is_not_daughter() (+6 more)

### Community 3 - "labour_rights.py"
Cohesion: 0.12
Nodes (25): check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), leave_entitlements(), row(), _money() (+17 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.14
Nodes (26): _reset_cache_for_tests(), _haystack_numbers(), _is_legal_claim(), Returns (answer with unsupported legal claims marked, report)., verify(), _words_to_digits(), parametrize, V1: trust engine - deterministic citation verifier, status on every source,… (+18 more)

### Community 5 - "llm.py"
Cohesion: 0.06
Nodes (67): The per-piece part of tidy_answer (the constitutional "धारा" fix), so streamed…, Stream the model's JSON, verifying every sentence as it completes. A generator:…, _stream_generate(), _tidy_piece(), _anthropic_complete(), _call_limit(), _client_http(), _compat_enabled() (+59 more)

### Community 6 - "test_dense.py"
Cohesion: 0.18
Nodes (15): hybrid(), Dense retrieval: vector store (digest mismatch, missing file, id alignment),…, Attach a fake dense, restore afterwards., test_agreement_beats_either_signal_alone(), test_bills_never_surface_by_default_even_if_dense_top(), test_category_filter_after_fusion(), test_dense_finds_what_bm25_cannot(), test_dense_weight_shifts_the_order() (+7 more)

### Community 7 - "test_api.py"
Cohesion: 0.08
Nodes (13): focus(), normalize_citations(), _passage(), The part of a passage that matters for this question: the heading line plus the…, One numbered passage for the prompt, in ONE language (V3.2 token diet): the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, client(), fixture (+5 more)

### Community 8 - "extract_laws.py"
Cohesion: 0.07
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), find_sections(), _font_bytes(), _font_family() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.20
Nodes (28): available(), _http(), llm_usage_list(), llm_usage_record(), matter_create(), matter_file_delete(), matter_file_list(), matter_file_signed_url() (+20 more)

### Community 10 - "test_v25_routing.py"
Cohesion: 0.08
Nodes (49): _is_bank_query(), _is_fiscal_query(), _match_playbook(), _nrb_directive_hits(), _playbook_id_for(), _playbook_pick(), playbook_support(), `text` with known Devanagari spelling slips corrected (unchanged when nothing… (+41 more)

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
Nodes (10): Index, Load the query encoder + corpus vectors if available (best-effort, never…, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., test_stream_endpoint_forwards_replace() (+2 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "get"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "tokenize"
Cohesion: 0.15
Nodes (20): law_topic_terms(), Stemmed section titles of the retrieved STATUTES ("बेइज्जती गर्न नहुने",…, fold(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term() (+12 more)

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
Nodes (9): _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip(), test_status_is_never_guessed() (+1 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.06
Nodes (52): appeal_fee(), court_fee(), estimate(), estimate_appeal(), flat_fee(), flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2)). (+44 more)

### Community 24 - "retrieval.py"
Cohesion: 0.04
Nodes (78): argparse, array, _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, clear_query_cache(), passage_text(), Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, Load everything and run one query through it (used by… (+70 more)

### Community 25 - "audit.py"
Cohesion: 0.10
Nodes (25): AuditError, AuditMeta, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines() (+17 more)

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
Cohesion: 0.06
Nodes (56): age_on(), markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days() (+48 more)

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "generation.py"
Cohesion: 0.04
Nodes (79): The corpus files a long section under its FIRST sub-section ("दफा 10 (1)")…, relabel_subsections(), analyze_needs_llm(), analyze_query(), answer_question(), apply_topical_gate(), build_queries(), check_context() (+71 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "test_calculators_tools.py"
Cohesion: 0.06
Nodes (65): Problems (empty when fine) with one source., verify_source(), income_tax(), Annual income tax on `taxable_income` (NPR) for a resident individual or couple…, api(), _corpus_hadmyad_sections(), fixture, parametrize (+57 more)

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
Cohesion: 0.22
Nodes (10): Pin the headline numbers so an edit to the YAML can't drift from the law., test_numeric_rules_match_the_statute_numbers(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus), Next session (+2 more)

### Community 61 - "chat"
Cohesion: 0.12
Nodes (22): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+14 more)

### Community 62 - "checklists.py"
Cohesion: 0.17
Nodes (19): _keyword_table(), assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_raw(), _load_all(), public_listing() (+11 more)

### Community 63 - "catalog"
Cohesion: 0.15
Nodes (19): _by_id(), catalog(), entry_view(), general_rules(), is_computable(), list_claim_types(), The public JSON shape of one entry (also what the catalog lists)., Every entry, grouped by category (categories in the file's order). (+11 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "chat.py"
Cohesion: 0.08
Nodes (51): corpus_stats(), create_draft(), create_matter(), create_matter_note(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file() (+43 more)

### Community 67 - "_generate_verified"
Cohesion: 0.11
Nodes (20): answer_max_tokens(), answer_system(), _generate_verified(), add_usage(), paid_call(), repair(), (structured.build() result | None if no model answered, usage). Never raises.…, Output budget for the answer JSON. Groq/Gemini free tiers count the requested… (+12 more)

### Community 68 - "documents.py"
Cohesion: 0.15
Nodes (20): asyncio, AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut (+12 more)

### Community 69 - "useLang"
Cohesion: 0.09
Nodes (59): Account(), AccountPage(), Compliance(), CompliancePage(), Obligations(), ProfileForm(), submit(), FilesTab() (+51 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (30): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+22 more)

### Community 71 - "limitation.py"
Cohesion: 0.05
Nodes (61): Labour Act, 2074 (श्रम ऐन, २०७४) calculators (S8): gratuity, termination…, normalise_text(), parse_period_phrase(), Limitation-period (हदम्याद) database and deadline checker (S8, extended).…, Resolve every entry's citation once. None marks a citation the corpus no longer…, Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari…, (value, unit) of the number+unit at the start of a phrase like 'छ महिनाभित्र'… (+53 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): _text_key(), assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest() (+24 more)

### Community 73 - "schemas.py"
Cohesion: 0.08
Nodes (43): ai_fill_field(), get_drafting_template(), list_draft_versions(), list_drafting_templates(), list_llm_usage(), match_playbooks(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, Expands a free-text field's short hint via the LLM. Signed-in only, metered… (+35 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.08
Nodes (25): 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500) (+17 more)

### Community 75 - "re"
Cohesion: 0.11
Nodes (20): expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, (matched phrase words, its Nepali terms) for each glossary phrase in `text`,…, size(), S13: prompt-injection guard for user-supplied text going into an LLM prompt.… (+12 more)

### Community 76 - "check"
Cohesion: 0.13
Nodes (24): check(), get_entry(), _legacy_note(), ne_digits(), NotComputable, period_text(), ValueError, Human wording of a period in both languages ("6 months" / "६ महिना"). (+16 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.12
Nodes (21): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), draft_document() (+13 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (33): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+25 more)

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
Cohesion: 0.10
Nodes (16): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+8 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.13
Nodes (36): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+28 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (124): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+116 more)

### Community 87 - "get_index"
Cohesion: 0.15
Nodes (27): parse_json(), get_index(), detect_language(), ask(), main(), Retrieval metrics through the DEPLOYED pipeline (LLM query rewrite included).…, cmd_e2e(), cmd_retrieval() (+19 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.13
Nodes (22): _coerce(), Coerce a model-returned value to the fact's declared type, or None., Model JSON -> {fact: {"value": typed value | None, "clause_id": str | None}}.…, validate_extraction(), _ascii(), Clause, clause_by_id(), _clause_start() (+14 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "dsl.py"
Cohesion: 0.12
Nodes (31): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+23 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (31): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+23 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "test_drafting.py"
Cohesion: 0.14
Nodes (12): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_missing_required_field_raises() (+4 more)

### Community 95 - "ai_fill.py"
Cohesion: 0.23
Nodes (10): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+2 more)

### Community 96 - "run_audit"
Cohesion: 0.10
Nodes (24): Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), get_checklist(), The type's checklist with only verified checks, each carrying…, Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, requires_corpus, A model that tries to declare things legal (extra keys, verdicts) has no… (+16 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (44): addToCalendar(), frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp() (+36 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.15
Nodes (17): _answer_cache_key(), _cache_key(), cache_get(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Validate a Supabase access token (from the frontend's Authorization header) and… (+9 more)

### Community 99 - "_View"
Cohesion: 0.15
Nodes (15): clause_context(), (tokens of the clause up to the end of the quote, tokens of the clause after…, Polisher, _qtokens(), quote_in_source(), Quote tokens: NFC, PUA glyphs and punctuation/danda gone, digits ASCII,…, One source prepared for span matching., None if the quote is a verbatim span of the source, else a reason code. (+7 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.05
Nodes (36): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+28 more)

### Community 101 - "IncrementalDoc"
Cohesion: 0.15
Nodes (11): _Frame, IncrementalDoc, Truly incremental reader of the growing answer JSON: feed() consumes only the…, parametrize, _sentences_of(), split_random(), test_incremental_parser_cut_off_mid_sentence_and_prose_prefix(), test_incremental_parser_devanagari_and_escaped_quotes() (+3 more)

### Community 102 - "docx_out.py"
Cohesion: 0.10
Nodes (32): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), _add_font_table_fallback() (+24 more)

### Community 103 - "run"
Cohesion: 0.19
Nodes (13): all_company_profiles(), company_profile_get(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent() (+5 more)

### Community 104 - "i18n.ts"
Cohesion: 0.11
Nodes (17): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+9 more)

### Community 105 - "render.py"
Cohesion: 0.09
Nodes (46): build_docx(), TemplateSpec, Inline emphasis inside a paragraph: **bold** and __underline__ (e.g. the bold…, [(segment, bold, underline), ...]; markers toggle the style and are dropped., split_inline(), strip_inline(), build_html(), build_pdf() (+38 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.12
Nodes (24): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+16 more)

### Community 107 - "verifier.py"
Cohesion: 0.09
Nodes (44): _bridge(), check_sentence(), check_structured_sentence(), _cite_conflicts(), _cite_list(), _clean_doc_sentence(), _guidance_ok(), _in_terms() (+36 more)

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.09
Nodes (28): extract_pdf(), main(), Download the official PDFs that carry prescribed forms (schedules) and dump…, slug(), build_parser(), cmd_crawl(), cmd_ocr(), cmd_stats() (+20 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "test_v3_structured.py"
Cohesion: 0.15
Nodes (29): check(), parametrize, V3: generate-then-verify. The model's JSON answer is checked sentence by…, S(), test_altered_quote_is_removed(), test_answer_review_rows_and_aggregate(), test_bad_citation_number_is_removed(), test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook() (+21 more)

### Community 112 - "topical_fit_calibration.py"
Cohesion: 0.19
Nodes (20): auc(), build_features(), choose_threshold(), evaluate(), _fam_source(), fit_variant(), fit_weights(), loao_cv_logloss() (+12 more)

### Community 113 - "test_v32_claim_checks.py"
Cohesion: 0.08
Nodes (53): guidance_term_set(), ctx_of(), _ctx_reason(), judge(), labelled(), parametrize, V3.2: deterministic claim checks, built from the V3 live review (2026-09-30).…, (kept?, reason) of one sentence through verify_sentence exactly as the pipeline… (+45 more)

### Community 114 - "_date"
Cohesion: 0.08
Nodes (27): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+19 more)

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.16
Nodes (18): clean_document(), clean_page(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), _latin_dominant(), normalise_digits() (+10 more)

### Community 117 - "main.py"
Cohesion: 0.14
Nodes (15): _GZipExceptStreams, health(), lifespan(), Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies(), root(), _security_headers() (+7 more)

### Community 118 - "test_v31_streaming.py"
Cohesion: 0.14
Nodes (30): fake_stream(), gen(), V3.1: progressive streaming with per-sentence verification. The provider stream…, Simulated provider at 40 ms per ~3-char token: time to first verified text vs…, What the frontend ends up showing: deltas append, `replace` swaps., run_events(), test_cache_hit_still_has_no_streaming_events(), test_cut_off_stream_shows_only_complete_sentences() (+22 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.11
Nodes (27): _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _playbook_vetoes(), _positions(), Pattern (+19 more)

### Community 120 - "test_v33_topical_fit.py"
Cohesion: 0.15
Nodes (13): orphan_opener(), anaphor" when the sentence opens with a demonstrative / connective that points…, Family ids the passage belongs to although neither the question nor the matched…, specialist_hits(), V3.3: the topical-fit gate, the abstain / topical-extractive replies and the…, spec_hits(), test_a_question_that_mentions_the_regime_is_not_flagged(), test_held_out_markers_catch_most_review2_wrong_law_without_review2_families() (+5 more)

### Community 121 - "scrape_regulators.py"
Cohesion: 0.20
Nodes (14): download(), fiscal_year_bs(), giwms_files(), _is_doc_url(), _links(), _now(), Scrapes primary regulatory texts (acts, regulations, directives, circulars)…, Download doc['url'] into the store (skipped when already present) and record… (+6 more)

### Community 122 - "pytest"
Cohesion: 0.17
Nodes (6): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources(), pytest

### Community 123 - "test_eval_sets.py"
Cohesion: 0.18
Nodes (4): _lines(), _norm(), V1: the real-world and held-out eval sets, the `--set` flag of…, test_heldout_is_disjoint_and_marked_do_not_tune()

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.09
Nodes (18): paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, S13: plan-based tier routing and token-cost accounting. STRATEGY.md §2's…, `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).…, select_tier(), _FakeAnthropicClient, _FakeMessage, _FakeTextBlock (+10 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "Dense"
Cohesion: 0.16
Nodes (8): Dense, Encoder, ndarray, L2-normalised float32 embeddings, shape (len(texts), DIM). Batches are length-…, int8 vectors aligned to an Index's row order. `have[i]` is False for rows with…, (n_passages, n_queries) cosine similarities; -1 where a passage has no vector., Query encoder + vector store for one Index., VectorStore

### Community 127 - "parse_answer"
Cohesion: 0.18
Nodes (12): _norm_doc(), _norm_sentence(), _objects_from(), parse_answer(), Complete {...} objects of the array whose items start at `pos`; whether the…, Every complete block, and every complete sentence of the block that was cut off., (doc, complete). complete=False when the object was cut off or broken and only…, _salvage() (+4 more)

### Community 128 - "ingest_scraped.py"
Cohesion: 0.17
Nodes (20): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+12 more)

### Community 129 - "search"
Cohesion: 0.10
Nodes (20): search(), main(), E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,… (+12 more)

### Community 130 - "verify_sentence"
Cohesion: 0.20
Nodes (16): Remove a leading "But/And/तर/र" that joined the sentence to one that was…, strip_leading_conjunction(), make_views(), One sentence through the same checks verify_structured applies: (kept sentence,…, verify_sentence(), _flagged(), src_of(), test_abstain_reply_in_nepali_and_english_lists_possibly_related_and_the_plan() (+8 more)

### Community 131 - "audit_document"
Cohesion: 0.17
Nodes (16): S13: writes one llm_usage row per real (non-cached, non-free-tier) generation,…, _record_llm_usage_sync(), audit_document(), _error(), HTTPException, UploadFile, Bounded chunked read (see routes/chat.py:upload_matter_file): an oversized…, Signed-in only. Metered against the caller's plan-based daily quota exactly… (+8 more)

### Community 133 - "Layout"
Cohesion: 0.14
Nodes (17): Layout, leading_scope_problem(), _locate(), quote_section(), quote_subsection(), Section/rule numbers a sentence names as ITS provision (not sub-section /…, A passage split (a) at section headings ("२३. विवरण सच्याउने :") and (b) at…, The heading number the quote sits under, when the passage holds several… (+9 more)

### Community 134 - "Scorer"
Cohesion: 0.19
Nodes (11): _cterms(), _head_string(), heading_of(), _in(), _is_precedent(), (law title, section heading) of a passage without the parenthetical law name…, Features (and the score) of the candidate passages for ONE question.…, d_head, d_head_rel, d_pass_rel per candidate (NaN when the passage has no… (+3 more)

### Community 135 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 136 - "filter_gaps"
Cohesion: 0.16
Nodes (15): _dev_share(), filter_gaps(), gap_in_language(), invented_subject(), (kept gaps, [(dropped gap, reason)]). Cited passages are tested first, then…, A proper noun / brand the PERSON typed (eSewa, Khalti, a company) that the…, _clean_side_text(), _passage_text() (+7 more)

### Community 137 - "Client"
Cohesion: 0.15
Nodes (13): Client, _first_reachable(), _giwms_site(), Fetch a page/file if robots allows. Returns response (any status < 500) or None., Fetch a page; `patient` re-tries a few times after a pause, for listing pages…, Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher., Discover legal-text categories from a GIWMS site's home page and crawl them., One rate-limited request with retry on 5xx/network errors. Returns the… (+5 more)

### Community 138 - "build"
Cohesion: 0.11
Nodes (19): asks_quantity(), build(), _log_fallback(), Markdown in the shape the UI already shows: bold headings, bullets, inline [n]., Why an answer fell back to the extractive provisions: structure counts only (no…, The model's raw reply -> {"answer": markdown | None, "verification": report,…, _recount(), render() (+11 more)

### Community 139 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 140 - "load_dense"
Cohesion: 0.18
Nodes (13): _download(), enabled(), load_dense(), model_ready(), prepare_model(), Path, Vectors for `ids` (the loaded corpus's passage ids, in row order), or None when…, Best-effort: a Dense for this corpus, or None (BM25-only). Never raises. (+5 more)

### Community 141 - "StreamVerifier"
Cohesion: 0.20
Nodes (9): clean_ocr_text(), dedupe_marks(), OCR glitches the model copied from a scanned source into its own sentence: a…, [5][5] -> [5]; order kept., _line(), Verify each sentence the moment it is complete and produce the markdown pieces…, New model text in; the text now safe to show (possibly ""), out., StreamVerifier (+1 more)

### Community 142 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), Pattern, A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale()

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 144 - "fit_reply.py"
Cohesion: 0.22
Nodes (13): abstain_answer(), _cite(), _excerpt(), extractive_answer(), gate_ran(), on_topic_laws(), V3.3: what the user sees when the topical-fit gate leaves too little to answer…, (number, source) of the closest statute passages the gate did not rule out by… (+5 more)

### Community 145 - "make_profile"
Cohesion: 0.18
Nodes (13): judge(), make_profile(), `queries`: weighted (text, weight) list as generation.build_queries makes it…, Off-topic logit (higher = more likely off topic)., A verdict per candidate. A passage fails when a specialist regime the question…, score(), _variant(), Verdict (+5 more)

### Community 146 - "compliance/page.tsx"
Cohesion: 0.15
Nodes (16): RFC-5545, daysLabel(), ENTITY_TYPES, WINDOWS, CompanyProfile, EntityType, getCompanyProfile(), ObligationDue (+8 more)

### Community 147 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

### Community 148 - "authority"
Cohesion: 0.18
Nodes (11): authority(), _clean(), giwms_table(), nia_rows(), Rows of a GIWMS table listing: | # | title | published | pdf link | ... |, (title, ISO date, pdf url) rows of one NIA /law/ page. Only the main table is…, Nepal Insurance Authority (nia.gov.np; formerly Beema Samiti). Its HTTPS…, Nepal Gazette (rajpatra.dop.gov.np). Not reachable from the build sandbox; the… (+3 more)

### Community 149 - "Done"
Cohesion: 0.22
Nodes (9): Done, S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S9 — Drafting engine (2026-09-28), V1 baselines (2026-09-30), V2 exit — live held-out measurement (2026-09-30), V3 live review (2026-09-30), V-batch 1 — trust engine, full UI, Document AI (2026-09-29), V-batch 2 — regulator corpus, official drafting formats, tools, prod fixes (2026-09-29) (+1 more)

### Community 150 - "match"
Cohesion: 0.22
Nodes (9): match(), The word itself, then with a glued Nepali postposition (-le/-ko/-lai/-ma ...)…, Lexicon entries hit by the Latin-script words of `text`, in order of appearance…, _stem_variants(), strong_count(), S7: non-LLM playbook matcher - keyword/glossary routing, no embeddings.…, test_matcher_precision_at_least_90_percent(), test_matcher_returns_none_for_empty_query() (+1 more)

### Community 151 - "situation_guards.py"
Cohesion: 0.25
Nodes (8): Guard, Pattern, _r(), V3.2: a small DATA table of wrong-law guards - (what the user's question says…, The id of the guard that forbids citing `source` for this question, else None., _section_no(), violation(), _guard_hit()

### Community 153 - "parse_verdicts"
Cohesion: 0.25
Nodes (6): parse_verdicts(), One verdict (yes/no/partial) per item from {"v":["y",...]} or the older…, _doc_with(), test_entailment_is_one_call_sees_the_question_and_partial_is_configurable(), test_entailment_payload_carries_the_user_situation_once_and_is_compact(), test_entailment_reads_both_formats_and_fails_open()

### Community 154 - ".search"
Cohesion: 0.33
Nodes (4): ndarray, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, Adds each eligible query's dense (cosine) ranking to `fused` in place, by…, _title_tokens()

### Community 155 - "alignment_ok"
Cohesion: 0.29
Nodes (8): alignment_ok(), _lev(), near_variant(), Same word up to a character slip (matra/spelling/OCR): edit distance 1, or 2…, Every token of the quote is in the passage window, or is a near variant of the…, _fuzzy_span(), >=90% of the quote's tokens found in one contiguous run of the source; every…, test_fused_or_split_words_are_line_break_noise_not_substitution()

### Community 156 - "newest_per_series"
Cohesion: 0.20
Nodes (11): _ad_date(), newest_per_series(), _nrb_listing_pages(), pub_sort_key(), Title with amendment parentheticals, digits and punctuation removed, so 'X ऐन,…, Comparable (year, month, day) for an AD ('July 22, 2025', '2025-07-22') or BS…, Keep the newest document of each title series (dated docs win; ties keep the…, Yield (href, title, date_str) over a paginated NRB category listing. (+3 more)

### Community 158 - "Store"
Cohesion: 0.24
Nodes (6): cmd_stats(), main(), sources/regulators/<authority>/{files/,manifest.jsonl}, Rewrite the manifest keeping only the latest record per URL., run_authority(), Store

### Community 159 - "number_role_conflict"
Cohesion: 0.50
Nodes (4): number_role_conflict(), A reason code when a number of the sentence is bound to a unit/head noun the…, test_number_role_property_same_pair_passes_other_value_same_unit_fails(), test_number_with_unit_swapped_is_refused_and_unbound_numbers_are_not_judged()

### Community 161 - "scrape_lawcommission_gap"
Cohesion: 0.27
Nodes (10): existing_corpus_titles(), in_corpus(), Spelling/digit-insensitive identity of a law title (years are part of the…, title_key -> doc_title_ne for every law document in the pre-existing corpus…, True when a law of this title (same year, near-identical spelling:…, Compare the Law Commission's current-acts index (alphabetical index page: ~350…, scrape_lawcommission_gap(), fresh() (+2 more)

### Community 162 - "quantize"
Cohesion: 0.31
Nodes (9): quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., save_vectors(), test_quantize_roundtrip_keeps_cosine(), test_store_digest_mismatch_reuses_surviving_ids(), test_store_exact_match(), test_store_same_ids_other_digest_is_used_but_flagged(), _vectors() (+1 more)

### Community 163 - "draft_update"
Cohesion: 0.28
Nodes (9): draft_create(), draft_get(), draft_list(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft… (+1 more)

### Community 164 - "FakeDense"
Cohesion: 0.25
Nodes (5): FakeDense, attach(), idx(), fixture, Stands in for dense.Dense: `wanted` maps query text -> {passage id: cosine};…

### Community 165 - "entailment_filter"
Cohesion: 0.29
Nodes (6): entailment_filter(), ONE cheap call over every cited sentence: drop those whose quote does NOT…, test_build_runs_entailment_only_when_given_and_recounts(), test_entailment_fails_open(), boom(), test_entailment_removes_no_and_keeps_yes_and_partial()

### Community 166 - "_lookup"
Cohesion: 0.43
Nodes (7): canon(), _lookup(), loose(), Spelling-tolerant form of a roman word: sh->s, w/v->b, z->j, ph/f->p,…, Even looser: chh==ch and trailing vowels dropped (dharauti/dharauta). Used only…, Entries for a word sequence. A literal spelling always matches. Fuzzy matching…, _tables()

### Community 167 - "S13 — AI gateway v2 (2026-09-29)"
Cohesion: 0.40
Nodes (6): looks_like_injection(), free(), parametrize, test_looks_like_injection_does_not_flag_ordinary_legal_questions(), test_looks_like_injection_flags_common_patterns(), S13 — AI gateway v2 (2026-09-29)

### Community 168 - "load_model"
Cohesion: 0.33
Nodes (5): load_model(), Profile, Everything the gate needs to know about one question., The fitted gate (data/topical_fit.json); a missing/broken file disables the…, test_model_file_is_fitted_and_sane()

### Community 169 - "cache_put"
Cohesion: 0.40
Nodes (5): cache_put(), jsonb_safe(), Postgres jsonb rejects the NUL character (\\u0000), which some scanned law…, saved_research_create(), test_answer_cache_strips_nul_characters_postgres_jsonb_rejects()

### Community 170 - "giwms_listing"
Cohesion: 0.40
Nodes (5): bs_key(), giwms_listing(), १३ असोज, २०८३' or '2083-06-13' -> (2083, 6, 13) for ordering; None if…, Iterate a GIWMS category listing (?page=N). Only the main list is read (not the…, scrape_ocr()

### Community 171 - "test_chat_route_anonymous_caller_stays_on_free_tier"
Cohesion: 0.40
Nodes (4): The core S13 wiring bug surface: a paid-plan user's /api/chat call must route…, test_chat_route_anonymous_caller_stays_on_free_tier(), test_chat_route_selects_tier_from_plan(), fake_answer_question()

### Community 172 - "tidy_answer"
Cohesion: 0.50
Nodes (4): Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer(), test_dhara_becomes_dafa_for_statutes_only(), test_trailing_empty_heading_is_removed()

### Community 173 - "_temporal_status"
Cohesion: 0.67
Nodes (4): _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status(), test_old_ordinances_are_lapsed_and_recent_ones_temporary()

### Community 174 - "_is_regulator_query"
Cohesion: 0.67
Nodes (3): _is_regulator_query(), test_regulator_directives_only_surface_for_banking_securities_company_questions(), test_regulator_cues_cover_english_romanised_and_devanagari()

## Knowledge Gaps
- **306 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+301 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1233 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `generation.py`, `ui.tsx`, `cache_put`, `Done`, `get_index`, `chat`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `search`, `test_translit.py`, `test_v1_trust_engine.py`, `test_v25_routing.py`, `Index`, `retrieval.py`, `generation.py`, `load_model`, `chat`, `checklists.py`, `chat.py`, `limitation.py`, `re`, `test_documents_audit.py`, `S5 — Supabase auth + DB (2026-09-26)`, `scrape_lawcommission.py`, `topical_fit_calibration.py`, `main.py`, `test_eval_sets.py`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _306 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `claim_checks.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06823529411764706 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06845513413506013 - nodes in this community are weakly interconnected._