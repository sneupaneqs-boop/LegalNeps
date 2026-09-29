# Graph Report - LegalNeps  (2026-09-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1136 nodes · 2290 edges · 69 communities (53 shown, 16 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 162 edges (avg confidence: 0.92)
- Token cost: 3,941 input · 813 output

## Graph Freshness
- Built from commit: `4cbb811c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Drafting API Schemas
- Frontend Pages and Components
- Law Commission Scraper
- Court Fee Calculator
- Document Drafting Templates
- LLM Provider Configuration
- Playbook Routing Logic
- Citation Normalization and Testing
- PDF Text Extraction
- Quota and Draft Management
- Legal Query Analysis
- Graphify Tool Documentation
- Frontend Package Dependencies
- Document Metadata Extraction
- Search Index Management
- Devanagari PDF Glyph Recovery
- Search and Evaluation Execution
- Text Tokenization and Normalization
- Web Crawler Implementation
- Project Strategy and Prompts
- TypeScript Configuration
- LLM Assisted Drafting
- BM25 Retrieval Engine
- Question Answering Logic
- Corpus Building Pipeline
- Embedding Benchmark Tools
- Corpus Manifest Data
- Civil Law Playbooks
- Graph Export Documentation
- Project Progress Tracking
- Graph Query Documentation
- Criminal Law Playbooks
- Labor Law Playbooks
- Legal Engine Roadmap
- Personal Loan Playbooks
- Sexual Harassment Playbooks
- Matter and Research Management
- Folder Watching Documentation
- Git Hook Documentation
- Incremental Update Documentation
- Theft Complaint Playbooks
- Traffic Compensation Playbooks
- Dependency and CI Workflows
- GitHub Integration Documentation
- Media Transcription Documentation
- Root Claude Documentation
- Local Claude Documentation
- Extraction Specification
- Next.js Configuration
- Next.js Environment Types
- Cheque Bounce Playbook
- Citizenship Playbook
- Consumer Complaint Playbook
- Domestic Violence Playbook
- FIR Registration Playbook
- Employment Fraud Playbook
- Land Dispute Playbook
- RTI Request Playbook
- Matter Store Mocking
- Legal Calculation Utilities
- Chat and Stream Handling
- Supreme Court Precedent Scraper
- Glossary and OCR Scripts
- Matter Creation Endpoints
- Scraped Data Ingestion
- PDF Ingestion Scripts
- Legal Glossary Index
- Playbook Matching Service

## God Nodes (most connected - your core abstractions)
1. `available()` - 33 edges
2. `_http()` - 32 edges
3. `get_index()` - 27 edges
4. `complete()` - 24 edges
5. `FakeMattersStore` - 21 edges
6. `analyze_query()` - 21 edges
7. `tokenize()` - 20 edges
8. `run()` - 20 edges
9. `Index` - 19 edges
10. `AuthWidget()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `S6 — Action Plan engine (2026-09-26)` --references--> `UnresolvedProvision`  [INFERRED]
  docs/PROGRESS.md → backend/app/playbooks.py
- `S8 — Calculators (2026-09-27)` --references--> `UnresolvedProvision`  [INFERRED]
  docs/PROGRESS.md → backend/app/playbooks.py
- `S5 — Supabase auth + DB (2026-09-26)` --references--> `AuthWidget()`  [INFERRED]
  docs/PROGRESS.md → frontend/components/AuthWidget.tsx
- `S5 — Supabase auth + DB (2026-09-26)` --references--> `signOut()`  [INFERRED]
  docs/PROGRESS.md → frontend/lib/supabase.ts
- `S5 — Supabase auth + DB (2026-09-26)` --references--> `verifyOtp()`  [INFERRED]
  docs/PROGRESS.md → frontend/lib/supabase.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (69 total, 16 thin omitted)

### Community 0 - "Drafting API Schemas"
Cohesion: 0.12
Nodes (30): ai_fill_field(), get_drafting_template(), law_section(), Expands a free-text field's short hint via the LLM. Signed-in only, and metered…, AiFillRequest, AiFillResponse, Amendment, Analysis (+22 more)

### Community 1 - "Frontend Pages and Components"
Cohesion: 0.05
Nodes (70): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, frontend_app_globals, DOC_TYPE_LABEL, LawDocPage() (+62 more)

