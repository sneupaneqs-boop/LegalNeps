# Graph Report - LegalNeps  (2026-09-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1057 nodes · 2088 edges · 59 communities (42 shown, 17 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 145 edges (avg confidence: 0.91)
- Token cost: 3,173 input · 689 output

## Graph Freshness
- Built from commit: `b57ae5ab`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Chat and Stats API
- Frontend Pages and Components
- Data Ingestion Scripts
- Legal Fee Calculators
- Document Drafting Engine
- LLM Provider Clients
- Glossary and Query Matching
- Citation and Test Fixtures
- PDF Text Extraction
- Config and Rate Limiting
- Query Intent Analysis
- Graphify Extraction Pipeline
- Frontend Dependencies
- Document Metadata Processing
- Search Index Management
- Devanagari Glyph Mapping
- Search and Evaluation Runner
- Text Normalization and Tokenization
- Web Crawler
- Project Strategy and Roadmap
- TypeScript Configuration
- FastAPI Application Setup
- BM25 Retrieval Engine
- RAG Generation Pipeline
- Corpus Build System
- Embedding Benchmarks
- Corpus Manifest Metadata
- Civil Law Playbooks
- Graph Export Formats
- Session Audit Logs
- Graph Query Reference
- Criminal Law Playbooks
- Labor Law Playbooks
- Project Milestone Tracking
- Loan and Debt Playbooks
- Harassment Prevention Playbooks
- LRU Cache Utility
- File Watching Documentation
- Git Hook Documentation
- Incremental Update Documentation
- Theft and Procedure Playbooks
- Traffic Law Playbooks
- Dependency Management
- GitHub Integration Documentation
- Media Transcription Documentation
- Claude Integration Guide
- Claude Configuration
- Extraction Prompt Specification
- Next.js Configuration
- Next.js Type Definitions
- Banking Law Playbook
- Citizenship Law Playbook
- Consumer Rights Playbook
- Domestic Violence Playbook
- Police Procedure Playbook
- Employment Fraud Playbook
- Property Dispute Playbook
- RTI Request Playbook

