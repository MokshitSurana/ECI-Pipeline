# Ecosystem Change Intelligence (ECI)

**Autonomous multi-agent threat intelligence that turns fast-changing security feeds into evidence-backed action tickets.**

ECI monitors the Android digital-risk ecosystem (security bulletins, Play Integrity API docs, CISA Known Exploited Vulnerabilities, developer-policy updates), detects what actually changed between snapshots, links those changes across sources with a knowledge graph, and uses LLM agents to triage risk and write structured, traceable recommendations. Built against a fraud-operations workflow (developed with TransUnion).

The core idea: most ecosystem monitoring dumps raw diffs on analysts. ECI instead emits an *Action Ticket* with a risk score, a suggested owner, an urgency level, and citations back to the evidence, so the output plugs straight into a triage queue instead of becoming more noise to read.

---

## Pipeline at a glance

```
Ingest  ->  Diff  ->  Embed  ->  KG build  ->  Sentinel (triage)  ->  Coordinator (synthesize)  ->  Action Ticket
```

- **Ingest** fetches and cleans snapshots from 10 live sources, hashing content (SHA-256) so re-fetches only register real changes.
- **Diff** extracts added/deleted spans with `difflib`, filtering cosmetic noise (whitespace, formatting) below a lexical-distance threshold.
- **Embed** chunks and embeds *only the delta content*, not whole documents, which keeps the vector index focused on operationally relevant signal instead of diluting it with unchanged background text.
- **KG build** runs deterministic regex entity extraction (CVEs, API levels, permissions, policy clauses) into a NetworkX graph with typed edges (`affects`, `deprecates`, `co-occurs`, `references`, `supersedes`).
- **Sentinel agent (LLM)** scores each change 0 to 10 for relevance and risk and drops anything below threshold, so the expensive Coordinator never sees noise.
- **Coordinator agent (LLM)** runs DeltaRAG retrieval, links cross-source evidence, and produces the final Action Ticket.

---

## The LLM engineering

The part worth reading if you're evaluating this as LLM work rather than as a security tool.

**Two agents, both on `llama-3.1-8b-instant` via Groq.** The model was chosen for sub-second latency and reliable structured output, not raw capability. Every agent response must pass `json.loads()` and validate against a Pydantic schema with no manual post-processing. A response that doesn't parse is a failed response, not something to clean up downstream.

**Prompting for structured-output stability.** Getting an 8B model to emit valid, schema-conformant JSON every time is the actual engineering problem here. What made it reliable:
- a system-level role that pins the agent to a security-analyst persona
- the full JSON schema inlined in the prompt with per-field value constraints
- an explicit instruction to output only the JSON object, no preamble or explanation
- few-shot examples covering both the relevant and the irrelevant case for the Sentinel, and numbered evidence blocks with required `evidence_ids` for the Coordinator

**DeltaRAG retrieval (what the Coordinator runs).** Vector search over the delta-chunk index runs in parallel with a 2-hop knowledge-graph traversal, and the two ranked lists are fused with Reciprocal Rank Fusion (k = 60). RRF is a deliberate choice over naive concatenation or graph-distance boosting: a chunk ranked highly by vector search keeps its score even when the graph finds no path to it, so the graph layer can only help, never drag results below the vector baseline. That fallback property is what makes the fusion safe to deploy.

---

## Evaluation

I evaluated this honestly, which means the headline is a **trade-off, not a clean win.** That framing is intentional. The interesting question for a retrieval system isn't "does my method win on average," it's "where does the extra machinery help, where does it hurt, and why."

**Setup.** 100 deterministic benchmark queries (85 scored, 10 query types), top-k = 5, Nomic v1.5 embeddings. Significance via paired Wilcoxon signed-rank tests with Holm-Bonferroni correction across the confirmatory comparisons; 95% bootstrap confidence intervals (10,000 resamples).

**Variants.** V1 Standard RAG (vector only), V2 KG-Only (2-hop traversal, no vectors), V3 DeltaRAG (vector + KG fused via RRF).

| Variant | P@1 | P@5 | R@5 | nDCG@5 | MRR | False-alarm rejection |
|---|---|---|---|---|---|---|
| Standard RAG (vector only) | 0.847 | **0.504** | **0.931** | 0.877 | 0.913 | 100% |
| KG-Only | 0.635 | 0.341 | 0.571 | 0.587 | 0.639 | 100% |
| **DeltaRAG (fused)** | **0.882** | 0.478 | 0.899 | **0.873**\* | **0.930** | 100% |

