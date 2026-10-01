# Graph Report - LegalNeps  (2026-10-01)

## Corpus Check
- 229 files · ~671,885 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 34 file(s) not represented in the graph (top: .jsonl 14, (none) 6, .css 5)

## Summary
- 3705 nodes · 8823 edges · 164 communities (139 shown, 25 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 352 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9b6bcc00`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- claim_checks.py
- api.ts
- translit.py
- dates.py
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
- bs
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- test_query_understanding.py
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
- playbooks.py
- limitation.py
- ocr_regulators.py
- forms_common.py
- chat.py
- _run
- documents.py
- matters/[id]/page.tsx
- ui.tsx
- match
- ingest_regulators.py
- audit_document
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- ai_fill.py
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
- test_drafting.py
- complete
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- _require_matter
- Per-playbook findings
- test_v31_streaming.py
- docx_out.py
- embedding_benchmark.py
- i18n.ts
- render.py
- extract_doc_meta
- verifier.py
- scrape_lawcommission.py
- nepali.py
- report.py
- test_v3_structured.py
- authority
- test_v32_claim_checks.py
- _date
- scripts
- ocr_clean.py
- newest_per_series
- fake_stream
- playbook_matcher.py
- answer_review.py
- scrape_regulators.py
- test_s11_matters.py
- test_eval_sets.py
- re
- Env
- main
- parse_answer
- ingest_scraped.py
- Done
- test_v33_topical_fit.py
- get_index
- calendar
- _line
- topical_fit.py
- matter_file_create
- filter_gaps
- Client
- entailment_filter
- Store
- scrape_lawcommission_gap
- generation.py
- _generate_verified
- Run the API in Docker (no cloud payment needed)
- smoke.spec.ts
- _targets
- useLang
- _playbook_id_for
- @playwright/test
- mark_stale_precedents
- devDependencies
- situation_guards.py
- _SSE
- giwms_listing
- .search
- alignment_ok
- dependencies
- pipeline
- Handler
- match_playbooks
- test_garbage_is_unparseable_and_repair_gets_one_attempt
- draft_update
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
- `V-batch 1 — trust engine, full UI, Document AI (2026-09-29)` --references--> `search()`  [INFERRED]
  docs/PROGRESS.md → backend/app/generation.py
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `V-batch 2b — OCR of the scanned regulator PDFs + NIA/MoLESS (2026-09-30)` --references--> `nia_rows()`  [INFERRED]
  docs/PROGRESS.md → backend/scripts/scrape_regulators.py
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

## Communities (164 total, 25 thin omitted)

### Community 0 - "claim_checks.py"
Cohesion: 0.05
Nodes (66): clause_context(), _clean(), dangling_additive(), _dev_share(), document_requirement(), _fmt(), _folded(), forum_classes() (+58 more)

### Community 1 - "api.ts"
Cohesion: 0.07
Nodes (43): adToBs(), Amendment, AppealFeeResult, BsDate, bsToAd(), calcGratuity(), calcNotice(), calcSeverance() (+35 more)

### Community 2 - "translit.py"
Cohesion: 0.12
Nodes (25): canon(), Entry, expand_ne(), _key_in(), laws_ne(), _lookup(), loose(), match_ne() (+17 more)

### Community 3 - "dates.py"
Cohesion: 0.18
Nodes (11): Age calculator for majority and consent-age questions. Age is counted on the…, BsDiff, BS <-> AD date conversion and Bikram Sambat date arithmetic (S8). Nepal's…, Calendar difference between two dates, counted on the BS calendar., BS date arithmetic tools: add years/months/days to a date, and the difference…, Interest on private loans under the Muluki Civil Code, 2074, chapter 15 (लेनदेन…, Where every number in a calculator comes from. Each calculator module lists its…, Source (+3 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.07
Nodes (44): _is_regulator_query(), _pipeline_fingerprint(), _reset_cache_for_tests(), _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status(), _expand_multiplier(), _haystack_numbers() (+36 more)

### Community 5 - "llm.py"
Cohesion: 0.16
Nodes (27): _anthropic_complete(), _call_limit(), _client_http(), _cool(), _gemini(), _gemini_cfg(), _gemini_complete(), _gemini_stream() (+19 more)

### Community 6 - "test_dense.py"
Cohesion: 0.06
Nodes (42): Dense, enabled(), load_dense(), ndarray, quantize(), float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale)., int8 vectors aligned to an Index's row order. `have[i]` is False for rows with…, Vectors for `ids` (the loaded corpus's passage ids, in row order), or None when… (+34 more)

### Community 7 - "test_api.py"
Cohesion: 0.09
Nodes (10): focus(), normalize_citations(), The part of a passage that matters for this question: the heading line plus the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, client(), fixture, test_focus_keeps_heading_and_the_matching_clause(), test_research_save_list_delete_roundtrip() (+2 more)

### Community 8 - "extract_laws.py"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "supa.py"
Cohesion: 0.14
Nodes (41): all_company_profiles(), available(), company_profile_get(), company_profile_upsert(), draft_get(), draft_list(), _http(), llm_usage_list() (+33 more)

### Community 10 - "test_v25_routing.py"
Cohesion: 0.11
Nodes (36): _is_bank_query(), _is_fiscal_query(), _match_playbook(), _nrb_directive_hits(), playbook_support(), `text` with known Devanagari spelling slips corrected (unchanged when nothing…, A retail-banking question (see _BANK_ACTOR/_BANK_SERVICE): NRB directives are…, How many of the top `depth` retrieved passages back one of the plan's… (+28 more)

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
Nodes (17): _heading(), Index, Path, A passage's own section heading: title_ne without the trailing " (document…, 1-based id of the specialist regime a passage belongs to (0 = general law)., Per-passage heading weights and specialist-regime ids (best-effort, never…, Load the query encoder + corpus vectors if available (best-effort, never…, All passages (loads everything - for scripts/evals, not requests). (+9 more)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "get"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "tokenize"
Cohesion: 0.14
Nodes (20): law_topic_terms(), _party_generic(), `ctx_tokens`: the quote's clause up to the end of the quote (heading text + the…, A quote that names 'the family/relatives' or the couple covers husband/wife., Stemmed section titles of the retrieved STATUTES ("बेइज्जती गर्न नहुने",…, scope_conflict(), fold(), tokenize() (+12 more)

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
Cohesion: 0.15
Nodes (10): _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip(), test_status_is_never_guessed() (+2 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.06
Nodes (53): appeal_fee(), court_fee(), estimate(), estimate_appeal(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%…, The दफा ६९ अदालती शुल्क for a claim of this disclosed value. (+45 more)

### Community 24 - "retrieval.py"
Cohesion: 0.07
Nodes (45): argparse, array, Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, BM25 search over the government-sourced corpus (laws + precedents). The corpus…, _objects_from(), V3: generate-then-verify answers. The model returns ONE JSON object (blocks of…, Complete {...} objects of the array whose items start at `pos`; whether the…, Every complete block, and every complete sentence of the block that was cut off. (+37 more)

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

### Community 29 - "bs"
Cohesion: 0.07
Nodes (50): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference() (+42 more)

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
Nodes (36): analyze_needs_llm(), confidence(), _is_devanagari(), Script check on the message itself. NOT the language hint: the hint is "ne" for…, How sure we are this message can be searched well WITHOUT an LLM rewriting it.…, The one rule for "answer this question without the query-rewrite call" - shared…, Whether analyze_query() will reach a provider for this message., _skip_llm() (+28 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "test_calculators_tools.py"
Cohesion: 0.05
Nodes (91): markers_table(), flat_fee(), flat_fee_types(), The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., bs_month_length(), Number of days in a BS month (29-32; varies by year)., max_lawful_rate(), Interest on a private loan from `start` to `end`, with the lawful cap applied.… (+83 more)

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
Cohesion: 0.25
Nodes (9): Pin the headline numbers so an edit to the YAML can't drift from the law., test_numeric_rules_match_the_statute_numbers(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus), Next session (+1 more)

### Community 61 - "chat"
Cohesion: 0.15
Nodes (18): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+10 more)

### Community 62 - "playbooks.py"
Cohesion: 0.07
Nodes (47): assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all(), public_listing() (+39 more)

### Community 63 - "limitation.py"
Cohesion: 0.06
Nodes (57): _by_id(), catalog(), check(), entry_view(), general_rules(), get_entry(), is_computable(), _legacy_note() (+49 more)

### Community 64 - "ocr_regulators.py"
Cohesion: 0.10
Nodes (30): all_ocr_records(), binarise(), build_vocabs(), classify_new(), cmd_ingest(), rank(), _existing_docs(), load_raw_pages() (+22 more)

### Community 65 - "forms_common.py"
Cohesion: 0.09
Nodes (41): F(), Compact Field builder; fields on prescribed forms are optional by default…, A select field whose options are Nepali words shown in both languages., SELECT(), Field, court_field(), court_line(), law_url() (+33 more)

### Community 66 - "chat.py"
Cohesion: 0.06
Nodes (83): corpus_stats(), create_draft(), create_matter(), create_matter_note(), get_company_profile(), get_draft(), get_drafting_template(), get_matter() (+75 more)

### Community 67 - "_run"
Cohesion: 0.20
Nodes (10): answer_system(), test_only_the_reply_language_example_is_sent_and_the_rules_are_smaller_than_before(), _run(), test_free_tier_entailment_is_off_by_default_and_env_flag_enables_it_as_one_extra_call(), test_pipeline_version_and_fingerprint_cover_the_new_modules(), test_run_falls_back_to_the_provisions_when_too_little_survives(), test_run_streams_status_then_verified_deltas_then_done(), test_run_truncated_json_is_salvaged_not_cut_mid_sentence() (+2 more)

### Community 68 - "documents.py"
Cohesion: 0.07
Nodes (36): asyncio, AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut (+28 more)

### Community 69 - "matters/[id]/page.tsx"
Cohesion: 0.10
Nodes (41): FilesTab(), download(), handleFile(), remove(), formatSize(), MatterBackLink(), MatterDetail(), MatterDetailPage() (+33 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (32): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+24 more)

### Community 71 - "match"
Cohesion: 0.10
Nodes (24): expand(), laws(), match(), Lexicon entries hit by the Latin-script words of `text`, in order of appearance…, Devanagari statute terms for the roman/English words in `text` (deduplicated,…, Exact corpus titles of the statutes the matched strong entries point to., S7: non-LLM playbook matcher - keyword/glossary routing, no embeddings.…, test_matcher_precision_at_least_90_percent() (+16 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): _text_key(), assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest() (+24 more)

### Community 73 - "audit_document"
Cohesion: 0.21
Nodes (13): ai_fill_field(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, S13: writes one llm_usage row per real (non-cached, non-free-tier) generation,…, _record_llm_usage_sync(), audit_document(), _error(), HTTPException, UploadFile (+5 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.08
Nodes (25): 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500) (+17 more)

### Community 75 - "glossary.py"
Cohesion: 0.23
Nodes (12): _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes… (+4 more)

### Community 76 - "ai_fill.py"
Cohesion: 0.16
Nodes (14): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+6 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "_bad_input"
Cohesion: 0.16
Nodes (17): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), draft_document() (+9 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.09
Nodes (38): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of…, A DOCX with one paragraph per line (Unicode/Devanagari safe). (+30 more)

### Community 80 - "search/page.tsx"
Cohesion: 0.31
Nodes (10): DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit(), runSearch(), Strings (+2 more)

### Community 81 - "ics.ts"
Cohesion: 0.29
Nodes (9): RFC-5545, buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay(), stamp() (+1 more)

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
Cohesion: 0.14
Nodes (35): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+27 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.06
Nodes (122): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+114 more)

### Community 87 - "run_eval.py"
Cohesion: 0.07
Nodes (44): analyze_query(), build_queries(), quick_intent(), Obvious non-legal messages, recognised without any LLM., Weighted query set. Sources, best first: the LLM's Nepali legal phrasings; the…, search(), available(), parse_json() (+36 more)

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
Nodes (31): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+23 more)

### Community 92 - "rules.py"
Cohesion: 0.10
Nodes (29): Any, apply_checklist(), _clause_label(), Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate(), fields_in(), _leaf() (+21 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "test_drafting.py"
Cohesion: 0.14
Nodes (12): parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises(), test_legal_notice_salary_includes_answers_and_citation_ne(), test_missing_required_field_raises() (+4 more)

### Community 95 - "complete"
Cohesion: 0.16
Nodes (17): complete(), One completion within `budget_s` seconds across all providers, or…, Yield answer text incrementally. A provider/model is only abandoned before it…, stream(), gateway(), fixture, test_content_as_list_of_parts_and_reasoning_hint(), test_direct_providers_rotate_keys_and_skip_unconfigured() (+9 more)

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.09
Nodes (43): frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload() (+35 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.14
Nodes (18): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+10 more)

### Community 99 - "_require_matter"
Cohesion: 0.17
Nodes (15): create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task(), delete_research(), download_matter_file() (+7 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.05
Nodes (37): test_salary_question_flags_1970s_precedents_as_stale(), All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer (+29 more)

### Community 101 - "test_v31_streaming.py"
Cohesion: 0.12
Nodes (15): _Frame, IncrementalDoc, Truly incremental reader of the growing answer JSON: feed() consumes only the…, parametrize, V3.1: progressive streaming with per-sentence verification. The provider stream…, _sentences_of(), split_random(), test_incremental_parser_cut_off_mid_sentence_and_prose_prefix() (+7 more)

### Community 102 - "docx_out.py"
Cohesion: 0.10
Nodes (37): _add_font_table_fallback(), build_docx(), _get_or_add(), _insert_ordered(), _local(), _page_setup(), _paragraph(), Resolved layout blocks -> a real .docx (python-docx). Page and type set-up… (+29 more)

### Community 103 - "embedding_benchmark.py"
Cohesion: 0.25
Nodes (7): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize()

### Community 104 - "i18n.ts"
Cohesion: 0.10
Nodes (18): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+10 more)

### Community 105 - "render.py"
Cohesion: 0.12
Nodes (30): TemplateSpec, strip_inline(), _build_context(), _effective_language(), get_template(), get_template_detail(), _items(), list_templates() (+22 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.18
Nodes (17): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, parametrize (+9 more)

### Community 107 - "verifier.py"
Cohesion: 0.07
Nodes (58): check_sentence(), check_structured_sentence(), _cite_conflicts(), _cite_list(), _fuzzy_span(), _guidance_ok(), _in_terms(), lexical_support() (+50 more)

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.11
Nodes (23): build_parser(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text., Truncate to a byte budget without splitting a multi-byte character (Devanagari… (+15 more)

### Community 109 - "nepali.py"
Cohesion: 0.17
Nodes (19): ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka(), nd(), opts() (+11 more)

### Community 110 - "report.py"
Cohesion: 0.21
Nodes (11): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), Document (+3 more)

### Community 111 - "test_v3_structured.py"
Cohesion: 0.16
Nodes (31): check(), parametrize, V3: generate-then-verify. The model's JSON answer is checked sentence by…, S(), test_altered_quote_is_removed(), test_bad_citation_number_is_removed(), test_empathy_and_plain_advice_pass_uncited_but_uncited_procedure_needs_the_playbook(), test_english_sentence_with_english_translation_quote() (+23 more)

### Community 112 - "authority"
Cohesion: 0.18
Nodes (11): authority(), _clean(), giwms_table(), nia_rows(), Rows of a GIWMS table listing: | # | title | published | pdf link | ... |, (title, ISO date, pdf url) rows of one NIA /law/ page. Only the main table is…, Nepal Insurance Authority (nia.gov.np; formerly Beema Samiti). Its HTTPS…, Nepal Gazette (rajpatra.dop.gov.np). Not reachable from the build sandbox; the… (+3 more)

### Community 113 - "test_v32_claim_checks.py"
Cohesion: 0.07
Nodes (54): ctx_of(), _ctx_reason(), _doc_with(), judge(), labelled(), parametrize, V3.2: deterministic claim checks, built from the V3 live review (2026-09-30).…, (kept?, reason) of one sentence through verify_sentence exactly as the pipeline… (+46 more)

### Community 114 - "_date"
Cohesion: 0.08
Nodes (27): bs_to_ad(), add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule() (+19 more)

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.07
Nodes (40): clean_document(), clean_page(), document_verdict(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), is_table_noise() (+32 more)

### Community 117 - "newest_per_series"
Cohesion: 0.20
Nodes (11): _ad_date(), newest_per_series(), _nrb_listing_pages(), pub_sort_key(), Title with amendment parentheticals, digits and punctuation removed, so 'X ऐन,…, Comparable (year, month, day) for an AD ('July 22, 2025', '2025-07-22') or BS…, Keep the newest document of each title series (dated docs win; ties keep the…, Yield (href, title, date_str) over a paginated NRB category listing. (+3 more)

### Community 118 - "fake_stream"
Cohesion: 0.15
Nodes (26): fake_stream(), gen(), Simulated provider at 40 ms per ~3-char token: time to first verified text vs…, What the frontend ends up showing: deltas append, `replace` swaps., run_events(), test_cache_hit_still_has_no_streaming_events(), test_cut_off_stream_shows_only_complete_sentences(), test_document_level_failure_after_release_uses_replace() (+18 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.11
Nodes (29): _playbook_pick(), (playbook id or None, trusted). Trusted = an exact keyword phrase of the plan…, _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _playbook_vetoes() (+21 more)

### Community 120 - "answer_review.py"
Cohesion: 0.10
Nodes (22): corpus_source(), entail_payload(), (compact JSON for the entailment call, [(block, sentence) per item]). One item…, aggregate(), main(), Passages, post(), Collect answers from a running API for human / LLM review of the V3 generate-… (+14 more)

### Community 121 - "scrape_regulators.py"
Cohesion: 0.20
Nodes (14): download(), fiscal_year_bs(), giwms_files(), _is_doc_url(), _links(), _now(), Scrapes primary regulatory texts (acts, regulations, directives, circulars)…, Download doc['url'] into the store (skipped when already present) and record… (+6 more)

### Community 122 - "test_s11_matters.py"
Cohesion: 0.18
Nodes (5): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 123 - "test_eval_sets.py"
Cohesion: 0.09
Nodes (14): DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl…, Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the…, Return a list of problems ([] = every cited provision found and confirmed)., verify_case(), _lines(), _norm() (+6 more)

### Community 124 - "re"
Cohesion: 0.05
Nodes (39): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, looks_like_injection(), S13: prompt-injection guard for user-supplied text going into an LLM prompt.…, wrap_user_text(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Index term for one folded token ('' = drop it)., _stem_en() (+31 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "main"
Cohesion: 0.14
Nodes (15): _download(), Encoder, model_ready(), passage_text(), prepare_model(), Path, L2-normalised float32 embeddings, shape (len(texts), DIM). Batches are length-…, Document title + section heading + body, Nepali first, English title/heading… (+7 more)

### Community 127 - "parse_answer"
Cohesion: 0.12
Nodes (17): Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer(), _loose_blocks(), _n_sentences(), _norm_doc(), parse_answer(), Free-tier models sometimes emit JSON-ish text whose structure is broken (keys…, (doc, complete). complete=False when the object was cut off or broken and only… (+9 more)

### Community 128 - "ingest_scraped.py"
Cohesion: 0.17
Nodes (20): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+12 more)

### Community 129 - "Done"
Cohesion: 0.14
Nodes (16): _entry_status(), _index_text(), _prior(), Authority of the source x usefulness of this particular passage., Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S4 — Search + law browser UI (2026-09-26) (+8 more)

### Community 130 - "test_v33_topical_fit.py"
Cohesion: 0.06
Nodes (49): asks_quantity(), CheckContext, orphan_opener(), What the checks may know about the request. All optional: with none of it the…, Remove a leading "But/And/तर/र" that joined the sentence to one that was…, anaphor" when the sentence opens with a demonstrative / connective that points…, strip_leading_conjunction(), build() (+41 more)

### Community 131 - "get_index"
Cohesion: 0.10
Nodes (27): clear_query_cache(), Load everything and run one query through it (used by…, warm_up(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, get_index(), _inactive_regimes(), Regime ids whose cue words the (lower-cased) query text does not contain. (+19 more)

### Community 133 - "_line"
Cohesion: 0.22
Nodes (8): clean_ocr_text(), dedupe_marks(), OCR glitches the model copied from a scanned source into its own sentence: a…, [5][5] -> [5]; order kept., _line(), _norm_sentence(), New model text in; the text now safe to show (possibly ""), out., test_duplicate_adjacent_markers_are_merged_rw30()

### Community 134 - "topical_fit.py"
Cohesion: 0.05
Nodes (63): apply_topical_gate(), _guidance_terms_text(), V3.3: score every retrieved source for topical fit (topical_fit.py) and mark…, Every step/forum/evidence line of the plan in both languages: the only place an…, _cterms(), _f(), Family, _head_string() (+55 more)

### Community 135 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 136 - "filter_gaps"
Cohesion: 0.27
Nodes (10): filter_gaps(), gap_in_language(), (kept gaps, [(dropped gap, reason)]). Cited passages are tested first, then…, _clean_side_text(), _passage_text(), Gaps and follow-up questions carry no legal claim: keep them short and number-…, _gap_case(), test_honest_gaps_of_the_same_review_are_kept() (+2 more)

### Community 137 - "Client"
Cohesion: 0.15
Nodes (13): Client, _first_reachable(), _giwms_site(), Fetch a page/file if robots allows. Returns response (any status < 500) or None., Fetch a page; `patient` re-tries a few times after a pause, for listing pages…, Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher., Discover legal-text categories from a GIWMS site's home page and crawl them., One rate-limited request with retry on 5xx/network errors. Returns the… (+5 more)

### Community 138 - "entailment_filter"
Cohesion: 0.22
Nodes (7): entailment_filter(), ONE cheap call over every cited sentence: drop those whose quote does NOT…, test_build_runs_entailment_only_when_given_and_recounts(), test_entailment_fails_open(), boom(), test_entailment_removes_no_and_keeps_yes_and_partial(), test_run_provider_failure_gives_the_extractive_answer()

### Community 139 - "Store"
Cohesion: 0.24
Nodes (6): cmd_stats(), main(), sources/regulators/<authority>/{files/,manifest.jsonl}, Rewrite the manifest keeping only the latest record per URL., run_authority(), Store

### Community 140 - "scrape_lawcommission_gap"
Cohesion: 0.27
Nodes (10): existing_corpus_titles(), in_corpus(), Spelling/digit-insensitive identity of a law title (years are part of the…, title_key -> doc_title_ne for every law document in the pre-existing corpus…, True when a law of this title (same year, near-identical spelling:…, Compare the Law Commission's current-acts index (alphabetical index page: ~350…, scrape_lawcommission_gap(), fresh() (+2 more)

### Community 141 - "generation.py"
Cohesion: 0.06
Nodes (46): abstain_answer(), _cite(), _excerpt(), extractive_answer(), gate_ran(), on_topic_laws(), V3.3: what the user sees when the topical-fit gate leaves too little to answer…, The corpus files a long section under its FIRST sub-section ("दफा 10 (1)")… (+38 more)

### Community 142 - "_generate_verified"
Cohesion: 0.12
Nodes (21): answer_max_tokens(), _generate_verified(), add_usage(), paid_call(), repair(), (structured.build() result | None if no model answered, usage). Never raises.…, The per-piece part of tidy_answer (the constitutional "धारा" fix), so streamed…, Stream the model's JSON, verifying every sentence as it completes. A generator:… (+13 more)

### Community 143 - "Run the API in Docker (no cloud payment needed)"
Cohesion: 0.33
Nodes (5): 1. Start the API, 2. Give it a public HTTPS address (free, no domain, no card), 3. Point the website at it, Run the API in Docker (no cloud payment needed), Trade-offs

### Community 144 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 145 - "_targets"
Cohesion: 0.36
Nodes (8): _cool_target(), _model_key(), _openai_complete(), (base_url, api_key, model_id sent to the API, cooldown key)., Expand a "provider/model" chain into concrete endpoint+key+model calls:…, _Target, _targets(), tuple

### Community 146 - "useLang"
Cohesion: 0.16
Nodes (27): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), addToCalendar() (+19 more)

### Community 147 - "_playbook_id_for"
Cohesion: 0.29
Nodes (7): _playbook_id_for(), A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, The half-match on "boss" must not pin the Workplace Sexual Harassment…, test_the_wrong_playbook_is_not_a_confident_match(), parametrize, test_recurring_situations_route_to_their_playbook(), test_v25_lexicon_entries_map_to_statutory_terms()

### Community 148 - "@playwright/test"
Cohesion: 0.29
Nodes (3): Json, ref_node_fs, @playwright/test

### Community 149 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), Pattern, A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale()

### Community 150 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 151 - "situation_guards.py"
Cohesion: 0.25
Nodes (8): Guard, Pattern, _r(), V3.2: a small DATA table of wrong-law guards - (what the user's question says…, The id of the guard that forbids citing `source` for this question, else None., _section_no(), violation(), _guard_hit()

### Community 153 - "giwms_listing"
Cohesion: 0.40
Nodes (5): bs_key(), giwms_listing(), १३ असोज, २०८३' or '2083-06-13' -> (2083, 6, 13) for ordering; None if…, Iterate a GIWMS category listing (?page=N). Only the main list is read (not the…, scrape_ocr()

### Community 154 - ".search"
Cohesion: 0.38
Nodes (4): ndarray, Multiplies the fused scores (in place) by (a) a demotion for passages from a…, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, _title_tokens()

### Community 155 - "alignment_ok"
Cohesion: 0.40
Nodes (6): alignment_ok(), _lev(), near_variant(), Same word up to a character slip (matra/spelling/OCR): edit distance 1, or 2…, Every token of the quote is in the passage window, or is a near variant of the…, test_fused_or_split_words_are_line_break_noise_not_substitution()

### Community 156 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 163 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

## Knowledge Gaps
- **308 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+303 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1247 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `Done`, `get_index`, `ui.tsx`, `generation.py`, `run_eval.py`, `chat`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `test_v1_trust_engine.py`, `topical_fit.py`, `test_v25_routing.py`, `generation.py`, `Index`, `test_calculators.py`, `retrieval.py`, `chat`, `playbooks.py`, `limitation.py`, `chat.py`, `documents.py`, `match`, `test_documents_audit.py`, `run_eval.py`, `S5 — Supabase auth + DB (2026-09-26)`, `embedding_benchmark.py`, `answer_review.py`, `test_eval_sets.py`, `main`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _308 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `claim_checks.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04788732394366197 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.07293868921775898 - nodes in this community are weakly interconnected._