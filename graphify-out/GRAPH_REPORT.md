# Graph Report - LegalNeps  (2026-09-30)

## Corpus Check
- 198 files · ~431,768 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 29 file(s) not represented in the graph (top: .jsonl 11, .css 5, (none) 4)

## Summary
- 3018 nodes · 7042 edges · 141 communities (120 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 286 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6c92f315`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- test_translit.py
- test_calculators_tools.py
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
- tools.py
- text_norm.py
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
- analyze_query
- Personal Loan Playbooks
- Sexual Harassment Playbooks
- list_llm_usage
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
- translit.py
- limitation.py
- ocr_regulators.py
- forms_common.py
- ai_fill.py
- generation.py
- documents.py
- useLang
- ui.tsx
- test_playbooks.py
- ingest_regulators.py
- chat.py
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- glossary.py
- scrape_regulators.py
- test_ocr_clean.py
- get
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
- S5 — Supabase auth + DB (2026-09-26)
- checklists.py
- Per-playbook findings
- models.py
- docx_out.py
- send_compliance_reminders.py
- i18n.ts
- render.py
- extract_doc_meta
- audit_document
- scrape_lawcommission.py
- datetime
- contract_fixtures.py
- match
- post
- smoke.spec.ts
- FakeComplianceStore
- scripts
- ocr_clean.py
- test_eval_sets.py
- paid_complete
- playbook_matcher.py
- devDependencies
- dependencies
- pytest
- _FakeAnthropicClient
- test_s13_ai_gateway.py
- Env
- test_s12_compliance_radar.py
- json
- ingest_scraped.py
- Progress
- contract_types
- _playbook_id_for
- calendar
- doc_slug
- .search
- draft_update
- matter_file_create
- test_chat_route_anonymous_caller_stays_on_free_tier
- _GZipExceptStreams
- .attach_dense
- ._doc_index

## God Nodes (most connected - your core abstractions)
1. `get_index()` - 50 edges
2. `available()` - 47 edges
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
- `S8 — Calculators (2026-09-27)` --references--> `UnsupportedDate`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/dates.py
- `Known issues` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (141 total, 21 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.11
Nodes (33): ai_fill_field(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, AiFillRequest, AiFillResponse, Amendment, Analysis, Bilingual, CourtFeeAppealResponse (+25 more)

### Community 1 - "api.ts"
Cohesion: 0.05
Nodes (66): formatSize(), add(), remove(), Tab, TasksTab(), add(), patch(), remove() (+58 more)

### Community 2 - "test_translit.py"
Cohesion: 0.15
Nodes (14): expand(), Devanagari statute terms for the roman/English words in `text` (deduplicated,…, index(), fixture, parametrize, V2: the romanised-Nepali -> statute-Nepali lexicon (app/translit.py). The…, The validation that keeps the lexicon honest: after the same tokenisation the…, test_chh_ch_variants_tolerated_but_theft_is_not_daughter() (+6 more)

### Community 3 - "test_calculators_tools.py"
Cohesion: 0.04
Nodes (99): markers_table(), flat_fee(), flat_fee_types(), The fixed court fee for a case type where no value is claimed (s. 70, s. 71(2))., s. 74: when a review / retrial of a case is granted, an extra 10% of the plaint…, s. 82(1): on a settlement (मिलापत्र) of a fully paid case, the court keeps 25%…, review_fee(), settlement_fee() (+91 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.06
Nodes (54): _bs_year(), _is_regulator_query(), mark_stale_precedents(), _pipeline_fingerprint(), Pattern, A precedent decided before the statute now governing the topic was enacted…, Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer() (+46 more)

### Community 5 - "llm.py"
Cohesion: 0.08
Nodes (51): _anthropic_complete(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini(), _gemini_cfg() (+43 more)

### Community 6 - "test_dense.py"
Cohesion: 0.05
Nodes (44): Dense, enabled(), Encoder, load_dense(), ndarray, quantize(), L2-normalised float32 embeddings, shape (len(texts), DIM). Batches are length-…, float32 (n, DIM) -> int8 + per-vector float16 scale (cos ~ (q . x) * scale). (+36 more)

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
Cohesion: 0.08
Nodes (50): clear_query_cache(), Load everything and run one query through it (used by…, warm_up(), _is_fiscal_query(), _match_playbook(), pinned_provisions(), The curated playbook's own provisions, fetched as full corpus entries - hand-…, The curated action plan for this situation, when the keyword matcher is… (+42 more)

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
Nodes (7): Index, All passages (loads everything - for scripts/evals, not requests)., Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., Connection, S6 — Action Plan engine (2026-09-26)

### Community 15 - "devanagari_glyphs.py"
Cohesion: 0.14
Nodes (19): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+11 more)

### Community 16 - "tools.py"
Cohesion: 0.09
Nodes (57): _bad(), _catalog(), court_fee_flat(), court_fee_flat_types(), court_fee_review(), court_fee_settlement(), date_add(), date_age() (+49 more)

### Community 17 - "text_norm.py"
Cohesion: 0.14
Nodes (22): focus(), The part of a passage that matters for this question: the heading line plus the…, _is_english(), Latin-script and not romanised Nepali ("mero ghardhani le bhada badhayo")., fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised… (+14 more)

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
Nodes (9): _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip(), test_status_is_never_guessed() (+1 more)

### Community 23 - "test_calculators.py"
Cohesion: 0.08
Nodes (39): appeal_fee(), court_fee(), estimate(), The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its…, gratuity(), notice() (+31 more)

### Community 24 - "retrieval.py"
Cohesion: 0.07
Nodes (38): array, _download(), model_ready(), passage_text(), prepare_model(), Dense (semantic, cross-lingual) retrieval, fused with BM25 inside…, Document title + section heading + body, Nepali first, English title/heading…, Download the int8 ONNX encoder + sentencepiece model and prune the embedding… (+30 more)

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
Cohesion: 0.06
Nodes (77): age_on(), Age of someone born on `birth` on the date `as_of`, and when they reach each…, ad_to_bs(), add_bs_months(), add_bs_years(), add_days(), add_period(), bs_difference() (+69 more)

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
Nodes (49): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), _is_devanagari(), quick_intent(), Obvious non-legal messages, recognised without any LLM., Script check on the message itself. NOT the language hint: the hint is "ne" for… (+41 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "list_llm_usage"
Cohesion: 0.67
Nodes (3): list_llm_usage(), Cost-per-query visibility (STRATEGY's S13 "done when" bar): every paid-tier…, LlmUsageOut

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
Cohesion: 0.16
Nodes (14): _entry_status(), _index_text(), _prior(), Authority of the source x usefulness of this particular passage., Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S4 — Search + law browser UI (2026-09-26) (+6 more)

### Community 61 - "chat"
Cohesion: 0.11
Nodes (24): stream_answer(), chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage() (+16 more)

### Community 62 - "translit.py"
Cohesion: 0.31
Nodes (10): canon(), Entry, _lookup(), loose(), _parse(), Romanised-Nepali / English -> formal statute-Nepali legal lexicon. The corpus…, Spelling-tolerant form of a roman word: sh->s, w/v->b, z->j, ph/f->p,…, Even looser: chh==ch and trailing vowels dropped (dharauti/dharauta). Used only… (+2 more)

### Community 63 - "limitation.py"
Cohesion: 0.06
Nodes (56): estimate_appeal(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, Labour Act, 2074 (श्रम ऐन, २०७४) calculators (S8): gratuity, termination…, _by_id(), catalog(), check(), entry_view(), general_rules() (+48 more)

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
Cohesion: 0.13
Nodes (20): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), _history_text(), _LRU, _passage(), _playbook_card() (+12 more)

### Community 68 - "documents.py"
Cohesion: 0.11
Nodes (22): asyncio, health(), lifespan(), get, Request, _reject_oversized_bodies(), root(), _security_headers() (+14 more)

### Community 69 - "useLang"
Cohesion: 0.12
Nodes (42): Account(), AccountPage(), Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), ProfileForm() (+34 more)

### Community 70 - "ui.tsx"
Cohesion: 0.11
Nodes (31): frontend_app_globals, metadata, RootLayout(), viewport, SavedPage(), handleDelete(), AuthWidget(), handleSendCode() (+23 more)

### Community 71 - "test_playbooks.py"
Cohesion: 0.15
Nodes (16): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), Every playbook with every provision resolved - raises UnresolvedProvision on…, Summary list (no provision resolution - cheap, for GET /api/playbooks)., _resolve_playbook(), requires_corpus (+8 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.09
Nodes (32): _text_key(), assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest() (+24 more)

### Community 73 - "chat.py"
Cohesion: 0.10
Nodes (39): corpus_stats(), create_draft(), create_matter_note(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task() (+31 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.08
Nodes (25): 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices), 3.3 Fixed costs to run commercially (~$75/mo ≈ Rs 10,500) (+17 more)

### Community 75 - "glossary.py"
Cohesion: 0.26
Nodes (11): _expansion_precise(), The glossary's word-for-word expansion is trustworthy: it found something, and…, expand(), expand_hits(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes… (+3 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.05
Nodes (68): _ad_date(), authority(), bs_key(), _clean(), Client, cmd_stats(), download(), existing_corpus_titles() (+60 more)

### Community 77 - "test_ocr_clean.py"
Cohesion: 0.08
Nodes (4): OCR cleaning + quality-gate tests (ocr_clean.py, ocr_regulators.py helpers).…, _seed(), test_part002_rebuild_keeps_part003_after_it_in_the_digest(), test_second_shard_registered_last_with_own_counters()

### Community 78 - "get"
Cohesion: 0.11
Nodes (28): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+20 more)

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
Cohesion: 0.10
Nodes (15): audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, api_client(), _FakeHttp, _FakeResponse, fixture (+7 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.15
Nodes (20): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+12 more)

### Community 85 - "test_drafting_formats.py"
Cohesion: 0.13
Nodes (36): render_docx(), _all_text(), _answers(), _blank_text(), _dummy(), parametrize, requires_corpus, Prescribed-format drafting: every template renders to a real DOCX and a PDF,… (+28 more)

### Community 86 - "calculators.tsx"
Cohesion: 0.05
Nodes (125): AccrualCard(), AccrualResult, AddResult, AgeCard(), AgeResult, AppealFeeCard(), CourtFeeCard(), DateAddCard() (+117 more)

### Community 87 - "audit.py"
Cohesion: 0.11
Nodes (23): AuditError, classify_contract(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines(), keyword_scores() (+15 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.13
Nodes (22): _coerce(), Coerce a model-returned value to the fact's declared type, or None., Model JSON -> {fact: {"value": typed value | None, "clause_id": str | None}}.…, validate_extraction(), _ascii(), Clause, clause_by_id(), _clause_start() (+14 more)

### Community 90 - "extract.py"
Cohesion: 0.13
Nodes (24): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+16 more)

### Community 91 - "dsl.py"
Cohesion: 0.12
Nodes (32): _cell(), doc(), _flags(), _label_split(), _paragraph(), A tiny line-oriented markup for writing prescribed forms compactly, so the…, `@flags rest` -> (flags, rest); a line without a leading @ has no flags., The ल्याप्चे सहीछाप (thumbprint) block: a bold caption followed by a bordered… (+24 more)

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (31): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+23 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "normalise_text"
Cohesion: 0.18
Nodes (12): normalise_text(), parse_period_phrase(), Problems with one general rule's citation (the phrase must be in the cited…, Comparison form of a corpus text/phrase: NFC, no zero-width marks, Devanagari…, (value, unit) of the number+unit at the start of a phrase like 'छ महिनाभित्र'…, Problems (empty when fine) with one entry's citation and stated period: the…, verify_entry(), verify_rule() (+4 more)

### Community 95 - "@playwright/test"
Cohesion: 0.29
Nodes (3): Json, ref_node_fs, @playwright/test

### Community 96 - "run_audit"
Cohesion: 0.10
Nodes (23): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), get_checklist(), The type's checklist with only verified checks, each carrying…, Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader (+15 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.08
Nodes (46): addToCalendar(), frontend_app_draft_draft, DraftPage(), handleDelete(), Msg, TemplateForm(), cleanAnswers(), handleAiHelp() (+38 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.14
Nodes (18): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), jsonb_safe(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Postgres jsonb rejects the NUL character (\\u0000), which some scanned law… (+10 more)

### Community 99 - "checklists.py"
Cohesion: 0.21
Nodes (15): assert_integrity(), _bilingual(), ChecklistError, _load_all(), public_listing(), ValueError, Loads and validates the contract checklists in data/contract_checklists/*.yaml.…, Raise UnresolvedProvision for any cited provision (verified or not) the corpus… (+7 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (32): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+24 more)

### Community 101 - "models.py"
Cohesion: 0.26
Nodes (12): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+4 more)

### Community 102 - "docx_out.py"
Cohesion: 0.07
Nodes (48): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), _add_font_table_fallback() (+40 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.18
Nodes (14): all_company_profiles(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent(), reminder_record_sent() (+6 more)

### Community 104 - "i18n.ts"
Cohesion: 0.11
Nodes (16): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DOC_TYPE_LABEL, LawDocPage(), LawSectionPage() (+8 more)

### Community 105 - "render.py"
Cohesion: 0.13
Nodes (30): TemplateSpec, strip_inline(), build_pdf(), _build_context(), _effective_language(), get_template(), get_template_detail(), _items() (+22 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.18
Nodes (16): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, requires_corpus (+8 more)

### Community 107 - "audit_document"
Cohesion: 0.33
Nodes (7): audit_document(), _error(), HTTPException, UploadFile, Bounded chunked read (see routes/chat.py:upload_matter_file): an oversized…, Signed-in only. Metered against the caller's plan-based daily quota exactly…, _read_capped()

### Community 108 - "scrape_lawcommission.py"
Cohesion: 0.09
Nodes (27): build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text. (+19 more)

### Community 109 - "datetime"
Cohesion: 0.12
Nodes (22): Age calculator for majority and consent-age questions. Age is counted on the…, Interest on private loans under the Muluki Civil Code, 2074, chapter 15 (लेनदेन…, ad_numeric(), _as_date(), blank(), bs_numeric(), bs_parts(), ka() (+14 more)

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "match"
Cohesion: 0.22
Nodes (9): match(), The word itself, then with a glued Nepali postposition (-le/-ko/-lai/-ma ...)…, Lexicon entries hit by the Latin-script words of `text`, in order of appearance…, _stem_variants(), strong_count(), S7: non-LLM playbook matcher - keyword/glossary routing, no embeddings.…, test_matcher_precision_at_least_90_percent(), test_matcher_returns_none_for_empty_query() (+1 more)

### Community 112 - "post"
Cohesion: 0.13
Nodes (15): create_matter(), create_matter_task(), draft_document(), Response, UploadFile, The drafted document as DOCX (default) or PDF (`format: "pdf"`)., save_research(), upload_matter_file() (+7 more)

### Community 113 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 114 - "FakeComplianceStore"
Cohesion: 0.18
Nodes (4): compliance_client(), FakeComplianceStore, fixture, test_reminder_job_dedups_via_reminders_sent()

### Community 115 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 116 - "ocr_clean.py"
Cohesion: 0.09
Nodes (31): clean_document(), clean_page(), document_verdict(), drop_latin_noise(), _fix_devanagari(), _header_key(), _is_noise_line(), is_table_noise() (+23 more)

### Community 117 - "test_eval_sets.py"
Cohesion: 0.09
Nodes (14): DocResolver, norm(), Corpus verification for eval cases (V1). Each case in questions_realworld.jsonl…, Resolve a case's `doc` (exact title or unambiguous prefix) to a title in the…, Return a list of problems ([] = every cited provision found and confirmed)., verify_case(), _lines(), _norm() (+6 more)

### Community 118 - "paid_complete"
Cohesion: 0.22
Nodes (10): paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, looks_like_injection(), free(), parametrize, test_looks_like_injection_does_not_flag_ordinary_legal_questions(), test_looks_like_injection_flags_common_patterns(), test_paid_complete_calls_the_named_model_and_returns_usage() (+2 more)

### Community 119 - "playbook_matcher.py"
Cohesion: 0.19
Nodes (17): _keyword_hit_fraction(), _keyword_weight(), Match, match_scored(), _playbook_keywords(), _query_tokens(), Non-LLM query -> playbook routing (S7). Scores each playbook's `keywords` list…, match(), but also returns the winning score. (+9 more)

### Community 120 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 121 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 122 - "pytest"
Cohesion: 0.17
Nodes (6): matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, test_user_b_cannot_see_user_a_matter_or_its_subresources(), pytest

### Community 123 - "_FakeAnthropicClient"
Cohesion: 0.22
Nodes (4): _FakeAnthropicClient, _FakeMessage, _FakeTextBlock, _FakeUsage

### Community 124 - "test_s13_ai_gateway.py"
Cohesion: 0.13
Nodes (18): daily_quota_for(), estimate_cost_usd(), model_for_tier(), S13: plan-based tier routing and token-cost accounting. STRATEGY.md §2's…, `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).…, select_tier(), test_audit_happy_path_on_the_free_plan_uses_the_free_chain(), test_paid_plan_routes_to_sonnet_and_logs_llm_usage() (+10 more)

