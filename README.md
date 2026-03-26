# ECI Pipeline — Ecosystem Change Intelligence

**From Deltas to Decisions: DeltaRAG and Graph-RAG for Digital Risk Change Intelligence**

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key (for LLM agents)
export GROQ_API_KEY="your-key-here"

# 3. Run the full pipeline
python main.py

# Or run individual stages:
python main.py --stage seed       # Seed source registry
python main.py --stage scrape     # Fetch snapshots
python main.py --stage diff       # Detect changes
python main.py --stage embed      # Chunk + embed changes
python main.py --stage triage     # Run Sentinel agent
python main.py --stage coordinate # Run Coordinator agent
python main.py --stage report     # Generate summary report
```

## Architecture

```
sources (SQLite) → scrape → snapshots → diff → changes → chunk → embed (ChromaDB)
                                                              ↓
                                          Sentinel Agent → Coordinator Agent → Action Tickets
```

## Project Structure

```
eci-pipeline/
├── main.py                  # Pipeline orchestrator
├── config/
│   └── settings.py          # All configuration
├── data/                    # SQLite DB + ChromaDB stored here
├── scripts/
│   ├── seed_sources.py      # Source registry seeding
│   ├── scraper.py           # Snapshot fetching
│   └── diff_detector.py     # Change detection
├── rag/
│   ├── chunker.py           # 1600/200 chunking
│   ├── embedder.py          # Nomic v1.5 embedding
│   └── retriever.py         # ChromaDB similarity search
├── agents/
│   ├── sentinel.py          # Triage agent
│   └── coordinator.py       # Synthesis + recommendations
├── utils/
│   └── db.py                # SQLite models + helpers
├── evaluation/
│   └── golden_dataset.py    # Retrieval evaluation
└── requirements.txt
```
