# 🌐 Ecosystem Change Intelligence (ECI) Pipeline

> **Autonomous Threat Intelligence via DeltaRAG & Graph-RAG**

The **ECI Pipeline** is an autonomous, multi-agent AI system designed to solve alert fatigue for product security teams in the Android ecosystem. 

Instead of forcing analysts to manually read fragmented data streams (CISA vulnerability drops, Google Play Policy changes, OEM patches, API deprecations), ECI continuously scrapes the ecosystem, computes structural diffs, builds a cross-source Knowledge Graph, and uses LLM agents to automatically triage risk and generate actionable intelligence tickets.

---

## 🛑 The Problem: Ecosystem Noise
Security teams are drowning in unstructured noise:
1. **Alert Fatigue**: A typical National Vulnerability Database (NVD) or CISA JSON feed update can contain thousands of CVEs. 99% of them don't matter to your specific infrastructure.
2. **Decoupled Data**: A new Google Play Developer Policy might mandate the use of the `Photo Picker API`, which deprecates the `READ_MEDIA_IMAGES` permission. Traditional Vector Search (RAG) fails to connect these logical dots across different PDF documents and API diffs.
3. **Manual Triage**: Highly-paid risk engineers spend 80% of their time reading raw diffs rather than actively mitigating threats.

## 🚀 The Solution: DeltaRAG & Graph-RAG
ECI solves this through a novel architecture:

1. **Delta Processing**: We don't embed massive documents. We compute exact `git`-style diffs of what changed between yesterday and today.
2. **Graph-RAG**: We use NLP to extract entities (CVEs, System Components, Policy Clauses, Permissions) and build a directed Knowledge Graph. If an API change deprecates a permission, an explicit `deprecates` edge is drawn.
3. **DeltaRAG (Late Fusion)**: We combine Vector Similarity (for semantic context) with Graph Traversal (for blast-radius mapping) to feed highly relevant context to our LLMs.
4. **Agentic Triage**: 
   - **Sentinel Agent**: Acts as the first filter. It scores raw diffs on a 1-10 scale for Relevance and Risk. Low-scoring items are ignored.
   - **Coordinator Agent**: Takes high-risk escalated items and synthesizes them into "Action Tickets" with evidence-backed mitigation plans assigned to specific engineering teams.

---

## 🏗️ Architecture Stack

- **Backend / DB**: Supabase (PostgreSQL + `pgvector` for embeddings)
- **Vector Embeddings**: `nomic-ai/nomic-embed-text-v1.5` (8,192 token context window)
- **Knowledge Graph**: NetworkX + D3.js Force-Directed Graph
- **LLM Agents**: Groq (`llama-3.1-8b-instant`) for lightning-fast, cheap structured JSON generation.
- **Frontend**: Next.js 14 Dashboard
- **Package Management**: `uv` (Fast Python package installer)

---

## ⚙️ Quick Start Guide

### 1. Prerequisites
You will need:
- A [Supabase](https://supabase.com/) account (Nano/Free tier works, but monitor connection limits).
- A [Groq](https://console.groq.com/) API key.
- Python 3.11+ and Node.js 18+.

### 2. Environment Setup

Clone the repository and set up your Python environment using `uv`:
```bash
# Install uv if you don't have it
pip install uv

# Sync dependencies
uv sync

# Create your .env file in the root directory
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

**Configure Supabase:**
By default, the pipeline uses the hardcoded Supabase connection in `config/settings.py` and `dashboard/lib/db.js`. If you are using your own Supabase instance, update the `DATABASE_URL` / connection strings in both files, and run the `scripts/init_supabase.py` script to build the SQL tables.

### 3. Running the ECI Pipeline

The pipeline is orchestrated via `main.py`. You can run the entire pipeline at once, which will scrape sources, detect diffs, embed chunks, build the graph, and run the AI agents.

```bash
uv run main.py --stage all
```

**Running Individual Stages:**
```bash
uv run main.py --stage seed       # 1. Seed the source registry (sources.json)
uv run main.py --stage scrape     # 2. Fetch HTML/JSON snapshots from the web
uv run main.py --stage diff       # 3. Detect changes between snapshots
uv run main.py --stage embed      # 4. Chunk deltas and upload to pgvector
uv run main.py --stage graph      # 5. Build Knowledge Graph (capped to prevent UI bloat)
uv run main.py --stage triage     # 6. Run Sentinel Agent (Filters noise)
uv run main.py --stage coordinate # 7. Run Coordinator Agent (Builds Action Tickets)
```

### 4. Running the Dashboard

Once the pipeline has populated your database, start the Next.js frontend to visualize the intelligence:

```bash
cd dashboard
npm install
npm run dev
```
Open `http://localhost:3000` in your browser. 
- **Action Tickets**: The executive view of critical, synthesized alerts.
- **Changes**: The raw chronological audit log of all diffs + Sentinel scores.
- **Knowledge Graph**: The interactive D3.js visualization mapping the blast radius of vulnerabilities across policies and components.

---

## 🔬 Evaluation & Ablation Study

The repository includes a rigorous evaluation framework (`evaluation/ablation_study.py`) built on a synthetic, deterministic dataset of 50 Golden Queries spanning 10 sources.

We evaluated 3 architectural variants:
1. **Vector-Only RAG**: Standard chunk similarity search.
2. **Graph-Only RAG**: Pure Knowledge Graph traversal (2-hop).
3. **DeltaRAG (Late Fusion)**: Combining Vector + Graph using Reciprocal Rank Fusion (RRF).

The study utilizes paired Wilcoxon signed-rank tests and Holm-Bonferroni corrections to statistically prove the retrieval superiority of Graph-RAG over traditional methods when tracking cross-document ecosystem changes.