### Community 2 - "Law Commission Scraper"
Cohesion: 0.15
Nodes (16): build_parser(), classify(), cmd_crawl(), cmd_ocr(), cmd_stats(), _extractable_text_fraction(), Crawls lawcommission.gov.np (and, optionally, other Nepali legal-source domains…, Rough heuristic: fraction of sampled pages that yield >20 chars of text. (+8 more)

### Community 3 - "Court Fee Calculator"
Cohesion: 0.05
Nodes (62): appeal_fee(), court_fee(), estimate(), estimate_appeal(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its… (+54 more)

### Community 4 - "Document Drafting Templates"
Cohesion: 0.08
Nodes (35): Field, Paragraph, Questionnaire field + document paragraph shapes shared by every drafting…, One paragraph of the generated document. `text` holds a Jinja source string per…, TemplateSpec, S9's first 6 drafting templates. Every statute reference embedded in a…, _build_context(), get_template() (+27 more)

### Community 5 - "LLM Provider Configuration"
Cohesion: 0.07
Nodes (54): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, _anthropic_complete(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target() (+46 more)

### Community 6 - "Playbook Routing Logic"
Cohesion: 0.07
Nodes (36): _keyword_hit_fraction(), _keyword_weight(), Match, _playbook_keywords(), _query_tokens(), Non-LLM query -> playbook routing (S7). Scores each playbook's `keywords` list…, Longer, more specific phrases count for more than a bare one-word keyword, so a…, 1.0 for an exact phrase hit, else the fraction of the keyword's own words that… (+28 more)

### Community 7 - "Citation Normalization and Testing"
Cohesion: 0.05
Nodes (16): normalize_citations(), Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, client(), fixture, test_law_browser_doc_and_section_endpoints(), test_research_save_list_delete_roundtrip() (+8 more)

### Community 8 - "PDF Text Extraction"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "Quota and Draft Management"
Cohesion: 0.10
Nodes (52): available(), cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), draft_create(), draft_delete(), draft_get() (+44 more)

### Community 10 - "Legal Query Analysis"
Cohesion: 0.13
Nodes (25): analyze_needs_llm(), analyze_query(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message is a legal question we can search well without an…, Whether analyze_query() will reach a provider for this message - kept in sync… (+17 more)

### Community 11 - "Graphify Tool Documentation"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "Frontend Package Dependencies"
Cohesion: 0.08
Nodes (24): dependencies, next, react, react-dom, @supabase/supabase-js, devDependencies, @types/node, @types/react (+16 more)

### Community 13 - "Document Metadata Extraction"
Cohesion: 0.15
Nodes (20): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, parametrize (+12 more)

### Community 14 - "Search Index Management"
Cohesion: 0.18
Nodes (6): Index, ndarray, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, _title_tokens(), Connection

### Community 15 - "Devanagari PDF Glyph Recovery"
Cohesion: 0.13
Nodes (20): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+12 more)

### Community 16 - "Search and Evaluation Execution"
Cohesion: 0.27
Nodes (16): search(), parse_json(), get_index(), detect_language(), cmd_e2e(), cmd_retrieval(), run(), cmd_synth() (+8 more)

### Community 17 - "Text Tokenization and Normalization"
Cohesion: 0.14
Nodes (22): focus(), The part of a passage that matters for this question: the heading line plus the…, fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised…, Index term for one folded token ('' = drop it)., _stem_en() (+14 more)

### Community 18 - "Web Crawler Implementation"
Cohesion: 0.18
Nodes (4): Crawler, push(), Icon-only PDF links (common on the category tables) carry no anchor text; fall…, Listing pages (category tables, index pages, pagination) link directly to every…

### Community 19 - "Project Strategy and Prompts"
Cohesion: 0.11
Nodes (17): Add-ons for specific sessions (append to the kickoff), Session prompts, Universal kickoff prompt (paste this at the start of every session), When to switch models yourself, 1. What already exists, 2. Changes to the original roadmap, 3. Target architecture, 4. Session plan (1 session = 1 milestone = 1 PR) (+9 more)

### Community 20 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "LLM Assisted Drafting"
Cohesion: 0.07
Nodes (31): asyncio, fill(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Expand `hint` into fuller prose for `field_id` of `template_id`, in `language`.…, UnknownField, _GZipExceptStreams (+23 more)

### Community 22 - "BM25 Retrieval Engine"
Cohesion: 0.14
Nodes (12): array, corpus_source(), _index_text(), _prior(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, Backwards-compatible single-query search., Authority of the source x usefulness of this particular passage., retrieve() (+4 more)

### Community 23 - "Question Answering Logic"
Cohesion: 0.18
Nodes (14): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), _history_text(), _LRU, _passage(), _prompt() (+6 more)

### Community 24 - "Corpus Building Pipeline"
Cohesion: 0.23
Nodes (12): curated_entries(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -…, Earlier hand-verified constitution-art-N entries carry English translations;… (+4 more)

### Community 25 - "Embedding Benchmark Tools"
Cohesion: 0.21
Nodes (9): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), numpy (+1 more)

### Community 26 - "Corpus Manifest Data"
Cohesion: 0.20
Nodes (9): built_at, counts, curated, law_chunks, law_documents, precedents, total, digest (+1 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Documentation"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "Project Progress Tracking"
Cohesion: 0.40
Nodes (6): _doc_type(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Next session, Progress

### Community 30 - "Graph Query Documentation"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "Legal Engine Roadmap"
Cohesion: 0.29
Nodes (8): _entry_status(), Doc-level metadata plus its ordered section list, for /law/[doc]., One section's full entry plus neighbouring sections, for /law/[doc]/[section]., Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S4 — Search + law browser UI (2026-09-26), S6 — Action Plan engine (2026-09-26)

### Community 34 - "Personal Loan Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Sexual Harassment Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 36 - "Matter and Research Management"
Cohesion: 0.12
Nodes (32): corpus_stats(), create_matter_note(), delete_draft(), delete_matter(), delete_matter_file(), delete_matter_note(), delete_matter_task(), delete_research() (+24 more)

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

### Community 59 - "Matter Store Mocking"
Cohesion: 0.08
Nodes (7): FakeMattersStore, matters_client(), fixture, S11: Matter workspace lite - matters, notes, tasks, files. Supabase isn't…, The API-layer proof: every sub-resource route 404s for a matter that isn't the…, In-memory stand-in for supa.py's matters/notes/tasks/files functions, keyed by…, test_user_b_cannot_see_user_a_matter_or_its_subresources()

### Community 60 - "Legal Calculation Utilities"
Cohesion: 0.11
Nodes (26): ad_to_bs(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance(), check_limitation(), estimate_appeal_fee() (+18 more)

### Community 61 - "Chat and Stream Handling"
Cohesion: 0.16
Nodes (18): chat(), chat_stream(), events(), _client_ip(), _current_user(), _enforce_limits(), _log_request(), NDJSON stream: {"type":"meta", sources...} then {"type":"delta","text"}* then… (+10 more)

### Community 62 - "Supreme Court Precedent Scraper"
Cohesion: 0.16
Nodes (14): fetch(), _lines(), main(), work(), parse(), Scrapes Supreme Court of Nepal precedents from the official Nepal Kanoon…, _section_after(), test_parse_extracts_headnote_and_metadata() (+6 more)

### Community 63 - "Glossary and OCR Scripts"
Cohesion: 0.22
Nodes (10): argparse, main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, main(), OCR for documents extract_laws.py flagged `needs_ocr` (scanned PDFs, or text…, render(), transcribe(), os (+2 more)

### Community 64 - "Matter Creation Endpoints"
Cohesion: 0.17
Nodes (12): create_draft(), create_matter(), create_matter_task(), draft_document(), save_research(), DraftRequest, MatterIn, MatterTaskIn (+4 more)

### Community 65 - "Scraped Data Ingestion"
Cohesion: 0.27
Nodes (11): ask_json(), load_corpus(), load_ingested(), load_manifest(), main(), Step 2 of the scrape pipeline: turns documents downloaded by…, save_corpus(), save_ingested() (+3 more)

### Community 66 - "PDF Ingestion Scripts"
Cohesion: 0.44
Nodes (9): add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims(), load_corpus(), One-off ingestion script: reads real Nepali legal PDFs (constitution, legal…, save_corpus() (+1 more)

### Community 67 - "Legal Glossary Index"
Cohesion: 0.36
Nodes (7): _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, size(), functools, json

### Community 68 - "Playbook Matching Service"
Cohesion: 0.67
Nodes (3): match_playbooks(), Non-LLM keyword+glossary routing (S7): a confident hit lets the UI jump…, PlaybookMatchResponse

## Knowledge Gaps
- **154 isolated node(s):** `Strings`, `Amendment`, `ChatResponse`, `LawDoc`, `LawSection` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 417 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `Quota and Draft Management` to `Legal Engine Roadmap`, `Frontend Pages and Components`, `Legal Query Analysis`, `Search and Evaluation Execution`, `Question Answering Logic`, `Chat and Stream Handling`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `Frontend Pages and Components` to `Quota and Draft Management`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `get_index()` connect `Search and Evaluation Execution` to `Drafting API Schemas`, `Legal Engine Roadmap`, `Court Fee Calculator`, `Matter and Research Management`, `Playbook Routing Logic`, `Quota and Draft Management`, `Search Index Management`, `LLM Assisted Drafting`, `BM25 Retrieval Engine`, `Question Answering Logic`, `Embedding Benchmark Tools`, `Legal Calculation Utilities`, `Chat and Stream Handling`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Strings`, `Amendment`, `ChatResponse` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Drafting API Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.11612903225806452 - nodes in this community are weakly interconnected._
- **Should `Frontend Pages and Components` be split into smaller, more focused modules?**
  _Cohesion score 0.05381400208986416 - nodes in this community are weakly interconnected._