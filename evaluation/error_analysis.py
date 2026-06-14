"""Structured error analysis for the ECI/DeltaRAG retrieval failures.

Classifies every scored golden query into one of the advisor's failure
categories using mechanical rules over the extractor + the three retrievers,
so the per-category counts are derived rather than hand-tallied:

  C1  Entity not captured by regex      — an identifier/component token is
                                           present but the extractor finds nothing
                                           (KG blackout despite extractable signal)
  C2  Implicit relation not captured    — entities were extracted, but the KG
                                           still misses some gold cross-source links
  C3  NL query, no extractable id       — no identifier/component token at all;
                                           the KG path has nothing to anchor on
  C4  Fusion demotes a relevant item    — RRF ranks DeltaRAG below Standard RAG
  C5  Incomplete structural linkage     — KG fires but recovers only part of the
                                           gold link set (and fusion does not regress)

Runs on the isolated eval DB (ECI_EVAL=1). Read-only; no LLM calls.
"""
import os
os.environ["ECI_EVAL"] = "1"

import re
import argparse
from collections import defaultdict

from utils.db import get_session, Source, Change
from rag.entity_extractor import extract_entities
from rag.knowledge_graph import KnowledgeGraph
from evaluation.golden_queries import GOLDEN_QUERIES, QUERY_TYPE_LABELS
from evaluation.ablation_study import (
    run_vanilla_rag, run_graph_only, run_deltarag,
    prepare_top_k, compute_recall, assert_expected_db_state,
)

K = 5

# Tokens that *should* anchor the KG even when the regex extractor misses them.
IDENTIFIER_RE = re.compile(
    r"(CVE-\d{4}-\w+|SVE-\d{4}-\w+|CVE-\d{4}-P\d+|CVSS|SDK[_ ]?\d+|API[_ ]?\d+)",
    re.IGNORECASE,
)
COMPONENT_HINTS = [
    "knox", "secure folder", "titan", "theft detection", "exynos",
    "secure boot", "modem", "baseband",
]


def has_anchorable_token(text: str) -> bool:
    """True if the text contains an identifier or known component keyword that
    a complete extractor should have turned into a graph anchor."""
    if IDENTIFIER_RE.search(text):
        return True
    low = text.lower()
    return any(h in low for h in COMPONENT_HINTS)


def classify(query_text, expected_ids, rag_r, graph_r, delta_r, n_entities):
    """Return a category code C1..C5, or 'clean'."""
    # Fusion regression takes precedence: it is an active harm.
    if delta_r < rag_r:
        return "C4"
    # KG blackout: graph contributed nothing.
    if graph_r == 0.0:
        if n_entities == 0:
            return "C1" if has_anchorable_token(query_text) else "C3"
        # Entities extracted but the graph still returned nothing relevant:
        # the connecting relation is absent from the graph.
        return "C2"
    # KG fired but recovered only part of the gold set.
    if graph_r < 1.0:
        return "C5"
    return "clean"


def main():
    parser = argparse.ArgumentParser(description="Structured error analysis.")
    parser.add_argument("--seed", action="store_true",
                        help="Reseed the isolated eval DB before running.")
    parser.add_argument("--output", type=str, default="error_analysis.md")
    args = parser.parse_args()

    if args.seed:
        from evaluation.test_data import seed_test_data
        seed_test_data()
    else:
        assert_expected_db_state()

    session = get_session()
    sources = session.query(Source).all()
    name_to_id = {s.name: s.id for s in sources}
    id_to_category = {s.id: s.category for s in sources}
    changes_by_source = {}
    for change in session.query(Change).filter_by(status="pending").all():
        changes_by_source[change.source_id] = change
    session.close()

    kg = KnowledgeGraph.load_or_create()

    buckets = defaultdict(list)  # category -> [(id, type, query_text, rag_r, graph_r, delta_r)]
    n_scored = 0

    for gq in GOLDEN_QUERIES:
        source_id = name_to_id.get(gq["source"])
        if not source_id:
            continue
        if gq["query"] is None:
            change = changes_by_source.get(source_id)
            if not change or not change.diff_text:
                continue
            query_text = change.diff_text
        else:
            query_text = gq["query"]
        expected_ids = {name_to_id[n] for n in gq["expected"] if n in name_to_id}
        if not expected_ids:
            continue  # negative-rejection probes excluded from failure typing
        n_scored += 1

        n_entities = len(extract_entities(query_text).entities)
        rag_r = compute_recall(prepare_top_k(run_vanilla_rag(query_text, source_id, K), K), expected_ids, K)
        graph_r = compute_recall(
            prepare_top_k(run_graph_only(query_text, source_id, K, kg, id_to_category.get(source_id, "")), K),
            expected_ids, K)
        delta_r = compute_recall(prepare_top_k(run_deltarag(query_text, source_id, K), K), expected_ids, K)

        cat = classify(query_text, expected_ids, rag_r, graph_r, delta_r, n_entities)
        buckets[cat].append((gq["id"], gq["type"], query_text, rag_r, graph_r, delta_r))

    _report(buckets, n_scored, args.output)


CAT_LABELS = {
    "C1": "Entity not captured by regex",
    "C2": "Implicit relation not captured",
    "C3": "Natural-language query, no extractable identifier",
    "C4": "Fusion demotes a relevant item",
    "C5": "Incomplete structural linkage",
}


def _report(buckets, n_scored, output_path):
    lines = ["# Structured Error Analysis", "",
             f"{n_scored} scored queries (negative-rejection probes excluded). "
             f"Categories assigned by mechanical rule at k={K}.", ""]
    for cat in ["C1", "C2", "C3", "C4", "C5"]:
        items = buckets.get(cat, [])
        lines.append(f"## {cat}: {CAT_LABELS[cat]}  —  n={len(items)}")
        for qid, qtype, qtext, r, g, d in items:
            snippet = qtext.replace("\n", " ")[:90]
            lines.append(f"- {qid} ({qtype}): RAG_R={r:.2f} Graph_R={g:.2f} Delta_R={d:.2f} | {snippet}")
        lines.append("")
    clean = buckets.get("clean", [])
    lines.append(f"## clean (no failure) — n={len(clean)}")
    lines.append("")
    report = "\n".join(lines)
    print(report)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nWritten to {output_path}")
    # Console summary line for quick transcription.
    counts = {c: len(buckets.get(c, [])) for c in ["C1", "C2", "C3", "C4", "C5"]}
    counts["clean"] = len(clean)
    print("COUNTS:", counts, "total_scored:", n_scored)


if __name__ == "__main__":
    main()
