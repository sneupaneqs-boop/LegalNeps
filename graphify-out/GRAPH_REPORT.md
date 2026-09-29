# Graph Report - LegalNeps  (2026-09-29)

## Corpus Check
- 146 files · ~237,052 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .jsonl 7, (none) 3, .gz 3)

## Summary
- 2082 nodes · 4544 edges · 129 communities (112 shown, 17 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 229 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `333b8d00`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- api.ts
- scrape_nkp.py
- test_calculators.py
- test_v1_trust_engine.py
- llm.py
- playbook_matcher.py
- test_api.py
- extract_laws.py
- supa.py
- search
- Graphify Tool Documentation
- package.json
- build_corpus.py
- Index
- devanagari_glyphs.py
- test_s12_compliance_radar.py
- text_norm.py
- Web Crawler Implementation
- Project Strategy and Prompts
- TypeScript Configuration
- test_s10_ai_and_save.py
- test_regulators_ingest.py
- resolve_provision
- compliance.py
- test_drafting.py
- counts
- Civil Law Playbooks
- Graph Export Documentation
- dates.py
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- run_eval.py
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
- get
- chat
- scrape_lawcommission.py
- limitation.py
- list_llm_usage
- ai_fill.py
- test_s13_ai_gateway.py
- generation.py
- documents.py
- matters/[id]/page.tsx
- ui.tsx
- json
- ingest_regulators.py
- post
- Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform
- retrieval.py
- scrape_regulators.py
- ingest_scraped.py
- Client
- test_documents_audit.py
- LangContext.tsx
- ingest_pdfs.py
- test_retrieval.py
- test_s14_security.py
- ChatMessage.tsx
- compliance/page.tsx
- useLang
- audit.py
- audit/page.tsx
- segment.py
- extract.py
- mark_stale_precedents
- rules.py
- Session prompts — V2 (commercial build)
- chunk_document
- match_playbooks
- run_audit
- [templateId]/page.tsx
- S5 — Supabase auth + DB (2026-09-26)
- checklists.py
- Per-playbook findings
- models.py
- report.py
- send_compliance_reminders.py
- playbooks.py
- render.py
- extract_doc_meta
- pytest
- giwms_listing
- glossary.py
- contract_fixtures.py
- ics.ts
- Progress
- @playwright/test
- Env
- smoke.spec.ts
- scripts
- Done
- test_playbook_matcher.py
- devDependencies
- dependencies
- verifier.py
- _FakeAnthropicClient
- preeti.ts
- draft_update
- scrape_lawcommission_gap
- S6 — Action Plan engine (2026-09-26)
- doc_slug
- drop_redraw_passes

## God Nodes (most connected - your core abstractions)
1. `useLang()` - 48 edges
2. `available()` - 47 edges
3. `_http()` - 42 edges
4. `get_index()` - 35 edges
5. `callJson()` - 32 edges
6. `errorText()` - 30 edges
7. `run()` - 28 edges
8. `run_audit()` - 27 edges
9. `Client` - 26 edges
10. `Per-playbook findings` - 25 edges

## Surprising Connections (you probably didn't know these)
- `V-batch 1 — trust engine, full UI, Document AI (2026-09-29)` --references--> `search()`  [INFERRED]
  docs/PROGRESS.md → backend/app/generation.py
- `Next session` --references--> `audit_log()`  [INFERRED]
  docs/PROGRESS.md → backend/app/supa.py
- `S8 — Calculators (2026-09-27)` --references--> `check()`  [INFERRED]
  docs/PROGRESS.md → backend/app/calculators/limitation.py
- `Known issues` --references--> `extract_doc_meta()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py
- `Known issues` --references--> `classify_status()`  [INFERRED]
  docs/PROGRESS.md → backend/app/doc_meta.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (129 total, 17 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.11
Nodes (34): ai_fill_field(), law_doc(), list_playbooks(), Expands a free-text field's short hint via the LLM. Signed-in only, metered…, upcoming_obligations(), AiFillRequest, AiFillResponse, Amendment (+26 more)

### Community 1 - "api.ts"
Cohesion: 0.05
Nodes (46): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, DraftPage(), handleDelete(), DOC_TYPE_LABEL (+38 more)

### Community 2 - "scrape_nkp.py"
Cohesion: 0.17
Nodes (13): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+5 more)

### Community 3 - "test_calculators.py"
Cohesion: 0.12
Nodes (25): appeal_fee(), court_fee(), estimate(), estimate_appeal(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its… (+17 more)

### Community 4 - "test_v1_trust_engine.py"
Cohesion: 0.12
Nodes (26): _is_regulator_query(), Drop a trailing heading with nothing under it (a cut-off stream) and fix "धारा"…, tidy_answer(), _current_bs_year(), Corrects status/type the source metadata gets wrong for law that isn't…, _temporal_status(), Returns (answer with unsupported legal claims marked, report)., verify() (+18 more)

### Community 5 - "llm.py"
Cohesion: 0.07
Nodes (52): _anthropic_complete(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini(), _gemini_cfg() (+44 more)

### Community 6 - "playbook_matcher.py"
Cohesion: 0.22
Nodes (13): _keyword_hit_fraction(), _keyword_weight(), Match, _playbook_keywords(), _query_tokens(), Non-LLM query -> playbook routing (S7). Scores each playbook's `keywords` list…, Longer, more specific phrases count for more than a bare one-word keyword, so a…, 1.0 for an exact phrase hit, else the fraction of the keyword's own words that… (+5 more)

### Community 7 - "test_api.py"
Cohesion: 0.10
Nodes (7): normalize_citations(), Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, client(), fixture, test_research_save_list_delete_roundtrip(), test_text_citations_are_mapped_to_numbered_sources(), fastapi_testclient

### Community 8 - "extract_laws.py"
Cohesion: 0.15
Nodes (23): build_glyph_reference(), build_vocab(), convert_legacy(), extract_pdf(), _font_bytes(), _font_family(), font_plan(), _get_mapper() (+15 more)

### Community 9 - "supa.py"
Cohesion: 0.20
Nodes (28): available(), _http(), llm_usage_list(), llm_usage_record(), matter_create(), matter_file_delete(), matter_file_list(), matter_file_signed_url() (+20 more)

### Community 10 - "search"
Cohesion: 0.21
Nodes (14): build_queries(), _is_fiscal_query(), _match_playbook(), pinned_provisions(), Weighted query set: the LLM's Nepali legal phrasings carry most weight;…, The curated playbook's own provisions, fetched as full corpus entries - hand-…, The curated action plan for this situation, when the keyword matcher is…, search() (+6 more)

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

### Community 16 - "test_s12_compliance_radar.py"
Cohesion: 0.12
Nodes (5): compliance_client(), FakeComplianceStore, fixture, S12: Compliance Radar lite - company profile, obligations, upcoming-due…, test_reminder_job_dedups_via_reminders_sent()

### Community 17 - "text_norm.py"
Cohesion: 0.14
Nodes (22): focus(), The part of a passage that matters for this question: the heading line plus the…, ndarray, _title_tokens(), fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised… (+14 more)

### Community 18 - "Web Crawler Implementation"
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
Nodes (10): _text_key(), _ex(), Chunking + schema tests for the regulator pipeline (ingest_regulators.py /…, test_english_documents_use_english_fields(), test_exact_duplicates_of_existing_text_are_dropped(), test_manifest_update_appends_shard_and_recomputes_digest_like_build_corpus(), test_nepali_directive_entries_match_schema(), test_shard_roundtrip() (+2 more)

### Community 23 - "resolve_provision"
Cohesion: 0.15
Nodes (17): gratuity(), notice(), notice_period_days(), Labour Act, 2074 (श्रम ऐन, २०७४) calculators (S8): gratuity, termination…, दफा ५३: उपदान accrues at 8.33% of basic monthly pay for every month worked,…, दफा १४४(१): minimum notice before ending an employment relationship (either…, दफा १४४: the notice period owed, and the pay-in-lieu (दफा १४४(२)/(३)) if the…, दफा १४५(७): one month's basic pay per completed year of service as a lump-sum… (+9 more)

### Community 24 - "compliance.py"
Cohesion: 0.18
Nodes (20): add_bs_days(), add_bs_months(), applies_to(), _bs_date(), bs_month_end(), _due_date_ad(), due_date_for_fy_end_rule(), due_date_for_month_end_rule() (+12 more)

### Community 25 - "test_drafting.py"
Cohesion: 0.16
Nodes (15): list_templates(), render_docx(), parametrize, requires_corpus, S9: drafting engine - questionnaire answers -> rendered DOCX, bilingual. Table-…, test_drafting_api_endpoints(), test_generated_docx_opens(), test_invalid_language_raises() (+7 more)

### Community 26 - "counts"
Cohesion: 0.17
Nodes (11): built_at, counts, curated, law_chunks, law_documents, precedents, regulator_chunks, regulator_documents (+3 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Documentation"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "dates.py"
Cohesion: 0.16
Nodes (14): ad_to_bs(), bs_to_ad(), date, ValueError, BS <-> AD date conversion (S8). Nepal's Bikram Sambat calendar has variable…, Outside the BS calendar table this build ships with., UnsupportedDate, test_ad_to_bs_rejects_out_of_range() (+6 more)

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "run_eval.py"
Cohesion: 0.11
Nodes (35): analyze_needs_llm(), analyze_query(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message is a legal question we can search well without an…, Whether analyze_query() will reach a provider for this message - kept in sync…, available() (+27 more)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "chat.py"
Cohesion: 0.13
Nodes (31): corpus_stats(), create_matter_task(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task(), delete_research() (+23 more)

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
Cohesion: 0.08
Nodes (7): FakeMattersStore, matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, In-memory stand-in for supa.py's matters/notes/tasks/files functions, keyed by…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 60 - "get"
Cohesion: 0.10
Nodes (28): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+20 more)

### Community 61 - "chat"
Cohesion: 0.13
Nodes (21): chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_llm_usage(), _log_request() (+13 more)

### Community 62 - "scrape_lawcommission.py"
Cohesion: 0.17
Nodes (15): build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text. (+7 more)

### Community 63 - "limitation.py"
Cohesion: 0.25
Nodes (6): LimitationRule, ValueError, Limitation-period (हदम्याद) checker (S8). मुलुकी देवानी कार्यविधि संहिता दफा ४९…, UnknownClaimType, calendar, dataclasses

### Community 64 - "list_llm_usage"
Cohesion: 0.67
Nodes (3): list_llm_usage(), Cost-per-query visibility (STRATEGY's S13 "done when" bar): every paid-tier…, LlmUsageOut

### Community 65 - "ai_fill.py"
Cohesion: 0.23
Nodes (10): _build(), fill_paid(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Returns (system, user) for the given field, or raises ValueError /…, S13: same expansion, billed to a specific paid-tier model…, UnknownField (+2 more)

### Community 66 - "test_s13_ai_gateway.py"
Cohesion: 0.10
Nodes (21): paid_complete(), S13: a direct call to one specific Anthropic model, no fallback chain. Paid…, looks_like_injection(), `task` is "chat" (structured Q&A) or "draft" (AI-fill / document drafting).…, select_tier(), gateway_client(), fixture, parametrize (+13 more)

### Community 67 - "generation.py"
Cohesion: 0.12
Nodes (21): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), _history_text(), _LRU, _passage(), _playbook_card() (+13 more)

### Community 68 - "documents.py"
Cohesion: 0.07
Nodes (34): asyncio, _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, _GZipExceptStreams, health(), lifespan(), get, Request (+26 more)

### Community 69 - "matters/[id]/page.tsx"
Cohesion: 0.09
Nodes (48): FilesTab(), download(), handleFile(), remove(), formatSize(), MatterBackLink(), MatterDetail(), MatterDetailPage() (+40 more)

### Community 70 - "ui.tsx"
Cohesion: 0.13
Nodes (28): Account(), AccountPage(), frontend_app_globals, metadata, RootLayout(), viewport, AuthWidget(), handleSendCode() (+20 more)

### Community 71 - "json"
Cohesion: 0.19
Nodes (12): argparse, main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, main(), OCR for documents extract_laws.py flagged `needs_ocr` (scanned PDFs, or text…, render(), transcribe(), Build the BM25 search index at deploy BUILD time, not on first request.… (+4 more)

### Community 72 - "ingest_regulators.py"
Cohesion: 0.10
Nodes (30): assess(), build_entries(), _cache_path(), chunk_directive(), chunk_text(), clean_title(), corpus_digest(), english_title() (+22 more)

### Community 73 - "post"
Cohesion: 0.15
Nodes (13): create_draft(), create_matter(), create_matter_note(), draft_document(), Response, save_research(), DraftRequest, MatterIn (+5 more)

### Community 74 - "Kanooni Sathi — Strategy V2: from backend foundations to a commercial legal intelligence platform"
Cohesion: 0.07
Nodes (26): free(), 1.1 What exists, 1.2 What's broken or risky (found live, not theoretical), 1.3 Verdict, 1. Audit: where the product actually is (measured 2026-09-29), 2. What to take from the research reports — and what to reject, 3.1 Plans (recommended), 3.2 Unit economics (assume ~Rs 140/USD; Anthropic list prices) (+18 more)

### Community 75 - "retrieval.py"
Cohesion: 0.11
Nodes (19): array, corpus_source(), get_index(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, Backwards-compatible single-query search., retrieve(), E5Small, _first_hit() (+11 more)

### Community 76 - "scrape_regulators.py"
Cohesion: 0.12
Nodes (24): _clean(), cmd_stats(), download(), fiscal_year_bs(), giwms_files(), giwms_table(), _is_doc_url(), _links() (+16 more)

### Community 77 - "ingest_scraped.py"
Cohesion: 0.27
Nodes (11): ask_json(), load_corpus(), load_ingested(), load_manifest(), main(), Step 2 of the scrape pipeline: turns documents downloaded by…, save_corpus(), save_ingested() (+3 more)

### Community 78 - "Client"
Cohesion: 0.13
Nodes (16): authority(), Client, _giwms_site(), Fetch a page/file if robots allows. Returns response (any status < 500) or None., Fetch a page; `patient` re-tries a few times after a pause, for listing pages…, Rate-limited, robots-aware, retrying fetcher built on scrapling.Fetcher., Discover legal-text categories from a GIWMS site's home page and crawl them., One rate-limited request with retry on 5xx/network errors. Returns the… (+8 more)

### Community 79 - "test_documents_audit.py"
Cohesion: 0.08
Nodes (42): extract_text(), Extract clean text from a PDF or DOCX. Raises a DocumentError subclass…, daily_quota_for(), _esc(), make_docx(), make_pdf(), Generators for the PDF and DOCX fixtures used by test_documents_audit.py. Built…, A minimal text PDF (Helvetica, Latin text only) with one page per inner list of… (+34 more)

### Community 80 - "LangContext.tsx"
Cohesion: 0.12
Nodes (21): SavedPage(), handleDelete(), DOC_TYPES, docTypeLabel(), ResultCard(), resultHref(), SearchPage(), handleSubmit() (+13 more)

### Community 81 - "ingest_pdfs.py"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 82 - "test_retrieval.py"
Cohesion: 0.12
Nodes (3): idx(), fixture, test_cache_roundtrip()

### Community 83 - "test_s14_security.py"
Cohesion: 0.10
Nodes (13): matter_file_create(), A display-safe file name: no directory parts, no "..", no control or path…, Uploads the bytes to Storage, then records the metadata row. Storage upload…, safe_filename(), api_client(), _FakeHttp, _FakeResponse, fixture (+5 more)

### Community 84 - "ChatMessage.tsx"
Cohesion: 0.14
Nodes (21): Home(), handleKeyDown(), handleSaveResearch(), handleSend(), frontend_components_chat_extras, ChatMessage(), Message, statusClass() (+13 more)

### Community 85 - "compliance/page.tsx"
Cohesion: 0.18
Nodes (16): Compliance(), CompliancePage(), daysLabel(), ENTITY_TYPES, Obligations(), addToCalendar(), ProfileForm(), submit() (+8 more)

### Community 86 - "useLang"
Cohesion: 0.23
Nodes (33): AppealFeeCard(), CalcError(), CalcState, Card(), CourtFeeCard(), DateCard(), GratuityCard(), LimitationCard() (+25 more)

### Community 87 - "audit.py"
Cohesion: 0.09
Nodes (27): AuditError, classify_contract(), _coerce(), _confident(), ContractTypeUnknown, extract_facts(), ExtractionFailed, _fact_lines() (+19 more)

### Community 88 - "audit/page.tsx"
Cohesion: 0.12
Nodes (28): frontend_app_audit_audit, AuditPage(), describe(), handleDownload(), runAudit(), FindingRow(), fmtBytes(), fmtValue() (+20 more)

### Community 89 - "segment.py"
Cohesion: 0.15
Nodes (19): _ascii(), Clause, clause_by_id(), _clause_start(), _normalise_id(), _paragraph_fallback(), prompt_view(), Split contract text into numbered clauses so findings can cite "Clause 7".… (+11 more)

### Community 90 - "extract.py"
Cohesion: 0.12
Nodes (25): CorruptDocumentError, DocumentError, EmptyDocumentError, _extract_docx(), _extract_pdf(), ExtractedDocument, LegacyFontError, looks_garbled() (+17 more)

### Community 91 - "mark_stale_precedents"
Cohesion: 0.33
Nodes (6): _bs_year(), mark_stale_precedents(), A precedent decided before the statute now governing the topic was enacted…, test_annual_finance_act_does_not_make_precedents_stale(), test_precedent_older_than_governing_act_is_stale(), Pattern

### Community 92 - "rules.py"
Cohesion: 0.09
Nodes (32): Any, apply_checklist(), _clause_label(), _quote(), A short excerpt of the clause, cut by us (never model-written). Prefers the…, Deterministically judge `facts` against the checklist. Returns (findings,…, applies(), evaluate() (+24 more)

### Community 93 - "Session prompts — V2 (commercial build)"
Cohesion: 0.40
Nodes (4): Master prompt (paste at the start of every session), Model guidance, Session add-ons (append to the master prompt), Session prompts — V2 (commercial build)

### Community 94 - "chunk_document"
Cohesion: 0.14
Nodes (14): chunk_document(), find_sections(), _join_zwnj_breaks(), हेजिङ्‌ग" typed with ZWNJ is often drawn with a space glyph; rejoin such…, Paragraph-aligned windows of ~size chars. Returns (window, offset of its first…, Split into sections (legislation) or windows (everything else). Each chunk…, Section headings: every strict match, plus loose matches that supply exactly…, _section_no() (+6 more)

### Community 95 - "match_playbooks"
Cohesion: 0.67
Nodes (3): match_playbooks(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, PlaybookMatchResponse

### Community 96 - "run_audit"
Cohesion: 0.12
Nodes (20): AuditMeta, Side-channel for the route: usage to bill/log, and the injection flag., Audit contract `text`. `contract_type` None/"auto" -> classify. Raises…, run_audit(), Callable with the signature of llm.complete (system, user, **kw) -> str., RegexReader, A model that tries to declare things legal (extra keys, verdicts) has no…, test_classification_keywords_first_then_llm_fallback() (+12 more)

### Community 97 - "[templateId]/page.tsx"
Cohesion: 0.17
Nodes (20): Msg, TemplateForm(), cleanAnswers(), handleAiHelp(), handleDownload(), handleSave(), missingFields(), setAnswer() (+12 more)

### Community 98 - "S5 — Supabase auth + DB (2026-09-26)"
Cohesion: 0.17
Nodes (15): cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), get_user(), None on a miss OR if the cached row is from a stale corpus_version - the whole…, Validate a Supabase access token (from the frontend's Authorization header) and…, True if this IP is still under its hourly budget (and records the hit). (+7 more)

### Community 99 - "checklists.py"
Cohesion: 0.14
Nodes (22): _keyword_table(), assert_integrity(), _bilingual(), ChecklistError, contract_types(), get_checklist(), get_raw(), _load_all() (+14 more)

### Community 100 - "Per-playbook findings"
Cohesion: 0.06
Nodes (32): All NEEDS-ADVOCATE-REVIEW items (64), bonus_not_paid - Employer has not paid bonus, cheque_bounce - Cheque given to me bounced, child_custody - Custody of children after separation/divorce, child_marriage_protection - Stop or report a child marriage, citizenship_by_descent - Citizenship by descent (self or child), consumer_complaint - Defective product / cheated as consumer, cyber_harassment - Online harassment / photos or private information shared (+24 more)

### Community 101 - "models.py"
Cohesion: 0.19
Nodes (15): AuditResult, Bilingual, ChecklistCheckOut, ChecklistTypeOut, ExtractedFactOut, FindingOut, NotEnforcedOut, ProvisionOut (+7 more)

### Community 102 - "report.py"
Cohesion: 0.16
Nodes (14): _add(), _cell(), _fonts(), Render an audit result as a DOCX report (python-docx), in English or Nepali., Latin text in Calibri, Devanagari (complex script) in Mangal so Word renders…, `audit` is the dict returned by audit.run_audit (or the API's JSON)., render_report(), audit_report() (+6 more)

### Community 103 - "send_compliance_reminders.py"
Cohesion: 0.17
Nodes (15): all_company_profiles(), company_profile_get(), company_profile_upsert(), obligations_list(), One profile per user - create it if missing, otherwise overwrite it., The full seeded obligation catalogue - public reference data, not scoped to any…, Used only by the reminder job (backend/scripts/send_compliance_reminders.py),…, reminder_already_sent() (+7 more)

### Community 104 - "playbooks.py"
Cohesion: 0.16
Nodes (14): all_playbooks_resolved(), get_playbook(), _get_playbook_cached(), list_playbooks(), Action Plan engine (S6): loads YAML playbooks (issue -> fact questions -> cited…, Every playbook with every provision resolved - raises UnresolvedProvision on…, Summary list (no provision resolution - cheap, for GET /api/playbooks)., _resolve_playbook() (+6 more)

### Community 105 - "render.py"
Cohesion: 0.15
Nodes (19): Field, Paragraph, Questionnaire field + document paragraph shapes shared by every drafting…, One paragraph of the generated document. `text` holds a Jinja source string per…, TemplateSpec, S9's first 6 drafting templates. Every statute reference embedded in a…, _build_context(), get_template() (+11 more)

### Community 106 - "extract_doc_meta"
Cohesion: 0.15
Nodes (20): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, _entry_status() (+12 more)

### Community 107 - "pytest"
Cohesion: 0.22
Nodes (13): ValueError, A playbook cites a law_title_ne/section that isn't in the corpus., _resolve_provision(), UnresolvedProvision, requires_corpus, S6: every playbook's cited provisions must actually exist in the corpus. Uses…, test_bogus_provision_is_rejected_not_silently_dropped(), test_every_cited_provision_resolves_in_the_real_corpus() (+5 more)

### Community 108 - "giwms_listing"
Cohesion: 0.16
Nodes (14): _ad_date(), bs_key(), giwms_listing(), newest_per_series(), pub_sort_key(), १३ असोज, २०८३' or '2083-06-13' -> (2083, 6, 13) for ordering; None if…, Iterate a GIWMS category listing (?page=N). Only the main list is read (not the…, Title with amendment parentheticals, digits and punctuation removed, so 'X ऐन,… (+6 more)

### Community 109 - "glossary.py"
Cohesion: 0.43
Nodes (7): expand(), _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, Nepali statute terms for the English/romanised phrases in `text`, longest…, size()

### Community 110 - "contract_fixtures.py"
Cohesion: 0.31
Nodes (10): _has(), _interest(), _n(), _num(), _payment_interval(), Synthetic contracts with SEEDED defects, plus a stand-in for the LLM reader.…, _search(), _term_years() (+2 more)

### Community 111 - "ics.ts"
Cohesion: 0.29
Nodes (9): RFC-5545, buildIcs(), compact(), escapeText(), fold(), IcsEvent, nextDay(), stamp() (+1 more)

### Community 112 - "Progress"
Cohesion: 0.25
Nodes (9): parametrize, test_enacted_date_matches_known_acts(), rule(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Metrics (S2, real corpus), Next session (+1 more)

### Community 113 - "@playwright/test"
Cohesion: 0.22
Nodes (4): Json, PAIRS, ref_node_fs, @playwright/test

### Community 114 - "Env"
Cohesion: 0.25
Nodes (4): client(), Env, fixture, Fake Supabase surface for the route tests.

### Community 115 - "smoke.spec.ts"
Cohesion: 0.25
Nodes (3): API, API_WAIT, PAGES

### Community 116 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test:e2e, test:mock, test:unit

### Community 117 - "Done"
Cohesion: 0.20
Nodes (12): _require_user(), audit_log(), draft_delete(), matter_delete(), Best-effort record of an irreversible user action (a delete, so far - see…, test_audit_log_fails_open_without_supabase_configured(), test_draft_delete_writes_an_audit_log_entry(), test_matter_delete_writes_an_audit_log_entry() (+4 more)

### Community 119 - "devDependencies"
Cohesion: 0.33
Nodes (6): devDependencies, @playwright/test, @types/node, @types/react, @types/react-dom, typescript

### Community 120 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, next, react, react-dom, @supabase/supabase-js

### Community 121 - "verifier.py"
Cohesion: 0.36
Nodes (9): check_sentence(), _haystack_numbers(), _is_legal_claim(), _norm_num(), _quantities(), Deterministic citation verifier for generated answers. The model writes the…, None if the claim is supported, else a short reason code., _sections() (+1 more)

### Community 122 - "_FakeAnthropicClient"
Cohesion: 0.22
Nodes (4): _FakeAnthropicClient, _FakeMessage, _FakeTextBlock, _FakeUsage

### Community 123 - "preeti.ts"
Cohesion: 0.17
Nodes (9): CHARS, I_MATRA_RE, JOIN_RULES, MATRA_AFTER_HALANT_RE, MATRA_BEFORE_HALANT_RE, NASAL_BEFORE_MATRA_RE, REPH_RE, SEQUENCES (+1 more)

### Community 124 - "draft_update"
Cohesion: 0.24
Nodes (10): draft_create(), draft_get(), draft_list(), draft_update(), _draft_version_insert(), draft_versions_list(), Overwrites the draft's current state and appends a new version snapshot;…, Newest first, or None if Supabase is unavailable (distinct from `[]`, a draft… (+2 more)

### Community 125 - "scrape_lawcommission_gap"
Cohesion: 0.27
Nodes (10): existing_corpus_titles(), in_corpus(), Spelling/digit-insensitive identity of a law title (years are part of the…, title_key -> doc_title_ne for every law document in the pre-existing corpus…, True when a law of this title (same year, near-identical spelling:…, Compare the Law Commission's current-acts index (alphabetical index page: ~350…, scrape_lawcommission_gap(), fresh() (+2 more)

### Community 126 - "S6 — Action Plan engine (2026-09-26)"
Cohesion: 0.32
Nodes (4): Doc-level metadata plus its ordered section list, for /law/[doc]., section label -> position within the doc's rows, built once per document…, One section's full entry plus neighbouring sections, for /law/[doc]/[section]., S6 — Action Plan engine (2026-09-26)

### Community 127 - "doc_slug"
Cohesion: 0.33
Nodes (6): doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, test_law_browser_doc_and_section_endpoints(), test_law_browser_doc_lists_its_sections_in_order(), test_law_browser_excludes_bill_doc_by_default(), test_law_browser_section_has_prev_next_neighbours()

### Community 128 - "drop_redraw_passes"
Cohesion: 0.50
Nodes (3): drop_redraw_passes(), Simulated bold is often drawn as 2-4 passes of the same glyphs inside one span.…, test_simulated_bold_redraw_passes_are_dropped()

## Knowledge Gaps
- **255 isolated node(s):** `LimitationRule`, `built_at`, `curated`, `law_chunks`, `precedents` (+250 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 742 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `S5 — Supabase auth + DB (2026-09-26)` to `run_eval.py`, `generation.py`, `ui.tsx`, `retrieval.py`, `Done`?**
  _High betweenness centrality (0.282) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `ui.tsx` to `audit/page.tsx`, `S5 — Supabase auth + DB (2026-09-26)`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **Why does `get_index()` connect `retrieval.py` to `schemas.py`, `run_eval.py`, `S5 — Supabase auth + DB (2026-09-26)`, `generation.py`, `checklists.py`, `documents.py`, `chat.py`, `json`, `playbooks.py`, `test_v1_trust_engine.py`, `search`, `pytest`, `Index`, `test_documents_audit.py`, `resolve_provision`, `get`, `chat`, `S6 — Action Plan engine (2026-09-26)`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LimitationRule`, `built_at`, `curated` to the rest of the system?**
  _255 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10588235294117647 - nodes in this community are weakly interconnected._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.05325814536340852 - nodes in this community are weakly interconnected._