"""End-to-end latency / overhead profile for the ECI pipeline.

Breaks Action-Ticket generation into its main components and reports the
per-component and total wall-clock cost, plus the overhead of the full
DeltaRAG pipeline over a simpler vector-only baseline:

    Components
      - Vector retrieval        (DeltaRAG same-source + cross-source vector search)
      - KG extraction+traversal (entity extraction, 2-hop traversal, chunk fetch)
      - Fusion / reranking      (RRF scoring + dedup)
      - LLM synthesis           (Sentinel triage + Coordinator generation, Groq)

The deterministic retrieval stages are repeated and averaged; the LLM calls
(network-bound, higher variance) are timed once per change. Runs on the
isolated eval DB (ECI_EVAL=1). The LLM stages call the Groq API.
"""
import os
os.environ["ECI_EVAL"] = "1"

import argparse
from time import perf_counter
from statistics import mean, pstdev

from groq import Groq
from config.settings import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from utils.db import get_session, Source, Change
from rag.retriever import retrieve_context, retrieve_graph_rag
from agents.sentinel import triage_change
from agents.coordinator import COORDINATOR_SYSTEM_PROMPT
from evaluation.ablation_study import assert_expected_db_state

RETRIEVAL_REPEATS = 3  # deterministic stages averaged over this many runs


def _coordinator_llm_call(client, change, sentinel, delta_ctx, cross_ctx):
    """Replicate the Coordinator's Groq call (inference only) so retrieval is
    not double-counted. Mirrors agents/coordinator.py prompt assembly."""
    graph_info = ""
    if cross_ctx.get("entities_extracted", 0) > 0:
        graph_info = f"\nEntities extracted: {cross_ctx['entities_extracted']}"
        if cross_ctx.get("graph_change_ids"):
            graph_info += f"\nGraph-connected changes: {cross_ctx['graph_change_ids']}"
    user_prompt = f"""Analyze this escalated platform change and produce an Action Ticket.

=== SENTINEL TRIAGE SUMMARY ===
Title: {sentinel.get('title', '')}
Summary: {sentinel.get('summary', '')}

=== CHANGE CONTENT ===
{(change.diff_text or '')[:2000]}

=== RELATED EVIDENCE (DeltaRAG) ===
{delta_ctx['formatted_context'][:2000]}

=== CROSS-SOURCE EVIDENCE (Graph-RAG) ===
{cross_ctx['formatted_context'][:1500]}
{graph_info}

Respond with ONLY the JSON object."""
    t = perf_counter()
    client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": COORDINATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=LLM_TEMPERATURE,
        max_tokens=2048,
    )
    return perf_counter() - t


def profile_change(client, change, source_name):
    """Return per-component timings (seconds) for one change, full + baseline."""
    diff = change.diff_text or ""
    sid = change.source_id

    # ── Deterministic retrieval stages (averaged) ─────────────────
    vec, kg, fus = [], [], []
    for _ in range(RETRIEVAL_REPEATS):
        tm = {}
        t = perf_counter()
        delta_ctx = retrieve_context(diff, top_k=5, source_filter=sid)
        same_source_vec = perf_counter() - t
        cross_ctx = retrieve_graph_rag(diff, source_id=sid, top_k=3, timings=tm)
        vec.append(same_source_vec + tm.get("vector_retrieval", 0.0))
        kg.append(tm.get("entity_extraction", 0.0) + tm.get("kg_traversal", 0.0))
        fus.append(tm.get("fusion", 0.0))
    # Keep the last contexts for the LLM prompt.

    # ── LLM synthesis (timed once) ────────────────────────────────
    t = perf_counter()
    sentinel = triage_change(change, source_name) or {}
    t_sentinel = perf_counter() - t

    t_coord_full = _coordinator_llm_call(client, change, sentinel, delta_ctx, cross_ctx)

    # Baseline: vector-only context (no cross-source evidence block)
    empty_cross = {"formatted_context": "No cross-source connections found.",
                   "entities_extracted": 0, "graph_change_ids": []}
    t_coord_base = _coordinator_llm_call(client, change, sentinel, delta_ctx, empty_cross)

    return {
        "vector": mean(vec),
        "kg": mean(kg),
        "fusion": mean(fus),
        "sentinel": t_sentinel,
        "coord_full": t_coord_full,
        "coord_base": t_coord_base,
    }