## God Nodes (most connected - your core abstractions)
1. `get_index()` - 27 edges
2. `complete()` - 24 edges
3. `analyze_query()` - 21 edges
4. `tokenize()` - 20 edges
5. `run()` - 20 edges
6. `Index` - 19 edges
7. `AuthWidget()` - 19 edges
8. `resolve_provision()` - 19 edges
9. `Crawler` - 18 edges
10. `extract_doc_meta()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `S9 — Drafting engine (2026-09-28)` --references--> `MissingField`  [INFERRED]
  docs/PROGRESS.md → backend/app/drafting/render.py
- `S8 — Calculators (2026-09-27)` --references--> `UnresolvedProvision`  [INFERRED]
  docs/PROGRESS.md → backend/app/playbooks.py
- `S5 — Supabase auth + DB (2026-09-26)` --references--> `_require_user()`  [INFERRED]
  docs/PROGRESS.md → backend/app/routes/chat.py
- `S5 — Supabase auth + DB (2026-09-26)` --references--> `AuthWidget()`  [INFERRED]
  docs/PROGRESS.md → frontend/components/AuthWidget.tsx
- `S5 — Supabase auth + DB (2026-09-26)` --references--> `signOut()`  [INFERRED]
  docs/PROGRESS.md → frontend/lib/supabase.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Criminal Law Playbooks** — backend_app_data_playbooks_child_marriage_protection, backend_app_data_playbooks_cyber_harassment, backend_app_data_playbooks_defamation, backend_app_data_playbooks_physical_assault, backend_app_data_playbooks_fir_not_registered [EXTRACTED 0.90]
- **Family Law Playbooks** — backend_app_data_playbooks_child_custody, backend_app_data_playbooks_divorce, backend_app_data_playbooks_domestic_violence, backend_app_data_playbooks_maintenance_alimony, backend_app_data_playbooks_inheritance_share [EXTRACTED 0.90]
- **Employment Law Playbooks** — backend_app_data_playbooks_unpaid_salary, backend_app_data_playbooks_workplace_sexual_harassment, backend_app_data_playbooks_wrongful_termination [EXTRACTED 1.00]

## Communities (59 total, 17 thin omitted)

### Community 0 - "Chat and Stats API"
Cohesion: 0.05
Nodes (93): corpus_stats(), ad_to_bs(), ai_fill_field(), _bad_input(), bs_to_ad(), calc_gratuity(), calc_notice(), calc_severance() (+85 more)

### Community 1 - "Frontend Pages and Components"
Cohesion: 0.05
Nodes (70): ActionPlanPage(), Bi(), ProvisionCard(), ActionPlansPage(), AREA_LABEL, frontend_app_globals, DOC_TYPE_LABEL, LawDocPage() (+62 more)

### Community 2 - "Data Ingestion Scripts"
Cohesion: 0.05
Nodes (61): argparse, main(), Builds backend/app/data/glossary.json: English and romanised-Nepali words…, add_entries(), ask_json(), ingest_acts(), ingest_constitution(), ingest_maxims() (+53 more)

### Community 3 - "Legal Fee Calculators"
Cohesion: 0.05
Nodes (62): appeal_fee(), court_fee(), estimate(), estimate_appeal(), Court fee (अदालती शुल्क) calculator (S8). मुलुकी देवानी कार्यविधि संहिता, २०७४…, The दफा ६९ अदालती शुल्क for a claim of this disclosed value., The दफा ७३ additional appeal fee for appealing a claim of this (portion of the)…, Filing fee + court fee for filing a plaint over `claim_value`, each with its… (+54 more)

### Community 4 - "Document Drafting Engine"
Cohesion: 0.05
Nodes (52): fill(), _get_field(), ValueError, LLM-assisted drafting for free-text fields (S10). Only `textarea` fields go…, Expand `hint` into fuller prose for `field_id` of `template_id`, in `language`.…, UnknownField, Field, Paragraph (+44 more)

### Community 5 - "LLM Provider Clients"
Cohesion: 0.08
Nodes (51): _anthropic_complete(), _client_http(), _compat_enabled(), complete(), _cool(), _cool_target(), _gemini(), _gemini_cfg() (+43 more)

### Community 6 - "Glossary and Query Matching"
Cohesion: 0.06
Nodes (44): _index(), _key(), _norm_en(), Local English / romanised-Nepali -> statute-Nepali query expansion. Statutes…, size(), _keyword_hit_fraction(), _keyword_weight(), Match (+36 more)

### Community 7 - "Citation and Test Fixtures"
Cohesion: 0.05
Nodes (18): focus(), normalize_citations(), The part of a passage that matters for this question: the heading line plus the…, Models sometimes cite as "[Muluki Civil Code 2074, Section 400]" instead of…, doc_slug(), Stable, URL-safe id for a document's law-browser page, derived from its title…, client(), fixture (+10 more)

### Community 8 - "PDF Text Extraction"
Cohesion: 0.08
Nodes (40): build_glyph_reference(), build_vocab(), chunk_document(), convert_legacy(), drop_redraw_passes(), extract_pdf(), find_sections(), _font_bytes() (+32 more)

### Community 9 - "Config and Rate Limiting"
Cohesion: 0.11
Nodes (36): _keys(), All keys from comma-separated env vars (GROQ_API_KEYS=k1,k2 and/or…, available(), cache_get(), cache_put(), check_and_increment_quota(), check_ip_rate_limit(), draft_create() (+28 more)

### Community 10 - "Query Intent Analysis"
Cohesion: 0.12
Nodes (23): analyze_needs_llm(), build_queries(), confidence(), quick_intent(), Obvious non-legal messages, recognised without any LLM., How sure we are this message is a legal question we can search well without an…, Whether analyze_query() will reach a provider for this message - kept in sync…, Weighted query set: the LLM's Nepali legal phrasings carry most weight;… (+15 more)

### Community 11 - "Graphify Extraction Pipeline"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 12 - "Frontend Dependencies"
Cohesion: 0.08
Nodes (24): dependencies, next, react, react-dom, @supabase/supabase-js, devDependencies, @types/node, @types/react (+16 more)

### Community 13 - "Document Metadata Processing"
Cohesion: 0.15
Nodes (20): _bs_date(), classify_status(), extract_doc_meta(), _find_enacted_date(), Doc-level status/date metadata shared by scripts/build_corpus.py (which…, First BS date following a certification/gazette-date trigger word, within the…, status/enacted_bs/amended_by/consolidated_upto for one document, from its first…, parametrize (+12 more)

### Community 14 - "Search Index Management"
Cohesion: 0.13
Nodes (10): Index, ndarray, All passages (loads everything - for scripts/evals, not requests)., slug -> row indices, in corpus order (which is section order for scraped…, Doc-level metadata plus its ordered section list, for /law/[doc]., One section's full entry plus neighbouring sections, for /law/[doc]/[section]., _title_tokens(), test_cache_roundtrip() (+2 more)

### Community 15 - "Devanagari Glyph Mapping"
Cohesion: 0.13
Nodes (20): build_glyph_table(), build_reference(), decode_span(), _outline_hash(), prepare(), Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are…, glyphs: (unicode string, is_reph) per glyph, in visual order., chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox). Returns None if… (+12 more)

### Community 16 - "Search and Evaluation Runner"
Cohesion: 0.26
Nodes (19): analyze_query(), search(), available(), parse_json(), get_index(), detect_language(), cmd_e2e(), cmd_retrieval() (+11 more)

### Community 17 - "Text Normalization and Tokenization"
Cohesion: 0.18
Nodes (18): fold(), guess_language(), Normalisation + tokenisation shared by indexing and querying. Nepali legal text…, Reply language for 'auto': Devanagari -> ne; Latin script counts as romanised…, Index term for one folded token ('' = drop it)., _stem_en(), _stem_ne(), _term() (+10 more)

### Community 18 - "Web Crawler"
Cohesion: 0.18
Nodes (4): Crawler, push(), Icon-only PDF links (common on the category tables) carry no anchor text; fall…, Listing pages (category tables, index pages, pagination) link directly to every…

### Community 19 - "Project Strategy and Roadmap"
Cohesion: 0.11
Nodes (18): Session Prompts, Add-ons for specific sessions (append to the kickoff), Session prompts, Universal kickoff prompt (paste this at the start of every session), When to switch models yourself, 1. What already exists, 2. Changes to the original roadmap, 3. Target architecture (+10 more)

### Community 20 - "TypeScript Configuration"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 21 - "FastAPI Application Setup"
Cohesion: 0.15
Nodes (13): asyncio, _GZipExceptStreams, health(), lifespan(), get, gzip buffers a streamed body until it ends, which would defeat…, root(), index_ready() (+5 more)

### Community 22 - "BM25 Retrieval Engine"
Cohesion: 0.15
Nodes (12): array, corpus_source(), _index_text(), _prior(), BM25 search over the government-sourced corpus (laws + precedents). The corpus…, Backwards-compatible single-query search., Authority of the source x usefulness of this particular passage., retrieve() (+4 more)

### Community 23 - "RAG Generation Pipeline"
Cohesion: 0.26
Nodes (13): _answer_cache_key(), answer_question(), _cache_key(), _extractive(), _history_text(), _passage(), _prompt(), Question understanding -> retrieval -> grounded answer. 1. analyze_query: a… (+5 more)

### Community 24 - "Corpus Build System"
Cohesion: 0.23
Nodes (12): curated_entries(), _is_gov(), law_entries(), main(), merge_constitution_translations(), precedent_entries(), Builds the app's searchable corpus from government sources only: -…, Earlier hand-verified constitution-art-N entries carry English translations;… (+4 more)

### Community 25 - "Embedding Benchmarks"
Cohesion: 0.23
Nodes (8): E5Small, _first_hit(), load_questions(), main(), ndarray, S4: does adding embeddings to the BM25 ranking actually help? Per STRATEGY.md,…, summarize(), numpy

### Community 26 - "Corpus Manifest Metadata"
Cohesion: 0.20
Nodes (9): built_at, counts, curated, law_chunks, law_documents, precedents, total, digest (+1 more)

### Community 27 - "Civil Law Playbooks"
Cohesion: 0.22
Nodes (9): Bonus Not Paid Playbook, Child Custody Playbook, Rental Deposit Playbook, Divorce Playbook, Inheritance Share Playbook, Maintenance and Alimony Playbook, Tenant Eviction Playbook, Kanooni Sathi Backend (+1 more)

### Community 28 - "Graph Export Formats"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 29 - "Session Audit Logs"
Cohesion: 0.40
Nodes (6): _doc_type(), Known issues, Later (ideas raised but out of scope for the current session), Live deployment (2026-09-28/29 audit), Next session, Progress

### Community 30 - "Graph Query Reference"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "Criminal Law Playbooks"
Cohesion: 0.40
Nodes (5): Child Marriage Protection Playbook, Cyber Harassment Playbook, Defamation Playbook, Physical Assault Playbook, Muluki Aparadh Samhita, 2074 (Criminal Code)

### Community 32 - "Labor Law Playbooks"
Cohesion: 0.40
Nodes (5): Unpaid Salary Playbook, Wrongful Termination Playbook, Shram Ain, 2074 Section 144, Shram Ain, 2074 Section 162, Shram Ain, 2074 Section 34

### Community 33 - "Project Milestone Tracking"
Cohesion: 0.50
Nodes (5): _entry_status(), Done, S2 — Legal data engine v2 (2026-09-26), S3.1 — bill-exclusion gap in curated entries (2026-09-26, pre-S4 check), S9 — Drafting engine (2026-09-28)

### Community 34 - "Loan and Debt Playbooks"
Cohesion: 0.50
Nodes (4): Unpaid Personal Loan Playbook, Muluki Dewani Sanhita, 2074 Section 495, Muluki Dewani Sanhita, 2074 Section 500, Muluki Dewani Sanhita, 2074 Section 520

### Community 35 - "Harassment Prevention Playbooks"
Cohesion: 0.50
Nodes (4): Workplace Sexual Harassment Playbook, Workplace Sexual Harassment (Prevention) Act, 2071 Section 15, Workplace Sexual Harassment (Prevention) Act, 2071 Section 5, Workplace Sexual Harassment (Prevention) Act, 2071 Section 7

### Community 37 - "File Watching Documentation"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 38 - "Git Hook Documentation"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 39 - "Incremental Update Documentation"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 40 - "Theft and Procedure Playbooks"
Cohesion: 0.67
Nodes (3): Theft Complaint Playbook, Muluki Aparadh Sanhita, 2074 Section 242, Muluki Faujdari Karyavidhi Sanhita, 2074 Section 4 (1)

### Community 41 - "Traffic Law Playbooks"
Cohesion: 0.67
Nodes (3): Traffic Accident Compensation Playbook, Sawari tatha Yatayat Wyawastha Ain, 2049 Section 152, Sawari tatha Yatayat Wyawastha Ain, 2049 Section 163

### Community 42 - "Dependency Management"
Cohesion: 0.67
Nodes (3): Backend Dependencies, Script Dependencies, CI Workflow

## Knowledge Gaps
- **154 isolated node(s):** `Strings`, `Amendment`, `ChatResponse`, `LawDoc`, `LawSection` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 396 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `S5 — Supabase auth + DB (2026-09-26)` connect `Config and Rate Limiting` to `Chat and Stats API`, `Project Milestone Tracking`, `Frontend Pages and Components`, `Search and Evaluation Runner`, `RAG Generation Pipeline`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Why does `AuthWidget()` connect `Frontend Pages and Components` to `Config and Rate Limiting`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `get_index()` connect `Search and Evaluation Runner` to `Chat and Stats API`, `Legal Fee Calculators`, `Glossary and Query Matching`, `Config and Rate Limiting`, `Search Index Management`, `FastAPI Application Setup`, `BM25 Retrieval Engine`, `RAG Generation Pipeline`, `Embedding Benchmarks`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_index()` (e.g. with `lifespan()` and `S5 — Supabase auth + DB (2026-09-26)`) actually correct?**
  _`get_index()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `complete()` (e.g. with `Metrics (baseline, S1)` and `S10 — Drafting + AI fill + save (2026-09-28)`) actually correct?**
  _`complete()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `analyze_query()` (e.g. with `Metrics (baseline, S1)` and `S3 — LLM-free hot path (2026-09-26)`) actually correct?**
  _`analyze_query()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Strings`, `Amendment`, `ChatResponse` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._