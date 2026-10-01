# Graph Report - LegalNeps  (2026-10-01)

## Corpus Check
- 239 files · ~700,582 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: .jsonl 16, (none) 6, .css 5)

## Summary
- 3827 nodes · 9198 edges · 184 communities (161 shown, 23 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 360 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `930f6de6`
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
- respell_devanagari
- extract_laws.py
- supa.py
- test_v25_routing.py
- Graphify Tool Documentation
- package.json
- test_calculators_tools.py
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
- app/__init__.py
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
- parametrize
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
- _View
- chat
- checklists.py
- limitation.py
- ocr_regulators.py
- forms_common.py
- chat.py
- condition_checks.py
- documents.py
- useLang
- ui.tsx
- test_translit.py
- ingest_regulators.py
- tiers.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- fill_paid
- test_ocr_clean.py
- _bad_input
- test_documents_audit.py
- search/page.tsx
- ics.ts
- test_api.py
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
- test_v27_fit.py
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- _require_matter
- Per-playbook findings
- IncrementalDoc
- docx_out.py
- embedding_benchmark.py
- LangContext.tsx
- render.py
- build_corpus.py
- verifier.py
- scrape_lawcommission.py
- nepali.py
- report.py
- test_v3_structured.py
- authority
- test_v32_claim_checks.py
- test_s12_compliance_radar.py
- scripts
- ocr_clean.py
- newest_per_series
- test_v31_streaming.py
- playbook_matcher.py
- config.py
- scrape_regulators.py
- test_s11_matters.py
- re
- test_s13_ai_gateway.py
- Env
- retrieval.py
- parse_answer
- ingest_scraped.py
- Done
- test_v33_topical_fit.py
- get_index
- calendar
- verify_structured
- topical_fit.py
- matter_file_create
- section_routes.py
- Client
- build
- Store
- scrape_lawcommission_gap
- generation.py
- playbooks.py
- Run the API in Docker (no cloud payment needed)
- smoke.spec.ts
- main.py
- normalise_text
- Dense
- @playwright/test
- mark_stale_precedents
- devDependencies
- CheckContext
- _SSE
- giwms_listing
- .search
- make_profile
- dependencies
- pipeline
- load_dense
- match_playbooks
- run
- ._lexical
- Playbook audit - the 25 curated action plans
- preeti.ts
- ai_fill.py
- match
- test_answer_review_rows_and_aggregate
- contract_fixtures.py
- S13 — AI gateway v2 (2026-09-29)
- .section
- quantize
- ._build_aux
- page_verdict
- direct_fit
- FakeDense
- laws
- 6. Session plan (1 session = 1 milestone = 1 commit/PR)
- cache_put
- _ocr_page
- test_chat_route_anonymous_caller_stays_on_free_tier
- _LRU
- update_manifest
- is_table_noise
- chunks

## God Nodes (most connected - your core abstractions)
1. `get_index()` - 83 edges
2. `get()` - 61 edges
3. `available()` - 47 edges
4. `tokenize()` - 47 edges
5. `run()` - 43 edges
6. `useLang()` - 43 edges
7. `_http()` - 42 edges
8. `useTools()` - 41 edges
9. `S()` - 40 edges
10. `analyze_query()` - 38 edges

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
- 3-file cycle: `backend/app/claim_checks.py -> backend/app/verifier.py -> backend/app/condition_checks.py -> backend/app/claim_checks.py`

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (184 total, 23 thin omitted)

### Community 0 - "claim_checks.py"
Cohesion: 0.06
Nodes (49): alignment_ok(), asks_quantity(), dangling_additive(), _dev_share(), filter_gaps(), _fmt(), gap_in_language(), gap_is_false() (+41 more)

### Community 1 - "api.ts"
Cohesion: 0.06
Nodes (51): ActionPlanPage(), Bi(), ProvisionCard(), adToBs(), Amendment, ApiError, AppealFeeResult, Bilingual (+43 more)

### Community 2 - "translit.py"
Cohesion: 0.15
Nodes (21): canon(), Entry, expand_ne(), _key_in(), _lookup(), loose(), match_ne(), _ne_slots() (+13 more)

### Community 3 - "cite"
Cohesion: 0.07
Nodes (37): markers_table(), Age calculator for majority and consent-age questions. Age is counted on the…, flat_fee_types(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%…, review_fee(), settlement_fee() (+29 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.07
Nodes (48): _is_regulator_query(), Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, search(), tidy_answer(), _reset_cache_for_tests(), _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status() (+40 more)

### Community 5 - "llm.py"
Cohesion: 0.06
Nodes (65): _anthropic_complete(), _call_limit(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini() (+57 more)

### Community 6 - "test_dense.py"
Cohesion: 0.18
Nodes (15): hybrid(), Dense retrieval: vector store (digest mismatch, missing file, id alignment),…, Attach a fake dense, restore afterwards., test_agreement_beats_either_signal_alone(), test_bills_never_surface_by_default_even_if_dense_top(), test_category_filter_after_fusion(), test_dense_finds_what_bm25_cannot(), test_dense_weight_shifts_the_order() (+7 more)

### Community 7 - "respell_devanagari"
Cohesion: 0.29
Nodes (7): normalize_citations(), `text` with known Devanagari spelling slips corrected (unchanged when nothing…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, respell_devanagari(), fix(), known(), test_text_citations_are_mapped_to_numbered_sources()

### Community 8 - "extract_laws.py"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.15
Nodes (37): available(), draft_create(), draft_get(), draft_list(), draft_update(), _draft_version_insert(), draft_versions_list(), _http() (+29 more)

### Community 10 - "test_v25_routing.py"
Cohesion: 0.09
Nodes (43): _is_bank_query(), _match_playbook(), _nrb_directive_hits(), pinned_provisions(), _playbook_id_for(), _playbook_pick(), playbook_support(), A retail-banking question (see _BANK_ACTOR/_BANK_SERVICE): NRB directives are… (+35 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "package.json"
Cohesion: 0.22
Nodes (8): name, private, version, react-dom, @types/node, @types/react, @types/react-dom, typescript

### Community 13 - "test_calculators_tools.py"
Cohesion: 0.09
Nodes (48): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, flat_fee(), The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., check(), get_entry(), Deadline + days remaining for `claim_type`, whose limitation clock started on…, income_tax() (+40 more)

### Community 14 - "Index"
Cohesion: 0.10
Nodes (14): Index, _index_text(), _prior(), Authority of the source x usefulness of this particular passage., Load the query encoder + corpus vectors if available (best-effort, never…, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, client() (+6 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "get"
Cohesion: 0.09
Nodes (58): limitation_claim_types(), _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add() (+50 more)

### Community 17 - "tokenize"
Cohesion: 0.12
Nodes (24): law_topic_terms(), Stemmed section titles of the retrieved STATUTES ("बेइज्जती गर्न नहुने",…, focus(), The part of a passage that matters for this question: the heading line plus the…, fold(), _glossary_roman(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Words of the glossary's romanised-Nepali phrases (data/glossary.json "roman"… (+16 more)

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
Cohesion: 0.08
Nodes (42): appeal_fee(), court_fee(), estimate(), estimate_appeal(), The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its…, bs_to_ad() (+34 more)

### Community 24 - "app/__init__.py"
Cohesion: 0.07
Nodes (38): argparse, entail_payload(), _objects_from(), V3: generate-then-verify answers. The model returns ONE JSON object (blocks of…, Complete {...} objects of the array whose items start at `pos`; whether the…, Every complete block, and every complete sentence of the block that was cut off., (compact JSON for the entailment call, [(block, sentence) per item]). One item…, The answer system prompt for a reply language: rules + the one worked example… (+30 more)

### Community 25 - "audit.py"
Cohesion: 0.11
Nodes (22): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+14 more)

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
Cohesion: 0.09
Nodes (42): ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference(), bs_to_iso(), BsDiff (+34 more)

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
Nodes (46): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message can be searched well WITHOUT an LLM rewriting it.…, The one rule for "answer this question without the query-rewrite call" - shared… (+38 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "parametrize"
Cohesion: 0.07
Nodes (40): bs_month_length(), Number of days in a BS month (29-32; varies by year)., check_hours(), festival_allowance(), fund_contributions(), leave_accrual(), leave_encashment(), _money() (+32 more)

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

### Community 60 - "_View"
Cohesion: 0.07
Nodes (37): clause_context(), Layout, leading_scope_problem(), _locate(), quote_section(), quote_subsection(), Section/rule numbers a sentence names as ITS provision (not sub-section /…, A passage split (a) at section headings ("२३. विवरण सच्याउने :") and (b) at… (+29 more)

### Community 61 - "chat"
Cohesion: 0.10
Nodes (26): chat(), chat_stream(), events(), _client_ip(), create_draft(), _current_user(), draft_document(), _enforce_limits() (+18 more)

### Community 62 - "checklists.py"
Cohesion: 0.12
Nodes (25): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+17 more)

### Community 63 - "limitation.py"
Cohesion: 0.09
Nodes (36): _by_id(), catalog(), entry_view(), general_rules(), is_computable(), _legacy_note(), list_claim_types(), ne_digits() (+28 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.12
Nodes (25): all_ocr_records(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages(), main() (+17 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "chat.py"
Cohesion: 0.06
Nodes (77): corpus_stats(), create_matter(), create_matter_note(), get_company_profile(), get_draft(), get_drafting_template(), get_playbook(), law_doc() (+69 more)

### Community 67 - "condition_checks.py"
Cohesion: 0.11
Nodes (29): _clean(), document_requirement(), _folded(), forum_classes(), forum_not_in_sources(), _qtok(), A sentence that says which document a filing needs (as opposed to "keep your…, An uncited sentence that names an office/forum or a filing document that the… (+21 more)

### Community 68 - "documents.py"
Cohesion: 0.11
Nodes (27): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+19 more)

### Community 69 - "useLang"
Cohesion: 0.09
Nodes (60): Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), ProfileForm(), submit(), WINDOWS (+52 more)

### Community 70 - "ui.tsx"
Cohesion: 0.15
Nodes (23): Account(), AccountPage(), AuthWidget(), handleSendCode(), handleVerify(), isActive(), NAV, Shell() (+15 more)

### Community 71 - "test_translit.py"
Cohesion: 0.15
Nodes (14): expand(), Devanagari statute terms for the roman/English words in `text` (deduplicated,…, index(), fixture, parametrize, V2: the romanised-Nepali -> statute-Nepali lexicon (app/translit.py). The…, The validation that keeps the lexicon honest: after the same tokenisation the…, test_chh_ch_variants_tolerated_but_theft_is_not_daughter() (+6 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.11
Nodes (27): assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), english_title(), ensure_glyph_reference() (+19 more)

### Community 73 - "tiers.py"
Cohesion: 0.27
Nodes (9): daily_quota_for(), estimate_cost_usd(), model_for_tier(), S13: plan-based tier routing and token-cost accounting. STRATEGY.md §2's…, test_audit_happy_path_on_the_free_plan_uses_the_free_chain(), test_paid_plan_routes_to_sonnet_and_logs_llm_usage(), test_daily_quota_for_matches_plan_table(), test_estimate_cost_usd_matches_known_pricing() (+1 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.13
Nodes (14): 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500), 3.4 Legal/business prerequisites (founder to-do, confirm with your advocate), 3. Who pays, and for what, 4.1 Must-have for commercial launch, 4.2 Growth (post-launch) (+6 more)

### Community 75 - "glossary.py"
Cohesion: 0.26
Nodes (11): _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes… (+3 more)

### Community 76 - "fill_paid"
Cohesion: 0.22
Nodes (8): fill_paid(), S13: same expansion, billed to a specific paid-tier model…, paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, test_fill_paid_propagates_unknown_field(), test_fill_paid_wraps_hint_and_uses_the_tiered_model(), test_paid_complete_calls_the_named_model_and_returns_usage(), test_paid_complete_without_api_key_raises()

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.17
Nodes (16): ad_to_bs(), ai_fill_field(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation() (+8 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.08
Nodes (38): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+30 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "ics.ts"
Cohesion: 0.29
Nodes (9): RFC-5545, buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay(), stamp() (+1 more)

### Community 82 - "test_api.py"
Cohesion: 0.06
Nodes (9): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), test_research_save_list_delete_roundtrip(), test_cache_roundtrip(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours() (+1 more)

### Community 83 - "test_s14_security.py"
Cohesion: 0.10
Nodes (16): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+8 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.12
Nodes (38): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+30 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (113): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+105 more)

### Community 87 - "run_eval.py"
Cohesion: 0.13
Nodes (28): answer_question(), parse_json(), detect_language(), ask(), main(), cmd_e2e(), cmd_retrieval(), cmd_synth() (+20 more)

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
Cohesion: 0.14
Nodes (29): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+21 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (31): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+23 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "test_drafting.py"
Cohesion: 0.14
Nodes (13): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_list_templates_matches_registry() (+5 more)

### Community 95 - "test_v27_fit.py"
Cohesion: 0.12
Nodes (29): abstain_answer(), _cite(), _excerpt(), extractive_answer(), gate_ran(), V3.3: what the user sees when the topical-fit gate leaves too little to answer…, The provisions themselves. With the gate: only passages that passed it (V3.2…, (number, source) of the closest statute passages the gate did not rule out by… (+21 more)

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (44): addToCalendar(), frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp() (+36 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.13
Nodes (20): cache_get(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Validate a Supabase access token (from the frontend's Authorization header) and…, True if this IP is still under its hourly budget (and records the hit)., Atomic check-and-increment via the increment_usage() RPC (avoids a read-then-… (+12 more)

### Community 99 - "_require_matter"
Cohesion: 0.16
Nodes (16): create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task(), delete_research(), download_matter_file() (+8 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.08
Nodes (24): bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared, defamation - Someone defamed me (+16 more)

### Community 101 - "IncrementalDoc"
Cohesion: 0.15
Nodes (11): _Frame, IncrementalDoc, Truly incremental reader of the growing answer JSON: feed() consumes only the…, parametrize, _sentences_of(), split_random(), test_incremental_parser_cut_off_mid_sentence_and_prose_prefix(), test_incremental_parser_devanagari_and_escaped_quotes() (+3 more)

### Community 102 - "docx_out.py"
Cohesion: 0.11
Nodes (36): _add_font_table_fallback(), build_docx(), _get_or_add(), _insert_ordered(), _local(), _page_setup(), _paragraph(), Resolved layout blocks -> a real .docx (python-docx). Page and type set-up… (+28 more)

### Community 103 - "embedding_benchmark.py"
Cohesion: 0.25
Nodes (7): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize()

### Community 104 - "LangContext.tsx"
Cohesion: 0.09
Nodes (25): ActionPlansPage(), AREA_LABEL, frontend_app_globals, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage(), metadata, RootLayout() (+17 more)

### Community 105 - "render.py"
Cohesion: 0.13
Nodes (30): TemplateSpec, strip_inline(), build_pdf(), _build_context(), _effective_language(), get_template(), get_template_detail(), _items() (+22 more)

### Community 106 - "build_corpus.py"
Cohesion: 0.10
Nodes (34): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+26 more)

### Community 107 - "verifier.py"
Cohesion: 0.08
Nodes (48): _bridge(), check_sentence(), check_structured_sentence(), _cite_conflicts(), _cite_list(), _clean_doc_sentence(), _condition_problem(), _guidance_ok() (+40 more)

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.09
Nodes (28): main(), Download the official PDFs that carry prescribed forms (schedules) and dump…, slug(), build_parser(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction() (+20 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "report.py"
Cohesion: 0.19
Nodes (12): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), Document (+4 more)

### Community 111 - "test_v3_structured.py"
Cohesion: 0.13
Nodes (35): check(), parametrize, V3: generate-then-verify. The model's JSON answer is checked sentence by…, _run(), S(), test_altered_quote_is_removed(), test_bad_citation_number_is_removed(), test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook() (+27 more)

### Community 112 - "authority"
Cohesion: 0.18
Nodes (11): authority(), _clean(), giwms_table(), nia_rows(), Rows of a GIWMS table listing: | # | title | published | pdf link | ... |, (title, ISO date, pdf url) rows of one NIA /law/ page. Only the main table is…, Nepal Insurance Authority (nia.gov.np; formerly Beema Samiti). Its HTTPS…, Nepal Gazette (rajpatra.dop.gov.np). Not reachable from the build sandbox; the… (+3 more)

### Community 113 - "test_v32_claim_checks.py"
Cohesion: 0.05
Nodes (65): clean_ocr_text(), dedupe_marks(), Remove a leading "But/And/तर/र" that joined the sentence to one that was…, OCR glitches the model copied from a scanned source into its own sentence: a…, [5][5] -> [5]; order kept., strip_leading_conjunction(), _line(), parse_verdicts() (+57 more)

### Community 114 - "test_s12_compliance_radar.py"
Cohesion: 0.07
Nodes (23): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+15 more)

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.16
Nodes (18): clean_document(), clean_page(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), _latin_dominant(), normalise_digits() (+10 more)

### Community 117 - "newest_per_series"
Cohesion: 0.20
Nodes (11): _ad_date(), newest_per_series(), _nrb_listing_pages(), pub_sort_key(), Title with amendment parentheticals, digits and punctuation removed, so 'X ऐन,…, Comparable (year, month, day) for an AD ('July 22, 2025', '2025-07-22') or BS…, Keep the newest document of each title series (dated docs win; ties keep the…, Yield (href, title, date_str) over a paginated NRB category listing. (+3 more)

### Community 118 - "test_v31_streaming.py"
Cohesion: 0.14
Nodes (29): fake_stream(), gen(), V3.1: progressive streaming with per-sentence verification. The provider stream…, Simulated provider at 40 ms per ~3-char token: time to first verified text vs…, What the frontend ends up showing: deltas append, `replace` swaps., run_events(), test_cache_hit_still_has_no_streaming_events(), test_cut_off_stream_shows_only_complete_sentences() (+21 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.11
Nodes (28): _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _playbook_vetoes(), _positions(), Pattern (+20 more)

### Community 120 - "config.py"
Cohesion: 0.12
Nodes (19): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, V2.7: how many labelled `supported` sentences does the PASSAGE-level gate (V3.3…, build(), load_sentences(), main(), V2.7: what the NEW sentence checks (dropped-condition checks on the full…, reason_for() (+11 more)

### Community 121 - "scrape_regulators.py"
Cohesion: 0.20
Nodes (14): download(), fiscal_year_bs(), giwms_files(), _is_doc_url(), _links(), _now(), Scrapes primary regulatory texts (acts, regulations, directives, circulars)…, Download doc['url'] into the store (skipped when already present) and record… (+6 more)

### Community 122 - "test_s11_matters.py"
Cohesion: 0.18
Nodes (5): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 123 - "re"
Cohesion: 0.09
Nodes (15): DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl…, Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the…, Return a list of problems ([] = every cited provision found and confirmed)., verify_case(), _lines(), _norm() (+7 more)

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.12
Nodes (12): `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).…, select_tier(), _FakeAnthropicClient, _FakeMessage, _FakeTextBlock, _FakeUsage, gateway_client(), fixture (+4 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "retrieval.py"
Cohesion: 0.09
Nodes (24): array, passage_text(), Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, Document title + section heading + body, Nepali first, English title/heading…, corpus_source(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, build_pool(), embed_pool() (+16 more)

### Community 127 - "parse_answer"
Cohesion: 0.17
Nodes (13): _loose_blocks(), _n_sentences(), _norm_doc(), _norm_sentence(), parse_answer(), Free-tier models sometimes emit JSON-ish text whose structure is broken (keys…, (doc, complete). complete=False when the object was cut off or broken and only…, test_malformed_json_from_a_free_model_keeps_its_intact_cited_sentences() (+5 more)

### Community 128 - "ingest_scraped.py"
Cohesion: 0.17
Nodes (20): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+12 more)

### Community 129 - "Done"
Cohesion: 0.09
Nodes (22): order_for_display(), V2.7 citation labels: statutes that fit directly first, then the other on-topic…, _is_devanagari(), Script check on the message itself. NOT the language hint: the hint is "ne" for…, _is_english(), Latin-script and not romanised Nepali ("mero ghardhani le bhada badhayo")., guess_language(), Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised… (+14 more)

### Community 130 - "test_v33_topical_fit.py"
Cohesion: 0.12
Nodes (27): orphan_opener(), anaphor" when the sentence opens with a demonstrative / connective that points…, Family ids the passage belongs to although neither the question nor the matched…, specialist_hits(), make_views(), One sentence through the same checks verify_structured applies: (kept sentence,…, verify_sentence(), _flagged() (+19 more)

### Community 131 - "get_index"
Cohesion: 0.08
Nodes (29): clear_query_cache(), Load everything and run one query through it (used by…, warm_up(), get_index(), _inactive_regimes(), Regime ids whose cue words the (lower-cased) query text does not contain., Backwards-compatible single-query search., retrieve() (+21 more)

### Community 133 - "verify_structured"
Cohesion: 0.17
Nodes (12): Verify each sentence the moment it is complete and produce the markdown pieces…, New model text in; the text now safe to show (possibly ""), out., Markdown in the shape the UI already shows: bold headings, bullets, inline [n]., render(), StreamVerifier, (verified doc, report). Failing sentences are dropped; blocks left with nothing…, verify_structured(), test_stream_and_final_agree_when_a_heading_repeats() (+4 more)

### Community 134 - "topical_fit.py"
Cohesion: 0.10
Nodes (29): Family, V3.3: a DATA-DRIVEN topical-fit gate. The V3.2 checks prove a quote is real and…, idf of a stem over the BM25 index's passages (document frequency from the CSC…, Off-topic logit (higher = more likely off topic)., score(), _Stats, auc(), choose_threshold() (+21 more)

### Community 135 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 136 - "section_routes.py"
Cohesion: 0.15
Nodes (23): Alt, is_suppressed(), load_routes(), matching_routes(), _normalise(), _present(), V2.7: verified keyword -> SECTION routes. A playbook pins the governing…, (corpus entries of the routed sections, in route order and capped at `limit`,… (+15 more)

### Community 137 - "Client"
Cohesion: 0.15
Nodes (13): Client, _first_reachable(), _giwms_site(), Fetch a page/file if robots allows. Returns response (any status < 500) or None., Fetch a page; `patient` re-tries a few times after a pause, for listing pages…, Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher., Discover legal-text categories from a GIWMS site's home page and crawl them., One rate-limited request with retry on 5xx/network errors. Returns the… (+5 more)

### Community 138 - "build"
Cohesion: 0.09
Nodes (21): build(), _clean_side_text(), entailment_filter(), _log_fallback(), _passage_text(), Gaps and follow-up questions carry no legal claim: keep them short and number-…, ONE cheap call over every cited sentence: drop those whose quote does NOT…, Why an answer fell back to the extractive provisions: structure counts only (no… (+13 more)

### Community 139 - "Store"
Cohesion: 0.24
Nodes (6): cmd_stats(), main(), sources/regulators/<authority>/{files/,manifest.jsonl}, Rewrite the manifest keeping only the latest record per URL., run_authority(), Store

### Community 140 - "scrape_lawcommission_gap"
Cohesion: 0.27
Nodes (10): existing_corpus_titles(), in_corpus(), Spelling/digit-insensitive identity of a law title (years are part of the…, title_key -> doc_title_ne for every law document in the pre-existing corpus…, True when a law of this title (same year, near-identical spelling:…, Compare the Law Commission's current-acts index (alphabetical index page: ~350…, scrape_lawcommission_gap(), fresh() (+2 more)

### Community 141 - "generation.py"
Cohesion: 0.06
Nodes (58): direct_laws(), on_topic_laws(), The corpus files a long section under its FIRST sub-section ("दफा 10 (1)")…, On-topic statute passages that also pass the strict fit check (verified, or the…, relabel_subsections(), _answer_cache_key(), answer_max_tokens(), answer_system() (+50 more)

### Community 142 - "playbooks.py"
Cohesion: 0.14
Nodes (21): all_playbooks_resolved(), _get_playbook_cached(), list_playbooks(), lookup_entry(), _norm(), Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Summary list (no provision resolution - cheap, for GET /api/playbooks)., Every playbook with every provision resolved - raises UnresolvedProvision on… (+13 more)

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 144 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 145 - "main.py"
Cohesion: 0.13
Nodes (16): asyncio, _GZipExceptStreams, health(), lifespan(), Request, gzip buffers a streamed body until it ends, which would defeat…, _reject_oversized_bodies(), root() (+8 more)

### Community 146 - "normalise_text"
Cohesion: 0.13
Nodes (18): normalise_text(), parse_period_phrase(), Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari…, (value, unit) of the number+unit at the start of a phrase like 'छ महिनाभित्र'…, Problems (empty when fine) with one entry's citation and stated period: the…, section_text(), verify_entry() (+10 more)

### Community 147 - "Dense"
Cohesion: 0.16
Nodes (8): Dense, Encoder, ndarray, L2-normalised float32 embeddings, shape (len(texts), DIM). Batches are length-…, int8 vectors aligned to an Index's row order. `have[i]` is False for rows with…, (n_passages, n_queries) cosine similarities; -1 where a passage has no vector., Query encoder + vector store for one Index., VectorStore

### Community 148 - "@playwright/test"
Cohesion: 0.22
Nodes (4): Json, PAIRS, ref_node_fs, @playwright/test

### Community 149 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), Pattern, A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale()

### Community 150 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 151 - "CheckContext"
Cohesion: 0.11
Nodes (23): CheckContext, precedent_problem(), What the checks may know about the request. All optional: with none of it the…, The quote is a holding/rule (must, cannot, entitled...), not just a record of…, Does `text` share a distinctive noun with the user's question? None when the…, states_rule(), topic_overlap(), Guard (+15 more)

### Community 153 - "giwms_listing"
Cohesion: 0.40
Nodes (5): bs_key(), giwms_listing(), १३ असोज, २०८३' or '2083-06-13' -> (2083, 6, 13) for ordering; None if…, Iterate a GIWMS category listing (?page=N). Only the main list is read (not the…, scrape_ocr()

### Community 154 - ".search"
Cohesion: 0.31
Nodes (5): ndarray, Multiplies the fused scores (in place) by (a) a demotion for passages from a…, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, Adds each eligible query's dense (cosine) ranking to `fused` in place, by…, _title_tokens()

### Community 155 - "make_profile"
Cohesion: 0.24
Nodes (16): asks_for_form(), judge(), make_profile(), `queries`: weighted (text, weight) list as generation.build_queries makes it…, Features (and the score) of the candidate passages for ONE question.…, A verdict per candidate. A passage fails when a specialist regime the question…, Scorer, _variant() (+8 more)

### Community 156 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 158 - "load_dense"
Cohesion: 0.18
Nodes (13): _download(), enabled(), load_dense(), model_ready(), prepare_model(), Path, Vectors for `ids` (the loaded corpus's passage ids, in row order), or None when…, Best-effort: a Dense for this corpus, or None (BM25-only). Never raises. (+5 more)

### Community 160 - "run"
Cohesion: 0.19
Nodes (13): all_company_profiles(), company_profile_get(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent() (+5 more)

### Community 161 - "._lexical"
Cohesion: 0.19
Nodes (8): _cterms(), _head_string(), heading_of(), _in(), (law title, section heading) of a passage without the parenthetical law name…, d_head, d_head_rel, d_pass_rel per candidate (NaN when the passage has no…, _same(), unexpl()

### Community 162 - "Playbook audit - the 25 curated action plans"
Cohesion: 0.17
Nodes (11): All NEEDS-ADVOCATE-REVIEW items (64), Existing playbooks changed in V2.5, How to read the per-playbook sections, Method and limits of this audit, New playbooks (all NEEDS-ADVOCATE-REVIEW), Playbook audit - the 25 curated action plans, Result in one paragraph, Summary table (+3 more)

### Community 163 - "preeti.ts"
Cohesion: 0.17
Nodes (9): CHARS, I_MATRA_RE, JOIN_RULES, MATRA_AFTER_HALANT_RE, MATRA_BEFORE_HALANT_RE, NASAL_BEFORE_MATRA_RE, REPH_RE, SEQUENCES (+1 more)

### Community 164 - "ai_fill.py"
Cohesion: 0.25
Nodes (9): _build(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, UnknownField, S13: prompt-injection guard for user-supplied text going into an LLM prompt.…, wrap_user_text() (+1 more)

### Community 165 - "match"
Cohesion: 0.22
Nodes (9): match(), The word itself, then with a glued Nepali postposition (-le/-ko/-lai/-ma ...)…, Lexicon entries hit by the Latin-script words of `text`, in order of appearance…, _stem_variants(), strong_count(), S7: non-LLM playbook matcher - keyword/glossary routing, no embeddings.…, test_matcher_precision_at_least_90_percent(), test_matcher_returns_none_for_empty_query() (+1 more)

### Community 167 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 168 - "S13 — AI gateway v2 (2026-09-29)"
Cohesion: 0.22
Nodes (10): looks_like_injection(), free(), parametrize, test_looks_like_injection_does_not_flag_ordinary_legal_questions(), test_looks_like_injection_flags_common_patterns(), S13 — AI gateway v2 (2026-09-29), 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical) (+2 more)

### Community 169 - ".section"
Cohesion: 0.24
Nodes (6): Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., V2.6 additions (2026-10-01): three new playbooks and changes to existing ones, V2.7 additions (2026-10-01): section routes (not playbooks) and guard rows, S6 — Action Plan engine (2026-09-26)

### Community 170 - "quantize"
Cohesion: 0.31
Nodes (9): quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., save_vectors(), test_quantize_roundtrip_keeps_cosine(), test_store_digest_mismatch_reuses_surviving_ids(), test_store_exact_match(), test_store_same_ids_other_digest_is_used_but_flagged(), _vectors() (+1 more)

### Community 171 - "._build_aux"
Cohesion: 0.25
Nodes (6): _heading(), Path, A passage's own section heading: title_ne without the trailing " (document…, 1-based id of the specialist regime a passage belongs to (0 = general law)., Per-passage heading weights and specialist-regime ids (best-effort, never…, _regime_of()

### Community 172 - "page_verdict"
Cohesion: 0.22
Nodes (8): document_verdict(), page_verdict(), Word-token counts and how many are known words. Nepali tokens are compared…, Vocabulary-free check of Devanagari words: share of words whose combining marks…, (keep, reason, stats) for one cleaned page., Judge every page; a document survives when enough of its words sit on kept…, structural_share(), token_stats()

### Community 173 - "direct_fit"
Cohesion: 0.25
Nodes (7): direct_fit(), _is_precedent(), law_key(), Profile, Everything the gate needs to know about one question., A statute's name without its year or the parenthetical amendment note ("कम्पनी…, V2.7 strict topical fit, stricter than "not ruled out": the passage is verified…

### Community 174 - "FakeDense"
Cohesion: 0.25
Nodes (5): FakeDense, attach(), idx(), fixture, Stands in for dense.Dense: `wanted` maps query text -> {passage id: cosine};…

### Community 175 - "laws"
Cohesion: 0.29
Nodes (7): named_laws(), V2.7: statutes the question's own concepts name: the curated romanised and…, laws(), laws_ne(), Exact corpus titles of the statutes the matched strong entries point to., test_laws_are_reported_for_strong_matches_only(), test_bank_terms_carry_the_bfi_act_as_their_statute()

### Community 176 - "6. Session plan (1 session = 1 milestone = 1 commit/PR)"
Cohesion: 0.29
Nodes (7): 6. Session plan (1 session = 1 milestone = 1 commit/PR), Phase A — Trust engine, Phase B — Surface the product, Phase C — Document AI, Phase D — Commercial, Phase E — Retention + moat, Phase F — Launch

### Community 177 - "cache_put"
Cohesion: 0.40
Nodes (5): cache_put(), jsonb_safe(), Postgres jsonb rejects the NUL character (\\u0000), which some scanned law…, saved_research_create(), test_answer_cache_strips_nul_characters_postgres_jsonb_rejects()

### Community 178 - "_ocr_page"
Cohesion: 0.40
Nodes (5): binarise(), _ocr_page(), Adaptive (local-mean) threshold of a grayscale pixmap -> PNG bytes., Render page `pno` (0-based) of `path` at 300 dpi grayscale and run tesseract., _tesseract()

### Community 179 - "test_chat_route_anonymous_caller_stays_on_free_tier"
Cohesion: 0.40
Nodes (4): The core S13 wiring bug surface: a paid-plan user's /api/chat call must route…, test_chat_route_anonymous_caller_stays_on_free_tier(), test_chat_route_selects_tier_from_plan(), fake_answer_question()

### Community 181 - "update_manifest"
Cohesion: 0.50
Nodes (4): corpus_digest(), Digest exactly as build_corpus.main(): sha256("".join(ids in shard…, Register `shard` (append if new) and recompute digest + counts. `count_keys`…, update_manifest()

### Community 182 - "is_table_noise"
Cohesion: 0.50
Nodes (4): is_table_noise(), numeric_share(), Share of whitespace-separated tokens that are only digits/separators - a…, A chunk that is mostly figures: OCR'd code lists carry no searchable meaning…

### Community 183 - "chunks"
Cohesion: 0.67
Nodes (3): chunks(), Word-boundary chunks of ~`size` chars (newlines kept) for simulated streaming., test_chunks_are_small_lossless_and_never_split_a_citation()

## Knowledge Gaps
- **308 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+303 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1282 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `Done`, `analyze_query`, `get_index`, `ui.tsx`, `generation.py`, `cache_put`, `chat`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `test_v1_trust_engine.py`, `topical_fit.py`, `respell_devanagari`, `section_routes.py`, `test_v25_routing.py`, `generation.py`, `playbooks.py`, `Index`, `main.py`, `normalise_text`, `app/__init__.py`, `analyze_query`, `.section`, `direct_fit`, `chat`, `checklists.py`, `limitation.py`, `chat.py`, `test_translit.py`, `test_documents_audit.py`, `run_eval.py`, `test_v27_fit.py`, `S5 — Supabase auth + DB (2026-09-26)`, `embedding_benchmark.py`, `scrape_lawcommission.py`, `re`, `retrieval.py`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _308 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `claim_checks.py` be split into smaller, more focused modules?**
  _Cohesion score 0.058823529411764705 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.0593990216631726 - nodes in this community are weakly interconnected._