### Community 125 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 126 - "test_s12_compliance_radar.py"
Cohesion: 0.18
Nodes (4): S12: Compliance Radar lite - company profile, obligations, upcoming-due…, test_applies_to_gates_on_profile_fields(), test_next_due_annual_obligation(), test_next_due_is_always_in_the_future_and_recurs_monthly()

### Community 127 - "json"
Cohesion: 0.10
Nodes (20): argparse, _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, E5Small, _first_hit(), load_questions(), main(), ndarray (+12 more)

### Community 128 - "ingest_scraped.py"
Cohesion: 0.17
Nodes (20): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+12 more)

### Community 129 - "Progress"
Cohesion: 0.25
Nodes (9): parametrize, test_enacted_date_matches_known_acts(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus), Next session (+1 more)

### Community 130 - "contract_types"
Cohesion: 0.38
Nodes (6): _keyword_table(), contract_types(), get_raw(), `verify` lists substrings that carry each rule's number/requirement ("छ महिना",…, test_every_verified_rule_number_appears_in_the_cited_corpus_text(), test_five_contract_types_each_with_verified_checks()

### Community 131 - "_playbook_id_for"
Cohesion: 0.29
Nodes (7): _playbook_id_for(), A playbook id for `text`, or None. The keyword matcher alone is loose: a single…, laws(), Exact corpus titles of the statutes the matched strong entries point to., The half-match on "boss" must neither skip the LLM nor pin the Workplace Sexual…, test_the_wrong_playbook_is_not_a_confident_match(), test_laws_are_reported_for_strong_matches_only()

