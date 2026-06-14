# ECI Pipeline — Latency / Overhead Profile

Profiled over 10 escalated changes on the isolated eval DB. Retrieval stages averaged over 3 runs each; LLM stages (Groq, llama-3.1-8b-instant) timed once per change. Times in milliseconds (mean ± population SD across changes).

## Full DeltaRAG Pipeline (per Action Ticket)

| Component | Time (ms) | % of total |
| :-- | --: | --: |
| Vector retrieval | 668.9 ± 131.5 | 2.4% |
| KG extraction + traversal | 890.0 ± 453.4 | 3.2% |
| Fusion / reranking | 0.0 ± 0.0 | 0.0% |
| LLM synthesis (Sentinel + Coordinator) | 26489.5 | 94.4% |
| **Total (end-to-end)** | **28048.4** | 100% |

## Overhead vs. Vector-Only Baseline

Baseline pipeline = vector retrieval + LLM synthesis, with no KG extraction/traversal, no fusion, and no cross-source evidence block in the Coordinator prompt.

| Pipeline | Retrieval+KG+Fusion (ms) | LLM (ms) | Total (ms) |
| :-- | --: | --: | --: |
| Vector-only baseline | 668.9 | 26411.7 | 27080.6 |
| Full DeltaRAG | 1558.9 | 26489.5 | 28048.4 |
| **Added overhead** | **890.0** | **77.8** | **967.8** |

The structural machinery (KG + fusion) adds 890.0 ms (3.2% of end-to-end time); the dominant cost is LLM synthesis. The DeltaRAG pipeline's measured overhead over the vector-only baseline is 967.8 ms per ticket.