def main():
    parser = argparse.ArgumentParser(description="ECI latency/overhead profile.")
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--limit", type=int, default=0,
                        help="Profile only the first N changes (0 = all).")
    parser.add_argument("--output", type=str, default="latency_profile.md")
    args = parser.parse_args()

    if not GROQ_API_KEY:
        raise SystemExit("GROQ_API_KEY not set — the LLM synthesis stage needs it.")

    if args.seed:
        from evaluation.test_data import seed_test_data
        seed_test_data()
    else:
        assert_expected_db_state()

    # Keep this session open through the loop: the Sentinel/Coordinator agents
    # lazy-load change.source, so the ORM objects must stay session-bound.
    session = get_session()
    try:
        changes = session.query(Change).filter_by(status="pending").all()
        id_to_name = {s.id: s.name for s in session.query(Source).all()}
        changes = [c for c in changes if c.diff_text]
        if args.limit:
            changes = changes[:args.limit]

        client = Groq(api_key=GROQ_API_KEY)

        # Warm up the embedding model (not timed).
        print("Warming up embedder...")
        retrieve_context(changes[0].diff_text or "", top_k=5, source_filter=changes[0].source_id)

        rows = []
        for i, change in enumerate(changes, 1):
            name = id_to_name.get(change.source_id, "Unknown")
            print(f"  [{i}/{len(changes)}] profiling change {change.id} ({name})...")
            rows.append(profile_change(client, change, name))
    finally:
        session.close()

    _report(rows, len(changes), args.output)


def _ms(x):
    return f"{x * 1000:.1f}"


def _report(rows, n, output_path):
    def agg(key):
        vals = [r[key] for r in rows]
        return mean(vals), pstdev(vals) if len(vals) > 1 else 0.0

    vec_m, vec_s = agg("vector")
    kg_m, kg_s = agg("kg")
    fus_m, fus_s = agg("fusion")
    sent_m, sent_s = agg("sentinel")
    cf_m, _ = agg("coord_full")
    cb_m, _ = agg("coord_base")

    llm_full = sent_m + cf_m
    llm_base = sent_m + cb_m
    total_full = vec_m + kg_m + fus_m + llm_full
    total_base = vec_m + llm_base  # baseline: no KG, no fusion

    lines = [
        "# ECI Pipeline — Latency / Overhead Profile",
        "",
        f"Profiled over {n} escalated changes on the isolated eval DB. "
        f"Retrieval stages averaged over {RETRIEVAL_REPEATS} runs each; LLM stages "
        f"(Groq, {LLM_MODEL}) timed once per change. Times in milliseconds "
        f"(mean ± population SD across changes).",
        "",
        "## Full DeltaRAG Pipeline (per Action Ticket)",
        "",
        "| Component | Time (ms) | % of total |",
        "| :-- | --: | --: |",
        f"| Vector retrieval | {_ms(vec_m)} ± {_ms(vec_s)} | {100*vec_m/total_full:.1f}% |",
        f"| KG extraction + traversal | {_ms(kg_m)} ± {_ms(kg_s)} | {100*kg_m/total_full:.1f}% |",
        f"| Fusion / reranking | {_ms(fus_m)} ± {_ms(fus_s)} | {100*fus_m/total_full:.1f}% |",
        f"| LLM synthesis (Sentinel + Coordinator) | {_ms(llm_full)} | {100*llm_full/total_full:.1f}% |",
        f"| **Total (end-to-end)** | **{_ms(total_full)}** | 100% |",
        "",
        "## Overhead vs. Vector-Only Baseline",
        "",
        "Baseline pipeline = vector retrieval + LLM synthesis, with no KG "
        "extraction/traversal, no fusion, and no cross-source evidence block in "
        "the Coordinator prompt.",
        "",
        "| Pipeline | Retrieval+KG+Fusion (ms) | LLM (ms) | Total (ms) |",
        "| :-- | --: | --: | --: |",
        f"| Vector-only baseline | {_ms(vec_m)} | {_ms(llm_base)} | {_ms(total_base)} |",
        f"| Full DeltaRAG | {_ms(vec_m + kg_m + fus_m)} | {_ms(llm_full)} | {_ms(total_full)} |",
        f"| **Added overhead** | **{_ms(kg_m + fus_m)}** | **{_ms(llm_full - llm_base)}** | **{_ms(total_full - total_base)}** |",
        "",
        f"The structural machinery (KG + fusion) adds {_ms(kg_m + fus_m)} ms "
        f"({100*(kg_m+fus_m)/total_full:.1f}% of end-to-end time); the dominant "
        f"cost is LLM synthesis. The DeltaRAG pipeline's measured overhead over the "
        f"vector-only baseline is {_ms(total_full - total_base)} ms per ticket.",
        "",
    ]
    report = "\n".join(lines)
    print("\n" + report)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