### Community 133 - "doc_slug"
Cohesion: 0.33
Nodes (6): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours()

### Community 134 - ".search"
Cohesion: 0.33
Nodes (4): ndarray, `mode`: "hybrid" (BM25 + dense when available), "bm25" or "dense" (ablations);…, Adds each eligible query's dense (cosine) ranking to `fused` in place, by…, _title_tokens()

### Community 135 - "draft_update"
Cohesion: 0.38
Nodes (7): draft_create(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft…, test_draft_functions_fail_open_without_supabase_configured()

### Community 136 - "matter_file_create"
Cohesion: 0.29
Nodes (7): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), parametrize, test_safe_filename(), test_uploaded_filename_cannot_steer_the_storage_path()

### Community 137 - "test_chat_route_anonymous_caller_stays_on_free_tier"
Cohesion: 0.40
Nodes (4): The core S13 wiring bug surface: a paid-plan user's /api/chat call must route…, test_chat_route_anonymous_caller_stays_on_free_tier(), test_chat_route_selects_tier_from_plan(), fake_answer_question()

## Knowledge Gaps
- **296 isolated node(s):** `built_at`, `curated`, `law_chunks`, `precedents`, `total` (+291 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1053 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `analyze_query`, `generation.py`, `ui.tsx`, `get_index`, `Done`, `chat`?**
  _High betweenness centrality (0.265) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `get_index()` connect `get_index` to `contract_types`, `generation.py`, `checklists.py`, `documents.py`, `test_translit.py`, `test_v1_trust_engine.py`, `S5 — Supabase auth + DB (2026-09-26)`, `chat.py`, `Index`, `get`, `test_documents_audit.py`, `test_eval_sets.py`, `retrieval.py`, `json`, `chat`, `limitation.py`?**
  _High betweenness centrality (0.182) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `built_at`, `curated`, `law_chunks` to the rest of the system?**
  _296 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10873440285204991 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.05487269534679543 - nodes in this community are weakly interconnected._