\*nDCG@5 for DeltaRAG is statistically tied with Standard RAG (p = 0.43).

**The honest reading:**

- **DeltaRAG vs Standard RAG is a trade, not a sweep.** It improves top-rank precision (P@1 0.882 vs 0.847, MRR 0.930 vs 0.913) and ties on nDCG@5, while giving back a couple of points of depth-5 recall (R@5 0.899 vs 0.931, p = 0.014). For a triage tool where an analyst acts on the *first* surfaced result, trading depth-5 recall for top-of-list precision is the right direction.
- **The KG component earns its place on `policy_compliance`, `temporal_change`, and `noisy_adversarial` queries**, where a shared identifier links two sources that share no vocabulary. On clean identifier queries the embedding already solves, the KG is redundant but not harmful, which is the behavior the RRF fallback was designed for.
- **KG-Only (V2) lags badly, but that gap is diagnostic, not competitive.** The regex entity extractor returns nothing on free-text queries, so the traversal has no seed node and scores zero. That's a coverage limit of the current extractor, not of structural retrieval, and it's the top future-work item (LLM-driven extraction).
- **All three variants reject 100% of out-of-scope queries.**

A depth sweep (k in {3, 5, 10}) and RRF-constant sweep, full per-query failure analysis (extraction blackouts, fusion-induced recall regressions, the structural precision ceiling), and four representative case studies spanning win / parity / failure are in the paper.

---

## Stack

- **Orchestration:** async worker polling a `pipeline_jobs` queue (no heavy agent framework), streaming step-level logs to a relational table for full traceability
- **LLMs:** Groq `llama-3.1-8b-instant` (Sentinel + Coordinator)
- **Embeddings:** `nomic-ai/nomic-embed-text-v1.5` (768-dim, 8,192-token context, task-aware prefixes), run locally so vulnerability data never leaves controlled infrastructure
- **Store:** Supabase (PostgreSQL + `pgvector`, HNSW index for sub-10ms cosine search), which lets vector chunks, relational change events, and recommendations live in one place and join with plain SQL
- **Knowledge graph:** NetworkX (typed edges, 2-hop traversal, entity-type weighting, cross-category bonus)
- **Frontend:** Next.js 14 dashboard (Action Tickets view, raw change log with Sentinel scores, interactive force-directed knowledge graph)
- **Tooling:** Python 3.11, `uv`

---

## Quick start

### Prerequisites
- A [Supabase](https://supabase.com/) account (free tier works; watch connection limits)
- A [Groq](https://console.groq.com/) API key
- Python 3.11+ and Node.js 18+

### Setup
```bash
# Install uv if needed
pip install uv

# Sync dependencies
uv sync

# Add your key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

If you're using your own Supabase instance, update the connection strings in `config/settings.py` and `dashboard/lib/db.js`, then build the tables:
```bash
uv run scripts/init_supabase.py
```

### Run the pipeline
```bash
# Everything end to end
uv run main.py --stage all

# Or stage by stage
uv run main.py --stage seed        # one-time: seed the source registry (sources.json)
uv run main.py --stage scrape      # fetch HTML/JSON snapshots
uv run main.py --stage diff        # detect changes between snapshots
uv run main.py --stage embed       # chunk deltas, embed, upload to pgvector
uv run main.py --stage graph       # build the knowledge graph
uv run main.py --stage triage      # Sentinel agent (filter noise)
uv run main.py --stage coordinate  # Coordinator agent (build Action Tickets)
```

### Run the dashboard
```bash
cd dashboard
npm install
npm run dev
```
Open `http://localhost:3000`.
- **Action Tickets:** the synthesized, prioritized alerts
- **Changes:** the raw chronological diff log with Sentinel scores
- **Knowledge Graph:** the interactive map of how a vulnerability connects across policies, components, and Android versions

---

## Paper

The full write-up (formal framework, architecture, ablation, failure analysis, sensitivity study) is included in the repo: *From Deltas to Decisions: DeltaRAG and Ecosystem Change Intelligence for Digital Risk Monitoring.*
